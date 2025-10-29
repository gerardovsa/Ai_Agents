# 🚀 Quick Reference - New Services

## AssemblyAI | CloudConvert | Ngrok

---

## 🎤 AssemblyAI - 1 Minute Start

```python
import assemblyai as aai
import os

aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
transcript = aai.Transcriber().transcribe("audio.mp3")
print(transcript.text)
```

**Dashboard**: https://www.assemblyai.com/dashboard

---

## 🔄 CloudConvert - 1 Minute Start

```python
import cloudconvert
import os

cloudconvert.configure(api_key=os.getenv('CLOUDCONVERT_API_KEY'))
job = cloudconvert.Job.create(payload={
    "tasks": {
        "import": {"operation": "import/url", "url": "file.docx"},
        "convert": {"operation": "convert", "input": "import", "output_format": "pdf"},
        "export": {"operation": "export/url", "input": "convert"}
    }
})
```

**Dashboard**: https://cloudconvert.com/dashboard

---

## 🌐 Ngrok - 1 Minute Start

```bash
# CLI
ngrok config add-authtoken 2ib2EN8rFZ9rpwn3JDosYMi1tJr_28oYLATi1G21JoYXSgZVk
ngrok http 3000 --region=au
```

```python
# Python
from pyngrok import ngrok
import os

ngrok.set_auth_token(os.getenv('NGROK_AUTHTOKEN'))
public_url = ngrok.connect(3000, region='au')
print(f"URL: {public_url}")
```

**Dashboard**: https://dashboard.ngrok.com/

---

## 📦 Install

```bash
pip install assemblyai cloudconvert-python pyngrok
```

---

## 📚 Full Documentation

- **NEW_SERVICES_GUIDE.md** - Complete guide with examples
- **ENV_UPDATE_SUMMARY.md** - Configuration summary
- **.env.master** - All credentials configured

---

## ✅ Status

| Service | API Key | Documentation |
|---------|---------|---------------|
| AssemblyAI | ✅ Active | [Docs](https://www.assemblyai.com/docs) |
| CloudConvert | ✅ Active (Never expires) | [Docs](https://cloudconvert.com/api/v2) |
| Ngrok | ✅ Active | [Docs](https://ngrok.com/docs) |

---

**Ready to use! 🎉**
