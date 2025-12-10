"""
Visualization Guidance Tools
============================

Meta-tools that provide detailed instructions for creating visualizations.
These are READ-ONLY guidance tools that return documentation, not execute actions.
"""

# Import the detailed visualization documentation
import json
import os

def visualization_guide(visual_type, **kwargs):
    """
    Returns comprehensive guidance for a specific visualization type.
    
    Args:
        visual_type: One of 14 visualization types
        
    Returns:
        Dictionary with delimiter, structure, rules, examples, best practices
    """
    
    # Load detailed guidance from embedded documentation
    guidance = _get_visualization_guidance()
    
    visual_type = visual_type.lower()
    
    if visual_type not in guidance:
        return {
            "success": False,
            "error": f"Unknown visualization type: {visual_type}",
            "available_types": list(guidance.keys())
        }
    
    return {
        "success": True,
        "visual_type": visual_type,
        "data": guidance[visual_type]
    }


def list_visualization_types(filter_by="all", **kwargs):
    """
    Lists all available visualization types with brief descriptions.
    
    Args:
        filter_by: Optional category filter (charts, diagrams, animations, etc.)
        
    Returns:
        Dictionary of visualization types grouped by category
    """
    
    categories = {
        "charts": [
            {
                "type": "apexcharts",
                "name": "ApexCharts",
                "best_for": "Modern interactive charts with professional look",
                "complexity": "Medium",
                "use_cases": ["Business dashboards", "Sales reports", "Analytics"]
            },
            {
                "type": "plotly",
                "name": "Plotly",
                "best_for": "Data analysis & scientific visualization",
                "complexity": "High",
                "use_cases": ["Scientific data", "Statistical analysis", "Complex datasets"]
            },
            {
                "type": "chartjs",
                "name": "Chart.js",
                "best_for": "Simple bar/line/pie charts",
                "complexity": "Low",
                "use_cases": ["Basic charts", "Simple reports", "Quick visualizations"]
            }
        ],
        "diagrams": [
            {
                "type": "mermaid",
                "name": "Mermaid",
                "best_for": "Flowcharts, sequence diagrams, process flows",
                "complexity": "Low",
                "use_cases": ["Flowcharts", "System diagrams", "Process documentation"]
            }
        ],
        "animations": [
            {
                "type": "gsap",
                "name": "GSAP",
                "best_for": "Professional UI animations",
                "complexity": "High",
                "use_cases": ["UI transitions", "Complex animations", "Timeline sequences"]
            },
            {
                "type": "lottie",
                "name": "Lottie",
                "best_for": "Loading spinners and vector animations",
                "complexity": "Low",
                "use_cases": ["Loading indicators", "Icons", "Simple animations"]
            }
        ],
        "technical": [
            {
                "type": "cad",
                "name": "CAD Viewer",
                "best_for": "Engineering drawings and 3D models",
                "complexity": "High",
                "use_cases": ["Mechanical drawings", "Product designs", "Engineering specs"]
            },
            {
                "type": "schematic",
                "name": "Schematic Diagrams",
                "best_for": "Electrical circuits and technical schematics",
                "complexity": "Medium",
                "use_cases": ["Circuit diagrams", "Wiring diagrams", "Electronic schematics"]
            },
            {
                "type": "blueprint",
                "name": "Blueprint",
                "best_for": "Architectural plans and blueprints",
                "complexity": "Medium",
                "use_cases": ["Floor plans", "Building layouts", "Architectural drawings"]
            }
        ],
        "interactive": [
            {
                "type": "execute_html",
                "name": "Interactive HTML",
                "best_for": "Custom interactive widgets and forms",
                "complexity": "High",
                "use_cases": ["Interactive demos", "Custom forms", "Educational tools"]
            },
            {
                "type": "threejs",
                "name": "Three.js 3D",
                "best_for": "3D graphics and interactive 3D scenes",
                "complexity": "High",
                "use_cases": ["3D models", "Interactive 3D", "Game-like visuals"]
            }
        ],
        "math": [
            {
                "type": "latex",
                "name": "LaTeX Math",
                "best_for": "Mathematical equations and formulas",
                "complexity": "Medium",
                "use_cases": ["Math equations", "Scientific formulas", "Academic papers"]
            },
            {
                "type": "molecule",
                "name": "Molecule Viewer",
                "best_for": "Chemical structures and molecular diagrams",
                "complexity": "Medium",
                "use_cases": ["Chemical structures", "Molecular models", "Chemistry education"]
            }
        ],
        "graphics": [
            {
                "type": "svg",
                "name": "SVG Graphics",
                "best_for": "Custom vector graphics and icons",
                "complexity": "Medium",
                "use_cases": ["Custom icons", "Vector illustrations", "Scalable graphics"]
            }
        ]
    }
    
    if filter_by == "all":
        return {
            "success": True,
            "total_types": sum(len(cat) for cat in categories.values()),
            "categories": categories
        }
    
    if filter_by in categories:
        return {
            "success": True,
            "category": filter_by,
            "types": categories[filter_by]
        }
    
    return {
        "success": False,
        "error": f"Unknown category: {filter_by}",
        "available_categories": list(categories.keys()) + ["all"]
    }


