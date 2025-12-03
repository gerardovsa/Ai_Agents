"""
ToolRegistry diagnostic helper
Run this locally or on the server to list loaded schemas, implementations,
and tools that lack implementations.
"""
from tools.registry import ToolRegistry


def main():
    print("Initializing ToolRegistry for diagnostics...")
    registry = ToolRegistry()

    print('\nSummary:')
    print(f"  Total tool schemas: {len(registry.tools)}")
    print(f"  Total implementation modules: {len(registry.implementations)}")

    # Show first 20 platforms
    platforms = registry.get_all_platforms()
    print(f"  Platforms (sample 20): {platforms[:20]}")

    # Find tools whose implementation module is missing
    missing_impl = {}
    for tool_name, schema in registry.tools.items():
        platform = schema.get('platform')
        if not platform:
            missing_impl.setdefault('UNKNOWN', []).append(tool_name)
            continue
        if platform not in registry.implementations and not registry.implementations.get(f"{platform}_tools"):
            missing_impl.setdefault(platform, []).append(tool_name)

    if missing_impl:
        print('\nTools without implementations:')
        for platform, tools in missing_impl.items():
            print(f"  {platform}: {len(tools)} tools (examples: {tools[:5]})")
    else:
        print('\nAll tools have matching implementations loaded.')


if __name__ == '__main__':
    main()
