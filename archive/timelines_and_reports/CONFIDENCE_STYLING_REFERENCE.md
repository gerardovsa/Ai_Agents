# 🎨 Confidence-Based Styling Reference - Dual-Mode STT

## Overview

The dual-mode STT system includes **visual confidence indicators** that help users understand transcription quality at a glance.

---

## Confidence Levels

### High Confidence (80-100%)
- **Color:** Green (`#3fb950`)
- **Meaning:** Very accurate transcription
- **Sources:** 
  - Browser STT with confidence ≥ 0.8
  - Whisper (default high quality)
- **Visual:** Solid green text, no transparency

**Example:**
```
✅ "Hello, my name is John" (confidence: 95%)
```

---

### Medium Confidence (50-79%)
- **Color:** Orange (`#f0883e`)
- **Meaning:** Moderately accurate, may have errors
- **Sources:** 
  - Browser STT with confidence 0.5-0.79
- **Visual:** Orange text, full opacity

**Example:**
```
⚠️ "I think you sed something" (confidence: 62%)
```

---

### Low Confidence (<50%)
- **Color:** Red (`#f85149`)
- **Meaning:** Potentially inaccurate, verify manually
- **Sources:** 
  - Browser STT with confidence < 0.5
  - Unclear audio, background noise
- **Visual:** Red text, slightly transparent (85% opacity)

**Example:**
```
❌ "mmm... unclear... maybe yes?" (confidence: 35%)
```

---

