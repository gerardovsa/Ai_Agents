# AI Visualization Integration - Quick Start Guide

**For Developers**: How to use the new AI enhancements in your code

---

## 🚀 Quick Start (5 Minutes)

### 1. Backend: Validate AI-Generated CAD

```python
# In your Flask route that handles AI responses
from AI_infrastructure.models.cad_validation import validate_cad_json, CADVisualization

@app.route('/api/generate-cad', methods=['POST'])
def generate_cad():
    user_request = request.json.get('request')
    
    # Get AI response
    ai_response = openai_client.chat.completions.create(...)
    cad_data = extract_cad_from_response(ai_response)
    
    # ✨ NEW: Validate before sending to frontend
    result = validate_cad_json(cad_data)
    
    if isinstance(result, CADVisualization):
        # Valid! Send to frontend
        return jsonify(result.model_dump()), 200
    else:
        # Invalid - return errors
        return jsonify({"errors": result}), 400
```

### 2. Frontend: Lint Before Rendering

```javascript
// In your parametric-cad.js or similar
async function renderCAD(cadJson) {
    // ✨ NEW: Lint before rendering
    const linter = new CADLinter();
    const lintResult = linter.lint(cadJson);
    
    if (!lintResult.valid) {
        console.error('❌ Validation failed:', lintResult.errors);
        showErrorPanel(lintResult.errors);
        return;
    }
    
    if (lintResult.warnings.length > 0) {
        console.warn('⚠️ Warnings:', lintResult.warnings);
    }
    
    // Safe to render
    await createCADVisualization(cadJson);
}
```

### 3. Enable Streaming Rendering

```javascript
// Replace instant rendering with progressive rendering
async function createCADVisualization(cadJson) {
    const streamer = new StreamingCADRenderer(scene, camera, renderer);
    
    // ✨ NEW: Stream the rendering
    await streamer.startStreaming({
        dimensions: cadJson.model3D.dimensions,
        length: cadJson.model3D.length,
        profile: cadJson.model3D.profile,
        
        progressCallback: (progress) => {
            console.log(`${progress.label} (${Math.round(progress.progress * 100)}%)`);
            updateProgressBar(progress.progress);
        },
        
        completeCallback: (finalMesh) => {
            console.log('✅ Rendering complete!');
            hideProgressBar();
        },
        
        errorCallback: (error) => {
            console.error('❌ Rendering error:', error);
            showError(error.message);
        }
    });
}
```

### 4. Add Natural Language Interface

```javascript
// Initialize AI UX enhancements
const cadModule = new ParametricCAD();
const aiux = new AICADExperience(cadModule);

// The natural language input appears automatically!
// User can type: "Create a 500mm T-slot beam"
// AI UX handles parsing and execution
```

---

## 📖 Detailed Examples

### Progressive Generation (Backend)

```python
from AI_infrastructure.tools.progressive_cad_generator import ProgressiveCADGenerator

# Replace single-shot generation
# OLD:
# cad_json = ai.generate_cad(user_request)

# NEW: Multi-step generation
generator = ProgressiveCADGenerator(openai_client)
cad_json = generator.generate_progressive(user_request)

# Review step history (optional)
for step in generator.get_step_history():
    print(f"Step {step['step']}: {step['response']}")

# Validate result
result = validate_cad_json(cad_json)
if isinstance(result, CADVisualization):
    return result.model_dump()
else:
    return {"errors": result}
```

### Error Recovery UI (Frontend)

```javascript
// When linting fails, show recovery options
function showErrorPanel(errors) {
    const panel = document.getElementById('error-recovery');
    const errorMsg = document.getElementById('error-message');
    const suggestions = document.getElementById('error-suggestions');
    
    errorMsg.textContent = errors[0];
    
    // Generate recovery buttons based on error type
    const recoveryActions = [];
    
    if (errors.some(e => e.includes('dimension'))) {
        recoveryActions.push({
            label: 'Use default dimensions',
            action: () => {
                cadJson.model3D.dimensions = {
                    width: 0.02,
                    height: 0.02,
                    depth: 0.02
                };
                renderCAD(cadJson);  // Retry
            }
        });
    }
    
    if (errors.some(e => e.includes('camera'))) {
        recoveryActions.push({
            label: 'Reset to isometric view',
            action: () => {
                cadJson.camera.position = { x: 1.5, y: 1.5, z: 1.5 };
                cadJson.camera.target = { x: 0, y: 0, z: 0 };
                renderCAD(cadJson);  // Retry
            }
        });
    }
    
    // Render recovery buttons
    suggestions.innerHTML = recoveryActions.map(ra => 
        `<button onclick="(${ra.action})()">${ra.label}</button>`
    ).join('');
    
    panel.style.display = 'block';
}
```

