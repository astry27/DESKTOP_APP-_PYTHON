# Path: api/routes/pesan_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

pesan_bp = Blueprint('pesan', __name__, url_prefix='/pesan')

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

@pesan_bp.route('', methods=['GET'])
def get_pesan():
    """Ambil semua pesan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        is_broadcast = request.args.get('is_broadcast')
        target = request.args.get('target')
        
        cursor = connection.cursor(dictionary=True)
        
        # Query dengan JOIN untuk mendapatkan nama pengirim
        query = """
        SELECT p.*, 
               COALESCE(a.nama_lengkap, pg.nama_lengkap, 'System') as pengirim_nama
        FROM pesan p
        LEFT JOIN admin a ON p.pengirim_admin = a.id_admin
        LEFT JOIN pengguna pg ON p.pengirim_pengguna = pg.id_pengguna
        """
        conditions = []
        params = []
        
        if is_broadcast is not None:
            conditions.append("p.is_broadcast = %s")
            params.append(is_broadcast.lower() == 'true')
        
        if target:
            conditions.append("p.target = %s")
            params.append(target)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY p.waktu_kirim DESC LIMIT %s OFFSET %s"
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

@pesan_bp.route('', methods=['POST'])
def send_pesan():
    """Kirim pesan baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        pengirim_admin = data.get('pengirim_admin')
        pengirim_pengguna = data.get('pengirim_pengguna')
        pesan = data.get('pesan')
        is_broadcast = data.get('is_broadcast', False)
        broadcast_type = data.get('broadcast_type', 'specific_client')
        target = data.get('target')
        
        if not pesan:
            return jsonify({'status': 'error', 'message': 'Pesan tidak boleh kosong'}), 400
        
        cursor = connection.cursor()
        query = """
        INSERT INTO pesan (pengirim_admin, pengirim_pengguna, pesan, 
                          is_broadcast, broadcast_type, target, waktu_kirim, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            pengirim_admin,
            pengirim_pengguna,
            pesan,
            is_broadcast,
            broadcast_type,
            target,
            datetime.datetime.now(),
            'Terkirim'
        )
        cursor.execute(query, params)
        connection.commit()
        
        pesan_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Pesan berhasil dikirim',
            'pesan_id': pesan_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pesan_bp.route('/<int:pesan_id>', methods=['GET'])
def get_pesan_by_id(pesan_id):
    """Ambil pesan berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT p.*, 
               COALESCE(a.nama_lengkap, pg.nama_lengkap, 'System') as pengirim_nama
        FROM pesan p
        LEFT JOIN admin a ON p.pengirim_admin = a.id_admin
        LEFT JOIN pengguna pg ON p.pengirim_pengguna = pg.id_pengguna
        WHERE p.id_pesan = %s
        """
        cursor.execute(query, (pesan_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Pesan tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pesan_bp.route('/<int:pesan_id>/status', methods=['PUT'])
def update_pesan_status(pesan_id):
    """Update status pesan (misalnya dari Terkirim ke Dibaca)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        new_status = data.get('status', 'Dibaca')
        
        cursor = connection.cursor()
        query = "UPDATE pesan SET status = %s WHERE id_pesan = %s"
        cursor.execute(query, (new_status, pesan_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Status pesan berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pesan tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pesan_bp.route('/<int:pesan_id>', methods=['DELETE'])
def delete_pesan(pesan_id):
    """Hapus pesan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        query = "DELETE FROM pesan WHERE id_pesan = %s"
        cursor.execute(query, (pesan_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Pesan berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pesan tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pesan_bp.route('/broadcast', methods=['GET'])
def get_broadcast_messages():
    """Ambil semua pesan broadcast"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT p.*, 
               COALESCE(a.nama_lengkap, pg.nama_lengkap, 'System') as pengirim_nama
        FROM pesan p
        LEFT JOIN admin a ON p.pengirim_admin = a.id_admin
        LEFT JOIN pengguna pg ON p.pengirim_pengguna = pg.id_pengguna
        WHERE p.is_broadcast = 1
        ORDER BY p.waktu_kirim DESC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pesan_bp.route('/recent', methods=['GET'])
def get_recent_messages():
    """Ambil pesan terbaru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        hours = request.args.get('hours', 24, type=int)  # Pesan dalam X jam terakhir
        
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT p.*, 
               COALESCE(a.nama_lengkap, pg.nama_lengkap, 'System') as pengirim_nama
        FROM pesan p
        LEFT JOIN admin a ON p.pengirim_admin = a.id_admin
        LEFT JOIN pengguna pg ON p.pengirim_pengguna = pg.id_pengguna
        WHERE p.waktu_kirim >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY p.waktu_kirim DESC
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