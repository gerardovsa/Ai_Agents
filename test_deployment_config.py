"""
Test script for deployment configuration and module filtering

Tests:
1. Environment detection
2. Module filtering logic
3. Module registry integration
4. Local vs Render behavior

Run:
    python test_deployment_config.py
"""
import os
import sys

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from AI_infrastructure.config.deployment_config import (
    get_environment_name,
    get_disabled_modules,
    is_module_enabled,
    get_module_filter_stats,
    IS_LOCAL,
    IS_RENDER,
    IS_PRODUCTION
)

def test_environment_detection():
    """Test environment detection logic"""
    print("\n" + "="*60)
    print("TEST 1: Environment Detection")
    print("="*60)
    
    env_name = get_environment_name()
    print(f"✅ Current environment: {env_name.upper()}")
    print(f"   IS_LOCAL: {IS_LOCAL}")
    print(f"   IS_RENDER: {IS_RENDER}")
    print(f"   IS_PRODUCTION: {IS_PRODUCTION}")
    
    # Show environment variables
    print(f"\n📋 Environment Variables:")
    print(f"   RENDER = {os.environ.get('RENDER', 'not set')}")
    print(f"   FLASK_ENV = {os.environ.get('FLASK_ENV', 'not set')}")


def test_module_filtering():
    """Test module filtering logic"""
    print("\n" + "="*60)
    print("TEST 2: Module Filtering")
    print("="*60)
    
    disabled = get_disabled_modules()
    print(f"✅ Disabled modules ({len(disabled)}):")
    for module_id in disabled:
        print(f"   ⏸️  {module_id}")
    
    if not disabled:
        print("   (none - all modules enabled)")
    
    # Test specific modules
    print(f"\n📊 Module Status:")
    test_modules = [
        'parametric-cad',
        'veterinary_alerts',
        'voip-demo',
        'inhouse-kanban',
        'github',
        'debug-module',
        'agents',
        'synergy'
    ]
    
    for module_id in test_modules:
        enabled = is_module_enabled(module_id)
        status = "✅ ENABLED" if enabled else "⏸️  DISABLED"
        print(f"   {status}: {module_id}")


def test_filter_stats():
    """Test filter statistics"""
    print("\n" + "="*60)
    print("TEST 3: Filter Statistics")
    print("="*60)
    
    stats = get_module_filter_stats()
    
    print(f"✅ Environment: {stats['environment'].upper()}")
    print(f"   Disabled modules: {stats['disabled_count']}")
    print(f"   Always enabled modules: {stats['always_enabled_count']}")
    
    if stats['disabled_modules']:
        print(f"\n⏸️  Disabled Modules:")
        for module_id in stats['disabled_modules']:
            print(f"   - {module_id}")


def test_module_registry():
    """Test module registry integration"""
    print("\n" + "="*60)
    print("TEST 4: Module Registry Integration")
    print("="*60)
    
    try:
        from AI_infrastructure.core.module_registry import get_module_registry
        
        registry = get_module_registry()
        registry._ensure_initialized()
        
        all_modules = registry.get_all_modules()
        print(f"✅ Module registry initialized")
        print(f"   Total registered modules: {len(all_modules)}")
        
        # Show registered modules
        print(f"\n📦 Registered Modules:")
        for module in all_modules:
            print(f"   - {module.id} (v{module.version})")
        
        # Check if disabled modules are absent
        disabled = get_disabled_modules()
        registered_ids = [m.id for m in all_modules]
        
        print(f"\n🔍 Verification:")
        for module_id in disabled:
            if module_id in registered_ids:
                print(f"   ❌ FAIL: {module_id} should be disabled but is registered!")
            else:
                print(f"   ✅ PASS: {module_id} correctly excluded from registry")
        
    except Exception as e:
        print(f"❌ Error loading module registry: {e}")
        import traceback
        traceback.print_exc()


def simulate_render_environment():
    """Simulate Render deployment environment"""
    print("\n" + "="*60)
    print("TEST 5: Render Environment Simulation")
    print("="*60)
    
    # Save original environment
    original_render = os.environ.get('RENDER')
    original_flask_env = os.environ.get('FLASK_ENV')
    
    # Set Render environment
    os.environ['RENDER'] = 'true'
    os.environ['FLASK_ENV'] = 'production'
    
    print("🌐 Simulating Render deployment (RENDER=true, FLASK_ENV=production)")
    
    # Reimport to get new environment detection
    import importlib
    import AI_infrastructure.config.deployment_config as config_module
    importlib.reload(config_module)
    
    from AI_infrastructure.config.deployment_config import (
        get_environment_name as get_env_sim,
        get_disabled_modules as get_disabled_sim,
        IS_RENDER as IS_RENDER_SIM
    )
    
    env_name = get_env_sim()
    disabled = get_disabled_sim()
    
    print(f"   Environment: {env_name.upper()}")
    print(f"   IS_RENDER: {IS_RENDER_SIM}")
    print(f"   Disabled modules: {len(disabled)}")
    
    for module_id in disabled:
        print(f"   ⏸️  {module_id}")
    
    # Restore original environment
    if original_render is None:
        os.environ.pop('RENDER', None)
    else:
        os.environ['RENDER'] = original_render
    
    if original_flask_env is None:
        os.environ.pop('FLASK_ENV', None)
    else:
        os.environ['FLASK_ENV'] = original_flask_env
    
    # Reload to restore original state
    importlib.reload(config_module)
    
    print("\n✅ Environment restored to original state")


def main():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("DEPLOYMENT CONFIGURATION TEST SUITE")
    print("🧪"*30)
    
    try:
        test_environment_detection()
        test_module_filtering()
        test_filter_stats()
        test_module_registry()
        simulate_render_environment()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nNext steps:")
        print("1. Review disabled modules list")
        print("2. Test Flask app startup: python AI_infrastructure/flask_app.py")
        print("3. Deploy to Render with RENDER=true environment variable")
        print("4. Verify modules are correctly filtered in production")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
