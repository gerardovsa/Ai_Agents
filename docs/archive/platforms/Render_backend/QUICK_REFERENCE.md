# 🎯 AI-Render Integration - Quick Reference Card

## ✅ Status (October 26, 2025)
- **Render Flask:** ✅ Active (https://inhouseprint-flask.onrender.com)
- **Render Streamlit:** ✅ Active (https://inhouseprint-streamlit.onrender.com)
- **DeepSeek AI:** ✅ Operational (10 keys)
- **Claude AI:** ✅ Operational
- **GPT AI:** ✅ Operational

---

## 🚀 Common Commands

### Test Everything
```bash
python Render_backend\ai_render_integration.py --test
```

### Process with AI
```bash
# DeepSeek (default)
python Render_backend\ai_render_integration.py --prompt "Your question here"

# Claude
python Render_backend\ai_render_integration.py --prompt "Your question" --provider claude

# GPT
python Render_backend\ai_render_integration.py --prompt "Your question" --provider openai
```

### Check Services
```bash
python Render_backend\ai_render_integration.py --check-services
```

---

## 📋 Python Quick Start

```python
from Render_backend.ai_render_integration import AIRenderClient

# Initialize
client = AIRenderClient()

# Process with AI
result = client.process_with_ai("Your prompt", provider="deepseek")
print(result['content'])

# Check services
status = client.check_render_services()
```

---

## 🔑 Key Credentials

### Render.com
- **API Key:** `rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu`
- **Flask ID:** `srv-d3oaosbe5dus73aj45pg`
- **Streamlit ID:** `srv-d3oal8bipnbc73fr5lf0`

### AI Providers
- **DeepSeek:** 10 keys configured (auto-rotation ready)
- **Anthropic:** 1 key configured
- **OpenAI:** 1 key configured

All keys stored in `.env.master` and `.env`

---

## 🎓 Example Outputs

### DeepSeek Response
```
Provider: deepseek
Model: deepseek-chat
Response: [Detailed analysis with 494 tokens]
Usage: 519 total tokens (~$0.0003)
```

### Claude Response
```
Provider: anthropic
Model: claude-sonnet-4-20250514
Response: [Concise, safety-focused answer]
Usage: 159 total tokens (~$0.0008)
```

---

## 📞 Quick Links

- **Render Dashboard:** https://dashboard.render.com/
- **Full Guide:** `AI_RENDER_INTEGRATION_GUIDE.md`
- **Test Scripts:** `Render_backend/test_*.py`

---

**Need Help?** Check `AI_RENDER_INTEGRATION_GUIDE.md` for detailed documentation.
