# Research: AI Integration for Graph/Chart Visualization Generation

**Date**: December 14, 2025  
**Research Focus**: How other platforms integrate AI to generate CAD/graph/chart visualizations

---

## 🎯 Executive Summary

Based on GitHub research of major AI and visualization platforms, here are the **frameworks, libraries, and prompt patterns** used for AI-powered visualization generation:

### Key Findings:
1. **No Direct "AI → Visualization" Libraries** - Most platforms use AI to generate **code** that creates visualizations, not images
2. **Two-Stage Process**: AI generates code → Code renders visualization
3. **Prompt Engineering** is critical for structured outputs

---

## 📚 Major Approaches Found

### 1. **OpenAI's Approach: GPT Image Generation**

**Repository**: `openai/openai-python`

**How It Works**:
- **GPT-Image-1** / **DALL-E-3**: Generate images from text prompts
- **Streaming Support**: Can generate partial images during generation
- **Parameters**:
  ```python
  client.images.generate(
      model="gpt-image-1",
      prompt="A technical CAD drawing of a mechanical part",
      size="1024x1024",
      quality="high",
      response_format="b64_json",
      stream=True,
      partial_images=3  # Show progress
  )
  ```

**Limitations for Technical Visualizations**:
- ❌ Not precise enough for engineering CAD (can't guarantee dimensions)
- ❌ No parametric control
- ✅ Good for conceptual sketches, illustrations

**What We Can Learn**:
- Streaming visualization rendering improves UX
- Base64 encoding for easy embedding
- Partial image generation shows progress

---

### 2. **Plotly's Approach: Code-Based Visualization**

**Repository**: `plotly/plotly.py`

**How It Works**:
- AI generates **Python code** using Plotly library
- Code creates interactive, data-driven visualizations
- Uses declarative syntax (JSON-like objects)

**Example Pattern**:
```python
# AI generates this code:
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter3d(
    x=[1, 2, 3],
    y=[1, 2, 3],
    z=[1, 2, 3],
    mode='lines+markers'
))
fig.update_layout(
    scene=dict(
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)  # Isometric view
        )
    )
)
fig.show()
```

**Chart Types Supported**:
- 2D: Bar, Line, Scatter, Heatmap, Histogram
- 3D: Scatter3D, Surface, Mesh3D, Cone, Volume
- Specialized: Funnel, Waterfall, Sunburst, Treemap, Candlestick
- CAD-like: Streamline, Quiver (vector fields)

**Key Libraries Used**:
1. **`plotly.graph_objects`** - Low-level chart creation
2. **`plotly.express`** - High-level, concise API
3. **`plotly.figure_factory`** - Complex specialized charts
4. **`plotly.tools`** - Utilities (subplots, annotations)

**What We Can Learn**:
- ✅ **Structured output format** - JSON/dict-based configuration
- ✅ **Template system** - Reusable chart templates
- ✅ **Camera positioning** - Explicit camera controls for 3D views
- ✅ **Text templating** - Use d3-format syntax for labels (`%{variable:d3-format}`)

---

## 🔧 Implementation Patterns for AI → Visualization

### Pattern 1: **Structured Output with Pydantic**

**Source**: `openai/openai-python` examples

```python
from pydantic import BaseModel
from typing import List

class VisualizationConfig(BaseModel):
    type: str  # "scatter3d", "bar", "cad"
    data: dict
    layout: dict
    camera: dict

# AI call with structured output
completion = client.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Generate visualization config"},
        {"role": "user", "content": "Create a 3D scatter plot"}
    ],
    response_format=VisualizationConfig
)

config = completion.choices[0].message.parsed
```

**Benefits**:
- Guaranteed valid JSON structure
- Type safety
- AI can't output malformed data

---

### Pattern 2: **Tool Calling / Function Calling**

**How It Works**:
```python
tools = [{
    "type": "function",
    "function": {
        "name": "create_visualization",
        "description": "Create a 3D CAD visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "viz_type": {"type": "string", "enum": ["cad", "graph", "chart"]},
                "geometry": {"type": "object"},
                "camera_position": {"type": "object"},
                "constraints": {"type": "array"}
            }
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Show me a T-slot beam"}],
    tools=tools
)

# AI returns function call with structured args
tool_call = response.choices[0].message.tool_calls[0]
viz_config = json.loads(tool_call.function.arguments)
```

**This is EXACTLY what you're already doing!** ✅

---

### Pattern 3: **Code Generation → Sandboxed Execution**

**How Jupyter/Notebooks Do It**:
```python
# AI generates code string
code = """
import plotly.graph_objects as go
fig = go.Figure(data=[go.Mesh3d(x=[0,1,0], y=[0,0,1], z=[0,0,0])])
fig.show()
"""

# Execute in sandbox
exec(code, {"go": go, "np": np})  # Limited namespace
```

**Security Considerations**:
- ⚠️ Never use `exec()` directly in production
- ✅ Use restricted execution environments
- ✅ Validate all generated code before execution

---

## 📐 Specific CAD/Technical Drawing Approaches

### Approach 1: **SVG Path Generation**

**From Plotly Pattern Hatching**:
```python
# AI generates SVG paths for technical drawings
pattern = {
    "shape": "M0,0C0,2,4,2,4,4C4,6,0,6,0,8H2C2,6,6,6,6,4C6,2,2,2,2,0Z",
    "fillmode": "overlay",
    "size": 20,
    "solidity": 0.7
}
```

**What We Can Learn**:
- SVG paths can be AI-generated for custom shapes
- Use declarative format (path strings, not imperative drawing commands)

---

### Approach 2: **Parametric 3D Models**

**From Plotly 3D Examples**:
```python
# AI generates parametric equations
fig = go.Figure(data=[go.Surface(
    x=np.outer(np.linspace(-1, 1, 30), np.ones(30)),
    y=np.outer(np.ones(30), np.linspace(-1, 1, 30)),
    z=lambda x, y: np.sin(np.sqrt(x**2 + y**2))  # Parametric surface
)])
```

**For CAD**:
```python
# AI could generate:
{
    "type": "box",
    "dimensions": {"width": 0.02, "height": 0.04, "depth": 0.5},
    "position": {"x": 0, "y": 0, "z": 0},
    "rotation": {"x": 0, "y": 45, "z": 0}
}
```

---

## 🎨 Prompt Engineering Patterns

### Pattern 1: **Role + Format Instructions**

```
You are a technical CAD visualization expert. Generate visualizations in this EXACT format:

<CAD>
{
  "type": "constrained_engineering_cad",
  "model3D": {...},
  "technical_drawing": "<svg>...</svg>",
  "constraints": {...}
}
</CAD>

RULES:
1. Use double quotes for all JSON keys
2. Escape double quotes in SVG: viewBox=\"0 0 800 400\"
3. Always include camera position
4. Validate dimensions are positive numbers
```

**Why This Works**:
- Explicit format specification
- Examples prevent ambiguity
- Rules prevent common errors

---

### Pattern 2: **Few-Shot Examples**

```
Here are examples of valid CAD visualizations:

Example 1: Simple Box
<CAD>
{"type": "box", "dimensions": {"width": 1, "height": 1, "depth": 1}}
</CAD>

Example 2: T-Slot Beam
<CAD>
{
  "type": "constrained_engineering_cad",
  "profile": "20x40mm T-Slot",
  "model3D": {"type": "box", "dimensions": {...}},
  "constraints": {"accuracy": "±0.1mm"}
}
</CAD>

Now generate a visualization for: [USER REQUEST]
```

---

### Pattern 3: **Progressive Refinement**

```python
# Step 1: Get high-level structure
response1 = ai("What type of visualization? Options: cad, graph, chart")

# Step 2: Get specific parameters
response2 = ai(f"For {viz_type}, what are the dimensions/data?")

# Step 3: Get rendering details
response3 = ai("What camera angle and colors?")

# Combine into final visualization
```

**Benefits**:
- Reduces hallucination (smaller context per step)
- Easier to validate each step
- Can cache intermediate results

---

## 🚀 Recommended Architecture

### What You're Already Doing Right:
✅ **Delimiter-based detection** (`<CAD>...</CAD>`)  
✅ **Tool calling** (visualization_guide function)  
✅ **Structured JSON format**  
✅ **Client-side rendering** (Three.js)  

### Suggested Improvements:

#### 1. **Add Structured Output Validation**

```python
from pydantic import BaseModel, validator

class CADVisualization(BaseModel):
    type: str
    model3D: dict
    technical_drawing: str
    constraints: dict
    
    @validator('technical_drawing')
    def validate_svg(cls, v):
        if not v.startswith('<svg'):
            raise ValueError('Must be valid SVG')
        if '\\"' in v:  # Check for escaped quotes
            raise ValueError('SVG has escaping issues')
        return v

# In tool:
try:
    viz = CADVisualization(**json.loads(cad_content))
except ValidationError as e:
    return f"Invalid CAD format: {e}"
```

---

#### 2. **Template-Based Generation**

```python
CAD_TEMPLATES = {
    "t_slot_beam": {
        "type": "constrained_engineering_cad",
        "model3D": {
            "type": "box",
            "dimensions": {"width": "{width}", "height": "{height}", "depth": "{length}"}
        },
        "camera": {"position": {"x": "{cam_x}", "y": "{cam_y}", "z": "{cam_z}"}}
    }
}

# AI fills in placeholders:
template = CAD_TEMPLATES["t_slot_beam"]
filled = template.format(width=0.02, height=0.04, length=0.5, ...)
```

---

#### 3. **Add Visualization Linting**

```python
def lint_cad_visualization(cad_json):
    """Check for common AI errors"""
    errors = []
    
    # Check dimensions are positive
    if any(d <= 0 for d in cad_json.get('dimensions', {}).values()):
        errors.append("Dimensions must be positive")
    
    # Check SVG has proper quotes
    svg = cad_json.get('technical_drawing', '')
    if 'viewBox=\\"' in svg or "viewBox=\\'" in svg:
        errors.append("SVG has escaped quotes (use viewBox=\"0 0 800 400\")")
    
    # Check camera position
    cam = cad_json.get('camera', {}).get('position', {})
    if cam.get('x') == 0 and cam.get('y') == 0 and cam.get('z') == 0:
        errors.append("Camera at origin (0,0,0) - set isometric view")
    
    return errors
```

---

## 📊 Comparison Table

| **Approach** | **Accuracy** | **Flexibility** | **AI Difficulty** | **Best For** |
|--------------|--------------|-----------------|-------------------|--------------|
| **DALL-E Image Gen** | Low | High | Easy | Conceptual art, sketches |
| **Code Generation (Plotly)** | High | Very High | Medium | Data visualizations, graphs |
| **Structured JSON → Renderer** | Very High | Medium | Easy | Engineering CAD, technical drawings |
| **SVG Path Generation** | High | High | Hard | 2D technical diagrams |
| **Parametric 3D Models** | Very High | Low | Medium | Mechanical parts, CAD |

**Your Current Approach**: Structured JSON → Three.js Renderer ✅  
**Why It's Good**: High accuracy, easy for AI, perfect for engineering

---

## 🔗 Key Takeaways

### What Works Best for CAD Visualization:

1. **Use Structured Output** (JSON schema validation)
2. **Provide Detailed Examples** (few-shot prompting)
3. **Separate Concerns**:
   - AI generates **data structure**
   - Client renders **visualization**
4. **Isometric Default Camera** (you already fixed this!)
5. **Escape Handling** (you already fixed this!)

### Your System is Following Best Practices! ✅

You're using the **industry-standard approach**:
- AI generates structured data (JSON)
- Client-side renderer (Three.js) handles visualization
- Delimiter-based content detection (`<CAD>...</CAD>`)
- Tool calling for guidance (`visualization_guide()`)

---

## 📖 References

1. **OpenAI Image Generation**: https://github.com/openai/openai-python
   - Streaming images, partial generation
   - Base64 encoding, quality controls

2. **Plotly Python**: https://github.com/plotly/plotly.py  
   - Graph objects, declarative syntax
   - 3D camera controls, templates
   - Text formatting (d3-format, d3-time-format)

3. **Pydantic Structured Outputs**: 
   - Type validation for AI responses
   - Error handling for malformed data

4. **Three.js Best Practices**:
   - Local library files (no CDN timeouts)
   - Isometric camera defaults
   - OrbitControls for interaction

---

## 🎯 Next Steps for Your System

### Short Term (Already Done):
✅ Fixed Three.js CDN timeout (local files)  
✅ Fixed quote escaping in SVG examples  
✅ Set isometric home camera position  

### Medium Term (Recommended):
1. Add Pydantic validation for CAD JSON
2. Create CAD template library for common shapes
3. Add visualization linting (check for common AI errors)
4. Implement progressive refinement (multi-step generation)

### Long Term (Advanced):
1. Add streaming visualization updates (like OpenAI's partial images)
2. Implement visualization diff/comparison (show changes between versions)
3. Create visual debugging (show constraint violations in 3D)
4. Add collaborative editing (multiple users modify same CAD)

---

**Your system is already using the best patterns from industry leaders!** The fixes you just implemented (local Three.js, proper quote handling, isometric camera) align perfectly with how top platforms handle AI-generated visualizations.
