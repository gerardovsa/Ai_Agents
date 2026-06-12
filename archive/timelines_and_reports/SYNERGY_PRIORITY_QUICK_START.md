# Synergy Priority & Markdown - Quick Start Guide

**Date:** December 1, 2025  
**Status:** ✅ Ready to Use

---

## 🚀 Quick Start: Using Priority

### Creating Tasks with Priority

```python
# Simple task with priority
synergy_create_task(
    milestone_id="mil_123",
    task="Fix critical bug",
    priority="critical"  # 🔴 Shows red badge
)

# Task with prioritized subtasks
synergy_create_task(
    milestone_id="mil_123",
    task="Deploy to production",
    priority="high",  # 🟠 Shows orange badge
    subtasks=[
        "Run tests",  # No priority = medium (no badge)
        {"task": "Database migration", "priority": "critical"},  # 🔴 Red badge
        {"task": "Update documentation", "priority": "low"}  # 🟢 Green badge
    ]
)
```

### Priority Levels

| Level | Badge | Color | When to Use |
|-------|-------|-------|-------------|
| `'critical'` | 🔴 CRITICAL | Red | Urgent/blocking issues |
| `'high'` | 🟠 HIGH | Orange | Important, time-sensitive |
| `'medium'` | (no badge) | - | Standard tasks (default) |
| `'low'` | 🟢 LOW | Green | Nice-to-have, low urgency |

---

## 📝 Quick Start: Using Markdown

### Formatting Descriptions

```markdown
# Project Title

This is a **bold statement** with *italic text*.

## Key Points:
- First bullet point
- Second with `inline code`
- Third with [a link](https://example.com)

### Next Steps
1. Complete phase 1
2. Review with stakeholders
3. Deploy to production

*Note: This is italic text*
```

### Supported Syntax

| Syntax | Renders As |
|--------|-----------|
| `# H1` | Large header with underline |
| `## H2` | Medium header |
| `### H3` | Small header |
| `**bold**` | **Bold text** |
| `*italic*` | *Italic text* |
| `` `code` `` | `Inline code` with background |
| `[text](url)` | Clickable link (opens in new tab) |
| `- item` | Bullet list item |
| `1. item` | Numbered list item |

---

## 🎯 Visual Examples

### Priority Badges in UI

```
📋 Milestone 1: Core Development
   ☐ Create API endpoints 🟠 HIGH
      ☐ Define routes
      ☐ Add authentication 🔴 CRITICAL
      ☐ Write tests 🟢 LOW
   ☐ Database setup
      ☐ Design schema
      ☐ Create migrations 🟠 HIGH
```

### Markdown Rendering

**Input:**
```markdown
# Phase 1

**Goal:** Set up infrastructure

Resources:
- [AWS Console](https://console.aws.amazon.com)
- Setup guide: `terraform apply`
```

**Output:**  
<div style="border: 1px solid #e5e7eb; padding: 12px; border-radius: 8px; background: #f9fafb;">
<h1 style="font-size: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 4px;">Phase 1</h1>
<p><strong>Goal:</strong> Set up infrastructure</p>
<p>Resources:</p>
<ul>
<li><a href="https://console.aws.amazon.com" style="color: #3b82f6;">AWS Console</a></li>
<li>Setup guide: <code style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 2px 6px; color: #d97706;">terraform apply</code></li>
</ul>
</div>

---

## 🔧 AI Agent Usage

### Full Example with Both Features

