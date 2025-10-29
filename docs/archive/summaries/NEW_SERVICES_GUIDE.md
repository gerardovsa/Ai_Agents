# New Services Integration Guide
## AssemblyAI, CloudConvert, and Ngrok

**Created**: October 23, 2025  
**Services Added**: AssemblyAI, CloudConvert, Ngrok  
**Status**: ✅ Configured in `.env.master`

---

## 🎤 **AssemblyAI - Speech-to-Text & Audio Intelligence**

### **Overview**
AssemblyAI provides advanced speech recognition and audio intelligence APIs with features beyond basic transcription.

### **Configuration**
```bash
ASSEMBLYAI_API_KEY=763707ce46c647149998f6f16acd8ea6
ASSEMBLYAI_BASE_URL=https://api.assemblyai.com/v2
```

### **Features Available**
- ✅ **Speech-to-text transcription** - Convert audio/video to text
- ✅ **Speaker diarization** - Identify who spoke when
- ✅ **Sentiment analysis** - Detect positive/negative/neutral sentiment
- ✅ **Topic detection** - Automatically identify topics discussed
- ✅ **Content moderation** - Flag sensitive content
- ✅ **Entity detection** - Extract names, places, organizations
- ✅ **Auto chapters** - Generate chapter markers
- ✅ **Summarization** - Create summaries of conversations

### **Quick Start (Python)**

```python
import os
import assemblyai as aai

# Configure API key
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

# Basic transcription
transcriber = aai.Transcriber()
transcript = transcriber.transcribe("https://example.com/audio.mp3")

# Or from local file
transcript = transcriber.transcribe("./path/to/audio.mp3")

# Get the text
print(transcript.text)

# With advanced features
config = aai.TranscriptionConfig(
    speaker_labels=True,  # Enable speaker diarization
    sentiment_analysis=True,  # Enable sentiment analysis
    entity_detection=True,  # Detect entities
    auto_chapters=True  # Generate chapters
)

transcript = transcriber.transcribe("./audio.mp3", config=config)

# Access advanced features
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")

for sentiment in transcript.sentiment_analysis:
    print(f"{sentiment.text} - {sentiment.sentiment}")
```

### **Use Cases**
- 📹 **Video content analysis** - Transcribe YouTube videos, webinars
- 📞 **Call center analytics** - Analyze customer service calls
- 🎙️ **Podcast transcription** - Create show notes automatically
- 📚 **Meeting notes** - Transcribe Zoom/Teams meetings
- 🎬 **Media production** - Generate subtitles and captions

### **Links**
- Dashboard: https://www.assemblyai.com/dashboard
- Documentation: https://www.assemblyai.com/docs
- Python SDK: https://github.com/AssemblyAI/assemblyai-python-sdk

---

## 🔄 **CloudConvert - Universal File Conversion API**

### **Overview**
CloudConvert supports 200+ file formats for document, image, video, audio, and archive conversion.

### **Configuration**
```bash
CLOUDCONVERT_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
CLOUDCONVERT_BASE_URL=https://api.cloudconvert.com/v2
CLOUDCONVERT_WEBHOOK_SIGNING_SECRET=your-webhook-secret
```

**Token Details**:
- Created: September 3, 2024
- Expires: Never (long-term token)
- Account ID: 65052210

**Scopes Granted**:
- ✅ user.read, user.write
- ✅ task.read, task.write
- ✅ webhook.read, webhook.write
- ✅ preset.read, preset.write

### **Supported Formats** (200+ total)

**Documents**:
- PDF, DOCX, XLSX, PPTX, ODT, HTML, Markdown, TXT, RTF

**Images**:
- JPG, PNG, GIF, SVG, WEBP, TIFF, BMP, ICO, HEIC, HEIF

**Videos**:
- MP4, AVI, MOV, MKV, WEBM, FLV, WMV, M4V, 3GP

**Audio**:
- MP3, WAV, FLAC, AAC, OGG, M4A, WMA, OPUS

**Archives**:
- ZIP, RAR, 7Z, TAR, GZ, BZ2

**E-books**:
- EPUB, MOBI, AZW3, PDF

**Vector Graphics**:
- SVG, EPS, AI, PDF

### **Quick Start (Python)**

```python
import os
import cloudconvert

# Configure API
cloudconvert.configure(api_key=os.getenv('CLOUDCONVERT_API_KEY'))

# Simple conversion
job = cloudconvert.Job.create(payload={
    "tasks": {
        "import-my-file": {
            "operation": "import/url",
            "url": "https://example.com/document.docx"
        },
        "convert-my-file": {
            "operation": "convert",
            "input": "import-my-file",
            "output_format": "pdf"
        },
        "export-my-file": {
            "operation": "export/url",
            "input": "convert-my-file"
        }
    }
})

# Wait for job completion
job = cloudconvert.Job.wait(id=job['id'])

# Get download URL
export_task = [t for t in job['tasks'] if t['name'] == 'export-my-file'][0]
download_url = export_task['result']['files'][0]['url']
print(f"Download: {download_url}")
```

### **Advanced Examples**

