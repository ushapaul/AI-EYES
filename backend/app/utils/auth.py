"""
Authentication utilities for AI Eyes Security System
"""
import os
import functools
from flask import request, jsonify
from datetime import datetime, timedelta

# Import JWT with explicit handling
try:
    import jwt
except ImportError:
    try:
        import PyJWT as jwt
    except ImportError:
        print("Warning: JWT library not found. Authentication features will be limited.")
        jwt = None

def verify_admin_password(password):
    """Verify admin password against environment variable"""
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    return password == admin_password

def verify_api_key(api_key):
    """Verify API key against environment variable"""
    valid_api_key = os.getenv('API_KEY', 'your-secure-api-key-here')
    return api_key == valid_api_key

def generate_jwt_token(user_id, expires_hours=24):
    """Generate JWT token for authenticated user"""
    if jwt is None:
        return None
    
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_jwt_token(token):
    """Verify JWT token and return user_id if valid"""
    if jwt is None:
        return None
    
    try:
        secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication for protected endpoints"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if api_key and verify_api_key(api_key):
            return f(*args, **kwargs)
        
        # Check for JWT token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_id = verify_jwt_token(token)
            if user_id:
                # Store user_id in request context
                setattr(request, 'current_user', user_id)
                return f(*args, **kwargs)
        
        # Check for password in request body (for simple auth)
        if request.is_json and request.json:
            password = request.json.get('password')
            if password and verify_admin_password(password):
                return f(*args, **kwargs)
        
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please provide valid credentials (password, API key, or JWT token)'
        }), 401
    
    return decorated_function

def require_admin_password(f):
    """Decorator to require admin password for critical operations"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for password in request body
        if not request.is_json:
            return jsonify({
                'error': 'JSON request required',
                'message': 'Password must be provided in JSON body'
            }), 400
        
        if not request.json:
            return jsonify({
                'error': 'Empty request body',
                'message': 'Request body cannot be empty'
            }), 400
        
        password = request.json.get('password')
        if not password:
            return jsonify({
                'error': 'Password required',
                'message': 'Admin password must be provided'
            }), 401
        
        if not verify_admin_password(password):
            return jsonify({
                'error': 'Invalid password',
                'message': 'Incorrect admin password'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function