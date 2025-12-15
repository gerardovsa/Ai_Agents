"""
AI Vision Integration for CAD
Enables AI to "see" and analyze visual designs
"""

import base64
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import io
from PIL import Image, ImageDraw, ImageFont
import cairosvg


@dataclass
class VisualAnalysisResult:
    """Result of AI vision analysis"""
    observations: List[str]
    warnings: List[str]
    suggestions: List[Dict]
    confidence: float
    focus_areas: List[str]  # Object IDs AI focused on


class AIVisionIntegration:
    """
    Integrates vision models (GPT-4V, Claude Vision) with CAD system
    Allows AI to "see" designs and provide visual feedback
    """
    
    def __init__(self, model_type='gpt4v'):
        self.model_type = model_type
        self.last_snapshot = None
        
    def generate_svg_snapshot(self, scene_graph: Dict, viewport: str = 'top') -> str:
        """
        Generate SVG representation of scene for AI to view
        
        Args:
            scene_graph: Current CAD scene
            viewport: 'top', 'front', 'side', '3d'
        
        Returns:
            SVG string
        """
        
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" ',
            'width="2000" height="1400" viewBox="0 0 2000 1400">',
            
            # Background
            '<rect width="2000" height="1400" fill="#f5f5f5"/>',
            
            # Grid
            self._generate_grid(2000, 1400, 100),
        ]
        
        # Draw objects
        objects = scene_graph.get('objects', {})
        for object_id, obj_data in objects.items():
            if obj_data.get('visible', True):
                svg_parts.append(self._render_object_to_svg(object_id, obj_data, viewport))
        
        # Add annotations for AI
        svg_parts.append(self._generate_ai_annotations(scene_graph))
        
        svg_parts.append('</svg>')
        
        svg_content = '\n'.join(svg_parts)
        self.last_snapshot = svg_content
        return svg_content
    
    def _generate_grid(self, width: int, height: int, spacing: int) -> str:
        """Generate SVG grid"""
        lines = []
        
        # Vertical lines
        for x in range(0, width + 1, spacing):
            lines.append(
                f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" '
                f'stroke="#ddd" stroke-width="1"/>'
            )
        
        # Horizontal lines
        for y in range(0, height + 1, spacing):
            lines.append(
                f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" '
                f'stroke="#ddd" stroke-width="1"/>'
            )
        
        return '\n'.join(lines)
    
    def _render_object_to_svg(self, object_id: str, obj_data: Dict, viewport: str) -> str:
        """Render single object to SVG"""
        
        obj_type = obj_data.get('type')
        
        if obj_type == 't-slot-beam':
            return self._render_beam_svg(object_id, obj_data, viewport)
        elif obj_type == 'corner-bracket':
            return self._render_bracket_svg(object_id, obj_data, viewport)
        
        return ''
    
    def _render_beam_svg(self, object_id: str, beam: Dict, viewport: str) -> str:
        """Render beam as SVG"""
        pos = beam.get('position', {})
        length = beam.get('length', 1000)
        profile = beam.get('profile', '40x40_standard')
        
        # Parse profile size
        profile_size = int(profile.split('x')[0]) if 'x' in profile else 40
        
        # Scale: 1mm = 0.5px
        scale = 0.5
        x = pos.get('x', 0) * scale + 100
        y = pos.get('y', 0) * scale + 100
        w = length * scale
        h = profile_size * scale
        
        color = beam.get('color', '#A0A0A0')
        
        # Main beam rectangle
        svg = f'''
        <g id="{object_id}" class="beam">
            <rect x="{x}" y="{y}" width="{w}" height="{h}" 
                  fill="{color}" stroke="#333" stroke-width="2"/>
            
            <!-- T-slots -->
            <rect x="{x + w/3}" y="{y + 2}" width="4" height="{h - 4}" fill="#666"/>
            <rect x="{x + 2*w/3}" y="{y + 2}" width="4" height="{h - 4}" fill="#666"/>
            
            <!-- Dimension label -->
            <text x="{x + w/2}" y="{y - 5}" 
                  text-anchor="middle" font-size="12" fill="#000">
                {length}mm
            </text>
            
            <!-- AI metadata -->
            <title>{object_id}: {profile}, {length}mm</title>
        </g>
        '''
        
        return svg
    
    def _render_bracket_svg(self, object_id: str, bracket: Dict, viewport: str) -> str:
        """Render bracket as SVG"""
        pos = bracket.get('position', {})
        scale = 0.5
        x = pos.get('x', 0) * scale + 100
        y = pos.get('y', 0) * scale + 100
        
        svg = f'''
        <g id="{object_id}" class="bracket">
            <circle cx="{x}" cy="{y}" r="8" fill="#888" stroke="#333" stroke-width="2"/>
            <title>{object_id}: Corner Bracket</title>
        </g>
        '''
        
        return svg
    
    def _generate_ai_annotations(self, scene_graph: Dict) -> str:
        """Generate AI-specific annotations"""
        
        annotations = ['<g id="ai-annotations">']
        
        # TODO: Add stress points, warnings, etc.
        # For now, add placeholder
        annotations.append(
            '<text x="10" y="20" font-size="14" fill="#666">'
            'AI Analysis: Ready'
            '</text>'
        )
        
        annotations.append('</g>')
        
        return '\n'.join(annotations)
    
    def svg_to_png(self, svg_content: str, width: int = 2000, height: int = 1400) -> bytes:
        """Convert SVG to PNG for vision models"""
        
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height
        )
        
        return png_data
    
    def svg_to_base64_png(self, svg_content: str) -> str:
        """Convert SVG to base64-encoded PNG"""
        png_data = self.svg_to_png(svg_content)
        return base64.b64encode(png_data).decode('utf-8')
    
    async def analyze_with_vision_model(
        self, 
        scene_graph: Dict,
        question: str = None,
        focus_objects: List[str] = None
    ) -> VisualAnalysisResult:
        """
        Send visual snapshot to AI vision model for analysis
        
        Args:
            scene_graph: Current CAD scene
            question: Specific question to ask AI
            focus_objects: Specific objects to focus on
        
        Returns:
            VisualAnalysisResult
        """
        
        # Generate SVG snapshot
        svg = self.generate_svg_snapshot(scene_graph)
        
        # Convert to PNG
        png_base64 = self.svg_to_base64_png(svg)
        
        # Build prompt for vision model
        prompt = self._build_vision_prompt(scene_graph, question, focus_objects)
        
        # Call vision model
        if self.model_type == 'gpt4v':
            result = await self._call_gpt4v(png_base64, prompt)
        elif self.model_type == 'claude':
            result = await self._call_claude_vision(png_base64, prompt)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        return self._parse_vision_result(result)
    
    def _build_vision_prompt(
        self,
        scene_graph: Dict,
        question: Optional[str],
        focus_objects: Optional[List[str]]
    ) -> str:
        """Build prompt for vision model"""
        
        # Extract key design parameters
        objects = scene_graph.get('objects', {})
        beam_count = sum(1 for obj in objects.values() if obj.get('type') == 't-slot-beam')
        connector_count = sum(1 for obj in objects.values() if obj.get('type') == 'corner-bracket')
        
        prompt_parts = [
            "You are an expert structural engineer analyzing a T-slot aluminum frame design.",
            "",
            f"This design has {beam_count} beams and {connector_count} connectors.",
            "",
            "Design specifications (JSON):",
            json.dumps(scene_graph, indent=2),
            "",
            "Please analyze this design and provide:",
            "1. Structural observations (strengths, weaknesses)",
            "2. Warnings (safety issues, excessive deflection, inadequate support)",
            "3. Suggestions for improvement (specific changes with exact positions/dimensions)",
            "4. Confidence level (0-1) in your analysis",
            "",
        ]
        
        if question:
            prompt_parts.append(f"Specific question: {question}")
            prompt_parts.append("")
        
        if focus_objects:
            prompt_parts.append(f"Focus specifically on these objects: {', '.join(focus_objects)}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "IMPORTANT: For any suggestions, provide them in this JSON format:",
            "{",
            '  "op": "add" or "replace" or "remove",',
            '  "path": "/objects/object_id/property",',
            '  "value": new_value,',
            '  "reason": "Explanation of why this change is recommended"',
            "}",
            "",
            "Focus on actionable, specific changes that can be applied directly to the design."
        ])
        
        return '\n'.join(prompt_parts)
    
    async def _call_gpt4v(self, image_base64: str, prompt: str) -> Dict:
        """Call GPT-4 Vision API"""
        
        # TODO: Actual API call
        # For now, return mock response
        
        import asyncio
        await asyncio.sleep(1)  # Simulate API call
        
        return {
            "observations": [
                "Main horizontal beams span 1800mm with 40x40mm profiles",
                "No center support visible - may cause excessive deflection",
                "Corner connections appear adequate with brackets"
            ],
            "warnings": [
                "Beam deflection may exceed L/240 limit under 200kg load",
                "Recommend adding center support or upgrading to 60x60mm profile"
            ],
            "suggestions": [
                {
                    "op": "add",
                    "path": "/objects/support_beam_001",
                    "value": {
                        "type": "t-slot-beam",
                        "profile": "40x40_standard",
                        "position": {"x": 900, "y": 0, "z": -600},
                        "length": 1400,
                        "rotation": {"x": 0, "y": 0, "z": 0}
                    },
                    "reason": "Adding center support beam reduces main beam deflection by 75% (from 4.2mm to 1.1mm)"
                },
                {
                    "op": "replace",
                    "path": "/objects/beam_main_001/profile",
                    "value": "60x60_standard",
                    "reason": "Upgrading to 60x60mm profile increases moment of inertia by 5x, reducing deflection to acceptable levels"
                }
            ],
            "confidence": 0.85,
            "focus_areas": ["beam_main_001", "beam_main_002"]
        }
    
    async def _call_claude_vision(self, image_base64: str, prompt: str) -> Dict:
        """Call Claude Vision API"""
        
        # TODO: Actual API call
        import asyncio
        await asyncio.sleep(1)
        
        return await self._call_gpt4v(image_base64, prompt)
    
    def _parse_vision_result(self, result: Dict) -> VisualAnalysisResult:
        """Parse vision model response into structured result"""
        
        return VisualAnalysisResult(
            observations=result.get('observations', []),
            warnings=result.get('warnings', []),
            suggestions=result.get('suggestions', []),
            confidence=result.get('confidence', 0.0),
            focus_areas=result.get('focus_areas', [])
        )
    
    def generate_annotated_svg(
        self,
        scene_graph: Dict,
        analysis_result: VisualAnalysisResult
    ) -> str:
        """
        Generate SVG with AI annotations overlaid
        Shows warnings, suggestions visually
        """
        
        svg = self.generate_svg_snapshot(scene_graph)
        
        # Add warning markers
        warning_markers = []
        for i, warning in enumerate(analysis_result.warnings):
            y_pos = 50 + i * 30
            warning_markers.append(f'''
                <g class="warning-marker">
                    <rect x="10" y="{y_pos}" width="300" height="25" 
                          fill="rgba(255, 152, 0, 0.8)" rx="5"/>
                    <text x="20" y="{y_pos + 17}" font-size="12" fill="white">
                        ⚠️ {warning[:50]}...
                    </text>
                </g>
            ''')
        
        # Add suggestion markers
        suggestion_markers = []
        for obj_id in analysis_result.focus_areas:
            suggestion_markers.append(f'''
                <circle class="ai-focus" 
                        data-object="{obj_id}"
                        r="20" fill="none" 
                        stroke="#4CAF50" stroke-width="3" stroke-dasharray="5,5">
                    <animate attributeName="r" values="20;25;20" dur="2s" repeatCount="indefinite"/>
                </circle>
            ''')
        
        # Insert annotations before closing </svg>
        annotated_svg = svg.replace(
            '</svg>',
            '\n'.join(warning_markers + suggestion_markers) + '\n</svg>'
        )
        
        return annotated_svg


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example scene graph
    scene = {
        "metadata": {"version": 1},
        "objects": {
            "beam_001": {
                "type": "t-slot-beam",
                "profile": "40x40_standard",
                "position": {"x": 0, "y": 0, "z": 0},
                "length": 1800,
                "color": "#A0A0A0"
            },
            "beam_002": {
                "type": "t-slot-beam",
                "profile": "40x40_standard",
                "position": {"x": 0, "y": 1360, "z": 0},
                "length": 1800,
                "color": "#A0A0A0"
            }
        }
    }
    
    async def test():
        vision = AIVisionIntegration(model_type='gpt4v')
        
        # Generate SVG
        svg = vision.generate_svg_snapshot(scene)
        print("SVG generated, length:", len(svg))
        
        # Save to file for inspection
        with open('cad_snapshot.svg', 'w') as f:
            f.write(svg)
        
        # Analyze with vision model
        result = await vision.analyze_with_vision_model(
            scene,
            question="Is this bed frame design structurally sound?"
        )
        
        print("\n=== AI VISION ANALYSIS ===")
        print(f"Confidence: {result.confidence}")
        print(f"\nObservations:")
        for obs in result.observations:
            print(f"  - {obs}")
        
        print(f"\nWarnings:")
        for warn in result.warnings:
            print(f"  ⚠️  {warn}")
        
        print(f"\nSuggestions:")
        for sug in result.suggestions:
            print(f"  ✨ {sug['reason']}")
            print(f"     Action: {sug['op']} {sug['path']}")
        
        # Generate annotated SVG
        annotated = vision.generate_annotated_svg(scene, result)
        with open('cad_annotated.svg', 'w') as f:
            f.write(annotated)
        
        print("\nAnnotated SVG saved to cad_annotated.svg")
    
    asyncio.run(test())
