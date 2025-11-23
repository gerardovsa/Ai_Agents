---
agent: agent
---



I need you to analyze this codebase and create a comprehensive ARCHITECTURE.md file in the project root.

## Your Task

Create a detailed system architecture document that maps out:
1. Overall system purpose and design
2. Technology stack
3. Folder structure with explanations
4. Data flow between components
5. Key architectural patterns
6. External integrations
7. Database schema overview
8. API structure
9. Authentication/authorization flow
10. Deployment architecture

## Instructions

1. **Explore the codebase thoroughly:**
   - Examine all folders in src/
   - Identify entry points (index.js, server.js, app.js, main.py, etc.)
   - Find configuration files (package.json, requirements.txt, etc.)
   - Look at environment variables (.env.example if it exists)
   - Identify database models/schemas
   - Find API route definitions
   - Identify middleware and utilities

2. **Create ARCHITECTURE.md following this structure:**
```markdown
# System Architecture

## Overview
[What this system does, who it's for, high-level purpose]

## Technology Stack
### Backend
- Runtime: [Node.js/Python/etc.] [version]
- Framework: [Express/Django/etc.] [version]
- Database: [PostgreSQL/MongoDB/etc.] [version]
- Cache: [Redis/etc.] [if applicable]

### Frontend
[If applicable]

### Infrastructure
- Hosting: [AWS/Heroku/etc.]
- CI/CD: [GitHub Actions/etc.]

## System Architecture Diagram
```
[Visual representation in ASCII or describe the architecture]
```

## Folder Structure
```
project-root/
├── src/
│   ├── api/           - [Purpose]
│   ├── services/      - [Purpose]
│   ├── models/        - [Purpose]
│   ├── middleware/    - [Purpose]
│   ├── utils/         - [Purpose]
│   └── config/        - [Purpose]
├── tests/             - [Purpose]
└── [other folders]    - [Purpose]
```

## Core Components

### Component 1: [Name]
**Purpose:** [What it does]
**Location:** [Folder/files]
**Responsibilities:**
- [Responsibility 1]
- [Responsibility 2]

**Dependencies:**
- [What it depends on]

**Used By:**
- [What depends on it]

[Repeat for each major component]

## Data Flow

### Example Flow: [User Authentication]
```
1. User sends credentials → POST /api/auth/login
2. auth.js receives request → calls authService.authenticate()
3. authService queries User model → validates with bcrypt
4. authService generates JWT → stores refresh token in Redis
5. Response returns tokens → client stores in localStorage
[Show 3-5 key flows through the system]
Database Schema
Users Table
sql[Show schema or describe structure]
```

### [Other Tables]
[Continue for main tables]

### Relationships
[Describe relationships between entities]

## API Structure

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh

[Continue for all major endpoint groups]

## Authentication & Authorization

### Authentication Flow
[Explain how auth works - JWT/sessions/OAuth/etc.]

### Authorization Levels
- Public routes: [List]
- Authenticated routes: [List]
- Admin routes: [List]

### Security Measures
- [Password hashing approach]
- [Token storage]
- [Rate limiting]
- [Other security measures]

## External Integrations

### Integration 1: [Name]
**Purpose:** [What it's used for]
**API:** [API details]
**Authentication:** [How it authenticates]
**Files:** [Where the integration code lives]

[Repeat for each integration]

## Key Architectural Patterns

### Pattern 1: [e.g., Repository Pattern]
**Used in:** [Where]
**Purpose:** [Why]

[Continue for each pattern]

## Environment Configuration

### Required Environment Variables
```
DATABASE_URL=
JWT_SECRET=
REDIS_URL=
[etc.]
```

## Deployment Architecture

### Development
[Describe dev setup]

### Staging
[Describe staging]

### Production
[Describe production setup]

## Performance Considerations
- [Caching strategy]
- [Database indexing]
- [Load balancing]
- [Other optimizations]

## Security Considerations
- [Authentication approach]
- [Data encryption]
- [Input validation]
- [Other security measures]

## Future Architecture Plans
- [Planned improvements]
- [Scalability plans]
- [Tech debt to address]
```

