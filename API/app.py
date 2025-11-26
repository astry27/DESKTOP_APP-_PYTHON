from flask import Flask, jsonify, request
from flask_cors import CORS
from config import get_db_connection, DB_CONFIG
import datetime
import os
import sys

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes (adjust origins for production security)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Change to specific domains in production
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['JSON_AS_ASCII'] = False  # Support Indonesian characters
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Import all blueprints
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.jemaat_routes import jemaat_bp
from routes.kegiatan_routes import kegiatan_bp
from routes.keuangan_routes import keuangan_bp
from routes.pengumuman_routes import pengumuman_bp
from routes.dokumen_routes import dokumen_bp
from routes.struktur_routes import struktur_bp
from routes.aset_routes import aset_bp
from routes.program_kerja_routes import program_kerja_bp
from routes.pengguna_routes import pengguna_bp
from routes.client_routes import client_bp
from routes.pesan_routes import pesan_bp
from routes.log_routes import log_bp
from routes.broadcast_routes import broadcast_bp
from routes.kegiatan_wr_routes import kegiatan_wr_bp
# from routes.program_kerja_wr_routes import program_kerja_wr_bp  # File not found
from routes.program_kerja_k_kategorial_routes import program_kerja_k_kategorial_bp
from routes.buku_kronik_routes import buku_kronik_bp
from routes.kategorial_routes import kategorial_bp
from routes.binaan_routes import binaan_bp
from routes.wr_routes import wr_bp
from routes.tim_pembina_routes import tim_pembina_bp

# Register all blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(jemaat_bp)
app.register_blueprint(kegiatan_bp)
app.register_blueprint(keuangan_bp)
app.register_blueprint(pengumuman_bp)
app.register_blueprint(dokumen_bp)
app.register_blueprint(struktur_bp)
app.register_blueprint(aset_bp)
app.register_blueprint(program_kerja_bp)
app.register_blueprint(pengguna_bp)
app.register_blueprint(client_bp)
app.register_blueprint(pesan_bp)
app.register_blueprint(log_bp)
app.register_blueprint(broadcast_bp)
app.register_blueprint(kegiatan_wr_bp)
# app.register_blueprint(program_kerja_wr_bp)  # File not found
app.register_blueprint(program_kerja_k_kategorial_bp)
app.register_blueprint(buku_kronik_bp)
app.register_blueprint(kategorial_bp)
app.register_blueprint(binaan_bp)
app.register_blueprint(wr_bp)
app.register_blueprint(tim_pembina_bp)

# Basic routes
@app.route('/')
def home():
    """API Home - Shows API status and available endpoints"""
    return jsonify({
        'status': 'success',
        'message': 'Church Management System API',
        'name': 'Sistem Informasi Gereja Katolik API',
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'database': DB_CONFIG['database'],
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'test_db': '/test-db',
            'admin': '/admin',
            'auth': '/auth',
            'jemaat': '/jemaat',
            'kegiatan': '/kegiatan',
            'kegiatan_wr': '/kegiatan-wr',
            'keuangan': '/keuangan',
            'pengumuman': '/pengumuman',
            'dokumen': '/dokumen',
            'struktur': '/struktur',
            'aset': '/aset',
            'program_kerja': '/program-kerja',
            'program_kerja_wr': '/program-kerja-wr',
            'program_kerja_kategorial': '/program-kerja-kategorial',
            'pengguna': '/pengguna',
            'client': '/client',
            'pesan': '/pesan',
            'log': '/log',
            'broadcast': '/broadcast',
            'buku_kronik': '/buku-kronik',
            'kategorial': '/kategorial',
            'wilayah_rohani': '/wr',
            'binaan': '/binaan',
            'tim_pembina': '/tim-pembina'
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/test-db')
def test_database():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version_row = cursor.fetchone()
            cursor.close()
            connection.close()
            if version_row:
                version_str = str(version_row[0]) if isinstance(version_row, (list, tuple)) else str(version_row)  # type: ignore
            else:
                version_str = 'Unknown'
            return jsonify({
                'status': 'success',
                'message': 'Database terhubung',
                'version': version_str
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

@app.route('/debug/check-routes')
def debug_check_routes():
    """Debug endpoint untuk cek file tim_pembina_routes.py"""
    import os
    file_path = 'routes/tim_pembina_routes.py'

    if not os.path.exists(file_path):
        return jsonify({
            'file_exists': False,
            'message': 'File tim_pembina_routes.py tidak ditemukan'
        })

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # Check critical lines
        line_53 = lines[52] if len(lines) > 52 else ''
        line_432 = lines[431] if len(lines) > 431 else ''

        return jsonify({
            'file_exists': True,
            'file_size': len(content),
            'total_lines': len(lines),
            'line_53_content': line_53.strip(),
            'uses_tim_pembina_peserta': 'tim_pembina_peserta' in content,
            'count_tim_pembina_peserta': content.count('tim_pembina_peserta'),
            'has_search_jemaat_route': 'search-jemaat' in content,
            'has_statistics_route': '/statistics' in content,
            'line_432_has_search_jemaat': 'search-jemaat' in line_432,
            'blueprint_registered': 'tim_pembina' in [bp.name for bp in app.blueprints.values()]
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

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
        'message': 'Internal server error',
        'error': str(error)
    }), 500

if __name__ == '__main__':
    print("Starting Flask API on http://localhost:5000")
    print("Registered blueprints:", [bp.name for bp in app.blueprints.values()])
    app.run(debug=True, host='localhost', port=5000)
