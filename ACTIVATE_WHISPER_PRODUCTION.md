# Activate Whisper for Render Production

**Date:** January 19, 2026  
**Status:** ✅ Ready to Deploy  
**Current:** Whisper working locally, disabled on Render  
**Goal:** Enable high-quality transcription in production

---

## ✅ Pre-Flight Check (Already Complete)

- ✅ **requirements.txt** has Whisper dependencies (lines 26-28):
  ```txt
  openai-whisper>=20231117
  torch>=2.0.0
  torchaudio>=2.0.0
  ```

- ✅ **Local testing confirmed:**
  - Whisper version: 20250625
  - Models downloaded: base.en.pt, base.pt, small.pt
  - Model loads successfully: ✅ Tested and working

- ✅ **Code ready:**
  - Lazy loading implemented (no startup delay)
  - Error handling in place
  - Fallback to browser STT if Whisper fails

---

## 🚀 Deployment Steps

### Step 1: Set Render Environment Variable

1. **Go to Render Dashboard:**
   - Navigate to: https://dashboard.render.com
   - Select your web service (AI Agents project)

2. **Add Environment Variable:**
   - Click "Environment" tab
   - Click "Add Environment Variable"
   - **Key:** `WHISPER_MODEL_SIZE`
   - **Value:** `base` (recommended - 145MB, 90% accuracy)
   - Click "Save Changes"

   **Model Options:**
   | Value | Size | Accuracy | Memory | Speed |
   |-------|------|----------|--------|-------|
   | `tiny` | 75 MB | 85% | Low | Fast |
   | `base` | 145 MB | 90% | Medium | ⭐ Recommended |
   | `small` | 483 MB | 93% | High | Slower |

### Step 2: Deploy to Render

```bash
# From AI_agents directory
git add -A
git commit -m "feat(transcription): enable Whisper for production

- Whisper dependencies already in requirements.txt
- Set WHISPER_MODEL_SIZE=base for Render
- Model downloads automatically on first use
- Lazy loading prevents startup delays"

git push origin v10
```

**Auto-deployment will start immediately** (v10 branch auto-deploys)

### Step 3: Monitor Deployment

1. **Check Render logs:**
   - Go to Render Dashboard → Logs
   - Look for these success messages:
   ```
   [TRANSCRIPTION] Whisper library not available at import: ...  ← Normal (lazy loading)
   [TRANSCRIPTION] Loading Whisper model lazily: base            ← On first request
   [TRANSCRIPTION] Whisper loaded successfully on cpu
   [TRANSCRIPTION] Model size: base
   ```

2. **Expected build time:**
   - ⏱️ First build: **25-30 minutes**
     - PyTorch install: ~10 minutes
     - Whisper install: ~5 minutes
     - Other dependencies: ~10 minutes
   - ⏱️ Subsequent builds: **15-20 minutes** (Docker layer caching)

3. **First transcription request:**
   - Model downloads automatically (~145 MB for `base`)
   - Downloads to `/opt/render/.cache/whisper/` on Render
   - Takes ~30-60 seconds on first request
   - Subsequent requests: 2-5 seconds

---

## 🧪 Testing After Deployment

### Test 1: Health Check
```bash
curl https://your-app.onrender.com/api/system/check
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "transcription",
  "available": true,
  "provider": "Local Whisper Model",
  "model": "base (local)",
  "supported_formats": ["wav", "mp3", "webm", "ogg", "m4a", "flac"]
}
```

### Test 2: Transcribe Audio File

Create a test audio file or use existing one:

```bash
# Upload audio for transcription
curl -X POST https://your-app.onrender.com/api/transcribe \
  -F "file=@test_audio.webm" \
  -F "language=en" \
  -F "session_id=production-test-001"
```

**Expected Response:**
```json
{
  "success": true,
  "transcript": "This is the transcribed text from the audio file",
  "text": "This is the transcribed text from the audio file",
  "language": "en",
  "confidence": 0.92,
  "duration": 12.5,
  "session_id": "production-test-001",
  "file_info": {
    "filename": "test_audio.webm",
    "size": 524288,
    "format": "webm"
  }
}
```

### Test 3: Frontend Transcription Sidebar

1. Open your production app
2. Navigate to Transcription Sidebar
3. Upload an audio file
4. Verify transcription appears
5. Check browser console for logs:
   ```
   [TRANSCRIPTION SIDEBAR] Sending audio to Whisper...
   [TRANSCRIPTION SIDEBAR] Whisper result: {...}
   ```