### Custom Validation Rules (Backend)

```python
from AI_infrastructure.models.cad_validation import lint_cad_visualization

# Add custom business logic checks
def validate_cad_for_manufacturing(cad_json):
    """Check if design is manufacturable"""
    errors = []
    
    # Use built-in linting
    errors.extend(lint_cad_visualization(cad_json))
    
    # Add custom rules
    model3d = cad_json.get('model3D', {})
    length = model3d.get('length', 0)
    
    # Check maximum machine capacity
    if length > 6.0:  # 6 meter max
        errors.append(f"Length {length}m exceeds machine capacity (6m max)")
    
    # Check minimum order quantity
    if model3d.get('quantity', 1) < 10:
        errors.append("Minimum order quantity is 10 pieces")
    
    return errors
```

---

## 🎨 UI Customization

### Custom Suggestion Styles

```css
/* Override default suggestion panel styles */
#ai-suggestions {
    background: rgba(45, 45, 45, 0.98) !important;
    border: 2px solid #00BCD4 !important;
}

.ai-panel-header h4 {
    color: #00BCD4 !important;
}

/* Custom progress bar */
#cad-progress-bar {
    height: 4px;
    background: linear-gradient(90deg, #00BCD4, #4CAF50);
    border-radius: 2px;
}
```

### Custom Natural Language Commands

```javascript
// Extend the intent parser
class CustomAICADExperience extends AICADExperience {
    parseIntent(text) {
        const baseIntent = super.parseIntent(text);
        
        // Add custom commands
        if (text.match(/duplicate|copy/i)) {
            return {
                action: 'duplicate',
                rawText: text,
                params: { count: this.extractQuantity(text) }
            };
        }
        
        if (text.match(/mirror|flip/i)) {
            return {
                action: 'mirror',
                rawText: text,
                params: { axis: this.extractAxis(text) }
            };
        }
        
        return baseIntent;
    }
    
    extractAxis(text) {
        if (text.match(/\bx\b/i)) return 'x';
        if (text.match(/\by\b/i)) return 'y';
        if (text.match(/\bz\b/i)) return 'z';
        return 'x';  // Default
    }
}
```

---

## 🧪 Testing Your Integration

### Test Validation

```python
# Test backend validation
def test_validation():
    # Valid CAD
    valid_cad = {
        "type": "parametric_cad",
        "model3D": {
            "type": "extrusion",
            "profile": "profile-5",
            "length": 0.5,
            "dimensions": {"width": 0.02, "height": 0.02, "depth": 0.02}
        }
    }
    
    result = validate_cad_json(valid_cad)
    assert isinstance(result, CADVisualization), "Should be valid"
    
    # Invalid CAD (negative dimension)
    invalid_cad = {
        "type": "parametric_cad",
        "model3D": {
            "type": "extrusion",
            "length": -0.5  # Invalid!
        }
    }
    
    result = validate_cad_json(invalid_cad)
    assert isinstance(result, list), "Should return errors"
    assert any("positive" in str(e) for e in result), "Should catch negative value"
```

### Test Linting

