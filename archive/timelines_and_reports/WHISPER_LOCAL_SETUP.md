# Whisper Transcription - Local Model Setup

## Overview

The AI Agents platform now uses **local Whisper models** for voice transcription instead of the OpenAI API. This provides:

- ✅ **Zero API costs** - Completely free transcription
- ✅ **Privacy** - Audio never leaves your server
- ✅ **No rate limits** - Unlimited transcription
- ✅ **Offline capable** - Works without internet
- ✅ **Fast** - No network latency

---

## Installation

### Local Development (Windows)

```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
pip install openai-whisper torch torchaudio
```

### Render.com Deployment

Whisper is already included in `requirements.txt`:
```
openai-whisper>=20231117
torch>=2.0.0
torchaudio>=2.0.0
```

Render will automatically install these during deployment.

---

## Model Selection

Whisper has 5 model sizes. Choose based on your server's RAM:

| Model | Size | RAM | Speed | Accuracy | Render Tier |
|-------|------|-----|-------|----------|-------------|
| `tiny` | 75MB | 1GB | Very Fast | Good | Free ($0/mo) |
| `base` | 150MB | 1GB | Fast | Better | Free ($0/mo) |
| `small` | 500MB | 2GB | Medium | Great | Starter ($7/mo) |
| `medium` | 1.5GB | 5GB | Slow | Excellent | Standard ($25/mo) |
| `large` | 3GB | 10GB+ | Very Slow | Best | Not practical |

**Recommended:**
- **Render Free Tier**: Use `base` model (good quality, 150MB)
- **Render Starter**: Use `small` model (great quality, 500MB)
- **Local Development**: Use `medium` or `large` if you have GPU

---

## Configuration

### Environment Variable

Set the Whisper model size via environment variable:

```bash
# In Render.com Environment Variables
WHISPER_MODEL_SIZE=base

# Or in .env.master file (local)
WHISPER_MODEL_SIZE=base
```

**Default:** `base` (if not specified)

### Model Download

On first startup, Whisper will automatically download the model to:
- **Local**: `~/.cache/whisper/`
- **Render**: `/opt/render/.cache/whisper/`

This happens once and takes 10-30 seconds depending on model size.

---

## Usage

### From Browser

1. Click the microphone button in chat input
2. Speak your message
3. Click stop recording
4. Audio is automatically transcribed via local Whisper
5. Transcript appears in chat input

### From Transcription Sidebar

1. Click "Voice Transcription" button (top-right)
2. Go to "Recording" tab
3. Click "Start Recording"
4. Speak your message
5. Click "Stop Recording"
6. Transcript saved to "Transcripts" tab

### API Endpoint

```javascript
// Send audio file for transcription
const formData = new FormData();
formData.append('file', audioBlob, 'recording.webm');
formData.append('session_id', 'unique-session-id');

const response = await fetch('http://localhost:5001/api/transcribe', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.transcript);
```

---

## System Check

Check if Whisper is loaded:

```javascript
// In browser console
fetch('http://localhost:5001/api/system/check')
    .then(r => r.json())
    .then(console.log);

// Expected response:
{
    "status": "ok",
    "service": "transcription",
    "available": true,
    "provider": "Local Whisper Model",
    "model": "base (local)",
    "supported_formats": ["wav", "mp3", "webm", "ogg", "m4a", "flac"]
}
```

---

## Performance

### Transcription Speed

| Model | CPU (1 min audio) | GPU (1 min audio) |
|-------|-------------------|-------------------|
| `tiny` | ~5 seconds | ~1 second |
| `base` | ~10 seconds | ~2 seconds |
| `small` | ~30 seconds | ~5 seconds |
| `medium` | ~60 seconds | ~10 seconds |
| `large` | ~120 seconds | ~15 seconds |

**Note:** Render.com uses CPUs (no GPU), so transcription will take longer. The `base` model is a good balance of speed and accuracy.

### Memory Usage

Whisper keeps the model loaded in RAM for fast transcription:
- **Startup**: Model loads once (10-30 seconds)
- **Runtime**: Model stays in memory
- **Transcription**: Minimal additional memory

**Render Free Tier** (512MB RAM):
- ✅ Can run `tiny` model (75MB)
- ⚠️ `base` model (150MB) might work but could cause OOM errors under load

**Render Starter** ($7/mo, 2GB RAM):
- ✅ Can run `base` model (150MB) comfortably
- ✅ Can run `small` model (500MB) with room to spare

---

## Troubleshooting

### Issue: "Whisper not available"

**Cause:** Whisper library not installed

**Solution:**
```powershell
pip install openai-whisper torch torchaudio
```

Then restart Flask:
```powershell
BISTOP; Start-Sleep -Seconds 3; BISTART
```

### Issue: "Out of Memory" on Render

**Cause:** Model too large for free tier

**Solutions:**
1. Use smaller model: `WHISPER_MODEL_SIZE=tiny`
2. Upgrade to Render Starter ($7/mo) for 2GB RAM
3. Use OpenAI API instead (see alternative below)

### Issue: Slow transcription

**Cause:** CPU transcription is slower than GPU

**Solutions:**
1. Use smaller model (`tiny` or `base`)
2. Accept slower speed (CPU transcription is normal)
3. For local dev: Use GPU if available (CUDA)

### Issue: Model download fails

**Cause:** Network issues or disk space

**Check:**
```bash
# Disk space on Render
df -h

# Manual download
python -c "import whisper; whisper.load_model('base')"
```

---

## Alternative: OpenAI Whisper API

If local Whisper doesn't work on Render free tier, you can switch to OpenAI API:

**Cost:** $0.006 per minute of audio (~$0.10 per hour)

**Setup:**
1. Get OpenAI API key from https://platform.openai.com
2. Add to environment: `OPENAI_API_KEY=sk-...`
3. Update `transcription_routes.py` to use OpenAI API (previous version)

---

## Deployment Checklist

### Render.com

1. ✅ Add environment variable: `WHISPER_MODEL_SIZE=base`
2. ✅ Ensure `requirements.txt` includes `openai-whisper`
3. ✅ Upgrade to Starter plan if using `small` model ($7/mo)
4. ✅ Wait for model download on first deployment (30 seconds)
5. ✅ Test endpoint: `/api/system/check`

### Local Development

1. ✅ Install Whisper: `pip install openai-whisper torch torchaudio`
2. ✅ Set model size in `.env.master`: `WHISPER_MODEL_SIZE=medium` (or `large` if GPU)
3. ✅ Restart Flask: `BISTART`
4. ✅ Test transcription via browser

---

## Files Modified

- `AI_infrastructure/routes/transcription_routes.py` - Local Whisper integration
- `requirements.txt` - Added openai-whisper, torch, torchaudio
- `UI/modules/transcription/config.js` - Uses window.API_BASE_URL
- `UI/modules/transcription/transcription-sidebar.js` - Fixed audioChunks reference

---

**Last Updated:** November 26, 2025  
**Version:** 1.0.0 (Local Whisper)  
**Status:** ✅ Production Ready
