"""
Add Tabulator support to Stock Management module - SURGICAL APPROACH

This script adds Tabulator initialization and updates data loading
WITHOUT changing existing HTML structure significantly.
"""

import re
import os

js_path = r'C:\Users\gpoli\GIT\AI_agents\UI\external\modules\stock-management\stock-management.js'

# Read file
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the loadReorderDashboard function and check its current implementation
print("Current file loaded. Checking for populateReorderTable method...")

if 'populateReorderTable' in content:
    print("✅ Found populateReorderTable method")
else:
    print("❌ populateReorderTable NOT found")

# Check if Tabulator is already used
if 'new Tabulator' in content or 'this.reorderTable' in content:
    print("⚠️  Tabulator code already exists! Skipping...")
    exit(0)

print("\nAdding Tabulator support...")

# Step 1: Replace the Reorder Dashboard tab HTML to include Tabulator container
print("Step 1: Update tab HTML...")

old_table_container = r'<div class="table-container">\s*<table class="data-table" id="reorder-table">'
new_table_container = '''<div id="reorder-table-container" style="min-height: 500px; background: #0B0E13; border: 1px solid #2A3142; border-radius: 6px;"></div>
                
                <!-- OLD HTML TABLE (Hidden - keeping for reference) -->
                <div id="old-reorder-table" style="display: none;">
                <div class="table-container">
                    <table class="data-table" id="reorder-table">'''

content = re.sub(old_table_container, new_table_container, content, flags=re.DOTALL)

# Step 2: Add Tabulator initialization helper method BEFORE loadReorderDashboard
print("Step 2: Add initReorderTabulator method...")

# Find where to insert (before async loadReorderDashboard)
insert_marker = r'(\s+async loadReorderDashboard\(\) \{)'

tabulator_init_method = r'''
    initReorderTabulator(data) {
        const container = document.getElementById('reorder-table-container');
        if (!container) {
            console.error('Reorder table container not found!');
            return;
        }

        // Destroy existing table
        if (window.stockReorderTable) {
            window.stockReorderTable.destroy();
        }

        // Create new Tabulator
        window.stockReorderTable = new Tabulator(container, {
            data: data,
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: "600px",
            placeholder: "No reorder data. Click Refresh.",
            columns: [
                {
                    title: "Stock ID",
                    field: "stock_id",
                    width: 150,
                    headerSort: true,
                    headerFilter: "input",
                    formatter: (cell) => `<span style="font-weight: 600; color: #0078d4;">${cell.getValue() || 'N/A'}</span>`
                },
                {
                    title: "Stock Type",
                    field: "stock_type",
                    width: 250,
                    headerSort: true,
                    headerFilter: "input"
                },
                {
                    title: "Current Level",
                    field: "current_level",
                    width: 120,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: (cell) => `<span style="font-weight: 700;">${cell.getValue() || 0}</span>`
                },
                {
                    title: "Reorder Point",
                    field: "reorder_point",
                    width: 120,
                    headerSort: true,
                    hozAlign: "center",
                    formatter: (cell) => `<span style="color: #f97316;">${cell.getValue() || 100}</span>`
                },
                {
                    title: "Status",
                    field: "status_display",
                    width: 150,
                    headerSort: true,
                    headerFilter: "select",
                    headerFilterParams: { values: { "": "All", "CRITICAL": "Critical", "LOW": "Low", "ADEQUATE": "Adequate" } },
                    formatter: (cell) => cell.getValue()
                },
                {
                    title: "Last Order",
                    field: "last_order_date",
                    width: 150,
                    headerSort: true,
                    formatter: (cell) => {
                        const val = cell.getValue();
                        return val && val !== 'N/A' ? `<span style="color: #9ca3af;">${val}</span>` : '<span style="color: #6b7280;">Never</span>';
                    }
                },
                {
                    title: "Supplier",
                    field: "supplier",
                    width: 180,
                    headerSort: true,
                    headerFilter: "input"
                }
            ]
        });

        console.log(`✅ Reorder Tabulator created with ${data.length} rows`);
    }

\1'''

content = re.sub(insert_marker, tabulator_init_method, content)

# Step 3: Update loadReorderDashboard to call Tabulator instead of HTML population
print("Step 3: Update data loading to use Tabulator...")

# Find and replace the populateReorderTable call with Tabulator init
old_populate_call = r'this\.populateReorderTable\(stocks\);'
new_populate_call = '''// Use Tabulator instead of HTML table
        const enrichedData = stocks.map(stock => {
            const level = parseInt(stock.current_level || 0);
            const reorderPoint = parseInt(stock.reorder_point || 100);
            
            let statusText, statusColor, statusIcon;
            if (level === 0 || level < (reorderPoint * 0.5)) {
                statusText = 'CRITICAL';
                statusColor = '#ef4444';
                statusIcon = 'fa-exclamation-triangle';
            } else if (level < reorderPoint) {
                statusText = 'LOW';
                statusColor = '#f97316';
                statusIcon = 'fa-bell';
            } else {
                statusText = 'ADEQUATE';
                statusColor = '#22c55e';
                statusIcon = 'fa-check-circle';
            }
            
            return {
                ...stock,
                status_display: `<span style="background: ${statusColor}33; color: ${statusColor}; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;"><i class="fas ${statusIcon}"></i> ${statusText}</span>`
            };
        });
        
        this.initReorderTabulator(enrichedData);'''

content = re.sub(old_populate_call, new_populate_call, content)

# Save
backup_path = js_path + '.pre_tabulator_backup'
os.rename(js_path, backup_path)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ COMPLETE!")
print(f"✅ Backup saved: {backup_path}")
print(f"✅ Tabulator integration added")
print(f"\nNext: Bump manifest version to 1.1.8 and hard refresh browser")