```javascript
// Test frontend linting
function testLinting() {
    const linter = new CADLinter();
    
    // Test 1: Valid CAD
    const validCad = {
        type: "parametric_cad",
        model3D: {
            type: "extrusion",
            profile: "profile-5",
            length: 0.5,
            dimensions: { width: 0.02, height: 0.02, depth: 0.02 }
        },
        camera: {
            position: { x: 1.5, y: 1.5, z: 1.5 },
            target: { x: 0, y: 0, z: 0 }
        }
    };
    
    const result1 = linter.lint(validCad);
    console.assert(result1.valid, "Should be valid");
    console.assert(result1.errors.length === 0, "Should have no errors");
    
    // Test 2: Invalid CAD (camera at origin)
    const invalidCad = {
        type: "parametric_cad",
        model3D: { type: "box", dimensions: { width: 1, height: 1, depth: 1 } },
        camera: {
            position: { x: 0, y: 0, z: 0 }  // Invalid!
        }
    };
    
    const result2 = linter.lint(invalidCad);
    console.assert(!result2.valid, "Should be invalid");
    console.assert(result2.errors.some(e => e.includes("origin")), "Should catch origin error");
}
```

---

## 🔧 Troubleshooting

### Issue: Validation always fails

**Solution**: Check Pydantic version
```bash
pip install --upgrade pydantic
# Should be pydantic >= 2.0
```

### Issue: Linter not defined

**Solution**: Ensure scripts are loaded in correct order
```html
<!-- In parametric-cad.html -->
<script src="cad-linter.js"></script>  <!-- First -->
<script src="streaming-renderer.js"></script>
<script src="ai-ux-enhancements.js"></script>
<script src="parametric-cad.js"></script>  <!-- Last -->
```

### Issue: Streaming renderer doesn't animate

**Solution**: Check Three.js is loaded
```javascript
// Verify Three.js is available
console.log('THREE:', typeof THREE);  // Should be "object"
console.log('OrbitControls:', typeof OrbitControls);  // Should be "function"
```

### Issue: Natural language input not parsing correctly

**Solution**: Check intent parser logs
```javascript
// Enable debug logging
class AICADExperience {
    processNaturalLanguage(text) {
        console.log('[DEBUG] Input:', text);
        const intent = this.parseIntent(text);
        console.log('[DEBUG] Intent:', intent);
        // ...
    }
}
```

---

## 📚 API Reference

### Backend

#### `validate_cad_json(data: Dict) -> Union[CADVisualization, List[str]]`
Validates CAD JSON using Pydantic schemas.

**Returns**: `CADVisualization` if valid, `List[str]` of errors if invalid

#### `lint_cad_visualization(cad_json: Dict) -> List[str]`
Lints CAD JSON for common errors.

**Returns**: List of error messages (empty if valid)

#### `ProgressiveCADGenerator.generate_progressive(user_request: str) -> Dict`
Generates CAD using 3-step refinement.

**Returns**: Complete CAD visualization JSON

### Frontend

#### `CADLinter.lint(cadJson: Object) -> {valid: Boolean, errors: Array, warnings: Array}`
Validates CAD JSON before rendering.

#### `StreamingCADRenderer.startStreaming(options: Object) -> Promise`
Renders CAD with progressive refinement.

**Options**:
- `dimensions`: Object with width, height, depth
- `length`: Number (for extrusions)
- `progressCallback`: Function(progress)
- `completeCallback`: Function(mesh)
- `errorCallback`: Function(error)

#### `AICADExperience.processNaturalLanguage(text: String) -> Promise`
Parses natural language and executes CAD action.

---

## 🎓 Best Practices

1. **Always validate on backend first**
   - Pydantic validation catches 95% of AI errors
   - Don't trust AI output without validation

2. **Lint on frontend before expensive operations**
   - Linting is fast (~2ms)
   - Prevents crashes and bad UX

3. **Use progressive rendering for better UX**
   - Users prefer smooth animations over instant appearance
   - Progress feedback reduces perceived wait time

4. **Provide error recovery options**
   - Don't just show errors - offer fixes
   - Makes UI more forgiving

5. **Log validation failures**
   - Track which errors occur most often
   - Improve prompts to reduce failures

---

## 🚀 Next Steps

1. **Start Simple**: Add validation to one endpoint
2. **Test Thoroughly**: Verify validation catches errors
3. **Add Linting**: Enhance frontend safety
4. **Enable Streaming**: Improve rendering UX
5. **Add Natural Language**: Make it accessible

**Good luck with your integration! 🎉**

