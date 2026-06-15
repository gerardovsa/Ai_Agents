"""
Test Calculator Pricing Management Queries
"""
from query_library import QueryLibrary
import json

print('='*80)
print('QUERY LIBRARY - CALCULATOR PRICING MANAGEMENT QUERIES TEST')
print('='*80)

q = QueryLibrary()

# Test 1: Verify queries exist
print('\n1. QUERY CATALOG VERIFICATION')
print('-'*80)
calc_queries = {k: v for k, v in q.query_catalog.items() if v.get('category') == 'Calculator Pricing Management'}
print(f'Total queries in catalog: {len(q.query_catalog)}')
print(f'Calculator Pricing queries: {len(calc_queries)}')
print(f'Query names: {list(calc_queries.keys())}')

# Test 2: Build SQL for each query
print('\n2. SQL GENERATION TESTS')
print('-'*80)
test_cases = [
    ('get_pricing_constant', {'parameter_name': 'impos_setup'}),
    ('get_pricing_constant', {'parameter_name': 'markup_multiplier', 'calculator_name': 'BollardSigns'}),
    ('get_calculator_config', {'calculator_name': 'BollardSigns'}),
    ('get_calculator_config', {'calculator_name': 'BusinessCards', 'include_product_options': False}),
    ('get_product_options_for_calculator', {'calculator_name': 'BusinessCards'}),
    ('get_product_options_for_calculator', {'calculator_name': 'PerfectBoundBooks', 'include_inactive': True}),
    ('find_high_variance_parameters', {'variance_threshold': 100}),
    ('find_high_variance_parameters', {'variance_threshold': 50, 'min_calculators': 5}),
    ('get_parameter_usage_map', {}),
    ('get_parameter_usage_map', {'parameter_name': 'impos_setup'}),
    ('search_product_options', {'search_term': 'size'}),
    ('search_product_options', {'calculator_name': 'BusinessCards', 'option_type': 'select'}),
    ('get_option_price_variance', {'min_choices': 3}),
    ('get_option_price_variance', {'calculator_name': 'BusinessCards'})
]

success_count = 0
for query_name, params in test_cases:
    try:
        result = q.build_query(query_name, **params)
        sql_length = len(result['sql'])
        returns = result['metadata']['returns']
        
        print(f'\n✅ {query_name}')
        print(f'   Params: {params}')
        print(f'   SQL: {sql_length} chars')
        print(f'   Returns: {returns[:100]}{"..." if len(returns) > 100 else ""}')
        
        # Verify SQL contains key elements
        sql = result['sql'].upper()
        if 'SELECT' in sql:
            print(f'   ✓ Contains SELECT')
        if 'FROM' in sql:
            print(f'   ✓ Contains FROM')
        if 'calculator_pricing_parameters' in result['sql'] or 'product_options' in result['sql']:
            print(f'   ✓ Queries calculator pricing tables')
            
        success_count += 1
    except Exception as e:
        print(f'\n❌ {query_name} with {params}')
        print(f'   Error: {str(e)}')

print('\n' + '='*80)
print(f'RESULTS: {success_count}/{len(test_cases)} tests passed')
print('='*80)

# Test 3: Verify metadata completeness
print('\n3. METADATA COMPLETENESS CHECK')
print('-'*80)
for name, meta in calc_queries.items():
    required_fields = ['category', 'description', 'parameters', 'returns', 'best_for', 'validated']
    missing = [f for f in required_fields if f not in meta]
    
    if missing:
        print(f'\n⚠️  {name}: Missing fields: {missing}')
    else:
        print(f'\n✅ {name}: All metadata present')
        print(f'   Description: {meta["description"][:80]}...')
        print(f'   Parameters: {list(meta["parameters"].keys())}')
        print(f'   Validated: {meta["validated"]}')

# Test 4: Sample SQL output
print('\n4. SAMPLE SQL OUTPUT')
print('-'*80)
print('\nQuery: get_pricing_constant (parameter_name="impos_setup")')
print('-'*40)
result = q.build_query('get_pricing_constant', parameter_name='impos_setup')
print(result['sql'])

print('\n' + '='*80)
print('TEST COMPLETE')
print('='*80)
