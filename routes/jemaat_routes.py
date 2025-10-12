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
            'status': 'error', 
            'message': 'API sedang dinonaktifkan'
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
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM jemaat WHERE created_by_pengguna = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@jemaat_bp.route('', methods=['POST'])
def add_jemaat():
    """Tambah data jemaat baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()

        fields = ['created_by_pengguna']
        values = [data.get('user_id')]

        field_mapping = {
            'nama_lengkap': 'nama_lengkap',
            'alamat': 'alamat',
            'email': 'email',
            'tanggal_lahir': 'tanggal_lahir',
            'jenis_kelamin': 'jenis_kelamin',
            'wilayah_rohani': 'wilayah_rohani',
            'nama_keluarga': 'nama_keluarga',
            'tempat_lahir': 'tempat_lahir',
            'umur': 'umur',
            'kategori': 'kategori',
            'hubungan_keluarga': 'hubungan_keluarga',
            'pendidikan_terakhir': 'pendidikan_terakhir',
            'status_menikah': 'status_menikah',
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
            'status_keanggotaan': 'status_keanggotaan',
            'wr_tujuan': 'wr_tujuan',
            'paroki_tujuan': 'paroki_tujuan',
            'tanggal_bergabung': 'tanggal_bergabung'
        }

        for field_name, db_column in field_mapping.items():
            if field_name in data and data[field_name] not in [None, '']:
                fields.append(db_column)
                values.append(data[field_name])

        query = f"INSERT INTO jemaat ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(values))})"
        params = tuple(values)
        cursor.execute(query, params)
        connection.commit()
        
        jemaat_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Jemaat berhasil ditambahkan',
            'id': jemaat_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['GET'])
def get_jemaat_by_id(jemaat_id):
    """Ambil data jemaat berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM jemaat WHERE id_jemaat = %s"
        cursor.execute(query, (jemaat_id,))
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
                'message': 'Jemaat tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['PUT'])
def update_jemaat(jemaat_id):
    """Update data jemaat"""
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
        UPDATE jemaat SET 
            nama_lengkap = %s, alamat = %s, no_telepon = %s, email = %s, 
            tanggal_lahir = %s, jenis_kelamin = %s, status_pernikahan = %s,
            pekerjaan = %s, pendidikan = %s, baptis_tanggal = %s, baptis_tempat = %s,
            komuni_tanggal = %s, komuni_tempat = %s, krisma_tanggal = %s, krisma_tempat = %s,
            nama_ayah = %s, nama_ibu = %s, lingkungan = %s, wilayah = %s,
            keterangan = %s, updated_at = %s
        WHERE id_jemaat = %s
        """
        params = (
            data.get('nama_lengkap'),
            data.get('alamat'),
            data.get('no_telepon'),
            data.get('email'),
            data.get('tanggal_lahir'),
            data.get('jenis_kelamin'),
            data.get('status_pernikahan'),
            data.get('pekerjaan'),
            data.get('pendidikan'),
            data.get('baptis_tanggal'),
            data.get('baptis_tempat'),
            data.get('komuni_tanggal'),
            data.get('komuni_tempat'),
            data.get('krisma_tanggal'),
            data.get('krisma_tempat'),
            data.get('nama_ayah'),
            data.get('nama_ibu'),
            data.get('lingkungan'),
            data.get('wilayah'),
            data.get('keterangan'),
            datetime.datetime.now(),
            jemaat_id
        )
        cursor.execute(query, params)
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Jemaat berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Jemaat tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@jemaat_bp.route('/<int:jemaat_id>', methods=['DELETE'])
def delete_jemaat(jemaat_id):
    """Hapus data jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        query = "DELETE FROM jemaat WHERE id_jemaat = %s"
        cursor.execute(query, (jemaat_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Jemaat berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Jemaat tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@jemaat_bp.route('/statistics', methods=['GET'])
def get_jemaat_statistics():
    """Ambil statistik jemaat"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query menggunakan view yang sudah ada
        cursor.execute("SELECT * FROM v_statistik_jemaat")
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500