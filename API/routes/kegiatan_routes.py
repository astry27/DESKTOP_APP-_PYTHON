# Path: api/routes/kegiatan_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

kegiatan_bp = Blueprint('kegiatan', __name__, url_prefix='/kegiatan')

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

@kegiatan_bp.route('/my', methods=['GET'])
def get_my_kegiatan():
    """Ambil data kegiatan user sendiri saja"""
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

        # Check if user_id column exists in kegiatan table
        cursor.execute("""
            SELECT COUNT(*) as col_exists
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema = DATABASE()
            AND table_name = 'kegiatan'
            AND column_name = 'user_id'
        """)
        col_check = cursor.fetchone()
        has_user_id = col_check.get('col_exists', 0) > 0 if col_check else False  # type: ignore

        if has_user_id:
            query = """
                SELECT k.*,
                       COALESCE(p.username, 'system') as username,
                       COALESCE(p.nama_lengkap, 'System') as nama_lengkap
                FROM kegiatan k
                LEFT JOIN pengguna p ON k.user_id = p.id_pengguna
                WHERE k.user_id = %s
                ORDER BY k.tanggal_kegiatan DESC
            """
            cursor.execute(query, (user_id,))
        else:
            # Fallback: return empty if user_id column doesn't exist
            query = "SELECT * FROM kegiatan WHERE 1=0"
            cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        connection.close()

        # Convert timedelta and date objects to string for JSON serialization
        for row in result:
            if row.get('waktu_kegiatan') and hasattr(row['waktu_kegiatan'], 'total_seconds'):  # type: ignore
                hours, remainder = divmod(row['waktu_kegiatan'].total_seconds(), 3600)  # type: ignore
                minutes, _ = divmod(remainder, 60)
                row['waktu_kegiatan'] = f"{int(hours):02d}:{int(minutes):02d}"  # type: ignore

            # Convert date fields
            if row.get('tanggal_kegiatan') and hasattr(row['tanggal_kegiatan'], 'isoformat'):  # type: ignore
                row['tanggal_kegiatan'] = row['tanggal_kegiatan'].isoformat()  # type: ignore
            if row.get('created_at') and hasattr(row['created_at'], 'isoformat'):  # type: ignore
                row['created_at'] = row['created_at'].isoformat()  # type: ignore
            if row.get('updated_at') and hasattr(row['updated_at'], 'isoformat'):  # type: ignore
                row['updated_at'] = row['updated_at'].isoformat()  # type: ignore

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_my_kegiatan: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@kegiatan_bp.route('', methods=['GET'])
def get_kegiatan():
    """Ambil semua data kegiatan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        kategori = request.args.get('kategori')
        status = request.args.get('status')
        user_id = request.args.get('user_id')

        cursor = connection.cursor(dictionary=True)

        # Check if user_id column exists in kegiatan table
        cursor.execute("""
            SELECT COUNT(*) as col_exists
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema = DATABASE()
            AND table_name = 'kegiatan'
            AND column_name = 'user_id'
        """)
        col_check = cursor.fetchone()
        has_user_id = col_check.get('col_exists', 0) > 0 if col_check else False  # type: ignore

        # Build query - with or without user_id depending on column existence
        if has_user_id:
            query = """
                SELECT k.*,
                       COALESCE(p.username, 'admin') as username,
                       COALESCE(p.nama_lengkap, 'Admin') as nama_lengkap
                FROM kegiatan k
                LEFT JOIN pengguna p ON k.user_id = p.id_pengguna
            """
        else:
            # Without user_id column, just select from kegiatan
            query = """
                SELECT k.*,
                       'admin' as username,
                       'Admin' as nama_lengkap
                FROM kegiatan k
            """

        conditions = []
        params = []

        if start_date:
            conditions.append("k.tanggal_kegiatan >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("k.tanggal_kegiatan <= %s")  # Gunakan tanggal_kegiatan, bukan NULL yang sudah dihapus
            params.append(end_date)

        if kategori:
            conditions.append("k.kategori = %s")
            params.append(kategori)

        if status:
            conditions.append("k.status = %s")
            params.append(status)

        if user_id and has_user_id:
            conditions.append("k.user_id = %s")
            params.append(user_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY k.tanggal_kegiatan DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        # Convert timedelta and date objects to string for JSON serialization
        for row in result:
            if row.get('waktu_kegiatan') and hasattr(row['waktu_kegiatan'], 'total_seconds'):  # type: ignore
                hours, remainder = divmod(row['waktu_kegiatan'].total_seconds(), 3600)  # type: ignore
                minutes, _ = divmod(remainder, 60)
                row['waktu_kegiatan'] = f"{int(hours):02d}:{int(minutes):02d}"  # type: ignore

            # Convert date fields
            if row.get('tanggal_kegiatan') and hasattr(row['tanggal_kegiatan'], 'isoformat'):  # type: ignore
                row['tanggal_kegiatan'] = row['tanggal_kegiatan'].isoformat()  # type: ignore
            if row.get('created_at') and hasattr(row['created_at'], 'isoformat'):  # type: ignore
                row['created_at'] = row['created_at'].isoformat()  # type: ignore
            if row.get('updated_at') and hasattr(row['updated_at'], 'isoformat'):  # type: ignore
                row['updated_at'] = row['updated_at'].isoformat()  # type: ignore

        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_kegiatan: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@kegiatan_bp.route('', methods=['POST'])
def add_kegiatan():
    """Tambah kegiatan baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Request body is required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)

        # Check if user_id column exists in kegiatan table
        cursor.execute("""
            SELECT COUNT(*) as col_exists
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema = DATABASE()
            AND table_name = 'kegiatan'
            AND column_name = 'user_id'
        """)
        col_check = cursor.fetchone()
        has_user_id = col_check.get('col_exists', 0) > 0 if col_check else False  # type: ignore

        # Support both old and new field names
        nama_kegiatan = data.get('nama_kegiatan')
        deskripsi = data.get('deskripsi')
        lokasi = data.get('lokasi') or data.get('tempat')
        tanggal_kegiatan = data.get('tanggal_kegiatan') or data.get('tanggal')
        NULL = data.get('NULL') or data.get('tanggal')
        waktu_kegiatan = data.get('waktu_kegiatan') or data.get('waktu')
        waktu_selesai = data.get('waktu_selesai') or data.get('waktu')
        penanggungjawab = data.get('penanggungjawab') or data.get('dibuat_oleh')
        kategori = data.get('kategori', 'Lainnya')
        status = data.get('status', 'Direncanakan')
        user_id = data.get('user_id')

        # Validate required fields
        if not nama_kegiatan:
            return jsonify({'status': 'error', 'message': 'nama_kegiatan is required'}), 400
        if not tanggal_kegiatan:
            return jsonify({'status': 'error', 'message': 'tanggal_kegiatan is required'}), 400

        # Build query based on column existence
        if has_user_id:
            query = """
            INSERT INTO kegiatan (nama_kegiatan, deskripsi, lokasi, tanggal_kegiatan,
                                 NULL, waktu_kegiatan, waktu_selesai,
                                 penanggungjawab, kategori, status, max_peserta, biaya, keterangan, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                nama_kegiatan,
                deskripsi,
                lokasi,
                tanggal_kegiatan,
                NULL,
                waktu_kegiatan,
                waktu_selesai,
                penanggungjawab,
                kategori,
                status,
                data.get('max_peserta'),
                data.get('biaya', 0),
                data.get('keterangan'),
                user_id
            )
        else:
            # Without user_id column
            query = """
            INSERT INTO kegiatan (nama_kegiatan, deskripsi, lokasi, tanggal_kegiatan,
                                 NULL, waktu_kegiatan, waktu_selesai,
                                 penanggungjawab, kategori, status, max_peserta, biaya, keterangan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                nama_kegiatan,
                deskripsi,
                lokasi,
                tanggal_kegiatan,
                NULL,
                waktu_kegiatan,
                waktu_selesai,
                penanggungjawab,
                kategori,
                status,
                data.get('max_peserta'),
                data.get('biaya', 0),
                data.get('keterangan')
            )

        cursor.execute(query, params)
        connection.commit()

        kegiatan_id = cursor.lastrowid

        return jsonify({
            'status': 'success',
            'message': 'Kegiatan berhasil ditambahkan',
            'id': kegiatan_id
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in add_kegiatan: {error_details}")
        try:
            connection.rollback()
        except:
            pass
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@kegiatan_bp.route('/<int:kegiatan_id>', methods=['GET'])
def get_kegiatan_by_id(kegiatan_id):
    """Ambil kegiatan berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM kegiatan WHERE id_kegiatan = %s"
        cursor.execute(query, (kegiatan_id,))
        result = cursor.fetchone()

        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Kegiatan tidak ditemukan'
            }), 404
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_kegiatan_by_id: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@kegiatan_bp.route('/<int:kegiatan_id>', methods=['PUT'])
def update_kegiatan(kegiatan_id):
    """Update kegiatan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Request body is required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        cursor = connection.cursor()

        # Support both old and new field names
        nama_kegiatan = data.get('nama_kegiatan')
        deskripsi = data.get('deskripsi')
        lokasi = data.get('lokasi') or data.get('tempat')
        tanggal_kegiatan = data.get('tanggal_kegiatan') or data.get('tanggal')
        NULL = data.get('NULL') or data.get('tanggal')
        waktu_kegiatan = data.get('waktu_kegiatan') or data.get('waktu')
        waktu_selesai = data.get('waktu_selesai') or data.get('waktu')
        penanggungjawab = data.get('penanggungjawab') or data.get('dibuat_oleh')
        kategori = data.get('kategori')
        status = data.get('status', 'Direncanakan')

        query = """
        UPDATE kegiatan SET
            nama_kegiatan = %s, deskripsi = %s, lokasi = %s,
            tanggal_kegiatan = %s, NULL = %s, waktu_kegiatan = %s,
            waktu_selesai = %s, penanggungjawab = %s, kategori = %s,
            status = %s, max_peserta = %s, biaya = %s, keterangan = %s,
            updated_at = %s
        WHERE id_kegiatan = %s
        """
        params = (
            nama_kegiatan,
            deskripsi,
            lokasi,
            tanggal_kegiatan,
            NULL,
            waktu_kegiatan,
            waktu_selesai,
            penanggungjawab,
            kategori,
            status,
            data.get('max_peserta'),
            data.get('biaya'),
            data.get('keterangan'),
            datetime.datetime.now(),
            kegiatan_id
        )
        cursor.execute(query, params)
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({
                'status': 'success',
                'message': 'Kegiatan berhasil diupdate'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Kegiatan tidak ditemukan'
            }), 404
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in update_kegiatan: {error_details}")
        try:
            connection.rollback()
        except:
            pass
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@kegiatan_bp.route('/<int:kegiatan_id>', methods=['DELETE'])
def delete_kegiatan(kegiatan_id):
    """Hapus kegiatan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM kegiatan WHERE id_kegiatan = %s"
        cursor.execute(query, (kegiatan_id,))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({
                'status': 'success',
                'message': 'Kegiatan berhasil dihapus'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Kegiatan tidak ditemukan'
            }), 404
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in delete_kegiatan: {error_details}")
        try:
            connection.rollback()
        except:
            pass
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@kegiatan_bp.route('/mendatang', methods=['GET'])
def get_kegiatan_mendatang():
    """Ambil kegiatan mendatang menggunakan view"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        limit = request.args.get('limit', 10, type=int)

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM v_kegiatan_mendatang LIMIT %s"
        cursor.execute(query, (limit,))
        result = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_kegiatan_mendatang: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@kegiatan_bp.route('/wr/all', methods=['GET'])
def get_kegiatan_wr_all():
    """Ambil semua kegiatan dari WR (Warga/Client) dengan informasi user"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)

        # Check if user_id column exists in kegiatan table
        cursor.execute("""
            SELECT COUNT(*) as col_exists
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema = DATABASE()
            AND table_name = 'kegiatan'
            AND column_name = 'user_id'
        """)
        col_check = cursor.fetchone()
        has_user_id = col_check.get('col_exists', 0) > 0 if col_check else False  # type: ignore

        if has_user_id:
            # Query untuk mendapatkan semua kegiatan dengan informasi user
            query = """
            SELECT k.*, p.username, p.nama_lengkap, p.peran
            FROM kegiatan k
            LEFT JOIN pengguna p ON k.user_id = p.id_pengguna
            WHERE k.user_id IS NOT NULL
            ORDER BY k.tanggal_kegiatan DESC
            """
        else:
            # Without user_id, return empty array (kegiatan WR tidak ada tanpa kolom user_id)
            return jsonify({'status': 'success', 'data': []})

        cursor.execute(query)
        result = cursor.fetchall()

        # Transform data to match client expectations
        transformed_data = []
        for row in result:
            transformed_data.append({
                'id_kegiatan': row.get('id_kegiatan'),
                'nama_kegiatan': row.get('nama_kegiatan'),
                'deskripsi': row.get('deskripsi'),
                'tempat': row.get('lokasi'),
                'tanggal': row.get('tanggal_kegiatan'),
                'waktu': row.get('waktu_kegiatan'),
                'kategori': row.get('kategori'),
                'dibuat_oleh': row.get('penanggungjawab'),
                'user_id': row.get('user_id'),
                'username': row.get('username'),
                'nama_lengkap': row.get('nama_lengkap'),
                'peran': row.get('peran'),
                'created_at': row.get('created_at'),
                # Keep original fields for backward compatibility
                'lokasi': row.get('lokasi'),
                'tanggal_kegiatan': row.get('tanggal_kegiatan'),
                'NULL': row.get('NULL'),
                'waktu_kegiatan': row.get('waktu_kegiatan'),
                'waktu_selesai': row.get('waktu_selesai'),
                'penanggungjawab': row.get('penanggungjawab'),
                'status': row.get('status'),
                'max_peserta': row.get('max_peserta'),
                'biaya': row.get('biaya'),
                'keterangan': row.get('keterangan')
            })

        return jsonify({
            'status': 'success',
            'data': transformed_data
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_kegiatan_wr_all: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()