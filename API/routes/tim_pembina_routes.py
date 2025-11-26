# Path: API/routes/tim_pembina_routes.py
# PRODUCTION VERSION - Compatible with production server wrapper

from flask import Blueprint, jsonify, request
from config import get_db_connection
import os

tim_pembina_bp = Blueprint('tim_pembina', __name__, url_prefix='/tim-pembina')

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

@tim_pembina_bp.route('', methods=['GET'])
def get_tim_pembina():
    """Ambil semua data tim pembina peserta"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        search = request.args.get('search', '')
        tim_pembina_filter = request.args.get('tim_pembina', '')
        wilayah_rohani_filter = request.args.get('wilayah_rohani', '')
        jabatan_filter = request.args.get('jabatan', '')
        tahun_filter = request.args.get('tahun', '')

        cursor = connection.cursor(dictionary=True)

        # Build query dengan filter
        base_query = """
        SELECT * FROM tim_pembina_peserta
        WHERE 1=1
        """
        params = []

        if search:
            base_query += """ AND (
                nama_peserta LIKE %s OR
                tim_pembina LIKE %s OR
                tim_pembina_lainnya LIKE %s OR
                wilayah_rohani LIKE %s OR
                jabatan LIKE %s
            )"""
            search_param = f'%{search}%'
            params.extend([search_param] * 5)

        if tim_pembina_filter:
            base_query += " AND tim_pembina = %s"
            params.append(tim_pembina_filter)

        if wilayah_rohani_filter:
            base_query += " AND wilayah_rohani = %s"
            params.append(wilayah_rohani_filter)

        if jabatan_filter:
            base_query += " AND jabatan = %s"
            params.append(jabatan_filter)

        if tahun_filter:
            base_query += " AND tahun = %s"
            params.append(tahun_filter)

        base_query += " ORDER BY tahun DESC, nama_peserta ASC"

        cursor.execute(base_query, params)
        tim_pembina_list = cursor.fetchall()

        # Convert dates to string untuk JSON serialization
        for tim_pembina in tim_pembina_list:
            created_at = tim_pembina.get('created_at')
            if created_at:
                tim_pembina['created_at'] = created_at.isoformat()  # type: ignore
            updated_at = tim_pembina.get('updated_at')
            if updated_at:
                tim_pembina['updated_at'] = updated_at.isoformat()  # type: ignore
            # Convert boolean to int
            if 'is_manual_entry' in tim_pembina:
                tim_pembina['is_manual_entry'] = 1 if tim_pembina['is_manual_entry'] else 0  # type: ignore

        return jsonify({
            'status': 'success',
            'data': tim_pembina_list,
            'total': len(tim_pembina_list)
        })

    except Exception as e:
        print(f"Error getting tim pembina: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('', methods=['POST'])
def add_tim_pembina():
    """Tambah data tim pembina peserta baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        # Validasi required fields
        required_fields = ['nama_peserta', 'tim_pembina', 'wilayah_rohani', 'jabatan', 'tahun']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Field {field} diperlukan'
                }), 400

        cursor = connection.cursor()

        # Cek duplikasi
        check_query = """
        SELECT id_tim_pembina FROM tim_pembina_peserta
        WHERE nama_peserta = %s AND tim_pembina = %s AND tahun = %s
        """
        cursor.execute(check_query, (data.get('nama_peserta'), data.get('tim_pembina'), data.get('tahun')))
        existing = cursor.fetchone()

        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Peserta sudah terdaftar di tim ini pada tahun yang sama'
            }), 400

        insert_query = """
        INSERT INTO tim_pembina_peserta (
            nama_peserta, is_manual_entry, id_jemaat, tim_pembina,
            tim_pembina_lainnya, wilayah_rohani, jabatan, tahun
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        params = (
            data.get('nama_peserta'),
            1 if data.get('is_manual_entry') else 0,
            data.get('id_jemaat'),
            data.get('tim_pembina'),
            data.get('tim_pembina_lainnya') if data.get('tim_pembina') == 'Lainnya' else None,
            data.get('wilayah_rohani'),
            data.get('jabatan'),
            data.get('tahun')
        )

        cursor.execute(insert_query, params)
        connection.commit()

        tim_pembina_id = cursor.lastrowid

        return jsonify({
            'status': 'success',
            'message': 'Data tim pembina peserta berhasil ditambahkan',
            'id': tim_pembina_id
        })

    except Exception as e:
        print(f"Error adding tim pembina: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('/<int:tim_pembina_id>', methods=['GET'])
def get_tim_pembina_by_id(tim_pembina_id):
    """Ambil data tim pembina peserta berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tim_pembina_peserta WHERE id_tim_pembina = %s", (tim_pembina_id,))
        tim_pembina_row = cursor.fetchone()

        if not tim_pembina_row:
            return jsonify({'status': 'error', 'message': 'Data tim pembina tidak ditemukan'}), 404

        # Convert dates to string untuk JSON serialization
        created_at = tim_pembina_row.get('created_at')
        if created_at:
            tim_pembina_row['created_at'] = created_at.isoformat()  # type: ignore
        updated_at = tim_pembina_row.get('updated_at')
        if updated_at:
            tim_pembina_row['updated_at'] = updated_at.isoformat()  # type: ignore
        # Convert boolean to int
        if 'is_manual_entry' in tim_pembina_row:
            tim_pembina_row['is_manual_entry'] = 1 if tim_pembina_row['is_manual_entry'] else 0  # type: ignore

        return jsonify({
            'status': 'success',
            'data': tim_pembina_row
        })

    except Exception as e:
        print(f"Error getting tim pembina by ID: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('/<int:tim_pembina_id>', methods=['PUT'])
def update_tim_pembina(tim_pembina_id):
    """Update data tim pembina peserta"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        data = request.get_json()

        cursor = connection.cursor()

        # Check if exists
        cursor.execute("SELECT id_tim_pembina FROM tim_pembina_peserta WHERE id_tim_pembina = %s", (tim_pembina_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Data tim pembina tidak ditemukan'}), 404

        # Cek duplikasi (kecuali record sendiri)
        check_query = """
        SELECT id_tim_pembina FROM tim_pembina_peserta
        WHERE nama_peserta = %s AND tim_pembina = %s AND tahun = %s AND id_tim_pembina != %s
        """
        cursor.execute(check_query, (data.get('nama_peserta'), data.get('tim_pembina'), data.get('tahun'), tim_pembina_id))
        existing = cursor.fetchone()

        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Peserta sudah terdaftar di tim ini pada tahun yang sama'
            }), 400

        update_query = """
        UPDATE tim_pembina_peserta SET
            nama_peserta = %s, is_manual_entry = %s, id_jemaat = %s,
            tim_pembina = %s, tim_pembina_lainnya = %s, wilayah_rohani = %s,
            jabatan = %s, tahun = %s, updated_at = NOW()
        WHERE id_tim_pembina = %s
        """

        params = (
            data.get('nama_peserta'),
            1 if data.get('is_manual_entry') else 0,
            data.get('id_jemaat'),
            data.get('tim_pembina'),
            data.get('tim_pembina_lainnya') if data.get('tim_pembina') == 'Lainnya' else None,
            data.get('wilayah_rohani'),
            data.get('jabatan'),
            data.get('tahun'),
            tim_pembina_id
        )

        cursor.execute(update_query, params)
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Data tim pembina peserta berhasil diupdate'
        })

    except Exception as e:
        print(f"Error updating tim pembina: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('/<int:tim_pembina_id>', methods=['DELETE'])
def delete_tim_pembina(tim_pembina_id):
    """Hapus data tim pembina peserta"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Check if exists
        cursor.execute("SELECT nama_peserta FROM tim_pembina_peserta WHERE id_tim_pembina = %s", (tim_pembina_id,))
        tim_pembina = cursor.fetchone()
        if not tim_pembina:
            return jsonify({'status': 'error', 'message': 'Data tim pembina tidak ditemukan'}), 404

        nama_peserta = tim_pembina.get('nama_peserta', 'Unknown')

        cursor.execute("DELETE FROM tim_pembina_peserta WHERE id_tim_pembina = %s", (tim_pembina_id,))
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': f'Data peserta {nama_peserta} berhasil dihapus'
        })

    except Exception as e:
        print(f"Error deleting tim pembina: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('/statistics', methods=['GET'])
def get_tim_pembina_statistics():
    """Ambil statistik tim pembina"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Total peserta
        cursor.execute("SELECT COUNT(*) as total FROM tim_pembina_peserta")
        total_row = cursor.fetchone()
        total = total_row.get('total', 0) if total_row else 0

        # Per tim pembina
        cursor.execute("""
            SELECT
                CASE
                    WHEN tim_pembina = 'Lainnya' AND tim_pembina_lainnya IS NOT NULL
                    THEN tim_pembina_lainnya
                    ELSE tim_pembina
                END as tim,
                COUNT(*) as jumlah
            FROM tim_pembina_peserta
            GROUP BY tim
            ORDER BY jumlah DESC
        """)
        per_tim = cursor.fetchall()

        # Per wilayah rohani
        cursor.execute("""
            SELECT wilayah_rohani, COUNT(*) as jumlah
            FROM tim_pembina_peserta
            GROUP BY wilayah_rohani
            ORDER BY jumlah DESC
        """)
        per_wilayah = cursor.fetchall()

        # Per jabatan
        cursor.execute("""
            SELECT jabatan, COUNT(*) as jumlah
            FROM tim_pembina_peserta
            GROUP BY jabatan
            ORDER BY jumlah DESC
        """)
        per_jabatan = cursor.fetchall()

        # Per tahun
        cursor.execute("""
            SELECT tahun, COUNT(*) as jumlah
            FROM tim_pembina_peserta
            GROUP BY tahun
            ORDER BY tahun DESC
        """)
        per_tahun = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': {
                'total': total,
                'per_tim': per_tim,
                'per_wilayah': per_wilayah,
                'per_jabatan': per_jabatan,
                'per_tahun': per_tahun
            }
        })

    except Exception as e:
        print(f"Error getting tim pembina statistics: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@tim_pembina_bp.route('/search-jemaat', methods=['GET'])
def search_jemaat():
    """Cari umat berdasarkan nama untuk field Nama Peserta"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

    try:
        search = request.args.get('search', '')

        cursor = connection.cursor(dictionary=True)

        # If search is empty, return all jemaat with limit
        # Otherwise, filter by search keyword
        if search and len(search) >= 1:
            query = """
            SELECT id_jemaat, nama_lengkap, wilayah_rohani
            FROM jemaat
            WHERE nama_lengkap LIKE %s
            ORDER BY nama_lengkap ASC
            LIMIT 50
            """
            search_param = f'%{search}%'
            cursor.execute(query, (search_param,))
        else:
            # No search keyword - return all jemaat
            query = """
            SELECT id_jemaat, nama_lengkap, wilayah_rohani
            FROM jemaat
            ORDER BY nama_lengkap ASC
            LIMIT 100
            """
            cursor.execute(query)

        jemaat_list = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'data': jemaat_list,
            'total': len(jemaat_list)
        })

    except Exception as e:
        print(f"Error searching jemaat: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()