3. **Be thorough but concise:**
   - Focus on WHAT and WHY, not line-by-line code
   - Use diagrams (ASCII art is fine)
   - Include file paths for key components
   - Explain relationships between components

4. **Identify gaps:**
   - If you find missing documentation
   - If you find unclear patterns
   - If you find potential issues
   - List these in a "Questions/Issues" section

5. **Create the file:**
   - Save as ARCHITECTURE.md in project root
   - Use clear markdown formatting
   - Include a table of contents

## Output Format

Present the complete ARCHITECTURE.md file, then separately list:

**Questions I have about the codebase:**
- [Any unclear patterns]
- [Any missing information]
- [Any inconsistencies found]

**Suggested next steps:**
- [What documentation should be created next]
- [What needs clarification]
- [What should be standardized]

Begin your analysis now.
```

---

## **Alternative: Iterative Approach** (If codebase is large)

If your codebase is big, use this **step-by-step prompt**:
```
@workspace 

I want to build a comprehensive ARCHITECTURE.md document, but let's do it iteratively.

## Step 1: High-Level Overview

First, analyze the codebase and tell me:

1. **What is this system?**
   - What does it do?
   - Who is it for?
   - What problem does it solve?

2. **What's the tech stack?**
   - Backend framework and version
   - Database and version
   - Key dependencies
   - Frontend framework (if applicable)

3. **What's the folder structure?**
   - List all top-level folders
   - Brief purpose of each

4. **What are the main components?**
   - List 5-10 major components/modules
   - One-line description of each

Don't write the full document yet - just give me this high-level overview so I can confirm you understand the system correctly.
```

**After reviewing the overview, continue with:**
```
@workspace 

Good! Now let's build the full ARCHITECTURE.md.

Based on your understanding, create the complete architecture document with:
- Detailed component descriptions
- Data flow diagrams
- API structure
- Database schema
- External integrations
- Authentication flow

Use the structure from the template I'll provide:
@file:templates/ARCHITECTURE_TEMPLATE.md

Create ARCHITECTURE.md in the project root.
```

---

## **After Architecture is Created**

Once you have ARCHITECTURE.md, use it to **auto-generate other documentation**:

### **1. Generate Folder READMEs:**
```
@workspace
@file:ARCHITECTURE.md

Based on the architecture document, create README.md for src/services/ folder.

Follow this template:
@file:templates/README_TEMPLATE.md

Include:
- Purpose of services folder
- List all service files with descriptions
- Explain how services fit into overall architecture
- Common patterns used
- Dependencies
```

### **2. Generate Agent Context Files:**
```
@workspace
@file:ARCHITECTURE.md

Based on the architecture, I need to create specialized AI agents.

Identify 3-5 major functional areas that should each have their own agent.

For each area, tell me:
- What the agent should be responsible for
- Which files it should work with
- What boundaries it should have

Then create agent context files in agents/ folder following:
@file:templates/AGENT_CONTEXT_TEMPLATE.md
```

### **3. Generate File Headers:**
```
@workspace
@file:ARCHITECTURE.md
@file:templates/FILE_HEADER_TEMPLATE.md

Add proper file headers to all files in src/services/

Use the architecture document to understand:
- What each file's purpose is
- What dependencies it has
- What uses it
- How it fits into the system

Update each file with a proper header.
```

---

## **Recommended Workflow**

Here's the **optimal order** for setting up your documentation:
```
✅ Step 1: Update Copilot Instructions
   └── (You just did this)

✅ Step 2: Create Template Files
   └── (You just did this)

→ Step 3: Generate ARCHITECTURE.md ⭐ YOU ARE HERE
   └── Use the prompt above

