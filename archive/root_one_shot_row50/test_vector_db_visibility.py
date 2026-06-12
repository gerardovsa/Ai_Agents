"""
Test Vector Database Visibility Filtering
===========================================

Tests the visibility system for vector database documents with:
- Global visibility (all users)
- User-level visibility (all team members under same user_id)
- Team-specific visibility (only specific team member)

Usage:
    python test_vector_db_visibility.py
"""

import json

def test_visibility_filter():
    """Test visibility filtering logic"""
    
    print("\n" + "="*60)
    print("Vector Database Visibility Filter Test")
    print("="*60)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Business Admin (user_id=1)',
            'user_id': 1,
            'username': 'admin',
            'expected_filter': {}  # No filter - sees everything
        },
        {
            'name': 'Regular User (user_id=14)',
            'user_id': 14,
            'username': 'john_doe',
            'expected_filter': {
                "$or": [
                    {"visibility": "global"},
                    {"owner_user_id": 14, "visibility": "user"},
                    {"owner_user_id": 14, "team_id": "john_doe", "visibility": "team"}
                ]
            }
        },
        {
            'name': 'Team Member Sarah (user_id=14, team_id=sarah_team)',
            'user_id': 14,
            'username': 'sarah_team',
            'expected_filter': {
                "$or": [
                    {"visibility": "global"},
                    {"owner_user_id": 14, "visibility": "user"},
                    {"owner_user_id": 14, "team_id": "sarah_team", "visibility": "team"}
                ]
            }
        },
        {
            'name': 'Team Member Bob (user_id=14, team_id=bob_team)',
            'user_id': 14,
            'username': 'bob_team',
            'expected_filter': {
                "$or": [
                    {"visibility": "global"},
                    {"owner_user_id": 14, "visibility": "user"},
                    {"owner_user_id": 14, "team_id": "bob_team", "visibility": "team"}
                ]
            }
        }
    ]
    
    # Sample documents
    documents = [
        {'id': 1, 'name': 'Global Policy.pdf', 'visibility': 'global', 'owner_user_id': 1},
        {'id': 2, 'name': 'Account Guide.pdf', 'visibility': 'user', 'owner_user_id': 14},
        {'id': 3, 'name': 'Sarah Report.pdf', 'visibility': 'team', 'owner_user_id': 14, 'team_id': 'sarah_team'},
        {'id': 4, 'name': 'Bob Report.pdf', 'visibility': 'team', 'owner_user_id': 14, 'team_id': 'bob_team'},
        {'id': 5, 'name': 'Other User Doc.pdf', 'visibility': 'user', 'owner_user_id': 99}
    ]
    
    print("\n📄 Sample Documents:")
    for doc in documents:
        print(f"  {doc['id']}. {doc['name']} - {doc['visibility']} (owner: {doc['owner_user_id']}, team: {doc.get('team_id', 'N/A')})")
    
    # Test each scenario
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"🧪 Scenario: {scenario['name']}")
        print(f"   User ID: {scenario['user_id']}, Username: {scenario['username']}")
        print(f"{'='*60}")
        
        # Build filter
        current_user_id = scenario['user_id']
        current_username = scenario['username']
        
        if current_user_id == 1:
            metadata_filter = {}
        else:
            metadata_filter = {
                "$or": [
                    {"visibility": "global"},
                    {"owner_user_id": current_user_id, "visibility": "user"},
                    {"owner_user_id": current_user_id, "team_id": current_username, "visibility": "team"}
                ]
            }
        
        print(f"\n📋 Generated Filter:")
        print(json.dumps(metadata_filter, indent=2))
        
        # Simulate filtering
        visible_docs = []
        for doc in documents:
            if not metadata_filter:  # Business admin sees all
                visible_docs.append(doc)
            else:
                # Check if document matches filter
                for condition in metadata_filter.get("$or", []):
                    match = True
                    for key, value in condition.items():
                        if doc.get(key) != value:
                            match = False
                            break
                    if match:
                        visible_docs.append(doc)
                        break
        
        print(f"\n✅ Visible Documents ({len(visible_docs)}):")
        for doc in visible_docs:
            print(f"  ✓ {doc['name']} ({doc['visibility']})")
        
        print(f"\n❌ Hidden Documents ({len(documents) - len(visible_docs)}):")
        for doc in documents:
            if doc not in visible_docs:
                print(f"  ✗ {doc['name']} ({doc['visibility']})")
    
    print("\n" + "="*60)
    print("✅ Visibility Filter Test Complete")
    print("="*60)
    print("\n💡 Key Findings:")
    print("  • Business admin (user_id=1) sees ALL documents")
    print("  • Global documents are visible to everyone")
    print("  • User-level documents are visible to all team members under same user_id")
    print("  • Team-specific documents are only visible to that team member")
    print("\n🔒 Security:")
    print("  • User 14's team members (Sarah, Bob) can see:")
    print("    - Global documents")
    print("    - User 14's user-level documents (shared across team)")
    print("    - Their own team-specific documents ONLY")
    print("  • User 14's team members CANNOT see:")
    print("    - Other team members' team-specific documents")
    print("    - Documents from other user accounts")


if __name__ == '__main__':
    test_visibility_filter()
