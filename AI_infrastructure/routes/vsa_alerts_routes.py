"""
VSA Veterinary Alerts API Routes
Handles transcript loading and AI coaching generation
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import requests
import os
import sys

# Create blueprint
vsa_alerts_bp = Blueprint('vsa_alerts', __name__, url_prefix='/api/vsa-alerts')

# DeepSeek API Configuration
DEEPSEEK_API_KEYS = [
    "sk-d276e3e75dfd4c20a56f32be994e7095",
    "sk-08f857560d0a4d06b87d32263bd94b6c",
    "sk-73afdf6294904542ad27ea4ab11500df",
    "sk-31d23ef70dd843488bb3144417682fb6",
    "sk-058f17e9cfc64cec8b4a488f5423d022",
    "sk-2d4d3628d06848079d48d65e7dc2c843",
    "sk-e80f2ba0077c4a6d9a6e6d604818a705",
    "sk-2b4ef1670ea54ac6a58de6d5ecaecf7b",
    "sk-add8fdc15d9a4874ad0e198ec799520d"
]
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Import database connector
try:
    from tools.Database_Data.unified_database_connector import get_unified_connector
    connector = get_unified_connector()
    supabase_client = connector.supabase_client
except Exception as e:
    print(f"Warning: Could not initialize Supabase connector: {e}", file=sys.stderr)
    supabase_client = None


@vsa_alerts_bp.route('/transcript/<call_id>', methods=['GET'])
def get_transcript(call_id):
    """
    Fetch full transcript text for a specific call
    """
    try:
        if not supabase_client:
            return jsonify({
                'success': False,
                'error': 'Database connection not available'
            }), 500
        
        # Query transcript from database
        result = supabase_client.table('call_full_transcript_and_full_analysis')\
            .select('full_transcript_text')\
            .eq('call_id', call_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            transcript_text = result.data[0].get('full_transcript_text', '')
            
            if transcript_text:
                return jsonify({
                    'success': True,
                    'transcript': transcript_text,
                    'call_id': call_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No transcript text available'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Transcript not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching transcript: {str(e)}'
        }), 500


@vsa_alerts_bp.route('/generate-coaching', methods=['POST'])
def generate_coaching():
    """
    Generate AI coaching document using DeepSeek API
    """
    try:
        data = request.json
        call_id = data.get('call_id')
        
        if not call_id:
            return jsonify({
                'success': False,
                'error': 'call_id is required'
            }), 400
        
        if not supabase_client:
            return jsonify({
                'success': False,
                'error': 'Database connection not available'
            }), 500
        
        # 1. Fetch transcript and analysis from database
        transcript_result = supabase_client.table('call_full_transcript_and_full_analysis')\
            .select('full_transcript_text, full_analysis_text')\
            .eq('call_id', call_id)\
            .execute()
        
        if not transcript_result.data or len(transcript_result.data) == 0:
            return jsonify({
                'success': False,
                'error': 'Transcript not found for this call'
            }), 404
        
        transcript_text = transcript_result.data[0].get('full_transcript_text', '')
        full_analysis = transcript_result.data[0].get('full_analysis_text', '')
        
        if not transcript_text:
            return jsonify({
                'success': False,
                'error': 'No transcript text available'
            }), 404
        
        # 2. Fetch alert information from call_manager_alerts
        alert_result = supabase_client.table('call_manager_alerts')\
            .select('*')\
            .eq('call_id', call_id)\
            .execute()
        
        alert_info = {}
        if alert_result.data and len(alert_result.data) > 0:
            alert_data = alert_result.data[0]
            alert_info = {
                'severity': alert_data.get('alert_1_severity', 'MED'),
                'alert_code': alert_data.get('alert_1_code', 'GENERAL'),
                'core_reason': alert_data.get('alert_1_core_reason', 'Multiple areas flagged'),
                'triggers_met': alert_data.get('alert_1_triggers_met', ''),
                'key_metrics': alert_data.get('alert_1_key_metrics', ''),
                'evidence': alert_data.get('alert_1_evidence', ''),
                'risk_if_ignored': alert_data.get('alert_1_risk_if_ignored', ''),
                'coaching_focus': alert_data.get('alert_1_coaching_focus', '')
            }
        
        # 3. Generate coaching document using DeepSeek
        coaching_result = _generate_ai_coaching_document(
            call_id, 
            transcript_text, 
            full_analysis, 
            alert_info
        )
        
        if not coaching_result['success']:
            return jsonify(coaching_result), 500
        
        # 4. Save coaching document to database
        coaching_content = coaching_result['content']
        current_time = datetime.now().isoformat()
        
        update_result = supabase_client.table('call_manager_alerts')\
            .update({
                'ai_coaching_support': coaching_content,
                'ai_coaching_generated_date': current_time
            })\
            .eq('call_id', call_id)\
            .execute()
        
        if not update_result.data:
            return jsonify({
                'success': False,
                'error': 'Failed to save coaching document'
            }), 500
        
        # 5. Return success with coaching content
        return jsonify({
            'success': True,
            'coaching': coaching_content,
            'generated_date': current_time,
            'usage': coaching_result.get('usage', {}),
            'call_id': call_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating coaching: {str(e)}'
        }), 500


def _generate_ai_coaching_document(call_id: str, transcript_text: str, full_analysis: str, alert_info: dict) -> dict:
    """
    Internal function to generate AI coaching document using DeepSeek API
    Copied from SQL_Data_AI_UI_v5/tools/Dashboard_Actions/alert_v4_tiered.py
    """
    try:
        if not DEEPSEEK_API_KEYS:
            return {'success': False, 'error': 'No DeepSeek API keys available', 'content': ''}
        
        # Use first available API key (implement rotation if needed)
        api_key = DEEPSEEK_API_KEYS[0]
        
        # Build coaching prompt (comprehensive version from original)
        coaching_prompt = f"""You are an expert veterinary practice management consultant and clinical communication coach. 

