# Visualization Renderer Test Suite

## 📋 Overview
`test_visualizations.html` is a standalone HTML test harness that **exactly replicates** the AI chat panel UI for testing visualization renderers in isolation.

## 🎯 Purpose
- Test visualization renderers without running the full AI agent platform
- Verify CSS isolation and theming
- Debug memory leaks and cleanup issues
- Validate the BaseRenderer refactor
- Get real console logs from actual chart libraries

## 🚀 Usage

### Quick Start
1. Open `test_visualizations.html` in your browser
2. Click "Run All Tests" to test all renderers
3. Or click individual renderer buttons for targeted testing
4. Check console log panel for detailed output

### Features
- **Exact AI Chat Panel Replica**: Uses same CSS classes and structure as real AI messages
- **Dark/Light Theme Toggle**: Test theme detection with live switching
- **Individual Tests**: Test one renderer at a time
- **Console Logger**: Real-time feedback in the UI (no need for browser DevTools)
- **Memory Leak Testing**: Monitor Three.js animation loop cleanup

## 📂 File Location
```
C:\Users\gpoli\GIT\AI_agents\UI\visualisation_engine\test_visualizations.html
```

## 🔧 What It Tests

### 1. Chart.js Renderer
- Canvas sizing (width/height attributes)
- Theme application
- Bar chart rendering
- Config immutability

### 2. Plotly Renderer
- 3D scatter plot
- JavaScript eval fallback
- Theme detection
- Responsive sizing

### 3. ApexCharts Renderer
- Donut chart
- Theme mode switching
- Instance tracking

### 4. Three.js Renderer
- Animation loop cleanup
- Memory leak prevention
- requestAnimationFrame cancellation

### 5. GSAP Renderer
- Timeline animations
- Position parameter handling
- Infinite loop testing

## 🎨 UI Components

### Message Bubble Structure
```html
<div class="message-bubble ai-message">
    <div class="message-header">
        <i class="fas fa-robot"></i> Chart.js Test
    </div>
    <div class="message-content">
        <div class="viz-container">
            <div class="viz-content-area">
                <!-- Chart renders here -->
            </div>
        </div>
    </div>
</div>
```

### CSS Classes Used
- `.message-bubble` - Main message container
- `.ai-message` - AI-generated content styling
- `.user-message` - User message styling
- `.viz-container` - Visualization wrapper
- `.viz-content-area` - Chart render target

## 📊 Console Log Output

### Log Types
- **Info** (Blue): General information
- **Success** (Green): Test passed
- **Error** (Red): Test failed

### Example Output
```
========================================
Starting Test Suite
========================================
Testing Chart.js renderer...
✅ Chart.js rendered successfully
Testing Plotly renderer...
✅ Plotly rendered successfully
Testing ApexCharts renderer...
✅ ApexCharts rendered successfully
Testing GSAP renderer...
✅ GSAP animation started successfully
========================================
All tests complete!
========================================
```

## 🔍 How to Use for Development

### Testing Base Renderer Changes
1. Make changes to `base_renderer.js`
2. Reload `test_visualizations.html`
3. Click "Run All Tests"
4. Check console log for errors

### Testing Individual Renderers
1. Update a specific renderer (e.g., `apexcharts_renderer.js`)
2. Click the individual test button (e.g., "Test ApexCharts")
3. Inspect the rendered chart in the message bubble
4. Check console for warnings/errors

### Testing Memory Leaks
1. Run Three.js test
2. Open browser DevTools → Performance/Memory tab
3. Take heap snapshot
4. Remove the message bubble from DOM
5. Take another heap snapshot
6. Check if animation loop was properly canceled

### Testing Theme Changes
1. Render a chart
2. Click "Toggle Theme" button
3. Verify chart colors update correctly
4. Check if visualization respects theme

## 🐛 Debugging Tips

### Chart Not Rendering
1. Check console log panel for error messages
2. Open browser DevTools console for detailed stack traces
3. Verify CDN libraries loaded (check Network tab)
4. Ensure `base_renderer.js` loaded before specific renderers

### Theme Not Working
1. Check ThemeDetector mock in script
2. Verify CSS variables in `:root` and `[data-theme="dark"]`
3. Inspect element to see computed CSS values

### Animation Issues
1. For GSAP: Check if timeline created correctly
2. For Three.js: Monitor animation frame IDs
3. Check if cleanup methods called on removal

## 📝 Test Data Sources

All test data is hardcoded in the HTML file:
- **Chart.js**: Bar chart with 6 months of sales data
- **Plotly**: 3D scatter with 5 data points
- **ApexCharts**: Donut chart with 4 categories
- **GSAP**: Simple bouncing box animation

You can modify these in the test functions to try different scenarios.

## 🔗 Dependencies

### CSS Files
- `../modules_internal/agents/agent-ui.css` - Chat panel styling
- `./visualization_enhancements.css` - Viz container styles
- `../shared/styles/code-blocks.css` - Code block formatting

### JavaScript Libraries (CDN)
- Chart.js 4.4.1
- Plotly.js 2.27.1
- ApexCharts 3.45.1
- Mermaid 10.6.1
- GSAP 3.12.5
- Lottie Web 5.12.2
- DOMPurify 3.0.6

### Local Scripts
- `base_renderer.js` - Base renderer class
- `apexcharts_renderer.js` - ApexCharts renderer
- `threejs_renderer.js` - Three.js renderer
- `gsap_renderer.js` - GSAP renderer
- `cad_renderer.js` - CAD renderer
- `html_renderer.js` - HTML renderer

## 🎯 Success Criteria

A test passes when:
✅ Chart renders visibly in the message bubble  
✅ No console errors logged  
✅ Theme colors match current mode  
✅ No memory leaks (for Three.js/GSAP)  
✅ Cleanup methods work correctly  

## 🚨 Known Issues

1. **Three.js Test**: Requires manual memory profiling
2. **CSS Linting**: Some harmless CSS warnings (can be ignored)
3. **CDN Loading**: Tests require internet connection

## 🔄 Workflow

### Development Cycle
1. Make code changes to renderer
2. Save file
3. Reload `test_visualizations.html` in browser (Ctrl+R)
4. Click test button
5. Verify in console log
6. Repeat until working

### Integration Testing
After tests pass:
1. Test in actual AI agent platform
2. Verify with real AI-generated content
3. Check various delimiter formats
4. Test error handling with invalid configs

## 📦 Extending Tests

### Add New Renderer Test
```javascript
async function testNewRenderer() {
    log('Testing NewRenderer...', 'info');
    try {
        const contentArea = createAIMessage('New Test', 'Description');
        
        // Your rendering code here
        
        log('✅ NewRenderer rendered successfully', 'success');
    } catch (error) {
        log(`❌ NewRenderer error: ${error.message}`, 'error');
    }
}
```

Then add button:
```html
<button class="test-btn secondary" onclick="testNewRenderer()">
    Test New Renderer
</button>
```

## 🎓 Learning Resources

- **CSS Variables**: See `:root` section for all theme variables
- **Message Structure**: Inspect AI message bubble HTML
- **Console Logger**: Study `log()` function for custom logging
- **Theme Toggle**: Review `toggleTheme()` for theme switching

## ✨ Benefits

1. **Fast Iteration**: No need to restart Flask server
2. **Isolated Testing**: Test one renderer at a time
3. **Visual Feedback**: See exactly how charts look in chat
4. **Real Console**: Actual error messages from libraries
5. **Theme Testing**: Switch themes instantly
6. **Memory Profiling**: Easy to check for leaks

---

**Next Steps**: Once tests pass, integrate into main visualization engine and test with real AI-generated content.
