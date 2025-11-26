# Path: routes/kategorial_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

kategorial_bp = Blueprint('kategorial', __name__, url_prefix='/kategorial')

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

@kategorial_bp.route('', methods=['GET'])
def get_kategorial():
    """Ambil semua data pengurus komunitas kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Ambil semua data kategorial
        cursor.execute("""
            SELECT
                id_kategorial,
                kelompok_kategorial,
                kelompok_kategorial_lainnya,
                nama_lengkap,
                jenis_kelamin,
                jabatan,
                no_hp,
                email,
                alamat,
                wilayah_rohani,
                masa_jabatan,
                status,
                foto_path,
                created_at,
                updated_at
            FROM kategorial
            ORDER BY created_at DESC
        """)

        data = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': data
        })

    except Exception as e:
        print(f"Error getting kategorial data: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@kategorial_bp.route('', methods=['POST'])
def add_kategorial():
    """Tambah pengurus komunitas kategorial baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        # Validasi input
        if not data.get('nama_lengkap'):
            return jsonify({'status': 'error', 'message': 'Nama lengkap harus diisi'}), 400

        if not data.get('kelompok_kategorial'):
            return jsonify({'status': 'error', 'message': 'Kelompok kategorial harus dipilih'}), 400

        cursor = connection.cursor()

        # Insert data
        cursor.execute("""
            INSERT INTO kategorial (
                kelompok_kategorial,
                kelompok_kategorial_lainnya,
                nama_lengkap,
                jenis_kelamin,
                jabatan,
                no_hp,
                email,
                alamat,
                wilayah_rohani,
                masa_jabatan,
                status,
                foto_path,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            data.get('kelompok_kategorial'),
            data.get('kelompok_kategorial_lainnya', ''),
            data.get('nama_lengkap'),
            data.get('jenis_kelamin', ''),
            data.get('jabatan', ''),
            data.get('no_hp', ''),
            data.get('email', ''),
            data.get('alamat', ''),
            data.get('wilayah_rohani', ''),
            data.get('masa_jabatan', ''),
            data.get('status', 'Aktif'),
            data.get('foto_path', '')
        ))

        connection.commit()
        new_id = cursor.lastrowid

        return jsonify({
            'status': 'success',
            'message': 'Pengurus komunitas kategorial berhasil ditambahkan',
            'id': new_id
        }), 201

    except Exception as e:
        connection.rollback()
        print(f"Error adding kategorial: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@kategorial_bp.route('/<int:kategorial_id>', methods=['PUT'])
def update_kategorial(kategorial_id):
    """Update data pengurus komunitas kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        # Validasi input
        if not data.get('nama_lengkap'):
            return jsonify({'status': 'error', 'message': 'Nama lengkap harus diisi'}), 400

        if not data.get('kelompok_kategorial'):
            return jsonify({'status': 'error', 'message': 'Kelompok kategorial harus dipilih'}), 400

        cursor = connection.cursor()

        # Update data
        cursor.execute("""
            UPDATE kategorial SET
                kelompok_kategorial = %s,
                kelompok_kategorial_lainnya = %s,
                nama_lengkap = %s,
                jenis_kelamin = %s,
                jabatan = %s,
                no_hp = %s,
                email = %s,
                alamat = %s,
                wilayah_rohani = %s,
                masa_jabatan = %s,
                status = %s,
                foto_path = %s,
                updated_at = NOW()
            WHERE id_kategorial = %s
        """, (
            data.get('kelompok_kategorial'),
            data.get('kelompok_kategorial_lainnya', ''),
            data.get('nama_lengkap'),
            data.get('jenis_kelamin', ''),
            data.get('jabatan', ''),
            data.get('no_hp', ''),
            data.get('email', ''),
            data.get('alamat', ''),
            data.get('wilayah_rohani', ''),
            data.get('masa_jabatan', ''),
            data.get('status', 'Aktif'),
            data.get('foto_path', ''),
            kategorial_id
        ))

        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Pengurus komunitas kategorial berhasil diupdate'
        })

    except Exception as e:
        connection.rollback()
        print(f"Error updating kategorial: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@kategorial_bp.route('/<int:kategorial_id>', methods=['DELETE'])
def delete_kategorial(kategorial_id):
    """Hapus pengurus komunitas kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()

        # Delete data
        cursor.execute("DELETE FROM kategorial WHERE id_kategorial = %s", (kategorial_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan'}), 404

        return jsonify({
            'status': 'success',
            'message': 'Pengurus komunitas kategorial berhasil dihapus'
        })

    except Exception as e:
        connection.rollback()
        print(f"Error deleting kategorial: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@kategorial_bp.route('/statistics', methods=['GET'])
def get_kategorial_statistics():
    """Ambil statistik komunitas kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Total kategorial aktif
        cursor.execute("SELECT COUNT(*) as total FROM kategorial WHERE status = 'Aktif'")
        total_result = cursor.fetchone()
        total_aktif = total_result.get('total', 0) if total_result else 0

        # Kategorial per kelompok
        cursor.execute("""
            SELECT kelompok_kategorial, COUNT(*) as jumlah
            FROM kategorial
            WHERE status = 'Aktif' AND kelompok_kategorial IS NOT NULL
            GROUP BY kelompok_kategorial
            ORDER BY jumlah DESC
        """)
        per_kelompok = cursor.fetchall()

        # Kategorial per wilayah rohani
        cursor.execute("""
            SELECT wilayah_rohani, COUNT(*) as jumlah
            FROM kategorial
            WHERE status = 'Aktif' AND wilayah_rohani IS NOT NULL
            GROUP BY wilayah_rohani
            ORDER BY jumlah DESC
        """)
        per_wilayah = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': {
                'total_aktif': total_aktif,
                'per_kelompok': per_kelompok,
                'per_wilayah': per_wilayah
            }
        })

    except Exception as e:
        print(f"Error getting kategorial statistics: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()
