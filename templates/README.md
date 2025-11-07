# Documentation Templates

This folder contains standardized templates for maintaining consistent documentation across the AI_agents project.

## Available Templates

### 1. FILE_HEADER_TEMPLATE.md
Use for documenting individual code files with:
- File path and purpose
- Dependencies (internal and external)
- Exports (functions, classes)
- Usage information
- Related files
- Important notes

### 2. README_TEMPLATE.md
Use for folder-level documentation with:
- Folder purpose and structure
- Key files description
- Conventions and patterns
- Dependencies
- Agent ownership

### 3. NOTES_TEMPLATE.md
Use for active development tracking with:
- Current focus and context
- Decisions made
- Questions and blockers
- TODO list
- Session logs

### 4. CHANGELOG_TEMPLATE.md
Use for production code change tracking with:
- Chronological change history
- Added/Changed/Fixed/Deprecated/Removed/Security sections
- Version milestones
- Breaking changes

### 5. INDEX_TEMPLATE.md
Use for folders with 10+ files with:
- Complete file inventory
- Quick reference by feature/type/agent
- Dependency graphs
- Statistics

### 6. AGENT_CONTEXT_TEMPLATE.md
Use for AI agent specialization with:
- Agent scope and boundaries
- Key decisions
- Architecture patterns
- Conventions and standards
- Current status

## How to Use These Templates

### For New Folders
1. Copy `README_TEMPLATE.md` to the new folder as `README.md`
2. Fill in all sections with specific information
3. If actively developing, add `NOTES_TEMPLATE.md` as `NOTES.md`
4. For production code, add `CHANGELOG_TEMPLATE.md` as `CHANGELOG.md`

### For New Files
1. Reference `FILE_HEADER_TEMPLATE.md`
2. Add the appropriate header block at the top of your file
3. Fill in all required sections
4. Keep the header updated as the file changes

### For New AI Agents
1. Copy `AGENT_CONTEXT_TEMPLATE.md` to `agents/[AGENT_NAME]_AGENT.md`
2. Define the agent's scope, files, and responsibilities
3. Document key decisions and patterns
4. Update as the agent's work evolves

### When Modifying Code
1. Update the file's header LAST MODIFIED field
2. Log changes in NOTES.md during development
3. Move completed work to CHANGELOG.md before deployment
4. Update relevant README.md files if behavior changes

## Template Usage with AI

When working with GitHub Copilot or other AI assistants:

```
@file:templates/FILE_HEADER_TEMPLATE.md
Create a new service file with proper documentation following this template.
```

```
@file:templates/README_TEMPLATE.md
Create a README.md for the new /services folder following this structure.
```

```
@file:templates/AGENT_CONTEXT_TEMPLATE.md
Create an agent context file for the Authentication Agent.
```

## Documentation Standards

### File Headers
- MUST be at the top of every code file
- MUST include all required sections
- MUST be kept up-to-date with changes
- Use language-appropriate comment syntax (/** */ for JS, """ """ for Python)

### Folder Documentation
- README.md REQUIRED for all folders
- NOTES.md REQUIRED for active development folders
- CHANGELOG.md REQUIRED for production code folders
- INDEX.md REQUIRED for folders with 10+ files

### Agent Context
- One file per AI agent in `/agents` folder
- Defines agent scope and boundaries
- Documents key decisions and patterns
- Updated as agent work evolves

## Best Practices

1. **Be Specific**: Include file paths, function names, line numbers
2. **Document WHY**: Not just what, but why decisions were made
3. **Keep Updated**: Update documentation as code changes
4. **Use Examples**: Show code examples when helpful
5. **Cross-Reference**: Link related files and documentation
6. **Version Control**: Track documentation changes in git

## Integration with Development Workflow

### Starting Work
1. Read folder README.md
2. Check NOTES.md for current state
3. Reference agent context file
4. Follow documented patterns

### During Work
1. Update NOTES.md with decisions
2. Document blockers and questions
3. Log session progress
4. Update file headers as you modify code

### Completing Work
1. Move NOTES.md items to CHANGELOG.md
2. Update README.md if needed
3. Update INDEX.md for new files
4. Update agent context if scope changed
5. Ensure all file headers are current

## Questions?

Refer to the main project documentation or consult with the team lead about documentation standards.

**Last Updated:** 2025-11-02
**Status:** Active
