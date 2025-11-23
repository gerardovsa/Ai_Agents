# User Instructions Documentation

**Purpose:** End-user documentation for all UI features and platform integrations in the AI Agents system.

## Folder Structure

This folder contains user-facing documentation organized by feature/platform:

```
user_instructions/
├── README.md (this file)
├── chat_interface/          # Chat UI documentation
├── thread_management/       # Thread and conversation management
├── automation_workflows/    # Visual workflow builder
├── task_management/         # Universal task sync
├── integrations/           # Platform-specific guides
│   ├── google_workspace/
│   ├── microsoft_365/
│   ├── slack/
│   ├── shopify/
│   └── ...
└── admin/                  # Admin/setup documentation
```

## Documentation Standards

Each documentation file should follow this format:

### Structure
1. **Overview** - What the feature does (1-2 sentences)
2. **Getting Started** - First steps for new users
3. **Common Tasks** - Step-by-step guides for frequent operations
4. **Tips & Tricks** - Power user features
5. **Troubleshooting** - Common issues and solutions
6. **Examples** - Real-world use cases with screenshots

### Writing Style
- Use simple, clear language
- Include screenshots/GIFs where helpful
- Provide step-by-step instructions
- Focus on USER goals, not technical implementation
- Include "Why" explanations for non-obvious features

### Naming Convention
- Use descriptive names: `how_to_create_workflows.md`
- Prefix with category: `chat_using_markdown_formatting.md`
- Avoid technical jargon in filenames

## Target Audience

- **End Users** - Non-technical users who interact with the UI
- **Power Users** - Users who want to leverage advanced features
- **Administrators** - Users who manage accounts and integrations

## Not Included Here

- Developer documentation (see `/AI_infrastructure/docs/`)
- API documentation (see `/AI_infrastructure/routes/`)
- Tool schemas (see `/tools/schemas/`)
- Internal architecture (see `copilot-instructions.md`)

## Getting Started for Documenters

1. Pick a UI feature or platform integration
2. Create a folder for it (if needed)
3. Create a markdown file with clear, user-focused content
4. Include screenshots from the actual UI
5. Test the instructions yourself
6. Update this README with a link to the new doc

## Status

**Created:** November 22, 2025
**Maintained by:** Documentation Team
**Last Updated:** November 22, 2025

---

*This folder will be populated with comprehensive user guides for all features.*