**Image Optimization**:
```python
job = cloudconvert.Job.create(payload={
    "tasks": {
        "import": {"operation": "import/url", "url": "https://example.com/large-image.png"},
        "convert": {
            "operation": "convert",
            "input": "import",
            "output_format": "webp",
            "options": {
                "quality": 85,
                "resize": {"width": 1920, "height": 1080, "fit": "inside"}
            }
        },
        "export": {"operation": "export/url", "input": "convert"}
    }
})
```

**Video Compression**:
```python
job = cloudconvert.Job.create(payload={
    "tasks": {
        "import": {"operation": "import/url", "url": "https://example.com/video.mov"},
        "convert": {
            "operation": "convert",
            "input": "import",
            "output_format": "mp4",
            "options": {
                "video_codec": "h264",
                "video_bitrate": "1000k",
                "audio_codec": "aac",
                "audio_bitrate": "128k"
            }
        },
        "export": {"operation": "export/url", "input": "convert"}
    }
})
```

**PDF Operations**:
```python
# Merge PDFs
job = cloudconvert.Job.create(payload={
    "tasks": {
        "import-1": {"operation": "import/url", "url": "https://example.com/file1.pdf"},
        "import-2": {"operation": "import/url", "url": "https://example.com/file2.pdf"},
        "merge": {
            "operation": "merge",
            "input": ["import-1", "import-2"]
        },
        "export": {"operation": "export/url", "input": "merge"}
    }
})
```

### **Use Cases**
- 📄 **Document workflow** - Convert DOCX to PDF for distribution
- 🖼️ **Image optimization** - Bulk convert/resize images for web
- 🎬 **Video processing** - Convert and compress video files
- 📊 **Data processing** - Convert between CSV, JSON, XML
- 📱 **App integration** - Handle user file uploads in any format

### **Links**
- Dashboard: https://cloudconvert.com/dashboard
- Documentation: https://cloudconvert.com/api/v2
- Python SDK: https://github.com/cloudconvert/cloudconvert-python

---

## 🌐 **Ngrok - Secure Tunneling & Webhook Testing**

### **Overview**
Ngrok creates secure tunnels from public URLs to your localhost, perfect for testing webhooks and sharing local development.

### **Configuration**
```bash
NGROK_AUTHTOKEN=2ib2EN8rFZ9rpwn3JDosYMi1tJr_28oYLATi1G21JoYXSgZVk
NGROK_REGION=au
NGROK_API_KEY=your-api-key-here
```

**Account**: gerardovsa  
**Region**: Australia (au)

### **Features**
- ✅ **Secure HTTPS tunnels** - Expose localhost with SSL
- ✅ **Custom domains** - Use your own domain (paid plans)
- ✅ **Webhook testing** - Test Stripe, GitHub, Twilio webhooks locally
- ✅ **Request inspection** - View all HTTP requests/responses
- ✅ **Replay requests** - Resend requests for debugging
- ✅ **TLS termination** - Handle SSL at the edge
- ✅ **Basic authentication** - Protect tunnels with username/password
- ✅ **IP whitelisting** - Restrict access by IP address

### **Quick Start (CLI)**

**Install Ngrok**:
```bash
# Windows (via Chocolatey)
choco install ngrok

# Or download from: https://ngrok.com/download
```

**Configure Auth Token**:
```bash
ngrok config add-authtoken 2ib2EN8rFZ9rpwn3JDosYMi1tJr_28oYLATi1G21JoYXSgZVk
```

**Start Tunnel**:
```bash
# Tunnel to port 3000
ngrok http 3000

# Tunnel with custom region
ngrok http 3000 --region=au

# Tunnel with custom subdomain (paid plan)
ngrok http 3000 --subdomain=myapp

# Tunnel with basic auth
ngrok http 3000 --basic-auth="username:password"
```

### **Quick Start (Python)**

```python
import os
from pyngrok import ngrok

# Set auth token
ngrok.set_auth_token(os.getenv('NGROK_AUTHTOKEN'))

# Start tunnel
public_url = ngrok.connect(3000, region='au')
print(f"🌐 Public URL: {public_url}")

# With custom options
public_url = ngrok.connect(
    3000,
    region='au',
    bind_tls=True,  # Only HTTPS
    auth="username:password"  # Basic auth
)

# Keep tunnel open
try:
    input("Press Enter to close tunnel...")
finally:
    ngrok.disconnect(public_url)
```

### **Advanced Usage**

**Configuration File** (`~/.ngrok2/ngrok.yml`):
```yaml
authtoken: 2ib2EN8rFZ9rpwn3JDosYMi1tJr_28oYLATi1G21JoYXSgZVk
region: au

tunnels:
  myapp:
    proto: http
    addr: 3000
    auth: "username:password"
    inspect: true
  
  api:
    proto: http
    addr: 8080
    bind_tls: true
```

**Start multiple tunnels**:
```bash
ngrok start myapp api
```

### **Common Use Cases**

