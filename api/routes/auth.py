# Path: api/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime, timedelta
import requests
import logging

from models.user_session import UserSession
from models.api_log import ApiLog

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - authenticate dengan server lokal"""
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['username', 'password', 'server_host', 'server_port']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} required'}), 400
        
        username = data['username']
        password = data['password']
        server_host = data['server_host']
        server_port = data['server_port']
        
        # Coba authenticate ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/auth/login"
        
        try:
            response = requests.post(server_url, json={
                'username': username,
                'password': password
            }, timeout=10)
            
            if response.status_code == 200:
                server_data = response.json()
                user_data = server_data.get('user', {})
                
                # Generate JWT token untuk API
                token_payload = {
                    'user_id': user_data.get('id', 0),
                    'username': username,
                    'server_host': server_host,
                    'server_port': server_port,
                    'exp': datetime.utcnow() + timedelta(hours=24),
                    'iat': datetime.utcnow()
                }
                
                token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
                
                # Simpan session
                session = UserSession.create_session(
                    user_id=user_data.get('id', 0),
                    token=token,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    device_info=f"Client-{server_host}:{server_port}"
                )
                
                # Log activity
                ApiLog.log_activity(
                    user_id=user_data.get('id', 0),
                    action='LOGIN',
                    details=f'User {username} logged in via server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user_data.get('id'),
                        'username': username,
                        'nama_lengkap': user_data.get('nama_lengkap'),
                        'peran': user_data.get('peran')
                    },
                    'server_info': {
                        'host': server_host,
                        'port': server_port
                    },
                    'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
                })
            
            else:
                # Log failed attempt
                ApiLog.log_activity(
                    user_id=None,
                    action='LOGIN_FAILED',
                    details=f'Failed login attempt for {username} via {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=401,
                    level='WARNING'
                )
                
                return jsonify({
                    'success': False,
                    'error': 'Invalid credentials'
                }), 401
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': 'Cannot connect to server. Please check server address and ensure server is running.'
            }), 503
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Connection timeout. Server might be overloaded.'
            }), 408
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        # Decode token to get user info
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            
            # Invalidate session
            session = UserSession.query.filter_by(
                user_id=user_id,
                token=token,
                is_active=True
            ).first()
            
            if session:
                session.invalidate()
                from models.user_session import db
                db.session.commit()
            
            # Log activity
            ApiLog.log_activity(
                user_id=user_id,
                action='LOGOUT',
                details=f'User {data.get("username")} logged out',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                endpoint=request.endpoint,
                method=request.method,
                status_code=200
            )
            
            return jsonify({
                'success': True,
                'message': 'Logout successful'
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalid'}), 401
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify token validity"""
    try:
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'valid': False, 'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            
            # Check session validity
            session = UserSession.query.filter_by(
                user_id=user_id,
                token=token,
                is_active=True
            ).first()
            
            if not session or session.is_expired():
                return jsonify({'valid': False, 'error': 'Session expired'}), 401
            
            # Update last activity
            session.update_activity()
            from models.user_session import db
            db.session.commit()
            
            return jsonify({
                'valid': True,
                'user': {
                    'id': data['user_id'],
                    'username': data['username']
                },
                'server_info': {
                    'host': data.get('server_host'),
                    'port': data.get('server_port')
                },
                'expires_at': session.expires_at.isoformat()
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({'valid': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'valid': False, 'error': 'Token invalid'}), 401
            
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'valid': False, 'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
    try:
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # Decode token (allow expired for refresh)
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], options={"verify_exp": False})
            user_id = data['user_id']
            
            # Check if session exists and is active
            session = UserSession.query.filter_by(
                user_id=user_id,
                token=token,
                is_active=True
            ).first()
            
            if not session:
                return jsonify({'error': 'Session not found'}), 401
            
            # Generate new token
            new_token_payload = {
                'user_id': data['user_id'],
                'username': data['username'],
                'server_host': data.get('server_host'),
                'server_port': data.get('server_port'),
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            new_token = jwt.encode(new_token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            # Update session with new token
            session.token = new_token
            session.extend_session(24)
            from models.user_session import db
            db.session.commit()
            
            # Log activity
            ApiLog.log_activity(
                user_id=user_id,
                action='TOKEN_REFRESH',
                details=f'Token refreshed for user {data.get("username")}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                endpoint=request.endpoint,
                method=request.method,
                status_code=200
            )
            
            return jsonify({
                'success': True,
                'token': new_token,
                'expires_at': session.expires_at.isoformat()
            })
            
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalid'}), 401
            
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/sessions', methods=['GET'])
def get_user_sessions():
    """Get user's active sessions"""
    try:
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            
            # Get user sessions
            sessions = UserSession.get_user_sessions(user_id, active_only=True)
            
            sessions_data = []
            for session in sessions:
                sessions_data.append({
                    'id': session.id,
                    'ip_address': session.ip_address,
                    'device_info': session.device_info,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'expires_at': session.expires_at.isoformat(),
                    'is_current': session.token == token
                })
            
            return jsonify({
                'sessions': sessions_data,
                'total': len(sessions_data)
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalid'}), 401
            
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500