```python
result = synergy_smart_project_tracker(
    title="Customer Portal Upgrade",
    platforms_involved=["sheets", "forms", "gmail"],
    description="""
# Project Overview

Upgrade customer portal with **enhanced security** and *improved UX*.

## Phases:
1. Security audit
2. UI redesign
3. Performance optimization

[Design Mockups](https://figma.com/project123)

*Timeline: 6 weeks*
""",
    use_milestones=True,
    initial_milestones=[
        {
            "milestone_name": "Phase 1: Security",
            "priority": "critical",
            "tasks": [
                {
                    "task": "Security audit",
                    "priority": "critical",
                    "subtasks": [
                        {"task": "Penetration testing", "priority": "critical"},
                        "Code review",
                        {"task": "Update dependencies", "priority": "high"}
                    ]
                },
                {
                    "task": "Implement 2FA",
                    "priority": "high",
                    "subtasks": [
                        "Research providers",
                        {"task": "Integration", "priority": "high"},
                        {"task": "User testing", "priority": "low"}
                    ]
                }
            ]
        }
    ]
)
```

---

## 📊 Priority Decision Matrix

### When to Use Each Level:

**🔴 CRITICAL:**
- System is down
- Security vulnerability
- Blocking other work
- Legal/compliance deadline

**🟠 HIGH:**
- Important feature
- Customer-facing issue
- Time-sensitive task
- Significant impact

**🟢 LOW:**
- Documentation updates
- Code cleanup
- Nice-to-have features
- Future improvements

**No Badge (Medium):**
- Standard workflow
- Normal priority tasks
- Routine maintenance
- Default choice

---

## 🎨 Markdown Best Practices

### Do's:

✅ Use headers to create sections  
✅ Bold important terms  
✅ Add links to relevant resources  
✅ Use lists for steps/requirements  
✅ Use inline code for technical terms  

### Don'ts:

❌ Don't over-format (keep it readable)  
❌ Don't use headers excessively  
❌ Don't nest lists too deeply  
❌ Don't forget to escape HTML  

### Example of Well-Formatted Description:

```markdown
# Customer Database Migration

## Overview
Migrate legacy SQL database to **modern cloud solution** with zero downtime.

## Prerequisites:
- [ ] Backup current database
- [ ] Set up staging environment
- [ ] Create rollback plan

## Key Resources:
- [Migration Guide](https://docs.internal.com/migration)
- Database connection string: `postgres://prod-db.internal`
- Contact: tech-lead@company.com

*Last updated: December 1, 2025*
```

---

## 🧪 Testing Your Implementation

### Check Priority Badges:

1. Create task with `priority: "critical"`
2. Verify 🔴 red badge appears
3. Complete the task
4. Badge should dim but remain visible

### Check Markdown Rendering:

1. Edit session description
2. Add markdown syntax (headers, bold, links)
3. Save changes
4. Verify HTML renders correctly
5. Check links open in new tab

---

## 📱 Browser Compatibility

✅ Chrome/Edge (Chromium) - Full support  
✅ Firefox - Full support  
✅ Safari - Full support  
⚠️ IE11 - Not tested (deprecated)

---

## 🆘 Troubleshooting

### Priority badges not showing:

1. Check browser cache (Ctrl+Shift+R)
2. Verify CSS file loaded
3. Inspect element - class should be `priority-badge priority-{level}`
4. Check priority value in database (must be 'low', 'medium', 'high', or 'critical')

### Markdown not rendering:

1. Check description contains markdown syntax
2. Verify using synergy-sidebar-renderer-v2-FLAT.js (not V1)
3. Look for `renderMarkdown()` method in browser console
4. Check CSS file includes markdown styles

### Common Issues:

**Issue:** Medium priority shows no badge  
**Solution:** This is correct - medium is default, no badge shown

**Issue:** Links don't open in new tab  
**Solution:** Use markdown format `[text](url)`, not HTML `<a>`

**Issue:** Code blocks not styled  
**Solution:** Use single backticks `` `code` `` for inline code only

---

## 📚 More Information

- **Complete Documentation:** `SYNERGY_PRIORITY_AND_MARKDOWN_IMPLEMENTATION.md` (30 pages)
- **Database Migration:** `migrations/add_task_subtask_priority_fields.sql`
- **Architecture Analysis:** `SYNERGY_TITLE_FIELD_ANALYSIS.md` (31 pages)

---

**Version:** 1.0.0  
**Last Updated:** December 1, 2025  
**Status:** ✅ Production Ready
