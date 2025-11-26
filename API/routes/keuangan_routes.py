# Path: api/routes/keuangan_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

keuangan_bp = Blueprint('keuangan', __name__, url_prefix='/keuangan')

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

@keuangan_bp.route('/my', methods=['GET'])
def get_my_keuangan():
    """Ambil data keuangan user sendiri saja"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    user_id = request.args.get('user_id', type=int)
    print(f"[DEBUG API] /keuangan/my called with user_id: {user_id}")

    if not user_id:
        print("[ERROR API] user_id required but not provided")
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    connection = get_db_connection()
    if not connection:
        print("[ERROR API] Database connection failed")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Query dengan backward compatibility - tidak include deskripsi jika tidak ada
        query = """
            SELECT k.id_keuangan, k.tanggal, k.kategori as jenis, k.sub_kategori as kategori,
                   k.keterangan, k.jumlah, k.created_at, k.created_by_pengguna,
                   COALESCE(p.username, 'system') as dibuat_oleh,
                   COALESCE(p.nama_lengkap, 'System') as nama_user
            FROM keuangan k
            LEFT JOIN pengguna p ON k.created_by_pengguna = p.id_pengguna
            WHERE k.created_by_pengguna = %s
            ORDER BY k.tanggal DESC
        """

        print(f"[DEBUG API] Executing query for user_id: {user_id}")
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        print(f"[DEBUG API] Query returned {len(result)} records")
        if result:
            print(f"[DEBUG API] First record: {result[0]}")

        cursor.close()
        connection.close()

        response = {'status': 'success', 'data': result}
        print(f"[DEBUG API] Returning response with {len(result)} records")
        return jsonify(response)

    except Exception as e:
        print(f"[ERROR API] Exception in get_my_keuangan: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('', methods=['GET'])
def get_keuangan():
    """Ambil semua data keuangan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        kategori = request.args.get('kategori')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        sub_kategori = request.args.get('sub_kategori')

        cursor = connection.cursor(dictionary=True)

        # Check user permissions
        user_id = request.args.get('user_id', type=int)
        is_admin = request.args.get('is_admin', 'false').lower() == 'true'

        # Build query dengan error handling untuk kolom yang mungkin tidak ada
        # Safe column selection - hanya ambil kolom yang pasti ada
        # Fallback untuk created_by_pengguna jika tidak ada di database
        query = """
        SELECT k.id_keuangan, k.tanggal, k.kategori, k.sub_kategori, k.keterangan,
               k.jumlah, k.created_at,
               COALESCE(k.created_by_pengguna, 0) as created_by_pengguna,
               COALESCE(p.username, 'system') as dibuat_oleh,
               COALESCE(p.nama_lengkap, 'System') as nama_user
        FROM keuangan k
        LEFT JOIN pengguna p ON k.created_by_pengguna = p.id_pengguna
        """
        conditions = []
        params = []

        if kategori:
            conditions.append("k.kategori = %s")
            params.append(kategori)

        if sub_kategori:
            conditions.append("k.sub_kategori = %s")
            params.append(sub_kategori)

        if start_date:
            conditions.append("k.tanggal >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("k.tanggal <= %s")
            params.append(end_date)

        # User isolation: non-admin only see their own data
        if not is_admin and user_id:
            conditions.append("k.created_by_pengguna = %s")
            params.append(user_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY k.tanggal DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        print(f"[DEBUG API] Executing query: {query}")
        print(f"[DEBUG API] Params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        print(f"[DEBUG API] Query returned {len(result)} records")
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        print(f"[ERROR API] get_keuangan failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('', methods=['POST'])
def add_keuangan():
    """Tambah data keuangan baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        # Ensure user_id is always set
        created_by_pengguna = data.get('user_id')
        print(f"[DEBUG API] POST /keuangan - user_id: {created_by_pengguna}")

        if not created_by_pengguna:
            print("[ERROR API] user_id is required")
            return jsonify({'status': 'error', 'message': 'user_id is required'}), 400

        cursor = connection.cursor()

        # Insert hanya dengan kolom yang ada sekarang (tanpa deskripsi, metode_pembayaran, dll)
        query = """
        INSERT INTO keuangan (tanggal, kategori, sub_kategori, keterangan, jumlah, created_by_pengguna)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('keterangan'),  # Hanya keterangan, BUKAN deskripsi
            data.get('jumlah'),
            created_by_pengguna
        )

        print(f"[DEBUG API] Inserting keuangan: {params}")
        cursor.execute(query, params)

        connection.commit()

        keuangan_id = cursor.lastrowid
        cursor.close()
        connection.close()

        print(f"[DEBUG] Keuangan added successfully: ID={keuangan_id}, user_id={created_by_pengguna}")

        return jsonify({
            'status': 'success',
            'message': 'Data keuangan berhasil ditambahkan',
            'id': keuangan_id
        })
    except Exception as e:
        print(f"[ERROR] add_keuangan failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/<int:keuangan_id>', methods=['GET'])
def get_keuangan_by_id(keuangan_id):
    """Ambil data keuangan berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT k.*,
                   COALESCE(p.username, 'system') as dibuat_oleh,
                   COALESCE(p.nama_lengkap, 'System') as nama_user
            FROM keuangan k
            LEFT JOIN pengguna p ON k.created_by_pengguna = p.id_pengguna
            WHERE k.id_keuangan = %s
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
                'message': 'Data keuangan tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/<int:keuangan_id>', methods=['PUT'])
def update_keuangan(keuangan_id):
    """Update data keuangan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()

        # Update hanya dengan kolom yang ada (tanpa deskripsi, metode_pembayaran, dll)
        query = """
        UPDATE keuangan SET
            tanggal = %s, kategori = %s, sub_kategori = %s,
            jumlah = %s, keterangan = %s,
            updated_at = %s
        WHERE id_keuangan = %s
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('jumlah'),
            data.get('keterangan'),  # Hanya keterangan
            datetime.datetime.now(),
            keuangan_id
        )

        print(f"[DEBUG API] Updating keuangan ID {keuangan_id}: {params}")
        cursor.execute(query, params)

        connection.commit()

        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            print(f"[DEBUG] Keuangan updated successfully: ID={keuangan_id}")
            return jsonify({
                'status': 'success',
                'message': 'Data keuangan berhasil diupdate'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Data keuangan tidak ditemukan'
            }), 404
    except Exception as e:
        print(f"[ERROR] update_keuangan failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/<int:keuangan_id>', methods=['DELETE'])
def delete_keuangan(keuangan_id):
    """Hapus data keuangan"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        query = "DELETE FROM keuangan WHERE id_keuangan = %s"
        cursor.execute(query, (keuangan_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Data keuangan berhasil dihapus'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Data keuangan tidak ditemukan'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/laporan-bulanan', methods=['GET'])
def get_laporan_bulanan():
    """Ambil laporan keuangan bulanan menggunakan view"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        year = request.args.get('year', datetime.datetime.now().year, type=int)
        month = request.args.get('month', datetime.datetime.now().month, type=int)
        
        cursor = connection.cursor(dictionary=True)
        
        if year and month:
            query = "SELECT * FROM v_laporan_keuangan_bulanan WHERE tahun = %s AND bulan = %s"
            cursor.execute(query, (year, month))
        else:
            query = "SELECT * FROM v_laporan_keuangan_bulanan ORDER BY tahun DESC, bulan DESC LIMIT 12"
            cursor.execute(query)
        
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/saldo', methods=['GET'])
def get_saldo():
    """Hitung total saldo berdasarkan pemasukan dan pengeluaran"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Hitung total pemasukan
        cursor.execute("SELECT COALESCE(SUM(jumlah), 0) as total FROM keuangan WHERE kategori = 'Pemasukan'")
        pemasukan_result = cursor.fetchone()
        pemasukan = pemasukan_result.get('total', 0) if pemasukan_result else 0  # type: ignore

        # Hitung total pengeluaran
        cursor.execute("SELECT COALESCE(SUM(jumlah), 0) as total FROM keuangan WHERE kategori = 'Pengeluaran'")
        pengeluaran_result = cursor.fetchone()
        pengeluaran = pengeluaran_result.get('total', 0) if pengeluaran_result else 0  # type: ignore

        # Convert to float safely
        pemasukan_float = float(pemasukan) if pemasukan is not None else 0.0  # type: ignore
        pengeluaran_float = float(pengeluaran) if pengeluaran is not None else 0.0  # type: ignore
        saldo = pemasukan_float - pengeluaran_float

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': {
                'total_pemasukan': pemasukan_float,
                'total_pengeluaran': pengeluaran_float,
                'saldo': saldo
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== KEUANGAN KATEGORIAL ENDPOINTS ==========

@keuangan_bp.route('/kategorial', methods=['GET'])
def get_keuangan_kategorial():
    """Ambil semua data keuangan kategorial (admin-managed)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        jenis = request.args.get('jenis')
        kategori = request.args.get('kategori')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        cursor = connection.cursor(dictionary=True)

        # Safe column selection - explicit columns only
        query = """
        SELECT k.id_keuangan_kategorial, k.tanggal, k.kategori, k.sub_kategori,
               k.keterangan, k.jumlah, k.created_at, k.updated_at,
               k.created_by_admin,
               COALESCE(a.username, 'system') as dibuat_oleh,
               COALESCE(a.nama, 'System') as nama_admin
        FROM keuangan_kategorial k
        LEFT JOIN admin a ON k.created_by_admin = a.id_admin
        """
        conditions = []
        params = []

        if jenis:
            conditions.append("k.kategori = %s")
            params.append(jenis)

        if kategori:
            conditions.append("k.sub_kategori = %s")
            params.append(kategori)

        if start_date:
            conditions.append("k.tanggal >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("k.tanggal <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY k.tanggal DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        print(f"[DEBUG API] /kategorial GET - Executing query: {query}")
        print(f"[DEBUG API] /kategorial GET - Params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        print(f"[DEBUG API] /kategorial GET - Query returned {len(result)} records")
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        print(f"[ERROR API] /kategorial GET failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/kategorial', methods=['POST'])
def add_keuangan_kategorial():
    """Tambah data keuangan kategorial baru (admin)"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    data = request.json
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        created_by_admin = data.get('created_by_admin')

        if not created_by_admin:
            return jsonify({'status': 'error', 'message': 'created_by_admin is required'}), 400

        cursor = connection.cursor()

        query = """
        INSERT INTO keuangan_kategorial (tanggal, kategori, sub_kategori, keterangan, jumlah, created_by_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('keterangan'),
            data.get('jumlah'),
            created_by_admin
        )

        cursor.execute(query, params)
        connection.commit()

        keuangan_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Data keuangan kategorial berhasil ditambahkan',
            'id': keuangan_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/kategorial/<int:keuangan_id>', methods=['GET'])
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
        # Safe column selection - explicit columns only
        query = """
            SELECT k.id_keuangan_kategorial, k.tanggal, k.kategori, k.sub_kategori,
                   k.keterangan, k.jumlah, k.created_at, k.updated_at,
                   k.created_by_admin,
                   COALESCE(a.username, 'system') as dibuat_oleh,
                   COALESCE(a.nama, 'System') as nama_admin
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
        print(f"[ERROR API] /kategorial/{keuangan_id} GET failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/kategorial/<int:keuangan_id>', methods=['PUT'])
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
            tanggal = %s, kategori = %s, sub_kategori = %s,
            jumlah = %s, keterangan = %s,
            updated_at = %s
        WHERE id_keuangan_kategorial = %s
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('jumlah'),
            data.get('keterangan'),
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
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keuangan_bp.route('/kategorial/<int:keuangan_id>', methods=['DELETE'])
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
        return jsonify({'status': 'error', 'message': str(e)}), 500