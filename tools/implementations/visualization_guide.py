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
                "type": "execute_react",
                "name": "Interactive React",
                "best_for": "Stateful React components with hooks, charts (Recharts), and icons (Lucide)",
                "complexity": "Medium-High",
                "use_cases": ["Data dashboards", "Stateful widgets", "Component-based UIs", "Interactive charts"]
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
                "RULE 5: Keep all coordinates within viewBox range",
                "RULE 6: SVG TITLE BLOCK SPACING - If using title blocks in technical drawings, follow spacing rules from .github/SVG_CAD_GENERATION_RULES.md: Title block height = (font size × lines × 1.5) + 20px, text Y = block top + (font × 1.2), content start = block bottom + 40-60px clearance to prevent text overlap"
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
                "Add opacity for layered effects",
                "For technical drawings with title blocks: Ensure 40-60px clearance between title block bottom and content start. Formula: Title block ends at y=X, content starts at y=X+50 minimum. See .github/SVG_CAD_GENERATION_RULES.md for complete spacing calculations"
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
                "RULE 5: Use professional blue color scheme (#0074D9, #4db8ff)",
                "RULE 6: TITLE BLOCK SPACING - Title blocks MUST have 40-60px clearance before content starts. Formula: If title block ends at y=110, floor plan content starts at y=160+ (50px minimum gap). See .github/SVG_CAD_GENERATION_RULES.md"
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
  
  "technical_drawing": "<svg viewBox=\\"0 0 800 400\\" xmlns=\\"http://www.w3.org/2000/svg\\"><title>Technical Drawing</title><rect x=\\"100\\" y=\\"150\\" width=\\"600\\" height=\\"100\\" fill=\\"none\\" stroke=\\"black\\" stroke-width=\\"2\\"/><text x=\\"400\\" y=\\"280\\" text-anchor=\\"middle\\" font-size=\\"14\\">500mm</text></svg>",
  
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
                "Add notes for tolerances and finishes",
                "⚠️ SVG TITLE BLOCK SPACING - When generating SVG technical drawings (in 'technical_drawing' field), follow .github/SVG_CAD_GENERATION_RULES.md: Title block height = (font × lines × 1.5) + 20px, text Y position = block top + (font × 1.2), content start = block bottom + 40-60px clearance minimum"
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
                "RULE 5: Include circuit title and overall description",
                "RULE 6: TITLE BLOCK SPACING - If using title blocks, ensure 40-60px clearance between title block bottom and circuit diagram start. Formula: Title block height = (font × lines × 1.5) + 20px, text Y = block top + (font × 1.2), content start = block bottom + 50px minimum. See .github/SVG_CAD_GENERATION_RULES.md"
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
                "Include decoupling capacitors near ICs",
                "For schematics with title blocks: Position title at top with 40-60px spacing before circuit starts. Example: Title block y=20-110, circuit components start at y=160+. This prevents text overlap on title block."
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
        },

        "execute_react": {
            "delimiter": "<EXECUTE_REACT>...</EXECUTE_REACT>",
            "description": "Interactive React components with hooks, state, and modern UI libraries (Recharts, Lucide, Tailwind). Write JSX components ONLY — React, Babel, and library globals are injected automatically.",
            "security": "Runs in fully isolated sandboxed iframe — your JSX/CSS won't affect the parent page",
            "what_you_write": "Function components and hooks ONLY. DO NOT write import statements. Do NOT write ReactDOM.createRoot() — auto-injected. Just define: function App() { ... } or const App = () => { ... }",
            "auto_injected": [
                "React 18 (UMD global — all hooks available: useState, useEffect, useMemo, useCallback, useRef, useContext, useReducer, createContext, forwardRef, memo)",
                "ReactDOM 18 (createRoot auto-called on your App component)",
                "Babel Standalone (JSX transpilation at runtime — no build step)",
                "Recharts 2 (auto-included if BarChart, LineChart, PieChart etc. are detected — all chart components available as globals)",
                "Lucide React (auto-included if icon names detected — icons available as globals)",
                "Tailwind CSS (auto-included if Tailwind class names detected in className props)",
                "postMessage auto-resize (iframe grows to fit content automatically)"
            ],
            "root_component_rules": [
                "MUST define a function named 'App', 'Component', or 'Dashboard' — this is auto-mounted",
                "DO NOT call ReactDOM.createRoot() yourself — it is injected automatically",
                "DO NOT write import statements — all libraries are available as globals",
                "All React hooks are top-level destructures: const { useState } = React — already done for you",
                "Recharts components are already destructured from window.Recharts — just use <BarChart>",
                "Tailwind classes work directly in className props"
            ],
            "available_libraries": {
                "React hooks": "useState, useEffect, useMemo, useCallback, useRef, useContext, useReducer, createContext, forwardRef, memo, Fragment",
                "Recharts": "BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, Radar, ComposedChart, LabelList, ReferenceLine",
                "Lucide React": "All icons by name (ChevronRight, Star, Heart, Home, User, Settings, Search, Bell, Mail, Check, X, Plus, Minus, etc.) — auto-detected",
                "Tailwind CSS": "Full Tailwind v3 utility classes in className props — auto-detected"
            },
            "structure": {
                "pattern": "Write ONLY function components — no imports, no ReactDOM calls",
                "root_component": "function App() { ... } — renderer auto-mounts this",
                "hooks": "const [state, setState] = useState(0); — all hooks available at top level",
                "recharts_usage": "Use chart components directly: <BarChart data={data}><Bar dataKey='value' /></BarChart>",
                "tailwind_usage": "Use className='flex items-center gap-4 bg-blue-500 text-white p-4 rounded-lg'"
            },
            "examples": [
                {
                    "title": "Sales Dashboard with Recharts",
                    "use_case": "Business data visualizations with interactive charts",
                    "profession": "Data Analyst / Business Manager",
                    "code": """<EXECUTE_REACT>
const salesData = [
  { month: 'Jan', revenue: 42000, expenses: 28000, profit: 14000 },
  { month: 'Feb', revenue: 55000, expenses: 31000, profit: 24000 },
  { month: 'Mar', revenue: 48000, expenses: 29500, profit: 18500 },
  { month: 'Apr', revenue: 67000, expenses: 35000, profit: 32000 },
  { month: 'May', revenue: 71000, expenses: 38000, profit: 33000 },
  { month: 'Jun', revenue: 84000, expenses: 42000, profit: 42000 },
];

function App() {
  const [activeMetric, setActiveMetric] = useState('revenue');

  const metrics = [
    { key: 'revenue', label: 'Revenue', color: '#3b82f6' },
    { key: 'expenses', label: 'Expenses', color: '#ef4444' },
    { key: 'profit', label: 'Profit', color: '#10b981' },
  ];

  const activeColor = metrics.find(m => m.key === activeMetric)?.color || '#3b82f6';
  const total = salesData.reduce((sum, d) => sum + d[activeMetric], 0);

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif', background: '#f9fafb', minHeight: '100vh' }}>
      <h2 style={{ color: '#111', marginBottom: '8px' }}>Sales Dashboard</h2>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>
        Total {activeMetric}: <strong>${total.toLocaleString()}</strong>
      </p>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {metrics.map(m => (
          <button
            key={m.key}
            onClick={() => setActiveMetric(m.key)}
            style={{
              padding: '8px 16px', borderRadius: '8px', border: 'none',
              background: activeMetric === m.key ? m.color : '#e5e7eb',
              color: activeMetric === m.key ? 'white' : '#374151',
              cursor: 'pointer', fontWeight: '600', fontSize: '14px'
            }}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={salesData} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" tick={{ fill: '#6b7280' }} />
            <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fill: '#6b7280' }} />
            <Tooltip formatter={v => [`$${v.toLocaleString()}`, activeMetric]} />
            <Bar dataKey={activeMetric} fill={activeColor} radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
</EXECUTE_REACT>"""
                },
                {
                    "title": "Interactive Counter with Animated UI",
                    "use_case": "Stateful UI demo with hooks and transitions",
                    "profession": "Frontend Developer / UI Designer",
                    "code": """<EXECUTE_REACT>
function App() {
  const [count, setCount] = useState(0);
  const [history, setHistory] = useState([]);

  const add = (n) => {
    setCount(c => c + n);
    setHistory(h => [...h.slice(-8), { value: n, time: new Date().toLocaleTimeString() }]);
  };

  const reset = () => { setCount(0); setHistory([]); };

  const color = count > 0 ? '#10b981' : count < 0 ? '#ef4444' : '#6b7280';

  return (
    <div style={{ padding: '32px', fontFamily: 'system-ui, sans-serif', maxWidth: '480px', margin: '0 auto' }}>
      <div style={{
        textAlign: 'center', padding: '40px', background: 'white',
        borderRadius: '24px', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', marginBottom: '24px'
      }}>
        <p style={{ color: '#9ca3af', fontSize: '14px', margin: '0 0 8px' }}>Current Value</p>
        <div style={{ fontSize: '72px', fontWeight: '800', color, lineHeight: 1.1, transition: 'color 0.3s' }}>
          {count}
        </div>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px', flexWrap: 'wrap' }}>
          {[-10, -1, 1, 10].map(n => (
            <button
              key={n}
              onClick={() => add(n)}
              style={{
                padding: '12px 20px', borderRadius: '12px', border: 'none',
                background: n > 0 ? '#dbeafe' : '#fee2e2',
                color: n > 0 ? '#1d4ed8' : '#b91c1c',
                cursor: 'pointer', fontWeight: '700', fontSize: '16px'
              }}
            >
              {n > 0 ? `+${n}` : n}
            </button>
          ))}
        </div>
        <button onClick={reset} style={{
          marginTop: '16px', padding: '8px 24px', borderRadius: '8px',
          border: '2px solid #e5e7eb', background: 'white', cursor: 'pointer',
          color: '#6b7280', fontSize: '14px'
        }}>
          Reset
        </button>
      </div>

      {history.length > 0 && (
        <div style={{ background: 'white', borderRadius: '16px', padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <p style={{ color: '#374151', fontWeight: '600', marginBottom: '12px' }}>Recent Actions</p>
          {history.slice().reverse().map((h, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: '6px 0', borderBottom: '1px solid #f3f4f6', fontSize: '14px'
            }}>
              <span style={{ color: h.value > 0 ? '#10b981' : '#ef4444', fontWeight: '600' }}>
                {h.value > 0 ? `+${h.value}` : h.value}
              </span>
              <span style={{ color: '#9ca3af' }}>{h.time}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
</EXECUTE_REACT>"""
                }
            ],
            "best_practices": [
                "ONLY define function components — do not write imports or ReactDOM calls",
                "Always name your root component 'App', 'Component', or 'Dashboard'",
                "Use inline styles or Tailwind className for CSS (no external CSS files needed)",
                "For charts: use Recharts — just import BarChart, LineChart etc. directly (already provided)",
                "For icons: use Lucide icon components by name (e.g. <ChevronRight />) — already provided",
                "Split complex components into sub-functions defined above App",
                "Use useState for local state, useEffect for side effects",
                "Keep data arrays defined at module level (outside components) for static data",
                "Prefer ResponsiveContainer from Recharts so charts don't overflow"
            ],
            "when_to_use": [
                "Interactive stateful UIs (counters, toggles, filters, tabs)",
                "Data dashboards with charts (use Recharts)",
                "Multi-step forms or wizards",
                "Component demos and design system showcases",
                "Anything that benefits from React's component model and hooks",
                "Animated UIs (useState + CSS transitions)",
                "Real-time updating displays with useEffect + setInterval"
            ],
            "when_not_to_use": [
                "Static HTML/CSS layouts → use <EXECUTE_HTML>",
                "Simple charts without interactivity → use <APEXCHARTS> or <PLOTLY>",
                "SVG diagrams → use <SVG>",
                "Math equations → use <LATEX>",
                "Flowcharts → use <MERMAID>"
            ],
            "common_errors": [
                "Writing 'import React from react' — NOT needed, React is a global automatically",
                "Writing ReactDOM.createRoot() — NOT needed, auto-injected by renderer",
                "Not naming the root component App/Component/Dashboard — renderer won't find it",
                "Using npm package names in code that aren't available (only React, ReactDOM, Recharts, Lucide are auto-provided)",
                "Writing '=>' arrow functions in JSX attribute positions without wrapping in () — Babel handles this but be careful",
                "Forgetting to wrap multiple JSX sibling elements in a container or <></>"
            ],
            "vs_execute_html": {
                "use_execute_react_when": [
                    "You need React hooks (useState, useEffect, etc.)",
                    "You want Recharts for interactive charts",
                    "You are building component-based UI",
                    "You want Tailwind CSS utility classes",
                    "You prefer JSX syntax over raw HTML"
                ],
                "use_execute_html_when": [
                    "You want full control over raw HTML/CSS/JS",
                    "You are loading a CDN library not available in React mode",
                    "You are creating a complete HTML document with specific structure",
                    "You are building something that does not benefit from React components"
                ]
            }
        },

        "apexcharts": {
            "delimiter": "<APEXCHARTS>...</APEXCHARTS>",
            "description": "Modern interactive charts using ApexCharts library. Supports bar, line, area, pie, donut, scatter, heatmap, candlestick, radar, radialBar, treemap.",
            "content_format": "JSON object - standard ApexCharts options config (chart, series, xaxis, yaxis, etc.)",
            "critical_rules": [
                "RULE 1: Content MUST be a valid JSON object — the ApexCharts config object directly",
                "RULE 2: Do NOT wrap in HTML or <script> tags — just the JSON config",
                "RULE 3: chart.type must be a valid ApexCharts type: bar, line, area, pie, donut, scatter, heatmap, radialBar, radar, treemap, candlestick",
                "RULE 4: series must be an array",
                "RULE 5: xaxis.categories is required for most chart types",
                "RULE 6: DO NOT wrap in <EXECUTE_HTML> — use <APEXCHARTS> directly"
            ],
            "examples": [
                {
                    "title": "Bar Chart - Monthly Revenue",
                    "code": """<APEXCHARTS>
{
  "chart": { "type": "bar", "height": 350 },
  "series": [{ "name": "Revenue", "data": [45000, 52000, 48000, 61000, 55000, 67000] }],
  "xaxis": { "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"] },
  "title": { "text": "Monthly Revenue 2024", "align": "center" },
  "colors": ["#667eea"],
  "plotOptions": { "bar": { "borderRadius": 6, "columnWidth": "50%" } }
}
</APEXCHARTS>"""
                },
                {
                    "title": "Line Chart - Sales Trend",
                    "code": """<APEXCHARTS>
{
  "chart": { "type": "line", "height": 350, "zoom": { "enabled": true } },
  "series": [
    { "name": "Sales", "data": [30, 40, 35, 50, 49, 60, 70, 91, 125] },
    { "name": "Target", "data": [40, 40, 40, 50, 50, 60, 65, 80, 100] }
  ],
  "xaxis": { "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"] },
  "title": { "text": "Sales vs Target", "align": "center" },
  "stroke": { "curve": "smooth", "width": 3 },
  "markers": { "size": 5 }
}
</APEXCHARTS>"""
                },
                {
                    "title": "Donut Chart - Category Breakdown",
                    "code": """<APEXCHARTS>
{
  "chart": { "type": "donut", "height": 380 },
  "series": [44, 55, 13, 43, 22],
  "labels": ["Product A", "Product B", "Product C", "Product D", "Product E"],
  "title": { "text": "Sales by Category", "align": "center" },
  "legend": { "position": "bottom" },
  "plotOptions": { "pie": { "donut": { "size": "65%" } } }
}
</APEXCHARTS>"""
                },
                {
                    "title": "Area Chart - Website Traffic",
                    "code": """<APEXCHARTS>
{
  "chart": { "type": "area", "height": 350, "toolbar": { "show": true } },
  "series": [{ "name": "Page Views", "data": [3100, 4000, 2800, 5100, 4200, 6300, 7100] }],
  "xaxis": { "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] },
  "title": { "text": "Weekly Traffic", "align": "center" },
  "fill": { "type": "gradient", "gradient": { "shadeIntensity": 1, "opacityFrom": 0.7, "opacityTo": 0.1 } },
  "stroke": { "curve": "smooth" },
  "colors": ["#10b981"]
}
</APEXCHARTS>"""
                }
            ],
            "best_practices": [
                "Always set chart.height (350-500 is typical)",
                "Use colors array to set brand colors: ['#667eea', '#f5576c', '#10b981']",
                "Add title.text and title.align for labeling",
                "Use stroke.curve: 'smooth' for line/area charts",
                "Use plotOptions.bar.borderRadius for modern bar charts",
                "Add legend.position: 'bottom' for pie/donut charts",
                "Use responsive array for mobile breakpoints"
            ],
            "when_to_use": [
                "Business dashboards with bar, line, area charts",
                "Sales and revenue reporting",
                "KPI metrics and analytics",
                "Comparison charts",
                "Time-series data",
                "Distribution charts (pie, donut)"
            ],
            "when_not_to_use": [
                "Complex scientific/statistical plots → use <PLOTLY>",
                "3D charts → use <PLOTLY>",
                "Flowcharts/diagrams → use <MERMAID>",
                "Custom HTML widgets → use <EXECUTE_HTML>"
            ],
            "common_errors": [
                "Wrapping JSON in HTML tags (DON'T do this)",
                "Forgetting xaxis.categories for bar/line charts",
                "series not being an array",
                "Invalid chart.type value",
                "Missing chart.height (chart renders too small)"
            ]
        },

        "plotly": {
            "delimiter": "<PLOTLY>...</PLOTLY>",
            "description": "Scientific and data analysis charts using Plotly.js. Supports 40+ chart types including 3D, statistical, financial, maps, and scientific plots.",
            "content_format": "JSON object with 'data' array (traces) and 'layout' object — standard Plotly.js format",
            "critical_rules": [
                "RULE 1: Content MUST be JSON with 'data' array and 'layout' object",
                "RULE 2: Each element in 'data' is a trace object with 'type', 'x', 'y' (and 'z' for 3D)",
                "RULE 3: Do NOT wrap in HTML or <script> tags",
                "RULE 4: Supported trace types: scatter, bar, pie, box, heatmap, histogram, surface, scatter3d, contour, violin, waterfall, funnel, and more",
                "RULE 5: Use layout.title for chart title, layout.xaxis.title for axis labels",
                "RULE 6: DO NOT wrap in <EXECUTE_HTML>"
            ],
            "examples": [
                {
                    "title": "Scatter Plot - Correlation Analysis",
                    "code": """<PLOTLY>
{
  "data": [{
    "type": "scatter",
    "mode": "markers",
    "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "y": [2, 4, 5, 4, 7, 8, 9, 11, 12, 14],
    "marker": { "size": 10, "color": "#667eea" },
    "name": "Data Points"
  }],
  "layout": {
    "title": "Correlation: X vs Y",
    "xaxis": { "title": "X Variable" },
    "yaxis": { "title": "Y Variable" },
    "height": 400
  }
}
</PLOTLY>"""
                },
                {
                    "title": "Bar Chart - Sales by Region",
                    "code": """<PLOTLY>
{
  "data": [
    {
      "type": "bar",
      "x": ["North", "South", "East", "West"],
      "y": [120000, 95000, 138000, 107000],
      "marker": { "color": ["#667eea", "#f5576c", "#10b981", "#fbbf24"] },
      "name": "Revenue"
    }
  ],
  "layout": {
    "title": "Revenue by Region Q4 2024",
    "xaxis": { "title": "Region" },
    "yaxis": { "title": "Revenue ($)", "tickformat": "$,.0f" },
    "height": 400,
    "showlegend": false
  }
}
</PLOTLY>"""
                },
                {
                    "title": "3D Surface Plot",
                    "code": """<PLOTLY>
{
  "data": [{
    "type": "surface",
    "z": [
      [1, 2, 3, 4],
      [2, 4, 5, 6],
      [3, 5, 7, 8],
      [4, 6, 8, 10]
    ],
    "colorscale": "Viridis"
  }],
  "layout": {
    "title": "3D Surface Plot",
    "height": 500,
    "scene": {
      "xaxis": { "title": "X" },
      "yaxis": { "title": "Y" },
      "zaxis": { "title": "Z" }
    }
  }
}
</PLOTLY>"""
                },
                {
                    "title": "Box Plot - Statistical Distribution",
                    "code": """<PLOTLY>
{
  "data": [
    {
      "type": "box",
      "y": [52, 55, 69, 72, 45, 63, 78, 81, 57, 66, 71, 85, 48, 73, 64],
      "name": "Group A",
      "marker": { "color": "#667eea" }
    },
    {
      "type": "box",
      "y": [60, 65, 70, 72, 75, 80, 55, 68, 73, 79, 62, 77, 83, 58, 71],
      "name": "Group B",
      "marker": { "color": "#10b981" }
    }
  ],
  "layout": {
    "title": "Score Distribution by Group",
    "yaxis": { "title": "Score" },
    "height": 400
  }
}
</PLOTLY>"""
                }
            ],
            "best_practices": [
                "Always include both 'data' array and 'layout' object",
                "Use layout.height for consistent sizing (400-600 typical)",
                "Use layout.xaxis.title and layout.yaxis.title for axis labels",
                "Use layout.title for chart title",
                "Set tickformat for number formatting: '$,.0f' for currency, '.1%' for percentages",
                "Use colorscale for heatmaps and surfaces: 'Viridis', 'RdBu', 'Blues'",
                "Add mode: 'markers+lines' for scatter with lines"
            ],
            "when_to_use": [
                "Scientific and statistical data visualization",
                "3D charts (surface, scatter3d, mesh3d)",
                "Statistical plots (box, violin, histogram)",
                "Heatmaps and contour plots",
                "Financial charts (candlestick, OHLC, waterfall)",
                "Complex multi-trace charts",
                "Research and data analysis presentations"
            ],
            "when_not_to_use": [
                "Simple business dashboards → use <APEXCHARTS> (easier API)",
                "Flowcharts/diagrams → use <MERMAID>",
                "Custom interactive widgets → use <EXECUTE_HTML>"
            ],
            "common_errors": [
                "Missing 'data' array (required)",
                "Missing 'layout' object (required)",
                "Trace type not specified (always include 'type' in each trace)",
                "x/y arrays different lengths",
                "Using plotly Python syntax instead of JS (e.g., go.Bar vs {type: 'bar'})"
            ]
        },

        "chartjs": {
            "delimiter": "<CHARTJS>...</CHARTJS>",
            "description": "Simple, clean charts using Chart.js. Best for straightforward bar, line, pie, doughnut, radar and polar area charts.",
            "content_format": "JSON object — standard Chart.js config with 'type', 'data', and 'options'",
            "critical_rules": [
                "RULE 1: Content MUST be a valid JSON config object with 'type', 'data', and 'options'",
                "RULE 2: data.labels is required (array of label strings)",
                "RULE 3: data.datasets is required (array of dataset objects with 'label' and 'data')",
                "RULE 4: Do NOT wrap in HTML or <script> tags",
                "RULE 5: Valid chart types: bar, line, pie, doughnut, radar, polarArea, bubble, scatter",
                "RULE 6: DO NOT wrap in <EXECUTE_HTML>"
            ],
            "examples": [
                {
                    "title": "Bar Chart - Product Sales",
                    "code": """<CHARTJS>
{
  "type": "bar",
  "data": {
    "labels": ["Widgets", "Gadgets", "Doohickeys", "Thingamajigs"],
    "datasets": [{
      "label": "Units Sold Q4",
      "data": [1200, 890, 650, 430],
      "backgroundColor": ["#667eea", "#f5576c", "#10b981", "#fbbf24"],
      "borderRadius": 6
    }]
  },
  "options": {
    "responsive": true,
    "plugins": { "title": { "display": true, "text": "Q4 Product Sales" } },
    "scales": { "y": { "beginAtZero": true } }
  }
}
</CHARTJS>"""
                },
                {
                    "title": "Line Chart - Multi-Series",
                    "code": """<CHARTJS>
{
  "type": "line",
  "data": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "datasets": [
      {
        "label": "Revenue",
        "data": [45000, 52000, 48000, 61000, 55000, 67000],
        "borderColor": "#667eea",
        "backgroundColor": "rgba(102, 126, 234, 0.1)",
        "fill": true,
        "tension": 0.4
      },
      {
        "label": "Expenses",
        "data": [30000, 35000, 32000, 40000, 38000, 42000],
        "borderColor": "#f5576c",
        "backgroundColor": "rgba(245, 87, 108, 0.1)",
        "fill": true,
        "tension": 0.4
      }
    ]
  },
  "options": {
    "responsive": true,
    "plugins": { "title": { "display": true, "text": "Revenue vs Expenses 2024" } }
  }
}
</CHARTJS>"""
                },
                {
                    "title": "Doughnut Chart - Budget Allocation",
                    "code": """<CHARTJS>
{
  "type": "doughnut",
  "data": {
    "labels": ["Marketing", "R&D", "Operations", "Sales", "Admin"],
    "datasets": [{
      "data": [25, 30, 20, 15, 10],
      "backgroundColor": ["#667eea", "#f5576c", "#10b981", "#fbbf24", "#8b5cf6"]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": { "display": true, "text": "Budget Allocation %" },
      "legend": { "position": "bottom" }
    }
  }
}
</CHARTJS>"""
                }
            ],
            "best_practices": [
                "Always set 'responsive': true in options",
                "Use borderRadius for modern rounded bars",
                "Use tension: 0.4 for smooth curved lines",
                "Use fill: true with rgba backgroundColor for area effect under lines",
                "Add plugins.title.display: true and plugins.title.text for chart title",
                "Use scales.y.beginAtZero: true for bar charts",
                "Keep datasets labels short and clear"
            ],
            "when_to_use": [
                "Simple bar, line, pie charts",
                "Quick data overviews",
                "Basic reporting",
                "When you want a lightweight, fast chart"
            ],
            "when_not_to_use": [
                "Complex interactive dashboards → use <APEXCHARTS>",
                "Scientific/statistical analysis → use <PLOTLY>",
                "3D charts → use <PLOTLY>",
                "Custom styling needs → use <APEXCHARTS>"
            ],
            "common_errors": [
                "Missing data.labels array",
                "Missing data.datasets array",
                "Datasets with no 'data' property",
                "Invalid chart type string",
                "Wrong Chart.js v3 option paths (e.g. scales.yAxes[0] is OLD v2 — use scales.y in v3)"
            ]
        },

        "mermaid": {
            "delimiter": "<MERMAID>...</MERMAID>",
            "description": "Diagrams and flowcharts using Mermaid text syntax. Supports flowcharts, sequence diagrams, gantt charts, entity relationship diagrams, class diagrams, state diagrams, pie charts, journey diagrams.",
            "content_format": "Raw Mermaid diagram syntax — plain text, NOT JSON",
            "critical_rules": [
                "RULE 1: Content is plain Mermaid text syntax — NOT JSON",
                "RULE 2: First line must be the diagram type keyword: graph, flowchart, sequenceDiagram, gantt, erDiagram, classDiagram, stateDiagram-v2, pie, journey, xychart-beta",
                "RULE 3: Use correct Mermaid v10+ syntax",
                "RULE 4: For flowcharts use 'flowchart TD' or 'graph TD' (TD=top-down, LR=left-right)",
                "RULE 5: Colons in section names cause parse errors in gantt/journey — avoid them",
                "RULE 6: DO NOT wrap in <EXECUTE_HTML>"
            ],
            "examples": [
                {
                    "title": "Flowchart - Process Flow",
                    "code": """<MERMAID>
flowchart TD
    A[Start] --> B{Decision?}
    B -- Yes --> C[Do Action A]
    B -- No --> D[Do Action B]
    C --> E[End]
    D --> E
</MERMAID>"""
                },
                {
                    "title": "Sequence Diagram - API Call",
                    "code": """<MERMAID>
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    User->>Frontend: Submit form
    Frontend->>API: POST /submit
    API->>DB: INSERT record
    DB-->>API: Success
    API-->>Frontend: 200 OK
    Frontend-->>User: Show confirmation
</MERMAID>"""
                },
                {
                    "title": "Gantt Chart - Project Timeline",
                    "code": """<MERMAID>
gantt
    title Project Timeline Q1 2025
    dateFormat  YYYY-MM-DD
    section Design
    Wireframes        :a1, 2025-01-01, 14d
    Mockups           :after a1, 10d
    section Development
    Backend API       :2025-01-15, 21d
    Frontend Build    :2025-01-20, 25d
    section Testing
    QA Testing        :2025-02-10, 14d
    Bug Fixes         :2025-02-20, 7d
</MERMAID>"""
                },
                {
                    "title": "Entity Relationship Diagram",
                    "code": """<MERMAID>
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int customer_id FK
        date created_at
        float total
    }
    PRODUCT {
        int id PK
        string name
        float price
    }
    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
    }
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : included_in
</MERMAID>"""
                },
                {
                    "title": "Class Diagram - OOP Structure",
                    "code": """<MERMAID>
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +String breed
        +fetch() void
    }
    class Cat {
        +bool indoor
        +purr() void
    }
    Animal <|-- Dog
    Animal <|-- Cat
</MERMAID>"""
                },
                {
                    "title": "Pie Chart",
                    "code": """<MERMAID>
pie title Browser Market Share
    "Chrome" : 65.2
    "Safari" : 18.7
    "Firefox" : 3.9
    "Edge" : 4.1
    "Other" : 8.1
</MERMAID>"""
                }
            ],
            "best_practices": [
                "Use flowchart TD for vertical flow, flowchart LR for horizontal flow",
                "Quote node labels that contain special characters: A[\"Label with spaces\"]",
                "Use --> for solid arrows, ---> for dotted, === for thick",
                "Add labels on arrows: A -- label --> B",
                "For gantt: use dateFormat YYYY-MM-DD and specify dates precisely",
                "For sequence: use ->> for solid, -->> for dotted response arrows",
                "Keep diagrams focused — too many nodes reduces readability"
            ],
            "when_to_use": [
                "Flowcharts and process diagrams",
                "System architecture diagrams",
                "Sequence/interaction diagrams",
                "Database ER diagrams",
                "Class inheritance diagrams",
                "Project timeline (gantt charts)",
                "State machine diagrams",
                "Simple pie charts for proportional data"
            ],
            "when_not_to_use": [
                "Data charts with numbers → use <APEXCHARTS>, <PLOTLY>, or <CHARTJS>",
                "Technical engineering drawings → use <CAD> or <SCHEMATIC>",
                "Chemical structures → use <MOLECULE>",
                "Animations → use <GSAP> or <LOTTIE>"
            ],
            "common_errors": [
                "Using JSON format instead of Mermaid text syntax",
                "Missing diagram type keyword on first line",
                "Colons in section names for gantt/journey (causes parse error)",
                "Using old Mermaid v8 syntax that changed in v10",
                "Unquoted node labels with special characters"
            ]
        },

        "threejs": {
            "delimiter": "<THREEJS>...</THREEJS>",
            "description": "3D interactive graphics and scenes using Three.js. Supports 3D models, animations, interactive 3D environments.",
            "content_format": "JSON config describing the 3D scene: geometry, materials, lights, camera, animations",
            "critical_rules": [
                "RULE 1: Content MUST be a JSON config object",
                "RULE 2: Required top-level fields: scene (or geometry), camera, renderer",
                "RULE 3: Keep scenes focused and performant (avoid excessive polygon counts)",
                "RULE 4: DO NOT wrap in <EXECUTE_HTML> unless you need custom HTML around the 3D canvas"
            ],
            "examples": [
                {
                    "title": "Rotating 3D Box",
                    "code": """<THREEJS>
{
  "scene": {
    "background": "#1a1a2e"
  },
  "camera": {
    "type": "perspective",
    "fov": 75,
    "position": { "x": 0, "y": 0, "z": 5 }
  },
  "objects": [
    {
      "type": "mesh",
      "geometry": { "type": "BoxGeometry", "args": [2, 2, 2] },
      "material": { "type": "MeshPhongMaterial", "color": "#667eea", "shininess": 100 },
      "position": { "x": 0, "y": 0, "z": 0 },
      "animation": { "rotation": { "x": 0.01, "y": 0.01 } }
    }
  ],
  "lights": [
    { "type": "DirectionalLight", "color": "#ffffff", "intensity": 1, "position": { "x": 5, "y": 5, "z": 5 } },
    { "type": "AmbientLight", "color": "#404040", "intensity": 0.5 }
  ]
}
</THREEJS>"""
                }
            ],
            "best_practices": [
                "Always include lights (DirectionalLight + AmbientLight is standard)",
                "Set camera position to see the full scene",
                "Use MeshPhongMaterial or MeshStandardMaterial for realistic lighting",
                "Add animations (rotation/position tweens) to make scenes engaging",
                "Keep polygon counts reasonable for browser performance"
            ],
            "when_to_use": [
                "3D product visualization",
                "Interactive 3D data visualization",
                "3D scene setups",
                "3D games/simulations"
            ],
            "when_not_to_use": [
                "2D charts → use <APEXCHARTS> or <PLOTLY>",
                "Simple animations → use <GSAP> or <LOTTIE>",
                "Technical engineering drawings → use <CAD>"
            ],
            "common_errors": [
                "Missing lights — scene renders as solid black",
                "Camera too close or far from objects",
                "Missing animation loop — scene is static",
                "Invalid geometry type names (must match Three.js class names)"
            ]
        },

        "gsap": {
            "delimiter": "<GSAP>...</GSAP>",
            "description": "Professional UI animations and interactive motion graphics using GSAP (GreenSock Animation Platform).",
            "content_format": "JSON config describing elements to animate, timelines, and animation properties",
            "critical_rules": [
                "RULE 1: Content MUST be a JSON config with 'elements' and 'animations' or 'timeline'",
                "RULE 2: Specify target elements by id or class selector",
                "RULE 3: Animation properties use standard CSS property names",
                "RULE 4: DO NOT wrap in <EXECUTE_HTML>"
            ],
            "examples": [
                {
                    "title": "Animated Text Sequence",
                    "code": """<GSAP>
{
  "elements": [
    { "id": "headline", "type": "text", "content": "Welcome to the Future", "style": "font-size:48px;color:#667eea;font-weight:bold;" },
    { "id": "subtitle", "type": "text", "content": "Innovation starts here", "style": "font-size:24px;color:#555;" },
    { "id": "cta", "type": "button", "content": "Get Started", "style": "padding:16px 40px;background:#667eea;color:white;border:none;border-radius:30px;font-size:18px;cursor:pointer;" }
  ],
  "timeline": [
    { "target": "#headline", "from": { "opacity": 0, "y": -50 }, "to": { "opacity": 1, "y": 0 }, "duration": 1, "ease": "power2.out" },
    { "target": "#subtitle", "from": { "opacity": 0, "y": 30 }, "to": { "opacity": 1, "y": 0 }, "duration": 0.8, "ease": "power2.out" },
    { "target": "#cta", "from": { "opacity": 0, "scale": 0.8 }, "to": { "opacity": 1, "scale": 1 }, "duration": 0.6, "ease": "back.out(1.7)" }
  ],
  "layout": { "background": "#f8f9ff", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center", "height": "100%", "gap": "30px", "padding": "40px" }
}
</GSAP>"""
                }
            ],
            "best_practices": [
                "Use timelines for sequenced animations (elements animate one after another)",
                "Use ease values: 'power2.out', 'elastic.out', 'back.out(1.7)' for professional feel",
                "Animate from invisible (opacity:0) to visible for smooth entry",
                "Keep animation durations 0.3-1.5s for UI feel",
                "Chain related animations in a single timeline"
            ],
            "when_to_use": [
                "Landing page hero animations",
                "UI transition demos",
                "Interactive presentation slides",
                "Animated dashboards and data reveals",
                "Marketing animation concepts"
            ],
            "when_not_to_use": [
                "Loading spinners → use <LOTTIE>",
                "3D animations → use <THREEJS>",
                "Data charts → use <APEXCHARTS>"
            ],
            "common_errors": [
                "Missing target selectors that don't match element IDs",
                "Animation duration too long (>2s feels slow for UI)",
                "Forgetting to define all animated elements in the elements array"
            ]
        },

        "lottie": {
            "delimiter": "<LOTTIE>...</LOTTIE>",
            "description": "Pre-made vector animations in Lottie JSON format. Best for loading spinners, success/error indicators, animated icons, and decorative animations.",
            "content_format": "Lottie animation JSON (exported from Adobe After Effects via Bodymovin plugin, or from LottieFiles.com)",
            "critical_rules": [
                "RULE 1: Content MUST be a valid Lottie animation JSON object (has 'v', 'fr', 'ip', 'op', 'w', 'h', 'layers' fields)",
                "RULE 2: The JSON must be the FULL Lottie animation data",
                "RULE 3: Do NOT reference external URLs — embed the full JSON",
                "RULE 4: DO NOT wrap in <EXECUTE_HTML>"
            ],
            "examples": [
                {
                    "title": "Simple Loading Spinner (minimal Lottie)",
                    "code": """<LOTTIE>
{
  "v": "5.7.4",
  "fr": 30,
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 200,
  "nm": "Loading Spinner",
  "layers": [{
    "ty": 4,
    "nm": "Spinner",
    "sr": 1,
    "ks": {
      "o": { "a": 0, "k": 100 },
      "r": { "a": 1, "k": [
        { "t": 0, "s": [0], "e": [360] },
        { "t": 60, "s": [360] }
      ]},
      "p": { "a": 0, "k": [100, 100, 0] },
      "s": { "a": 0, "k": [100, 100, 100] }
    },
    "shapes": [{
      "ty": "gr",
      "it": [
        { "ty": "el", "s": { "a": 0, "k": [80, 80] }, "p": { "a": 0, "k": [0, 0] } },
        { "ty": "st", "c": { "a": 0, "k": [0.4, 0.49, 0.92, 1] }, "o": { "a": 0, "k": 100 }, "w": { "a": 0, "k": 8 }, "lc": 2, "lj": 1, "d": [{ "n": "d", "v": { "a": 0, "k": 200 } }, { "n": "o", "v": { "a": 0, "k": 0 } }] },
        { "ty": "fl", "c": { "a": 0, "k": [0, 0, 0, 0] }, "o": { "a": 0, "k": 0 } },
        { "ty": "tr", "p": { "a": 0, "k": [0, 0] }, "s": { "a": 0, "k": [100, 100] }, "o": { "a": 0, "k": 100 } }
      ]
    }],
    "ip": 0,
    "op": 60,
    "st": 0
  }]
}
</LOTTIE>"""
                }
            ],
            "best_practices": [
                "Use LottieFiles.com to find free pre-made animations — download as JSON",
                "For loading indicators: use a looping animation (ip=0, set loop=true in config if supported)",
                "Keep file size under 50KB for browser performance",
                "Set w/h to power of 2 values for optimization",
                "Use for simple icon animations — not for complex scenes"
            ],
            "when_to_use": [
                "Loading spinners and progress indicators",
                "Success/error confirmation animations",
                "Animated icons and micro-interactions",
                "Empty state illustrations",
                "Onboarding animations"
            ],
            "when_not_to_use": [
                "Complex interactive 3D → use <THREEJS>",
                "UI transition animations → use <GSAP>",
                "Data visualizations → use <APEXCHARTS> or <PLOTLY>",
                "Diagrams → use <MERMAID>"
            ],
            "common_errors": [
                "Missing required Lottie fields (v, fr, ip, op, w, h, layers)",
                "Referencing external assets that can't load in sandboxed iframe",
                "Invalid JSON structure (Lottie has very strict schema)"
            ]
        }
    }
