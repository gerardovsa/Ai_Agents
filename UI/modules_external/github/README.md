# GitHub Repository Management Module

## Overview
Personal GitHub integration module allowing each user to connect their own GitHub account and manage repositories, files, pull requests, and issues.

## Features
- ✅ Create repositories
- ✅ Commit files
- ✅ Create pull requests
- ✅ List issues
- ✅ Personal token integration (each user has own credentials)

## Files
```
github/
├── manifest.json       # Module metadata and configuration
├── github.html        # UI layout with modals
├── github.js          # Module logic and API integration
├── github.css         # GitHub-themed styling
└── README.md          # This file
```

## User Setup

### 1. Create GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `AI Agents Platform Access`
4. Select scopes:
   - ✅ `repo` - Full control of repositories
   - ✅ `workflow` - Update GitHub Actions
   - ✅ `write:org` - Manage organization repos (optional)
5. Generate and copy token (format: `ghp_...`)

### 2. Add Token to Platform
1. Open Account Settings → Connections
2. Find "GitHub" in platform list
3. Click "Add Connection"
4. Paste Personal Access Token
5. Optionally add username and email
6. Save

### 3. Start Using GitHub Tools
- Create repositories in your account
- Commit files with your identity
- Create pull requests
- List and manage issues

## Backend Integration

### Python Tools (tools/implementations/github.py)
```python
# User-specific credential injection
from AI_infrastructure.auth.credential_injector import get_github_credentials

def _get_github_client(user_id: int, **kwargs) -> Github:
    github_creds = get_github_credentials(user_id=user_id, **kwargs)
    return Github(github_creds['access_token'])
```

### Available Tools:
1. `github_create_repo` - Create repository
2. `github_commit_file` - Commit file to repo
3. `github_create_pr` - Create pull request
4. `github_get_issues` - List repository issues

## UI Components

### Action Cards
- **Create Repository** - Create new repo in user's account
- **Commit File** - Commit file to existing repo
- **Create Pull Request** - Create PR between branches
- **List Issues** - View repository issues

### Modals
- **Create Repository Modal** - Name, description, privacy
- **Commit File Modal** - Repo, file path, content, message
- **Create PR Modal** - Repo, title, branches, description
- **List Issues Modal** - Repo, state filter, limit

### Results Display
- Success state with formatted results
- Loading state with spinner
- Error state with clear messages
- Action buttons (Clear results)

## Styling
- GitHub-themed colors (#24292e)
- Clean, modern GitHub-style UI
- Responsive grid layout
- Accessible form controls
- Clear visual feedback

## Security
- ✅ Personal Access Token per user
- ✅ Stored in encrypted database
- ✅ Never exposed in UI after saving
- ✅ User isolation enforced
- ✅ Each user's actions attributed to them

## Module Registration

### Auto-discovery
Module is automatically discovered by the Flask backend module scanner:
```python
# Scans UI/external/modules/github/manifest.json
# Registers in module registry
# Available at /api/modules/list
```

### Frontend Integration
```javascript
window.ModuleRegistry['github'] = {
    instance: null,
    init: async () => {
        const module = new GitHubModule();
        await module.initialize();
        return module;
    }
};
```

## Testing

### Check Credentials
```javascript
window.ModuleRegistry['github'].instance.checkCredentials();
```

### Test Repository Creation
1. Open GitHub module
2. Click "Create Repo" card
3. Fill in form:
   - Name: `test-repo`
   - Description: `Testing AI Agents`
   - Private: Yes
4. Click "Create Repository"
5. Verify repo created at https://github.com/YOUR_USERNAME/test-repo

### Test File Commit
1. Click "Commit File" card
2. Fill in form:
   - Repo: `YOUR_USERNAME/test-repo`
   - File: `README.md`
   - Content: `# Test Repo`
   - Message: `Add README`
3. Click "Commit File"
4. Verify file appears in GitHub repo

## Troubleshooting

### "GitHub credentials not found"
**Solution:** Add Personal Access Token via Account Settings → Connections

### "Bad credentials" error
**Solution:** Token expired or invalid - generate new token and update

### "Resource not accessible"
**Solution:** Token needs broader scopes - regenerate with `repo`, `workflow` scopes

### Commits show wrong author
**Verification:** Commits ALWAYS show under the GitHub account that owns the token (this is correct!)

## API Endpoints Used

### Check Credentials
```
GET /api/connections
Authorization: Bearer <JWT>
```

### Execute GitHub Tool
```
POST /api/agent/execute-tool
{
    "tool_name": "github_create_repo",
    "parameters": {
        "name": "my-repo",
        "description": "Description",
        "private": true
    }
}
```

## Dependencies

### External Libraries
- None (uses native fetch API)

### Backend Dependencies
- `PyGithub` - GitHub API wrapper
- `get_github_credentials()` - Credential injector

## Future Enhancements
- [ ] Repository search
- [ ] Branch management
- [ ] Release creation
- [ ] Webhook configuration
- [ ] Organization management
- [ ] GitHub Actions integration

## Version History

### v1.0.0 (November 28, 2025)
- ✅ Initial release
- ✅ Personal token integration
- ✅ Create repositories
- ✅ Commit files
- ✅ Create pull requests
- ✅ List issues
- ✅ Full UI with modals
- ✅ GitHub-themed styling

---

**Author:** AI Agents Platform  
**License:** MIT  
**Support:** See GITHUB_PERSONAL_INTEGRATION_COMPLETE.md