#### **1. Test Stripe Webhooks**
```python
from pyngrok import ngrok
import os

# Start tunnel
public_url = ngrok.connect(5000, region='au')
print(f"Set Stripe webhook to: {public_url}/webhooks/stripe")

# Your Flask app
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.json
    print(f"Received webhook: {payload}")
    return {'success': True}

app.run(port=5000)
```

#### **2. Share Local Development**
```bash
# Start your dev server
npm start  # Running on localhost:3000

# In another terminal
ngrok http 3000 --region=au

# Share the ngrok URL with clients
# Example: https://abc123.ngrok-free.app
```

#### **3. Test Mobile App Backend**
```python
# Your local API
from fastapi import FastAPI
from pyngrok import ngrok
import os

app = FastAPI()

@app.get("/api/data")
def get_data():
    return {"message": "Hello from localhost!"}

# Start ngrok tunnel
public_url = ngrok.connect(8000, region='au')
print(f"📱 Use this URL in your mobile app: {public_url}")

# Run FastAPI
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **4. Test OAuth Redirect URLs**
```bash
# Your OAuth app needs a redirect URL
# Start tunnel
ngrok http 3000 --region=au

# Use ngrok URL in OAuth config
# Example: https://abc123.ngrok-free.app/auth/callback

# Your redirect endpoint
@app.route('/auth/callback')
def oauth_callback():
    code = request.args.get('code')
    # Exchange code for token
    return "Auth successful!"
```

### **Debugging & Inspection**

**Web Interface**: http://localhost:4040
- View all requests/responses
- Replay requests
- Inspect headers and body
- See timing information

**API Access**:
```python
import requests

# Get tunnel info
response = requests.get('http://localhost:4040/api/tunnels')
tunnels = response.json()['tunnels']

for tunnel in tunnels:
    print(f"Tunnel: {tunnel['public_url']} -> {tunnel['config']['addr']}")
```

### **Links**
- Dashboard: https://dashboard.ngrok.com/
- Documentation: https://ngrok.com/docs
- Python SDK: https://github.com/inconshreveable/ngrok

---

## 🔗 **Integration with Existing Services**

### **Combine AssemblyAI + CloudConvert**
```python
import assemblyai as aai
import cloudconvert
import os

# Step 1: Convert video to audio
cloudconvert.configure(api_key=os.getenv('CLOUDCONVERT_API_KEY'))

video_to_audio = cloudconvert.Job.create(payload={
    "tasks": {
        "import": {"operation": "import/url", "url": "https://example.com/video.mp4"},
        "convert": {"operation": "convert", "input": "import", "output_format": "mp3"},
        "export": {"operation": "export/url", "input": "convert"}
    }
})

audio_url = video_to_audio['tasks'][-1]['result']['files'][0]['url']

# Step 2: Transcribe audio
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
transcriber = aai.Transcriber()
transcript = transcriber.transcribe(audio_url)

print(f"Transcript: {transcript.text}")
```

### **Combine Ngrok + Webhook Testing**
```python
from pyngrok import ngrok
from flask import Flask, request
import os

# Start ngrok tunnel
ngrok.set_auth_token(os.getenv('NGROK_AUTHTOKEN'))
public_url = ngrok.connect(5000, region='au')

print(f"""
🌐 Webhook endpoints available:
- AssemblyAI: {public_url}/webhooks/assemblyai
- CloudConvert: {public_url}/webhooks/cloudconvert
- GitHub: {public_url}/webhooks/github
""")

app = Flask(__name__)

@app.route('/webhooks/assemblyai', methods=['POST'])
def assemblyai_webhook():
    data = request.json
    print(f"AssemblyAI: Transcription {data['transcript_id']} complete")
    return {'received': True}

@app.route('/webhooks/cloudconvert', methods=['POST'])
def cloudconvert_webhook():
    data = request.json
    print(f"CloudConvert: Job {data['job']['id']} complete")
    return {'received': True}

app.run(port=5000)
```

---

## 📊 **Summary of New Services**

| Service | Purpose | API Key Status | Use Cases |
|---------|---------|----------------|-----------|
| **AssemblyAI** | Speech-to-text & audio intelligence | ✅ Active | Transcription, sentiment analysis, speaker diarization |
| **CloudConvert** | Universal file conversion | ✅ Active (Never expires) | PDF conversion, image optimization, video processing |
| **Ngrok** | Secure tunneling & webhooks | ✅ Active | Webhook testing, local dev sharing, OAuth testing |

---

## ✅ **Next Steps**

1. **Install Python SDKs**:
   ```bash
   pip install assemblyai cloudconvert-python pyngrok
   ```

2. **Test Each Service**:
   - Run AssemblyAI transcription test
   - Run CloudConvert file conversion test
   - Start ngrok tunnel and test webhook

3. **Create Integration Modules** (Optional):
   - `AI_agents/AssemblyAI/` - Full AssemblyAI integration
   - `AI_agents/CloudConvert/` - Full CloudConvert integration
   - `AI_agents/Ngrok/` - Ngrok utilities and helpers

4. **Update `config.py`** (if needed):
   Add these services to the shared configuration for easy access across all integrations.

---

**All services are now configured and ready to use! 🎉**
