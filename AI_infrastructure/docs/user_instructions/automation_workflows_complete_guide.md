# Visual Automation Workflows - Complete User Guide

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**Audience:** End Users, Power Users, AI Agents

---

## 📋 Table of Contents

1. [What Are Visual Automation Workflows?](#what-are-visual-automation-workflows)
2. [Getting Started](#getting-started)
3. [Creating Your First Workflow](#creating-your-first-workflow)
4. [Understanding Workflow Components](#understanding-workflow-components)
5. [Publishing and Scheduling](#publishing-and-scheduling)
6. [Working with AI Assistants](#working-with-ai-assistants)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [Common Use Cases](#common-use-cases)
9. [Best Practices](#best-practices)
10. [Frequently Asked Questions](#frequently-asked-questions)
11. [Training Exercises](#training-exercises)
12. [AI Agent Instructions](#ai-agent-instructions)

---

## What Are Visual Automation Workflows?

Visual Automation Workflows allow you to automate repetitive tasks by creating flowcharts that AI can understand and execute. Think of them as visual recipes for automation - you drag and drop shapes to design what you want to happen, and the system handles the execution.

### Key Benefits
- ✅ **No coding required** - Visual drag-and-drop interface
- ✅ **AI-powered** - Ask AI to build or modify workflows
- ✅ **Scheduled execution** - Run automatically at specified times
- ✅ **Execution tracking** - Monitor success/failure rates
- ✅ **Thread linking** - Connect workflows to AI conversations

---

## Getting Started

### Accessing the Automation Canvas

1. Click the **purple workflow icon** (📊) in the left sidebar
2. The Automation Workflows module will open with a blank canvas
3. You'll see a toolbar at the top with shape tools and controls

### Understanding the Interface

**Canvas Area:**
- Central workspace where you build workflows
- Drag shapes onto the canvas
- Click and drag to connect shapes
- Right-click shapes for options (edit, delete, change color)

**Toolbar:**
- **Shape tools** - Hexagon (triggers), Rectangle (actions), Diamond (decisions)
- **Connection tool** - Draw arrows between shapes
- **Save** - Save your workflow
- **Load** - Open saved workflows
- **Send to AI** - Get AI assistance with your workflow

**Sidebar:**
- **Saved Workflows** - List of your existing workflows
- **Status badges** - DRAFT, ACTIVE, DISABLED
- **Execution stats** - Run count, success rate, last run time

---

## Creating Your First Workflow

### Step 1: Define Your Goal

Before you start, clearly define what you want to automate. Example:
> "Every morning at 9 AM, I want to get my unread emails, summarize them, and send myself a digest."

### Step 2: Add a Trigger (Start Point)

1. Click the **Hexagon** shape tool in the toolbar
2. Click on the canvas to place it
3. Double-click the shape to edit the text
4. Name it descriptively: `"Daily at 9 AM"` or `"New Email Received"`

**Trigger Types:**
- **Schedule** - Run at specific times (cron schedule)
- **Manual** - Run when you click "Execute"
- **Webhook** - Run when external system calls
- **Event** - Run when something happens (e.g., new email)

### Step 3: Add Actions (What Happens)

1. Click the **Rectangle** shape tool
2. Place it below your trigger
3. Name it with the action: `"Get Unread Emails"`
4. Add more action shapes for each step

**Common Actions:**
- `"Send Email"` - Gmail/Outlook email sending
- `"Update Spreadsheet"` - Google Sheets updates
- `"Post Message"` - Slack/Teams notifications
- `"Analyze Text"` - AI summarization/analysis

### Step 4: Connect the Shapes

1. Click the **Connection** tool
2. Click the trigger shape
3. Click the first action shape
4. An arrow appears showing the flow
5. Continue connecting all shapes in order

### Step 5: Add Decision Points (Optional)

If your workflow needs conditional logic:

1. Click the **Diamond** shape tool
2. Place it where a decision is needed
3. Name it: `"Is Priority Email?"`
4. Connect it to two different paths:
   - One arrow for "Yes" → High priority actions
   - One arrow for "No" → Normal handling

### Step 6: Save Your Workflow

1. Click the **Save** button in the toolbar
2. Enter a descriptive title: `"Daily Email Digest"`
3. Add a description: `"Summarizes unread emails every morning"`
4. Choose a category: `email`
5. The system generates a unique **slug** (ID): `daily-email-digest`

**Important:** The slug is permanent and used to identify your workflow. Keep it handy!

---

## Understanding Workflow Components

### Shapes and Colors

**Hexagon (Triggers)** - Starting points
- 🟢 **Green** - Scheduled triggers
- 🔵 **Blue** - Event-based triggers
- 🟡 **Yellow** - Manual triggers
- 🟣 **Purple** - Webhook triggers

**Rectangle (Actions)** - Tasks to perform
- 🔵 **Blue** - Standard actions
- 🟡 **Yellow** - Data processing
- 🟢 **Green** - Success actions
- 🔴 **Red** - Error handling

**Diamond (Decisions)** - Conditional logic
- 🟡 **Yellow** - Decision points
- 🟣 **Purple** - Complex conditions

**Circle (End Points)** - Flow completion
- 🟢 **Green** - Successful completion
- 🔴 **Red** - Error/failure end

### Connections (Arrows)

- **Solid lines** - Standard flow (one step to next)
- **Labels on arrows** - Data passed between steps (e.g., "email content")
- **Multiple arrows from one shape** - Conditional branching

### Workflow Status

Your workflow can be in one of these states:

- 📝 **DRAFT** - Being designed, not yet active
- ✅ **ACTIVE** - Published and running on schedule
- ⏸️ **DISABLED** - Temporarily paused
- 🗑️ **DELETED** - Permanently removed

---

## Publishing and Scheduling

### Publishing Your Workflow

Once your workflow is designed and saved, you need to **publish** it to make it live:

1. **Click "Publish" button** in the toolbar
2. **Review validation results:**
   - ✅ All shapes connected?
   - ✅ Trigger configured?
   - ✅ Actions have required parameters?
3. **Set up schedule** (if using time-based trigger):
   - Choose frequency: Daily, Hourly, Weekly, Custom
   - Set timezone (default: UTC)
   - Example: `0 9 * * *` = Every day at 9 AM
4. **Confirm publishing**

**What happens when you publish:**
- System validates your workflow structure
- Creates an **automation** record in the database
- Generates an **automation slug** (separate from workflow slug)
- Links the automation to your current conversation thread
- Starts the scheduler (if time-based)

### Understanding Slugs

Your workflow has TWO slugs:

**1. Workflow Slug** (Design Phase)
- 🟠 **Orange pill** in thread list
- Used for editing in the canvas
- Example: `daily-email-digest`
- Never changes

**2. Automation Slug** (Execution Phase)
- 🔵 **Blue pill** in thread list
- Used for live execution
- Example: `daily-email-digest-live`
- Created when you publish

**Why two slugs?**
- You can edit the workflow design without affecting the running automation
- You can have multiple published versions of the same workflow design
- You can pause automation but keep the workflow design for later

### Scheduling Options

**Cron Schedule (Advanced Users):**
```
0 9 * * *   = Daily at 9 AM
0 */2 * * * = Every 2 hours
0 0 * * 1   = Every Monday at midnight
*/15 * * * *= Every 15 minutes
```

**User-Friendly Options:**
- **Hourly** - Every hour on the hour
- **Daily** - Once per day at specified time
- **Weekly** - Once per week on specified day
- **Monthly** - First day of each month
- **Custom** - Enter your own cron expression

---

## Working with AI Assistants

Your AI assistant can help you create, modify, and troubleshoot workflows. Here's how to collaborate effectively:

### Method 1: Ask AI to Create a Workflow

**User:** "Create a workflow that backs up my Google Sheets to Drive every day at 2 AM"

**AI Response:**
```
I'll create that backup workflow for you!

[AI calls automation_create_workflow tool]

✅ Created: "Daily Sheets Backup"
📋 Workflow slug: daily-sheets-backup
🔵 Automation slug: daily-sheets-backup-live

This workflow will:
1. ⏰ Trigger: Every day at 2:00 AM
2. 📊 Get list of your Google Sheets
3. 💾 Copy each sheet to Drive backup folder
4. 📧 Email you a success confirmation

The workflow is now ACTIVE and scheduled. 
Next run: Tomorrow at 2:00 AM UTC.

Would you like me to:
- Add error notifications?
- Change the backup time?
- Include specific sheets only?
```

### Method 2: Drag Workflow Slug to AI

1. **Find your workflow** in the saved workflows sidebar
2. **Drag the slug pill** into the AI chat input
3. **Ask your question:**

**Example:**
```
[daily-email-digest]
Can you explain what this workflow does and suggest improvements?
```

**AI Response:**
```
I've analyzed your "Daily Email Digest" workflow. Here's what it does:

📧 Current Flow:
1. Trigger at 9 AM daily
2. Fetches last 20 unread emails
3. Summarizes content using AI
4. Sends summary email to you

💡 Suggested Improvements:
1. Add error handling for API failures
2. Filter spam before summarizing
3. Categorize emails by priority
4. Add retry logic if Gmail is down

Would you like me to implement any of these improvements?
```

### Method 3: Click "Send to AI" Button

1. **Open your workflow** in the canvas
2. **Click "Send to AI"** button in toolbar
3. **The workflow is automatically added** to the AI chat
4. **Describe what you want:**

**Example:**
```
[AUTOMATION: Daily Email Digest (daily-email-digest)]
Add a step that filters out newsletter emails before summarizing
```

**AI Response:**
```
I'll add email filtering to your workflow!

[AI calls automation_update_workflow]

✅ Updated workflow:
- Added "Filter Newsletters" step after email fetch
- Filters use common newsletter patterns:
  - Unsubscribe links
  - Marketing keywords
  - Bulk sender patterns
- Filtered emails bypass the summarization

Your workflow now processes only personal/work emails.
The canvas will refresh with the updated flow in 3 seconds.
```

### Method 4: Copy/Paste Slug

1. **Click the slug pill** (copies to clipboard)
2. **Paste in AI chat:** `daily-email-digest`
3. **AI recognizes it** and loads the workflow

### Common AI Commands

**Viewing:**
- `Show me all my workflows`
- `What does [slug] do?`
- `Explain this workflow step by step`

**Creating:**
- `Create a workflow that [describe goal]`
- `Build an automation for [task]`
- `I need to automate [process]`

**Modifying:**
- `Add error handling to [slug]`
- `Change the schedule to [new time]`
- `Remove the [step name] action`
- `Add a step that [does something]`

**Executing:**
- `Run [slug] now`
- `Execute [slug] with [custom data]`
- `Test [slug] and show results`

**Monitoring:**
- `How is [slug] performing?`
- `Show execution history for [slug]`
- `Why did [slug] fail last time?`
- `What's the success rate of [slug]?`

---

## Monitoring and Troubleshooting

### Checking Execution Status

**In the Sidebar:**
- Each workflow shows live stats:
  - ✅ **Success count** - Green checkmark
  - ❌ **Error count** - Red exclamation
  - ⚡ **Last run** - Time ago (e.g., "2h ago")
  - 🔄 **Total runs** - Lifetime execution count

**Click a workflow** to see detailed history:
- Execution timeline
- Success/failure for each run
- Error messages for failed runs
- Tools used in each execution
- Duration of each run

### Common Issues and Solutions

**Issue: "Workflow won't start"**
- ✅ Check if it's ACTIVE (not DRAFT or DISABLED)
- ✅ Verify schedule is correct (not in the past)
- ✅ Ensure trigger is properly configured
- ✅ Look for validation errors in the publish step

**Issue: "Workflow fails every time"**
- ❌ **Authentication errors** - Reconnect Google/Microsoft accounts
- ❌ **Missing permissions** - Grant required API access
- ❌ **Invalid data** - Check input parameters
- ❌ **API limits exceeded** - Reduce frequency or data volume

**Issue: "Some runs succeed, some fail"**
- ⚠️ **Intermittent failures** - Add retry logic
- ⚠️ **Rate limiting** - Space out API calls
- ⚠️ **Conditional logic** - Check decision points
- ⚠️ **External dependencies** - Add timeout handling

### Getting Help from AI

If your workflow is failing, ask AI to diagnose:

**User:** `[my-workflow-slug] keeps failing, can you check what's wrong?`

**AI Response:**
```
I've checked your workflow's execution history. Here's what I found:

🔴 Last 5 executions failed with:
Error: "Gmail API returned 403 Forbidden"

Root Cause:
Your Gmail authentication token expired. This happens when:
- You changed your Google password
- Security settings updated
- 30 days passed since last login

🔧 Fix:
1. Go to Settings → Account Linking
2. Click "Reconnect Google Workspace"
3. Complete OAuth flow
4. Return here and I'll test the workflow

Once reconnected, I'll add token refresh logic to prevent this in the future.
```

---

## Common Use Cases

### 1. Email Automation

**Daily Email Digest:**
```
Trigger: Daily at 9 AM
↓
Get Unread Emails (Gmail)
↓
Filter Out Spam/Newsletters
↓
Summarize with AI
↓
Send Digest Email
```

**Auto-Response for VIPs:**
```
Trigger: New Email Received
↓
Check If Sender Is VIP (Decision)
├─ YES → Send Auto-Reply "I'll respond soon"
└─ NO  → Mark as Read
```

### 2. Data Processing

**Daily Sales Report:**
```
Trigger: Daily at 6 PM
↓
Get Orders from Shopify
↓
Calculate Daily Revenue
↓
Append Row to Google Sheets
↓
Send Summary to Slack
```

**Weekly Backup:**
```
Trigger: Every Sunday at 2 AM
↓
List All Google Sheets
↓
For Each Sheet:
  ├─ Copy to Backup Folder
  └─ Compress as ZIP
↓
Email Backup Link
```

### 3. Notifications

**Low Inventory Alert:**
```
Trigger: Every 2 Hours
↓
Check Inventory Levels (API)
↓
Filter Items Below Threshold (Decision)
├─ Items Found → Send Slack Alert
└─ None Found  → End
```

**Bill Payment Reminder:**
```
Trigger: 3 Days Before Due Date
↓
Get Upcoming Bills (Database)
↓
Send Reminder Email
↓
Add to Google Calendar
```

### 4. Content Management

**Auto-Publish Blog Posts:**
```
Trigger: Manual (User Clicks)
↓
Get Draft Post from Google Docs
↓
Format for WordPress
↓
Upload Images to CDN
↓
Publish Post
↓
Share on Social Media
```

**Document Organization:**
```
Trigger: New File in Drive Folder
↓
Analyze File Type (Decision)
├─ PDF  → Move to Documents/PDF
├─ IMG  → Move to Images/2025
└─ Other → Flag for Review
```

---

## Best Practices

### Design Principles

✅ **DO:**
- Start simple - Add complexity later
- Use clear, descriptive shape names
- Add comments/notes to complex logic
- Test with manual trigger before scheduling
- Include error handling paths
- Use consistent color coding

❌ **DON'T:**
- Create overly complex workflows (split into smaller ones)
- Skip validation steps
- Schedule without testing first
- Ignore error notifications
- Forget to document what the workflow does

### Performance Tips

**For Frequent Workflows (Every 5-15 minutes):**
- Keep action count low (< 10 steps)
- Use efficient API calls (bulk operations)
- Cache data when possible
- Set reasonable timeouts

**For Long-Running Workflows:**
- Add progress notifications
- Split into multiple smaller workflows
- Use webhooks instead of polling
- Implement checkpoints for resumption

### Security Considerations

🔒 **Sensitive Data:**
- Don't log passwords or API keys in workflow steps
- Use secure credential storage (linked accounts)
- Limit workflow access with permissions
- Audit execution logs regularly

🔒 **API Access:**
- Use service accounts for automation
- Grant minimal required permissions
- Rotate credentials periodically
- Monitor for suspicious activity

### Maintenance

**Weekly:**
- ✅ Check execution logs for errors
- ✅ Review failure rates
- ✅ Update outdated API calls

**Monthly:**
- ✅ Audit all active workflows
- ✅ Remove unused workflows
- ✅ Optimize slow-running workflows
- ✅ Test disaster recovery

---

## Frequently Asked Questions

### General Questions

**Q: How many workflows can I create?**
A: No hard limit. However, we recommend organizing workflows by function and archiving unused ones.

**Q: Can workflows call other workflows?**
A: Yes! Use the `Execute Workflow` action and provide the target workflow's slug.

**Q: What happens if a workflow fails?**
A: The system logs the error, notifies you (if configured), and stops execution. You can review logs and re-run manually.

**Q: Can I export workflows?**
A: Yes. Click "Export" to download as JSON. You can import it later or share with others.

### Scheduling Questions

**Q: What timezone are schedules in?**
A: UTC by default. You can specify a timezone when publishing (e.g., "America/New_York").

**Q: Can I run a workflow immediately?**
A: Yes. Click "Execute Now" or use a manual trigger.

**Q: How do I change the schedule?**
A: Edit the workflow, modify the trigger shape, and republish.

**Q: What if I miss a scheduled run?**
A: The system will catch up by running it once (not multiple times for each missed slot).

### Editing Questions

**Q: Can I edit an active workflow?**
A: Yes, but changes won't take effect until you republish. The current automation continues with the old version.

**Q: What happens to the workflow slug when I edit?**
A: The workflow slug stays the same. If you publish, you get a new automation slug (version tracking).

**Q: Can I undo changes?**
A: Yes. Use the "Revert" button to restore the last saved version, or ask AI to roll back to a previous version.

### AI Collaboration Questions

**Q: Can AI create workflows without me?**
A: AI can design workflows, but YOU must approve and publish them. AI needs your permission to make workflows active.

**Q: Can AI access my workflow data?**
A: Only when you explicitly share the workflow slug with AI. AI cannot see your workflows unless you drag them into the chat or mention them.

**Q: What if AI makes a mistake in my workflow?**
A: You can always manually edit in the canvas or ask AI to fix it. All changes are tracked, so you can revert if needed.

**Q: Can AI monitor my workflows 24/7?**
A: AI can check status when you ask, but continuous monitoring requires you to set up notification workflows (e.g., "Alert me if X fails 3 times").

### Troubleshooting Questions

**Q: Why is my workflow not appearing in the list?**
A: Check that you saved it (not just closed the canvas). Also verify you're viewing the correct category filter.

**Q: Why did my workflow suddenly stop working?**
A: Common causes:
- Account credentials expired (reconnect)
- API changes from provider (update actions)
- Workflow disabled accidentally (re-enable)

**Q: How do I debug a failing workflow?**
A: 
1. Check execution logs for error messages
2. Run manually and observe each step
3. Ask AI to analyze: `[slug] keeps failing, why?`
4. Add logging/notification actions to track progress

**Q: Can I test a workflow without making it live?**
A: Yes! Use a manual trigger and click "Execute Now" before publishing.

---

## Training Exercises

### Exercise 1: Create Your First Workflow

**Goal:** Build a simple "Hello World" workflow

1. Add a hexagon trigger labeled "Manual"
2. Add a rectangle action labeled "Send Email"
3. Connect trigger → action
4. Save as "my-first-workflow"
5. Publish (no schedule needed)
6. Click "Execute Now"
7. Check your email!

### Exercise 2: Schedule a Daily Task

**Goal:** Automate a daily reminder

1. Trigger: "Daily at 8 AM"
2. Action: "Get Today's Calendar Events" (Google Calendar)
3. Action: "Send Summary Email"
4. Save and publish with schedule
5. Wait for first execution (or test manually)

### Exercise 3: Add Conditional Logic

**Goal:** Process emails differently based on sender

1. Trigger: "New Email Received"
2. Action: "Get Email Details"
3. Decision: "Is Sender My Boss?"
   - YES → "Send Auto-Reply + Flag Urgent"
   - NO → "Mark as Read"
4. Save and publish

### Exercise 4: Work with AI

**Goal:** Let AI help you build a workflow

1. Ask AI: "Create a workflow that backs up my Sheets weekly"
2. Drag the created workflow slug to chat
3. Ask AI: "Add error handling to this"
4. Review AI's changes in the canvas
5. Publish if satisfied

---

## AI Agent Instructions

*This section is specifically for AI assistants helping users with workflows.*

### AI Agent Core Responsibilities

When a user interacts with automation workflows, you must:

1. ✅ **Recognize workflow slugs** in conversation (brackets, pills, or plain text)
2. ✅ **Load workflow data** using appropriate tools when slug is mentioned
3. ✅ **Explain workflows** in clear, non-technical language
4. ✅ **Suggest improvements** based on best practices
5. ✅ **Create workflows** when users describe automation goals
6. ✅ **Modify workflows** when users request changes
7. ✅ **Troubleshoot failures** by analyzing execution logs
8. ✅ **Guide users** through the canvas UI if needed

### AI Tool Selection Decision Tree

#### STEP 1: Does the message contain a workflow slug?

**Slug Detection Patterns:**
- Brackets: `[email-to-sheets-automation]`
- Pills: `[AUTOMATION: Title (slug)]`
- Plain text matching pattern: `lowercase-with-hyphens`

**If YES:** Load the workflow first
```python
automation_get_workflow(automation_id='slug')
```

**If NO:** Check user intent (Step 2)

#### STEP 2: What does the user want to do?

**Intent: CREATE**
- Keywords: "create", "build", "make", "new workflow"
- **Tool:** `automation_create_workflow`

**Intent: LIST**
- Keywords: "show", "list", "what workflows", "my automations"
- **Tool:** `automation_list_workflows`

**Intent: MODIFY** (slug provided)
- Keywords: "update", "change", "modify", "add step", "remove action", "edit"
- **Tool:** `automation_update_workflow`

**Intent: EXECUTE**
- Keywords: "run", "execute", "start", "trigger now"
- **Tool:** `automation_execute_workflow`

**Intent: SCHEDULE**
- Keywords: "schedule", "automate", "run every", "daily at"
- **Tool:** `automation_schedule_workflow`

**Intent: MONITOR**
- Keywords: "status", "how is it doing", "execution history", "logs"
- **Tool:** `automation_get_execution_history`

**Intent: DELETE**
- Keywords: "delete", "remove", "get rid of"
- **Tool:** `automation_delete_workflow`

#### STEP 3: Execute the appropriate tool

**After tool execution:**
1. ✅ Confirm success or explain error
2. ✅ Show what changed (if applicable)
3. ✅ Suggest next steps
4. ✅ Ask if user wants modifications

### AI Response Templates

#### Template: Workflow Creation

```markdown
I've created your "[WORKFLOW_TITLE]" workflow!

📋 **Workflow Details:**
- **Slug:** `[workflow-slug]`
- **Automation Slug:** `[automation-slug-live]` (if published)
- **Status:** DRAFT / ACTIVE

🔧 **What it does:**
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

⚙️ **Configuration:**
- **Trigger:** [Manual / Schedule: X]
- **Actions:** [Count] steps
- **Category:** [email / data_processing / etc.]

✅ **Next Steps:**
- Test it: "Run this workflow now"
- Schedule it: "Run this daily at 9 AM"
- Modify it: "Add error handling"
- View in canvas: [Workflow pill inserted]

Would you like me to schedule it or make any changes?
```

#### Template: Workflow Explanation

```markdown
I've analyzed the "[WORKFLOW_TITLE]" workflow. Here's what it does:

📊 **Flow Diagram:**
[Trigger] → [Action 1] → [Decision?] → [Action 2] → [End]

📝 **Step-by-Step:**
1. **[Shape Name]** ([Type])
   - Purpose: [What it does]
   - Connects to: [Next step]

2. **[Shape Name]** ([Type])
   - Purpose: [What it does]
   - Connects to: [Next step]

⚙️ **Current Configuration:**
- **Trigger Type:** [Schedule / Manual / Event]
- **Total Actions:** [Count]
- **Has Error Handling:** YES / NO
- **Last Modified:** [Date]

📊 **Execution Stats:**
- **Total Runs:** [Count]
- **Success Rate:** [Percentage]
- **Last Run:** [Time ago]

💡 **Suggestions for Improvement:**
1. [Suggestion 1]
2. [Suggestion 2]
3. [Suggestion 3]

Would you like me to implement any of these improvements?
```

#### Template: Workflow Modification

```markdown
✅ I've updated your "[WORKFLOW_TITLE]" workflow!

🔄 **Changes Made:**

**Added:**
- ➕ [New step name] - [Description]
- ➕ [Another new step] - [Description]

**Removed:**
- ➖ [Removed step name]

**Modified:**
- ✏️ [Changed step] - [What changed]

📊 **Updated Flow:**
[Trigger] → [Step 1] → [NEW STEP] → [Step 2] → [End]

⚠️ **Important Notes:**
- [Any warnings or considerations]
- [Impact on execution]

🎨 **Visual Changes:**
The canvas will refresh in 3 seconds to show the updated flow.

✅ **Status:** 
- Your workflow is still [ACTIVE / DRAFT]
- [If active] Changes will take effect on the next scheduled run
- [If draft] Publish it to activate: "Publish this workflow"

Would you like me to:
- Test the updated workflow?
- Explain any of the new steps?
- Make additional changes?
```

#### Template: Execution Results

```markdown
✅ Workflow executed successfully!

📊 **Execution Summary:**
- **Workflow:** [Title] ([slug])
- **Started:** [Timestamp]
- **Completed:** [Timestamp]
- **Duration:** [X seconds / minutes]
- **Status:** SUCCESS / FAILED

🔧 **Steps Executed:**
1. ✅ [Step 1] - [Result]
2. ✅ [Step 2] - [Result]
3. ✅ [Step 3] - [Result]

📈 **Results:**
- [Key metric 1]: [Value]
- [Key metric 2]: [Value]
- [Output summary]

🔄 **Next Run:** [If scheduled: timestamp]

Would you like me to:
- Retry the workflow?
- Investigate the error?
- Modify the workflow to prevent this issue?
```

#### Template: Troubleshooting

```markdown
I've analyzed the failures in your "[WORKFLOW_TITLE]" workflow.

🔴 **Problem Identified:**
- **Error:** [Error message]
- **Frequency:** [X of Y runs failed]
- **First Occurred:** [Date]
- **Last Occurred:** [Date]

🔍 **Root Cause:**
[Explanation of why it's failing]

**Common Causes:**
1. [Cause 1] - [Likelihood: High/Medium/Low]
2. [Cause 2] - [Likelihood: High/Medium/Low]
3. [Cause 3] - [Likelihood: High/Medium/Low]

🔧 **Recommended Fixes:**

**Immediate Fix:**
[Step-by-step instructions]

**Long-term Solution:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

💡 **Preventive Measures:**
- Add retry logic for [step]
- Implement timeout handling
- Add error notifications
- Use fallback actions

Would you like me to:
- Apply the immediate fix now?
- Implement the long-term solution?
- Add preventive measures to the workflow?
```

### AI Best Practices

#### Communication Style

✅ **DO:**
- Use clear, non-technical language for non-technical users
- Structure responses with headers and bullet points
- Provide specific, actionable next steps
- Explain WHY something is recommended, not just WHAT

❌ **DON'T:**
- Use jargon without explanation
- Give vague responses like "Try fixing it"
- Overwhelm with too many options
- Skip validation/error checking
- Assume user understands technical concepts

#### Workflow Creation Guidelines

When creating workflows for users:

1. ✅ **Start simple** - Don't over-engineer the first version
2. ✅ **Ask clarifying questions** if the goal is unclear
3. ✅ **Suggest trigger type** based on user's description
4. ✅ **Include error handling** by default
5. ✅ **Test before publishing** (offer to run manually)
6. ✅ **Explain the schedule** in user-friendly terms
7. ✅ **Link to current thread** so user can find it later

**Example:**
```
User: "I want to automate my email responses"

❌ BAD AI RESPONSE:
"I've created an email automation workflow. It's done."

✅ GOOD AI RESPONSE:
"I'd love to help automate your email responses! 

Before I create the workflow, let me clarify:
- Which emails should get auto-responses? (all / VIPs only / specific senders)
- What should the response say?
- Should this run continuously or only during business hours?
- Do you want to review emails before responding, or fully automatic?

Once I know these details, I'll build a custom workflow for you!"
```

#### Modification Guidelines

When modifying existing workflows:

1. ✅ **Always load the workflow first** using the slug
2. ✅ **Explain what currently exists** before changing
3. ✅ **Confirm the changes** with the user before applying
4. ✅ **Show before/after** comparison
5. ✅ **Warn about breaking changes** (e.g., removing critical steps)
6. ✅ **Offer to test** after modification

#### Error Handling Guidelines

When workflows fail:

1. ✅ **Fetch execution history** immediately
2. ✅ **Identify the failing step** specifically
3. ✅ **Explain in simple terms** what went wrong
4. ✅ **Provide 2-3 solutions** (quick fix + proper fix)
5. ✅ **Offer to implement fixes** automatically
6. ✅ **Add preventive measures** to avoid recurrence

### AI Knowledge Base

#### Common Workflow Patterns

**Email Processing:**
```python
automation_create_workflow(
    title="Email Processor",
    trigger={"type": "event", "event": "new_email"},
    actions=[
        {"tool": "gmail_get_message", "params": {"message_id": "{{trigger.id}}"}},
        {"tool": "ai_analyze_email", "params": {"text": "{{email.body}}"}},
        {"tool": "gmail_label_message", "params": {"label": "{{analysis.category}}"}}
    ]
)
```

**Data Sync:**
```python
automation_create_workflow(
    title="Daily Sales Sync",
    trigger={"type": "schedule", "cron": "0 0 * * *"},
    actions=[
        {"tool": "shopify_get_orders", "params": {"since": "yesterday"}},
        {"tool": "google_sheets_append_rows", "params": {"data": "{{orders}}"}}
    ]
)
```

**Notification System:**
```python
automation_create_workflow(
    title="Inventory Alert",
    trigger={"type": "schedule", "cron": "0 */4 * * *"},
    actions=[
        {"tool": "check_inventory_levels"},
        {"tool": "slack_send_message", "params": {"text": "{{alert}}"}}
    ]
)
```

#### Cron Schedule Quick Reference

| Human Time | Cron Expression | Example Use Case |
|------------|----------------|------------------|
| Every 15 minutes | `*/15 * * * *` | Real-time monitoring |
| Every hour | `0 * * * *` | Hourly syncs |
| Every 2 hours | `0 */2 * * *` | Periodic checks |
| Daily at 9 AM | `0 9 * * *` | Morning reports |
| Weekly on Monday | `0 0 * * 1` | Weekly summaries |
| First of month | `0 0 1 * *` | Monthly invoices |
| Weekdays at 5 PM | `0 17 * * 1-5` | EOD reports |

#### Tool Categories and Use Cases

**Email Tools:**
- `gmail_send_email` - Send emails
- `gmail_get_messages` - Fetch emails
- `gmail_label_message` - Organize emails
- `gmail_search_messages` - Find specific emails

**Spreadsheet Tools:**
- `google_sheets_append_row` - Add data
- `google_sheets_read_data` - Fetch data
- `google_sheets_update_cell` - Modify cells
- `google_sheets_create` - Create new sheets

**AI Tools:**
- `ai_summarize_text` - Summarize content
- `ai_analyze_sentiment` - Analyze tone
- `ai_extract_data` - Pull structured data
- `ai_generate_text` - Create content

**Notification Tools:**
- `slack_post_message` - Slack notifications
- `microsoft_teams_send_message` - Teams alerts
- `email_send` - Email notifications
- `sms_send` - Text messages

### AI Debugging Process

When a workflow fails, follow this systematic approach:

#### Step 1: Gather Information
```python
# Get execution history
history = automation_get_execution_history(automation_id='slug', limit=10)

# Identify pattern
- How many failures? (all / intermittent)
- When did it start failing? (specific date)
- What's the error message?
```

#### Step 2: Categorize the Error

**Authentication Errors:**
- `403 Forbidden` → Expired credentials
- `401 Unauthorized` → Missing permissions
- **Fix:** Reconnect account, grant permissions

**Rate Limit Errors:**
- `429 Too Many Requests` → API limit exceeded
- **Fix:** Reduce frequency, add delays

**Data Errors:**
- `400 Bad Request` → Invalid parameters
- `404 Not Found` → Resource doesn't exist
- **Fix:** Validate inputs, check references

**Timeout Errors:**
- `504 Gateway Timeout` → External service slow
- **Fix:** Increase timeout, add retries

#### Step 3: Propose Solution

**Template:**
```markdown
🔴 Error: [Error category]

**Root Cause:**
[Explanation]

**Quick Fix:** (Immediate relief)
1. [Step 1]
2. [Step 2]

**Proper Fix:** (Long-term solution)
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prevention:**
- [Measure 1]
- [Measure 2]

Shall I apply the quick fix now and schedule the proper fix?
```

### AI Safety Rules

#### Never Do These Without Explicit User Approval:

❌ **Delete workflows** - Always confirm first
❌ **Publish workflows** - User must review and approve
❌ **Modify active automations** - Warn about downtime
❌ **Share user data** - Privacy is paramount
❌ **Execute workflows with financial impact** - Require confirmation
❌ **Disable critical automations** - Explain consequences first

#### Always Do These:

✅ **Validate user intent** before major actions
✅ **Explain risks** when suggesting changes
✅ **Provide rollback options** after modifications
✅ **Test workflows** in safe mode before going live
✅ **Document changes** in workflow description
✅ **Notify users** of execution failures

### AI Success Metrics

Track these KPIs to improve AI assistance:

📊 **User Satisfaction:**
- Workflow creation success rate (target: 95%+)
- User returns to modify workflow (target: <10%)
- User approves AI suggestions (target: 80%+)

⚡ **Efficiency:**
- Time to create workflow (target: <2 minutes)
- Questions needed to clarify intent (target: ≤3)
- Successful first-time executions (target: 90%+)

🎯 **Accuracy:**
- Workflows work as intended (target: 95%+)
- Errors fixed on first attempt (target: 85%+)
- Suggestions adopted by users (target: 70%+)

---

## Quick Reference Card

### Canvas Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Add Hexagon | `H` | Add trigger shape |
| Add Rectangle | `R` | Add action shape |
| Add Diamond | `D` | Add decision shape |
| Delete Shape | `Delete` | Remove selected shape |
| Save | `Ctrl+S` | Save workflow |
| Undo | `Ctrl+Z` | Undo last change |
| Connect | `C` | Activate connection tool |

### Status Icons

| Icon | Meaning |
|------|---------|
| 🟢 | Active and running |
| 🟡 | Draft (not published) |
| 🔴 | Error/Disabled |
| ⏸️ | Paused |
| ✅ | Last run succeeded |
| ❌ | Last run failed |

### Workflow Lifecycle

```
1. DESIGN    → Drag shapes on canvas
2. SAVE      → Click Save button
3. PUBLISH   → Click Publish button
4. SCHEDULE  → Set cron schedule
5. MONITOR   → Check execution logs
6. EDIT      → Modify and republish
```

---

**End of Complete Guide**

*For additional help, use the AI chat or visit the documentation portal.*
