"""
Advanced User Impersonation API
Provides secure endpoints for superior accounts to access inferior accounts
"""

from flask import Flask, request, jsonify, session
from functools import wraps
import jwt
import datetime
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Supabase configuration
SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Role hierarchy for impersonation permissions
ROLE_HIERARCHY = {
    'super_admin': ['admin', 'manager', 'user'],
    'admin': ['manager', 'user'],
    'manager': ['user'],
    'user': []
}

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            request.current_user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

def can_impersonate(admin_role, target_role):
    """Check if admin can impersonate target user"""
    return target_role in ROLE_HIERARCHY.get(admin_role, [])

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Enhanced login with impersonation support"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if auth_response.user is None:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get user profile
        profile_response = supabase.table('profiles').select('*').eq('id', auth_response.user.id).single().execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User profile not found'}), 404
        
        user_data = {
            'id': auth_response.user.id,
            'email': auth_response.user.email,
            **profile_response.data
        }
        
        # Generate JWT token
        token_payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'role': user_data.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': user_data,
            'can_impersonate': len(ROLE_HIERARCHY.get(user_data.get('role', 'user'), [])) > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/impersonatable', methods=['GET'])
@require_auth
def get_impersonatable_users():
    """Get list of users that current user can impersonate"""
    try:
        current_role = request.current_user.get('role', 'user')
        impersonatable_roles = ROLE_HIERARCHY.get(current_role, [])
        
        if not impersonatable_roles:
            return jsonify({'users': []})
        
        # Get users with impersonatable roles
        users_response = supabase.table('profiles').select('*').in_('role', impersonatable_roles).execute()
        
        users = []
        for user in users_response.data:
            users.append({
                'id': user['id'],
                'email': user['email'],
                'display_name': user.get('display_name'),
                'role': user.get('role', 'user'),
                'organization_id': user.get('organization_id')
            })
        
        return jsonify({'users': users})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/impersonate', methods=['POST'])
@require_auth
def start_impersonation():
    """Start impersonating another user"""
    try:
        data = request.json
        target_user_id = data.get('target_user_id')
        
        if not target_user_id:
            return jsonify({'error': 'Target user ID required'}), 400
        
        # Get target user
        target_response = supabase.table('profiles').select('*').eq('id', target_user_id).single().execute()
        
        if not target_response.data:
            return jsonify({'error': 'Target user not found'}), 404
        
        target_user = target_response.data
        current_role = request.current_user.get('role', 'user')
        target_role = target_user.get('role', 'user')
        
        # Check permissions
        if not can_impersonate(current_role, target_role):
            return jsonify({'error': 'Insufficient permissions to impersonate this user'}), 403
        
        # Create impersonation token
        impersonation_payload = {
            'user_id': target_user['id'],
            'email': target_user['email'],
            'role': target_user.get('role', 'user'),
            'display_name': target_user.get('display_name'),
            'is_impersonating': True,
            'original_user_id': request.current_user['user_id'],
            'original_email': request.current_user['email'],
            'impersonation_start': datetime.datetime.utcnow().isoformat(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        impersonation_token = jwt.encode(impersonation_payload, app.secret_key, algorithm='HS256')
        
        # Log impersonation event
        supabase.table('impersonation_logs').insert({
            'admin_user_id': request.current_user['user_id'],
            'target_user_id': target_user['id'],
            'start_time': datetime.datetime.utcnow().isoformat(),
            'admin_email': request.current_user['email'],
            'target_email': target_user['email']
        }).execute()
        
        return jsonify({
            'impersonation_token': impersonation_token,
            'target_user': target_user,
            'original_user': {
                'id': request.current_user['user_id'],
                'email': request.current_user['email']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/exit-impersonation', methods=['POST'])
@require_auth
def exit_impersonation():
    """Exit impersonation and return to original user"""
    try:
        if not request.current_user.get('is_impersonating'):
            return jsonify({'error': 'Not currently impersonating'}), 400
        
        original_user_id = request.current_user.get('original_user_id')
        
        # Get original user data
        original_response = supabase.table('profiles').select('*').eq('id', original_user_id).single().execute()
        
        if not original_response.data:
            return jsonify({'error': 'Original user not found'}), 404
        
        original_user = original_response.data
        
        # Create new token for original user
        token_payload = {
            'user_id': original_user['id'],
            'email': original_user['email'],
            'role': original_user.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
        
        # Log end of impersonation
        supabase.table('impersonation_logs').update({
            'end_time': datetime.datetime.utcnow().isoformat()
        }).eq('admin_user_id', original_user_id).eq('target_user_id', request.current_user['user_id']).is_('end_time', 'null').execute()
        
        return jsonify({
            'token': token,
            'user': original_user
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/validate', methods=['GET'])
@require_auth
def validate_token():
    """Validate current token and return user info"""
    return jsonify({'user': request.current_user})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
