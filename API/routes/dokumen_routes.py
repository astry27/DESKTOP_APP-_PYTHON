# Path: api/routes/dokumen_routes.py

from flask import Blueprint, jsonify, request, send_file
from config import get_db_connection
import datetime
import os

dokumen_bp = Blueprint('dokumen', __name__, url_prefix='/dokumen')

API_STATUS_FILE = 'api_status.txt'

def get_api_status():
    """Check if API is enabled - default to True if file doesn't exist"""
    try:
        if os.path.exists(API_STATUS_FILE):
            with open(API_STATUS_FILE, 'r') as f:
                content = f.read().strip()
                return content == 'enabled'
        # Default to True jika file tidak ada
        return True
    except Exception as e:
        print(f"Error reading API status: {e}")
        # Default to True jika ada error
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
        kategori_file = request.args.get('kategori_file')

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT d.*,
               COALESCE(a.nama_lengkap, 'Unknown') as uploaded_by_name
        FROM dokumen d
        LEFT JOIN admin a ON d.uploaded_by_admin = a.id_admin
        """
        params = []

        if kategori_file:
            query += " WHERE d.kategori_file = %s"
            params.append(kategori_file)

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
    """Upload file/dokumen baru - sesuai pola struktur_dpp"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    # Check file exists
    if 'file' not in request.files:
        return jsonify({'success': False, 'data': 'Tidak ada file yang diupload'}), 400

    file = request.files['file']
    if not file.filename or file.filename == '':
        return jsonify({'success': False, 'data': 'Tidak ada file yang dipilih'}), 400

    try:
        # Ambil metadata dari form
        nama_dokumen = request.form.get('nama_dokumen', file.filename)
        bentuk_dokumen = request.form.get('bentuk_dokumen', 'Lainnya')
        kategori_file = request.form.get('kategori_file', bentuk_dokumen)
        keterangan = request.form.get('keterangan', '')
        uploaded_by_admin = request.form.get('uploaded_by_admin')  # Optional admin ID

        # Connection ke database
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'data': 'Database error'}), 500

        # Disable foreign key check untuk insert (akan re-enable setelah)
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")

        # Baca file dan hitung size
        file_content = file.read()
        file_size = len(file_content)
        file.seek(0)

        # Buat direktori uploads jika belum ada
        import uuid
        from datetime import datetime
        upload_dir = 'uploads/dokumen'
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename sesuai pola struktur
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'bin'  # type: ignore
        unique_filename = f"dokumen_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save file ke disk
        file.save(file_path)

        # Insert ke database - include uploaded_by_admin if provided
        if uploaded_by_admin:
            query = """
            INSERT INTO dokumen (nama_dokumen, bentuk_dokumen, kategori_file, file_path, ukuran_file, keterangan, upload_date, uploaded_by_admin)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """
            params = (
                nama_dokumen,
                bentuk_dokumen,
                kategori_file,
                file_path,
                file_size,
                keterangan,
                uploaded_by_admin
            )
        else:
            query = """
            INSERT INTO dokumen (nama_dokumen, bentuk_dokumen, kategori_file, file_path, ukuran_file, keterangan, upload_date)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            params = (
                nama_dokumen,
                bentuk_dokumen,
                kategori_file,
                file_path,
                file_size,
                keterangan
            )
        cursor.execute(query, params)
        connection.commit()

        # Re-enable foreign key check
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        connection.commit()

        doc_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'data': {
                'file_id': doc_id,
                'message': 'File berhasil diupload',
                'file_path': file_path
            }
        })
    except Exception as e:
        print(f"Error uploading dokumen: {e}")
        import traceback
        traceback.print_exc()
        try:
            if connection and connection.is_connected():
                connection.close()
        except:
            pass
        return jsonify({'success': False, 'data': f'Upload error: {str(e)}'}), 500

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
               COALESCE(a.nama_lengkap, 'Unknown') as uploaded_by_name
        FROM dokumen d
        LEFT JOIN admin a ON d.uploaded_by_admin = a.id_admin
        WHERE d.id_dokumen = %s
        """
        cursor.execute(query, (file_id,))
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
                'data': 'File tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

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
            nama_dokumen = %s, jenis_dokumen = %s, kategori_file = %s, keterangan_lengkap = %s
        WHERE id_dokumen = %s
        """
        params = (
            data.get('nama_dokumen'),
            data.get('jenis_dokumen', 'Administrasi'),
            data.get('kategori_file'),
            data.get('keterangan_lengkap'),
            file_id
        )
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()

        if cursor.rowcount > 0:
            return jsonify({
                'success': True,
                'data': 'File berhasil diupdate'
            })
        else:
            return jsonify({
                'success': False,
                'data': 'File tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

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
                'success': False,
                'data': 'File tidak ditemukan'
            }), 404

        # Hapus record dari database
        cursor.execute("DELETE FROM dokumen WHERE id_dokumen = %s", (file_id,))
        connection.commit()

        # Hapus file fisik jika ada dan exists
        file_path = file_info['file_path']  # type: ignore
        if file_path and os.path.exists(str(file_path)):  # type: ignore
            try:
                os.remove(str(file_path))  # type: ignore
            except Exception as e:
                print(f"Error deleting physical file: {e}")

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'data': 'File berhasil dihapus'
        })
    except Exception as e:
        return jsonify({'success': False, 'data': str(e)}), 500

@dokumen_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download actual file content"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id_dokumen, nama_dokumen, file_path, ukuran_file, bentuk_dokumen FROM dokumen WHERE id_dokumen = %s"
        cursor.execute(query, (file_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if not result:
            return jsonify({
                'status': 'error',
                'message': 'File tidak ditemukan'
            }), 404

        file_path = result['file_path']  # type: ignore
        nama_dokumen = result['nama_dokumen']  # type: ignore

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': f'File tidak ditemukan di server: {file_path}'
            }), 404

        # Read file content
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Send file as binary data
            return send_file(
                file_path,
                as_attachment=True,
                download_name=nama_dokumen,
                mimetype='application/octet-stream'
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Gagal membaca file: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500