Generate comprehensive, growth-oriented coaching documents for veterinary team members based on call transcripts and analysis. These documents should build awareness of psychological principles that influence clinical communication decisions and provide practical strategies for delivering better patient care and client service.

CRITICAL FORMATTING RULES:
1. Use ONLY these heading formats (no other variations):
   - ## HEADING (for major sections)
   - ### Sub-Heading (for subsections)
   - #### Detail Point (for specific items)

2. Use ONLY these list formats:
   - **Bold Label:** Description text
   - • Bullet point text
   - 1. Numbered list item

3. NO fancy boxes, NO borders, NO === dividers
4. NO 📋 ✓ ▸ ► fancy symbols except basic emoji 🎯 📊 💡 ⚠️
5. Use simple markdown: **bold**, *italic*, `code`
6. Use horizontal rules (---) to separate major sections

## COACHING FRAMEWORK

Your coaching document should:
1. Start with recognition of strengths
2. Identify growth opportunities using behavioral psychology
3. Provide specific, actionable strategies
4. Include example scripts and techniques
5. Connect actions to business outcomes
6. End with encouragement and support

## ANALYSIS STRUCTURE

### CALL OVERVIEW
Provide context:
- Call type and purpose
- Client relationship stage
- Patient condition/needs
- Call outcome

### STRENGTHS & POSITIVE OBSERVATIONS
Recognize effective behaviors:
- Strong rapport-building moments
- Clinical knowledge demonstrated
- Professional handling of challenges
- Client-centered approaches

### GROWTH OPPORTUNITIES
Frame as development areas (not criticisms):
- Communication patterns to enhance
- Clinical presentation improvements
- Client education opportunities
- Relationship-building moments

