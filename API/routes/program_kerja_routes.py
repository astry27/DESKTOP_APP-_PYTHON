# Path: routes/program_kerja_routes.py

from flask import Blueprint, request, jsonify
from config import get_db_connection
import datetime

program_kerja_bp = Blueprint('program_kerja', __name__, url_prefix='/program-kerja')

def check_api_enabled():
    """Check if API is enabled"""
    import os
    try:
        if os.path.exists('api_status.txt'):
            with open('api_status.txt', 'r') as f:
                content = f.read().strip()
                if content != 'enabled':
                    return jsonify({'kategori': 'error', 'message': 'API sedang dinonaktifkan'}), 503
        return None
    except Exception as e:
        print(f"Error checking API status: {e}")
        return None

@program_kerja_bp.route('', methods=['GET'])
def get_program_kerja():
    """Get list of work programs"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'kategori': 'error', 'message': 'Database error'}), 500
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Filter parameters
        search = request.args.get('search', '')
        month = request.args.get('month', '')
        year = request.args.get('year', '')
        
        # Base query
        base_query = """
            SELECT
                id_program_kerja,
                estimasi_waktu,
                judul,
                sasaran,
                penanggung_jawab,
                anggaran,
                sumber_anggaran,
                kategori,
                keterangan,
                created_at,
                updated_at
            FROM program_kerja
            WHERE 1=1
        """
        
        params = []
        
        # Add filters
        if search:
            base_query += " AND (judul LIKE %s OR sasaran LIKE %s OR penanggung_jawab LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        if month:
            base_query += " AND MONTH(estimasi_waktu) = %s"
            params.append(month)

        if year:
            base_query += " AND YEAR(estimasi_waktu) = %s"
            params.append(year)

        base_query += " ORDER BY estimasi_waktu ASC"
        
        cursor.execute(base_query, params)
        program_list = cursor.fetchall()
        
        # Convert dates to string for JSON serialization
        for program in program_list:
            if program.get('estimasi_waktu'):
                program['estimasi_waktu'] = str(program['estimasi_waktu'])  # type: ignore
            if program.get('created_at'):
                program['created_at'] = program['created_at'].isoformat()  # type: ignore
            if program.get('updated_at'):
                program['updated_at'] = program['updated_at'].isoformat()  # type: ignore
        
        return jsonify({
            'kategori': 'success',
            'data': program_list,
            'total': len(program_list)
        })
        
    except Exception as e:
        print(f"Error getting program kerja: {e}")
        return jsonify({'kategori': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@program_kerja_bp.route('', methods=['POST'])
def add_program_kerja():
    """Add new work program"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'kategori': 'error', 'message': 'Database error'}), 500
        
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['estimasi_waktu', 'judul']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'kategori': 'error', 'message': f'Field {field} harus diisi'}), 400
        
        cursor = connection.cursor()
        
        # Insert new program
        query = """
            INSERT INTO program_kerja (
                estimasi_waktu, judul, sasaran, penanggung_jawab, anggaran, sumber_anggaran, kategori, keterangan
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            data.get('estimasi_waktu'),
            data.get('judul'),
            data.get('sasaran', ''),
            data.get('penanggung_jawab', ''),
            data.get('anggaran', ''),
            data.get('sumber_anggaran', 'Kas Gereja'),
            data.get('kategori', ''),
            data.get('keterangan', '')
        )
        
        cursor.execute(query, values)
        program_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            'kategori': 'success',
            'message': f'Program kerja "{data.get("judul")}" berhasil ditambahkan',
            'id': program_id
        })
        
    except Exception as e:
        print(f"Error adding program kerja: {e}")
        return jsonify({'kategori': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@program_kerja_bp.route('/<int:program_id>', methods=['PUT'])
def update_program_kerja(program_id):
    """Update work program"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'kategori': 'error', 'message': 'Database error'}), 500
        
    try:
        data = request.get_json()
        
        cursor = connection.cursor()
        
        # Check if program exists
        cursor.execute("SELECT id_program_kerja FROM program_kerja WHERE id_program_kerja = %s", (program_id,))
        if not cursor.fetchone():
            return jsonify({'kategori': 'error', 'message': 'Program kerja tidak ditemukan'}), 404
        
        # Update program
        query = """
            UPDATE program_kerja SET
                estimasi_waktu = %s, judul = %s, sasaran = %s, penanggung_jawab = %s,
                anggaran = %s, sumber_anggaran = %s, kategori = %s, keterangan = %s
            WHERE id_program_kerja = %s
        """

        values = (
            data.get('estimasi_waktu'),
            data.get('judul'),
            data.get('sasaran', ''),
            data.get('penanggung_jawab', ''),
            data.get('anggaran', ''),
            data.get('sumber_anggaran', 'Kas Gereja'),
            data.get('kategori', ''),
            data.get('keterangan', ''),
            program_id
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            'kategori': 'success',
            'message': f'Program kerja "{data.get("judul")}" berhasil diupdate'
        })
        
    except Exception as e:
        print(f"Error updating program kerja: {e}")
        return jsonify({'kategori': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@program_kerja_bp.route('/<int:program_id>', methods=['DELETE'])
def delete_program_kerja(program_id):
    """Delete work program"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'kategori': 'error', 'message': 'Database error'}), 500
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if program exists and get title
        cursor.execute("SELECT judul FROM program_kerja WHERE id_program_kerja = %s", (program_id,))
        program = cursor.fetchone()
        if not program:
            return jsonify({'kategori': 'error', 'message': 'Program kerja tidak ditemukan'}), 404
        
        # Delete program
        cursor.execute("DELETE FROM program_kerja WHERE id_program_kerja = %s", (program_id,))
        connection.commit()
        
        judul = program.get('judul', 'Unknown')

        return jsonify({
            'kategori': 'success',
            'message': f'Program kerja "{judul}" berhasil dihapus'
        })
        
    except Exception as e:
        print(f"Error deleting program kerja: {e}")
        return jsonify({'kategori': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@program_kerja_bp.route('/statistics', methods=['GET'])
def get_program_statistics():
    """Get work program statistics"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'kategori': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total programs
        cursor.execute("SELECT COUNT(*) as total FROM program_kerja")
        total_result = cursor.fetchone()
        total = total_result.get('total', 0) if total_result else 0
        
        # Programs by category
        cursor.execute("""
            SELECT kategori, COUNT(*) as jumlah
            FROM program_kerja
            GROUP BY kategori
            ORDER BY jumlah DESC
        """)
        by_status = cursor.fetchall()

        # Programs by month (current year)
        cursor.execute("""
            SELECT MONTH(estimasi_waktu) as bulan, COUNT(*) as jumlah
            FROM program_kerja
            WHERE YEAR(estimasi_waktu) = YEAR(NOW())
            GROUP BY MONTH(estimasi_waktu)
            ORDER BY bulan
        """)
        by_month = cursor.fetchall()
        
        return jsonify({
            'kategori': 'success',
            'data': {
                'total': total,
                'by_status': by_status,
                'by_month': by_month
            }
        })
        
    except Exception as e:
        print(f"Error getting program statistics: {e}")
        return jsonify({'kategori': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()