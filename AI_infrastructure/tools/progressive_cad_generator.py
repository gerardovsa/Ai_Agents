"""
Progressive Refinement for CAD Generation
Multi-step AI generation to reduce hallucination and improve accuracy
Based on OpenAI, Plotly, and Jupyter best practices
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json


class ProgressiveCADGenerator:
    """
    Generate CAD visualizations in multiple steps to improve accuracy
    
    Benefits:
    - Smaller context per step reduces hallucination
    - Each step can be validated independently
    - Can cache intermediate results
    - Better user feedback and control
    """
    
    def __init__(self, ai_client):
        """
        Initialize generator with AI client
        
        Args:
            ai_client: AI client instance (OpenAI, Anthropic, etc.)
        """
        self.ai_client = ai_client
        self.step_history = []
        
    def generate_step1_type_profile(self, user_request: str) -> Dict[str, Any]:
        """
        Step 1: Get CAD type and profile
        
        This step focuses only on determining WHAT to create,
        not the specific dimensions or rendering details.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            {
                "type": "parametric_cad",
                "profile": "profile-5",
                "description": "T-slot beam for frame construction"
            }
        """
        prompt = f"""
You are a CAD design expert. Based on the user's request, determine:
1. CAD type (constrained_engineering_cad, parametric_cad, or concept_sketch)
2. Profile (if applicable): profile-5, profile-6, profile-8, 1010, 1515, 2020
3. Brief description of what to create

User request: "{user_request}"

Respond with ONLY this JSON format:
{{
    "type": "<type>",
    "profile": "<profile or null>",
    "description": "<brief description>"
}}

RULES:
- Use "parametric_cad" for T-slot extrusions
- Use "constrained_engineering_cad" for custom machined parts
- Use "concept_sketch" for rough ideas/concepts
- If not a T-slot part, profile should be null
"""
        
        response = self.ai_client.chat(prompt)
        step1_data = self._extract_json(response)
        
        self.step_history.append({
            "step": 1,
            "prompt": prompt,
            "response": step1_data
        })
        
        return step1_data
    
    def generate_step2_dimensions(
        self,
        step1_data: Dict[str, Any],
        user_request: str
    ) -> Dict[str, Any]:
        """
        Step 2: Get dimensions and parameters
        
        This step focuses on specific measurements, not rendering details.
        
        Args:
            step1_data: Results from step 1
            user_request: Original user request
            
        Returns:
            {
                "dimensions": {"width": 0.02, "height": 0.02, "depth": 0.5},
                "length": 0.5,
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0}
            }
        """
        cad_type = step1_data.get('type')
        profile = step1_data.get('profile')
        description = step1_data.get('description')
        
        prompt = f"""
You are a CAD design expert. Based on the design specification, provide exact dimensions.

Design: {description}
Type: {cad_type}
Profile: {profile}

User request: "{user_request}"

Respond with ONLY this JSON format:
{{
    "dimensions": {{"width": <meters>, "height": <meters>, "depth": <meters>}},
    "length": <meters (for extrusions)>,
    "position": {{"x": 0, "y": 0, "z": 0}},
    "rotation": {{"x": 0, "y": 0, "z": 0}}
}}

RULES:
- Use meters (m) for all dimensions
- Standard T-slot profiles:
  * profile-5: 20x20mm = 0.02 x 0.02 m
  * profile-6: 30x30mm = 0.03 x 0.03 m
  * profile-8: 40x40mm = 0.04 x 0.04 m
