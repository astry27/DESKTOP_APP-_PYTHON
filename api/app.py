# Path: api/app.py

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
import requests
import logging
from functools import wraps
import json

# Import konfigurasi
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Override database URL for development to use SQLite
if not os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gereja_api_dev.db'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models setelah db diinisialisasi
from models.server_registry import ServerRegistry
from models.api_log import ApiLog
from models.user_session import UserSession

# Import routes
from routes.auth import auth_bp
from routes.server_management import server_bp
from routes.data_access import data_bp
from routes.monitoring import monitoring_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(server_bp, url_prefix='/api/server')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')

# Decorator untuk verifikasi token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Cek apakah session masih valid
            session_record = UserSession.query.filter_by(
                user_id=current_user_id,
                token=token,
                is_active=True
            ).first()
            
            if not session_record:
                return jsonify({'message': 'Token invalid or expired'}), 401
                
            # Update last activity
            session_record.last_activity = datetime.utcnow()
            db.session.commit()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/servers/register', methods=['POST'])
@token_required
def register_server(current_user_id):
    """Register server lokal ke API"""
    try:
        data = request.get_json()
        
        required_fields = ['server_name', 'host', 'port', 'church_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} required'}), 400
        
        # Cek apakah server sudah terdaftar
        existing_server = ServerRegistry.query.filter_by(
            host=data['host'],
            port=data['port']
        ).first()
        
        if existing_server:
            # Update existing server
            existing_server.server_name = data['server_name']
            existing_server.church_name = data['church_name']
            existing_server.status = 'online'
            existing_server.last_ping = datetime.utcnow()
            server = existing_server
        else:
            # Create new server
            server = ServerRegistry(
                server_name=data['server_name'],
                host=data['host'],
                port=data['port'],
                church_name=data['church_name'],
                registered_by=current_user_id,
                status='online'
            )
            db.session.add(server)
        
        db.session.commit()
        
        # Log activity
        log_api_activity(current_user_id, 'REGISTER_SERVER', f"Server {data['server_name']} registered")
        
        return jsonify({
            'message': 'Server registered successfully',
            'server_id': server.id,
            'status': 'online'
        })
        
    except Exception as e:
        logger.error(f"Error registering server: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/servers/<int:server_id>/ping', methods=['POST'])
@token_required
def ping_server(current_user_id, server_id):
    """Ping server untuk update status"""
    try:
        server = ServerRegistry.query.get_or_404(server_id)
        
        # Update ping time dan status
        server.last_ping = datetime.utcnow()
        server.status = 'online'
        db.session.commit()
        
        return jsonify({
            'message': 'Ping received',
            'server_id': server_id,
            'status': 'online'
        })
        
    except Exception as e:
        logger.error(f"Error ping server: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/servers', methods=['GET'])
@token_required
def get_servers(current_user_id):
    """Get daftar server yang terdaftar"""
    try:
        servers = ServerRegistry.query.all()
        
        servers_data = []
        for server in servers:
            # Check if server is really online (last ping < 5 minutes)
            time_diff = datetime.utcnow() - server.last_ping
            is_online = time_diff.total_seconds() < 300  # 5 menit
            
            servers_data.append({
                'id': server.id,
                'server_name': server.server_name,
                'host': server.host,
                'port': server.port,
                'church_name': server.church_name,
                'status': 'online' if is_online else 'offline',
                'last_ping': server.last_ping.isoformat() if server.last_ping else None,
                'registered_at': server.registered_at.isoformat()
            })
        
        return jsonify({
            'servers': servers_data,
            'total': len(servers_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting servers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/servers/<int:server_id>/proxy', methods=['POST'])
@token_required
def proxy_to_server(current_user_id, server_id):
    """Proxy request ke server lokal"""
    try:
        server = ServerRegistry.query.get_or_404(server_id)
        
        # Ambil data request
        data = request.get_json()
        endpoint = data.get('endpoint', '')
        method = data.get('method', 'GET')
        payload = data.get('data', {})
        
        # Buat URL ke server lokal
        server_url = f"http://{server.host}:{server.port}{endpoint}"
        
        # Forward request ke server lokal
        if method.upper() == 'GET':
            response = requests.get(server_url, params=payload, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(server_url, json=payload, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(server_url, json=payload, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(server_url, timeout=30)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        # Log activity
        log_api_activity(current_user_id, 'PROXY_REQUEST', f"Proxied {method} {endpoint} to server {server_id}")
        
        # Return response dari server lokal
        return jsonify({
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Server timeout'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to server'}), 503
    except Exception as e:
        logger.error(f"Error proxying to server: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def log_api_activity(user_id, action, details):
    """Log API activity"""
    try:
        log = ApiLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Cleanup expired sessions
def cleanup_expired_sessions():
    """Cleanup expired sessions"""
    try:
        expired_time = datetime.utcnow() - timedelta(hours=24)
        UserSession.query.filter(UserSession.last_activity < expired_time).delete()
        db.session.commit()
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Cleanup expired sessions at startup
        cleanup_expired_sessions()
    
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)