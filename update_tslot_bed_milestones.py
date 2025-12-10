#!/usr/bin/env python3
"""
Update T-slot bed frame milestones with proper names using direct API calls
"""

import requests
import json
import os

SESSION_ID = "sess_20251209_1740_t-slot_expanding_bed_frame_-_f"
API_BASE = os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com').rstrip('/')
SYNERGY_API = f"{API_BASE}/api/synergy"

# Milestone names for the T-slot expanding bed frame project
MILESTONE_NAMES = {
    1: "Engineering Calculations & Load Analysis",
    2: "CAD Design & Technical Drawings",
    3: "Bill of Materials & Australian Supplier Sourcing",
    4: "Assembly Instructions & Manufacturing Process",
    5: "AI Continuation Instructions & Knowledge Transfer"
}

def main():
    print(f"🔧 Updating T-slot bed frame project: {SESSION_ID}\n")
    
    # Step 1: Get current milestones
    print("📊 Fetching current milestones...")
    try:
        response = requests.get(f"{SYNERGY_API}/{SESSION_ID}/milestones", timeout=10)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"❌ Failed to get milestones: {e}")
        return
    
    milestones = result.get('milestones', [])
    print(f"✅ Found {len(milestones)} milestones\n")
    
    # Step 2: Update each milestone with proper names using field/value format
    print("✏️  Updating milestone names...")
    for milestone in milestones:
        milestone_id = milestone['milestone_id']
        milestone_num = milestone['milestone_number']
        current_name = milestone.get('milestone_name', 'Unnamed')
        new_name = MILESTONE_NAMES.get(milestone_num, f"Milestone {milestone_num}")
        
        print(f"   M{milestone_num}: '{current_name}' → '{new_name}'")
        
        # Use the inline edit format: {"field": "milestone_name", "value": "New Name"}
        try:
            response = requests.patch(
                f"{SYNERGY_API}/milestone/{milestone_id}/update",
                json={"field": "milestone_name", "value": new_name},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            print(f"      ✅ Updated")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
    
    print("\n🎉 Milestone names updated!")
    print(f"\n📍 View dashboard: https://ai-agents-backend-singapore.onrender.com")
    print(f"   Session: {SESSION_ID}")
    
    # Step 3: Show what documents need to be created
    print("\n📄 Documents to create:")
    print("   1️⃣  Milestone 1: Beam deflection calculations, load analysis spreadsheet")
    print("   2️⃣  Milestone 2: 3D CAD models (T-slot connections, expandable mechanism)")
    print("   3️⃣  Milestone 3: BOM with Bunnings/local supplier part numbers + costs")
    print("   4️⃣  Milestone 4: Step-by-step assembly guide with diagrams")
    print("   5️⃣  Milestone 5: AI handoff document (design decisions, open questions)")
    
    print("\n💡 Next: Create engineering documents for each milestone")

if __name__ == "__main__":
    main()