- Minimum dimension: 0.001m (1mm)
- Maximum dimension: 100m
- Default position and rotation to zeros unless specified
"""
        
        response = self.ai_client.chat(prompt)
        step2_data = self._extract_json(response)
        
        # Validate dimensions are positive
        if 'dimensions' in step2_data:
            dims = step2_data['dimensions']
            for key in ['width', 'height', 'depth']:
                if key in dims and dims[key] <= 0:
                    raise ValueError(f"Dimension {key} must be positive, got {dims[key]}")
        
        self.step_history.append({
            "step": 2,
            "prompt": prompt,
            "response": step2_data
        })
        
        return step2_data
    
    def generate_step3_rendering(
        self,
        step1_data: Dict[str, Any],
        step2_data: Dict[str, Any],
        user_request: str
    ) -> Dict[str, Any]:
        """
        Step 3: Get rendering details (camera, drawing, constraints)
        
        This step focuses on visualization, not geometry.
        
        Args:
            step1_data: Results from step 1
            step2_data: Results from step 2
            user_request: Original user request
            
        Returns:
            {
                "camera": {
                    "position": {"x": 1.5, "y": 1.5, "z": 1.5},
                    "target": {"x": 0, "y": 0, "z": 0}
                },
                "include_technical_drawing": true,
                "constraints": {
                    "accuracy": "±0.1mm",
                    "material": "Aluminum 6061-T6"
                }
            }
        """
        prompt = f"""
You are a CAD visualization expert. Provide rendering settings for this design.

Design: {step1_data.get('description')}
Dimensions: {json.dumps(step2_data.get('dimensions', {}), indent=2)}

User request: "{user_request}"

Respond with ONLY this JSON format:
{{
    "camera": {{
        "position": {{"x": 1.5, "y": 1.5, "z": 1.5}},
        "target": {{"x": 0, "y": 0, "z": 0}}
    }},
    "include_technical_drawing": true,
    "constraints": {{
        "accuracy": "±0.1mm",
        "material": "Aluminum 6061-T6",
        "finish": "Anodized"
    }}
}}

RULES:
- Use isometric camera view: position at (1.5, 1.5, 1.5) or similar
- NEVER place camera at origin (0, 0, 0)
- Target is usually at (0, 0, 0) to look at the part
- Include technical drawing unless user says otherwise
- Standard tolerances for T-slot: ±0.1mm to ±0.5mm
"""
        
        response = self.ai_client.chat(prompt)
        step3_data = self._extract_json(response)
        
        # Validate camera not at origin
        if 'camera' in step3_data and 'position' in step3_data['camera']:
            pos = step3_data['camera']['position']
            if pos.get('x') == 0 and pos.get('y') == 0 and pos.get('z') == 0:
                # Fix by setting isometric view
                step3_data['camera']['position'] = {"x": 1.5, "y": 1.5, "z": 1.5}
        
        self.step_history.append({
            "step": 3,
            "prompt": prompt,
            "response": step3_data
        })
        
        return step3_data
    
    def combine_steps(
        self,
        step1_data: Dict[str, Any],
        step2_data: Dict[str, Any],
        step3_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine all steps into final CAD visualization
        
        Args:
            step1_data: Type and profile
            step2_data: Dimensions
            step3_data: Rendering details
            
        Returns:
            Complete CAD visualization JSON
        """
        # Build model3D from steps 1 and 2
        model3d = {
            "type": "extrusion" if step1_data.get('profile') else "box",
        }
        
        if step1_data.get('profile'):
            model3d["profile"] = step1_data['profile']
        
        if 'dimensions' in step2_data:
            model3d["dimensions"] = step2_data['dimensions']
        
        if 'length' in step2_data:
            model3d["length"] = step2_data['length']
        
        if 'position' in step2_data:
            model3d["position"] = step2_data['position']
        
        if 'rotation' in step2_data:
            model3d["rotation"] = step2_data['rotation']
        
        # Build complete CAD visualization
        cad_visualization = {
            "type": step1_data.get('type', 'parametric_cad'),
            "model3D": model3d,
            "camera": step3_data.get('camera', {
                "position": {"x": 1.5, "y": 1.5, "z": 1.5},
                "target": {"x": 0, "y": 0, "z": 0}
            })
        }
        
        # Add optional fields
        if step3_data.get('constraints'):
            cad_visualization["constraints"] = step3_data['constraints']
        
        if step3_data.get('include_technical_drawing'):
            cad_visualization["technical_drawing"] = {
                "content": self._generate_svg_placeholder(step2_data.get('dimensions', {})),
                "viewBox": "0 0 800 400"
            }
        
        return cad_visualization
    
    def generate_progressive(self, user_request: str) -> Dict[str, Any]:
        """
        Generate CAD visualization using progressive refinement
        
        This is the main entry point. It runs all 3 steps sequentially.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            Complete CAD visualization JSON
        """
        # Step 1: Type and profile
        step1 = self.generate_step1_type_profile(user_request)
        
        # Step 2: Dimensions
        step2 = self.generate_step2_dimensions(step1, user_request)
        
        # Step 3: Rendering
        step3 = self.generate_step3_rendering(step1, step2, user_request)
        
        # Combine into final CAD
        final_cad = self.combine_steps(step1, step2, step3)
        
        return final_cad
    
    def get_step_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all steps for debugging/review
        
        Returns:
            List of step data with prompts and responses
        """
        return self.step_history
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from AI response
        
        Handles responses that may include extra text before/after JSON.
        
        Args:
            response: AI response string
            
        Returns:
            Parsed JSON dict
        """
        # Try to find JSON in response
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start == -1 or end == 0:
            raise ValueError(f"No JSON found in response: {response}")
        
        json_str = response[start:end]
        return json.loads(json_str)
    
    def _generate_svg_placeholder(self, dimensions: Dict[str, float]) -> str:
        """
        Generate simple SVG technical drawing placeholder
        
        Args:
            dimensions: Width, height, depth in meters
            
        Returns:
            SVG string
        """
        width = dimensions.get('width', 0.02) * 1000  # Convert to mm
        height = dimensions.get('height', 0.02) * 1000
        depth = dimensions.get('depth', 0.5) * 1000
        
        return f'''<svg viewBox="0 0 800 400" width="800" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect x="100" y="100" width="{width*2}" height="{height*2}" fill="none" stroke="#333" stroke-width="2"/>
    <text x="100" y="90" font-family="Arial" font-size="12" fill="#333">{width}mm</text>
    <text x="90" y="{100 + height}" font-family="Arial" font-size="12" fill="#333">{height}mm</text>
    <text x="300" y="250" font-family="Arial" font-size="14" fill="#666">Length: {depth}mm</text>
</svg>'''


