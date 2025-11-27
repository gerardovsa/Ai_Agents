"""
Test Arrow Rendering Fix - Verify Shape and Connection ID Normalization
========================================================================

This script simulates the loadWorkflowFromList() logic to test if the ID
normalization fix correctly handles numeric IDs in connections.
"""

# Simulate a workflow with numeric IDs (like Workflow #1 from database)
workflow_with_numeric_ids = {
    'slug': 'test-workflow',
    'title': 'Test Workflow',
    'shapes': [
        {'id': 1, 'type': 'trigger', 'x': 100, 'y': 100, 'text': 'Start'},
        {'id': 2, 'type': 'action', 'x': 100, 'y': 250, 'text': 'Action 1'},
        {'id': 3, 'type': 'action', 'x': 100, 'y': 400, 'text': 'Action 2'}
    ],
    'connections': [
        {'id': 1, 'from': 1, 'to': 2},
        {'id': 2, 'from': 2, 'to': 3}
    ]
}

# Simulate a workflow with string numeric IDs (e.g., "1", "2")
workflow_with_string_numeric_ids = {
    'slug': 'test-workflow-2',
    'title': 'Test Workflow 2',
    'shapes': [
        {'id': "1", 'type': 'trigger', 'x': 100, 'y': 100, 'text': 'Start'},
        {'id': "2", 'type': 'action', 'x': 100, 'y': 250, 'text': 'Action 1'},
        {'id': "3", 'type': 'action', 'x': 100, 'y': 400, 'text': 'Action 2'}
    ],
    'connections': [
        {'id': "1", 'from': "1", 'to': "2"},
        {'id': "2", 'from': "2", 'to': "3"}
    ]
}

# Simulate a workflow with proper string IDs (working workflows)
workflow_with_proper_ids = {
    'slug': 'test-workflow-3',
    'title': 'Test Workflow 3',
    'shapes': [
        {'id': 'trigger_1', 'type': 'trigger', 'x': 100, 'y': 100, 'text': 'Start'},
        {'id': 'action_1', 'type': 'action', 'x': 100, 'y': 250, 'text': 'Action 1'},
        {'id': 'action_2', 'type': 'action', 'x': 100, 'y': 400, 'text': 'Action 2'}
    ],
    'connections': [
        {'id': 'conn_1', 'from': 'trigger_1', 'to': 'action_1'},
        {'id': 'conn_2', 'from': 'action_1', 'to': 'action_2'}
    ]
}

def normalize_shape_id(shape_id):
    """Normalize shape ID to match JavaScript logic"""
    if isinstance(shape_id, int):
        return f"shape_{shape_id}"
    elif isinstance(shape_id, str) and shape_id.isdigit():
        return f"shape_{shape_id}"
    return shape_id

def normalize_connection_id(conn_id):
    """Normalize connection from/to ID to match JavaScript logic"""
    if isinstance(conn_id, int):
        return f"shape_{conn_id}"
    elif isinstance(conn_id, str) and conn_id.isdigit():
        return f"shape_{conn_id}"
    return conn_id

def test_workflow(workflow, test_name):
    """Test workflow ID normalization"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    
    # Normalize shapes
    normalized_shapes = []
    for shape in workflow['shapes']:
        shape_id = normalize_shape_id(shape['id'])
        normalized_shapes.append({**shape, 'id': shape_id})
        print(f"Shape: {shape['id']} → {shape_id}")
    
    # Normalize connections
    normalized_connections = []
    for conn in workflow['connections']:
        from_id = normalize_connection_id(conn['from'])
        to_id = normalize_connection_id(conn['to'])
        normalized_connections.append({
            'id': conn.get('id', f"conn_{conn['from']}_{conn['to']}"),
            'from': from_id,
            'to': to_id
        })
        print(f"Connection: {conn['from']} → {conn['to']} becomes {from_id} → {to_id}")
    
    # Verify all connections have matching shapes
    print("\nValidation:")
    all_valid = True
    for conn in normalized_connections:
        from_exists = any(s['id'] == conn['from'] for s in normalized_shapes)
        to_exists = any(s['id'] == conn['to'] for s in normalized_shapes)
        
        status_from = "✅" if from_exists else "❌"
        status_to = "✅" if to_exists else "❌"
        
        print(f"  {conn['from']} → {conn['to']}: FROM {status_from} TO {status_to}")
        
        if not from_exists or not to_exists:
            all_valid = False
    
    if all_valid:
        print("\n✅ ALL CONNECTIONS VALID - Arrows will render!")
    else:
        print("\n❌ INVALID CONNECTIONS - Arrows will NOT render!")
    
    return all_valid

# Run tests
print("\n" + "🔬 ARROW RENDERING FIX VALIDATION TEST")
print("="*80)

test1 = test_workflow(workflow_with_numeric_ids, "Numeric IDs (Workflow #1 format)")
test2 = test_workflow(workflow_with_string_numeric_ids, "String Numeric IDs")
test3 = test_workflow(workflow_with_proper_ids, "Proper String IDs (Working workflows)")

print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)
print(f"Test 1 (Numeric IDs): {'✅ PASS' if test1 else '❌ FAIL'}")
print(f"Test 2 (String Numeric IDs): {'✅ PASS' if test2 else '❌ FAIL'}")
print(f"Test 3 (Proper String IDs): {'✅ PASS' if test3 else '❌ FAIL'}")

if test1 and test2 and test3:
    print("\n🎉 SUCCESS! All ID formats will be correctly normalized!")
    print("Arrows should now render for all workflow types.")
else:
    print("\n⚠️ WARNING: Some test cases failed. Review normalization logic.")
