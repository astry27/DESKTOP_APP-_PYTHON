# Path: api/myfl.py

from flask import Flask, jsonify, request, send_from_directory
from config import get_db_connection
import datetime
import os

# Import all route blueprints
from routes.admin_routes import admin_bp
from routes.jemaat_routes import jemaat_bp
from routes.kegiatan_routes import kegiatan_bp
from routes.pengumuman_routes import pengumuman_bp
from routes.keuangan_routes import keuangan_bp
from routes.dokumen_routes import dokumen_bp
from routes.client_routes import client_bp
from routes.auth_routes import auth_bp
from routes.pesan_routes import pesan_bp
from routes.log_routes import log_bp
from routes.struktur_routes import struktur_bp
from routes.inventaris_routes import inventaris_bp
from routes.program_kerja_routes import program_kerja_bp
from routes.pengguna_routes import pengguna_bp
from routes.broadcast_routes import broadcast_bp
from routes.kegiatan_wr_routes import kegiatan_wr_bp

app = Flask(__name__)

# Register all blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(jemaat_bp)
app.register_blueprint(kegiatan_bp)
app.register_blueprint(pengumuman_bp)
app.register_blueprint(keuangan_bp)
app.register_blueprint(dokumen_bp)
app.register_blueprint(client_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(pesan_bp)
app.register_blueprint(log_bp)
app.register_blueprint(struktur_bp)
app.register_blueprint(inventaris_bp)
app.register_blueprint(program_kerja_bp)
app.register_blueprint(pengguna_bp)
app.register_blueprint(broadcast_bp)
app.register_blueprint(kegiatan_wr_bp)

API_STATUS_FILE = 'api_status.txt'

def get_api_status():
    try:
        if os.path.exists(API_STATUS_FILE):
            with open(API_STATUS_FILE, 'r') as f:
                content = f.read().strip()
                return content == 'enabled'
        else:
            with open(API_STATUS_FILE, 'w') as f:
                f.write('enabled')
            return True
    except Exception as e:
        print(f"Error reading API status: {e}")
        return True

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'API Gereja Katolik berjalan',
        'version': '2.1.0',
        'api_enabled': get_api_status(),
        'endpoints': {
            'admin': '/admin/*',
            'jemaat': '/jemaat',
            'kegiatan': '/kegiatan',
            'kegiatan_wr': '/kegiatan-wr',
            'pengumuman': '/pengumuman',
            'keuangan': '/keuangan',
            'dokumen': '/files',
            'program_kerja': '/program-kerja',
            'struktur': '/struktur',
            'inventaris': '/inventaris',
            'pengguna': '/pengguna',
            'client': '/client/*',
            'auth': '/auth/*'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'api_enabled': get_api_status()
    })

@app.route('/test-db')
def test_database():
    """Test koneksi database"""
    api_enabled = get_api_status()
    
    if not api_enabled:
        return jsonify({
            'status': 'error',
            'message': 'API sedang dinonaktifkan'
        }), 503
        
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Database terhubung',
                'version': version[0] if version else 'Unknown'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    else:
        return jsonify({
            'status': 'error',
            'message': 'Gagal terhubung database'
        }), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        # Remove any leading 'uploads/' from filename if present
        if filename.startswith('uploads/'):
            filename = filename[8:]  # Remove 'uploads/' prefix
        
        return send_from_directory('uploads', filename)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'File tidak ditemukan'
        }), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint tidak ditemukan'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        'status': 'error',
        'message': 'Service tidak tersedia'
    }), 503

if __name__ == '__main__':
    app.run(debug=True)