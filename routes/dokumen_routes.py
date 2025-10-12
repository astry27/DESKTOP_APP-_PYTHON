# Path: api/routes/dokumen_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

dokumen_bp = Blueprint('dokumen', __name__)

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

@dokumen_bp.route('/files', methods=['GET'])
def get_files():
    """Ambil semua data file/dokumen"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        kategori = request.args.get('kategori')
        
        cursor = connection.cursor(dictionary=True)
        
        # Query dengan JOIN untuk mendapatkan nama uploader
        query = """
        SELECT d.*, 
               COALESCE(a.nama_lengkap, p.nama_lengkap, 'Unknown') as uploaded_by_name
        FROM dokumen d
        LEFT JOIN admin a ON d.uploaded_by_admin = a.id_admin
        LEFT JOIN pengguna p ON d.uploaded_by_pengguna = p.id_pengguna
        """
        params = []
        
        if kategori:
            query += " WHERE d.kategori = %s"
            params.append(kategori)
        
        query += " ORDER BY d.upload_date DESC LIMIT %s OFFSET %s"
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

@dokumen_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload file/dokumen baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        # Ambil metadata dari form
        jenis_dokumen = request.form.get('jenis_dokumen', 'Administrasi')
        kategori = request.form.get('kategori', 'Lainnya')
        keterangan = request.form.get('keterangan', '')
        uploaded_by_admin = request.form.get('uploaded_by_admin')
        uploaded_by_pengguna = request.form.get('uploaded_by_pengguna')
        uploaded_by_name = request.form.get('uploaded_by_name', 'Administrator')
        
        filename = file.filename
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        # Simpan file ke direktori uploads (jika ada)
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, filename)
        # file.save(file_path)  # Uncomment jika ingin simpan file fisik
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': 'Database error'}), 500
        
        cursor = connection.cursor()
        query = """
        INSERT INTO dokumen (nama_dokumen, jenis_dokumen, file_path, ukuran_file, tipe_file,
                            kategori, keterangan, uploaded_by_admin, uploaded_by_pengguna, uploaded_by_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            filename,
            jenis_dokumen,
            file_path,
            file_size,
            file.content_type,
            kategori,
            keterangan,
            uploaded_by_admin if uploaded_by_admin else None,
            uploaded_by_pengguna if uploaded_by_pengguna else None,
            uploaded_by_name
        )
        cursor.execute(query, params)
        connection.commit()
        
        doc_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'File berhasil diupload',
            'file_id': doc_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@dokumen_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file_by_id(file_id):
    """Ambil data file berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT d.*, 
               COALESCE(a.nama_lengkap, p.nama_lengkap, 'Unknown') as uploaded_by_name
        FROM dokumen d
        LEFT JOIN admin a ON d.uploaded_by_admin = a.id_admin
        LEFT JOIN pengguna p ON d.uploaded_by_pengguna = p.id_pengguna
        WHERE d.id_dokumen = %s
        """
        cursor.execute(query, (file_id,))
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
                'message': 'File tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@dokumen_bp.route('/files/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    """Update metadata file"""
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
        UPDATE dokumen SET
            nama_dokumen = %s, jenis_dokumen = %s, kategori = %s, keterangan = %s
        WHERE id_dokumen = %s
        """
        params = (
            data.get('nama_dokumen'),
            data.get('jenis_dokumen', 'Administrasi'),
            data.get('kategori'),
            data.get('keterangan'),
            file_id
        )
        cursor.execute(query, params)
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'File berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'File tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@dokumen_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Hapus file/dokumen"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        # Ambil info file untuk hapus file fisik jika perlu
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT file_path FROM dokumen WHERE id_dokumen = %s", (file_id,))
        file_info = cursor.fetchone()
        
        if not file_info:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'File tidak ditemukan'
            }), 404
        
        # Hapus record dari database
        cursor.execute("DELETE FROM dokumen WHERE id_dokumen = %s", (file_id,))
        connection.commit()
        
        # Hapus file fisik jika ada dan exists
        file_path = file_info['file_path']
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting physical file: {e}")
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'File berhasil dihapus'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@dokumen_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download file (metadata saja untuk API)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM dokumen WHERE id_dokumen = %s"
        cursor.execute(query, (file_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'File info untuk download',
                'data': {
                    'nama_dokumen': result['nama_dokumen'],
                    'file_path': result['file_path'],
                    'ukuran_file': result['ukuran_file'],
                    'tipe_file': result['tipe_file']
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'File tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500