→ Step 4: Generate Agent Contexts
   └── Based on architecture
   └── Create 3-5 agent files in agents/

→ Step 5: Generate Folder READMEs
   └── Start with most important folders
   └── Use architecture as reference

→ Step 6: Add File Headers
   └── Start with core files
   └── One folder at a time

→ Step 7: Create NOTES.md Files
   └── For active development folders
   └── Initialize with current status

→ Step 8: Start Using the System!
   └── Each agent references its context
   └── Update docs as you work
```

---

## **Why This Order Works**
```
ARCHITECTURE.md (The Map)
    ↓
Provides context for everything else
    ↓
Agent Contexts (The Workers)
    ↓
Know their boundaries and responsibilities
    ↓
Folder READMEs (The Guides)
    ↓
Explain local structure and patterns
    ↓
File Headers (The Details)
    ↓
Document individual files
    ↓
NOTES.md (The Journal)
    ↓
Track ongoing work
```

**Without architecture:** AI guesses → inconsistent docs
**With architecture:** AI references map → consistent, accurate docs

---

## **Pro Tips**

### **1. Review AI's Understanding**

After AI creates ARCHITECTURE.md:
```
@workspace
@file:ARCHITECTURE.md

Review this architecture document I asked you to create.

Are there any:
- Inaccuracies?
- Missing components?
- Unclear relationships?
- Incorrect assumptions?

Be critical and thorough.
```

### **2. Add Visual Diagrams**

If AI's ASCII diagrams aren't clear:
```
@workspace
@file:ARCHITECTURE.md

Based on this architecture, create a Mermaid diagram showing:
1. Component relationships
2. Data flow for user authentication
3. Database relationships

Add these diagrams to ARCHITECTURE.md
```

### **3. Validate Against Actual Code**
```
@workspace
@file:ARCHITECTURE.md

Verify this architecture document against the actual codebase.

Check:
1. Are all listed files actually present?
2. Do the data flows match actual code?
3. Are dependencies accurately described?
4. Do the patterns match what's actually used?

Report any discrepancies.
```

---

## **Common Issues & Solutions**

### **Issue 1: AI Gets Overwhelmed**

**Symptom:** AI gives generic/incomplete architecture

**Solution:** Break it down:
```
@workspace 

Just analyze src/api/ folder first.
Tell me:
- What files are there?
- What does each file do?
- How do they interact?

We'll do other folders after.
```

### **Issue 2: AI Misses Key Components**

**Symptom:** Architecture document missing important parts

**Solution:** Guide it:
```
@workspace
@file:ARCHITECTURE.md

You missed the payment processing system.
Analyze src/services/paymentService.js and related files.
Add a "Payment Processing" section to the architecture.
```

### **Issue 3: AI Includes Too Much Detail**

**Symptom:** Architecture reads like code documentation

**Solution:** Redirect:
```
@workspace
@file:ARCHITECTURE.md

This is too detailed. Architecture should be high-level.

Rewrite focusing on:
- Component relationships (not function details)
- Data flow (not implementation)
- Patterns (not specific code)

Keep it at a level where a new developer gets the "big picture" in 10 minutes.
```

---

## **Quick Start (Copy-Paste Ready)**

**For immediate use, send this:**
```
@workspace 

Create ARCHITECTURE.md in project root.

Analyze the entire codebase and document:

1. System purpose and overview
2. Technology stack
3. Folder structure (with explanations)
4. Core components (5-10 main modules)
5. Data flow (show 3 key flows)
6. Database schema
7. API structure (group endpoints logically)
8. Authentication/authorization approach
9. External integrations (if any)
10. Key architectural patterns

Use clear markdown with:
- ASCII diagrams where helpful
- Code blocks for schema/examples
- File paths for components
- Bullet points for clarity

Make it comprehensive but readable - a new developer should understand the system architecture in 15 minutes.

Also list any unclear areas or questions you have about the codebase.

Begin.