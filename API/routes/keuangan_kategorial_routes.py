# Path: api/routes/keuangan_kategorial_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

keuangan_kategorial_bp = Blueprint('keuangan_kategorial', __name__, url_prefix='/keuangan-kategorial')

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

@keuangan_kategorial_bp.route('', methods=['GET'])
def get_keuangan_kategorial():
    """Ambil semua data keuangan kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT k.id_keuangan_kategorial, k.tanggal, k.jenis, k.kategori,
               k.keterangan, k.jumlah, k.created_at, k.updated_at,
               k.created_by_admin,
               COALESCE(a.username, 'system') as dibuat_oleh,
               COALESCE(a.nama_lengkap, 'System') as nama_admin
        FROM keuangan_kategorial k
        LEFT JOIN admin a ON k.created_by_admin = a.id_admin
        ORDER BY k.tanggal DESC, k.created_at DESC
        LIMIT %s OFFSET %s
        """

        print(f"[DEBUG API] GET /keuangan-kategorial - limit: {limit}, offset: {offset}")
        cursor.execute(query, (limit, offset))
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        print(f"[DEBUG API] GET /keuangan-kategorial - returned {len(result)} records")
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        print(f"[ERROR API] GET /keuangan-kategorial failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_kategorial_bp.route('', methods=['POST'])
def add_keuangan_kategorial():
    """Tambah data keuangan kategorial baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    print(f"[DEBUG API] POST /keuangan-kategorial - received data: {data}")

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        created_by_admin = data.get('created_by_admin')

        if not created_by_admin:
            print("[ERROR API] created_by_admin is required")
            return jsonify({'status': 'error', 'message': 'created_by_admin is required'}), 400

        cursor = connection.cursor()

        query = """
        INSERT INTO keuangan_kategorial (tanggal, jenis, kategori, keterangan, jumlah, created_by_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('tanggal'),
            data.get('jenis'),  # Pemasukan/Pengeluaran
            data.get('kategori'),  # Kolekte, Donasi, dll
            data.get('keterangan'),
            data.get('jumlah'),
            created_by_admin
        )

        print(f"[DEBUG API] Inserting keuangan kategorial: {params}")
        cursor.execute(query, params)
        connection.commit()

        keuangan_id = cursor.lastrowid
        cursor.close()
        connection.close()

        print(f"[DEBUG API] Keuangan kategorial added successfully: ID={keuangan_id}")
        return jsonify({
            'status': 'success',
            'message': 'Data keuangan kategorial berhasil ditambahkan',
            'id': keuangan_id
        })
    except Exception as e:
        print(f"[ERROR API] POST /keuangan-kategorial failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_kategorial_bp.route('/<int:keuangan_id>', methods=['GET'])
def get_keuangan_kategorial_by_id(keuangan_id):
    """Ambil data keuangan kategorial berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT k.id_keuangan_kategorial, k.tanggal, k.jenis, k.kategori,
                   k.keterangan, k.jumlah, k.created_at, k.updated_at,
                   k.created_by_admin,
                   COALESCE(a.username, 'system') as dibuat_oleh,
                   COALESCE(a.nama_lengkap, 'System') as nama_admin
            FROM keuangan_kategorial k
            LEFT JOIN admin a ON k.created_by_admin = a.id_admin
            WHERE k.id_keuangan_kategorial = %s
        """
        cursor.execute(query, (keuangan_id,))
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
                'message': 'Data keuangan kategorial tidak ditemukan'
            }), 404
    except Exception as e:
        print(f"[ERROR API] GET /keuangan-kategorial/{keuangan_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_kategorial_bp.route('/<int:keuangan_id>', methods=['PUT'])
def update_keuangan_kategorial(keuangan_id):
    """Update data keuangan kategorial"""
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
        UPDATE keuangan_kategorial SET
            tanggal = %s, jenis = %s, kategori = %s,
            keterangan = %s, jumlah = %s,
            updated_at = %s
        WHERE id_keuangan_kategorial = %s
        """
        params = (
            data.get('tanggal'),
            data.get('jenis'),  # Pemasukan/Pengeluaran
            data.get('kategori'),  # Kolekte, Donasi, dll
            data.get('keterangan'),
            data.get('jumlah'),
            datetime.datetime.now(),
            keuangan_id
        )

        cursor.execute(query, params)
        connection.commit()

        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Data keuangan kategorial berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Data keuangan kategorial tidak ditemukan'
            }), 404
    except Exception as e:
        print(f"[ERROR API] PUT /keuangan-kategorial/{keuangan_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_kategorial_bp.route('/<int:keuangan_id>', methods=['DELETE'])
def delete_keuangan_kategorial(keuangan_id):
    """Hapus data keuangan kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        query = "DELETE FROM keuangan_kategorial WHERE id_keuangan_kategorial = %s"
        cursor.execute(query, (keuangan_id,))
        connection.commit()

        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Data keuangan kategorial berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Data keuangan kategorial tidak ditemukan'
            }), 404
    except Exception as e:
        print(f"[ERROR API] DELETE /keuangan-kategorial/{keuangan_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
