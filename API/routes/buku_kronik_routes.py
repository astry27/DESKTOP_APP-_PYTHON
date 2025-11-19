# Path: routes/buku_kronik_routes.py
# Routes untuk Buku Kronik (Church Chronicles/Event Log)

from flask import Blueprint, request, jsonify, session
from typing import Tuple, Dict, Any
import datetime

# Blueprint
buku_kronik_bp = Blueprint('buku_kronik', __name__, url_prefix='/buku-kronik')


# ========== HELPER FUNCTIONS ==========
def check_user_logged_in():
    """Check if user is logged in"""
    if 'user_id' not in session:
        return False
    return True


def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')


def success_response(data=None, message="Success"):
    """Return success response"""
    return jsonify({
        "success": True,
        "data": data,
        "message": message
    }), 200


def error_response(message="Error", status_code=400):
    """Return error response"""
    return jsonify({
        "success": False,
        "data": message
    }), status_code


# ========== ROUTES ==========

@buku_kronik_bp.route('', methods=['GET'])
def get_buku_kronik_list():
    """Get list of all peristiwa/kronik entries"""
    try:
        # Admin dapat mengakses tanpa perlu session (api_client dari server admin tidak memiliki session)
        from config import get_db_connection
        db = get_db_connection()

        if not db:
            return error_response("Database connection failed", 500)

        # Get all kronik entries sorted by date descending
        query = """
            SELECT
                id_kronik,
                tanggal,
                peristiwa,
                keterangan,
                created_by,
                created_at,
                updated_at
            FROM buku_kronik
            ORDER BY tanggal DESC, created_at DESC
        """

        cursor = db.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format hasil
        kronik_list = []
        for row in rows:
            # Convert datetime objects to ISO format strings
            if row['tanggal']:
                row['tanggal'] = row['tanggal'].isoformat()
            if row['created_at']:
                row['created_at'] = row['created_at'].isoformat()
            if row['updated_at']:
                row['updated_at'] = row['updated_at'].isoformat()
            kronik = {
                'id_kronik': row['id_kronik'],
                'tanggal': row['tanggal'],
                'peristiwa': row['peristiwa'],
                'keterangan': row['keterangan'],
                'created_by': row['created_by'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            kronik_list.append(kronik)

        cursor.close()
        db.close()

        return success_response({"data": kronik_list}, "Buku kronik berhasil dimuat")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@buku_kronik_bp.route('', methods=['POST'])
def add_peristiwa():
    """Add new peristiwa/kronik entry"""
    try:
        # Admin dapat mengakses tanpa perlu session
        from config import get_db_connection
        db = get_db_connection()

        if not db:
            return error_response("Database connection failed", 500)

        data = request.get_json()

        # Validasi input
        if not data.get('tanggal'):
            return error_response("Tanggal tidak boleh kosong")
        if not data.get('peristiwa'):
            return error_response("Peristiwa tidak boleh kosong")

        # Insert peristiwa ke database
        query = """
            INSERT INTO buku_kronik
            (tanggal, peristiwa, keterangan, created_by, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """

        # Get created_by from request data (admin ID)
        created_by = data.get('created_by', 1)  # Default to 1 if not provided

        params = (
            data.get('tanggal'),  # Format: YYYY-MM-DD
            data.get('peristiwa', ''),
            data.get('keterangan', ''),
            created_by
        )

        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params)
        db.commit()

        # Get the inserted ID
        inserted_id = cursor.lastrowid

        # Fetch the newly inserted data
        fetch_query = "SELECT * FROM buku_kronik WHERE id_kronik = %s"
        cursor.execute(fetch_query, (inserted_id,))
        new_peristiwa = cursor.fetchone()

        cursor.close()
        db.close()

        return jsonify({
            'success': True,
            'message': 'Peristiwa berhasil ditambahkan',
            'data': new_peristiwa
        }), 201

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@buku_kronik_bp.route('/<int:kronik_id>', methods=['PUT'])
def update_peristiwa(kronik_id):
    """Update peristiwa/kronik entry"""
    try:
        # Admin dapat mengakses tanpa perlu session
        from config import get_db_connection
        db = get_db_connection()

        if not db:
            return error_response("Database connection failed", 500)

        data = request.get_json()

        # Validasi input
        if not data.get('tanggal'):
            return error_response("Tanggal tidak boleh kosong")
        if not data.get('peristiwa'):
            return error_response("Peristiwa tidak boleh kosong")

        # Check if kronik exists
        check_query = "SELECT id_kronik FROM buku_kronik WHERE id_kronik = %s"
        cursor = db.cursor(dictionary=True)
        cursor.execute(check_query, (kronik_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return error_response("Peristiwa tidak ditemukan", 404)

        # Update peristiwa
        query = """
            UPDATE buku_kronik
            SET tanggal = %s, peristiwa = %s, keterangan = %s, updated_at = NOW()
            WHERE id_kronik = %s
        """

        params = (
            data.get('tanggal'),
            data.get('peristiwa', ''),
            data.get('keterangan', ''),
            kronik_id
        )

        cursor.execute(query, params)
        db.commit()

        # Fetch the updated data
        fetch_query = "SELECT * FROM buku_kronik WHERE id_kronik = %s"
        cursor.execute(fetch_query, (kronik_id,))
        updated_peristiwa = cursor.fetchone()

        cursor.close()
        db.close()

        return jsonify({
            'success': True,
            'message': 'Peristiwa berhasil diperbarui',
            'data': updated_peristiwa
        })

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@buku_kronik_bp.route('/<int:kronik_id>', methods=['DELETE'])
def delete_peristiwa(kronik_id):
    """Delete peristiwa/kronik entry"""
    try:
        # Admin dapat mengakses tanpa perlu session
        from config import get_db_connection
        db = get_db_connection()

        if not db:
            return error_response("Database connection failed", 500)

        # Check if kronik exists
        check_query = "SELECT id_kronik FROM buku_kronik WHERE id_kronik = %s"
        cursor = db.cursor()
        cursor.execute(check_query, (kronik_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return error_response("Peristiwa tidak ditemukan", 404)

        # Delete peristiwa
        delete_query = "DELETE FROM buku_kronik WHERE id_kronik = %s"
        cursor.execute(delete_query, (kronik_id,))
        db.commit()
        cursor.close()
        db.close()

        return jsonify({
            'success': True,
            'message': 'Peristiwa berhasil dihapus',
            'data': None
        })

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@buku_kronik_bp.route('/search', methods=['GET'])
def search_peristiwa():
    """Search peristiwa by date range or keyword"""
    try:
        # Admin dapat mengakses tanpa perlu session
        from config import get_db_connection
        db = get_db_connection()

        if not db:
            return error_response("Database connection failed", 500)

        # Get query parameters
        search_keyword = request.args.get('q', '')  # Search by peristiwa or keterangan
        start_date = request.args.get('start_date', '')  # YYYY-MM-DD
        end_date = request.args.get('end_date', '')  # YYYY-MM-DD

        query = "SELECT id_kronik, tanggal, peristiwa, keterangan, created_by, created_at, updated_at FROM buku_kronik WHERE 1=1"
        params = []

        # Add keyword search
        if search_keyword:
            query += " AND (peristiwa LIKE %s OR keterangan LIKE %s)"
            params.extend([f"%{search_keyword}%", f"%{search_keyword}%"])

        # Add date range filter
        if start_date:
            query += " AND tanggal >= %s"
            params.append(start_date)
        if end_date:
            query += " AND tanggal <= %s"
            params.append(end_date)

        # Order by date descending
        query += " ORDER BY tanggal DESC, created_at DESC"

        cursor = db.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Format hasil
        kronik_list = []
        for row in rows:
            kronik = {
                'id_kronik': row[0],
                'tanggal': row[1].isoformat() if row[1] else None,
                'peristiwa': row[2],
                'keterangan': row[3],
                'created_by': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'updated_at': row[6].isoformat() if row[6] else None
            }
            kronik_list.append(kronik)

        cursor.close()
        db.close()

        return success_response({"data": kronik_list}, "Pencarian berhasil")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)