def compare_visualizations(types, use_case=None, **kwargs):
    """
    Compares 2-4 visualization types side-by-side.
    
    Args:
        types: List of 2-4 visualization types to compare
        use_case: Optional description of specific use case
        
    Returns:
        Comparison table and recommendation
    """
    
    if not isinstance(types, list) or len(types) < 2 or len(types) > 4:
        return {
            "success": False,
            "error": "Must provide 2-4 visualization types to compare"
        }
    
    # Comparison matrix
    features = {
        "apexcharts": {
            "interactivity": "High",
            "ease_of_use": "Medium",
            "visual_appeal": "High",
            "data_complexity": "Medium",
            "learning_curve": "Low",
            "strengths": ["Modern design", "Interactive tooltips", "Responsive", "Animation support"],
            "weaknesses": ["Requires CDN", "Limited 3D support"],
            "best_for": ["Business dashboards", "Sales reports", "Marketing analytics"]
        },
        "plotly": {
            "interactivity": "Very High",
            "ease_of_use": "Medium",
            "visual_appeal": "High",
            "data_complexity": "Very High",
            "learning_curve": "Medium",
            "strengths": ["Scientific-grade", "3D charts", "Statistical tools", "Zoom/pan"],
            "weaknesses": ["Complex API", "Large file size"],
            "best_for": ["Scientific data", "Research", "Complex analysis"]
        },
        "chartjs": {
            "interactivity": "Medium",
            "ease_of_use": "High",
            "visual_appeal": "Medium",
            "data_complexity": "Low-Medium",
            "learning_curve": "Very Low",
            "strengths": ["Simple API", "Small size", "Fast rendering"],
            "weaknesses": ["Basic features", "Limited interactivity"],
            "best_for": ["Simple charts", "Quick prototypes", "Basic reports"]
        },
        "mermaid": {
            "interactivity": "Low",
            "ease_of_use": "Very High",
            "visual_appeal": "Medium",
            "data_complexity": "N/A",
            "learning_curve": "Very Low",
            "strengths": ["Text-based", "Easy syntax", "Great for flowcharts"],
            "weaknesses": ["Not for data charts", "Limited styling"],
            "best_for": ["Flowcharts", "Diagrams", "Process flows"]
        },
        "execute_html": {
            "interactivity": "Very High",
            "ease_of_use": "Low",
            "visual_appeal": "Variable",
            "data_complexity": "Any",
            "learning_curve": "High",
            "strengths": ["Full control", "Any HTML/CSS/JS", "Unlimited possibilities"],
            "weaknesses": ["Requires coding", "Security concerns", "Time-consuming"],
            "best_for": ["Custom widgets", "Interactive demos", "Unique requirements"]
        }
    }
    
    comparison = {}
    for t in types:
        t = t.lower()
        if t in features:
            comparison[t] = features[t]
        else:
            comparison[t] = {
                "error": f"No comparison data for {t}"
            }
    
    # Generate recommendation based on use case
    recommendation = None
    reasoning = ""
    
    if use_case:
        use_case_lower = use_case.lower()
        
        if "business" in use_case_lower or "sales" in use_case_lower or "dashboard" in use_case_lower:
            recommendation = "apexcharts"
            reasoning = "ApexCharts excels at business dashboards with its modern design and interactive features"
        elif "scientific" in use_case_lower or "research" in use_case_lower or "analysis" in use_case_lower:
            recommendation = "plotly"
            reasoning = "Plotly is designed for scientific and statistical data with advanced features"
        elif "simple" in use_case_lower or "basic" in use_case_lower or "quick" in use_case_lower:
            recommendation = "chartjs"
            reasoning = "Chart.js is the easiest to use for simple, straightforward charts"
        elif "flowchart" in use_case_lower or "diagram" in use_case_lower or "process" in use_case_lower:
            recommendation = "mermaid"
            reasoning = "Mermaid is specifically designed for flowcharts and process diagrams"
        elif "custom" in use_case_lower or "interactive" in use_case_lower or "widget" in use_case_lower:
            recommendation = "execute_html"
            reasoning = "EXECUTE_HTML gives you full control for custom interactive elements"
    
    return {
        "success": True,
        "comparison": comparison,
        "recommendation": recommendation,
        "reasoning": reasoning,
        "types_compared": types
    }


