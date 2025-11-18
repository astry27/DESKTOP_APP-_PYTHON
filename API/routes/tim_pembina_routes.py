# Path: routes/tim_pembina_routes.py

from flask import Blueprint, request, jsonify
from config import get_db_connection
import logging

tim_pembina_bp = Blueprint('tim_pembina', __name__, url_prefix='/tim_pembina')
logger = logging.getLogger(__name__)


@tim_pembina_bp.route('', methods=['GET'])
def get_tim_pembina():
    """Get all tim pembina with peserta"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor(dictionary=True)

        # Get all tim pembina
        query_tim = "SELECT * FROM tim_pembina ORDER BY tim_pembina"
        cursor.execute(query_tim)
        tim_list = cursor.fetchall()

        # For each tim, get peserta and lainnya (if applicable)
        for tim in tim_list:
            tim_id = tim['id_tim_pembina']
            query_peserta = """
                SELECT * FROM tim_pembina_peserta
                WHERE id_tim_pembina = %s
                ORDER BY jabatan, nama_lengkap
            """
            cursor.execute(query_peserta, (tim_id,))
            tim['peserta'] = cursor.fetchall()

            # tim_pembina_lainnya column sudah termasuk dalam SELECT * query

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': tim_list}), 200

    except Exception as e:
        logger.error(f"Error getting tim pembina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('', methods=['POST'])
def add_tim_pembina():
    """Add new tim pembina"""
    try:
        data = request.json

        if not data.get('tim_pembina'):
            return jsonify({'success': False, 'error': 'Tim pembina harus dipilih'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor(dictionary=True)

        tim_pembina = data.get('tim_pembina')
        nama_lainnya = data.get('nama_lainnya', '').strip() if data.get('tim_pembina') == 'Lainnya' else ''

        # Insert into tim_pembina table
        query = """
            INSERT INTO tim_pembina
            (tim_pembina, tim_pembina_lainnya, tanggal_pelantikan, keterangan)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            tim_pembina,
            nama_lainnya if tim_pembina == 'Lainnya' else None,
            data.get('tanggal_pelantikan'),
            data.get('keterangan')
        )

        cursor.execute(query, values)
        conn.commit()

        # Get the inserted ID - use cursor.lastrowid which works after commit
        tim_id = cursor.lastrowid
        logger.info(f"[ADD TIM PEMBINA] lastrowid: {tim_id}")

        if tim_id == 0 or tim_id is None:
            # Fallback: query the database for the last inserted record by tim_pembina name and creation time
            select_query = """
                SELECT id_tim_pembina FROM tim_pembina
                WHERE tim_pembina = %s AND tanggal_pelantikan = %s
                ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(select_query, (tim_pembina, data.get('tanggal_pelantikan')))
            result = cursor.fetchone()
            tim_id = result['id_tim_pembina'] if result else 0
            logger.info(f"[ADD TIM PEMBINA] Fallback query result: {tim_id}")

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Tim pembina berhasil ditambahkan', 'id_tim_pembina': tim_id}), 201

    except Exception as e:
        logger.error(f"Error adding tim pembina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('/<int:tim_id>', methods=['GET'])
def get_tim_pembina_detail(tim_id):
    """Get detail tim pembina with peserta"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor(dictionary=True)

        # Get tim
        query_tim = "SELECT * FROM tim_pembina WHERE id_tim_pembina = %s"
        cursor.execute(query_tim, (tim_id,))
        tim = cursor.fetchone()

        if not tim:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Tim tidak ditemukan'}), 404

        # Get peserta
        query_peserta = """
            SELECT * FROM tim_pembina_peserta
            WHERE id_tim_pembina = %s
            ORDER BY jabatan, nama_lengkap
        """
        cursor.execute(query_peserta, (tim_id,))
        tim['peserta'] = cursor.fetchall()

        # tim_pembina_lainnya column sudah termasuk dalam SELECT * query

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': tim}), 200

    except Exception as e:
        logger.error(f"Error getting tim pembina detail: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('/<int:tim_id>', methods=['PUT'])
def update_tim_pembina(tim_id):
    """Update tim pembina"""
    try:
        data = request.json

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        tim_pembina = data.get('tim_pembina')
        nama_lainnya = data.get('nama_lainnya', '').strip() if data.get('tim_pembina') == 'Lainnya' else ''

        # Update tim_pembina table
        query = """
            UPDATE tim_pembina
            SET tim_pembina = %s, tim_pembina_lainnya = %s,
                tanggal_pelantikan = %s, keterangan = %s
            WHERE id_tim_pembina = %s
        """

        values = (
            tim_pembina,
            nama_lainnya if tim_pembina == 'Lainnya' else None,
            data.get('tanggal_pelantikan'),
            data.get('keterangan'),
            tim_id
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Tim pembina berhasil diupdate'}), 200

    except Exception as e:
        logger.error(f"Error updating tim pembina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('/<int:tim_id>', methods=['DELETE'])
def delete_tim_pembina(tim_id):
    """Delete tim pembina"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        # Delete will cascade to peserta due to foreign key
        query = "DELETE FROM tim_pembina WHERE id_tim_pembina = %s"
        cursor.execute(query, (tim_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Tim pembina berhasil dihapus'}), 200

    except Exception as e:
        logger.error(f"Error deleting tim pembina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('/<int:tim_id>/peserta', methods=['POST'])
def add_peserta(tim_id):
    """Add peserta to tim pembina"""
    try:
        data = request.json

        if not data.get('id_jemaat') or not data.get('jabatan'):
            return jsonify({'success': False, 'error': 'Data tidak lengkap'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        query = """
            INSERT INTO tim_pembina_peserta
            (id_tim_pembina, id_jemaat, nama_lengkap, wilayah_rohani, jabatan,
             koordinator_bidang, sie_bidang)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            tim_id,
            data.get('id_jemaat'),
            data.get('nama_lengkap'),
            data.get('wilayah_rohani'),
            data.get('jabatan'),
            data.get('koordinator_bidang'),
            data.get('sie_bidang')
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Peserta berhasil ditambahkan'}), 201

    except Exception as e:
        logger.error(f"Error adding peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('/peserta/<int:peserta_id>', methods=['DELETE'])
def delete_peserta(peserta_id):
    """Delete peserta from tim pembina"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        query = "DELETE FROM tim_pembina_peserta WHERE id_peserta = %s"
        cursor.execute(query, (peserta_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Peserta berhasil dihapus'}), 200

    except Exception as e:
        logger.error(f"Error deleting peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== NEW SINGLE-TABLE APPROACH ENDPOINTS (2025-11-19) ==========
# These endpoints handle the new simplified tim_pembina structure where
# peserta data is stored directly in tim_pembina table
# Note: These endpoints use base path /tim_pembina with _peserta suffix
# to avoid conflicts with old two-table approach

# Blueprint root is /tim_pembina, so these become:
# GET/POST /tim_pembina_peserta (external path, routed through _peserta)

@tim_pembina_bp.route('_peserta', methods=['GET'])
def get_tim_pembina_peserta_new():
    """Get all peserta from tim_pembina table (new single-table approach)
    External URL: /tim_pembina_peserta"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor(dictionary=True)

        # Get all peserta from tim_pembina table where nama_peserta is not null
        query = """
            SELECT
                id_tim_pembina,
                nama_peserta,
                wilayah_rohani,
                jabatan,
                tahun,
                tim_pembina as nama_tim,
                id_jemaat
            FROM tim_pembina
            WHERE nama_peserta IS NOT NULL AND nama_peserta != ''
            ORDER BY tahun DESC, tim_pembina, jabatan, nama_peserta
        """
        cursor.execute(query)
        peserta_list = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': peserta_list}), 200

    except Exception as e:
        logger.error(f"Error getting tim pembina peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('_peserta', methods=['POST'])
def add_tim_pembina_peserta_new():
    """Add new peserta to tim_pembina table (new single-table approach)
    External URL: /tim_pembina_peserta"""
    try:
        data = request.json

        # Validate required fields
        if not data.get('nama_peserta') or not data.get('jabatan') or not data.get('nama_tim') or not data.get('tahun'):
            return jsonify({'success': False, 'error': 'Data tidak lengkap (nama_peserta, jabatan, nama_tim, tahun wajib)'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor(dictionary=True)

        # First, find the tim_pembina id by name
        query_find_tim = "SELECT id_tim_pembina FROM tim_pembina WHERE tim_pembina = %s LIMIT 1"
        cursor.execute(query_find_tim, (data.get('nama_tim'),))
        tim_result = cursor.fetchone()

        if not tim_result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': f'Tim pembina "{data.get("nama_tim")}" tidak ditemukan'}), 404

        tim_pembina_id = tim_result['id_tim_pembina']

        # Insert peserta into tim_pembina table
        query = """
            INSERT INTO tim_pembina
            (tim_pembina, nama_peserta, id_jemaat, wilayah_rohani, jabatan, tahun)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('nama_tim'),
            data.get('nama_peserta'),
            data.get('id_jemaat'),
            data.get('wilayah_rohani'),
            data.get('jabatan'),
            data.get('tahun')
        )

        cursor.execute(query, values)
        conn.commit()

        peserta_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Peserta berhasil ditambahkan',
            'id_tim_pembina': peserta_id,
            'data': {
                'id_tim_pembina': peserta_id,
                'nama_peserta': data.get('nama_peserta'),
                'wilayah_rohani': data.get('wilayah_rohani'),
                'jabatan': data.get('jabatan'),
                'nama_tim': data.get('nama_tim'),
                'tahun': data.get('tahun')
            }
        }), 201

    except Exception as e:
        logger.error(f"Error adding peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('_peserta/<int:peserta_id>', methods=['PUT'])
def update_tim_pembina_peserta_new(peserta_id):
    """Update peserta in tim_pembina table (new single-table approach)
    External URL: /tim_pembina_peserta/{peserta_id}"""
    try:
        data = request.json

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        # Update peserta in tim_pembina table
        query = """
            UPDATE tim_pembina
            SET nama_peserta = %s,
                id_jemaat = %s,
                wilayah_rohani = %s,
                jabatan = %s,
                tahun = %s,
                tim_pembina = %s
            WHERE id_tim_pembina = %s
        """

        values = (
            data.get('nama_peserta'),
            data.get('id_jemaat'),
            data.get('wilayah_rohani'),
            data.get('jabatan'),
            data.get('tahun'),
            data.get('nama_tim'),
            peserta_id
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Peserta berhasil diupdate'}), 200

    except Exception as e:
        logger.error(f"Error updating peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tim_pembina_bp.route('_peserta/<int:peserta_id>', methods=['DELETE'])
def delete_tim_pembina_peserta_new(peserta_id):
    """Delete peserta from tim_pembina table (new single-table approach)
    External URL: /tim_pembina_peserta/{peserta_id}"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Gagal terhubung ke database'}), 500

        cursor = conn.cursor()

        # Delete peserta record from tim_pembina table
        query = """
            DELETE FROM tim_pembina
            WHERE id_tim_pembina = %s AND nama_peserta IS NOT NULL
        """
        cursor.execute(query, (peserta_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Peserta berhasil dihapus'}), 200

    except Exception as e:
        logger.error(f"Error deleting peserta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