---

## 📊 Performance Expectations

### Production (Render Free Tier)
- **Model:** base (145 MB)
- **CPU:** Shared (no GPU)
- **First request:** 30-60 seconds (model download + load)
- **Subsequent requests:** 2-5 seconds per transcription
- **Accuracy:** ~90%
- **Memory:** ~500 MB (base model loaded)

### Production (Render Paid Tier - Optional)
- Consider upgrading if:
  - High transcription volume (100+ requests/day)
  - Need faster processing (< 2 seconds)
  - Want better model (`small` = 93% accuracy)

---

## 🔍 Troubleshooting

### Issue: "Whisper not available" in production

**Check:**
1. Render environment variable `WHISPER_MODEL_SIZE` is set
2. Build logs show PyTorch/Whisper installation
3. No build errors related to torch/torchaudio

**Fix:**
```bash
# Rebuild from scratch
render build --clear-cache
```

### Issue: First request times out

**Cause:** Model downloading (145 MB takes 30-60 seconds)

**Fix:** Pre-download model during Docker build:

Add to `Dockerfile`:
```dockerfile
# Pre-download Whisper model during build (optional)
RUN python -c "import whisper; whisper.load_model('base'); print('Whisper model pre-cached')"
```

Then redeploy.

### Issue: Out of memory errors

**Cause:** `small` or `medium` model too large for Render free tier

**Fix:** Switch to `base` or `tiny` model:
```bash
# In Render Dashboard → Environment
WHISPER_MODEL_SIZE=base  # or tiny
```

### Issue: Slow transcription (> 10 seconds)

**Check:**
- Model size (use `base` not `small` or `medium`)
- Audio file size (keep under 10 MB)
- Audio duration (keep under 2 minutes)

**Optimize:**
- Use shorter audio clips
- Consider AssemblyAI for long files (cloud-based, faster)

---

## 🎯 Success Criteria

After deployment, verify:

- [ ] Build completes successfully (no errors)
- [ ] Health check returns `"available": true`
- [ ] File upload transcription works
- [ ] Transcription sidebar works in production
- [ ] Browser console shows no Whisper errors
- [ ] Response time < 5 seconds for 30-second audio

---

## 📈 Monitoring

### Check Render Metrics:
- **Memory usage:** Should be ~500 MB with model loaded
- **Response times:** Should average 2-5 seconds
- **Error rate:** Should be < 1%

### Check Flask Logs:
```bash
# In Render Dashboard → Logs
# Search for:
[TRANSCRIPTION] Whisper loaded successfully
[TRANSCRIPTION] Success: 150 chars, language: en, confidence: 0.92
```

---

## 🔄 Rollback Plan

If issues occur:

1. **Remove environment variable:**
   - In Render Dashboard, delete `WHISPER_MODEL_SIZE`
   - System will fallback to Browser STT only

2. **Revert code changes:**
   ```bash
   git revert HEAD
   git push origin v10
   ```

3. **Check fallback behavior:**
   - Browser STT still works (no backend required)
   - File upload shows graceful error message
   - No app crashes

---

## 💰 Cost Impact

**Render Free Tier:**
- ✅ No additional cost (PyTorch/Whisper are free)
- ⚠️ Longer build times (25-30 min vs 15 min)
- ⚠️ Higher memory usage (~500 MB vs ~200 MB)

**Render Paid Tier ($7-25/month):**
- ✅ Dedicated CPU (faster transcription)
- ✅ More memory (can use `small` model = 93% accuracy)
- ✅ Faster builds with persistent storage

---

## 📝 Documentation Updates

After successful deployment:

- [x] Update TRANSCRIPTION.md with production status
- [ ] Update UI/modules_internal/transcription/README.md
- [ ] Add performance metrics to dashboard
- [ ] Document typical response times

---

## 🎉 Benefits of Activation

**Before (Browser STT only):**
- ⚠️ 70-85% accuracy
- ⚠️ No file upload transcription
- ⚠️ Browser-dependent quality

**After (Dual-mode):**
- ✅ 90% accuracy (Whisper base model)
- ✅ File upload works (audio/video transcription)
- ✅ Consistent quality across browsers
- ✅ Fallback to browser STT if Whisper fails
- ✅ Best of both worlds: real-time + accuracy

---

**Ready to deploy?** 

Just run:
```bash
# Set environment variable in Render Dashboard first, then:
git add -A
git commit -m "feat(transcription): enable Whisper for production"
git push origin v10
```

🚀 **Deployment will start automatically!**
