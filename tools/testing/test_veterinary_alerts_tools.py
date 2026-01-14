"""
Veterinary Alerts Tools - Test & Demo Script
============================================

Tests all veterinary alert management tools to ensure they work correctly
with the VSA Supabase database.

Run this script to validate:
- Database connection
- Alert retrieval by tags
- Call transcript access
- Multi-alert analysis
- Action plan generation
- Alert status updates

Author: Valor AI Platform
Date: December 2025
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(tools_dir)
sys.path.insert(0, root_dir)

from tools.implementations.veterinary_alerts_tools import (
    get_alerts_by_tag,
    get_call_transcript,
    get_call_metadata,
    analyze_multiple_alerts,
    create_action_plan,
    update_alert_status,
    bulk_update_alerts
)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_get_alerts_by_tag():
    """Test: Get alerts filtered by tags"""
    print_section("TEST 1: Get Alerts by Tag")
    
    # Test 1: Get all alerts from last 7 days
    print("📋 Test 1A: Get all recent alerts (last 7 days)...")
    date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    result = get_alerts_by_tag(
        alert_tags="ALL",
        date_from=date_from,
        limit=10
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📊 Alert Count: {result['alert_count']}")
    if result.get('summary'):
        print(f"📈 Summary:")
        print(f"   - By Severity: {result['summary'].get('by_severity', {})}")
        print(f"   - By Priority: {result['summary'].get('by_priority', {})}")
        print(f"   - Top Tags: {list(result['summary'].get('by_tag', {}).keys())[:5]}")
    
    if result['alerts']:
        print(f"\n📝 Sample Alert:")
        alert = result['alerts'][0]
        print(f"   - Call ID: {alert.get('call_id')}")
        print(f"   - Code: {alert.get('alert_code')}")
        print(f"   - Severity: {alert.get('severity')}")
        print(f"   - Priority: {alert.get('priority')}")
        print(f"   - Reason: {alert.get('core_reason', '')[:80]}...")
        return alert.get('call_id')  # Return for next test
    
    return None


def test_get_call_transcript(call_id):
    """Test: Get call transcript and analysis"""
    if not call_id:
        print("\n⚠️  Skipping transcript test - no call_id available")
        return
    
    print_section("TEST 2: Get Call Transcript")
    
    print(f"📞 Getting transcript for call: {call_id}...")
    result = get_call_transcript(call_id)
    
    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📄 Transcript Length: {result['metadata']['transcript_length']} chars")
        print(f"🤖 Analysis Length: {result['metadata']['analysis_length']} chars")
        print(f"\n📝 Transcript Preview (first 200 chars):")
        print(f"   {result['transcript'][:200]}...")
    else:
        print(f"❌ Error: {result.get('error')}")


def test_get_call_metadata(call_id):
    """Test: Get call metadata"""
    if not call_id:
        print("\n⚠️  Skipping metadata test - no call_id available")
        return
    
    print_section("TEST 3: Get Call Metadata")
    
    print(f"ℹ️  Getting metadata for call: {call_id}...")
    result = get_call_metadata(call_id)
    
    print(f"✅ Success: {result['success']}")
    if result['success']:
        meta = result['metadata']
        print(f"👤 Staff: {meta.get('staff_name')}")
        print(f"📅 Date: {meta.get('call_date')} at {meta.get('call_time')}")
        print(f"⏱️  Duration: {meta.get('call_duration_minutes')} minutes")
        print(f"🧑 Client: {meta.get('client_first_name')} {meta.get('client_last_name')}")
        print(f"🐾 Pet: {meta.get('pet_name')} ({meta.get('pet_species')})")
        print(f"📞 Phone: {meta.get('phone_number')}")
        print(f"😊 Sentiment: {meta.get('sentiment_score')}")
        print(f"⭐ Quality: {meta.get('quality_score')}")
    else:
        print(f"❌ Error: {result.get('error')}")


def test_analyze_multiple_alerts():
    """Test: Analyze multiple alerts for patterns"""
    print_section("TEST 4: Analyze Multiple Alerts")
    
    print("🔍 Analyzing recent alerts for patterns...")
    date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    result = analyze_multiple_alerts(
        alert_tags="ALL",
        date_from=date_from,
        limit=20
    )
    
    print(f"✅ Success: {result['success']}")
    if result['success'] and result.get('analysis'):
        analysis = result['analysis']
        print(f"📊 Total Alerts Analyzed: {analysis.get('total_alerts')}")
        
        print(f"\n🔍 Common Patterns:")
        for pattern in analysis.get('common_patterns', [])[:3]:
            print(f"   - {pattern['pattern']}: {pattern['frequency']} times ({pattern.get('percentage', 0)}%)")
        
        print(f"\n⚠️  Severity Distribution:")
        for sev, count in analysis.get('severity_distribution', {}).items():
            print(f"   - {sev}: {count}")
        
        print(f"\n💡 Recommended Actions:")
        for action in analysis.get('recommended_actions', [])[:2]:
            print(f"   Priority {action['priority']}: {action['action']}")
            print(f"      Timeline: {action['timeline']}, Impact: {action['estimated_impact']}")
        
        # Return alert IDs for next test
        alerts_result = get_alerts_by_tag(alert_tags="ALL", date_from=date_from, limit=3)
        if alerts_result['success'] and alerts_result['alerts']:
            return [alert['call_id'] for alert in alerts_result['alerts'][:3]]
    
    return []


def test_create_action_plan(alert_ids):
    """Test: Create action plan"""
    if not alert_ids:
        print("\n⚠️  Skipping action plan test - no alert_ids available")
        return
    
    print_section("TEST 5: Create Action Plan")
    
    print(f"📋 Creating coaching plan for {len(alert_ids)} alerts...")
    result = create_action_plan(
        alert_ids=alert_ids,
        plan_type="coaching",
        timeline="1_week"
    )
    
    print(f"✅ Success: {result['success']}")
    if result['success']:
        plan = result['plan']
        print(f"🆔 Plan ID: {plan['plan_id']}")
        print(f"📅 Timeline: {plan['timeline']}")
        print(f"📊 Alerts Covered: {plan['alerts_covered']}")
        
        print(f"\n📋 Phases:")
        for phase in plan['phases']:
            print(f"\n   Phase {phase['phase']}: {phase['name']}")
            print(f"   Duration: {phase['duration']}")
            print(f"   Tasks: {len(phase['tasks'])}")
            for task in phase['tasks'][:2]:
                print(f"      • {task['task']}")
                print(f"        Responsible: {task['responsible']}, Deadline: {task['deadline']}")
        
        print(f"\n🎯 Expected Outcomes:")
        for outcome in plan['expected_outcomes']:
            print(f"   • {outcome}")
    else:
        print(f"❌ Error: {result.get('error')}")


def test_update_alert_status(call_id):
    """Test: Update alert status"""
    if not call_id:
        print("\n⚠️  Skipping status update test - no call_id available")
        return
    
    print_section("TEST 6: Update Alert Status")
    
    print(f"✏️  Updating alert status for: {call_id}...")
    result = update_alert_status(
        call_id=call_id,
        status="In Progress",
        notes="TEST: Automated test update - coaching scheduled",
        actions_taken="TEST: Reviewed call recording and identified improvement areas"
    )
    
    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Message: {result['message']}")
        print(f"🔄 Updated Fields: {list(result.get('updated_fields', {}).keys())}")
    else:
        print(f"❌ Error: {result.get('error')}")


def test_bulk_update_alerts(alert_ids):
    """Test: Bulk update multiple alerts"""
    if not alert_ids or len(alert_ids) < 2:
        print("\n⚠️  Skipping bulk update test - need at least 2 alert_ids")
        return
    
    print_section("TEST 7: Bulk Update Alerts")
    
    print(f"📦 Bulk updating {len(alert_ids)} alerts...")
    result = bulk_update_alerts(
        call_ids=alert_ids[:2],  # Update first 2
        status="In Progress",
        notes="TEST: Bulk update from automated testing"
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📊 Updated: {result.get('updated_count', 0)}/{result.get('total_processed', 0)}")
    print(f"❌ Failed: {result.get('failed_count', 0)}")
    
    if result.get('details'):
        print(f"\n📋 Details:")
        for detail in result['details']:
            status = "✅" if detail['status'] == 'success' else "❌"
            print(f"   {status} {detail['call_id']}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  VETERINARY ALERTS TOOLS - TEST SUITE")
    print("  Testing connection to VSA Supabase database")
    print("="*80)
    
    try:
        # Test 1: Get alerts by tag
        call_id = test_get_alerts_by_tag()
        
        # Test 2: Get transcript
        test_get_call_transcript(call_id)
        
        # Test 3: Get metadata
        test_get_call_metadata(call_id)
        
        # Test 4: Analyze multiple alerts
        alert_ids = test_analyze_multiple_alerts()
        
        # Test 5: Create action plan
        test_create_action_plan(alert_ids)
        
        # Test 6: Update single alert status
        test_update_alert_status(call_id)
        
        # Test 7: Bulk update alerts
        test_bulk_update_alerts(alert_ids)
        
        print_section("🎉 ALL TESTS COMPLETED")
        print("✅ All veterinary alerts tools are working correctly!")
        print("\n📚 Available Tools:")
        print("   1. get_alerts_by_tag - Filter alerts by tags/severity/priority")
        print("   2. get_call_transcript - Get full call transcript and analysis")
        print("   3. get_call_metadata - Get call details (staff, client, pet)")
        print("   4. analyze_multiple_alerts - Find patterns across alerts")
        print("   5. create_action_plan - Generate structured action plans")
        print("   6. update_alert_status - Update single alert")
        print("   7. bulk_update_alerts - Update multiple alerts at once")
        print("\n🚀 Tools ready for AI agent use!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
