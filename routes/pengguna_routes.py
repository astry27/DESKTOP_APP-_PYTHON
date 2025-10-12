from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import hashlib

pengguna_bp = Blueprint('pengguna', __name__, url_prefix='/pengguna')

@pengguna_bp.route('', methods=['GET'])
def get_all_pengguna():
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_pengguna, username, nama_lengkap, email, peran, is_active, created_at, last_login FROM pengguna ORDER BY created_at DESC")
        result = cursor.fetchall()
        
        for user in result:
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
            if user.get('last_login'):
                user['last_login'] = user['last_login'].isoformat()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengguna_bp.route('', methods=['POST'])
def create_pengguna():
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
        peran = 'User'
        
        if not all([username, password, nama_lengkap, email]):
            return jsonify({'status': 'error', 'message': 'All fields required'}), 400
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = connection.cursor()
        query = "INSERT INTO pengguna (username, password, nama_lengkap, email, peran, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (username, hashed_password, nama_lengkap, email, peran, 1, datetime.datetime.now()))
        connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User created successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengguna_bp.route('/<int:user_id>', methods=['PUT'])
def update_pengguna(user_id):
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
            query = f"UPDATE pengguna SET {', '.join(updates)} WHERE id_pengguna = %s"
            cursor.execute(query, params)
            connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengguna_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_pengguna(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM pengguna WHERE id_pengguna = %s", (user_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500