# Path: api/routes/admin_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import hashlib
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

API_STATUS_FILE = 'api_status.txt'

def get_api_status():
    try:
        if os.path.exists(API_STATUS_FILE):
            with open(API_STATUS_FILE, 'r') as f:
                content = f.read().strip()
                return content == 'enabled'
        else:
            set_api_status(True)
            return True
    except Exception as e:
        print(f"Error reading API status: {e}")
        return True

def set_api_status(enabled):
    try:
        with open(API_STATUS_FILE, 'w') as f:
            f.write('enabled' if enabled else 'disabled')
        return True
    except Exception as e:
        print(f"Error writing API status: {e}")
        return False

def check_api_enabled():
    if not get_api_status():
        return jsonify({
            'status': 'error', 
            'message': 'API sedang dinonaktifkan'
        }), 503
    return None

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Endpoint untuk login admin"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username dan password harus diisi'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            'status': 'error',
            'message': 'Database tidak tersedia. Pastikan MySQL server berjalan dan kredensial di .env file benar.'
        }), 503

    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id_admin, username, nama_lengkap, email, peran, is_active, created_at, last_login
        FROM admin
        WHERE username = %s AND password = %s AND is_active = 1
        """
        params = (username, hashed_password)
        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            # Update last login
            now = datetime.datetime.now()
            admin_id = result.get('id_admin')  # type: ignore
            if admin_id is not None:
                update_query = "UPDATE admin SET last_login = %s WHERE id_admin = %s"
                cursor.execute(update_query, (now, admin_id))  # type: ignore
                connection.commit()

            cursor.close()
            connection.close()

            return jsonify({
                'status': 'success',
                'message': 'Login admin berhasil',
                'admin': result
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Username atau password salah'
            }), 401
    except Exception as e:
        try:
            cursor.close()
            connection.close()
        except:
            pass
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)[:100]}'}), 500

@admin_bp.route('/update-last-login', methods=['POST'])
def update_admin_last_login():
    """Endpoint untuk update last login admin"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        admin_id = data.get('admin_id')
        last_login = data.get('last_login')
        
        if last_login:
            last_login_dt = datetime.datetime.fromisoformat(last_login.replace('Z', '+00:00'))
        else:
            last_login_dt = datetime.datetime.now()
        
        cursor = connection.cursor()
        query = "UPDATE admin SET last_login = %s WHERE id_admin = %s"
        params = (last_login_dt, admin_id)
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Last login berhasil diupdate'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/active-sessions', methods=['GET'])
def get_active_sessions():
    """Endpoint untuk mendapatkan daftar client yang aktif dengan timeout detection"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Step 1: Auto-disconnect clients yang timeout (tidak ada heartbeat selama 2 menit)
        # Client dianggap timeout jika last_activity > 2 menit yang lalu
        now = datetime.datetime.now()
        timeout_query = """
        UPDATE client_connections
        SET status = 'Terputus', disconnect_time = %s
        WHERE status = 'Terhubung'
        AND last_activity < DATE_SUB(NOW(), INTERVAL 2 MINUTE)
        """
        cursor.execute(timeout_query, (now,))
        timeout_count = cursor.rowcount
        connection.commit()

        # Step 2: Query hanya client yang benar-benar aktif (status = Terhubung)
        # Tambahkan id_connection untuk identifikasi unik dan hindari duplikasi
        query = """
        SELECT id_connection, client_ip, hostname, connect_time, status, last_activity
        FROM client_connections
        WHERE status = 'Terhubung'
        ORDER BY last_activity DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': result,
            'timeout_disconnected': timeout_count  # Jumlah client yang di-timeout
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/client-activity-history', methods=['GET'])
def get_client_activity_history():
    """Endpoint untuk mendapatkan riwayat aktivitas semua client (termasuk yang terputus)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Query semua aktivitas client, urutkan berdasarkan waktu terakhir aktivitas
        # Hanya tampilkan yang sudah disconnect (status = 'Terputus')
        query = """
        SELECT
            id_connection,
            client_ip,
            hostname,
            connect_time,
            disconnect_time,
            status,
            last_activity,
            TIMESTAMPDIFF(SECOND, connect_time, COALESCE(disconnect_time, last_activity)) as duration_seconds
        FROM client_connections
        WHERE status = 'Terputus'
        ORDER BY disconnect_time DESC, last_activity DESC
        LIMIT 100
        """
        cursor.execute(query)
        result = cursor.fetchall()

        # Format duration menjadi human-readable
        for record in result:
            duration = record.get('duration_seconds', 0)  # type: ignore
            if duration:
                hours = duration // 3600  # type: ignore
                minutes = (duration % 3600) // 60  # type: ignore
                seconds = duration % 60  # type: ignore

                if hours > 0:  # type: ignore
                    record['duration_formatted'] = f"{hours}h {minutes}m {seconds}s"  # type: ignore
                elif minutes > 0:  # type: ignore
                    record['duration_formatted'] = f"{minutes}m {seconds}s"  # type: ignore
                else:
                    record['duration_formatted'] = f"{seconds}s"  # type: ignore
            else:
                record['duration_formatted'] = "0s"  # type: ignore

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': result,
            'total_records': len(result)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/broadcast', methods=['POST'])
def admin_broadcast():
    """Endpoint untuk mengirim broadcast message dari admin"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        message = data.get('message')
        admin_id = data.get('admin_id', 1)
        
        cursor = connection.cursor()
        query = """
        INSERT INTO pesan (pengirim_admin, pesan, waktu_kirim, is_broadcast, broadcast_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            admin_id,
            message,
            datetime.datetime.now(),
            True,
            'all'
        )
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Broadcast message berhasil dikirim'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/enable', methods=['POST'])
def enable_api():
    """Aktifkan API service"""
    if set_api_status(True):
        return jsonify({
            'status': 'success',
            'message': 'API berhasil diaktifkan'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Gagal mengaktifkan API'
        }), 500

@admin_bp.route('/disable', methods=['POST'])
def disable_api():
    """Nonaktifkan API service"""
    if set_api_status(False):
        return jsonify({
            'status': 'success',
            'message': 'API berhasil dinonaktifkan'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Gagal menonaktifkan API'
        }), 500

@admin_bp.route('/status')
def api_status():
    """Cek status API"""
    return jsonify({
        'status': 'success',
        'api_enabled': get_api_status(),
        'message': 'API aktif' if get_api_status() else 'API nonaktif'
    })

@admin_bp.route('/log-activity', methods=['POST'])
def log_admin_activity():
    """Log aktivitas admin"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO log_aktivitas (id_admin, aktivitas, detail, ip_address, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data.get('admin_id'),
            data.get('aktivitas'),
            data.get('detail'),
            data.get('ip_address'),
            datetime.datetime.now()
        )
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Log aktivitas berhasil ditambahkan'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of all users"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_admin, username, nama_lengkap, email, is_active, created_at, last_login FROM admin")
        users = cursor.fetchall()
        
        # Convert datetime to string
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                user['created_at'] = created_at.isoformat()  # type: ignore
            last_login = user.get('last_login')
            if last_login:
                user['last_login'] = last_login.isoformat()  # type: ignore

        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'data': users})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        username = data.get('username')
        password = data.get('password')
        nama_lengkap = data.get('nama_lengkap')
        email = data.get('email')
        
        if not all([username, password, nama_lengkap, email]):
            return jsonify({'status': 'error', 'message': 'All fields required'}), 400
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        now = datetime.datetime.now()

        cursor = connection.cursor()
        query = "INSERT INTO admin (username, password, nama_lengkap, email, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (username, hashed_password, nama_lengkap, email, 1, now))
        connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User created successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        
        updates = []
        params = []
        
        if data.get('nama_lengkap'):
            updates.append("nama_lengkap = %s")
            params.append(data['nama_lengkap'])
        
        if data.get('email'):
            updates.append("email = %s")
            params.append(data['email'])
        
        if data.get('password'):
            updates.append("password = %s")
            params.append(hashlib.sha256(data['password'].encode()).hexdigest())
        
        if 'is_active' in data:
            updates.append("is_active = %s")
            params.append(data['is_active'])
        
        if updates:
            params.append(user_id)
            query = f"UPDATE admin SET {', '.join(updates)} WHERE id_admin = %s"
            cursor.execute(query, params)
            connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM admin WHERE id_admin = %s", (user_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/create-user', methods=['POST'])
