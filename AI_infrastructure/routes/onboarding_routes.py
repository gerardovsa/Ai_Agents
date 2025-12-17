"""
FILE: AI_infrastructure/routes/onboarding_routes.py
PURPOSE: API endpoints for user onboarding and training progress tracking

DEPENDENCIES:
- flask - Web framework
- AI_infrastructure.auth.user_auth - Authentication
- AI_infrastructure.shared.database_utils - Database connections

EXPORTS:
- GET /api/onboarding/status - Get user's onboarding progress
- POST /api/onboarding/complete-fre - Mark FRE as completed
- POST /api/onboarding/complete-step - Mark checklist step as completed
- POST /api/onboarding/complete-tour - Mark tour as completed
- POST /api/onboarding/complete-module - Mark learning module as completed
- POST /api/onboarding/dismiss - Dismiss onboarding checklist
- POST /api/onboarding/activate-user - Mark user as activated
- GET /api/onboarding/analytics - Get onboarding analytics (admin only)

NOTES:
- All endpoints require authentication
- Uses PostgreSQL ai_infrastructure.user_training table
- Returns JSON responses
- Includes analytics tracking

LAST MODIFIED: 2025-11-29 - Initial creation
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

# Import authentication
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth.user_auth import UserAuthManager, require_auth
from shared.database_utils import get_database_connection

# Create Blueprint
onboarding_bp = Blueprint('onboarding', __name__)
auth_manager = UserAuthManager()


def get_user_training(user_id: int):
    """
    Get user training record from database
    
    Args:
        user_id: User ID
    
    Returns:
        dict: User training data or None if not found
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, fre_completed, fre_completed_at, fre_skipped,
                   completed_steps, total_xp, tours_completed, completed_modules,
                   proficiency_level, proficiency_xp, is_activated, activated_at,
                   activation_method, time_to_activation_seconds, help_panel_views,
                   contextual_help_clicks, video_tutorials_watched, unlocked_badges,
                   onboarding_dismissed, checklist_collapsed, created_at, updated_at,
                   last_interaction_at, metadata
            FROM ai_infrastructure.user_training
            WHERE user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'user_id': row[1],
            'fre_completed': row[2],
            'fre_completed_at': row[3].isoformat() if row[3] else None,
            'fre_skipped': row[4],
            'completed_steps': row[5] if row[5] else [],
            'total_xp': row[6],
            'tours_completed': row[7] if row[7] else {},
            'completed_modules': row[8] if row[8] else [],
            'proficiency_level': row[9],
            'proficiency_xp': row[10],
            'is_activated': row[11],
            'activated_at': row[12].isoformat() if row[12] else None,
            'activation_method': row[13],
            'time_to_activation_seconds': row[14],
            'help_panel_views': row[15],
            'contextual_help_clicks': row[16],
            'video_tutorials_watched': row[17] if row[17] else [],
            'unlocked_badges': row[18] if row[18] else [],
            'onboarding_dismissed': row[19],
            'checklist_collapsed': row[20],
            'created_at': row[21].isoformat() if row[21] else None,
            'updated_at': row[22].isoformat() if row[22] else None,
            'last_interaction_at': row[23].isoformat() if row[23] else None,
            'metadata': row[24] if row[24] else {}
        }
    finally:
        cursor.close()
        conn.close()


def create_user_training(user_id: int):
    """
    Create user training record if it doesn't exist
    
    Args:
        user_id: User ID
    
    Returns:
        dict: Created user training data
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ai_infrastructure.user_training (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING id
        """, (user_id,))
        
        conn.commit()
        
        # Fetch and return the record
        return get_user_training(user_id)
    finally:
        cursor.close()
        conn.close()


