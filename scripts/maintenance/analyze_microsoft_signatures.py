"""
Analyze Microsoft tool method signatures to determine which ones need user_id wrapping
"""

import re
from pathlib import Path


def analyze_method_signatures(file_path: Path) -> dict:
    """Analyze method signatures in a Microsoft tools file"""
    content = file_path.read_text(encoding='utf-8-sig')
    
    # Find class name
    class_match = re.search(r'class (Microsoft\w+Tools):', content)
    if not class_match:
        return {}
    class_name = class_match.group(1)
    
    # Find all method definitions: def method_name(self, [user_id: str,] ...
    methods = {}
    pattern = r'def (\w+)\(self(?:, (user_id: str))?(?:, (.*?))?(?:\)|\n)'
    
    for match in re.finditer(pattern, content):
        method_name = match.group(1)
        has_user_id = match.group(2) is not None
        other_params = match.group(3) or ""
        methods[method_name] = {
            'has_user_id': has_user_id,
            'other_params': other_params.strip()
        }
    
    return methods


def main():
    base_path = Path("c:/Users/gpoli/GIT/AI_agents")
    impl_path = base_path / "tools" / "implementations"
    
    microsoft_files = [
        "microsoft_teams_tools.py",
        "microsoft_calendar_tools.py",
        "microsoft_onedrive_tools.py",
        "microsoft_word_tools.py",
        "microsoft_excel_tools.py",
        "microsoft_forms_tools.py",
        "microsoft_onenote_tools.py",
        "microsoft_sharepoint_tools.py",
        "microsoft_todo_tools.py",
        "microsoft_outlook_tools.py",
    ]
    
    print("=" * 100)
    print("MICROSOFT TOOLS METHOD SIGNATURE ANALYSIS")
    print("=" * 100)
    print()
    
    for filename in microsoft_files:
        file_path = impl_path / filename
        if not file_path.exists():
            print(f"❌ {filename}: Not found")
            continue
        
        methods = analyze_method_signatures(file_path)
        
        # Count how many have user_id
        has_user_id_count = sum(1 for m in methods.values() if m['has_user_id'])
        total_count = len(methods)
        
        print(f"\n{filename}")
        print(f"  Total methods: {total_count}")
        print(f"  Methods with user_id: {has_user_id_count}")
        print(f"  Methods without user_id: {total_count - has_user_id_count}")
        
        if has_user_id_count == total_count:
            print(f"  ✅ ALL methods have user_id (use user_id wrapper)")
        elif has_user_id_count == 0:
            print(f"  ⚠️  NO methods have user_id (use pass-through wrapper)")
        else:
            print(f"  🔀 MIXED (some have, some don't - needs careful handling)")
            print(f"     Methods WITH user_id:")
            for name, info in methods.items():
                if info['has_user_id']:
                    print(f"       - {name}")
            print(f"     Methods WITHOUT user_id:")
            for name, info in methods.items():
                if not info['has_user_id']:
                    print(f"       - {name}")


if __name__ == "__main__":
    main()
