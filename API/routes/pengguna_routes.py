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

        # Fetch from pengguna table
        cursor.execute("SELECT id_pengguna as id, username, nama_lengkap, email, peran, is_active, created_at, last_login, 'pengguna' as source_table FROM pengguna")
        pengguna_users = cursor.fetchall()

        # Fetch from admin table
        cursor.execute("SELECT id_admin as id, username, nama_lengkap, email, 'admin' as peran, is_active, created_at, last_login, 'admin' as source_table FROM admin")
        admin_users = cursor.fetchall()

        # Combine results and convert to proper dicts
        result = []
        for user in pengguna_users + admin_users:
            # Create a new dict and manually copy fields
            # type: ignore is used to suppress type checker warnings for dictionary access
            user_dict = {
                'id': user['id'],  # type: ignore
                'username': user['username'],  # type: ignore
                'nama_lengkap': user['nama_lengkap'],  # type: ignore
                'email': user['email'],  # type: ignore
                'peran': user['peran'],  # type: ignore
                'is_active': user['is_active'],  # type: ignore
                'created_at': user['created_at'].isoformat() if user['created_at'] else None,  # type: ignore
                'last_login': user['last_login'].isoformat() if user['last_login'] else None,  # type: ignore
                'source_table': user['source_table']  # type: ignore
            }
            result.append(user_dict)

        # Sort by created_at DESC
        result.sort(key=lambda x: x.get('created_at') or '', reverse=True)

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
        peran = data.get('peran', 'user')  # Get role from request, default to 'user'
        is_active = data.get('is_active', 1)

        if not all([username, password, nama_lengkap, email]):
            return jsonify({'status': 'error', 'message': 'All fields required'}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = connection.cursor()

        # Route to correct table based on role
        if peran.lower() == 'admin':
            # Check if username already exists in admin table
            check_query = "SELECT id_admin FROM admin WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'status': 'error', 'message': 'Username sudah digunakan'}), 400

            # Check if email already exists in admin table
            check_query = "SELECT id_admin FROM admin WHERE email = %s"
            cursor.execute(check_query, (email,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'status': 'error', 'message': 'Email sudah digunakan'}), 400

            # Insert into admin table
            query = "INSERT INTO admin (username, password, nama_lengkap, email, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (username, hashed_password, nama_lengkap, email, is_active, datetime.datetime.now()))
            user_id = cursor.lastrowid
            table_name = 'admin'
        else:
            # Check if username already exists in pengguna table
            check_query = "SELECT id_pengguna FROM pengguna WHERE username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'status': 'error', 'message': 'Username sudah digunakan'}), 400

            # Check if email already exists in pengguna table
            check_query = "SELECT id_pengguna FROM pengguna WHERE email = %s"
            cursor.execute(check_query, (email,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return jsonify({'status': 'error', 'message': 'Email sudah digunakan'}), 400

            # Insert into pengguna table (for user/operator roles)
            query = "INSERT INTO pengguna (username, password, nama_lengkap, email, peran, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (username, hashed_password, nama_lengkap, email, peran, is_active, datetime.datetime.now()))
            user_id = cursor.lastrowid
            table_name = 'pengguna'

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': f'User created successfully in {table_name} table',
            'user_id': user_id,
            'table': table_name
        })
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

        # Determine which table to update based on source_table or peran
        source_table = data.get('source_table')
        peran = data.get('peran', '')

        # If no source_table, check which table has this user
        if not source_table:
            # Check pengguna table first
            cursor.execute("SELECT id_pengguna FROM pengguna WHERE id_pengguna = %s", (user_id,))
            if cursor.fetchone():
                source_table = 'pengguna'
            else:
                # Check admin table
                cursor.execute("SELECT id_admin FROM admin WHERE id_admin = %s", (user_id,))
                if cursor.fetchone():
                    source_table = 'admin'
                else:
                    cursor.close()
                    connection.close()
                    return jsonify({'status': 'error', 'message': 'User not found'}), 404

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

        # Update peran only for pengguna table (admin table doesn't have peran column)
        if source_table == 'pengguna' and data.get('peran') and data.get('peran').lower() != 'admin':
            updates.append("peran = %s")
            params.append(data['peran'])

        if updates:
            params.append(user_id)
            if source_table == 'admin':
                query = f"UPDATE admin SET {', '.join(updates)} WHERE id_admin = %s"
            else:
                query = f"UPDATE pengguna SET {', '.join(updates)} WHERE id_pengguna = %s"

            cursor.execute(query, params)
            connection.commit()

        cursor.close()
        connection.close()
        return jsonify({
            'status': 'success',
            'message': f'User updated successfully in {source_table} table'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengguna_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_pengguna(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()

        # Try to delete from pengguna table first
        cursor.execute("DELETE FROM pengguna WHERE id_pengguna = %s", (user_id,))
        rows_affected = cursor.rowcount

        # If not found in pengguna table, try admin table
        if rows_affected == 0:
            cursor.execute("DELETE FROM admin WHERE id_admin = %s", (user_id,))
            rows_affected = cursor.rowcount
            table_name = 'admin'
        else:
            table_name = 'pengguna'

        connection.commit()

        if rows_affected > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': f'User deleted successfully from {table_name} table'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500