def create_admin_user():
    """Endpoint untuk menambah admin/user baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        # Validasi field required
        required_fields = ['username', 'password', 'nama_lengkap', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Field {field} harus diisi'}), 400
        
        username = data.get('username')
        password = data.get('password')
        nama_lengkap = data.get('nama_lengkap')
        email = data.get('email')
        is_active = data.get('is_active', 1)  # Default aktif
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = connection.cursor()
        
        # Cek apakah username sudah ada
        check_query = "SELECT id_admin FROM admin WHERE username = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Username sudah digunakan'}), 400
        
        # Cek apakah email sudah ada
        check_query = "SELECT id_admin FROM admin WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Email sudah digunakan'}), 400
        
        # Insert admin baru
        query = """
        INSERT INTO admin (username, password, nama_lengkap, email, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (username, hashed_password, nama_lengkap, email, is_active, datetime.datetime.now())
        cursor.execute(query, params)
        admin_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Admin "{nama_lengkap}" berhasil ditambahkan',
            'admin_id': admin_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/list-users', methods=['GET'])
def list_admin_users():
    """Endpoint untuk daftar semua admin/user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id_admin, username, nama_lengkap, email, is_active, created_at, last_login
        FROM admin 
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        
        # Convert datetime to string for JSON serialization
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                user['created_at'] = created_at.isoformat()  # type: ignore
            last_login = user.get('last_login')
            if last_login:
                user['last_login'] = last_login.isoformat()  # type: ignore

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': users,
            'total': len(users)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/update-user/<int:admin_id>', methods=['PUT'])
def update_admin_user(admin_id):
    """Endpoint untuk update admin/user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        
        # Cek apakah admin exists
        cursor.execute("SELECT id_admin FROM admin WHERE id_admin = %s", (admin_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Admin tidak ditemukan'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if data.get('nama_lengkap'):
            update_fields.append("nama_lengkap = %s")
            params.append(data.get('nama_lengkap'))
        
        if data.get('email'):
            update_fields.append("email = %s")
            params.append(data.get('email'))
        
        if data.get('password'):
            hashed_password = hashlib.sha256(data.get('password').encode()).hexdigest()
            update_fields.append("password = %s")
            params.append(hashed_password)
        
        if 'is_active' in data:
            update_fields.append("is_active = %s")
            params.append(data.get('is_active'))
        
        if not update_fields:
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Tidak ada field yang diupdate'}), 400
        
        # Add admin_id to params
        params.append(admin_id)
        
        query = f"UPDATE admin SET {', '.join(update_fields)} WHERE id_admin = %s"
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Admin berhasil diupdate'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500