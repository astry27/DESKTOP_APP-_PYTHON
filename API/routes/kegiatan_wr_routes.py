from flask import Blueprint, request, jsonify
import mysql.connector
from config import get_db_connection
from datetime import datetime

kegiatan_wr_bp = Blueprint('kegiatan_wr', __name__, url_prefix='/kegiatan-wr')

@kegiatan_wr_bp.route('/my', methods=['GET'])
def get_my_kegiatan_wr():
    """Get kegiatan WR for specific user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id parameter required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
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
            if row.get('waktu_mulai') and hasattr(row['waktu_mulai'], 'total_seconds'):  # type: ignore
                hours, remainder = divmod(row['waktu_mulai'].total_seconds(), 3600)  # type: ignore
                minutes, _ = divmod(remainder, 60)
                row['waktu_mulai'] = f"{int(hours):02d}:{int(minutes):02d}"  # type: ignore

            # Convert date objects to string
            if row.get('tanggal_pelaksanaan'):  # type: ignore
                row['tanggal_pelaksanaan'] = row['tanggal_pelaksanaan'].isoformat()  # type: ignore
            if row.get('created_at'):  # type: ignore
                row['created_at'] = row['created_at'].isoformat()  # type: ignore
            if row.get('updated_at'):  # type: ignore
                row['updated_at'] = row['updated_at'].isoformat()  # type: ignore

        return jsonify({"success": True, "data": result}), 200

    except mysql.connector.Error as e:
        import traceback
        print(f"Database error in get_my_kegiatan_wr: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        print(f"Error in get_my_kegiatan_wr: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@kegiatan_wr_bp.route('', methods=['GET'])
def get_all_kegiatan_wr():
    """Get all kegiatan WR (admin view)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
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
            if row.get('waktu_mulai') and hasattr(row['waktu_mulai'], 'total_seconds'):  # type: ignore
                hours, remainder = divmod(row['waktu_mulai'].total_seconds(), 3600)  # type: ignore
                minutes, _ = divmod(remainder, 60)
                row['waktu_mulai'] = f"{int(hours):02d}:{int(minutes):02d}"  # type: ignore

            # Convert date objects to string
            if row.get('tanggal_pelaksanaan'):  # type: ignore
                row['tanggal_pelaksanaan'] = row['tanggal_pelaksanaan'].isoformat()  # type: ignore
            if row.get('created_at'):  # type: ignore
                row['created_at'] = row['created_at'].isoformat()  # type: ignore
            if row.get('updated_at'):  # type: ignore
                row['updated_at'] = row['updated_at'].isoformat()  # type: ignore

        return jsonify(result), 200

    except mysql.connector.Error as e:
        import traceback
        print(f"Database error in get_all_kegiatan_wr: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        print(f"Error in get_all_kegiatan_wr: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@kegiatan_wr_bp.route('', methods=['POST'])
def create_kegiatan_wr():
    """Create new kegiatan WR"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Validate required fields
    required_fields = ['kategori', 'nama_kegiatan', 'tempat_kegiatan',
                      'tanggal_pelaksanaan', 'waktu_mulai', 'penanggung_jawab',
                      'status_kegiatan', 'user_id']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Field {field} is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO kegiatan_wr
            (kategori, nama_kegiatan, sasaran_kegiatan, tujuan_kegiatan,
             tempat_kegiatan, tanggal_pelaksanaan, waktu_mulai,
             penanggung_jawab, status_kegiatan, keterangan, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['kategori'],
            data['nama_kegiatan'],
            data.get('sasaran_kegiatan'),
            data.get('tujuan_kegiatan'),
            data['tempat_kegiatan'],
            data['tanggal_pelaksanaan'],
            data['waktu_mulai'],
            data['penanggung_jawab'],
            data['status_kegiatan'],
            data.get('keterangan'),
            data['user_id']
        )

        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid

        return jsonify({
            "message": "Kegiatan WR created successfully",
            "id": new_id
        }), 201

    except mysql.connector.Error as e:
        import traceback
        print(f"Database error in create_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        print(f"Error in create_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@kegiatan_wr_bp.route('/<int:id>', methods=['PUT'])
def update_kegiatan_wr(id):
    """Update kegiatan WR"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # Build dynamic update query
        update_fields = []
        values = []

        allowed_fields = ['kategori', 'nama_kegiatan', 'sasaran_kegiatan', 'tujuan_kegiatan',
                         'tempat_kegiatan', 'tanggal_pelaksanaan', 'waktu_mulai',
                         'penanggung_jawab', 'status_kegiatan', 'keterangan']

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
            return jsonify({"error": "Kegiatan WR not found"}), 404

        return jsonify({"message": "Kegiatan WR updated successfully"}), 200

    except mysql.connector.Error as e:
        import traceback
        print(f"Database error in update_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        print(f"Error in update_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@kegiatan_wr_bp.route('/<int:id>', methods=['DELETE'])
def delete_kegiatan_wr(id):
    """Delete kegiatan WR"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        query = "DELETE FROM kegiatan_wr WHERE id_kegiatan_wr = %s"
        cursor.execute(query, (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Kegiatan WR not found"}), 404

        return jsonify({"message": "Kegiatan WR deleted successfully"}), 200

    except mysql.connector.Error as e:
        import traceback
        print(f"Database error in delete_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        print(f"Error in delete_kegiatan_wr: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
