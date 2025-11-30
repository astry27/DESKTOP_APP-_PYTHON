# Path: API/routes/program_kerja_wr_routes.py
# Program Kerja WR Routes - For client users to manage their own work programs

from flask import Blueprint, request, jsonify
from config import get_db_connection, close_db_connection

program_kerja_wr_bp = Blueprint('program_kerja_wr', __name__)

# GET - List program kerja WR (filter by user_id if provided)
@program_kerja_wr_bp.route('/program-kerja-wr', methods=['GET'])
def get_program_kerja_wr():
    try:
        user_id = request.args.get('user_id')
        search = request.args.get('search')

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database tidak tersedia"}), 500

        cursor = conn.cursor(dictionary=True)

        # JOIN with pengguna table to get user name
        query = """
            SELECT
                pkw.*,
                p.nama_lengkap as user_name,
                p.username as username
            FROM program_kerja_wr pkw
            LEFT JOIN pengguna p ON pkw.reported_by = p.id_pengguna
            WHERE 1=1
        """
        params = []

        if user_id:
            query += " AND pkw.reported_by = %s"
            params.append(user_id)

        if search:
            query += " AND (pkw.judul LIKE %s OR pkw.keterangan LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY pkw.created_at DESC"

        cursor.execute(query, params)
        data = cursor.fetchall()

        cursor.close()
        close_db_connection(conn)

        return jsonify({"status": "success", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# POST - Add new program kerja WR
@program_kerja_wr_bp.route('/program-kerja-wr', methods=['POST'])
def add_program_kerja_wr():
    try:
        data = request.get_json()

        required_fields = ['kategori', 'estimasi_waktu', 'judul']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"status": "error", "message": f"Field {field} harus diisi"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database tidak tersedia"}), 500

        cursor = conn.cursor()

        query = """
            INSERT INTO program_kerja_wr
            (kategori, estimasi_waktu, judul, sasaran, penanggung_jawab,
             anggaran, sumber_anggaran, keterangan, reported_by, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('kategori'),
            data.get('estimasi_waktu'),
            data.get('judul'),
            data.get('sasaran', ''),
            data.get('penanggung_jawab', ''),
            data.get('anggaran', 0),
            data.get('sumber_anggaran', ''),
            data.get('keterangan', ''),
            data.get('user_id'),
            'pending'
        )

        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid

        cursor.close()
        close_db_connection(conn)

        return jsonify({
            "status": "success",
            "message": "Program kerja berhasil ditambahkan",
            "data": {"id_program_kerja_wr": new_id}
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# PUT - Update program kerja WR
@program_kerja_wr_bp.route('/program-kerja-wr/<int:id>', methods=['PUT'])
def update_program_kerja_wr(id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database tidak tersedia"}), 500

        cursor = conn.cursor(dictionary=True)

        # Check if record exists and belongs to user
        cursor.execute("SELECT reported_by FROM program_kerja_wr WHERE id_program_kerja_wr = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            close_db_connection(conn)
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404

        reported_by = existing.get('reported_by') if isinstance(existing, dict) else None
        if str(reported_by) != str(user_id):
            cursor.close()
            close_db_connection(conn)
            return jsonify({"status": "error", "message": "Anda tidak memiliki akses untuk mengubah data ini"}), 403

        # Update
        query = """
            UPDATE program_kerja_wr
            SET kategori = %s, estimasi_waktu = %s, judul = %s, sasaran = %s,
                penanggung_jawab = %s, anggaran = %s, sumber_anggaran = %s,
                keterangan = %s, updated_at = NOW()
            WHERE id_program_kerja_wr = %s
        """

        values = (
            data.get('kategori'),
            data.get('estimasi_waktu'),
            data.get('judul'),
            data.get('sasaran', ''),
            data.get('penanggung_jawab', ''),
            data.get('anggaran', 0),
            data.get('sumber_anggaran', ''),
            data.get('keterangan', ''),
            id
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        close_db_connection(conn)

        return jsonify({"status": "success", "message": "Program kerja berhasil diperbarui"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# DELETE - Delete program kerja WR
@program_kerja_wr_bp.route('/program-kerja-wr/<int:id>', methods=['DELETE'])
def delete_program_kerja_wr(id):
    try:
        user_id = request.args.get('user_id')
        if user_id:
            user_id = int(user_id)

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database tidak tersedia"}), 500

        cursor = conn.cursor(dictionary=True)

        # Check if record exists and belongs to user
        cursor.execute("SELECT reported_by FROM program_kerja_wr WHERE id_program_kerja_wr = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            close_db_connection(conn)
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404

        reported_by = existing.get('reported_by') if isinstance(existing, dict) else None
        if str(reported_by) != str(user_id):
            cursor.close()
            close_db_connection(conn)
            return jsonify({"status": "error", "message": "Anda tidak memiliki akses untuk menghapus data ini"}), 403

        # Delete
        cursor.execute("DELETE FROM program_kerja_wr WHERE id_program_kerja_wr = %s", (id,))
        conn.commit()

        cursor.close()
        close_db_connection(conn)

        return jsonify({"status": "success", "message": "Program kerja berhasil dihapus"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
