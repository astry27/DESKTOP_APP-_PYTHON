"""
Routes untuk Wilayah Rohani (WR) - Pengurus Wilayah Rohani
"""

from flask import Blueprint, request, jsonify
from config import get_db_connection
import logging

wr_bp = Blueprint('wr', __name__, url_prefix='/wr')
logger = logging.getLogger(__name__)

@wr_bp.route('', methods=['GET'])
def get_wr():
    """Get all Wilayah Rohani pengurus"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM wilayah_rohani ORDER BY nama_lengkap ASC")
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": data,
            "message": "Data retrieved successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error retrieving data"
        }), 500

@wr_bp.route('', methods=['POST'])
def add_wr():
    """Add new Wilayah Rohani pengurus"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('nama_lengkap'):
            return jsonify({
                "success": False,
                "data": "Nama lengkap harus diisi",
                "message": "Validation error"
            }), 400

        if not data.get('wilayah_rohani'):
            return jsonify({
                "success": False,
                "data": "Wilayah rohani harus dipilih",
                "message": "Validation error"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                INSERT INTO wilayah_rohani
                (wilayah_rohani, nama_lengkap, jenis_kelamin, jabatan, no_hp, email, alamat, masa_jabatan, status, foto_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('wilayah_rohani'),
                data.get('nama_lengkap'),
                data.get('jenis_kelamin'),
                data.get('jabatan'),
                data.get('no_hp'),
                data.get('email'),
                data.get('alamat'),
                data.get('masa_jabatan'),
                data.get('status', 'Aktif'),
                data.get('foto_path')
            ))

            conn.commit()
            new_id = cursor.lastrowid

            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "data": new_id,
                "message": "Data added successfully"
            }), 201
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise e
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error adding data"
        }), 500

@wr_bp.route('/<int:wr_id>', methods=['PUT'])
def update_wr(wr_id):
    """Update Wilayah Rohani pengurus"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('nama_lengkap'):
            return jsonify({
                "success": False,
                "data": "Nama lengkap harus diisi",
                "message": "Validation error"
            }), 400

        if not data.get('wilayah_rohani'):
            return jsonify({
                "success": False,
                "data": "Wilayah rohani harus dipilih",
                "message": "Validation error"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                UPDATE wilayah_rohani
                SET wilayah_rohani = %s, nama_lengkap = %s, jenis_kelamin = %s,
                    jabatan = %s, no_hp = %s, email = %s, alamat = %s,
                    masa_jabatan = %s, status = %s, foto_path = %s
                WHERE id_wilayah = %s
            """, (
                data.get('wilayah_rohani'),
                data.get('nama_lengkap'),
                data.get('jenis_kelamin'),
                data.get('jabatan'),
                data.get('no_hp'),
                data.get('email'),
                data.get('alamat'),
                data.get('masa_jabatan'),
                data.get('status', 'Aktif'),
                data.get('foto_path'),
                wr_id
            ))

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "data": "Data updated successfully",
                "message": "Update successful"
            }), 200
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise e
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error updating data"
        }), 500

@wr_bp.route('/<int:wr_id>', methods=['DELETE'])
def delete_wr(wr_id):
    """Delete Wilayah Rohani pengurus"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if exists
            cursor.execute("SELECT id_wilayah FROM wilayah_rohani WHERE id_wilayah = %s", (wr_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({
                    "success": False,
                    "data": "Data not found",
                    "message": "Delete failed"
                }), 404

            cursor.execute("DELETE FROM wilayah_rohani WHERE id_wilayah = %s", (wr_id,))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "data": "Data deleted successfully",
                "message": "Delete successful"
            }), 200
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise e
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error deleting data"
        }), 500

@wr_bp.route('/statistics', methods=['GET'])
def get_wr_statistics():
    """Get statistics about Wilayah Rohani"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total active
        cursor.execute("SELECT COUNT(*) as count FROM wilayah_rohani WHERE status = 'Aktif'")
        aktif_result = cursor.fetchone()
        aktif_count = aktif_result.get('count', 0) if aktif_result else 0

        # Total all
        cursor.execute("SELECT COUNT(*) as count FROM wilayah_rohani")
        total_result = cursor.fetchone()
        total_count = total_result.get('count', 0) if total_result else 0

        # Per wilayah
        cursor.execute("""
            SELECT wilayah_rohani, COUNT(*) as count
            FROM wilayah_rohani
            GROUP BY wilayah_rohani
            ORDER BY wilayah_rohani ASC
        """)
        per_wilayah = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "total": total_count,
                "aktif": aktif_count,
                "per_wilayah": per_wilayah
            },
            "message": "Statistics retrieved successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error retrieving statistics"
        }), 500
