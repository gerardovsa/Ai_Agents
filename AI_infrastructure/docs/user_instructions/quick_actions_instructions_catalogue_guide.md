# Quick Actions & Instructions Catalogue - Complete User Guide

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Audience:** End Users, Power Users, AI Agents

---

## 📋 Table of Contents

1. [What is the Instructions Catalogue?](#what-is-the-instructions-catalogue)
2. [Getting Started](#getting-started)
3. [Understanding Quick Actions vs Full Prompts](#understanding-quick-actions-vs-full-prompts)
4. [Browsing and Using Prompts](#browsing-and-using-prompts)
5. [Creating Custom Prompts](#creating-custom-prompts)
6. [Managing Your Prompt Library](#managing-your-prompt-library)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Frequently Asked Questions](#frequently-asked-questions)
10. [AI Agent Instructions](#ai-agent-instructions)

---

## What is the Instructions Catalogue?

The **Instructions Catalogue** (also called **Prompt Library** or **Quick Actions**) is a centralized library of reusable AI instructions that help you get better, more consistent results from your AI assistants. Think of it as a **toolbox of pre-written prompts** that you can apply to any conversation with one click.

### Key Features

- ⚡ **Quick Actions** - Short, instant AI behavior modifiers (e.g., "Be concise", "Use bullet points")
- 📝 **Full Prompts** - Detailed instruction sets for complex tasks
- 🗂️ **Organized by Category** - Development, Analysis, Data, Style, Business, Creative
- ⭐ **Favorites System** - Star your most-used prompts for quick access
- 🔍 **Smart Search** - Find prompts by name, description, or tags
- 🎨 **Customizable** - Create and save your own prompt templates
- 🔗 **Active Prompts Bar** - See which prompts are currently active in your conversation
- 📊 **Usage Tracking** - Most-used and recently-used filters

### Why Use the Instructions Catalogue?

**Without the Catalogue:**
```
You: "Write me a Python script for data analysis. Make it professional, 
well-documented, follow PEP 8, use type hints, include error handling, 
and add tests. Also make your responses concise and use bullet points..."

(You have to type this every time! 😩)
```

**With the Catalogue:**
```
You: [Clicks ⚡ button → Selects "Python Best Practices" + "Concise Responses"]
You: "Write me a Python script for data analysis."

AI automatically applies all your saved instructions! ✨
```

### Use Cases

✅ **Consistent Code Style** - Apply your team's coding standards automatically
✅ **Better Communication** - Get responses in your preferred format (bullet points, tables, etc.)
✅ **Role-Based Assistance** - Switch between "Business Analyst" and "Technical Developer" modes
✅ **Domain Expertise** - Load specialized knowledge (SQL optimization, API design, etc.)
✅ **Quality Control** - Enforce best practices (testing, documentation, security)
✅ **Workflow Efficiency** - Save multi-step instructions you use repeatedly

---

## Getting Started

### Accessing the Instructions Catalogue

**The ⚡ Bolt Button:**

Located in the **bottom action bar** of the AI chat interface (next to the send button):

```
┌────────────────────────────────────────┐
│ [Type your message here...]            │
│                                        │
└────────────────────────────────────────┘
  [📎] [⚡] [🎤] [➤ Send]
         ↑
    Bolt Button
```

**Click the ⚡ button** to open the Instructions Catalogue sidebar.

### First Time Opening

When you first open the catalogue, you'll see:

1. **Browse Tab** (default) - Pre-loaded prompts organized by category
2. **Create Tab** - Form to create your own custom prompts
3. **Filter Buttons** - Quick filters (All, Recent, Favorites, Most Used)
4. **Search Box** - Find prompts by keyword
5. **Category Dropdown** - Filter by category (Development, Analysis, etc.)

### Quick Tour

```
┌─────────────────────────────────────────┐
│ ⚡ Instructions Catalogue          [×]  │  ← Header
├─────────────────────────────────────────┤
│ [Browse] [Create New]                   │  ← Tabs
├─────────────────────────────────────────┤
│ 🔍 Search...    [Category Dropdown ▼]  │  ← Search & Filter
├─────────────────────────────────────────┤
│ [All] [Recent] [★] [Fire] | [⚡] [📝] │  ← Action Buttons
├─────────────────────────────────────────┤
│ 📋 Code Review Assistant            [+] │  ← Prompt Card
│ Analysis · Quick Action                 │
│ Review code for best practices...       │
├─────────────────────────────────────────┤
│ 📋 SQL Query Optimizer             [+] │
│ Data & SQL · Full Prompt                │
│ Optimize SQL queries for performance... │
├─────────────────────────────────────────┤
│ ... more prompts ...                    │
└─────────────────────────────────────────┘
```

---

## Understanding Quick Actions vs Full Prompts

The Instructions Catalogue supports **two types of prompts**:

### Quick Actions ⚡

**What they are:**
- Short, directive-style instructions (1-3 sentences)
- Modify AI's behavior or response style
- Can be stacked (use multiple at once)
- Applied immediately to the conversation

**Examples:**
- "Be concise. Use bullet points only."
- "Explain like I'm a beginner."
- "Focus on performance optimization."
- "Use British English spelling."
- "Include code examples with every explanation."

**When to use:**
- Changing response format (bullets, tables, paragraphs)
- Adjusting communication style (formal, casual, technical)
- Adding constraints (word limits, specific focus areas)
- Enabling/disabling features (code comments, error handling)

**Visual Indicator:**
- **⚡ Bolt icon** in the prompt card
- "Quick Action" label

### Full Prompts 📝

**What they are:**
- Complete instruction sets with context and details
- Define complex AI roles or workflows
- Usually used alone (not stacked)
- Provide comprehensive guidance

**Examples:**
- Multi-paragraph prompt for "Senior Python Developer" role
- Detailed code review checklist with 15 criteria
- Complete API documentation template
- Step-by-step debugging methodology

**When to use:**
- Role-playing scenarios (act as X expert)
- Multi-step processes (workflow, methodology)
- Domain-specific expertise (legal, medical, technical)
- Quality assurance frameworks

**Visual Indicator:**
- **📝 List icon** in the prompt card
- "Full Prompt" label

### Combining Prompts

You can **stack multiple Quick Actions** together:

```
Active Prompts:
┌───────────────────────────────────────┐
│ [⚡ Be Concise ×] [⚡ Use Bullets ×]  │
│ [⚡ Include Examples ×]               │
└───────────────────────────────────────┘

Result: AI gives brief, bullet-point responses with examples
```

But **only use ONE Full Prompt at a time** (they define complete contexts):

```
✅ GOOD:
[📝 Python Developer Role] + [⚡ Be Concise] + [⚡ Add Tests]

❌ CONFUSING:
[📝 Python Developer] + [📝 Business Analyst]
(Conflicting roles - which persona to use?)
```

---

## Browsing and Using Prompts

### The Browse Tab

The **Browse tab** is where you discover and apply prompts to your conversations.

### Filtering Prompts

**1. Quick Action Filters (Top Row Icons):**

| Icon | Filter | What It Shows |
|------|--------|---------------|
| 📊 All | Show all prompts | Complete library |
| 🕒 Recent | Recently used | Last 10 prompts you used |
| ⭐ Favorites | Starred prompts | Your favorited prompts |
| 🔥 Most Used | Popular prompts | Top 10 by usage count |

**2. Type Filters (After separator):**

| Icon | Filter | What It Shows |
|------|--------|---------------|
| ⚡ Quick | Quick Actions only | Short directive prompts |
| 📝 Detailed | Full Prompts only | Complete instruction sets |

**3. Category Dropdown:**

- All Categories
- Development (code, debugging, architecture)
- Analysis (data analysis, research)
- Data & SQL (database queries, optimization)
- Communication Style (tone, format, structure)
- Business (reports, strategy, management)
- Creative (writing, brainstorming, design)

### Searching Prompts

The **search box** filters prompts in real-time:

```
🔍 Search: "python"

Results:
- Python Best Practices
- Python Code Review
- Python Testing Guidelines
- SQL to Python Converter
```

**Search matches:**
- Prompt title
- Description text
- Tags

### Applying a Prompt

**Method 1: Click the [+] Button**
1. Find the prompt you want
2. Click the **[+] button** on the right side of the prompt card
3. The prompt is added to your **Active Prompts Bar** (above chat input)
4. Start typing your message - the prompt is automatically included

**Method 2: Click the Prompt Card**
1. Click anywhere on the prompt card (not the [+] button)
2. A **preview popup** appears showing:
   - Full prompt text
   - Category and type
   - Tags
   - Usage count
3. Click **"Apply"** button in popup
4. Prompt added to active prompts

**Method 3: Drag and Drop** (if enabled)
1. Click and hold a prompt card
2. Drag it to the chat input area
3. Release to apply

### Active Prompts Bar

When you apply prompts, they appear in the **Active Prompts Bar** above the chat input:

```
┌─────────────────────────────────────────┐
│ Active: [⚡ Be Concise ×] [⚡ Bullets ×]│  ← Active Bar
├─────────────────────────────────────────┤
│ [Type your message here...]             │  ← Chat Input
└─────────────────────────────────────────┘
```

**Features:**
- **[× Remove Button]** - Click to remove a prompt
- **Visual Pills** - Each active prompt shows as a colored pill
- **Persistent** - Prompts stay active until you remove them
- **Context Indicator** - Shows AI what instructions are in effect

### Removing a Prompt

**Method 1: Click [×] in Active Bar**
- Click the × on any active prompt pill
- Prompt is immediately removed

**Method 2: Clear All** (if button exists)
- Click "Clear All" to remove all active prompts at once

---

## Creating Custom Prompts

### Accessing the Editor

**Method 1: Click "Create New" Tab**
- Open Instructions Catalogue sidebar
- Click the **[Create New]** tab at the top

**Method 2: Click [+] Button in Action Bar**
- In Browse tab, click the **[+]** button in the top-right corner
- Switches to Create tab

### The Prompt Editor Form

**Form Fields:**

1. **Prompt Title** (required)
   - Clear, descriptive name
   - Example: "Python Type Hints Best Practices"

2. **Category** (required)
   - Choose from dropdown:
     - Development
     - Analysis
     - Data & SQL
     - Communication Style
     - Business
     - Creative
   - Or click [+] to add custom category

3. **Prompt Type** (required)
   - **Quick Action** - Short directive (default)
   - **Full Prompt** - Complete instruction set
   - Toggle by clicking the type buttons

4. **Short Description** (optional)
   - Brief summary shown in browse list
   - Example: "Enforce type hints in Python code"

5. **Prompt Text** (required)
   - The actual instructions for the AI
   - Can be 1 sentence or multiple paragraphs
   - Supports plain text or markdown

6. **Tags** (optional)
   - Comma-separated keywords
   - Example: "python, typing, best-practices"
   - Helps with search and organization

7. **Visibility** (required)
   - **Private** - Only you can see/use
   - **Workspace** - All team members can see/use
   - **Public** - Everyone can see/use (if sharing enabled)

### Creating a Quick Action

**Example: "Use Bullet Points"**

```
┌─────────────────────────────────────────┐
│ Prompt Title:                           │
│ Use Bullet Points                       │
├─────────────────────────────────────────┤
│ Category:                               │
│ [Communication Style ▼]                 │
├─────────────────────────────────────────┤
│ Prompt Type:                            │
│ [⚡ Quick Action] [Full Prompt]         │
├─────────────────────────────────────────┤
│ Short Description:                      │
│ Format responses as bullet lists        │
├─────────────────────────────────────────┤
│ Prompt Text:                            │
│ Format your responses as bullet points. │
│ Use clear, concise language. Avoid     │
│ long paragraphs.                        │
├─────────────────────────────────────────┤
│ Tags:                                   │
│ format, bullets, concise                │
├─────────────────────────────────────────┤
│ Visibility:                             │
│ [Private ▼]                             │
└─────────────────────────────────────────┘
[Cancel] [Create]
```

### Creating a Full Prompt

**Example: "Senior Python Developer Role"**

```
┌─────────────────────────────────────────┐
│ Prompt Title:                           │
│ Senior Python Developer                 │
├─────────────────────────────────────────┤
│ Category:                               │
│ [Development ▼]                         │
├─────────────────────────────────────────┤
│ Prompt Type:                            │
│ [Quick Action] [📝 Full Prompt]         │
├─────────────────────────────────────────┤
│ Short Description:                      │
│ Act as senior Python developer          │
├─────────────────────────────────────────┤
│ Prompt Text:                            │
│ You are a senior Python developer with │
│ 10+ years of experience. When writing  │
│ code, you:                              │
│                                         │
│ - Follow PEP 8 style guidelines         │
│ - Use type hints for all functions      │
│ - Write comprehensive docstrings        │
│ - Include error handling                │
│ - Add unit tests                        │
│ - Optimize for readability first        │
│ - Consider edge cases                   │
│                                         │
│ Explain your architectural decisions   │
│ and suggest improvements when relevant. │
├─────────────────────────────────────────┤
│ Tags:                                   │
│ python, development, senior, best-      │
│ practices, testing                      │
├─────────────────────────────────────────┤
│ Visibility:                             │
│ [Workspace ▼]                           │
└─────────────────────────────────────────┘
[Cancel] [Create]
```

### Saving Your Prompt

Click **[Create]** button to save. You'll see:
- Success notification: "Prompt saved successfully"
- Automatic switch to Browse tab
- Your new prompt appears in the list

---

## Managing Your Prompt Library

### Editing an Existing Prompt

**Method 1: Edit Button in Browse List**
1. Find the prompt in Browse tab
2. Hover over the prompt card
3. Click the **[✏️ Edit]** icon that appears
4. Editor tab opens with prompt loaded
5. Make changes and click **[Update]**

**Method 2: Context Menu** (if available)
1. Right-click a prompt card
2. Select "Edit" from menu
3. Editor opens

### Deleting a Prompt

**From Editor Tab:**
1. Open prompt for editing
2. Click **[Delete]** button (red, bottom-left)
3. Confirm deletion: "Are you sure?"
4. Prompt is permanently deleted

**From Browse Tab** (if available):
1. Right-click prompt card
2. Select "Delete" from menu
3. Confirm deletion

⚠️ **Warning:** Deletion is permanent and cannot be undone!

### Favoriting Prompts

**To add/remove favorites:**
1. Find prompt in Browse tab
2. Click the **⭐ star icon** on the prompt card
3. Star turns yellow (favorited) or gray (not favorited)

**To view favorites:**
1. Click the **[⭐ Favorites]** button in action bar
2. Only starred prompts appear

**Why favorite?**
- Quick access to your most-used prompts
- Personal shortlist for frequent tasks
- Easier to find in large libraries

### Usage Tracking

The system automatically tracks:
- **How many times** each prompt is used
- **When** it was last used
- **Most popular** prompts across all users (if workspace/public)

**View usage stats:**
- Click **[🔥 Most Used]** button - shows top 10 by usage count
- Click **[🕒 Recent]** button - shows last 10 you used
- Usage count shown on prompt cards (if enabled)

---

## Advanced Features

### Breadcrumb Navigation

When viewing prompt details, a **breadcrumb trail** appears:

```
┌─────────────────────────────────────────┐
│ Home > Development > Python Best Pract… │  ← Breadcrumb
├─────────────────────────────────────────┤
│ [Full prompt details here]              │
└─────────────────────────────────────────┘
```

**Features:**
- Shows current location in catalogue
- Click **Home** to return to browse list
- Click **Category** to filter by that category

### Custom Categories

**To add a new category:**
1. Open Create/Edit tab
2. In Category dropdown, click **[+] Add Category** button
3. Modal appears: "Enter category name"
4. Type name (e.g., "Marketing")
5. Click **[Add]**
6. New category available in dropdown

**Managing categories:**
- Categories are shared across workspace (if applicable)
- Cannot delete categories with existing prompts
- Rename via settings (if available)

### Prompt Templates

Some prompts may include **variables** (placeholders):

```
Prompt Text:
"You are a {{ROLE}} with {{YEARS}} years of experience 
in {{DOMAIN}}. Focus on {{FOCUS_AREA}}."

When applied, you can fill in:
- ROLE: "Software Architect"
- YEARS: "15"
- DOMAIN: "Cloud Infrastructure"
- FOCUS_AREA: "Security and Scalability"
```

**Using templates:**
1. Apply a template prompt
2. Modal appears asking for variable values
3. Fill in fields
4. Click **[Apply]**
5. Prompt added with your custom values

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open Instructions Catalogue |
| `Escape` | Close sidebar |
| `Ctrl+F` | Focus search box |
| `/` | Quick search (in Browse tab) |
| `Ctrl+N` | New prompt (switch to Create tab) |
| `Ctrl+S` | Save prompt (in Editor tab) |

### Sharing Prompts

**Visibility Levels:**

1. **Private** 🔒
   - Only you can see/use
   - Not shared with anyone
   - Good for personal preferences

2. **Workspace** 👥
   - All team members can see/use
   - Shared within your organization
   - Good for team standards

3. **Public** 🌍
   - Everyone can see/use (if enabled)
   - Contributes to community library
   - Good for general best practices

**Changing visibility:**
1. Edit the prompt
2. Change **Visibility** dropdown
3. Save changes

---

## Best Practices

### Naming Conventions

**✅ Good names:**
- "Python Type Hints"
- "SQL Performance Optimization"
- "Concise Bullet Point Responses"
- "Code Review Checklist"

**❌ Bad names:**
- "My Prompt" (too vague)
- "Prompt 1" (not descriptive)
- "PYTHON PYTHON PYTHON" (not helpful)
- "asdfghjkl" (meaningless)

### Writing Effective Prompts

**Quick Actions - Keep It Simple:**
```
✅ GOOD:
"Format responses as tables when comparing multiple items."

❌ TOO COMPLEX:
"You should consider using tabular formats whenever presenting 
comparative data, unless the user explicitly requests otherwise, 
in which case you should ask for clarification..."
```

**Full Prompts - Be Specific:**
```
✅ GOOD:
"You are a senior database architect. When designing schemas:
1. Normalize to 3NF by default
2. Use foreign keys for referential integrity
3. Index frequently queried columns
4. Document relationships with comments"

❌ TOO VAGUE:
"Help me with databases and make them good."
```

### Organizing Your Library

**Use consistent categories:**
- Don't create duplicate categories ("Code" vs "Coding" vs "Development")
- Use the existing 6 categories as much as possible
- Only create custom categories for specialized domains

**Tag thoughtfully:**
- 3-7 tags per prompt (not too few, not too many)
- Use common terms (lowercase, no special characters)
- Think about search terms users would type

**Leverage descriptions:**
- Write clear, one-line descriptions
- Explain what the prompt does, not how it works
- Good: "Enforces Python PEP 8 style guidelines"
- Bad: "This prompt tells AI to use PEP 8 when writing code"

### Workflow Recommendations

**Daily Habits:**
1. **Morning Setup** - Load your standard prompts at session start
   - Apply "Concise Responses"
   - Apply "Use Bullet Points"
   - Apply role-specific prompt (Developer, Analyst, etc.)

2. **Task-Specific** - Add prompts as needed
   - Starting code review? Add "Code Review Checklist"
   - Writing documentation? Add "Technical Writer Style"

3. **Clean Up** - Remove prompts when done
   - Finish code review? Remove that prompt
   - Switch tasks? Clear all and start fresh

**Project-Specific Prompts:**
- Create prompts for project conventions
  - "ProjectX Coding Standards"
  - "ClientY Communication Style"
  - "TeamZ Code Review Process"
- Share with workspace so team uses same standards

---

## Frequently Asked Questions

### General Questions

**Q: How many prompts can I have in my library?**
A: No hard limit. However, keep your library organized (< 50 prompts recommended for easy navigation).

**Q: Can I use multiple Quick Actions at once?**
A: Yes! Stack as many Quick Actions as you need. They combine together.

**Q: Can I use multiple Full Prompts at once?**
A: Not recommended. Full Prompts define complete contexts (roles, workflows) and can conflict. Use one Full Prompt + multiple Quick Actions.

**Q: Do prompts persist across sessions?**
A: **Active prompts** (currently applied) clear when you close/refresh. **Saved prompts** (in your library) persist forever.

**Q: Can I export/import prompts?**
A: Export feature may be available (check UI). You can copy prompt text manually and recreate in another account.

### Using Prompts

**Q: When do active prompts take effect?**
A: Immediately upon adding them. Every message you send after applying a prompt includes that prompt's instructions.

**Q: How do I know which prompts are active?**
A: Check the **Active Prompts Bar** above the chat input. All active prompts show as colored pills.

**Q: Can AI see my prompt library?**
A: No. AI only sees the prompts you've actively applied to the current conversation.

**Q: What if I apply conflicting prompts?**
A: Example: "Be concise" + "Be detailed" - AI will try to balance both, but results may be unpredictable. Remove one.

### Creating Prompts

**Q: Can I use markdown in prompt text?**
A: Yes! Use headings, lists, bold, etc. However, AI receives plain text (markdown syntax removed).

**Q: Can I edit prompts after creating them?**
A: Yes. Click Edit button in Browse tab, make changes, and save.

**Q: Can I duplicate a prompt?**
A: Not directly. Open for edit, copy text, cancel, create new, paste text.

**Q: How do I test a new prompt?**
A: Create and save it, then apply it to a test conversation. Try a few messages to see if AI responds as expected.

### Troubleshooting

**Q: My prompt isn't working - AI ignores it**
A: Possible causes:
1. Prompt is too vague ("be good")
2. Prompt conflicts with other active prompts
3. Prompt is too long (AI truncates)
4. Try rephrasing more directly

**Q: I don't see the ⚡ bolt button**
A: Check:
1. Are you in the AI chat interface?
2. Is the feature enabled? (contact admin)
3. Try refreshing the page
4. Check browser console for errors

**Q: Sidebar won't open**
A: Try:
1. Refresh page
2. Clear browser cache
3. Try different browser
4. Check for JavaScript errors (F12 console)

**Q: My custom category disappeared**
A: Check:
1. Was it shared at workspace level? (may have been removed by admin)
2. Did you delete all prompts in that category?
3. Try logging out/in

---

## AI Agent Instructions

*This section is specifically for AI assistants helping users with the Instructions Catalogue.*

### AI Agent Core Responsibilities

When a user works with prompts, you must:

1. ✅ **Respect active prompts** - Follow all instructions in Active Prompts Bar
2. ✅ **Acknowledge prompt changes** - When user adds/removes prompts, confirm
3. ✅ **Suggest relevant prompts** - Offer prompts that match user's task
4. ✅ **Explain prompt effects** - Help users understand what each prompt does
5. ✅ **Guide prompt creation** - Help users write effective custom prompts
6. ✅ **Maintain consistency** - Apply active prompts to every response

### Understanding Active Prompts

**When a user applies a prompt:**

```
User: [Applies "Be Concise" and "Use Bullet Points"]
User: "Explain how databases work"

AI should:
1. Read active prompts from context (you'll see them in system prompt)
2. Apply instructions: Be brief, use bullets
3. Respond accordingly:

"Databases store and organize data:
• Store: Save information persistently
• Query: Retrieve specific data quickly
• Update: Modify existing records
• Secure: Control access and permissions"
```

**NOT:**
```
"A database is a structured collection of data that is stored electronically 
in a computer system. It typically contains multiple tables with rows and 
columns, where each row represents a record and each column represents a 
field. Databases use a Database Management System (DBMS) to interact with 
users, applications, and the database itself..."

(Ignored "concise" and "bullets" - BAD!)
```

### AI Response Templates

#### Template: Acknowledging Prompt Changes

````markdown
[When user adds a prompt]

Understood! I've applied the "[PROMPT_NAME]" instructions.

From now on, I'll:
• [What the prompt does - bullet 1]
• [What the prompt does - bullet 2]
• [What the prompt does - bullet 3]

[Continue with user's request if provided]
````

#### Template: Suggesting Relevant Prompts

````markdown
[When user describes a task that matches a known prompt]

For this task, you might find these prompts helpful:

**[Prompt Name 1]** (⚡ Quick Action)
• [Brief description of what it does]
• Best for: [Use case]

**[Prompt Name 2]** (📝 Full Prompt)
• [Brief description]
• Best for: [Use case]

Would you like me to apply any of these? Or shall I proceed without them?
````

#### Template: Helping Create a Custom Prompt

````markdown
[When user wants to create a custom prompt]

I can help you create that prompt! Let's break it down:

**Prompt Title:** "[Suggested title]"
**Category:** [Suggested category]
**Type:** [Quick Action / Full Prompt]

**Draft Prompt Text:**
```
[Your drafted prompt text based on user's description]
```

**Suggested Tags:** [tag1, tag2, tag3]

Does this capture what you need? Any adjustments?
````

#### Template: Explaining Prompt Effects

````markdown
[When user asks "What does this prompt do?"]

The "[PROMPT_NAME]" prompt modifies my behavior as follows:

**What it does:**
• [Effect 1]
• [Effect 2]
• [Effect 3]

**Example:**
Without prompt: [Example response without prompt]
With prompt: [Example response with prompt]

**Best used for:**
• [Use case 1]
• [Use case 2]

Would you like to apply it?
````

### AI Best Practices

**DO:**
- ✅ Read and apply ALL active prompts in every response
- ✅ Confirm prompt changes when user adds/removes them
- ✅ Suggest prompts when user's task matches a known category
- ✅ Help users write clear, effective custom prompts
- ✅ Explain prompt effects when asked
- ✅ Maintain prompt consistency throughout conversation

**DON'T:**
- ❌ Ignore active prompts (even if they conflict)
- ❌ Apply prompts that user hasn't explicitly added
- ❌ Contradict active prompt instructions
- ❌ Forget prompts mid-conversation
- ❌ Assume user knows what each prompt does
- ❌ Create prompts for users without asking

### Handling Conflicting Prompts

**If user applies conflicting prompts:**

```
Active: [⚡ Be Concise] [⚡ Be Detailed]

AI Response:
"I notice you have both 'Be Concise' and 'Be Detailed' active, 
which give opposite instructions. Would you like me to:

1. Prioritize brevity (keep 'Be Concise')
2. Prioritize depth (keep 'Be Detailed')
3. Balance both (medium length with key details)

Which would you prefer?"
```

### Prompt Creation Assistance

**When user says: "Help me create a prompt"**

Ask clarifying questions:
1. What task is this for? (code review, writing, analysis, etc.)
2. Quick Action (short directive) or Full Prompt (complete role)?
3. What specific behavior do you want? (examples help)
4. Any restrictions or requirements?

Then draft the prompt and iterate with user.

### Safety Rules

**NEVER:**
- ❌ Create prompts that could cause harm
- ❌ Suggest prompts that violate user privacy
- ❌ Apply prompts without user consent
- ❌ Recommend prompts that contradict platform policies
- ❌ Create prompts with misleading names/descriptions

**ALWAYS:**
- ✅ Follow active prompts faithfully
- ✅ Suggest prompts helpfully, not intrusively
- ✅ Explain prompt effects clearly
- ✅ Help users understand trade-offs
- ✅ Respect user's prompt management choices

---

## Quick Reference Card

### Sidebar Navigation

| Action | Method |
|--------|--------|
| Open Catalogue | Click ⚡ bolt button in chat |
| Close Catalogue | Click [×] or press Escape |
| Switch to Browse | Click [Browse] tab |
| Switch to Create | Click [Create New] tab |
| Search Prompts | Type in 🔍 search box |
| Filter by Category | Use dropdown menu |

### Applying Prompts

| Action | Method |
|--------|--------|
| Apply Prompt | Click [+] button on card |
| View Details | Click anywhere on card |
| Remove Active Prompt | Click [×] on pill in Active Bar |
| Favorite Prompt | Click ⭐ star icon |

### Filter Buttons

| Icon | Filter | Shows |
|------|--------|-------|
| 📊 | All | All prompts |
| 🕒 | Recent | Last 10 used |
| ⭐ | Favorites | Your starred prompts |
| 🔥 | Most Used | Top 10 by usage |
| ⚡ | Quick | Quick Actions only |
| 📝 | Detailed | Full Prompts only |

### Creating Prompts

| Field | Required? | Notes |
|-------|-----------|-------|
| Title | Yes | Clear, descriptive name |
| Category | Yes | Use existing or add custom |
| Type | Yes | Quick Action or Full Prompt |
| Description | Optional | Brief summary |
| Text | Yes | Actual prompt instructions |
| Tags | Optional | Comma-separated keywords |
| Visibility | Yes | Private/Workspace/Public |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open catalogue |
| `Escape` | Close sidebar |
| `Ctrl+F` | Search |
| `Ctrl+N` | New prompt |
| `Ctrl+S` | Save prompt |

---

**End of Complete Guide**

*For additional help, click the ⚡ bolt button and explore the Instructions Catalogue!*
