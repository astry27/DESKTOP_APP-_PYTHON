"""
Routes untuk Kelompok Binaan (K. Binaan) - Pengurus Kelompok Binaan
"""

from flask import Blueprint, request, jsonify
from config import get_db_connection
import logging

binaan_bp = Blueprint('binaan', __name__, url_prefix='/binaan')
logger = logging.getLogger(__name__)

@binaan_bp.route('', methods=['GET'])
def get_binaan():
    """Get all Kelompok Binaan pengurus"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM k_binaan ORDER BY nama_lengkap ASC")
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

@binaan_bp.route('', methods=['POST'])
def add_binaan():
    """Add new Kelompok Binaan pengurus"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('nama_lengkap'):
            return jsonify({
                "success": False,
                "data": "Nama lengkap harus diisi",
                "message": "Validation error"
            }), 400

        if not data.get('kelompok_binaan'):
            return jsonify({
                "success": False,
                "data": "Kelompok binaan harus dipilih",
                "message": "Validation error"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                INSERT INTO k_binaan
                (kelompok_binaan, kelompok_binaan_lainnya, nama_lengkap, jenis_kelamin, jabatan, no_hp, email, alamat, wilayah_rohani, masa_jabatan, status, foto_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('kelompok_binaan'),
                data.get('kelompok_binaan_lainnya'),
                data.get('nama_lengkap'),
                data.get('jenis_kelamin'),
                data.get('jabatan'),
                data.get('no_hp'),
                data.get('email'),
                data.get('alamat'),
                data.get('wilayah_rohani'),
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

@binaan_bp.route('/<int:binaan_id>', methods=['PUT'])
def update_binaan(binaan_id):
    """Update Kelompok Binaan pengurus"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('nama_lengkap'):
            return jsonify({
                "success": False,
                "data": "Nama lengkap harus diisi",
                "message": "Validation error"
            }), 400

        if not data.get('kelompok_binaan'):
            return jsonify({
                "success": False,
                "data": "Kelompok binaan harus dipilih",
                "message": "Validation error"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                UPDATE k_binaan
                SET kelompok_binaan = %s, kelompok_binaan_lainnya = %s, nama_lengkap = %s, jenis_kelamin = %s,
                    jabatan = %s, no_hp = %s, email = %s, alamat = %s, wilayah_rohani = %s,
                    masa_jabatan = %s, status = %s, foto_path = %s
                WHERE id_binaan = %s
            """, (
                data.get('kelompok_binaan'),
                data.get('kelompok_binaan_lainnya'),
                data.get('nama_lengkap'),
                data.get('jenis_kelamin'),
                data.get('jabatan'),
                data.get('no_hp'),
                data.get('email'),
                data.get('alamat'),
                data.get('wilayah_rohani'),
                data.get('masa_jabatan'),
                data.get('status', 'Aktif'),
                data.get('foto_path'),
                binaan_id
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

@binaan_bp.route('/<int:binaan_id>', methods=['DELETE'])
def delete_binaan(binaan_id):
    """Delete Kelompok Binaan pengurus"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if exists
            cursor.execute("SELECT id_binaan FROM k_binaan WHERE id_binaan = %s", (binaan_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({
                    "success": False,
                    "data": "Data not found",
                    "message": "Delete failed"
                }), 404

            cursor.execute("DELETE FROM k_binaan WHERE id_binaan = %s", (binaan_id,))
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

@binaan_bp.route('/statistics', methods=['GET'])
def get_binaan_statistics():
    """Get statistics about Kelompok Binaan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total active
        cursor.execute("SELECT COUNT(*) as count FROM k_binaan WHERE status = 'Aktif'")
        aktif_result = cursor.fetchone()
        aktif_count = aktif_result.get('count', 0) if aktif_result else 0

        # Total all
        cursor.execute("SELECT COUNT(*) as count FROM k_binaan")
        total_result = cursor.fetchone()
        total_count = total_result.get('count', 0) if total_result else 0

        # Per kelompok
        cursor.execute("""
            SELECT kelompok_binaan, COUNT(*) as count
            FROM k_binaan
            GROUP BY kelompok_binaan
            ORDER BY kelompok_binaan ASC
        """)
        per_kelompok = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "total": total_count,
                "aktif": aktif_count,
                "per_kelompok": per_kelompok
            },
            "message": "Statistics retrieved successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "data": str(e),
            "message": "Error retrieving statistics"
        }), 500
