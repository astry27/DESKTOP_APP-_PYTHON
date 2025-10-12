from flask import Blueprint, request, jsonify
import mysql.connector
from config import get_db_connection
from datetime import datetime

kegiatan_wr_bp = Blueprint('kegiatan_wr', __name__)

@kegiatan_wr_bp.route('/kegiatan-wr/my', methods=['GET'])
def get_my_kegiatan_wr():
    """Get kegiatan WR for specific user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                kw.*,
                p.username,
                p.nama_lengkap
            FROM kegiatan_wr kw
            LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
            WHERE kw.user_id = %s
            ORDER BY kw.tanggal_pelaksanaan DESC
        """

        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        # Convert timedelta to HH:MM format
        for row in result:
            if row.get('waktu_mulai') and hasattr(row['waktu_mulai'], 'total_seconds'):
                hours, remainder = divmod(row['waktu_mulai'].total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                row['waktu_mulai'] = f"{int(hours):02d}:{int(minutes):02d}"

            if row.get('waktu_selesai') and hasattr(row['waktu_selesai'], 'total_seconds'):
                hours, remainder = divmod(row['waktu_selesai'].total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                row['waktu_selesai'] = f"{int(hours):02d}:{int(minutes):02d}"

            # Convert date objects to string
            if row.get('tanggal_pelaksanaan'):
                row['tanggal_pelaksanaan'] = row['tanggal_pelaksanaan'].isoformat()
            if row.get('tanggal_selesai'):
                row['tanggal_selesai'] = row['tanggal_selesai'].isoformat()
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat()

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kegiatan_wr_bp.route('/kegiatan-wr', methods=['GET'])
def get_all_kegiatan_wr():
    """Get all kegiatan WR (admin view)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                kw.*,
                p.username,
                p.nama_lengkap
            FROM kegiatan_wr kw
            LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
            ORDER BY kw.tanggal_pelaksanaan DESC
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # Convert timedelta to HH:MM format
        for row in result:
            if row.get('waktu_mulai') and hasattr(row['waktu_mulai'], 'total_seconds'):
                hours, remainder = divmod(row['waktu_mulai'].total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                row['waktu_mulai'] = f"{int(hours):02d}:{int(minutes):02d}"

            if row.get('waktu_selesai') and hasattr(row['waktu_selesai'], 'total_seconds'):
                hours, remainder = divmod(row['waktu_selesai'].total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                row['waktu_selesai'] = f"{int(hours):02d}:{int(minutes):02d}"

            # Convert date objects to string
            if row.get('tanggal_pelaksanaan'):
                row['tanggal_pelaksanaan'] = row['tanggal_pelaksanaan'].isoformat()
            if row.get('tanggal_selesai'):
                row['tanggal_selesai'] = row['tanggal_selesai'].isoformat()
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat()

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kegiatan_wr_bp.route('/kegiatan-wr', methods=['POST'])
def create_kegiatan_wr():
    """Create new kegiatan WR"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['kategori', 'nama_kegiatan', 'tempat_kegiatan',
                          'tanggal_pelaksanaan', 'waktu_mulai', 'penanggung_jawab',
                          'status_kegiatan', 'user_id']

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Field {field} is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO kegiatan_wr
            (kategori, nama_kegiatan, sasaran_kegiatan, tujuan_kegiatan,
             tempat_kegiatan, tanggal_pelaksanaan, tanggal_selesai,
             waktu_mulai, waktu_selesai, penanggung_jawab,
             status_kegiatan, deskripsi, keterangan, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['kategori'],
            data['nama_kegiatan'],
            data.get('sasaran_kegiatan'),
            data.get('tujuan_kegiatan'),
            data['tempat_kegiatan'],
            data['tanggal_pelaksanaan'],
            data.get('tanggal_selesai'),
            data['waktu_mulai'],
            data.get('waktu_selesai'),
            data['penanggung_jawab'],
            data['status_kegiatan'],
            data.get('deskripsi'),
            data.get('keterangan'),
            data['user_id']
        )

        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Kegiatan WR created successfully",
            "id": new_id
        }), 201

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kegiatan_wr_bp.route('/kegiatan-wr/<int:id>', methods=['PUT'])
def update_kegiatan_wr(id):
    """Update kegiatan WR"""
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build dynamic update query
        update_fields = []
        values = []

        allowed_fields = ['kategori', 'nama_kegiatan', 'sasaran_kegiatan', 'tujuan_kegiatan',
                         'tempat_kegiatan', 'tanggal_pelaksanaan', 'tanggal_selesai',
                         'waktu_mulai', 'waktu_selesai', 'penanggung_jawab', 'status_kegiatan',
                         'deskripsi', 'keterangan']

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(id)

        query = f"UPDATE kegiatan_wr SET {', '.join(update_fields)} WHERE id_kegiatan_wr = %s"

        cursor.execute(query, values)
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Kegiatan WR not found"}), 404

        cursor.close()
        conn.close()

        return jsonify({"message": "Kegiatan WR updated successfully"}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kegiatan_wr_bp.route('/kegiatan-wr/<int:id>', methods=['DELETE'])
def delete_kegiatan_wr(id):
    """Delete kegiatan WR"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM kegiatan_wr WHERE id_kegiatan_wr = %s"
        cursor.execute(query, (id,))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Kegiatan WR not found"}), 404

        cursor.close()
        conn.close()

        return jsonify({"message": "Kegiatan WR deleted successfully"}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