# Example usage with mock AI client
class MockAIClient:
    """Mock AI client for testing"""
    
    def chat(self, prompt: str) -> str:
        """Return mock JSON responses based on step"""
        if "Step 1" in prompt or "determine:" in prompt:
            return '''
{
    "type": "parametric_cad",
    "profile": "profile-5",
    "description": "T-slot beam for frame construction"
}
'''
        elif "Step 2" in prompt or "dimensions" in prompt:
            return '''
{
    "dimensions": {"width": 0.02, "height": 0.02, "depth": 0.02},
    "length": 0.5,
    "position": {"x": 0, "y": 0, "z": 0},
    "rotation": {"x": 0, "y": 0, "z": 0}
}
'''
        elif "Step 3" in prompt or "rendering" in prompt:
            return '''
{
    "camera": {
        "position": {"x": 1.5, "y": 1.5, "z": 1.5},
        "target": {"x": 0, "y": 0, "z": 0}
    },
    "include_technical_drawing": true,
    "constraints": {
        "accuracy": "±0.1mm",
        "material": "Aluminum 6061-T6",
        "finish": "Anodized"
    }
}
'''
        return "{}"


if __name__ == "__main__":
    # Test progressive generation
    mock_client = MockAIClient()
    generator = ProgressiveCADGenerator(mock_client)
    
    result = generator.generate_progressive("Create a 500mm T-slot beam")
    
    print("Progressive CAD Generation Result:")
    print(json.dumps(result, indent=2))
    
    print("\n\nStep History:")
    for step in generator.get_step_history():
        print(f"\nStep {step['step']}:")
        print(f"Response: {json.dumps(step['response'], indent=2)}")