def _get_visualization_guidance():
    """
    Returns embedded visualization guidance documentation.
    This contains ALL the detailed examples that were removed from the system prompt.
    """
    
    return {
        "molecule": {
            "delimiter": "<MOLECULE>...</MOLECULE>",
            "description": "Chemical molecular structures in SVG format",
            "structure": {
                "svg": "Standard SVG with viewBox",
                "title": "Required: Molecule name",
                "desc": "Required: Chemical formula (e.g., C8H10N4O2)"
            },
            "rules": [
                "RULE 1: Always include viewBox attribute",
                "RULE 2: Include title with molecule name",
                "RULE 3: Include desc with chemical formula",
                "RULE 4: Use standard chemical notation",
                "RULE 5: Keep structure centered in viewBox"
            ],
            "examples": [
                {
                    "title": "Caffeine Structure",
                    "code": """<MOLECULE>
<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
  <title>Caffeine</title>
  <desc>C8H10N4O2 structure</desc>
  <!-- Molecular structure elements here -->
</svg>
</MOLECULE>"""
                }
            ],
            "best_practices": [
                "Use consistent bond lengths",
                "Label atoms clearly",
                "Show stereochemistry when relevant",
                "Use standard color coding (C=black, O=red, N=blue, H=white)"
            ],
            "when_to_use": [
                "Chemistry education",
                "Research presentations",
                "Chemical documentation",
                "Molecular visualization"
            ],
            "when_not_to_use": [
                "3D molecular models (use dedicated molecular viewers)",
                "Interactive structure manipulation",
                "Large biomolecules like proteins or DNA"
            ],
            "common_errors": [
                "Missing viewBox attribute",
                "Incorrect chemical formula",
                "Poor scaling/positioning",
                "Missing title/desc elements"
            ]
        },
        
        "latex": {
            "delimiter": "<LATEX>...</LATEX>",
            "description": "Mathematical equations and formulas using LaTeX/KaTeX syntax",
            "structure": {
                "inline": "Simple equations without delimiters",
                "symbols": "\\int, \\sum, \\frac, \\sqrt, \\alpha, etc.",
                "subscripts": "x_i or x_{i+1}",
                "superscripts": "x^2 or x^{n+1}"
            },
            "rules": [
                "RULE 1: Use standard LaTeX math syntax",
                "RULE 2: Escape backslashes properly (use single \\)",
                "RULE 3: Use curly braces for multi-character sub/superscripts",
                "RULE 4: Use \\frac{numerator}{denominator} for fractions",
                "RULE 5: Keep equations readable and properly spaced"
            ],
            "examples": [
                {
                    "title": "Einstein's Energy Equation",
                    "code": "<LATEX>\nE = mc^2\n</LATEX>"
                },
                {
                    "title": "Fundamental Theorem of Calculus",
                    "code": "<LATEX>\n\\int_{a}^{b} f(x) \\, dx = F(b) - F(a)\n</LATEX>"
                },
                {
                    "title": "Standard Deviation Formula",
                    "code": "<LATEX>\n\\sigma = \\sqrt{\\frac{1}{N}\\sum_{i=1}^{N}(x_i - \\mu)^2}\n</LATEX>"
                },
                {
                    "title": "Quadratic Formula",
                    "code": "<LATEX>\nx = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\n</LATEX>"
                }
            ],
            "best_practices": [
                "Use proper spacing (\\,) in integrals and sums",
                "Define variables in surrounding text",
                "Break very long equations across multiple displays",
                "Use \\text{} for text within equations",
                "Use \\left and \\right for auto-sized parentheses"
            ],
            "when_to_use": [
                "Mathematical formulas",
                "Scientific equations",
                "Statistical notation",
                "Academic/research writing",
                "Physics equations"
            ],
            "when_not_to_use": [
                "Simple arithmetic (use plain text: 2 + 2 = 4)",
                "Code syntax (use markdown code blocks)",
                "Tables (use markdown tables)",
                "Chemical formulas (use subscript HTML or MOLECULE)"
            ],
            "common_errors": [
                "Unmatched braces {}",
                "Missing backslashes on symbols",
                "Incorrect subscript/superscript syntax",
                "Forgetting \\, spacing in integrals"
            ]
        },
        
        "svg": {
            "delimiter": "<SVG_VISUAL>...</SVG_VISUAL>",
            "description": "Custom vector graphics for logos, icons, illustrations, and print designs",
            "structure": {
                "svg": "Root element with xmlns and viewBox",
                "title": "REQUIRED for accessibility",
                "desc": "REQUIRED detailed description",
                "defs": "Optional: reusable elements (gradients, patterns)",
                "elements": "rect, circle, ellipse, line, polyline, polygon, path, text"
            },
            "rules": [
                "RULE 1: ALWAYS include viewBox='0 0 width height' attribute",
                "RULE 2: ALWAYS include <title> and <desc> elements for accessibility",
                "RULE 3: NEVER include JavaScript, scripts, or external resources",
                "RULE 4: Use xmlns='http://www.w3.org/2000/svg'",
                "RULE 5: Keep all coordinates within viewBox range"
            ],
            "examples": [
                {
                    "title": "Business Card - Premium Design",
                    "use_case": "Print design for graphic designers",
                    "code": """<SVG_VISUAL>
<svg viewBox="0 0 1050 600" xmlns="http://www.w3.org/2000/svg">
  <title>Business Card Design - 3.5" x 2"</title>
  <desc>Premium business card with gradient background</desc>
  
  <!-- Front side -->
  <rect x="0" y="0" width="525" height="600" fill="url(#gradient1)"/>
  <defs>
    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <circle cx="262" cy="200" r="60" fill="white" opacity="0.2"/>
  <text x="262" y="210" text-anchor="middle" fill="white" font-size="40" font-weight="bold">LOGO</text>
  <text x="262" y="350" text-anchor="middle" fill="white" font-size="28" font-weight="bold">JOHN DOE</text>
  <text x="262" y="380" text-anchor="middle" fill="white" font-size="16" opacity="0.9">Senior Designer</text>
  
  <!-- Back side -->
  <rect x="525" y="0" width="525" height="600" fill="#f8f8f8"/>
  <text x="787" y="300" text-anchor="middle" fill="#333" font-size="18" font-weight="bold">www.company.com</text>
</svg>
</SVG_VISUAL>"""
                },
                {
                    "title": "Event Poster - Concert",
                    "use_case": "Marketing materials for print designers",
                    "code": """<SVG_VISUAL>
<svg viewBox="0 0 816 1056" xmlns="http://www.w3.org/2000/svg">
  <title>Event Poster - Letter Size (8.5" x 11")</title>
  <desc>Concert poster with bold typography</desc>
  
  <rect width="816" height="1056" fill="url(#posterGradient)"/>
  <defs>
    <linearGradient id="posterGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1e3a8a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7e22ce;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <text x="408" y="300" text-anchor="middle" fill="white" font-size="72" font-weight="900">SUMMER</text>
  <text x="408" y="380" text-anchor="middle" fill="white" font-size="72" font-weight="900">CONCERT</text>
  <line x1="208" y1="420" x2="608" y2="420" stroke="white" stroke-width="3"/>
  
  <text x="408" y="500" text-anchor="middle" fill="white" font-size="32" font-weight="bold">LIVE MUSIC FESTIVAL</text>
  <text x="408" y="550" text-anchor="middle" fill="white" font-size="24" opacity="0.9">June 15-17, 2025</text>
  
  <rect x="308" y="700" width="200" height="60" fill="white" rx="30"/>
  <text x="408" y="740" text-anchor="middle" fill="#1e3a8a" font-size="24" font-weight="bold">GET TICKETS</text>
</svg>
</SVG_VISUAL>"""
                }
            ],
            "best_practices": [
                "Use viewBox for responsive scaling (not width/height attributes)",
                "Group related elements with <g> tags",
                "Define reusable elements (gradients, patterns) in <defs>",
                "Use semantic IDs for elements",
                "Optimize path data for smaller file sizes",
                "Use text-anchor='middle' for centered text",
                "Add opacity for layered effects"
            ],
            "when_to_use": [
                "Custom vector graphics and illustrations",
                "Logos and branding materials",
                "Print-ready designs (business cards, posters, flyers)",
                "Icons and UI elements",
                "Infographics",
                "T-shirt designs"
            ],
            "when_not_to_use": [
                "Interactive widgets or forms (use EXECUTE_HTML)",
                "Animations (use GSAP or Lottie)",
                "Data charts (use Chart.js, ApexCharts, or Plotly)",
                "3D graphics (use Three.js)"
            ],
            "common_errors": [
                "Missing viewBox attribute → graphic won't scale properly",
                "Missing title/desc elements → fails accessibility",
                "Including <script> tags → security risk, won't execute",
                "Coordinates outside viewBox → elements cut off",
                "Using external <image> resources → won't load"
            ]
        },
        
        "blueprint": {
            "delimiter": "<BLUEPRINT>...</BLUEPRINT>",
            "description": "Architectural floor plans, site layouts, and building drawings",
            "structure": {
                "svg": "Standard SVG with architectural grid background",
                "grid_pattern": "Optional repeating grid pattern for scale",
                "walls": "Thick strokes (stroke-width: 4) in professional blue",
                "doors": "Arcs showing door swing direction",
                "dimensions": "Text elements with measurement indicators",
                "labels": "Room names and dimensions"
            },
            "rules": [
                "RULE 1: Use thick lines (stroke-width: 4px) for walls",
                "RULE 2: Include grid pattern in <defs> for scale reference",
                "RULE 3: Label all rooms with text elements",
                "RULE 4: Show dimensions with measurement lines and text",
                "RULE 5: Use professional blue color scheme (#0074D9, #4db8ff)"
            ],
            "examples": [
                {
                    "title": "Commercial Office Floor Plan",
                    "use_case": "Architects presenting to clients",
                    "code": """<BLUEPRINT>
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <title>Commercial Office Floor Plan - Level 3</title>
  <desc>3,500 sq ft open plan with 4 meeting rooms</desc>
  
  <!-- Grid system for scale -->
  <defs>
    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#4db8ff" stroke-width="0.5" opacity="0.3"/>
    </pattern>
  </defs>
  <rect width="800" height="600" fill="url(#grid)"/>
  
  <!-- Outer walls (thick) -->
  <rect x="50" y="50" width="700" height="500" fill="none" stroke="#0074D9" stroke-width="4"/>
  
  <!-- Interior wall -->
  <line x1="200" y1="50" x2="200" y2="550" stroke="#0074D9" stroke-width="4"/>
  
  <!-- Door (arc showing swing) -->
  <path d="M 350 50 Q 370 50 370 70" fill="none" stroke="#0074D9" stroke-width="2"/>
  
  <!-- Dimensions -->
  <text x="400" y="30" text-anchor="middle" fill="#fff" font-size="14">70'-0"</text>
  <text x="20" y="300" text-anchor="middle" fill="#fff" font-size="14" transform="rotate(-90 20 300)">50'-0"</text>
  
  <!-- Room labels -->
  <text x="125" y="300" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">CONFERENCE A</text>
  <text x="125" y="320" fill="#fff" font-size="12" opacity="0.8">15' x 20'</text>
</svg>
</BLUEPRINT>"""
                }
            ],
            "best_practices": [
                "Use standard architectural symbols (AIA standards)",
                "Include scale reference (grid or scale bar)",
                "Show door swings with quarter-circle arcs",
                "Label all rooms with name and dimensions",
                "Add dimension lines with arrows for measurements",
                "Use consistent wall thickness (4px for exterior, 2px for interior)",
                "Include north arrow for orientation"
            ],
            "when_to_use": [
                "Architectural floor plans",
                "Site layouts and plot plans",
                "Space planning presentations",
                "Real estate marketing",
                "Construction documentation",
                "Renovation plans"
            ],
            "when_not_to_use": [
                "3D building models (use Three.js or dedicated CAD software)",
                "Detailed engineering specs (use CAD delimiter)",
                "Interactive virtual tours",
                "Photorealistic renderings"
            ],
            "common_errors": [
                "Inconsistent wall thickness",
                "Missing room labels",
                "No scale indicator (grid or scale bar)",
                "Poor alignment of walls and doors",
                "Dimensions not clearly visible",
                "Using wrong color scheme (not professional blue)"
            ]
        },
        
        "cad": {
            "delimiter": "<CAD>...</CAD>",
            "description": "Engineering CAD drawings, technical details, and mechanical parts. SUPPORTS BOTH: (1) SVG technical drawings, (2) Constrained 3D models with CadQuery",
            "structure": {
                "option_1_svg": "Technical 2D drawing with SVG - simple approach",
                "option_2_constrained": "Constrained 3D engineering CAD with validation - use for accurate mechanical parts",
                "dimension_lines": "Lines with arrow markers indicating measurements",
                "annotations": "Text labels for measurements and specifications",
                "cross_sections": "Detailed component views and cutaways",
                "leader_lines": "Lines connecting labels to parts"
            },
            "rules": [
                "RULE 1: For ACCURATE mechanical parts, use constrained_engineering_cad format (see examples)",
                "RULE 2: Use precise measurements and dimensions (±0.1mm tolerance available)",
                "RULE 3: Include title with part number/description",
                "RULE 4: Show all dimension lines with arrows (for SVG)",
                "RULE 5: Label all critical dimensions and tolerances",
                "RULE 6: For 3D models, include model3D geometry + technical_drawing SVG + constraints"
            ],
            "examples": [
                {
                    "title": "CONSTRAINED 3D CAD - T-Slot Beam (RECOMMENDED for accurate mechanical parts)",
                    "use_case": "Accurate mechanical engineering with constraint validation",
                    "code": """<CAD>
{
  "type": "constrained_engineering_cad",
  "profile": "20x40mm T-Slot Extrusion",
  "dimensions": {
    "width_mm": 20,
    "height_mm": 40,
    "length_mm": 500
  },
  "solver": "CadQuery",
  
  "model3D": {
    "type": "box",
    "dimensions": {
      "width": 0.02,
      "height": 0.04,
      "depth": 0.5
    },
    "material": {
      "color": 12632256,
      "metalness": 0.7,
      "roughness": 0.3
    },
    "camera": {
      "position": {
        "x": 0.3,
        "y": 0.3,
        "z": 0.8
      }
    }
  },
  
  "technical_drawing": "<svg viewBox='0 0 800 400' xmlns='http://www.w3.org/2000/svg'><title>Technical Drawing</title><rect x='100' y='150' width='600' height='100' fill='none' stroke='black' stroke-width='2'/><text x='400' y='280' text-anchor='middle' font-size='14'>500mm</text></svg>",
  
  "constraints": {
    "accuracy": "±0.1mm tolerance",
    "validation": {
      "dimensional_accuracy": true,
      "spacing_validated": true,
      "proportions_maintained": true
    },
    "applied": [
      "Length: 500mm (exact)",
      "Width: 20mm (exact)",
      "Height: 40mm (exact)",
      "All edges perpendicular (90°)",
      "All faces planar"
    ]
  }
}
</CAD>"""
                },
                {
                    "title": "SVG Technical Drawing - Steel Beam Connection (Simple 2D approach)",
                    "use_case": "Structural engineers showing connection details",
                    "code": """<CAD>
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <title>Steel Beam Connection Detail</title>
  <desc>W12x26 beam to W14x43 column connection with bolted plate</desc>
  
  <!-- I-beam cross section -->
  <rect x="250" y="100" width="100" height="200" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
  <rect x="240" y="100" width="120" height="20" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
  <rect x="240" y="280" width="120" height="20" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
  
  <!-- Dimension line with arrows -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <polygon points="0 0, 10 5, 0 10" fill="#333"/>
    </marker>
  </defs>
  <line x1="250" y1="80" x2="350" y2="80" stroke="#333" stroke-width="1" marker-start="url(#arrowhead)" marker-end="url(#arrowhead)"/>
  <text x="300" y="70" text-anchor="middle" font-size="12" fill="#333">12.0"</text>
  
  <!-- Bolt indicators -->
  <circle cx="270" cy="150" r="5" fill="none" stroke="#333" stroke-width="1"/>
  <circle cx="330" cy="150" r="5" fill="none" stroke="#333" stroke-width="1"/>
  
  <!-- Annotation -->
  <text x="380" y="150" font-size="10" fill="#333">4x 3/4" A325 bolts</text>
</svg>
</CAD>"""
                }
            ],
            "best_practices": [
                "🔥 USE CONSTRAINED CAD FORMAT when accuracy matters (±0.1mm tolerance)",
                "For constrained CAD: Set type='constrained_engineering_cad' in JSON",
                "Include both model3D (3D geometry) AND technical_drawing (2D SVG) for complete documentation",
                "Add constraints section to show validation status",
                "Show all critical dimensions with dimension lines",
                "Use standard engineering notation and units",
                "Include material specifications in annotations",
                "Add detail callouts for complex features",
                "Use proper scale and keep proportions accurate",
                "Show bolt patterns and hole locations",
                "Include weld symbols if applicable",
                "Add notes for tolerances and finishes"
            ],
            "when_to_use": [
                "Engineering drawings and specifications",
                "Mechanical part details with ACCURACY requirements (use constrained format)",
                "Manufacturing documentation",
                "Structural connection details",
                "Assembly instructions",
                "Technical proposals",
                "T-slot extrusions, beams, brackets, mounting plates"
            ],
            "when_not_to_use": [
                "Simple sketches or concepts (use SVG_VISUAL instead)",
                "Architectural plans (use BLUEPRINT)",
                "Electrical circuits (use SCHEMATIC)",
                "Animated assemblies (constrained CAD is static)"
            ],
            "common_errors": [
                "❌ Using SVG when accuracy is critical (use constrained format instead)",
                "❌ Missing 'type: constrained_engineering_cad' field in JSON",
                "❌ Missing constraints section",
                "Missing critical dimensions",
                "Incorrect scale or proportions (constrained CAD fixes this!)",
                "No title or part description",
                "Poor line weights (all same thickness)",
                "Missing material specifications",
                "Dimension lines without arrows"
            ],
            "constraint_solver_features": [
                "✅ Dimensional accuracy: ±0.1mm tolerance (vs ±5mm without constraints)",
                "✅ Hole spacing validation: Minimum 20mm enforced",
                "✅ Edge distance validation: Minimum 10mm enforced",
                "✅ Perpendicularity: All edges exactly 90°",
                "✅ Assembly constraints: Coincident, distance, parallel relationships",
                "✅ Renders as tabbed interface: 3D Model | Technical Drawing | Constraints tabs"
            ]
        },
        
        "schematic": {
            "delimiter": "<SCHEMATIC>...</SCHEMATIC>",
            "description": "Electrical circuit diagrams, electronic schematics, and wiring diagrams",
            "structure": {
                "svg": "Circuit layout with standard electrical symbols",
                "components": "Resistors, capacitors, transformers, ICs, etc.",
                "wires": "Lines connecting components (usually stroke='#ffd700')",
                "labels": "Component designators (R1, C1, T1) and values",
                "power_rails": "VCC, GND, voltage rails"
            },
            "rules": [
                "RULE 1: Use standard electrical/electronic symbols (IEEE/ANSI)",
                "RULE 2: Use gold/yellow color scheme (#ffd700) for professional look",
                "RULE 3: Label ALL components with designators (R1, C1, T1, IC1)",
                "RULE 4: Show component values (10KΩ, 100μF, 12V)",
                "RULE 5: Include circuit title and overall description"
            ],
            "examples": [
                {
                    "title": "12V Power Supply",
                    "use_case": "Electrical engineers documenting circuits",
                    "code": """<SCHEMATIC>
<svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
  <title>Power Supply Circuit - 12V DC Output</title>
  <desc>AC to DC converter with voltage regulation and filtering</desc>
  
  <!-- AC source -->
  <circle cx="50" cy="150" r="20" fill="none" stroke="#ffd700" stroke-width="2"/>
  <text x="50" y="155" text-anchor="middle" font-size="12" fill="#ffd700">AC</text>
  <text x="50" y="190" text-anchor="middle" font-size="10" fill="#ffd700">120V</text>
  
  <!-- Wire -->
  <line x1="70" y1="150" x2="150" y2="150" stroke="#ffd700" stroke-width="2"/>
  
  <!-- Transformer -->
  <rect x="150" y="120" width="60" height="60" fill="none" stroke="#ffd700" stroke-width="2"/>
  <line x1="170" y1="130" x2="170" y2="170" stroke="#ffd700" stroke-width="2"/>
  <line x1="190" y1="130" x2="190" y2="170" stroke="#ffd700" stroke-width="2"/>
  <text x="180" y="155" text-anchor="middle" font-size="10" fill="#ffd700">T1</text>
  <text x="180" y="200" text-anchor="middle" font-size="8" fill="#ffd700">12V 2A</text>
  
  <!-- Wire -->
  <line x1="210" y1="150" x2="250" y2="150" stroke="#ffd700" stroke-width="2"/>
  
  <!-- Resistor (zigzag) -->
  <path d="M 250 150 l 10 -10 l 10 20 l 10 -20 l 10 20 l 10 -10" fill="none" stroke="#ffd700" stroke-width="2"/>
  <text x="280" y="140" text-anchor="middle" font-size="10" fill="#ffd700">R1</text>
  <text x="280" y="175" text-anchor="middle" font-size="9" fill="#ffd700">10KΩ</text>
  
  <!-- Title -->
  <text x="250" y="30" text-anchor="middle" font-size="14" fill="#ffd700" font-weight="bold">12V DC POWER SUPPLY</text>
</svg>
</SCHEMATIC>"""
                }
            ],
            "best_practices": [
                "Follow IEEE/ANSI standard symbols",
                "Organize left-to-right (input → processing → output)",
                "Label all components with reference designators",
                "Show all component values and ratings",
                "Include power/ground symbols",
                "Use proper wire routing (minimize crossings)",
                "Add test points if applicable",
                "Include decoupling capacitors near ICs"
            ],
            "when_to_use": [
                "Electrical circuit diagrams",
                "Electronic schematics",
                "PCB design documentation",
                "Wiring diagrams",
                "Control system diagrams",
                "Signal flow diagrams"
            ],
            "when_not_to_use": [
                "3D circuit board views",
                "Mechanical drawings (use CAD)",
                "Software architecture (use Mermaid)",
                "Block diagrams without component details"
            ],
            "common_errors": [
                "Using non-standard symbols",
                "Missing component labels or values",
                "No reference designators",
                "Poor wire routing with many crossings",
                "Missing ground symbols",
                "Inconsistent color scheme"
            ]
        },
        
        "execute_html": {
            "delimiter": "<EXECUTE_HTML>...</EXECUTE_HTML>",
            "description": "Interactive widgets, forms, calculators, prototypes, and any custom HTML/CSS/JavaScript",
            "security": "Runs in fully isolated sandboxed iframe - your CSS/JS won't affect parent page",
            "structure": {
                "doctype": "<!DOCTYPE html> - REQUIRED",
                "html": "<html> root element",
                "head": "<head> with <style> tags for CSS",
                "body": "<body> with content and <script> tags"
            },
            "rules": [
                "RULE 1: Always include complete HTML5 structure (DOCTYPE, html, head, body)",
                "RULE 2: Put ALL CSS in <style> tags inside <head>",
                "RULE 3: Put ALL JavaScript in <script> tags at end of <body>",
                "RULE 4: Use modern, responsive CSS (flexbox, grid)",
                "RULE 5: Test all interactive functionality works correctly"
            ],
            "examples": [
                {
                    "title": "Logo Design Concept",
                    "use_case": "Graphic designers showing branding concepts",
                    "profession": "Graphic Designer",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    font-family: 'Helvetica Neue', sans-serif;
  }
  .logo-container {
    background: white;
    padding: 60px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    text-align: center;
  }
  .logo {
    font-size: 72px;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }
  .tagline {
    color: #666;
    font-size: 16px;
    letter-spacing: 3px;
    text-transform: uppercase;
  }
</style>
</head>
<body>
  <div class="logo-container">
    <div class="logo">BRAND</div>
    <div class="tagline">Excellence in Design</div>
  </div>
</body>
</html>
</EXECUTE_HTML>"""
                },
                {
                    "title": "Interactive Color Palette",
                    "use_case": "Designers presenting brand colors with click-to-copy",
                    "profession": "Graphic Designer / Brand Designer",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; padding: 30px; background: #f5f5f5; }
  h2 { color: #333; margin-bottom: 20px; }
  .palette { display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }
  .color { 
    width: 120px; 
    height: 120px; 
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.2s;
  }
  .color:hover { transform: scale(1.05); }
  .color-name { color: white; font-weight: bold; font-size: 14px; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }
  .color-hex { color: rgba(255,255,255,0.9); font-size: 12px; margin-top: 5px; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }
</style>
</head>
<body>
  <h2>Brand Color Palette</h2>
  <p>Click any color to copy hex code to clipboard</p>
  <div class="palette">
    <div class="color" style="background: #3b82f6;">
      <div class="color-name">Primary</div>
      <div class="color-hex">#3b82f6</div>
    </div>
    <div class="color" style="background: #8b5cf6;">
      <div class="color-name">Secondary</div>
      <div class="color-hex">#8b5cf6</div>
    </div>
    <div class="color" style="background: #10b981;">
      <div class="color-name">Accent</div>
      <div class="color-hex">#10b981</div>
    </div>
    <div class="color" style="background: #f59e0b;">
      <div class="color-name">Warning</div>
      <div class="color-hex">#f59e0b</div>
    </div>
  </div>
  <script>
    document.querySelectorAll('.color').forEach(el => {
      el.addEventListener('click', () => {
        const hexElement = el.querySelector('.color-hex');
        const hex = hexElement.textContent;
        navigator.clipboard.writeText(hex).then(() => {
          alert('Copied ' + hex + ' to clipboard!');
        });
      });
    });
  </script>
</body>
</html>
</EXECUTE_HTML>"""
                },
                {
                    "title": "Mobile App Wireframe",
                    "use_case": "UI/UX designers presenting app concepts",
                    "profession": "UI/UX Designer",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; 
    background: #f0f0f0; 
    padding: 20px; 
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .phone { 
    width: 375px; 
    height: 667px; 
    background: white; 
    border-radius: 30px; 
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
  }
  .status-bar { 
    height: 44px; 
    background: #f8f8f8; 
    display: flex; 
    justify-content: space-between;
    align-items: center;
    padding: 0 15px;
    font-size: 12px;
    border-bottom: 1px solid #e0e0e0;
  }
  .header { 
    padding: 20px; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  .header h1 { font-size: 28px; margin-bottom: 5px; font-weight: 700; }
  .header p { opacity: 0.9; font-size: 14px; }
  .card { 
    margin: 15px; 
    padding: 20px; 
    background: white; 
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: all 0.2s;
  }
  .card:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 4px 16px rgba(0,0,0,0.15); 
  }
  .card h3 { color: #333; margin-bottom: 8px; font-size: 18px; }
  .card p { color: #666; font-size: 14px; line-height: 1.5; }
</style>
</head>
<body>
  <div class="phone">
    <div class="status-bar">
      <span>9:41</span>
      <span>📶 📶 📶 ⚡ 100%</span>
    </div>
    <div class="header">
      <h1>Dashboard</h1>
      <p>Welcome back, User!</p>
    </div>
    <div class="card" onclick="alert('Analytics section clicked')">
      <h3>📊 Analytics</h3>
      <p>View your performance metrics and insights</p>
    </div>
    <div class="card" onclick="alert('Settings section clicked')">
      <h3>⚙️ Settings</h3>
      <p>Customize your preferences and account</p>
    </div>
    <div class="card" onclick="alert('Reports section clicked')">
      <h3>📈 Reports</h3>
      <p>Generate and download detailed reports</p>
    </div>
  </div>
</body>
</html>
</EXECUTE_HTML>"""
                },
                {
                    "title": "Design System Components",
                    "use_case": "UI developers showing component library",
                    "profession": "UI/UX Designer / Frontend Developer",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; 
    padding: 40px; 
    background: #fafafa; 
  }
  h1 { color: #111; margin-bottom: 10px; }
  h2 { margin: 30px 0 20px; color: #333; font-size: 20px; }
  .component-row { 
    display: flex; 
    gap: 15px; 
    flex-wrap: wrap; 
    margin: 20px 0; 
    align-items: center;
  }
  .btn {
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }
  .btn-primary { background: #3b82f6; color: white; }
  .btn-primary:hover { background: #2563eb; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
  .btn-secondary { background: #64748b; color: white; }
  .btn-secondary:hover { background: #475569; }
  .btn-success { background: #10b981; color: white; }
  .btn-success:hover { background: #059669; }
  .input { 
    padding: 12px; 
    border: 2px solid #e5e7eb; 
    border-radius: 6px;
    font-size: 14px;
    min-width: 250px;
    font-family: inherit;
  }
  .input:focus { 
    outline: none; 
    border-color: #3b82f6; 
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
</style>
</head>
<body>
  <h1>Design System Components</h1>
  <p style="color: #666; margin-bottom: 30px;">Reusable UI components for consistent design</p>
  
  <h2>Buttons</h2>
  <div class="component-row">
    <button class="btn btn-primary">Primary Button</button>
    <button class="btn btn-secondary">Secondary Button</button>
    <button class="btn btn-success">Success Button</button>
  </div>
  
  <h2>Form Inputs</h2>
  <div class="component-row">
    <input type="text" class="input" placeholder="Enter text...">
    <input type="email" class="input" placeholder="Email address">
    <input type="password" class="input" placeholder="Password">
  </div>
</body>
</html>
</EXECUTE_HTML>"""
                },
                {
                    "title": "Math Worksheet Generator",
                    "use_case": "Teachers creating practice problems",
                    "profession": "Teacher / Educator",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
    font-family: 'Comic Sans MS', 'Chalkboard SE', cursive; 
    padding: 40px; 
    background: #fff; 
  }
  .header { 
    text-align: center; 
    margin-bottom: 40px; 
    border-bottom: 3px solid #3b82f6; 
    padding-bottom: 20px; 
  }
  .header h1 { color: #3b82f6; margin: 0; font-size: 32px; }
  .header p { color: #666; margin: 10px 0 0; }
  .problems { 
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
    gap: 30px; 
  }
  .problem {
    padding: 20px;
    border: 2px dashed #ccc;
    border-radius: 8px;
    background: #f9fafb;
  }
  .problem-number { 
    background: #3b82f6;
    color: white;
    padding: 5px 12px;
    border-radius: 15px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 15px;
    font-size: 14px;
  }
  .equation { 
    font-size: 24px; 
    margin: 15px 0; 
    color: #333; 
    font-weight: bold;
  }
  .answer-line {
    border-top: 2px solid #333;
    width: 100px;
    margin-top: 20px;
    padding-top: 5px;
    color: #999;
    font-size: 12px;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>🎓 Math Practice Worksheet</h1>
    <p>Name: __________________ Date: __________</p>
    <p><strong>Topic:</strong> Addition & Subtraction (1-100)</p>
  </div>
  
  <div class="problems">
    <div class="problem">
      <span class="problem-number">1</span>
      <div class="equation">45 + 23 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
    
    <div class="problem">
      <span class="problem-number">2</span>
      <div class="equation">78 - 34 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
    
    <div class="problem">
      <span class="problem-number">3</span>
      <div class="equation">56 + 17 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
    
    <div class="problem">
      <span class="problem-number">4</span>
      <div class="equation">92 - 48 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
    
    <div class="problem">
      <span class="problem-number">5</span>
      <div class="equation">63 + 29 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
    
    <div class="problem">
      <span class="problem-number">6</span>
      <div class="equation">85 - 37 = ?</div>
      <div class="answer-line">Answer</div>
    </div>
  </div>
</body>
</html>
</EXECUTE_HTML>"""
                },
                {
                    "title": "Interactive Science Quiz",
                    "use_case": "Teachers creating interactive lessons",
                    "profession": "Teacher / Educator",
                    "code": """<EXECUTE_HTML>
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
    font-family: Arial, sans-serif; 
    padding: 30px; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
  }
  .container { 
    max-width: 600px; 
    width: 100%;
    background: white; 
    padding: 40px; 
    border-radius: 20px; 
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  }
  h1 { color: #333; text-align: center; margin-bottom: 10px; }
  .question { 
    font-size: 24px; 
    margin: 30px 0; 
    text-align: center; 
    color: #555; 
    font-weight: 500;
  }
  .options { 
    display: flex; 
    flex-direction: column; 
    gap: 15px; 
  }
  .option {
    padding: 20px;
    background: #f0f0f0;
    border: 3px solid transparent;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 18px;
  }
  .option:hover { background: #e0e0e0; transform: scale(1.02); }
  .option.correct { 
    background: #10b981; 
    color: white; 
    border-color: #059669; 
  }
  .option.incorrect { 
    background: #ef4444; 
    color: white; 
    border-color: #dc2626; 
  }
  .feedback { 
    margin-top: 20px; 
    padding: 20px; 
    border-radius: 10px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    display: none;
  }
  .feedback.show { display: block; }
  .feedback.correct { background: #d1fae5; color: #065f46; }
  .feedback.incorrect { background: #fee2e2; color: #991b1b; }
</style>
</head>
<body>
  <div class="container">
    <h1>🧠 Science Quiz</h1>
    <div class="question">What is the chemical symbol for water?</div>
    
    <div class="options">
      <div class="option" onclick="checkAnswer(this, false)">A) O2</div>
      <div class="option" onclick="checkAnswer(this, true)">B) H2O</div>
      <div class="option" onclick="checkAnswer(this, false)">C) CO2</div>
      <div class="option" onclick="checkAnswer(this, false)">D) NaCl</div>
    </div>
    
    <div class="feedback" id="feedback"></div>
  </div>
  
  <script>
    function checkAnswer(element, isCorrect) {
      const options = document.querySelectorAll('.option');
      options.forEach(opt => opt.style.pointerEvents = 'none');
      
      const feedback = document.getElementById('feedback');
      
      if (isCorrect) {
        element.classList.add('correct');
        feedback.className = 'feedback show correct';
        feedback.textContent = '✅ Correct! Water is H2O (2 Hydrogen atoms + 1 Oxygen atom)';
      } else {
        element.classList.add('incorrect');
        feedback.className = 'feedback show incorrect';
        feedback.textContent = '❌ Incorrect. The correct answer is H2O.';
      }
    }
  </script>
</body>
</html>
</EXECUTE_HTML>"""
                }
            ],
            "best_practices": [
                "Always use complete HTML5 structure (DOCTYPE → html → head → body)",
                "Put CSS in <style> tags in <head> (never inline unless necessary)",
                "Put JavaScript in <script> tags at end of <body> (before </body>)",
                "Use modern CSS (flexbox, grid, CSS variables)",
                "Make designs responsive (use %, vw/vh, flexbox, grid)",
                "Test all interactive elements work",
                "Use semantic HTML (header, nav, main, footer)",
                "Add accessibility features (labels, ARIA attributes)",
                "Comment complex CSS and JavaScript",
                "Use consistent naming conventions"
            ],
            "when_to_use": [
                "Interactive forms and calculators",
                "Custom widgets and tools",
                "UI/UX mockups and prototypes",
                "Design system component libraries",
                "Educational interactive content (quizzes, worksheets)",
                "Color palette previews with interactions",
                "Mobile app wireframes",
                "Business card/logo design concepts",
                "ANY custom HTML/CSS/JavaScript need"
            ],
            "when_not_to_use": [
                "Simple static charts → use Chart.js, ApexCharts, or Plotly",
                "Static vector graphics → use SVG delimiter",
                "3D graphics → use Three.js (unless you need custom HTML UI around it)",
                "Flowcharts/diagrams → use Mermaid",
                "Math equations → use LaTeX"
            ],
            "common_errors": [
                "Missing <!DOCTYPE html> declaration",
                "Using inline styles instead of <style> tags",
                "JavaScript errors breaking functionality (test before submitting)",
                "Not responsive (doesn't work on mobile)",
                "Missing closing tags (html, body, div, etc.)",
                "CSS selector specificity issues",
                "Event listeners on elements that don't exist yet"
            ],
            "security_notes": [
                "Runs in sandboxed iframe (cannot access parent page)",
                "Cannot access cookies or localStorage from parent",
                "Cannot make CORS requests (same-origin policy)",
                "Safe for user-generated content",
                "Your CSS will NOT affect the parent UI",
                "Your JavaScript runs in completely isolated context"
            ],
            "profession_examples": {
                "Graphic Designer": "Logo concepts, color palettes, brand mockups",
                "UI/UX Designer": "Wireframes, prototypes, component libraries",
                "Web Developer": "Interactive widgets, calculators, demos",
                "Teacher/Educator": "Quizzes, worksheets, interactive lessons",
                "Data Analyst": "Custom dashboards with interactions",
                "Print Designer": "Digital mockups of print materials"
            }
        }
    }
