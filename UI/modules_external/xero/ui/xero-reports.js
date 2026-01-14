/**
 * Xero Reports JavaScript
 * Handles ApexCharts visualization and Tabulator data tables
 * Integrates with Flask backend API
 */

// ===========================
// GLOBAL VARIABLES
// ===========================

let reportChart = null;
let reportTable = null;
let currentChartType = 'bar';

// Sample Data (Replace with API calls)
const sampleData = {
    summary: {
        total_outstanding: 45230.50,
        total_invoices: 127,
        overdue_critical: 23,
        avg_days: 45,
        trends: {
            total_outstanding_change: 12,
            invoice_count_change: -5,
            critical_count_change: 8,
            avg_days_change: 0
        }
    },
    chart_data: {
        labels: ['Current', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days'],
        values: [15000, 8000, 5000, 3000, 14230.50],
        colors: ['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f0000']
    },
    table_data: [
        {
            client_name: 'Acme Corporation',
            invoice_number: 'INV-1234',
            invoice_date: '2025-11-15',
            due_date: '2025-12-01',
            days_overdue: 22,
            amount: 2500.00,
            age_bucket: '1-30 Days',
            urgency: 'medium',
            contact_email: 'ap@acme.com'
        },
        {
            client_name: 'Beta LLC',
            invoice_number: 'INV-1235',
            invoice_date: '2025-10-20',
            due_date: '2025-11-15',
            days_overdue: 38,
            amount: 5200.00,
            age_bucket: '31-60 Days',
            urgency: 'high',
            contact_email: 'billing@beta.com'
        },
        {
            client_name: 'Gamma Inc',
            invoice_number: 'INV-1236',
            invoice_date: '2025-09-01',
            due_date: '2025-09-01',
            days_overdue: 113,
            amount: 8900.00,
            age_bucket: '90+ Days',
            urgency: 'critical',
            contact_email: 'finance@gamma.com'
        },
        {
            client_name: 'Delta Co',
            invoice_number: 'INV-1237',
            invoice_date: '2025-12-05',
            due_date: '2025-12-10',
            days_overdue: 13,
            amount: 1200.00,
            age_bucket: '1-30 Days',
            urgency: 'low',
            contact_email: 'accounts@delta.com'
        },
        {
            client_name: 'Epsilon Ltd',
            invoice_number: 'INV-1238',
            invoice_date: '2025-11-01',
            due_date: '2025-11-20',
            days_overdue: 33,
            amount: 3400.00,
            age_bucket: '31-60 Days',
            urgency: 'high',
            contact_email: 'ar@epsilon.com'
        }
    ]
};

// ===========================
// INITIALIZATION
// ===========================

document.addEventListener('DOMContentLoaded', function () {
    initializeReport();
});

function initializeReport() {
    showLoading();

    // Simulate API call
    setTimeout(() => {
        updateKPICards(sampleData.summary);
        initializeChart(sampleData.chart_data);
        initializeTable(sampleData.table_data);
        hideLoading();
    }, 500);
}

// ===========================
// KPI CARDS
// ===========================

function updateKPICards(summary) {
    document.getElementById('kpiTotalOutstanding').textContent =
        '$' + summary.total_outstanding.toLocaleString('en-US', { minimumFractionDigits: 2 });

    document.getElementById('kpiTotalInvoices').textContent = summary.total_invoices;
    document.getElementById('kpiOverdueCritical').textContent = summary.overdue_critical;
    document.getElementById('kpiAvgDays').textContent = summary.avg_days + ' days';

    // Update trends
    updateTrend('kpiTotalTrend', summary.trends.total_outstanding_change, 'up');
    updateTrend('kpiInvoicesTrend', summary.trends.invoice_count_change, 'down');
    updateTrend('kpiCriticalTrend', summary.trends.critical_count_change, 'up');
    updateTrend('kpiAvgDaysTrend', summary.trends.avg_days_change, 'neutral');
}

function updateTrend(elementId, change, direction) {
    const element = document.getElementById(elementId);
    const iconClass = direction === 'up' ? 'fa-arrow-up' : direction === 'down' ? 'fa-arrow-down' : 'fa-equals';
    const changeText = Math.abs(change) + '%';

    element.className = 'xero-kpi-trend ' + direction;
    element.innerHTML = `<i class="fas ${iconClass}"></i> ${changeText} vs last month`;
}

// ===========================
// CHART - APEXCHARTS
// ===========================

function initializeChart(chartData) {
    const options = getChartOptions(currentChartType, chartData);

    if (reportChart) {
        reportChart.destroy();
    }

    reportChart = new ApexCharts(document.querySelector("#xeroReportChart"), options);
    reportChart.render();
}

function getChartOptions(type, chartData) {
    const baseOptions = {
        chart: {
            height: 450,
            background: 'transparent',
            foreColor: '#b8bcc8',
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    selection: false,
                    zoom: false,
                    zoomin: false,
                    zoomout: false,
                    pan: false,
                    reset: false
                },
                export: {
                    csv: {
                        filename: 'aged-receivables-' + new Date().toISOString().split('T')[0]
                    },
                    svg: {
                        filename: 'aged-receivables-chart'
                    },
                    png: {
                        filename: 'aged-receivables-chart'
                    }
                }
            },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            }
        },
        theme: {
            mode: 'dark'
        },
        colors: chartData.colors,
        legend: {
            show: true,
            position: 'bottom',
            fontSize: '14px',
            labels: {
                colors: '#ffffff'
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 0 });
            },
            style: {
                fontSize: '12px',
                fontWeight: 'bold',
                colors: ['#fff']
            }
        },
        tooltip: {
            theme: 'dark',
            y: {
                formatter: function (val) {
                    return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2 });
                }
            }
        },
        grid: {
            borderColor: '#444'
        }
    };

    if (type === 'bar') {
        return {
            ...baseOptions,
            chart: {
                ...baseOptions.chart,
                type: 'bar'
            },
            series: [{
                name: 'Amount Outstanding',
                data: chartData.values
            }],
            plotOptions: {
                bar: {
                    horizontal: true,
                    distributed: true,
                    borderRadius: 4,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            xaxis: {
                categories: chartData.labels,
                labels: {
                    formatter: function (val) {
                        return '$' + (val / 1000) + 'K';
                    },
                    style: {
                        colors: '#b8bcc8'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: '#b8bcc8'
                    }
                }
            }
        };
    } else if (type === 'pie' || type === 'donut') {
        return {
            ...baseOptions,
            chart: {
                ...baseOptions.chart,
                type: 'pie'
            },
            series: chartData.values,
            labels: chartData.labels,
            plotOptions: {
                pie: {
                    donut: {
                        size: type === 'donut' ? '65%' : '0%',
                        labels: {
                            show: type === 'donut',
                            total: {
                                show: true,
                                label: 'Total Outstanding',
                                fontSize: '16px',
                                fontWeight: 600,
                                color: '#ffffff',
                                formatter: function (w) {
                                    const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                    return '$' + total.toLocaleString('en-US', { minimumFractionDigits: 2 });
                                }
                            }
                        }
                    }
                }
            }
        };
    }
}

function changeChartType() {
    currentChartType = document.getElementById('chartType').value;
    initializeChart(sampleData.chart_data);
}

function exportChartPNG() {
    reportChart.dataURI().then(({ imgURI }) => {
        const link = document.createElement('a');
        link.href = imgURI;
        link.download = 'aged-receivables-chart.png';
        link.click();
    });
}

function exportChartSVG() {
    reportChart.dataURI({ type: 'svg' }).then(({ imgURI }) => {
        const link = document.createElement('a');
        link.href = imgURI;
        link.download = 'aged-receivables-chart.svg';
        link.click();
    });
}

// ===========================
// TABLE - TABULATOR
// ===========================

function initializeTable(tableData) {
    reportTable = new Tabulator("#xeroReportTable", {
        data: tableData,
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 50,
        paginationSizeSelector: [25, 50, 100, 200],
        movableColumns: true,
        resizableColumns: true,
        columns: [
            {
                title: "Client Name",
                field: "client_name",
                sorter: "string",
                headerFilter: "input"
            },
            {
                title: "Invoice #",
                field: "invoice_number",
                sorter: "string",
                headerFilter: "input"
            },
            {
                title: "Invoice Date",
                field: "invoice_date",
                sorter: "date"
            },
            {
                title: "Due Date",
                field: "due_date",
                sorter: "date"
            },
            {
                title: "Days Overdue",
                field: "days_overdue",
                sorter: "number",
                formatter: function (cell) {
                    const val = cell.getValue();
                    const urgency = cell.getData().urgency;
                    let badgeClass = 'xero-badge-gray';

                    if (urgency === 'critical') badgeClass = 'xero-badge-red';
                    else if (urgency === 'high') badgeClass = 'xero-badge-orange';
                    else if (urgency === 'medium') badgeClass = 'xero-badge-yellow';
                    else if (urgency === 'low') badgeClass = 'xero-badge-green';

                    return `<span class="xero-badge ${badgeClass}">${val} days</span>`;
                }
            },
            {
                title: "Amount",
                field: "amount",
                sorter: "number",
                formatter: "money",
                formatterParams: {
                    decimal: ".",
                    thousand: ",",
                    symbol: "$",
                    precision: 2
                }
            },
            {
                title: "Age Bucket",
                field: "age_bucket",
                sorter: "string",
                formatter: function (cell) {
                    const val = cell.getValue();
                    const urgency = cell.getData().urgency;
                    let badgeClass = 'xero-badge-gray';

                    if (urgency === 'critical') badgeClass = 'xero-badge-red';
                    else if (urgency === 'high') badgeClass = 'xero-badge-orange';
                    else if (urgency === 'medium') badgeClass = 'xero-badge-yellow';
                    else if (urgency === 'low') badgeClass = 'xero-badge-green';

                    return `<span class="xero-badge ${badgeClass}">${val}</span>`;
                }
            },
            {
                title: "Actions",
                formatter: function () {
                    return '<button class="xero-btn-action" onclick="viewInvoice(this)">View</button> <button class="xero-btn-action" onclick="emailClient(this)">Email</button>';
                },
                headerSort: false,
                width: 180
            }
        ]
    });

    // Search functionality
    document.getElementById('tableSearch').addEventListener('keyup', function () {
        reportTable.setFilter([
            { field: "client_name", type: "like", value: this.value },
            { field: "invoice_number", type: "like", value: this.value }
        ]);
    });
}

function exportToCSV() {
    reportTable.download("csv", "aged-receivables-" + new Date().toISOString().split('T')[0] + ".csv");
}

function exportToExcel() {
    reportTable.download("xlsx", "aged-receivables-" + new Date().toISOString().split('T')[0] + ".xlsx", { sheetName: "Aged Receivables" });
}

// ===========================
// TABLE ACTIONS
// ===========================

function viewInvoice(btn) {
    const row = reportTable.getRow(btn.closest('.tabulator-row'));
    const data = row.getData();
    alert('View Invoice: ' + data.invoice_number + '\nClient: ' + data.client_name + '\nAmount: $' + data.amount);
    // Replace with actual navigation or modal
}

function emailClient(btn) {
    const row = reportTable.getRow(btn.closest('.tabulator-row'));
    const data = row.getData();
    window.location.href = `mailto:${data.contact_email}?subject=Invoice ${data.invoice_number} - Payment Reminder&body=Dear ${data.client_name},%0D%0A%0D%0AThis is a reminder that invoice ${data.invoice_number} for $${data.amount} is ${data.days_overdue} days overdue.%0D%0A%0D%0APlease arrange payment at your earliest convenience.`;
}

// ===========================
// UTILITIES
// ===========================

function updateReport() {
    showLoading();

    const dateRange = document.getElementById('dateRange').value;
    const businessId = document.getElementById('businessFilter').value;

    // Make API call here
    // Example: fetch(`/api/xero/reports/aged-receivables?days=${dateRange}&business_id=${businessId}`)

    // Simulate API call
    setTimeout(() => {
        // Update with new data
        hideLoading();
        console.log('Report updated! (Date Range: ' + dateRange + ' days, Business: ' + businessId + ')');
    }, 1000);
}

function showSettings() {
    alert('Settings panel coming soon!');
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Update timestamp
setInterval(() => {
    const now = new Date();
    const minutes = Math.floor((now - new Date(now - 2 * 60000)) / 60000);
    document.getElementById('lastUpdated').textContent = minutes + ' mins ago';
}, 60000);
