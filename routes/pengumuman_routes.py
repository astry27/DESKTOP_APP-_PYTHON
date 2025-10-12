# Path: api/routes/pengumuman_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

pengumuman_bp = Blueprint('pengumuman', __name__, url_prefix='/pengumuman')

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

@pengumuman_bp.route('', methods=['GET'])
def get_pengumuman():
    """Ambil semua data pengumuman"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        sasaran = request.args.get('sasaran')

        cursor = connection.cursor(dictionary=True)

        # Build query - kolom yang dihapus: dibuat_oleh_admin, dibuat_oleh_pengguna, kategori, prioritas, tanggal_mulai, tanggal_selesai
        query = """
            SELECT
                id_pengumuman,
                judul,
                isi,
                sasaran,
                pembuat,
                penanggung_jawab,
                is_active,
                created_at,
                updated_at
            FROM pengumuman
        """
        conditions = []
        params = []

        if active_only:
            conditions.append("is_active = 1")

        if sasaran:
            conditions.append("sasaran = %s")
            params.append(sasaran)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
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

@pengumuman_bp.route('', methods=['POST'])
def add_pengumuman():
    """Tambah pengumuman baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        # Struktur tabel baru: id_pengumuman, judul, isi, sasaran, pembuat, penanggung_jawab, is_active, created_at, updated_at
        query = """
        INSERT INTO pengumuman (judul, isi, sasaran, pembuat, penanggung_jawab, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (
            data.get('judul'),
            data.get('isi'),
            data.get('sasaran', 'Umum'),
            data.get('pembuat', 'Administrator'),
            data.get('penanggung_jawab', data.get('pembuat', 'Administrator')),
            data.get('is_active', True)
        )
        cursor.execute(query, params)
        connection.commit()

        pengumuman_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Pengumuman berhasil ditambahkan',
            'id': pengumuman_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengumuman_bp.route('/<int:pengumuman_id>', methods=['GET'])
def get_pengumuman_by_id(pengumuman_id):
    """Ambil pengumuman berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM pengumuman WHERE id_pengumuman = %s"
        cursor.execute(query, (pengumuman_id,))
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
                'message': 'Pengumuman tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengumuman_bp.route('/<int:pengumuman_id>', methods=['PUT'])
def update_pengumuman(pengumuman_id):
    """Update pengumuman"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        # Struktur tabel baru: hanya update field yang editable
        query = """
        UPDATE pengumuman SET
            judul = %s,
            isi = %s,
            sasaran = %s,
            penanggung_jawab = %s,
            is_active = %s,
            updated_at = %s
        WHERE id_pengumuman = %s
        """

        params = (
            data.get('judul'),
            data.get('isi'),
            data.get('sasaran', 'Umum'),
            data.get('penanggung_jawab'),
            data.get('is_active', True),
            datetime.datetime.now(),
            pengumuman_id
        )
        cursor.execute(query, params)
        connection.commit()

        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Pengumuman berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pengumuman tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengumuman_bp.route('/<int:pengumuman_id>', methods=['DELETE'])
def delete_pengumuman(pengumuman_id):
    """Hapus pengumuman"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        query = "DELETE FROM pengumuman WHERE id_pengumuman = %s"
        cursor.execute(query, (pengumuman_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Pengumuman berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Pengumuman tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pengumuman_bp.route('/aktif', methods=['GET'])
def get_pengumuman_aktif():
    """Ambil pengumuman aktif"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 10, type=int)

        cursor = connection.cursor(dictionary=True)
        # Query langsung ke tabel dengan filter is_active
        query = """
            SELECT
                id_pengumuman,
                judul,
                isi,
                sasaran,
                pembuat,
                penanggung_jawab,
                created_at,
                updated_at
            FROM pengumuman
            WHERE is_active = 1
            ORDER BY created_at DESC
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