@onboarding_bp.route('/api/onboarding/status', methods=['GET'])
@require_auth
def get_onboarding_status():
    """
    Get user's onboarding progress
    
    Returns:
        JSON: User training data
    """
    try:
        user_id = request.user_id
        
        # Get or create training record
        training = get_user_training(user_id)
        if not training:
            training = create_user_training(user_id)
        
        return jsonify({
            'success': True,
            'data': training
        }), 200
    
    except Exception as e:
        print(f"❌ [Onboarding] Error getting status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/complete-fre', methods=['POST'])
@require_auth
def complete_fre():
    """
    Mark First-Run Experience as completed
    
    Body:
        skipped (bool): Whether user skipped FRE
    
    Returns:
        JSON: Success status
    """
    try:
        user_id = request.user_id
        data = request.get_json() or {}
        skipped = data.get('skipped', False)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE ai_infrastructure.user_training
                SET fre_completed = TRUE,
                    fre_completed_at = NOW(),
                    fre_skipped = %s,
                    last_interaction_at = NOW()
                WHERE user_id = %s
            """, (skipped, user_id))
            
            conn.commit()
            
            print(f"✅ [Onboarding] FRE completed for user {user_id} (skipped: {skipped})")
            
            return jsonify({
                'success': True,
                'message': 'FRE marked as completed'
            }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error completing FRE: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/complete-step', methods=['POST'])
@require_auth
def complete_step():
    """
    Mark onboarding checklist step as completed
    
    Body:
        step_id (str): Step ID (e.g., 'create_thread')
        xp (int): XP to award
    
    Returns:
        JSON: Updated progress
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        step_id = data.get('step_id')
        xp = data.get('xp', 0)
        
        if not step_id:
            return jsonify({
                'success': False,
                'error': 'step_id is required'
            }), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            # Get current steps
            cursor.execute("""
                SELECT completed_steps, total_xp
                FROM ai_infrastructure.user_training
                WHERE user_id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'User training record not found'
                }), 404
            
            completed_steps = row[0] if row[0] else []
            current_xp = row[1] or 0
            
            # Add step if not already completed
            if step_id not in completed_steps:
                completed_steps.append(step_id)
                new_xp = current_xp + xp
                
                cursor.execute("""
                    UPDATE ai_infrastructure.user_training
                    SET completed_steps = %s,
                        total_xp = %s,
                        proficiency_xp = proficiency_xp + %s,
                        last_interaction_at = NOW()
                    WHERE user_id = %s
                """, (json.dumps(completed_steps), new_xp, xp, user_id))
                
                conn.commit()
                
                print(f"✅ [Onboarding] Step '{step_id}' completed for user {user_id} (+{xp} XP)")
                
                return jsonify({
                    'success': True,
                    'message': f'Step completed (+{xp} XP)',
                    'completed_steps': completed_steps,
                    'total_xp': new_xp
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'Step already completed',
                    'completed_steps': completed_steps,
                    'total_xp': current_xp
                }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error completing step: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/complete-tour', methods=['POST'])
@require_auth
def complete_tour():
    """
    Mark tour as completed
    
    Body:
        tour_id (str): Tour ID (e.g., 'basics', 'multiAgent')
    
    Returns:
        JSON: Success status
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        tour_id = data.get('tour_id')
        
        if not tour_id:
            return jsonify({
                'success': False,
                'error': 'tour_id is required'
            }), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            # Get current tours
            cursor.execute("""
                SELECT tours_completed
                FROM ai_infrastructure.user_training
                WHERE user_id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'User training record not found'
                }), 404
            
            tours_completed = row[0] if row[0] else {}
            
            # Mark tour as completed
            tours_completed[tour_id] = True
            
            cursor.execute("""
                UPDATE ai_infrastructure.user_training
                SET tours_completed = %s,
                    last_interaction_at = NOW()
                WHERE user_id = %s
            """, (json.dumps(tours_completed), user_id))
            
            conn.commit()
            
            print(f"✅ [Onboarding] Tour '{tour_id}' completed for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': f'Tour {tour_id} completed',
                'tours_completed': tours_completed
            }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error completing tour: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/complete-module', methods=['POST'])
@require_auth
def complete_module():
    """
    Mark learning module as completed
    
    Body:
        module_id (str): Module ID
        score (int): Quiz score (0-100)
    
    Returns:
        JSON: Success status
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        module_id = data.get('module_id')
        score = data.get('score', 0)
        
        if not module_id:
            return jsonify({
                'success': False,
                'error': 'module_id is required'
            }), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            # Get current modules
            cursor.execute("""
                SELECT completed_modules
                FROM ai_infrastructure.user_training
                WHERE user_id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'User training record not found'
                }), 404
            
            completed_modules = row[0] if row[0] else []
            
            # Add module if not already completed
            if module_id not in completed_modules:
                completed_modules.append(module_id)
                
                cursor.execute("""
                    UPDATE ai_infrastructure.user_training
                    SET completed_modules = %s,
                        last_interaction_at = NOW()
                    WHERE user_id = %s
                """, (json.dumps(completed_modules), user_id))
                
                conn.commit()
                
                print(f"✅ [Onboarding] Module '{module_id}' completed for user {user_id} (score: {score})")
                
                return jsonify({
                    'success': True,
                    'message': f'Module completed (score: {score}%)',
                    'completed_modules': completed_modules
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'Module already completed',
                    'completed_modules': completed_modules
                }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error completing module: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/dismiss', methods=['POST'])
@require_auth
def dismiss_onboarding():
    """
    Dismiss onboarding checklist
    
    Returns:
        JSON: Success status
    """
    try:
        user_id = request.user_id
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE ai_infrastructure.user_training
                SET onboarding_dismissed = TRUE,
                    last_interaction_at = NOW()
                WHERE user_id = %s
            """, (user_id,))
            
            conn.commit()
            
            print(f"✅ [Onboarding] Checklist dismissed for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Onboarding dismissed'
            }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error dismissing: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/activate-user', methods=['POST'])
@require_auth
def activate_user():
    """
    Mark user as activated (completed first meaningful action)
    
    Body:
        activation_method (str): How user activated ('checklist_completed', 'tour_completed', 'manual')
    
    Returns:
        JSON: Success status
    """
    try:
        user_id = request.user_id
        data = request.get_json() or {}
        activation_method = data.get('activation_method', 'manual')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            # Get user creation time to calculate time to activation
            cursor.execute("""
                SELECT u.created_at, ut.created_at
                FROM ai_infrastructure.users u
                LEFT JOIN ai_infrastructure.user_training ut ON u.id = ut.user_id
                WHERE u.id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            user_created_at = row[0]
            training_created_at = row[1]
            
            # Calculate time to activation (use earliest timestamp)
            start_time = training_created_at if training_created_at else user_created_at
            time_to_activation = int((datetime.now() - start_time).total_seconds())
            
            # Mark as activated
            cursor.execute("""
                UPDATE ai_infrastructure.user_training
                SET is_activated = TRUE,
                    activated_at = NOW(),
                    activation_method = %s,
                    time_to_activation_seconds = %s,
                    last_interaction_at = NOW()
                WHERE user_id = %s
            """, (activation_method, time_to_activation, user_id))
            
            conn.commit()
            
            print(f"🎉 [Onboarding] User {user_id} activated! Method: {activation_method}, Time: {time_to_activation}s")
            
            return jsonify({
                'success': True,
                'message': 'User activated',
                'time_to_activation_seconds': time_to_activation
            }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error activating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/analytics', methods=['GET'])
@require_auth
def get_analytics():
    """
    Get onboarding analytics (admin only)
    
    Returns:
        JSON: Analytics data
    """
    try:
        user_id = request.user_id
        
        # Check if user is admin
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT role FROM ai_infrastructure.users WHERE id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row or row[0] != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Admin access required'
                }), 403
            
            # Get analytics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE fre_completed = TRUE) as fre_completed_count,
                    COUNT(*) FILTER (WHERE fre_skipped = TRUE) as fre_skipped_count,
                    COUNT(*) FILTER (WHERE is_activated = TRUE) as activated_count,
                    AVG(time_to_activation_seconds) as avg_activation_time,
                    COUNT(*) FILTER (WHERE jsonb_array_length(completed_steps) >= 5) as checklist_completed_count,
                    AVG(total_xp) as avg_xp,
                    AVG(proficiency_xp) as avg_proficiency_xp
                FROM ai_infrastructure.user_training
            """)
            
            row = cursor.fetchone()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_users': row[0] or 0,
                    'fre_completed_count': row[1] or 0,
                    'fre_skipped_count': row[2] or 0,
                    'activated_count': row[3] or 0,
                    'avg_activation_time_seconds': float(row[4]) if row[4] else 0,
                    'checklist_completed_count': row[5] or 0,
                    'avg_xp': float(row[6]) if row[6] else 0,
                    'avg_proficiency_xp': float(row[7]) if row[7] else 0,
                    'activation_rate': round((row[3] / row[0] * 100) if row[0] > 0 else 0, 2)
                }
            }), 200
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        print(f"❌ [Onboarding] Error getting analytics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Export blueprint
def register_routes(app):
    """Register onboarding routes with Flask app"""
    app.register_blueprint(onboarding_bp)
    print("✅ Onboarding routes registered")