### Unknown Confidence
- **Color:** White (`#e6edf3`)
- **Meaning:** No confidence data available
- **Sources:** 
  - Whisper (doesn't provide confidence scores)
  - Legacy transcripts
- **Visual:** Default text color

---

## Source Indicators

### Browser STT (Instant Streaming)
- **Indicator:** Blue dot (●) before text
- **Color:** `#58a6ff`
- **Meaning:** Transcribed in real-time by browser
- **Speed:** 0.1-0.5 seconds delay
- **Accuracy:** Good for clear speech, struggles with accents/noise

**Visual:**
```
● "This is browser STT text"
```

---

### Whisper (Backend Quality)
- **Indicator:** Purple dot (●) before text
- **Color:** `#a371f7`
- **Meaning:** Transcribed by Whisper backend
- **Speed:** 1-5 seconds delay
- **Accuracy:** Very high, handles accents/noise well

**Visual:**
```
● "This is Whisper transcribed text"
```

---

## Interim vs Final Text

### Interim Text (Streaming)
- **Style:** Italic, gray color, pulsing animation
- **Meaning:** Text being spoken right now (not yet finalized)
- **Source:** Browser STT only (Whisper doesn't support interim)
- **Visual:** Gray (#8b949e), 60-100% opacity pulse

**CSS:**
```css
.ai-transcript-interim {
    color: #8b949e;
    font-style: italic;
    opacity: 0.8;
    animation: pulse-interim 1.5s ease-in-out infinite;
}
```

**Example:**
```
💭 "I am currently speaking..." (interim)
```

---

### Final Text (Committed)
- **Style:** Regular weight, confidence color, solid
- **Meaning:** Transcription is complete and committed
- **Sources:** Both browser STT and Whisper
- **Visual:** Confidence-based color, 100% opacity

**CSS:**
```css
.ai-transcript-final {
    color: #e6edf3; /* or confidence color */
    font-weight: normal;
    opacity: 1.0;
}
```

**Example:**
```
✅ "I am currently speaking" (final, high confidence)
```

---

## Typing Cursor Effect

Interim text shows a blinking cursor to indicate active transcription:

**CSS:**
```css
.ai-transcript-interim::after {
    content: '▋';
    color: #58a6ff;
    animation: blink-cursor 1s step-end infinite;
    margin-left: 2px;
}
```

**Visual:**
```
"Hello world▋"  (cursor blinks)
```

---

## Hover Effects

### Hover on Final Text

**Behavior:**
1. Background highlights (light blue transparent)
2. Slight padding added
3. Tooltip appears showing:
   - Source (browser-stt or whisper)
   - Confidence level (high/medium/low)

**CSS:**
```css
.ai-transcript-final:hover {
    background: rgba(88, 166, 255, 0.1);
    border-radius: 3px;
    padding: 2px 4px;
}

.ai-transcript-final:hover::after {
    content: attr(data-source) ' - ' attr(data-confidence) ' confidence';
    /* ... tooltip styling ... */
}
```

**Visual:**
```
Hover over text:
┌─────────────────────────────┐
│ browser-stt - high confidence │
└─────────────────────────────┘
   "Hello world"
```

---

## HTML Data Attributes

Each transcript element includes data attributes for styling and debugging:

```html
<!-- Browser STT with high confidence -->
<span class="ai-transcript-final" 
      data-source="browser-stt" 
      data-confidence="high">
    Hello world
</span>

<!-- Whisper transcription (no confidence) -->
<span class="ai-transcript-final" 
      data-source="whisper" 
      data-confidence="unknown">
    This is from Whisper
</span>

<!-- Interim text (streaming) -->
<span class="ai-transcript-interim" 
      data-source="browser-stt">
    Currently speaking...▋
</span>
```

---

## Color Palette Reference

| Element | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| High Confidence | Green | `#3fb950` | 80-100% confidence |
| Medium Confidence | Orange | `#f0883e` | 50-79% confidence |
| Low Confidence | Red | `#f85149` | <50% confidence |
| Unknown Confidence | White | `#e6edf3` | No data |
| Interim Text | Gray | `#8b949e` | Streaming text |
| Browser STT Dot | Blue | `#58a6ff` | Source indicator |
| Whisper Dot | Purple | `#a371f7` | Source indicator |
| Typing Cursor | Blue | `#58a6ff` | Active input |

---

## Animation Timings

| Animation | Duration | Timing Function | Purpose |
|-----------|----------|-----------------|---------|
| Pulse (Interim) | 1.5s | ease-in-out | Breathing effect |
| Cursor Blink | 1s | step-end | Typing indicator |
| Hover Transition | 0.2s | ease | Smooth highlight |
| Tooltip Fade | 0.2s | ease | Smooth appearance |

---

## Accessibility Considerations

### Screen Readers

**Interim Text:**
```html
<span class="ai-transcript-interim" aria-live="polite" aria-atomic="true">
    Currently speaking...
</span>
```

**Final Text:**
```html
<span class="ai-transcript-final" aria-live="assertive" aria-atomic="false">
    Completed sentence.
</span>
```

### High Contrast Mode

Colors automatically adjust in high contrast mode:

```css
@media (prefers-contrast: high) {
    .ai-transcript-final[data-confidence="high"] {
        color: #00ff00; /* Brighter green */
    }
    
    .ai-transcript-final[data-confidence="medium"] {
        color: #ffaa00; /* Brighter orange */
    }
    
    .ai-transcript-final[data-confidence="low"] {
        color: #ff0000; /* Brighter red */
    }
}
```

### Reduced Motion

Disable animations for users with motion sensitivity:

```css
@media (prefers-reduced-motion: reduce) {
    .ai-transcript-interim {
        animation: none;
        opacity: 0.8; /* Static opacity */
    }
    
    .ai-transcript-interim::after {
        animation: none;
        opacity: 1; /* Static cursor */
    }
}
```

---

## Usage Examples

### Example 1: User Speaking Clearly (High Confidence)

**Scenario:** User says "Hello, my name is John" with clear audio

**Visual Output:**
```
💭 "Hello, my..."▋                    (interim, gray, italic)
💭 "Hello, my name is..."▋            (interim, gray, italic)
💭 "Hello, my name is John"▋          (interim, gray, italic)
✅ "Hello, my name is John"           (final, green, solid)
● "Hello, my name is John"            (Whisper backup, purple dot)
```

**Timeline:**
- 0.0s: User starts speaking
- 0.3s: Browser STT interim appears (gray)
- 1.2s: Browser STT final appears (green, 95% confidence)
- 3.5s: Whisper backup appears (purple dot, very high quality)

---

### Example 2: User Speaking with Background Noise (Mixed Confidence)

**Scenario:** User says "Can you hear me?" with background music

**Visual Output:**
```
💭 "Can you..."▋                      (interim, gray)
💭 "Can you hear me?"▋                (interim, gray)
⚠️ "Can you here me?"                 (final, orange, 65% confidence - wrong)
● "Can you hear me?"                  (Whisper backup, purple dot - correct)
```

**Timeline:**
- 0.0s: User starts speaking
- 0.4s: Browser STT interim appears
- 1.5s: Browser STT final appears (orange, medium confidence, wrong word)
- 4.2s: Whisper corrects to proper text (purple dot, correct)

---

### Example 3: User Speaking Unclearly (Low Confidence)

**Scenario:** User mumbles "I don't know" with poor audio

**Visual Output:**
```
💭 "mmm..."▋                          (interim, gray)
💭 "I don know"▋                      (interim, gray)
❌ "I don know"                       (final, red, 42% confidence)
● "I don't know"                      (Whisper backup, purple dot - correct)
```

**Timeline:**
- 0.0s: User starts speaking
- 0.5s: Browser STT struggles (gray interim)
- 2.0s: Browser STT gives up (red, low confidence)
- 5.0s: Whisper decodes correctly (purple dot)

---

## CSS Customization

### Change Confidence Colors

```css
/* Custom green for high confidence */
.ai-transcript-final[data-confidence="high"] {
    color: #00ff00; /* Brighter green */
    text-shadow: 0 0 5px rgba(0, 255, 0, 0.3); /* Glow effect */
}

/* Custom orange for medium */
.ai-transcript-final[data-confidence="medium"] {
    color: #ffaa00;
}

/* Custom red for low */
.ai-transcript-final[data-confidence="low"] {
    color: #ff0000;
    text-decoration: underline wavy; /* Wavy underline */
}
```

---

### Change Source Indicators

```css
/* Larger dots */
.ai-transcript-final[data-source="browser-stt"]::before,
.ai-transcript-final[data-source="whisper"]::before {
    width: 8px;
    height: 8px;
    margin-right: 8px;
}

/* Square indicators instead of dots */
.ai-transcript-final[data-source="browser-stt"]::before {
    border-radius: 2px; /* Square */
}
```

---

### Disable Animations

```css
/* No pulse on interim text */
.ai-transcript-interim {
    animation: none;
    opacity: 0.7;
}

/* No blinking cursor */
.ai-transcript-interim::after {
    display: none;
}
```

---

## Debugging

### Check Confidence Values

**Browser Console:**
```javascript
// Get all final transcripts
const finals = document.querySelectorAll('.ai-transcript-final');

// Log confidence distribution
finals.forEach(el => {
    console.log('Text:', el.textContent.trim());
    console.log('Source:', el.getAttribute('data-source'));
    console.log('Confidence:', el.getAttribute('data-confidence'));
    console.log('---');
});
```

---

### Test Confidence Colors

**HTML Test:**
```html
<div id="ai-transcription-text">
    <span class="ai-transcript-final" data-source="browser-stt" data-confidence="high">
        High confidence text
    </span>
    <span class="ai-transcript-final" data-source="browser-stt" data-confidence="medium">
        Medium confidence text
    </span>
    <span class="ai-transcript-final" data-source="browser-stt" data-confidence="low">
        Low confidence text
    </span>
    <span class="ai-transcript-final" data-source="whisper" data-confidence="unknown">
        Whisper text
    </span>
</div>
```

---

### Monitor Confidence Distribution

**JavaScript:**
```javascript
// Track confidence over time
let confidenceStats = { high: 0, medium: 0, low: 0, unknown: 0 };

// Hook into streamText
const originalStreamText = window.TranscriptionStreaming.streamText.bind(window.TranscriptionStreaming);
window.TranscriptionStreaming.streamText = function(text, isFinal, confidence, source) {
    if (isFinal) {
        confidenceStats[confidence]++;
        console.log('Confidence Stats:', confidenceStats);
    }
    return originalStreamText(text, isFinal, confidence, source);
};
```

---

## Performance Notes

### CSS Performance

- **Animations:** Use `transform` and `opacity` for GPU acceleration
- **Hover effects:** Use `will-change` for frequently hovered elements
- **Large transcripts:** Consider virtualizing long text displays

**Optimization Example:**
```css
.ai-transcript-interim {
    will-change: opacity; /* GPU hint */
}

.ai-transcript-final:hover {
    will-change: background, padding; /* GPU hint */
}
```

---

## Browser Support

| Feature | Chrome | Edge | Firefox | Safari |
|---------|--------|------|---------|--------|
| Confidence Colors | ✅ | ✅ | ✅ | ✅ |
| Source Indicators | ✅ | ✅ | ✅ | ✅ |
| Interim Text | ✅ | ✅ | ⚠️ (No Web Speech API) | ⚠️ (Experimental) |
| Hover Tooltips | ✅ | ✅ | ✅ | ✅ |
| Animations | ✅ | ✅ | ✅ | ✅ |

**Note:** Firefox and Safari have limited Web Speech API support, so interim text may not appear.

---

**Last Updated:** 2025-11-27  
**Version:** 1.0.0  
**CSS File:** `UI/modules/transcription/transcription-streaming-container.css`
