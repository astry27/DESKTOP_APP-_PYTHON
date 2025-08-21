# Path: api/routes/server_management.py

from flask import Blueprint, request, jsonify, current_app
import jwt
import requests
import logging
from functools import wraps
from datetime import datetime

from models.server_registry import ServerRegistry
from models.user_session import UserSession
from models.api_log import ApiLog

server_bp = Blueprint('server', __name__)
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            session_record = UserSession.query.filter_by(
                user_id=current_user_id,
                token=token,
                is_active=True
            ).first()
            
            if not session_record:
                return jsonify({'message': 'Token invalid or expired'}), 401
                
            session_record.last_activity = datetime.utcnow()
            from models.user_session import db
            db.session.commit()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

@server_bp.route('/start', methods=['POST'])
@token_required
def start_server(current_user_id):
    """Start server melalui API"""
    try:
        data = request.get_json()
        
        required_fields = ['server_host', 'server_port']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} required'}), 400
        
        server_host = data['server_host']
        server_port = data['server_port']
        
        # Cek apakah server terdaftar
        server = ServerRegistry.query.filter_by(
            host=server_host,
            port=server_port
        ).first()
        
        if not server:
            return jsonify({'error': 'Server not registered'}), 404
        
        # Coba start server
        server_url = f"http://{server_host}:{server_port}/api/server/start"
        
        try:
            response = requests.post(server_url, json=data.get('config', {}), timeout=30)
            
            if response.status_code == 200:
                # Update status server
                server.status = 'online'
                server.last_ping = datetime.utcnow()
                from models.server_registry import db
                db.session.commit()
                
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='START_SERVER',
                    details=f'Server {server.server_name} started successfully',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Server started successfully',
                    'server_info': server.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to start server',
                    'details': response.text
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': 'Cannot connect to server'
            }), 503
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Server start timeout'
            }), 408
            
    except Exception as e:
        logger.error(f"Start server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@server_bp.route('/stop', methods=['POST'])
@token_required
def stop_server(current_user_id):
    """Stop server melalui API"""
    try:
        data = request.get_json()
        
        required_fields = ['server_host', 'server_port']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} required'}), 400
        
        server_host = data['server_host']
        server_port = data['server_port']
        
        # Cek apakah server terdaftar
        server = ServerRegistry.query.filter_by(
            host=server_host,
            port=server_port
        ).first()
        
        if not server:
            return jsonify({'error': 'Server not registered'}), 404
        
        # Coba stop server
        server_url = f"http://{server_host}:{server_port}/api/server/stop"
        
        try:
            response = requests.post(server_url, timeout=30)
            
            if response.status_code == 200:
                # Update status server
                server.status = 'offline'
                from models.server_registry import db
                db.session.commit()
                
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='STOP_SERVER',
                    details=f'Server {server.server_name} stopped successfully',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Server stopped successfully',
                    'server_info': server.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to stop server',
                    'details': response.text
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            # Server mungkin sudah mati, set status offline
            server.status = 'offline'
            from models.server_registry import db
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Server is already offline',
                'server_info': server.to_dict()
            })
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Server stop timeout'
            }), 408
            
    except Exception as e:
        logger.error(f"Stop server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@server_bp.route('/status', methods=['GET'])
@token_required
def get_server_status(current_user_id):
    """Get status server"""
    try:
        server_host = request.args.get('host')
        server_port = request.args.get('port')
        
        if not server_host or not server_port:
            return jsonify({'error': 'Host and port required'}), 400
        
        # Cek apakah server terdaftar
        server = ServerRegistry.query.filter_by(
            host=server_host,
            port=int(server_port)
        ).first()
        
        if not server:
            return jsonify({'error': 'Server not registered'}), 404
        
        # Coba ping server untuk status terkini
        server_url = f"http://{server_host}:{server_port}/api/health"
        
        try:
            response = requests.get(server_url, timeout=10)
            
            if response.status_code == 200:
                server.status = 'online'
                server.last_ping = datetime.utcnow()
                server_data = response.json()
            else:
                server.status = 'offline'
                server_data = None
                
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            server.status = 'offline'
            server_data = None
        
        from models.server_registry import db
        db.session.commit()
        
        return jsonify({
            'server_info': server.to_dict(),
            'server_data': server_data,
            'is_online': server.is_online()
        })
        
    except Exception as e:
        logger.error(f"Get server status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@server_bp.route('/restart', methods=['POST'])
@token_required
def restart_server(current_user_id):
    """Restart server melalui API"""
    try:
        data = request.get_json()
        
        required_fields = ['server_host', 'server_port']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} required'}), 400
        
        server_host = data['server_host']
        server_port = data['server_port']
        
        # Cek apakah server terdaftar
        server = ServerRegistry.query.filter_by(
            host=server_host,
            port=server_port
        ).first()
        
        if not server:
            return jsonify({'error': 'Server not registered'}), 404
        
        # Coba restart server
        server_url = f"http://{server_host}:{server_port}/api/server/restart"
        
        try:
            response = requests.post(server_url, json=data.get('config', {}), timeout=60)
            
            if response.status_code == 200:
                # Update status server
                server.status = 'online'
                server.last_ping = datetime.utcnow()
                from models.server_registry import db
                db.session.commit()
                
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='RESTART_SERVER',
                    details=f'Server {server.server_name} restarted successfully',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Server restarted successfully',
                    'server_info': server.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to restart server',
                    'details': response.text
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': 'Cannot connect to server'
            }), 503
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Server restart timeout'
            }), 408
            
    except Exception as e:
        logger.error(f"Restart server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@server_bp.route('/config', methods=['GET', 'POST'])
@token_required
def server_config(current_user_id):
    """Get atau set konfigurasi server"""
    try:
        server_host = request.args.get('host') or request.json.get('server_host')
        server_port = request.args.get('port') or request.json.get('server_port')
        
        if not server_host or not server_port:
            return jsonify({'error': 'Host and port required'}), 400
        
        server = ServerRegistry.query.filter_by(
            host=server_host,
            port=int(server_port)
        ).first()
        
        if not server:
            return jsonify({'error': 'Server not registered'}), 404
        
        if request.method == 'GET':
            # Get config dari server
            server_url = f"http://{server_host}:{server_port}/api/config"
            
            try:
                response = requests.get(server_url, timeout=10)
                
                if response.status_code == 200:
                    return jsonify({
                        'success': True,
                        'config': response.json()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to get server config'
                    }), response.status_code
                    
            except requests.exceptions.ConnectionError:
                return jsonify({'error': 'Cannot connect to server'}), 503
                
        elif request.method == 'POST':
            # Set config ke server
            data = request.get_json()
            config_data = data.get('config', {})
            
            server_url = f"http://{server_host}:{server_port}/api/config"
            
            try:
                response = requests.post(server_url, json=config_data, timeout=30)
                
                if response.status_code == 200:
                    # Log activity
                    ApiLog.log_activity(
                        user_id=current_user_id,
                        action='UPDATE_SERVER_CONFIG',
                        details=f'Server {server.server_name} config updated',
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', ''),
                        endpoint=request.endpoint,
                        method=request.method,
                        status_code=200
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': 'Server config updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update server config'
                    }), response.status_code
                    
            except requests.exceptions.ConnectionError:
                return jsonify({'error': 'Cannot connect to server'}), 503
                
    except Exception as e:
        logger.error(f"Server config error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500