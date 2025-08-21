# Path: api/routes/data_access.py

from flask import Blueprint, request, jsonify, current_app
import jwt
import requests
import logging
from functools import wraps
from datetime import datetime

from models.server_registry import ServerRegistry
from models.user_session import UserSession
from models.api_log import ApiLog

data_bp = Blueprint('data', __name__)
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
            server_host = data.get('server_host')
            server_port = data.get('server_port')
            
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
        
        return f(current_user_id, server_host, server_port, *args, **kwargs)
    
    return decorated

@data_bp.route('/jemaat', methods=['GET'])
@token_required
def get_jemaat(current_user_id, server_host, server_port):
    """Get data jemaat dari server"""
    try:
        # Build query parameters
        params = {}
        if 'limit' in request.args:
            params['limit'] = request.args.get('limit')
        if 'offset' in request.args:
            params['offset'] = request.args.get('offset')
        if 'search' in request.args:
            params['search'] = request.args.get('search')
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/jemaat"
        
        try:
            response = requests.get(server_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='GET_JEMAAT',
                    details=f'Retrieved jemaat data from server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get jemaat data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Get jemaat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/jemaat', methods=['POST'])
@token_required
def add_jemaat(current_user_id, server_host, server_port):
    """Tambah data jemaat ke server"""
    try:
        data = request.get_json()
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/jemaat"
        
        try:
            response = requests.post(server_url, json=data, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='ADD_JEMAAT',
                    details=f'Added jemaat {data.get("nama_lengkap", "Unknown")} to server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=response.status_code
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to add jemaat data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Add jemaat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/jemaat/<int:jemaat_id>', methods=['PUT'])
@token_required
def update_jemaat(current_user_id, server_host, server_port, jemaat_id):
    """Update data jemaat di server"""
    try:
        data = request.get_json()
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/jemaat/{jemaat_id}"
        
        try:
            response = requests.put(server_url, json=data, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='UPDATE_JEMAAT',
                    details=f'Updated jemaat ID {jemaat_id} in server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update jemaat data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Update jemaat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/kegiatan', methods=['GET'])
@token_required
def get_kegiatan(current_user_id, server_host, server_port):
    """Get data kegiatan dari server"""
    try:
        # Build query parameters
        params = {}
        if 'limit' in request.args:
            params['limit'] = request.args.get('limit')
        if 'offset' in request.args:
            params['offset'] = request.args.get('offset')
        if 'start_date' in request.args:
            params['start_date'] = request.args.get('start_date')
        if 'end_date' in request.args:
            params['end_date'] = request.args.get('end_date')
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/kegiatan"
        
        try:
            response = requests.get(server_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='GET_KEGIATAN',
                    details=f'Retrieved kegiatan data from server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get kegiatan data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Get kegiatan error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/kegiatan', methods=['POST'])
@token_required
def add_kegiatan(current_user_id, server_host, server_port):
    """Tambah data kegiatan ke server"""
    try:
        data = request.get_json()
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/kegiatan"
        
        try:
            response = requests.post(server_url, json=data, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='ADD_KEGIATAN',
                    details=f'Added kegiatan {data.get("nama_kegiatan", "Unknown")} to server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=response.status_code
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to add kegiatan data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Add kegiatan error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/pengumuman', methods=['GET'])
@token_required
def get_pengumuman(current_user_id, server_host, server_port):
    """Get data pengumuman dari server"""
    try:
        # Build query parameters
        params = {}
        if 'limit' in request.args:
            params['limit'] = request.args.get('limit')
        if 'offset' in request.args:
            params['offset'] = request.args.get('offset')
        if 'active_only' in request.args:
            params['active_only'] = request.args.get('active_only')
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/pengumuman"
        
        try:
            response = requests.get(server_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='GET_PENGUMUMAN',
                    details=f'Retrieved pengumuman data from server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get pengumuman data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Get pengumuman error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/keuangan', methods=['GET'])
@token_required
def get_keuangan(current_user_id, server_host, server_port):
    """Get data keuangan dari server"""
    try:
        # Build query parameters
        params = {}
        if 'limit' in request.args:
            params['limit'] = request.args.get('limit')
        if 'offset' in request.args:
            params['offset'] = request.args.get('offset')
        if 'category' in request.args:
            params['category'] = request.args.get('category')
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/keuangan"
        
        try:
            response = requests.get(server_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='GET_KEUANGAN',
                    details=f'Retrieved keuangan data from server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get keuangan data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Get keuangan error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data(current_user_id, server_host, server_port):
    """Get data dashboard dari server"""
    try:
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/dashboard"
        
        try:
            response = requests.get(server_url, timeout=30)
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='GET_DASHBOARD',
                    details=f'Retrieved dashboard data from server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get dashboard data'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Server timeout'}), 408
            
    except Exception as e:
        logger.error(f"Get dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@data_bp.route('/backup', methods=['POST'])
@token_required
def backup_database(current_user_id, server_host, server_port):
    """Backup database di server"""
    try:
        data = request.get_json()
        
        # Forward request ke server lokal
        server_url = f"http://{server_host}:{server_port}/api/backup"
        
        try:
            response = requests.post(server_url, json=data, timeout=120)  # Timeout lebih lama untuk backup
            
            if response.status_code == 200:
                # Log activity
                ApiLog.log_activity(
                    user_id=current_user_id,
                    action='BACKUP_DATABASE',
                    details=f'Database backup initiated on server {server_host}:{server_port}',
                    ip_address=request.remote_addr,
                    endpoint=request.endpoint,
                    method=request.method,
                    status_code=200
                )
                
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to backup database'
                }), response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to server'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Backup timeout'}), 408
            
    except Exception as e:
        logger.error(f"Backup database error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500