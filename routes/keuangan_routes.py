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
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT k.id_keuangan, k.tanggal, k.kategori as jenis, k.sub_kategori as kategori,
                   k.deskripsi, k.keterangan, k.jumlah, k.created_at, k.created_by_pengguna,
                   COALESCE(p.username, 'system') as dibuat_oleh,
                   COALESCE(p.nama_lengkap, 'System') as nama_user
            FROM keuangan k
            LEFT JOIN pengguna p ON k.created_by_pengguna = p.id_pengguna
            WHERE k.created_by_pengguna = %s
            ORDER BY k.tanggal DESC
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
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
        
        # Build query dengan JOIN ke tabel pengguna untuk mendapatkan username
        query = """
        SELECT k.*,
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
        cursor = connection.cursor()
        query = """
        INSERT INTO keuangan (tanggal, kategori, sub_kategori, deskripsi, 
                             jumlah, metode_pembayaran, nomor_referensi, 
                             penanggung_jawab, bukti_file, keterangan, created_by_pengguna)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('deskripsi'),
            data.get('jumlah'),
            data.get('metode_pembayaran', 'Tunai'),
            data.get('nomor_referensi'),
            data.get('penanggung_jawab'),
            data.get('bukti_file'),
            data.get('keterangan'),
            data.get('user_id')
        )
        cursor.execute(query, params)
        connection.commit()
        
        keuangan_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Data keuangan berhasil ditambahkan',
            'id': keuangan_id
        })
    except Exception as e:
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
        query = """
        UPDATE keuangan SET 
            tanggal = %s, kategori = %s, sub_kategori = %s, deskripsi = %s,
            jumlah = %s, metode_pembayaran = %s, nomor_referensi = %s,
            penanggung_jawab = %s, bukti_file = %s, keterangan = %s,
            updated_at = %s
        WHERE id_keuangan = %s
        """
        params = (
            data.get('tanggal'),
            data.get('kategori'),
            data.get('sub_kategori'),
            data.get('deskripsi'),
            data.get('jumlah'),
            data.get('metode_pembayaran'),
            data.get('nomor_referensi'),
            data.get('penanggung_jawab'),
            data.get('bukti_file'),
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
        pemasukan = cursor.fetchone()['total']
        
        # Hitung total pengeluaran
        cursor.execute("SELECT COALESCE(SUM(jumlah), 0) as total FROM keuangan WHERE kategori = 'Pengeluaran'")
        pengeluaran = cursor.fetchone()['total']
        
        saldo = float(pemasukan) - float(pengeluaran)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_pemasukan': float(pemasukan),
                'total_pengeluaran': float(pengeluaran),
                'saldo': saldo
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500