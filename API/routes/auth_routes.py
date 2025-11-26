# Path: api/routes/auth_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import hashlib
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

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

@auth_bp.route('/login', methods=['POST'])
def user_login():
    """Login untuk pengguna biasa (bukan admin)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username dan password harus diisi'}), 400
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id_pengguna, username, nama_lengkap, email, peran, is_active, created_at, last_login
        FROM pengguna 
        WHERE username = %s AND password = %s AND is_active = 1
        """
        params = (username, hashed_password)
        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            # Update last login
            now = datetime.datetime.now()
            user_id = result.get('id_pengguna')
            if user_id is not None:
                update_query = "UPDATE pengguna SET last_login = %s WHERE id_pengguna = %s"
                params = (now, user_id)
                cursor.execute(update_query, params)  # type: ignore[arg-type]
                connection.commit()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'status': 'success',
                'message': 'Login berhasil',
                'user': result
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Username atau password salah'
            }), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """Register pengguna baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        username = data.get('username')
        password = data.get('password')
        nama_lengkap = data.get('nama_lengkap')
        email = data.get('email')
        peran = data.get('peran', 'user')
        
        if not username or not password or not nama_lengkap:
            return jsonify({'status': 'error', 'message': 'Username, password, dan nama lengkap harus diisi'}), 400
        
        # Cek apakah username sudah ada
        cursor = connection.cursor()
        check_query = "SELECT id_pengguna FROM pengguna WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Username sudah digunakan'}), 409
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert pengguna baru
        insert_query = """
        INSERT INTO pengguna (username, password, nama_lengkap, email, peran, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (username, hashed_password, nama_lengkap, email, peran, True)
        cursor.execute(insert_query, params)
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Pengguna berhasil terdaftar',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Ganti password pengguna"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        user_id = data.get('user_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not user_id or not old_password or not new_password:
            return jsonify({'status': 'error', 'message': 'User ID, password lama, dan password baru harus diisi'}), 400
        
        # Verifikasi password lama
        old_hashed = hashlib.sha256(old_password.encode()).hexdigest()
        cursor = connection.cursor()
        verify_query = "SELECT id_pengguna FROM pengguna WHERE id_pengguna = %s AND password = %s"
        cursor.execute(verify_query, (user_id, old_hashed))
        verified = cursor.fetchone()
        
        if not verified:
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Password lama tidak sesuai'}), 401
        
        # Update password baru
        new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
        update_query = "UPDATE pengguna SET password = %s, updated_at = %s WHERE id_pengguna = %s"
        cursor.execute(update_query, (new_hashed, datetime.datetime.now(), user_id))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Password berhasil diubah'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password pengguna (untuk admin)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        user_id = data.get('user_id')
        new_password = data.get('new_password', 'password123')  # Default password
        admin_id = data.get('admin_id')  # ID admin yang melakukan reset
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID harus diisi'}), 400
        
        # Hash password baru
        new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
        
        cursor = connection.cursor()
        update_query = "UPDATE pengguna SET password = %s, updated_at = %s WHERE id_pengguna = %s"
        cursor.execute(update_query, (new_hashed, datetime.datetime.now(), user_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            # Log aktivitas reset password jika admin_id ada
            if admin_id:
                log_query = """
                INSERT INTO log_aktivitas (id_admin, aktivitas, detail, timestamp)
                VALUES (%s, %s, %s, %s)
                """
                log_params = (
                    admin_id,
                    'Reset Password',
                    f'Reset password untuk user ID {user_id}',
                    datetime.datetime.now()
                )
                cursor.execute(log_query, log_params)
                connection.commit()
            
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Password berhasil direset'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pengguna tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verifikasi token atau session (placeholder untuk future implementation)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'status': 'error', 'message': 'Token harus diisi'}), 400
    
    # Untuk saat ini, return success untuk semua token
    # Implementasi proper token verification bisa ditambahkan nanti
    return jsonify({
        'status': 'success',
        'message': 'Token valid',
        'user_id': 1  # Placeholder
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout pengguna"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    user_id = data.get('user_id')
    
    # Untuk saat ini hanya return success
    # Implementasi proper session management bisa ditambahkan nanti
    
    return jsonify({
        'status': 'success',
        'message': 'Logout berhasil'
    })

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Ambil profil pengguna berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID harus diisi'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id_pengguna, username, nama_lengkap, email, peran, is_active, created_at, last_login
        FROM pengguna 
        WHERE id_pengguna = %s
        """
        cursor.execute(query, (user_id,))
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
                'message': 'Pengguna tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update profil pengguna"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        user_id = data.get('user_id')
        nama_lengkap = data.get('nama_lengkap')
        email = data.get('email')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID harus diisi'}), 400
        
        cursor = connection.cursor()
        query = """
        UPDATE pengguna SET 
            nama_lengkap = %s, email = %s, updated_at = %s
        WHERE id_pengguna = %s
        """
        params = (nama_lengkap, email, datetime.datetime.now(), user_id)
        cursor.execute(query, params)
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Profil berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pengguna tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500