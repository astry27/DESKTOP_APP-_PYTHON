# Path: routes/aset_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import os

aset_bp = Blueprint('aset', __name__, url_prefix='/aset')

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

@aset_bp.route('', methods=['GET'])
def get_aset():
    """Ambil semua data aset"""
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
        kategori = request.args.get('kategori', '')
        kondisi = request.args.get('kondisi', '')
        status = request.args.get('status', '')
        lokasi = request.args.get('lokasi', '')

        cursor = connection.cursor(dictionary=True)

        # Build query dengan filter
        base_query = "SELECT * FROM aset WHERE 1=1"
        params = []

        if search:
            base_query += """ AND (
                kode_aset LIKE %s OR
                nama_aset LIKE %s OR
                merk_tipe LIKE %s OR
                penanggung_jawab LIKE %s OR
                lokasi LIKE %s
            )"""
            search_param = f'%{search}%'
            params.extend([search_param] * 5)

        if kategori:
            base_query += " AND kategori = %s"
            params.append(kategori)

        if kondisi:
            base_query += " AND kondisi = %s"
            params.append(kondisi)

        if status:
            base_query += " AND status = %s"
            params.append(status)

        if lokasi:
            base_query += " AND lokasi = %s"
            params.append(lokasi)

        base_query += " ORDER BY nama_aset ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(base_query, params)
        aset_list = cursor.fetchall()

        # Get total count untuk pagination
        count_query = "SELECT COUNT(*) as total FROM aset WHERE 1=1"
        count_params = []

        if search:
            count_query += """ AND (
                kode_aset LIKE %s OR
                nama_aset LIKE %s OR
                merk_tipe LIKE %s OR
                penanggung_jawab LIKE %s OR
                lokasi LIKE %s
            )"""
            count_params.extend([search_param] * 5)

        if kategori:
            count_query += " AND kategori = %s"
            count_params.append(kategori)

        if kondisi:
            count_query += " AND kondisi = %s"
            count_params.append(kondisi)

        if status:
            count_query += " AND status = %s"
            count_params.append(status)

        if lokasi:
            count_query += " AND lokasi = %s"
            count_params.append(lokasi)

        cursor.execute(count_query, count_params)
        total_result = cursor.fetchone()
        total = total_result.get('total', 0) if total_result else 0

        # Convert dates dan decimals untuk JSON serialization
        for item in aset_list:
            if item.get('nilai'):
                item['nilai'] = float(item['nilai'])  # type: ignore
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()  # type: ignore
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()  # type: ignore

        return jsonify({
            'status': 'success',
            'data': aset_list,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        print(f"Error getting aset: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('', methods=['POST'])
def add_aset():
    """Tambah data aset baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        # Validasi required fields
        required_fields = ['kode_aset', 'nama_aset']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Field {field} diperlukan'
                }), 400

        cursor = connection.cursor()

        # Check if kode_aset sudah ada
        cursor.execute("SELECT id_aset FROM aset WHERE kode_aset = %s", (data.get('kode_aset'),))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Kode aset sudah ada'
            }), 400

        insert_query = """
        INSERT INTO aset (
            kode_aset, nama_aset, jenis_aset, kategori, merk_tipe, tahun_perolehan,
            sumber_perolehan, nilai, kondisi, lokasi, status, penanggung_jawab, keterangan
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        params = (
            data.get('kode_aset'),
            data.get('nama_aset'),
            data.get('jenis_aset'),
            data.get('kategori'),
            data.get('merk_tipe'),
            data.get('tahun_perolehan'),
            data.get('sumber_perolehan'),
            data.get('nilai', 0),
            data.get('kondisi', 'Baik'),
            data.get('lokasi'),
            data.get('status', 'Aktif'),
            data.get('penanggung_jawab'),
            data.get('keterangan')
        )

        cursor.execute(insert_query, params)
        connection.commit()

        aset_id = cursor.lastrowid

        return jsonify({
            'status': 'success',
            'message': 'Data aset berhasil ditambahkan',
            'id': aset_id
        })

    except Exception as e:
        print(f"Error adding aset: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/<int:aset_id>', methods=['GET'])
def get_aset_by_id(aset_id):
    """Ambil data aset berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM aset WHERE id_aset = %s", (aset_id,))
        aset = cursor.fetchone()

        if not aset:
            return jsonify({'status': 'error', 'message': 'Data aset tidak ditemukan'}), 404

        # Convert dates dan decimals
        if aset.get('nilai'):
            aset['nilai'] = float(aset['nilai'])  # type: ignore
        if aset.get('created_at'):
            aset['created_at'] = aset['created_at'].isoformat()  # type: ignore
        if aset.get('updated_at'):
            aset['updated_at'] = aset['updated_at'].isoformat()  # type: ignore

        return jsonify({
            'status': 'success',
            'data': aset
        })

    except Exception as e:
        print(f"Error getting aset by ID: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/<int:aset_id>', methods=['PUT'])
def update_aset(aset_id):
    """Update data aset"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        cursor = connection.cursor()

        # Check if aset exists
        cursor.execute("SELECT id_aset FROM aset WHERE id_aset = %s", (aset_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Data aset tidak ditemukan'}), 404

        # Check jika kode_aset diubah, pastikan tidak conflict
        if data.get('kode_aset'):
            cursor.execute(
                "SELECT id_aset FROM aset WHERE kode_aset = %s AND id_aset != %s",
                (data.get('kode_aset'), aset_id)
            )
            if cursor.fetchone():
                return jsonify({
                    'status': 'error',
                    'message': 'Kode aset sudah ada'
                }), 400

        update_query = """
        UPDATE aset SET
            kode_aset = %s, nama_aset = %s, jenis_aset = %s, kategori = %s,
            merk_tipe = %s, tahun_perolehan = %s, sumber_perolehan = %s, nilai = %s,
            kondisi = %s, lokasi = %s, status = %s, penanggung_jawab = %s,
            keterangan = %s, updated_at = NOW()
        WHERE id_aset = %s
        """

        params = (
            data.get('kode_aset'),
            data.get('nama_aset'),
            data.get('jenis_aset'),
            data.get('kategori'),
            data.get('merk_tipe'),
            data.get('tahun_perolehan'),
            data.get('sumber_perolehan'),
            data.get('nilai', 0),
            data.get('kondisi', 'Baik'),
            data.get('lokasi'),
            data.get('status', 'Aktif'),
            data.get('penanggung_jawab'),
            data.get('keterangan'),
            aset_id
        )

        cursor.execute(update_query, params)
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Data aset berhasil diupdate'
        })

    except Exception as e:
        print(f"Error updating aset: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/<int:aset_id>', methods=['DELETE'])
def delete_aset(aset_id):
    """Hapus data aset"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()

        # Check if aset exists
        cursor.execute("SELECT nama_aset FROM aset WHERE id_aset = %s", (aset_id,))
        aset = cursor.fetchone()
        if not aset:
            return jsonify({'status': 'error', 'message': 'Data aset tidak ditemukan'}), 404

        cursor.execute("DELETE FROM aset WHERE id_aset = %s", (aset_id,))
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': f'Data aset {aset[0]} berhasil dihapus'  # type: ignore
        })

    except Exception as e:
        print(f"Error deleting aset: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/statistics', methods=['GET'])
def get_aset_statistics():
    """Ambil statistik aset"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Total aset
        cursor.execute("SELECT COUNT(*) as total_aset FROM aset")
        total_stats_result = cursor.fetchone()
        total_aset = total_stats_result.get('total_aset', 0) if total_stats_result else 0

        # Total nilai aset
        cursor.execute("SELECT SUM(COALESCE(nilai, 0)) as total_nilai FROM aset")
        total_nilai_result = cursor.fetchone()
        total_nilai = total_nilai_result.get('total_nilai', 0) if total_nilai_result else 0

        # Aset per kategori
        cursor.execute("""
            SELECT kategori, COUNT(*) as jumlah_item
            FROM aset
            WHERE kategori IS NOT NULL
            GROUP BY kategori
            ORDER BY jumlah_item DESC
        """)
        per_kategori = cursor.fetchall()

        # Aset per kondisi
        cursor.execute("""
            SELECT kondisi, COUNT(*) as jumlah
            FROM aset
            GROUP BY kondisi
            ORDER BY jumlah DESC
        """)
        per_kondisi = cursor.fetchall()

        # Aset per status
        cursor.execute("""
            SELECT status, COUNT(*) as jumlah
            FROM aset
            GROUP BY status
            ORDER BY jumlah DESC
        """)
        per_status = cursor.fetchall()

        # Aset per lokasi
        cursor.execute("""
            SELECT lokasi, COUNT(*) as jumlah
            FROM aset
            WHERE lokasi IS NOT NULL
            GROUP BY lokasi
            ORDER BY jumlah DESC
            LIMIT 10
        """)
        per_lokasi = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': {
                'total_aset': total_aset,
                'total_nilai': float(total_nilai) if total_nilai else 0.0,  # type: ignore
                'per_kategori': per_kategori,
                'per_kondisi': per_kondisi,
                'per_status': per_status,
                'per_lokasi': per_lokasi
            }
        })

    except Exception as e:
        print(f"Error getting aset statistics: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/kategori', methods=['GET'])
def get_aset_categories():
    """Ambil daftar kategori aset yang ada"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT kategori
            FROM aset
            WHERE kategori IS NOT NULL AND kategori != ''
            ORDER BY kategori
        """)
        categories = [row[0] for row in cursor.fetchall()]  # type: ignore

        return jsonify({
            'status': 'success',
            'data': categories
        })

    except Exception as e:
        print(f"Error getting aset categories: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@aset_bp.route('/lokasi', methods=['GET'])
def get_aset_locations():
    """Ambil daftar lokasi aset yang ada"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT lokasi
            FROM aset
            WHERE lokasi IS NOT NULL AND lokasi != ''
            ORDER BY lokasi
        """)
        locations = [row[0] for row in cursor.fetchall()]  # type: ignore

        return jsonify({
            'status': 'success',
            'data': locations
        })

    except Exception as e:
        print(f"Error getting aset locations: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()
