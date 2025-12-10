# 🏗️ CAMPERVAN AI ENGINEERING AGENT - COMPLETE TECHNOLOGY STACK

**Project:** AI Agent for T-Slot Aluminum Campervan Fitout Design  
**Created:** December 10, 2025  
**Purpose:** Complete technical specification for building an AI agent that performs structural engineering, material selection, 3D rendering, and BOM generation for campervan conversions

---

## 📋 TABLE OF CONTENTS

1. [Core Engineering Libraries](#core-engineering-libraries)
2. [3D Visualization & CAD](#3d-visualization--cad)
3. [AI Agent Framework](#ai-agent-framework)
4. [Material Databases & APIs](#material-databases--apis)
5. [UI Frameworks](#ui-frameworks)
6. [Physics Simulation](#physics-simulation)
7. [Data Management](#data-management)
8. [Deployment Stack](#deployment-stack)
9. [Development Tools](#development-tools)
10. [Complete Implementation Roadmap](#complete-implementation-roadmap)

---

## 🔧 1. CORE ENGINEERING LIBRARIES

### **Structural Analysis & FEA**

#### **PyNite** ⭐ PRIMARY CHOICE
```bash
pip install PyNiteFEA
```

**Capabilities:**
- 3D structural analysis (beams, trusses, frames)
- Linear elastic analysis
- Load combinations
- Deflection calculations
- Moment diagrams
- Shear force diagrams
- Node/member stress analysis

**Perfect For:**
- Bed frame cantilever calculations
- Floor frame load distribution
- Suspended storage analysis
- Roof rack load paths

**Example Usage:**
```python
from PyNite import FEModel3D

# Create model
model = FEModel3D()

# Add nodes (T-slot connection points)
model.add_node('N1', 0, 0, 0)
model.add_node('N2', 1900, 0, 0)  # Bed length

# Add members (40x40mm T-slot extrusion)
model.add_member('M1', 'N1', 'N2', E=69000, G=26000, Iy=8.2e4, Iz=8.2e4, J=1.6e5, A=615)

# Add loads (200kg person on bed)
model.add_member_dist_load('M1', 'Fy', -2000/1.9, -2000/1.9, 0, 1.9)

# Analyze
model.analyze()

# Get results
deflection = model.Members['M1'].max_deflection('Fy')
print(f"Max deflection: {deflection} mm")
```

---

#### **AnaStruct** - Alternative/Complementary
```bash
pip install anastruct
```

**Capabilities:**
- 2D frame analysis
- Built-in visualization (matplotlib)
- Simple API for quick calculations
- Great for cross-checking PyNite results

**Example:**
```python
from anastruct import SystemElements

ss = SystemElements()
ss.add_element(location=[[0, 0], [1.9, 0]])  # 1900mm beam
ss.add_support_hinged(node_id=1)
ss.add_support_roll(node_id=2)
ss.q_load(element_id=1, q=-1000)  # 1000 N/m distributed load
ss.solve()
ss.show_results()  # Automatic visualization
```

---

#### **sectionproperties** ⭐ ESSENTIAL
```bash
pip install sectionproperties
```

**Capabilities:**
- Cross-section property calculations
- Moment of inertia (Ixx, Iyy, Ixy)
- Section modulus (elastic & plastic)
- Torsion constants
- Shear center
- Warping properties
- Custom shape definitions

**Perfect For:**
- T-slot extrusion property database
- Custom aluminum profile analysis
- Composite section calculations
- Optimization of profiles

**Example - 40x40mm T-slot:**
```python
from sectionproperties.pre.library import rectangular_section
from sectionproperties.analysis import Section

# Create 40x40mm hollow section (T-slot equivalent)
geom = rectangular_section(d=40, b=40, t=3.5, r_out=2, n_r=8)
geom.create_mesh(mesh_sizes=[2])
section = Section(geom)
section.calculate_geometric_properties()
section.calculate_warping_properties()

# Results
print(f"Area: {section.get_area()} mm²")
print(f"Ixx: {section.get_ic()[0]} mm⁴")
print(f"Iyy: {section.get_ic()[1]} mm⁴")
print(f"Section modulus: {section.get_z()[0]} mm³")
```

---

### **Units & Calculations**

#### **forallpeople** ⭐ ESSENTIAL
```bash
pip install forallpeople
```

**Capabilities:**
- Unit-aware calculations (prevents errors)
- SI units with automatic conversions
- Force, stress, length, mass handling
- Safety in engineering calculations

**Example:**
```python
import forallpeople as si
si.environment('structural')

# Define properties with units
length = 1.9 * si.m
load = 200 * si.kg * si.g  # 200kg person
E = 69 * si.GPa  # Aluminum modulus
I = 8.2e4 * si.mm**4

# Calculate deflection with units
deflection = (load * length**3) / (48 * E * I)
print(f"Deflection: {deflection.to('mm')}")  # Auto converts to mm
```

---

#### **handcalcs** - Beautiful Documentation
```bash
pip install handcalcs
```

**Capabilities:**
- Renders Python calculations as formatted math equations
- LaTeX output
- Jupyter notebook integration
- Perfect for documentation/reports

**Example:**
```python
from handcalcs import handcalc

@handcalc(jupyter_display=True)
def beam_deflection(w, L, E, I):
    delta = (5 * w * L**4) / (384 * E * I)
    return delta

# Generates beautifully formatted equation documentation
```

---

### **Optimization**

#### **scipy.optimize** - Built-in
```python
from scipy.optimize import minimize

def objective(x):
    # x[0] = profile width, x[1] = profile thickness
    cost = material_cost(x[0], x[1])
    weight = material_weight(x[0], x[1])
    return cost + weight * 0.5  # Multi-objective

constraints = {'type': 'ineq', 'fun': lambda x: safety_factor(x) - 2.0}
result = minimize(objective, x0=[40, 3.5], constraints=constraints)
```

---

## 🎨 2. 3D VISUALIZATION & CAD

### **3D Modeling Libraries**

#### **CadQuery** ⭐ PRIMARY CHOICE
```bash
pip install cadquery
```

**Capabilities:**
- Parametric 3D CAD in Python
- STEP/STL export (for 3D printing, fabrication)
- DXF export (for laser cutting)
- Assembly modeling
- Perfect for T-slot extrusion designs

**Example - T-slot Frame:**
```python
import cadquery as cq

# Create 40x40mm T-slot extrusion
extrusion = (
    cq.Workplane("XY")
    .rect(40, 40)
    .extrude(1900)  # 1900mm length
    .faces(">Z")
    .rect(10, 40)
    .cutBlind(-10)  # T-slot channel
)

# Export
cq.exporters.export(extrusion, 'tslot_beam.step')
cq.exporters.export(extrusion, 'tslot_beam.stl')
```

**T-slot Connection Library:**
```python
def tslot_corner_bracket(size=40):
    """Generate corner bracket for T-slot"""
    bracket = (
        cq.Workplane("XY")
        .rect(size, size)
        .extrude(5)
        .faces(">Z")
        .workplane()
        .rect(size-10, size-10)
        .cutBlind(-3)
    )
    return bracket

def tslot_assembly(length1, length2, angle=90):
    """Create T-slot corner assembly"""
    beam1 = create_tslot_beam(40, 40, length1)
    beam2 = create_tslot_beam(40, 40, length2)
    bracket = tslot_corner_bracket()
    
    assembly = (
        cq.Assembly()
        .add(beam1, name="beam1", loc=cq.Location((0,0,0)))
        .add(beam2, name="beam2", loc=cq.Location((length1,0,0), (0,0,1), angle))
        .add(bracket, name="bracket", loc=cq.Location((length1,0,0)))
    )
    return assembly
```

---

#### **build123d** - Next-Gen CadQuery
```bash
pip install build123d
```

**Capabilities:**
- Modern successor to CadQuery
- Cleaner API
- Better performance
- Topology optimization

---

#### **ezdxf** - 2D CAD Export
```bash
pip install ezdxf
```

**Capabilities:**
- DXF file creation/editing
- 2D drawings for fabrication
- Cut lists with dimensions
- Layer management

**Example - Cut List:**
```python
import ezdxf

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Add cut list dimensions
cuts = [
    ("Bed Frame - Long", 1900),
    ("Bed Frame - Short", 1400),
    ("Floor Cross Member", 1850)
]

y = 0
for name, length in cuts:
    msp.add_text(f"{name}: {length}mm", dxfattribs={'height': 5}).set_placement((0, y))
    msp.add_line((0, y-10), (length/10, y-10))  # Scale down for drawing
    y -= 50

doc.saveas('cut_list.dxf')
```

---

### **3D Rendering & Visualization**

#### **VTK (Visualization Toolkit)** - Desktop Apps
```bash
pip install vtk
```

**Capabilities:**
- High-performance 3D rendering
- Scientific visualization
- Interactive 3D viewers
- Cross-platform (Windows, Mac, Linux)

---

#### **Three.js** ⭐ WEB VISUALIZATION
```bash
npm install three
```

**Capabilities:**
- WebGL-based 3D rendering
- Interactive web viewers
- Material/lighting simulation
- Mobile support

**Integration with Python:**
```python
# Python backend generates model
import cadquery as cq
import json

# Generate model
assembly = create_van_layout()

# Export to JSON for Three.js
model_data = {
    'components': [],
    'materials': {},
    'connections': []
}

# Web frontend (JavaScript)
"""
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

// Load van model
const loader = new GLTFLoader();
loader.load('van_layout.gltf', (gltf) => {
    scene.add(gltf.scene);
});
"""
```

---

#### **PyVista** - Python 3D Visualization
```bash
pip install pyvista
```

**Capabilities:**
- VTK wrapper with simpler API
- Jupyter notebook integration
- Quick 3D plotting
- Mesh analysis

**Example:**
```python
import pyvista as pv

# Create mesh from CAD model
mesh = pv.read('van_frame.stl')

# Visualize with stress coloring
plotter = pv.Plotter()
plotter.add_mesh(mesh, scalars='stress', cmap='jet')
plotter.add_text('T-Slot Frame Stress Analysis', font_size=12)
plotter.show()
```

---

#### **Plotly** - Interactive Web Graphics
```bash
pip install plotly
```

**Capabilities:**
- Interactive 3D plots (web-based)
- Streamlit/Dash integration
- Engineering diagrams
- Real-time updates

**Example:**
```python
import plotly.graph_objects as go

# Create 3D scatter plot of T-slot nodes
fig = go.Figure(data=[go.Scatter3d(
    x=[0, 1900, 1900, 0],
    y=[0, 0, 1400, 1400],
    z=[0, 0, 0, 0],
    mode='markers+lines',
    marker=dict(size=8, color='red'),
    line=dict(color='blue', width=4)
)])

fig.update_layout(
    title='Bed Frame Layout',
    scene=dict(
        xaxis_title='Length (mm)',
        yaxis_title='Width (mm)',
        zaxis_title='Height (mm)'
    )
)

fig.show()
```

---

## 🤖 3. AI AGENT FRAMEWORK

### **LangChain/LangGraph** ⭐ RECOMMENDED
```bash
pip install langchain langgraph langchain-anthropic
```

**Why LangChain:**
- Mature ecosystem
- Tool/function calling support
- Memory management
- Chain-of-thought reasoning
- Document loaders for engineering specs

**Architecture:**
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool

# Define engineering tools
structural_analysis_tool = Tool(
    name="structural_analysis",
    func=lambda x: analyze_beam_loading(x),
    description="Analyzes structural loads on T-slot beams. Input: JSON with beam dimensions, loads, supports"
)

material_selector_tool = Tool(
    name="material_selector",
    func=lambda x: select_tslot_profile(x),
    description="Selects optimal T-slot profile. Input: required strength, weight constraint, budget"
)

# Create agent
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
agent = create_openai_tools_agent(llm, [structural_analysis_tool, material_selector_tool])
agent_executor = AgentExecutor(agent=agent, tools=[...])

# Execute
result = agent_executor.invoke({
    "input": "Design a bed frame for 200kg capacity, 1900x1400mm, using T-slot aluminum"
})
```

---

### **CrewAI** - Multi-Agent Orchestration
```bash
pip install crewai crewai-tools
```

**Why CrewAI:**
- Multiple specialist agents
- Task delegation
- Hierarchical workflows
- Built-in collaboration

**Example:**
```python
from crewai import Agent, Task, Crew

structural_engineer = Agent(
    role='Structural Engineer',
    goal='Calculate loads and select beam sizes',
    backstory='Expert in lightweight structures',
    tools=[pynite_tool, section_properties_tool],
    verbose=True
)

materials_engineer = Agent(
    role='Materials Engineer',
    goal='Select optimal T-slot profiles',
    backstory='Aluminum extrusion specialist',
    tools=[material_database_tool, cost_calculator_tool],
    verbose=True
)

cad_designer = Agent(
    role='CAD Designer',
    goal='Create 3D models and assembly instructions',
    backstory='Parametric CAD expert',
    tools=[cadquery_tool, dxf_export_tool],
    verbose=True
)

# Define tasks
task1 = Task(
    description='Analyze structural requirements for drop-down bed (200kg, 1900x1400mm)',
    agent=structural_engineer,
    expected_output='Required section modulus and deflection limits'
)

task2 = Task(
    description='Select T-slot profiles meeting structural requirements',
    agent=materials_engineer,
    expected_output='Bill of materials with part numbers and costs'
)

task3 = Task(
    description='Create 3D model and assembly instructions',
    agent=cad_designer,
    expected_output='STEP files and PDF assembly guide'
)

# Create crew
crew = Crew(
    agents=[structural_engineer, materials_engineer, cad_designer],
    tasks=[task1, task2, task3],
    verbose=True
)

# Execute
result = crew.kickoff()
```

---

### **AutoGen** - Conversational Agents
```bash
pip install pyautogen
```

**Why AutoGen:**
- Multi-agent conversations
- Code execution
- Human-in-the-loop
- Cost tracking

---

## 🗄️ 4. MATERIAL DATABASES & APIs

### **T-Slot Aluminum Database (Custom)**

#### **JSON Structure:**
```json
{
  "profiles": [
    {
      "id": "tslot_40x40_light",
      "dimensions": {
        "width": 40,
        "height": 40,
        "wall_thickness": 2.5,
        "slot_width": 10
      },
      "properties": {
        "area": 385,
        "Ixx": 6.8e4,
        "Iyy": 6.8e4,
        "Zx": 3400,
        "weight_per_meter": 1.04,
        "material": "6063-T5"
      },
      "mechanical": {
        "yield_strength": 145,
        "tensile_strength": 185,
        "elastic_modulus": 69000,
        "shear_modulus": 26000
      },
      "cost": {
        "aud_per_meter": 12.50,
        "supplier": "Makerbeam",
        "url": "https://www.makerbeam.com/40x40mm"
      }
    },
    {
      "id": "tslot_40x40_standard",
      "dimensions": {
        "width": 40,
        "height": 40,
        "wall_thickness": 3.5,
        "slot_width": 10
      },
      "properties": {
        "area": 615,
        "Ixx": 8.2e4,
        "Iyy": 8.2e4,
        "Zx": 4100,
        "weight_per_meter": 1.66,
        "material": "6063-T5"
      },
      "mechanical": {
        "yield_strength": 145,
        "tensile_strength": 185,
        "elastic_modulus": 69000,
        "shear_modulus": 26000
      },
      "cost": {
        "aud_per_meter": 16.80,
        "supplier": "Makerbeam",
        "url": "https://www.makerbeam.com/40x40mm-standard"
      }
    }
  ],
  "connectors": [
    {
      "id": "corner_bracket_90deg",
      "type": "corner_bracket",
      "angle": 90,
      "compatible_profiles": ["tslot_40x40_light", "tslot_40x40_standard"],
      "load_capacity": {
        "shear": 500,
        "tension": 800
      },
      "cost": {
        "aud_each": 4.50
      }
    }
  ]
}
```

#### **Python Interface:**
```python
import json

class TSlotDatabase:
    def __init__(self, json_path):
        with open(json_path) as f:
            self.data = json.load(f)
    
    def get_profile(self, profile_id):
        for profile in self.data['profiles']:
            if profile['id'] == profile_id:
                return profile
        return None
    
    def find_profiles_by_strength(self, min_section_modulus):
        """Find profiles meeting strength requirements"""
        results = []
        for profile in self.data['profiles']:
            if profile['properties']['Zx'] >= min_section_modulus:
                results.append(profile)
        return sorted(results, key=lambda x: x['cost']['aud_per_meter'])
    
    def calculate_cost(self, profile_id, length_meters, quantity=1):
        profile = self.get_profile(profile_id)
        return profile['cost']['aud_per_meter'] * length_meters * quantity

# Usage
db = TSlotDatabase('tslot_database.json')
suitable_profiles = db.find_profiles_by_strength(min_section_modulus=4000)
print(f"Cheapest option: {suitable_profiles[0]['id']} at ${suitable_profiles[0]['cost']['aud_per_meter']}/m")
```

---

### **Materials Project API** - General Material Properties
```bash
pip install mp-api
```

**Access:**
```python
from mp_api.client import MPRester

with MPRester("YOUR_API_KEY") as mpr:
    # Get aluminum properties
    docs = mpr.materials.summary.search(formula="Al")
    for doc in docs:
        print(f"Material: {doc.material_id}")
        print(f"Density: {doc.density}")
```

---

### **Engineering Standards Database (Custom)**

```python
# Australian/NZ Standards
STANDARDS = {
    'AS_1170': {
        'name': 'Structural Design Actions',
        'load_factors': {
            'dead_load': 1.2,
            'live_load': 1.5,
            'wind_load': 1.0
        }
    },
    'AS_1664': {
        'name': 'Aluminum Structures',
        'safety_factor': 2.0,
        'deflection_limit': 'L/250'  # span/250
    }
}

def apply_safety_factor(calculated_stress, standard='AS_1664'):
    return calculated_stress * STANDARDS[standard]['safety_factor']
```

---

## 🖥️ 5. UI FRAMEWORKS

### **Streamlit** ⭐ RAPID PROTOTYPING
```bash
pip install streamlit streamlit-aggrid
```

**Why Streamlit:**
- Fastest UI development
- Built-in widgets (sliders, inputs, file upload)
- Real-time updates
- Native data visualization support

**Example App:**
```python
import streamlit as st
import plotly.graph_objects as go

st.title("🚐 T-Slot Campervan Designer")

# Sidebar inputs
st.sidebar.header("Bed Frame Specifications")
bed_length = st.sidebar.slider("Bed Length (mm)", 1500, 2100, 1900, 50)
bed_width = st.sidebar.slider("Bed Width (mm)", 1200, 1600, 1400, 50)
weight_capacity = st.sidebar.number_input("Weight Capacity (kg)", 100, 300, 200, 10)

# Profile selection
profile_options = ["40x40mm Light", "40x40mm Standard", "40x40mm Heavy"]
profile = st.sidebar.selectbox("T-Slot Profile", profile_options)

# Calculate button
if st.button("🔧 Calculate Design"):
    with st.spinner("Analyzing structure..."):
        # Run engineering calculations
        result = analyze_bed_frame(bed_length, bed_width, weight_capacity, profile)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        col1.metric("Max Deflection", f"{result['deflection']:.2f} mm", delta=None)
        col2.metric("Safety Factor", f"{result['safety_factor']:.1f}", delta=None)
        col3.metric("Total Weight", f"{result['weight']:.1f} kg", delta=None)
        
        # 3D visualization
        fig = create_3d_model(result)
        st.plotly_chart(fig, use_container_width=True)
        
        # BOM table
        st.subheader("📋 Bill of Materials")
        st.dataframe(result['bom'])
        
        # Download buttons
        col1, col2 = st.columns(2)
        col1.download_button("📄 Download BOM (CSV)", result['bom_csv'], "bom.csv")
        col2.download_button("📐 Download CAD (STEP)", result['step_file'], "bed_frame.step")
```

---

### **Gradio** - ML Model Interfaces
```bash
pip install gradio
```

**Why Gradio:**
- Great for AI model interfaces
- HuggingFace integration
- Public sharing (gradio.live)
- Quick demos

**Example:**
```python
import gradio as gr

def design_bed_frame(length, width, weight, profile):
    # Engineering calculations
    result = calculate_design(length, width, weight, profile)
    return result['image'], result['bom_text'], result['cad_file']

interface = gr.Interface(
    fn=design_bed_frame,
    inputs=[
        gr.Slider(1500, 2100, value=1900, label="Bed Length (mm)"),
        gr.Slider(1200, 1600, value=1400, label="Bed Width (mm)"),
        gr.Number(value=200, label="Weight Capacity (kg)"),
        gr.Dropdown(["40x40mm Light", "40x40mm Standard"], label="Profile")
    ],
    outputs=[
        gr.Image(label="3D Visualization"),
        gr.Textbox(label="Bill of Materials"),
        gr.File(label="CAD File (STEP)")
    ],
    title="T-Slot Bed Frame Designer",
    description="AI-powered campervan bed frame design tool"
)

interface.launch()
```

---

### **React + Three.js** - Advanced Web App
```bash
npm install react three @react-three/fiber @react-three/drei
```

**Why React:**
- Professional web apps
- Best 3D rendering (Three.js integration)
- Mobile responsive
- Real-time collaboration possible

**Component Structure:**
```
van-designer-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VanViewer3D.jsx        # Three.js viewer
│   │   │   ├── ParameterPanel.jsx     # Input controls
│   │   │   ├── BOMTable.jsx           # Materials list
│   │   │   └── EngineeringResults.jsx # Calculations display
│   │   ├── services/
│   │   │   └── api.js                 # Backend API calls
│   │   └── App.jsx
├── backend/
│   ├── main.py                        # FastAPI server
│   ├── engineering/
│   │   ├── structural.py              # PyNite calculations
│   │   ├── materials.py               # Database queries
│   │   └── cad_generator.py           # CadQuery models
│   └── ai_agent/
│       └── crew.py                    # CrewAI agents
```

**Example 3D Viewer:**
```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Box } from '@react-three/drei'

function BedFrame({ length, width, height }) {
  return (
    <group>
      {/* Main frame */}
      <Box args={[length/1000, 0.04, 0.04]} position={[0, 0, 0]} />
      <Box args={[length/1000, 0.04, 0.04]} position={[0, width/1000, 0]} />
      {/* ... more beams */}
    </group>
  )
}

function VanViewer3D({ bedLength, bedWidth }) {
  return (
    <Canvas camera={{ position: [3, 3, 3] }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <BedFrame length={bedLength} width={bedWidth} />
      <OrbitControls />
    </Canvas>
  )
}
```

---

## ⚛️ 6. PHYSICS SIMULATION

### **PyBullet** - Physical Simulation
```bash
pip install pybullet
```

**Use Cases:**
- Test bed mechanism movement
- Validate sliding systems
- Collision detection
- Dynamic load simulation

**Example:**
```python
import pybullet as p
import pybullet_data

# Start simulation
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Create bed frame (simplified)
bed_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.95, 0.7, 0.05])
bed_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.95, 0.7, 0.05])
bed_body = p.createMultiBody(baseMass=20, baseCollisionShapeIndex=bed_collision,
                              baseVisualShapeIndex=bed_visual,
                              basePosition=[0, 0, 1.5])

# Add person load (200kg)
person_collision = p.createCollisionShape(p.GEOM_CYLINDER, radius=0.3, height=0.2)
person_body = p.createMultiBody(baseMass=200, baseCollisionShapeIndex=person_collision,
                                basePosition=[0, 0, 1.8])

# Simulate
for i in range(1000):
    p.stepSimulation()
    time.sleep(1/240)

p.disconnect()
```

---

## 🗃️ 7. DATA MANAGEMENT

### **SQLite** - Embedded Database
```python
import sqlite3

conn = sqlite3.connect('campervan_designs.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE designs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    van_model TEXT,
    bed_length REAL,
    bed_width REAL,
    profile_id TEXT,
    total_cost REAL,
    total_weight REAL,
    created_date TEXT,
    bom_json TEXT,
    step_file BLOB
)
''')

# Save design
cursor.execute('''
INSERT INTO designs (name, van_model, bed_length, bed_width, profile_id, total_cost)
VALUES (?, ?, ?, ?, ?, ?)
''', ("Drop-down Bed v1", "Fiat Ducato L3H2", 1900, 1400, "tslot_40x40_standard", 847.50))

conn.commit()
```

---

### **Supabase** - Cloud Database
```bash
pip install supabase
```

**Use Cases:**
- Multi-user access
- Design library sharing
- Real-time collaboration
- Authentication

---

### **Pandas** - Data Analysis
```bash
pip install pandas openpyxl
```

**Use Cases:**
- BOM manipulation
- Cost analysis
- Material comparison

```python
import pandas as pd

# Create BOM
bom = pd.DataFrame({
    'Item': ['40x40mm T-slot', 'Corner Bracket', 'M8 Bolt', 'M8 T-nut'],
    'Part Number': ['TS-4040-1900', 'CB-90-40', 'M8x20-SS', 'TN-M8'],
    'Quantity': [4, 8, 32, 32],
    'Unit Price (AUD)': [31.92, 4.50, 0.45, 0.85],
    'Total Price (AUD)': [127.68, 36.00, 14.40, 27.20]
})

# Export to Excel with formatting
with pd.ExcelWriter('bom.xlsx', engine='openpyxl') as writer:
    bom.to_excel(writer, sheet_name='Bill of Materials', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Bill of Materials']
    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 15
```

---

## 🚀 8. DEPLOYMENT STACK

### **Backend: FastAPI** ⭐
```bash
pip install fastapi uvicorn python-multipart
```

**API Structure:**
```python
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI()

class BedFrameDesign(BaseModel):
    length: float
    width: float
    weight_capacity: float
    profile_id: str

@app.post("/api/design/bed-frame")
async def design_bed_frame(design: BedFrameDesign):
    # Run AI agent
    result = await run_engineering_agent(design)
    return {
        "bom": result.bom,
        "cad_url": result.step_file_url,
        "calculations": result.engineering_report
    }

@app.get("/api/materials/profiles")
async def get_profiles():
    return tslot_database.get_all_profiles()

@app.post("/api/generate/cad")
async def generate_cad(design: BedFrameDesign):
    step_file = await generate_cadquery_model(design)
    return FileResponse(step_file, media_type='application/octet-stream',
                       filename='bed_frame.step')
```

---

### **Frontend Hosting**
- **Vercel** - React apps (free tier excellent)
- **Netlify** - Static sites + serverless functions
- **Render** - Full-stack apps (your current choice)

---

### **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies for CAD libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🛠️ 9. DEVELOPMENT TOOLS

### **IDE Extensions**
- **VS Code Extensions:**
  - Python (Microsoft)
  - Pylance (type checking)
  - Jupyter (notebook support)
  - REST Client (API testing)

### **Testing**
```bash
pip install pytest pytest-cov hypothesis
```

**Example Test:**
```python
import pytest
from engineering.structural import calculate_beam_deflection

def test_beam_deflection():
    # Given
    length = 1.9  # meters
    load = 2000   # Newtons
    E = 69000     # MPa
    I = 8.2e4     # mm^4
    
    # When
    deflection = calculate_beam_deflection(length, load, E, I)
    
    # Then
    assert deflection < 10  # mm (L/190 limit)
    assert deflection > 0
```

### **Documentation**
```bash
pip install sphinx sphinx-rtd-theme
```

---

## 📅 10. COMPLETE IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (2-3 weeks)**

**Week 1: Engineering Core**
- [ ] Set up Python environment (Python 3.11+)
- [ ] Install PyNite, sectionproperties, forallpeople
- [ ] Create T-slot profile database (JSON)
- [ ] Implement basic beam deflection calculator
- [ ] Test with simple bed frame example

**Week 2: Material Database**
- [ ] Research T-slot profiles from suppliers (Makerbeam, Faztek, local)
- [ ] Build comprehensive JSON database (50+ profiles)
- [ ] Add connector library (brackets, hinges, slides)
- [ ] Create material selector algorithm
- [ ] Add cost calculator

**Week 3: CAD Integration**
- [ ] Install CadQuery + ezdxf
- [ ] Create T-slot extrusion generator
- [ ] Build connection library (corners, T-joints, etc.)
- [ ] Test STEP export
- [ ] Generate first complete bed frame model

---

### **Phase 2: AI Agent (3-4 weeks)**

**Week 4: LangChain Setup**
- [ ] Install LangChain + Anthropic
- [ ] Create engineering tools:
  - [ ] Structural analysis tool
  - [ ] Material selector tool
  - [ ] BOM generator tool
  - [ ] CAD generator tool
- [ ] Test single-agent workflow

**Week 5-6: Multi-Agent System**
- [ ] Install CrewAI
- [ ] Define specialist agents:
  - [ ] Structural Engineer
  - [ ] Materials Specialist
  - [ ] CAD Designer
  - [ ] Cost Optimizer
  - [ ] Documentation Generator
- [ ] Create task workflows
- [ ] Test agent collaboration

**Week 7: Agent Optimization**
- [ ] Add memory/context management
- [ ] Implement error handling
- [ ] Create validation checks
- [ ] Test with complex scenarios

---

### **Phase 3: UI Development (3-4 weeks)**

**Week 8-9: Streamlit Prototype**
- [ ] Install Streamlit + dependencies
- [ ] Create main interface:
  - [ ] Parameter input panel
  - [ ] Real-time calculations
  - [ ] 3D visualization (Plotly)
  - [ ] BOM table
  - [ ] Download buttons
- [ ] Test user workflow
- [ ] Gather feedback

**Week 10-11: Enhanced Features**
- [ ] Add design templates (bed, kitchen, storage)
- [ ] Implement save/load functionality
- [ ] Add comparison tool (multiple designs)
- [ ] Create optimization wizard
- [ ] Add assembly instructions generator

---

### **Phase 4: Advanced Visualization (2-3 weeks)**

**Week 12-13: 3D Rendering**
- [ ] Install PyVista or Three.js integration
- [ ] Create interactive 3D viewer
- [ ] Add material textures
- [ ] Implement exploded view mode
- [ ] Add measurement tools

**Week 14: CAD Export**
- [ ] Ensure STEP export quality
- [ ] Add DXF cut lists
- [ ] Generate assembly drawings
- [ ] Create part labels
- [ ] Test with fabrication partners

---

### **Phase 5: Deployment (2 weeks)**

**Week 15: Backend API**
- [ ] Create FastAPI backend
- [ ] Deploy to Render/AWS
- [ ] Set up database (Supabase/PostgreSQL)
- [ ] Add authentication
- [ ] Test API endpoints

**Week 16: Production Launch**
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation
- [ ] User testing
- [ ] Launch! 🚀

---

## 💾 COMPLETE INSTALLATION SCRIPT

```bash
#!/bin/bash
# Complete setup script for Campervan AI Engineering Agent

# Create project directory
mkdir campervan-ai-agent
cd campervan-ai-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install core engineering libraries
pip install PyNiteFEA==1.0.4
pip install anastruct==1.4.0
pip install sectionproperties==2.1.4
pip install forallpeople==2.8.1
pip install handcalcs==1.8.0

# Install CAD libraries
pip install cadquery==2.4.0
pip install build123d==0.5.0
pip install ezdxf==1.1.3

# Install visualization
pip install pyvista==0.43.1
pip install plotly==5.18.0
pip install matplotlib==3.8.2
pip install vtk==9.3.0

# Install AI agent frameworks
pip install langchain==0.1.0
pip install langgraph==0.0.20
pip install langchain-anthropic==0.1.0
pip install crewai==0.1.25
pip install crewai-tools==0.0.10

# Install UI frameworks
pip install streamlit==1.29.0
pip install gradio==4.13.0
pip install streamlit-aggrid==0.3.4

# Install data management
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install supabase==2.3.0
pip install sqlalchemy==2.0.25

# Install API/deployment
pip install fastapi==0.108.0
pip install uvicorn[standard]==0.25.0
pip install python-multipart==0.0.6
pip install python-dotenv==1.0.0

# Install utilities
pip install scipy==1.11.4
pip install numpy==1.26.3
pip install pybullet==3.2.6
pip install pytest==7.4.3
pip install black==23.12.1
pip install mypy==1.8.0

# Install Jupyter for development
pip install jupyter==1.0.0
pip install ipywidgets==8.1.1

# Create project structure
mkdir -p {engineering,cad,ai_agent,ui,data,tests,docs}
mkdir -p data/{materials,designs,exports}

# Create requirements.txt
pip freeze > requirements.txt

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file with API keys (ANTHROPIC_API_KEY, etc.)"
echo "2. Build T-slot material database (data/materials/tslot_profiles.json)"
echo "3. Run first test: python tests/test_beam_calculation.py"
echo ""
echo "Happy building! 🚐✨"
```

---

## 🎯 ESTIMATED COSTS

### **Development Costs (One-time)**
- **Labor:** 12-16 weeks @ 20-30 hours/week = 240-480 hours
- **Software:** $0 (all open-source)
- **API Credits:** $100-200 (Claude API testing)
- **Total Development:** $100-200

### **Operating Costs (Monthly)**
- **Claude API:** $50-150/month (depending on usage)
- **Hosting (Render/AWS):** $20-50/month
- **Database (Supabase):** $0-25/month
- **Domain:** $2/month
- **Total Monthly:** $72-227/month

### **Break-even Analysis**
- **Subscription Model:** $29-49/month per user
- **Break-even:** 3-8 paying customers
- **Target:** 50-100 customers = $1,450-4,900/month revenue

---

## 🎓 LEARNING RESOURCES

### **Engineering**
- PyNite Documentation: https://pynite.readthedocs.io/
- sectionproperties Tutorials: https://sectionproperties.readthedocs.io/

### **CAD**
- CadQuery Documentation: https://cadquery.readthedocs.io/
- CadQuery Discord: Active community support

### **AI Agents**
- LangChain Tutorials: https://python.langchain.com/docs/
- CrewAI Examples: https://github.com/joaomdmoura/crewai-examples

### **T-Slot Systems**
- 80/20 Design Guide: https://8020.net/design-resources
- OpenBuilds Resources: https://openbuilds.com/resources/

---

## ✅ SUCCESS CRITERIA

**Minimum Viable Product (MVP):**
- [ ] User inputs bed dimensions, weight capacity
- [ ] AI agent calculates structural requirements
- [ ] System selects T-slot profiles
- [ ] Generates BOM with costs
- [ ] Exports basic STEP file
- [ ] Displays 3D visualization
- [ ] Total time: < 2 minutes per design

**Full Production System:**
- [ ] Multiple module types (bed, kitchen, storage, etc.)
- [ ] Advanced optimization (weight/cost/strength)
- [ ] Assembly instructions with images
- [ ] Cut lists with DXF export
- [ ] Material ordering integration
- [ ] User accounts & saved designs
- [ ] Mobile responsive interface
- [ ] Educational content integration

---

## 🚀 NEXT STEPS

1. **Set up development environment** (Week 1)
2. **Build T-slot material database** (Week 1-2)
3. **Create first engineering calculator** (Week 2-3)
4. **Integrate AI agent** (Week 4-7)
5. **Develop Streamlit UI** (Week 8-11)
6. **Deploy MVP** (Week 15-16)

**Ready to start building?** This system will revolutionize how people design campervan conversions! 🎉

---

*Document created: December 10, 2025*  
*Author: AI Engineering Assistant*  
*Project: T-Slot Aluminum Campervan Fitout Design System*
