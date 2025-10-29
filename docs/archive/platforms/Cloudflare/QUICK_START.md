# Cloudflare AI Toolkit - Quick Reference

## ✅ Installation Complete!

Your Cloudflare AI toolkit is ready to use. All tests passed!

## 🚀 Quick Start

### Verify Connection
```powershell
cd c:\Users\gpoli\GIT\AI_agents\Cloudflare
node cli.js verify
```

### Chat with AI
```powershell
node cli.js chat "How do I fix CORS errors in Workers?"
```

### Diagnose Errors
```powershell
node cli.js diagnose 1101 "Worker threw exception"
```

## 📋 Common Commands

| Command | Description | Example |
|---------|-------------|---------|
| `verify` | Verify API token | `node cli.js verify` |
| `chat` | Ask AI a question | `node cli.js chat "question here"` |
| `diagnose` | Analyze Cloudflare error | `node cli.js diagnose 1101 "error message"` |
| `analyze` | Review code file | `node cli.js analyze ../background.js` |
| `logs` | View error history | `node cli.js logs 5` |
| `help` | Show all commands | `node cli.js help` |

## 🎯 Use Cases

### 1. Debug Chrome Extension Errors
```powershell
# When you see an error in your extension
node cli.js diagnose 1101 "Worker exception in background.js"
```

### 2. Code Review
```powershell
# Get AI feedback on any code file
node cli.js analyze "../../In_House_V2/sidebar.js"
```

### 3. Ask Technical Questions
```powershell
# Quick answers to technical questions
node cli.js chat "How do I optimize Workers performance?"
```

### 4. Review Past Errors
```powershell
# Check error diagnosis history
node cli.js logs 10
```

## 🔧 Configuration

- **API Token**: Automatically loaded from `../.env`
- **Account ID**: `d31a1c9ec65f373f4008216c30b071cc`
- **Default Model**: `@cf/meta/llama-3.1-8b-instruct`

## 📁 Project Structure

```
Cloudflare/
├── cloudflare-ai-client.js  # Core API client
├── cli.js                   # Command-line interface
├── test-client.js           # Automated tests
├── quick-test.js            # Quick API test
├── package.json             # Dependencies
├── logs/                    # Error diagnosis reports
└── README.md               # Full documentation
```

## 🧪 Testing

```powershell
# Run all tests
npm test

# Quick API test
node quick-test.js

# Test specific command
node cli.js verify
```

## 💡 Pro Tips

1. **Use Tab Completion**: Most PowerShell supports tab completion for file paths
2. **Save Diagnoses**: All error diagnoses are auto-saved to `logs/` folder
3. **Analyze Code**: Use `analyze` command before deploying new code
4. **Chat for Help**: The AI knows Cloudflare best practices

## 🔍 Common Error Codes

| Code | Meaning | Quick Fix |
|------|---------|-----------|
| 1101 | Worker exception | Check syntax, review stack trace |
| 1102 | Worker timeout | Optimize code, reduce execution time |
| 1015 | Rate limiting | Add delays between requests |
| 1000 | DNS error | Check domain configuration |

## 📚 Resources

- [Workers AI Models](https://developers.cloudflare.com/workers-ai/models/)
- [API Documentation](https://developers.cloudflare.com/api/)
- [Workers Docs](https://developers.cloudflare.com/workers/)

## 🆘 Troubleshooting

### Token Not Found
```powershell
# Make sure .env file exists
Get-Content ..\.env
```

### Authentication Error
```powershell
# Verify token is valid
node cli.js verify
```

### Module Not Found
```powershell
# Reinstall dependencies
npm install
```

---

**Created**: October 23, 2025  
**For**: GitHub Copilot AI Agent Management  
**Status**: ✅ Production Ready
