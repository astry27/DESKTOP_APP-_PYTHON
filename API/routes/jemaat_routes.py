# Path: api/routes/jemaat_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

jemaat_bp = Blueprint('jemaat', __name__, url_prefix='/jemaat')

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
            'success': False,
            'data': 'API sedang dinonaktifkan'
        }), 503
    return None

@jemaat_bp.route('/my', methods=['GET'])
def get_my_jemaat():
    """Ambil data jemaat user sendiri saja"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'success': False, 'data': 'user_id required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM jemaat WHERE created_by_pengguna = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('', methods=['GET'])
def get_jemaat():
    """Ambil semua data jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '')
        
        cursor = connection.cursor(dictionary=True)
        
        # Check user permissions
        user_id = request.args.get('user_id', type=int)
        is_admin = request.args.get('is_admin', 'false').lower() == 'true'
        
        # Build query dengan filter search dan user isolation
        query = "SELECT * FROM jemaat"
        params = []
        conditions = []
        
        if search:
            conditions.append("(nama_lengkap LIKE %s OR alamat LIKE %s OR no_telepon LIKE %s OR email LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])
        
        # User isolation: non-admin only see their own data
        if not is_admin and user_id:
            conditions.append("(created_by_pengguna = %s OR created_by_pengguna IS NULL)")
            params.append(user_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY nama_lengkap LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('', methods=['POST'])
def add_jemaat():
    """Tambah data jemaat baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        # Validate request data
        if not data:
            return jsonify({'success': False, 'data': 'Request body cannot be empty'}), 400

        if 'nama_lengkap' not in data or not data.get('nama_lengkap') or not str(data['nama_lengkap']).strip():
            return jsonify({'success': False, 'data': 'nama_lengkap (required) tidak boleh kosong'}), 400

        if 'user_id' not in data or data.get('user_id') is None:
            return jsonify({'success': False, 'data': 'user_id is required'}), 400

        cursor = connection.cursor()

        fields = ['created_by_pengguna']
        values = [data.get('user_id')]

        # Field mapping - IMPORTANT: Check if columns exist in actual database schema!
        # Some fields may not be in original schema - they were added via migration
        field_mapping = {
            # Core fields from original schema
            'nama_lengkap': 'nama_lengkap',
            'alamat': 'alamat',
            'no_telepon': 'no_telepon',
            'email': 'email',
            'tanggal_lahir': 'tanggal_lahir',
            'jenis_kelamin': 'jenis_kelamin',
            'status_menikah': 'status_pernikahan',  # Note: database uses status_pernikahan

            # Fields from migration (added via update_jemaat_schema.sql)
            'wilayah_rohani': 'wilayah_rohani',
            'nama_keluarga': 'nama_keluarga',
            'no_kk': 'no_kk',
            'nik': 'nik',
            'tempat_lahir': 'tempat_lahir',
            'umur': 'umur',  # Age field (calculated from tanggal_lahir)
            'status_kekatolikan': 'status_kekatolikan',
            'kategori': 'kategori',
            'hubungan_keluarga': 'hubungan_keluarga',
            'pendidikan_terakhir': 'pendidikan_terakhir',
            'jenis_pekerjaan': 'jenis_pekerjaan',
            'detail_pekerjaan': 'detail_pekerjaan',
            'status_babtis': 'status_babtis',
            'tanggal_babtis': 'tanggal_babtis',
            'tempat_babtis': 'tempat_babtis',
            'nama_babtis': 'nama_babtis',
            'status_ekaristi': 'status_ekaristi',
            'tanggal_komuni': 'tanggal_komuni',
            'tempat_komuni': 'tempat_komuni',
            'status_krisma': 'status_krisma',
            'tanggal_krisma': 'tanggal_krisma',
            'tempat_krisma': 'tempat_krisma',
            'status_perkawinan': 'status_perkawinan',
            'keuskupan': 'keuskupan',
            'paroki': 'paroki',
            'kota_perkawinan': 'kota_perkawinan',
            'tanggal_perkawinan': 'tanggal_perkawinan',
            'status_perkawinan_detail': 'status_perkawinan_detail',
            'status_keanggotaan': 'status_keanggotaan',
            'wr_tujuan': 'wr_tujuan',
            'paroki_tujuan': 'paroki_tujuan'
        }

        for field_name, db_column in field_mapping.items():
            if field_name in data and data[field_name] not in [None, '']:
                fields.append(db_column)
                values.append(data[field_name])

        query = f"INSERT INTO jemaat ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(values))})"
        params = tuple(values)

        try:
            cursor.execute(query, params)
            connection.commit()

            jemaat_id = cursor.lastrowid
            cursor.close()
            connection.close()

            return jsonify({
                'success': True,
                'data': {
                    'message': 'Jemaat berhasil ditambahkan',
                    'id': jemaat_id
                }
            })
        except Exception as inner_e:
            error_msg = str(inner_e)
            if cursor and connection:
                connection.rollback()
                cursor.close()
                connection.close()

            # Provide detailed error message for debugging
            print(f"[DEBUG] Error inserting jemaat: {error_msg}")
            print(f"[DEBUG] Query: {query}")
            print(f"[DEBUG] Params: {params}")

            if 'Unknown column' in error_msg:
                # Extract column name from error
                import re
                col_match = re.search(r"Unknown column '([^']+)'", error_msg)
                col_name = col_match.group(1) if col_match else "unknown"
                return jsonify({
                    'success': False,
                    'data': f'Database column error: Column "{col_name}" does not exist. Please run migration: sql/49-ensure_all_jemaat_columns.sql'
                }), 500
            elif 'Duplicate entry' in error_msg:
                return jsonify({
                    'success': False,
                    'data': f'Data sudah ada / Duplicate entry. Error: {error_msg}'
                }), 400
            else:
                return jsonify({'success': False, 'data': f'Database error: {error_msg}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['GET'])
def get_jemaat_by_id(jemaat_id):
    """Ambil data jemaat berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM jemaat WHERE id_jemaat = %s"
        cursor.execute(query, (jemaat_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'data': 'Jemaat tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['PUT'])
def update_jemaat(jemaat_id):
    """Update data jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        cursor = connection.cursor()

        # Build dynamic UPDATE query based on provided fields (only update non-null fields)
        set_clauses = []
        params = []

        # Field mapping based on updated jemaat schema
        field_mapping = {
            'nama_lengkap': 'nama_lengkap',
            'alamat': 'alamat',
            'no_telepon': 'no_telepon',
            'email': 'email',
            'tanggal_lahir': 'tanggal_lahir',
            'jenis_kelamin': 'jenis_kelamin',
            'wilayah_rohani': 'wilayah_rohani',
            'nama_keluarga': 'nama_keluarga',
            'no_kk': 'no_kk',
            'nik': 'nik',
            'tempat_lahir': 'tempat_lahir',
            'umur': 'umur',  # Age field (calculated from tanggal_lahir)
            'status_kekatolikan': 'status_kekatolikan',
            'kategori': 'kategori',
            'hubungan_keluarga': 'hubungan_keluarga',
            'pendidikan_terakhir': 'pendidikan_terakhir',
            'status_menikah': 'status_pernikahan',
            'jenis_pekerjaan': 'jenis_pekerjaan',
            'detail_pekerjaan': 'detail_pekerjaan',
            'status_babtis': 'status_babtis',
            'tanggal_babtis': 'tanggal_babtis',
            'tempat_babtis': 'tempat_babtis',
            'nama_babtis': 'nama_babtis',
            'status_ekaristi': 'status_ekaristi',
            'tanggal_komuni': 'tanggal_komuni',
            'tempat_komuni': 'tempat_komuni',
            'status_krisma': 'status_krisma',
            'tanggal_krisma': 'tanggal_krisma',
            'tempat_krisma': 'tempat_krisma',
            'status_perkawinan': 'status_perkawinan',
            'keuskupan': 'keuskupan',
            'paroki': 'paroki',
            'kota_perkawinan': 'kota_perkawinan',
            'tanggal_perkawinan': 'tanggal_perkawinan',
            'status_perkawinan_detail': 'status_perkawinan_detail',
            'status_keanggotaan': 'status_keanggotaan',
            'wr_tujuan': 'wr_tujuan',
            'paroki_tujuan': 'paroki_tujuan'
        }

        # Dynamically build update clauses (skip user_id and other system fields)
        for field_name, db_column in field_mapping.items():
            if data and field_name in data and data[field_name] not in [None, '']:  # type: ignore
                try:
                    set_clauses.append(f"{db_column} = %s")
                    params.append(data[field_name])  # type: ignore
                except Exception as e:
                    # Log but continue - skip fields that cause issues
                    print(f"[WARNING] Skipping field {field_name}: {e}")
                    continue

        if not set_clauses:
            return jsonify({
                'success': False,
                'data': 'Tidak ada field untuk diupdate'
            }), 400

        # Add updated_at timestamp
        set_clauses.append("updated_at = %s")
        params.append(datetime.datetime.now())

        # Add ID for WHERE clause
        params.append(jemaat_id)

        query = f"UPDATE jemaat SET {', '.join(set_clauses)} WHERE id_jemaat = %s"
        try:
            cursor.execute(query, params)
            connection.commit()

            if cursor.rowcount > 0:
                cursor.close()
                connection.close()
                return jsonify({
                    'success': True,
                    'data': 'Jemaat berhasil diupdate'
                })
            else:
                cursor.close()
                connection.close()
                return jsonify({
                    'success': False,
                    'data': 'Jemaat tidak ditemukan'
                }), 404
        except Exception as inner_e:
            error_msg = str(inner_e)
            if cursor and connection:
                connection.rollback()
                cursor.close()
                connection.close()

            # Provide detailed error message
            if 'Unknown column' in error_msg:
                return jsonify({
                    'success': False,
                    'data': f'Database column error - Missing column. Please run migration: sql/49-ensure_all_jemaat_columns.sql. Error: {error_msg}'
                }), 500
            else:
                return jsonify({'success': False, 'data': f'Database error: {error_msg}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['DELETE'])
def delete_jemaat(jemaat_id):
    """Hapus data jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        query = "DELETE FROM jemaat WHERE id_jemaat = %s"
        cursor.execute(query, (jemaat_id,))
        connection.commit()

        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'success': True,
                'data': 'Jemaat berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'success': False,
                'data': 'Jemaat tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@jemaat_bp.route('/statistics', methods=['GET'])
def get_jemaat_statistics():
    """Ambil statistik jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'data': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Query menggunakan view yang sudah ada
        cursor.execute("SELECT * FROM v_statistik_jemaat")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500