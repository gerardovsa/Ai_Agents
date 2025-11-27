"""
Tool Quality Audit Script - Analyze all tools against Platform Tool Suite Construction Agent standards

Checks for:
1. Schema completeness (description, parameters, returns, examples, usage_guide)
2. Implementation existence
3. Inline guidance quality
4. Anthropic format compatibility
5. Naming conventions
6. Documentation standards

Usage:
    python tool_quality_audit.py                    # Full audit
    python tool_quality_audit.py --platform google  # Platform filter
    python tool_quality_audit.py --detailed         # Detailed output
    python tool_quality_audit.py --export report.md # Export results
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

from tools.registry_v3 import RegistryV3


class ToolQualityAuditor:
    """Audit tool quality against Platform Tool Suite Construction Agent standards"""
    
    def __init__(self):
        self.registry = RegistryV3()
        self.results = {
            'total_tools': len(self.registry.tools),
            'platforms': {},
            'issues': defaultdict(list),
            'scores': {}
        }
    
    def audit_tool(self, tool_name: str, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Audit single tool against standards"""
        issues = []
        scores = {}
        
        # 1. Check description quality (should be 200-300 words)
        description = tool.get('description', '')
        word_count = len(description.split())
        if word_count < 50:
            issues.append(f"Description too short ({word_count} words, need 200+)")
            scores['description'] = 25
        elif word_count < 100:
            issues.append(f"Description needs expansion ({word_count} words, target 200+)")
            scores['description'] = 50
        elif word_count < 200:
            scores['description'] = 75
        else:
            scores['description'] = 100
        
        # 2. Check for reinforcement rule
        if '⚠️ MUST USE: execute_tool(' not in description:
            issues.append("Missing reinforcement rule (⚠️ MUST USE: execute_tool...)")
            scores['reinforcement'] = 0
        else:
            scores['reinforcement'] = 100
        
        # 3. Check parameters structure
        params = tool.get('parameters', {})
        if not params:
            issues.append("Missing parameters definition")
            scores['parameters'] = 0
        elif 'type' in params and params['type'] == 'object':
            # Anthropic format (good)
            props = params.get('properties', {})
            required = params.get('required', [])
            
            if not props:
                issues.append("Parameters has no properties")
                scores['parameters'] = 25
            else:
                # Check each parameter has description
                missing_desc = [p for p in props if 'description' not in props[p]]
                if missing_desc:
                    issues.append(f"Parameters missing descriptions: {', '.join(missing_desc[:3])}")
                    scores['parameters'] = 75
                else:
                    scores['parameters'] = 100
        else:
            # Legacy format (acceptable but not ideal)
            if not any(p.get('description') for p in params.values() if isinstance(p, dict)):
                issues.append("Parameters missing descriptions")
                scores['parameters'] = 50
            else:
                scores['parameters'] = 75
        
        # 4. Check examples
        examples = tool.get('examples', [])
        if not examples:
            issues.append("Missing examples (need 3+)")
            scores['examples'] = 0
        elif len(examples) < 2:
            issues.append(f"Only {len(examples)} examples (need 3+)")
            scores['examples'] = 33
        elif len(examples) < 3:
            scores['examples'] = 66
        else:
            # Check example quality
            has_simple = any('simple' in e.get('description', '').lower() for e in examples)
            has_complex = any('complex' in e.get('description', '').lower() or 'advanced' in e.get('description', '').lower() for e in examples)
            has_error = any('error' in e.get('description', '').lower() for e in examples)
            
            if has_simple and has_complex and has_error:
                scores['examples'] = 100
            elif len(examples) >= 3:
                scores['examples'] = 85
            else:
                scores['examples'] = 70
        
        # 5. Check usage_guide
        usage_guide = tool.get('usage_guide', {})
        if not usage_guide:
            issues.append("Missing usage_guide (need when_to_use, workflow, best_practices, error_handling, related_tools)")
            scores['usage_guide'] = 0
        else:
            required_sections = ['when_to_use', 'workflow', 'best_practices', 'error_handling', 'related_tools']
            missing = [s for s in required_sections if s not in usage_guide or not usage_guide[s]]
            
            if missing:
                issues.append(f"usage_guide missing sections: {', '.join(missing)}")
                scores['usage_guide'] = int((len(required_sections) - len(missing)) / len(required_sections) * 100)
            else:
                # Check quality of sections
                when_to_use = usage_guide.get('when_to_use', [])
                if len(when_to_use) < 3:
                    issues.append(f"when_to_use needs 3-5 scenarios (has {len(when_to_use)})")
                    scores['usage_guide'] = 90
                else:
                    scores['usage_guide'] = 100
        
        # 6. Check returns structure
        returns = tool.get('returns', {})
        if not returns:
            issues.append("Missing returns definition")
            scores['returns'] = 0
        elif 'description' not in returns:
            issues.append("Returns missing description")
            scores['returns'] = 50
        else:
            scores['returns'] = 100
        
        # 7. Check platform field
        platform = tool.get('platform')
        if not platform:
            issues.append("Missing platform field")
            scores['platform'] = 0
        else:
            scores['platform'] = 100
        
        # 8. Check implementation exists
        impl_module = self._get_implementation_module(tool_name)
        if impl_module:
            scores['implementation'] = 100
        else:
            issues.append("Implementation not found")
            scores['implementation'] = 0
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        
        return {
            'tool_name': tool_name,
            'platform': platform,
            'issues': issues,
            'scores': scores,
            'overall_score': overall_score
        }
    
    def _get_implementation_module(self, tool_name: str) -> Optional[Any]:
        """Check if implementation exists"""
        # Try to find implementation
        if '_' in tool_name:
            parts = tool_name.split('_')
            platform = parts[0]
            
            # Check google_workspace
            if platform in ['gmail', 'google']:
                impl_name = 'google_workspace.' + ('gmail' if platform == 'gmail' else parts[0] + '_' + parts[1])
                return self.registry.implementations.get(impl_name)
            
            # Check tools.implementations
            impl_name = f"tools.implementations.{platform}"
            return self.registry.implementations.get(impl_name)
        return None
    
    def audit_all(self, platform_filter: Optional[str] = None) -> Dict[str, Any]:
        """Audit all tools"""
        print(f"🔍 Auditing {self.results['total_tools']} tools...")
        
        platform_results = defaultdict(list)
        tool_results = []
        
        for tool_name, tool in self.registry.tools.items():
            platform = tool.get('platform', 'unknown')
            
            # Apply filter
            if platform_filter and platform_filter not in platform:
                continue
            
            # Audit tool
            result = self.audit_tool(tool_name, tool)
            tool_results.append(result)
            platform_results[platform].append(result)
        
        # Calculate platform scores
        for platform, results in platform_results.items():
            scores = [r['overall_score'] for r in results]
            self.results['platforms'][platform] = {
                'count': len(results),
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'tools': results
            }
        
        # Calculate overall statistics
        all_scores = [r['overall_score'] for r in tool_results]
        self.results['overall_avg_score'] = sum(all_scores) / len(all_scores) if all_scores else 0
        self.results['tools_audited'] = len(tool_results)
        
        # Categorize tools by score
        self.results['excellent'] = [r for r in tool_results if r['overall_score'] >= 90]
        self.results['good'] = [r for r in tool_results if 75 <= r['overall_score'] < 90]
        self.results['needs_improvement'] = [r for r in tool_results if 60 <= r['overall_score'] < 75]
        self.results['poor'] = [r for r in tool_results if r['overall_score'] < 60]
        
        return self.results
    
    def print_summary(self):
        """Print audit summary"""
        print("\n" + "="*80)
        print("📊 TOOL QUALITY AUDIT SUMMARY")
        print("="*80)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tools Audited: {self.results['tools_audited']}")
        print(f"   Average Score: {self.results['overall_avg_score']:.1f}/100")
        
        print(f"\n🎯 Score Distribution:")
        print(f"   ✅ Excellent (90-100): {len(self.results['excellent'])} tools ({len(self.results['excellent'])/self.results['tools_audited']*100:.1f}%)")
        print(f"   ✓  Good (75-89): {len(self.results['good'])} tools ({len(self.results['good'])/self.results['tools_audited']*100:.1f}%)")
        print(f"   ⚠️  Needs Improvement (60-74): {len(self.results['needs_improvement'])} tools ({len(self.results['needs_improvement'])/self.results['tools_audited']*100:.1f}%)")
        print(f"   ❌ Poor (<60): {len(self.results['poor'])} tools ({len(self.results['poor'])/self.results['tools_audited']*100:.1f}%)")
        
        print(f"\n🏢 Platform Breakdown:")
        sorted_platforms = sorted(self.results['platforms'].items(), 
                                 key=lambda x: x[1]['avg_score'], 
                                 reverse=True)
        
        for platform, data in sorted_platforms[:20]:  # Top 20
            score = data['avg_score']
            count = data['count']
            emoji = '✅' if score >= 90 else '✓' if score >= 75 else '⚠️' if score >= 60 else '❌'
            print(f"   {emoji} {platform:30s} {score:5.1f}/100  ({count} tools)")
        
        if len(sorted_platforms) > 20:
            print(f"   ... and {len(sorted_platforms) - 20} more platforms")
    
    def print_detailed_issues(self, limit: int = 10):
        """Print detailed issues for worst tools"""
        print(f"\n🔍 Top {limit} Tools Needing Attention:")
        print("="*80)
        
        worst_tools = sorted(self.results['poor'] + self.results['needs_improvement'], 
                           key=lambda x: x['overall_score'])[:limit]
        
        for i, tool in enumerate(worst_tools, 1):
            print(f"\n{i}. {tool['tool_name']} ({tool['platform']})")
            print(f"   Score: {tool['overall_score']:.1f}/100")
            print(f"   Issues:")
            for issue in tool['issues']:
                print(f"      ❌ {issue}")
            
            # Show score breakdown
            print(f"   Component Scores:")
            for component, score in sorted(tool['scores'].items()):
                emoji = '✅' if score >= 90 else '✓' if score >= 75 else '⚠️' if score >= 60 else '❌'
                print(f"      {emoji} {component:20s} {score:3.0f}/100")
    
    def export_report(self, output_path: str):
        """Export detailed markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Tool Quality Audit Report\n\n")
            f.write(f"**Generated**: {Path(__file__).name}\n")
            f.write(f"**Total Tools**: {self.results['tools_audited']}\n")
            f.write(f"**Average Score**: {self.results['overall_avg_score']:.1f}/100\n\n")
            
            f.write("## Score Distribution\n\n")
            f.write(f"- ✅ Excellent (90-100): {len(self.results['excellent'])} tools\n")
            f.write(f"- ✓ Good (75-89): {len(self.results['good'])} tools\n")
            f.write(f"- ⚠️ Needs Improvement (60-74): {len(self.results['needs_improvement'])} tools\n")
            f.write(f"- ❌ Poor (<60): {len(self.results['poor'])} tools\n\n")
            
            f.write("## Platform Scores\n\n")
            f.write("| Platform | Score | Tools | Status |\n")
            f.write("|----------|-------|-------|--------|\n")
            
            sorted_platforms = sorted(self.results['platforms'].items(), 
                                     key=lambda x: x[1]['avg_score'], 
                                     reverse=True)
            
            for platform, data in sorted_platforms:
                score = data['avg_score']
                count = data['count']
                status = '✅' if score >= 90 else '✓' if score >= 75 else '⚠️' if score >= 60 else '❌'
                f.write(f"| {platform} | {score:.1f}/100 | {count} | {status} |\n")
            
            f.write("\n## Tools Needing Attention\n\n")
            
            poor_tools = sorted(self.results['poor'] + self.results['needs_improvement'], 
                              key=lambda x: x['overall_score'])
            
            for tool in poor_tools:
                f.write(f"### {tool['tool_name']} ({tool['platform']})\n\n")
                f.write(f"**Score**: {tool['overall_score']:.1f}/100\n\n")
                f.write("**Issues**:\n")
                for issue in tool['issues']:
                    f.write(f"- ❌ {issue}\n")
                f.write("\n**Component Scores**:\n")
                for component, score in sorted(tool['scores'].items()):
                    status = '✅' if score >= 90 else '✓' if score >= 75 else '⚠️' if score >= 60 else '❌'
                    f.write(f"- {status} {component}: {score:.0f}/100\n")
                f.write("\n")
        
        print(f"\n✅ Report exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Audit tool quality against standards')
    parser.add_argument('--platform', type=str, help='Filter by platform (e.g., google, microsoft)')
    parser.add_argument('--detailed', action='store_true', help='Show detailed issues')
    parser.add_argument('--export', type=str, help='Export report to file')
    parser.add_argument('--limit', type=int, default=10, help='Number of tools to show in detailed view')
    
    args = parser.parse_args()
    
    # Run audit
    auditor = ToolQualityAuditor()
    results = auditor.audit_all(platform_filter=args.platform)
    
    # Print summary
    auditor.print_summary()
    
    # Print detailed issues if requested
    if args.detailed:
        auditor.print_detailed_issues(limit=args.limit)
    
    # Export report if requested
    if args.export:
        auditor.export_report(args.export)
    
    print("\n" + "="*80)
    print("✅ Audit complete!")
    print("="*80)


if __name__ == "__main__":
    main()