### PSYCHOLOGICAL INSIGHTS
Explain the "why" behind recommendations:
- Cognitive biases affecting decisions
- Emotional intelligence applications
- Behavioral triggers and responses
- Trust-building mechanisms

### ACTION PLAN
Provide specific, implementable strategies:
1. Immediate actions (this week)
2. Short-term focus (this month)
3. Long-term development (ongoing)

### EXAMPLE SCRIPTS & TECHNIQUES
Give concrete examples:
- Reframe phrases for better outcomes
- Questions that uncover client needs
- Techniques for handling objections
- Ways to present recommendations

### EXPECTED OUTCOMES
Connect actions to results:
- Clinical quality improvements
- Client satisfaction impacts
- Revenue/booking effects
- Team efficiency gains

## TONE & STYLE GUIDELINES
- Supportive and constructive
- Specific and evidence-based
- Action-oriented and practical
- Professional yet warm
- Growth-focused (not punitive)

Generate the coaching document now."""

        # Build analysis context
        analysis_context = f"""# CALL INFORMATION
- Call ID: {call_id}
- Alert Severity: {alert_info.get('severity', 'Not specified')}
- Primary Alert: {alert_info.get('alert_code', 'Not specified')}

# ALERT DETAILS
- Core Reason: {alert_info.get('core_reason', 'Not specified')}
- Triggers Met: {alert_info.get('triggers_met', 'Not specified')}
- Key Metrics: {alert_info.get('key_metrics', 'Not specified')}
- Evidence: {alert_info.get('evidence', 'Not specified')}
- Risk If Ignored: {alert_info.get('risk_if_ignored', 'Not specified')}
- Current Coaching Focus: {alert_info.get('coaching_focus', 'Not specified')}

# FULL ANALYSIS
{full_analysis}

# CALL TRANSCRIPT
{transcript_text}

Please generate the coaching document now."""

        # Make API call to DeepSeek
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": coaching_prompt},
                {"role": "user", "content": analysis_context}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f"DeepSeek API error {response.status_code}: {response.text}",
                'content': ''
            }
        
        data = response.json()
        coaching_content = data["choices"][0]["message"]["content"]
        
        return {
            'success': True,
            'content': coaching_content,
            'error': '',
            'usage': data.get('usage', {})
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error generating coaching document: {str(e)}",
            'content': ''
        }


@vsa_alerts_bp.route('/coaching/<call_id>', methods=['GET'])
def get_coaching(call_id):
    """
    Fetch existing AI coaching document for a specific call
    """
    try:
        if not supabase_client:
            return jsonify({
                'success': False,
                'error': 'Database connection not available'
            }), 500
        
        # Query coaching from database
        result = supabase_client.table('call_manager_alerts')\
            .select('ai_coaching_support, ai_coaching_generated_date')\
            .eq('call_id', call_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            coaching_content = result.data[0].get('ai_coaching_support', '')
            coaching_date = result.data[0].get('ai_coaching_generated_date', '')
            
            if coaching_content:
                return jsonify({
                    'success': True,
                    'coaching': coaching_content,
                    'generated_date': coaching_date,
                    'call_id': call_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No coaching document available'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Call not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching coaching: {str(e)}'
        }), 500


@vsa_alerts_bp.route('/coaching/<call_id>', methods=['DELETE'])
def delete_coaching(call_id):
    """
    Delete AI coaching document for a specific call
    """
    try:
        if not supabase_client:
            return jsonify({
                'success': False,
                'error': 'Database connection not available'
            }), 500
        
        # Delete coaching from database
        result = supabase_client.table('call_manager_alerts')\
            .update({
                'ai_coaching_support': None,
                'ai_coaching_generated_date': None
            })\
            .eq('call_id', call_id)\
            .execute()
        
        if result.data:
            return jsonify({
                'success': True,
                'message': 'Coaching document deleted successfully',
                'call_id': call_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete coaching document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error deleting coaching: {str(e)}'
        }), 500
