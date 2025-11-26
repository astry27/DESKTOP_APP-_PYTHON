# Path: routes/struktur_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

struktur_bp = Blueprint('struktur', __name__, url_prefix='/struktur')

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

@struktur_bp.route('', methods=['GET'])
def get_struktur():
    """Ambil semua data struktur organisasi"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        search = request.args.get('search', '')
        level = request.args.get('level', type=int)
        status_aktif = request.args.get('status', 'Aktif')
        
        cursor = connection.cursor(dictionary=True)
        
        # Build query dengan filter
        base_query = """
        SELECT * FROM struktur 
        WHERE 1=1
        """
        params = []
        
        if search:
            base_query += """ AND (
                nama_lengkap LIKE %s OR
                jabatan_utama LIKE %s OR
                wilayah_rohani LIKE %s OR
                email LIKE %s OR
                telepon LIKE %s
            )"""
            search_param = f'%{search}%'
            params.extend([search_param] * 5)
            
        if status_aktif and status_aktif != 'Semua':
            base_query += " AND status_aktif = %s"
            params.append(status_aktif)
        
        base_query += " ORDER BY nama_lengkap ASC"
        
        cursor.execute(base_query, params)
        struktur_list = cursor.fetchall()
        
        # Convert dates to string untuk JSON serialization
        for struktur in struktur_list:
            if struktur.get('created_at'):
                struktur['created_at'] = struktur['created_at'].isoformat()  # type: ignore
            if struktur.get('updated_at'):
                struktur['updated_at'] = struktur['updated_at'].isoformat()  # type: ignore
        
        return jsonify({
            'status': 'success',
            'data': struktur_list,
            'total': len(struktur_list)
        })
        
    except Exception as e:
        print(f"Error getting struktur: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('', methods=['POST'])
def add_struktur():
    """Tambah data struktur baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        data = request.get_json()
        
        # Validasi required fields
        required_fields = ['nama_lengkap', 'jabatan_utama']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error', 
                    'message': f'Field {field} diperlukan'
                }), 400
        
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO struktur (
            nama_lengkap, jenis_kelamin, wilayah_rohani,
            jabatan_utama, status_aktif, email, telepon, periode, foto_path
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        params = (
            data.get('nama_lengkap'),
            data.get('jenis_kelamin'),
            data.get('wilayah_rohani'),
            data.get('jabatan_utama'),
            data.get('status_aktif', 'Aktif'),
            data.get('email'),
            data.get('telepon'),
            data.get('periode'),
            data.get('foto_path')
        )
        
        cursor.execute(insert_query, params)
        connection.commit()
        
        struktur_id = cursor.lastrowid
        
        return jsonify({
            'status': 'success',
            'message': 'Data struktur berhasil ditambahkan',
            'id': struktur_id
        })
        
    except Exception as e:
        print(f"Error adding struktur: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('/<int:struktur_id>', methods=['GET'])
def get_struktur_by_id(struktur_id):
    """Ambil data struktur berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM struktur WHERE id_struktur = %s", (struktur_id,))
        struktur = cursor.fetchone()
        
        if not struktur:
            return jsonify({'status': 'error', 'message': 'Data struktur tidak ditemukan'}), 404
        
        # Convert dates to string
        if struktur.get('created_at'):
            struktur['created_at'] = struktur['created_at'].isoformat()  # type: ignore
        if struktur.get('updated_at'):
            struktur['updated_at'] = struktur['updated_at'].isoformat()  # type: ignore
        
        return jsonify({
            'status': 'success',
            'data': struktur
        })
        
    except Exception as e:
        print(f"Error getting struktur by ID: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('/<int:struktur_id>', methods=['PUT'])
def update_struktur(struktur_id):
    """Update data struktur"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        data = request.get_json()
        
        cursor = connection.cursor()
        
        # Check if struktur exists
        cursor.execute("SELECT id_struktur FROM struktur WHERE id_struktur = %s", (struktur_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Data struktur tidak ditemukan'}), 404
        
        update_query = """
        UPDATE struktur SET
            nama_lengkap = %s, jenis_kelamin = %s, wilayah_rohani = %s,
            jabatan_utama = %s, status_aktif = %s, email = %s,
            telepon = %s, periode = %s, foto_path = %s, updated_at = NOW()
        WHERE id_struktur = %s
        """

        params = (
            data.get('nama_lengkap'),
            data.get('jenis_kelamin'),
            data.get('wilayah_rohani'),
            data.get('jabatan_utama'),
            data.get('status_aktif', 'Aktif'),
            data.get('email'),
            data.get('telepon'),
            data.get('periode'),
            data.get('foto_path'),
            struktur_id
        )
        
        cursor.execute(update_query, params)
        connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Data struktur berhasil diupdate'
        })
        
    except Exception as e:
        print(f"Error updating struktur: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('/<int:struktur_id>', methods=['DELETE'])
def delete_struktur(struktur_id):
    """Hapus data struktur"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if struktur exists
        cursor.execute("SELECT nama_lengkap FROM struktur WHERE id_struktur = %s", (struktur_id,))
        struktur = cursor.fetchone() # type: ignore
        if not struktur:
            return jsonify({'status': 'error', 'message': 'Data struktur tidak ditemukan'}), 404
        
        cursor.execute("DELETE FROM struktur WHERE id_struktur = %s", (struktur_id,))
        connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Data struktur {struktur[0]} berhasil dihapus'  # type: ignore
        })
        
    except Exception as e:
        print(f"Error deleting struktur: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('/<int:struktur_id>/upload-photo', methods=['POST'])
def upload_struktur_photo(struktur_id):
    """Upload foto untuk struktur tertentu"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        # Check if struktur exists
        cursor = connection.cursor()
        cursor.execute("SELECT id_struktur, nama_lengkap FROM struktur WHERE id_struktur = %s", (struktur_id,))
        struktur = cursor.fetchone()
        if not struktur:
            return jsonify({'status': 'error', 'message': 'Struktur tidak ditemukan'}), 404

        # Check if file is uploaded
        if 'photo' not in request.files:
            return jsonify({'status': 'error', 'message': 'Tidak ada file foto yang diupload'}), 400

        file = request.files['photo']
        if not file.filename or file.filename == '':
            return jsonify({'status': 'error', 'message': 'Tidak ada file yang dipilih'}), 400

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        filename = file.filename  # Already validated as not None above
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'status': 'error', 'message': 'Tipe file tidak diizinkan. Gunakan: PNG, JPG, JPEG, GIF, BMP'}), 400

        # Create upload directory if not exists
        import os
        upload_dir = 'uploads/struktur'
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        import uuid
        from datetime import datetime
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"struktur_{struktur_id}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Update database with photo path
        cursor.execute(
            "UPDATE struktur SET foto_path = %s, updated_at = NOW() WHERE id_struktur = %s", 
            (file_path, struktur_id)
        )
        connection.commit()
        
        # Generate full photo URL with domain
        import os
        base_url = os.getenv('HOST', '')
        photo_url = f"{base_url}/uploads/struktur/{unique_filename}"
        
        return jsonify({
            'status': 'success',
            'message': f'Foto berhasil diupload untuk {struktur[1]}',  # type: ignore
            'photo_path': photo_url,
            'photo_url': photo_url
        })
        
    except Exception as e:
        print(f"Error uploading struktur photo: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@struktur_bp.route('/upload-photo', methods=['POST'])
def upload_struktur_photo_new():
    """Upload foto untuk struktur baru (sebelum disimpan)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    try:
        # Check if file is uploaded
        if 'photo' not in request.files:
            return jsonify({'status': 'error', 'message': 'Tidak ada file foto yang diupload'}), 400

        file = request.files['photo']
        if not file.filename or file.filename == '':
            return jsonify({'status': 'error', 'message': 'Tidak ada file yang dipilih'}), 400

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        filename = file.filename  # Already validated as not None above
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'status': 'error', 'message': 'Tipe file tidak diizinkan. Gunakan: PNG, JPG, JPEG, GIF, BMP'}), 400

        # Create upload directory if not exists
        import os
        upload_dir = 'uploads/struktur'
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        import uuid
        from datetime import datetime
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"struktur_new_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Generate full photo URL with domain
        import os
        base_url = os.getenv('HOST', '')
        photo_url = f"{base_url}/uploads/struktur/{unique_filename}"
        
        return jsonify({
            'status': 'success',
            'message': 'Foto berhasil diupload',
            'photo_path': photo_url,
            'photo_url': photo_url
        })
        
    except Exception as e:
        print(f"Error uploading new struktur photo: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@struktur_bp.route('/statistics', methods=['GET'])
def get_struktur_statistics():
    """Ambil statistik struktur organisasi"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total struktur aktif
        cursor.execute("SELECT COUNT(*) as total FROM struktur WHERE status_aktif = 'Aktif'")
        total_result = cursor.fetchone()
        total_aktif = total_result.get('total', 0) if total_result else 0

        # Struktur per jabatan
        cursor.execute("""
            SELECT jabatan_utama, COUNT(*) as jumlah
            FROM struktur
            WHERE status_aktif = 'Aktif' AND jabatan_utama IS NOT NULL
            GROUP BY jabatan_utama
            ORDER BY jumlah DESC
            LIMIT 10
        """)
        per_jabatan = cursor.fetchall()

        # Struktur per wilayah rohani
        cursor.execute("""
            SELECT wilayah_rohani, COUNT(*) as jumlah
            FROM struktur
            WHERE status_aktif = 'Aktif' AND wilayah_rohani IS NOT NULL
            GROUP BY wilayah_rohani
            ORDER BY jumlah DESC
        """)
        per_wilayah = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': {
                'total_aktif': total_aktif,
                'per_jabatan': per_jabatan,
                'per_wilayah': per_wilayah
            }
        })
        
    except Exception as e:
        print(f"Error getting struktur statistics: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()