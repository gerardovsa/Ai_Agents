# Agent Context Template

Create one for each AI agent in `agents/` folder:

---

# [FEATURE]_AGENT Context

**Agent Name:** [Feature/Domain] Agent  
**Created:** YYYY-MM-DD  
**Owner:** [Your name or team]  
**Status:** [Active / In Development / Completed]

---

## Scope

This agent ONLY handles [specific feature/domain] features.

**DO work on:**
- [Specific area 1]
- [Specific area 2]
- [Specific area 3]

**DO NOT work on:**
- [Out of scope area 1]
- [Out of scope area 2]
- [Another agent's domain]

---

## Files This Agent Works With

### Primary Files (Modify Freely)
- `src/[path]/file1.js` - [Purpose]
- `src/[path]/file2.js` - [Purpose]

### Read-Only Files (Can read, cannot modify)
- `src/[path]/sharedFile.js` - [What to use from it]

### Related Files (Might need occasionally)
- `src/[path]/relatedFile.js` - [When to use it]

---

## Key Decisions

### Technical Decisions
- **[Decision 1]:** [What was decided and why]
- **[Decision 2]:** [What was decided and why]

### Architecture Decisions
- **Pattern:** [Design pattern used]
- **Database:** [Database choice and why]
- **External Services:** [Third-party services and why]

### Security Decisions
- **Authentication:** [Approach]
- **Authorization:** [Approach]
- **Data Protection:** [Approach]

---

## Architecture

### Data Flow
```
[Component A] → [Component B] → [Component C]
      ↓
[Component D]
```

### Code Pattern
All files follow this pattern:
```javascript
// [Show standard pattern]
```

### Dependencies
```
[This Service]
    ↓ uses
[Dependency 1] → [Dependency 2]
    ↓
[External Service]
```

---

## Dependencies

### External Packages
- `package-name` ^[version] - [What it's used for, why chosen]

### Internal Modules
- `src/shared/validation.js` - [What to use from it]
- `src/shared/errorHandler.js` - [What to use from it]

### External Integrations
- **[Service Name]** ([website])
  - API Version: [version]
  - Auth Method: [method]
  - Documentation: [link]
  - Credentials: [where stored]

---

## Conventions & Standards

### Naming
- Functions: [convention, e.g., camelCase]
- Classes: [convention, e.g., PascalCase]
- Files: [convention, e.g., camelCase.js]
- Constants: [convention, e.g., UPPER_SNAKE_CASE]

### Error Handling
- Use: `src/shared/errorHandler.js`
- Pattern:
```javascript
  // [Show error handling pattern]
```

### Logging
- Use: `src/shared/logger.js`
- Levels: [debug, info, warn, error]
- Format:
```javascript
  logger.info('Message', { context: data });
```

### Testing
- Framework: [Jest / Mocha / pytest / etc.]
- Location: `tests/[feature]/`
- Coverage Target: [percentage]%
- Run: `[command]`

---

## API / Interfaces

### Public Functions
```javascript
/**
 * @param {type} param - Description
 * @returns {type} Description
 */
function publicFunction(param) {
  // This is the contract other code can rely on
}
```

### Events Emitted
- `event.name` - [When emitted, payload structure]

### Events Listened To
- `event.name` - [What it does, source]

---

## Current Status

### Completed Features
- ✅ [Feature 1] (YYYY-MM-DD)
- ✅ [Feature 2] (YYYY-MM-DD)

### In Progress
- 🔄 [Feature 3] (Started YYYY-MM-DD, [percentage]% complete)
  - Status: [Details]
  - Blockers: [Any blockers]

### Planned
- ⏳ [Feature 4]
- ⏳ [Feature 5]

---

## Important Notes

### Critical Information
- [Critical note 1]
- [Critical note 2]

### Gotchas & Warnings
- ⚠️ [Warning about edge case]
- ⚠️ [Warning about performance]

### Performance Considerations
- [Performance note 1]
- [Performance note 2]

### Security Considerations
- 🔒 [Security requirement 1]
- 🔒 [Security requirement 2]

---

## Testing

### Unit Tests
- Location: `tests/unit/[feature]/`
- Run: `npm test -- [feature]`
- Coverage: [percentage]%

### Integration Tests
- Location: `tests/integration/[feature]/`
- Run: `npm run test:integration`
- Key Scenarios:
  - [Scenario 1]
  - [Scenario 2]

### Manual Testing
- [Step-by-step manual test procedure]

---

## Related Agents

### Dependencies (This agent needs)
- **[OTHER_AGENT]** for [what functionality]
  - Interface: [How to interact]
  - Contact via: `agents/HANDOFFS.md`

### Dependents (Other agents need this)
- **[OTHER_AGENT]** needs [what functionality]
  - Interface: [What they can use]

---

## Resources

### Documentation
- Internal: [Link to internal docs]
- External: [Link to external docs]
- API Docs: [Link]

### Examples
- Example 1: [Link or file path]
- Example 2: [Link or file path]

---

## Changelog

### YYYY-MM-DD
- [Major change or milestone]

### YYYY-MM-DD
- [Major change or milestone]

---

## AI Usage Instructions

### Starting a Session
```
@file:agents/[FEATURE]_AGENT.md

I'm working on [specific task] for [feature].
Follow the decisions, patterns, and scope defined in this context file.
```

### During Work
- Reference this file frequently
- Update "Current Status" as you progress
- Document decisions in "Key Decisions"
- Log handoffs in `agents/HANDOFFS.md` if needed

### Finishing Work
- Update "Current Status"
- Move completed items to "Completed Features"
- Update relevant folder documentation
- Log changes in CHANGELOG.md
