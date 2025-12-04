# Path: api/routes/client_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

client_bp = Blueprint('client', __name__, url_prefix='/client')

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

@client_bp.route('/register', methods=['POST'])
def register_client():
    """Register client baru ke sistem - support multiple connections dari IP yang sama"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        client_ip = data.get('client_ip')
        hostname = data.get('hostname', '')
        session_id = data.get('session_id', '')  # Unique session identifier

        if not client_ip:
            return jsonify({'status': 'error', 'message': 'Client IP required'}), 400

        cursor = connection.cursor()

        # Cek apakah client dengan IP dan hostname yang sama sudah terdaftar
        # Ini memungkinkan multiple clients dari IP yang sama (admin + client di komputer yang sama)
        check_query = """
        SELECT id_connection FROM client_connections
        WHERE client_ip = %s AND hostname = %s AND status = 'Terhubung'
        """
        cursor.execute(check_query, (client_ip, hostname))
        existing = cursor.fetchone()

        if existing:
            # Update last activity untuk connection yang sudah ada
            update_query = """
            UPDATE client_connections
            SET last_activity = %s
            WHERE id_connection = %s
            """
            cursor.execute(update_query, (datetime.datetime.now(), existing[0]))  # type: ignore
            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({
                'status': 'success',
                'message': 'Client sudah terdaftar, aktivitas diperbarui',
                'connection_id': existing[0]  # type: ignore
            })

        # Register client baru - allow multiple connections dari IP yang sama
        # jika hostname berbeda (admin vs client application)
        insert_query = """
        INSERT INTO client_connections (client_ip, hostname, connect_time, status, last_activity)
        VALUES (%s, %s, %s, 'Terhubung', %s)
        """
        now = datetime.datetime.now()
        params = (client_ip, hostname, now, now)
        cursor.execute(insert_query, params)
        connection.commit()

        connection_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Client berhasil terdaftar',
            'connection_id': connection_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@client_bp.route('/disconnect', methods=['POST'])
def disconnect_client():
    """Disconnect client dari sistem"""
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        connection_id = data.get('connection_id')
        client_ip = data.get('client_ip')
        
        cursor = connection.cursor()
        
        if connection_id:
            # Disconnect berdasarkan connection ID
            query = """
            UPDATE client_connections 
            SET status = 'Terputus', disconnect_time = %s 
            WHERE id_connection = %s
            """
            params = (datetime.datetime.now(), connection_id)
        elif client_ip:
            # Disconnect berdasarkan IP
            query = """
            UPDATE client_connections 
            SET status = 'Terputus', disconnect_time = %s 
            WHERE client_ip = %s AND status = 'Terhubung'
            """
            params = (datetime.datetime.now(), client_ip)
        else:
            return jsonify({'status': 'error', 'message': 'Connection ID atau Client IP required'}), 400
        
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Client berhasil disconnect'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@client_bp.route('/heartbeat', methods=['POST'])
def client_heartbeat():
    """Update heartbeat client untuk menandakan masih aktif"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        connection_id = data.get('connection_id')
        client_ip = data.get('client_ip')
        
        cursor = connection.cursor()
        
        if connection_id:
            # Update berdasarkan connection ID
            query = """
            UPDATE client_connections 
            SET last_activity = %s 
            WHERE id_connection = %s AND status = 'Terhubung'
            """
            params = (datetime.datetime.now(), connection_id)
        elif client_ip:
            # Update berdasarkan IP
            query = """
            UPDATE client_connections 
            SET last_activity = %s 
            WHERE client_ip = %s AND status = 'Terhubung'
            """
            params = (datetime.datetime.now(), client_ip)
        else:
            return jsonify({'status': 'error', 'message': 'Connection ID atau Client IP required'}), 400
        
        cursor.execute(query, params)
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Heartbeat updated'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Client connection tidak ditemukan atau tidak aktif'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@client_bp.route('/messages', methods=['GET'])
def get_client_messages():
    """Ambil pesan untuk client"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        since = request.args.get('since')  # timestamp untuk ambil pesan setelah waktu tertentu
        
        cursor = connection.cursor(dictionary=True)
        
        # Query untuk ambil broadcast messages
        query = """
        SELECT p.*, 
               COALESCE(a.nama_lengkap, pg.nama_lengkap, 'System') as pengirim_nama
        FROM pesan p
        LEFT JOIN admin a ON p.pengirim_admin = a.id_admin
        LEFT JOIN pengguna pg ON p.pengirim_pengguna = pg.id_pengguna
        WHERE p.is_broadcast = 1
        """
        params = []
        
        if since:
            query += " AND p.waktu_kirim > %s"
            params.append(since)
        
        query += " ORDER BY p.waktu_kirim DESC LIMIT %s"
        params.append(limit)
        
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

@client_bp.route('/send-message', methods=['POST'])
def send_client_message():
    """Kirim pesan dari client"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        pengirim_pengguna = data.get('pengirim_pengguna')
        pesan = data.get('pesan')
        target = data.get('target', 'admin')
        
        if not pesan:
            return jsonify({'status': 'error', 'message': 'Pesan tidak boleh kosong'}), 400
        
        cursor = connection.cursor()
        query = """
        INSERT INTO pesan (pengirim_pengguna, pesan, waktu_kirim, is_broadcast, broadcast_type, target)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            pengirim_pengguna,
            pesan,
            datetime.datetime.now(),
            False,
            'specific_client',
            target
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

@client_bp.route('/active', methods=['GET'])
def get_active_clients():
    """Ambil daftar client yang sedang aktif"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Menggunakan view yang sudah ada
        query = "SELECT * FROM v_active_clients ORDER BY last_activity DESC"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@client_bp.route('/connections/history', methods=['GET'])
def get_client_connections_history():
    """Ambil semua riwayat koneksi client (aktif dan terputus)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        status_filter = request.args.get('status', None)  # 'Terhubung' atau 'Terputus'

        cursor = connection.cursor(dictionary=True)

        # Query untuk ambil semua koneksi client dengan informasi lengkap
        query = """
        SELECT
            id_connection,
            client_ip,
            hostname,
            status,
            connect_time,
            disconnect_time,
            last_activity,
            TIMESTAMPDIFF(SECOND, last_activity, NOW()) as seconds_since_activity
        FROM client_connections
        """

        params = []

        if status_filter:
            query += " WHERE status = %s"
            params.append(status_filter)

        query += " ORDER BY last_activity DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        result = cursor.fetchall()

        # Proses hasil untuk menambahkan informasi status yang lebih detail
        for row in result:
            if row['status'] == 'Terhubung':
                # Cek apakah benar-benar masih aktif (< 5 menit)
                if row['seconds_since_activity'] > 300:
                    row['actual_status'] = 'Timeout'
                else:
                    row['actual_status'] = 'Aktif'
            else:
                row['actual_status'] = 'Terputus'

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500