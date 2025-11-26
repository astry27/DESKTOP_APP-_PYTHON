# Path: api/routes/log_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

log_bp = Blueprint('log', __name__, url_prefix='/log')

API_STATUS_FILE = 'api_status.txt'

def get_api_status():
    try:
        if os.path.exists(API_STATUS_FILE):
            with open(API_STATUS_FILE, 'r') as f:
                content = f.read().strip()
                return content == 'enabled'
        else:
            return True
    except Exception as e:
        print(f"Error reading API status: {e}")
        return True

def check_api_enabled():
    if not get_api_status():
        return jsonify({
            'status': 'error', 
            'message': 'API sedang dinonaktifkan'
        }), 503
    return None

@log_bp.route('/activities', methods=['GET'])
def get_log_activities():
    """Ambil log aktivitas"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        admin_id = request.args.get('admin_id', type=int)
        pengguna_id = request.args.get('pengguna_id', type=int)
        
        cursor = connection.cursor(dictionary=True)
        
        # Build query dengan filter
        query = """
        SELECT l.*, 
               COALESCE(a.nama_lengkap, p.nama_lengkap, 'System') as user_name
        FROM log_aktivitas l
        LEFT JOIN admin a ON l.id_admin = a.id_admin
        LEFT JOIN pengguna p ON l.id_pengguna = p.id_pengguna
        """
        conditions = []
        params = []
        
        if admin_id:
            conditions.append("l.id_admin = %s")
            params.append(admin_id)
        
        if pengguna_id:
            conditions.append("l.id_pengguna = %s")
            params.append(pengguna_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY l.timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@log_bp.route('/activities', methods=['POST'])
def add_log_activity():
    """Tambah log aktivitas baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO log_aktivitas (id_admin, id_pengguna, aktivitas, detail, ip_address, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('id_admin'),
            data.get('id_pengguna'),
            data.get('aktivitas'),
            data.get('detail'),
            data.get('ip_address'),
            datetime.datetime.now()
        )
        cursor.execute(query, params)
        connection.commit()
        
        log_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Log aktivitas berhasil ditambahkan',
            'id': log_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@log_bp.route('/activities/recent', methods=['GET'])
def get_recent_activities():
    """Ambil aktivitas terbaru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT l.*, 
               COALESCE(a.nama_lengkap, p.nama_lengkap, 'System') as user_name
        FROM log_aktivitas l
        LEFT JOIN admin a ON l.id_admin = a.id_admin
        LEFT JOIN pengguna p ON l.id_pengguna = p.id_pengguna
        WHERE l.timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY l.timestamp DESC
        LIMIT %s
        """
        cursor.execute(query, (hours, limit))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@log_bp.route('/activities/admin/<int:admin_id>', methods=['GET'])
def get_admin_activities(admin_id):
    """Ambil aktivitas admin tertentu"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 100, type=int)
        
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT l.*, a.nama_lengkap as admin_name
        FROM log_aktivitas l
        JOIN admin a ON l.id_admin = a.id_admin
        WHERE l.id_admin = %s
        ORDER BY l.timestamp DESC
        LIMIT %s
        """
        cursor.execute(query, (admin_id, limit))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@log_bp.route('/activities/stats', methods=['GET'])
def get_activity_stats():
    """Ambil statistik aktivitas"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total aktivitas hari ini
        cursor.execute("""
            SELECT COUNT(*) as total_today
            FROM log_aktivitas
            WHERE DATE(timestamp) = CURDATE()
        """)
        today_result = cursor.fetchone()
        today_count = today_result.get('total_today', 0) if today_result else 0

        # Total aktivitas minggu ini
        cursor.execute("""
            SELECT COUNT(*) as total_week
            FROM log_aktivitas
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        week_result = cursor.fetchone()
        week_count = week_result.get('total_week', 0) if week_result else 0
        
        # Aktivitas per admin
        cursor.execute("""
            SELECT a.nama_lengkap, COUNT(*) as count
            FROM log_aktivitas l
            JOIN admin a ON l.id_admin = a.id_admin
            WHERE l.timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY l.id_admin, a.nama_lengkap
            ORDER BY count DESC
        """)
        admin_stats = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'today_count': today_count,
                'week_count': week_count,
                'admin_stats': admin_stats
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500