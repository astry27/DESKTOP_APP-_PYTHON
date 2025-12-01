# Path: routes/program_kerja_k_kategorial_routes.py
# Routes untuk Program Kerja K. Kategorial

from flask import Blueprint, request, jsonify
from typing import Tuple, Dict, Any
import datetime
import os

# Blueprint
program_kerja_k_kategorial_bp = Blueprint('program_kerja_k_kategorial', __name__, url_prefix='/program-kerja-k-kategorial')

API_STATUS_FILE = 'api_status.txt'

# ========== HELPER FUNCTIONS ==========
def get_api_status():
    """Get API enabled/disabled status"""
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
    """Check if API is enabled"""
    if not get_api_status():
        return jsonify({
            'status': 'error',
            'message': 'API sedang dinonaktifkan'
        }), 503
    return None


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

@program_kerja_k_kategorial_bp.route('', methods=['GET'])
def get_program_kerja_k_kategorial_list():
    """Get list of program kerja K. Kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    try:
        from config import get_db_connection
        connection = get_db_connection()

        if not connection:
            return error_response("Database tidak tersedia", 500)

        search = request.args.get('search', '')

        query = """
            SELECT
                id_program_kerja_k_kategorial,
                program_kerja,
                subyek_sasaran,
                indikator_pencapaian,
                model_bentuk_metode,
                materi,
                tempat,
                waktu,
                pic,
                perincian,
                quantity,
                satuan,
                harga_satuan,
                frekuensi,
                jumlah,
                total,
                keterangan,
                created_by,
                created_at,
                updated_at
            FROM program_kerja_k_kategorial
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (program_kerja LIKE %s OR subyek_sasaran LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY created_at DESC"

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Format hasil
        programs = []
        for row in rows:
            # Safely convert numeric fields
            def safe_float(value, default=0):
                """Safely convert value to float"""
                if value is None:
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

            program = {
                'id_program_kerja_k_kategorial': row.get('id_program_kerja_k_kategorial'),
                'program_kerja': row.get('program_kerja', ''),
                'subyek_sasaran': row.get('subyek_sasaran', ''),
                'indikator_pencapaian': row.get('indikator_pencapaian', ''),
                'model_bentuk_metode': row.get('model_bentuk_metode', ''),
                'materi': row.get('materi', ''),
                'tempat': row.get('tempat', ''),
                'waktu': row.get('waktu', ''),
                'pic': row.get('pic', ''),
                'perincian': row.get('perincian', ''),
                'quantity': row.get('quantity', ''),
                'satuan': row.get('satuan', ''),
                'harga_satuan': safe_float(row.get('harga_satuan')),
                'frekuensi': row.get('frekuensi', 1),
                'jumlah': safe_float(row.get('jumlah')),
                'total': safe_float(row.get('total')),
                'keterangan': row.get('keterangan', ''),
                'created_by': row.get('created_by'),
                'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
                'updated_at': row.get('updated_at').isoformat() if row.get('updated_at') else None
            }
            programs.append(program)

        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "data": {"data": programs},
            "message": "Program kerja K. Kategorial berhasil dimuat"
        }), 200

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>/budget', methods=['GET'])
def get_program_budget(program_id):
    """Get budget sources for a program"""
    try:
        from config import get_db
        db = get_db()

        query = """
            SELECT
                id_budget,
                sumber_anggaran,
                sumber_anggaran_lainnya,
                jumlah_anggaran,
                nama_akun_pengeluaran,
                sumber_pembiayaan
            FROM program_kerja_k_kategorial_budget
            WHERE id_program_kerja_k_kategorial = %s
            ORDER BY id_budget
        """

        cursor = db.cursor()
        cursor.execute(query, (program_id,))
        rows = cursor.fetchall()

        budgets = []
        for row in rows:
            budget = {
                'id_budget': row[0],
                'sumber_anggaran': row[1],
                'sumber_anggaran_lainnya': row[2],
                'jumlah_anggaran': float(row[3]) if row[3] else 0,
                'nama_akun_pengeluaran': row[4],
                'sumber_pembiayaan': row[5]
            }
            budgets.append(budget)

        cursor.close()

        return success_response({"data": budgets}, "Budget sources berhasil dimuat")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>/evaluation', methods=['GET'])
def get_program_evaluation(program_id):
    """Get evaluation for a program"""
    try:
        from config import get_db
        db = get_db()

        query = """
            SELECT
                id_evaluation,
                evaluasi_program,
                status,
                tindak_lanjut,
                keterangan_evaluasi
            FROM program_kerja_k_kategorial_evaluation
            WHERE id_program_kerja_k_kategorial = %s
        """

        cursor = db.cursor()
        cursor.execute(query, (program_id,))
        row = cursor.fetchone()

        if row:
            evaluation = {
                'id_evaluation': row[0],
                'evaluasi_program': row[1],
                'status': row[2],
                'tindak_lanjut': row[3],
                'keterangan_evaluasi': row[4]
            }
        else:
            evaluation = None

        cursor.close()

        return success_response({"data": evaluation}, "Evaluation berhasil dimuat")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('', methods=['POST'])
def add_program_kerja_k_kategorial():
    """Add new program kerja K. Kategorial with budget and evaluation"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    try:
        from config import get_db_connection
        connection = get_db_connection()

        if not connection:
            return error_response("Database tidak tersedia", 500)

        data = request.get_json()

        # Validasi input
        if not data.get('program_kerja'):
            return error_response("Program kerja tidak boleh kosong")

        # Admin tidak perlu created_by dari session, bisa null atau dari data
        created_by = data.get('created_by', None)

        # Hitung jumlah dan total
        quantity = data.get('quantity', 0)
        frekuensi = data.get('frekuensi', 1)
        harga_satuan = data.get('harga_satuan', 0)

        # Convert to numeric
        try:
            quantity = float(quantity) if quantity else 0
            frekuensi = int(frekuensi) if frekuensi else 1
            harga_satuan = float(harga_satuan) if harga_satuan else 0
        except (ValueError, TypeError):
            quantity = 0
            frekuensi = 1
            harga_satuan = 0

        jumlah = quantity * frekuensi
        total = jumlah * harga_satuan

        # Insert program ke database
        query = """
            INSERT INTO program_kerja_k_kategorial
            (program_kerja, subyek_sasaran, indikator_pencapaian, model_bentuk_metode,
             materi, tempat, waktu, pic, perincian, quantity, satuan, harga_satuan,
             frekuensi, jumlah, total, keterangan, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """

        params = (
            data.get('program_kerja', ''),
            data.get('subyek_sasaran', ''),
            data.get('indikator_pencapaian', ''),
            data.get('model_bentuk_metode', ''),
            data.get('materi', ''),
            data.get('tempat', ''),
            data.get('waktu', ''),
            data.get('pic', ''),
            data.get('perincian', ''),
            quantity,
            data.get('satuan', ''),
            harga_satuan,
            frekuensi,
            jumlah,
            total,
            data.get('keterangan', ''),
            created_by
        )

        cursor = connection.cursor()
        cursor.execute(query, params)
        program_id = cursor.lastrowid

        # Insert budget sources jika ada
        budgets = data.get('budgets', [])
        if budgets:
            budget_query = """
                INSERT INTO program_kerja_k_kategorial_budget
                (id_program_kerja_k_kategorial, sumber_anggaran, sumber_anggaran_lainnya,
                 jumlah_anggaran, nama_akun_pengeluaran, sumber_pembiayaan, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            for budget in budgets:
                budget_params = (
                    program_id,
                    budget.get('sumber_anggaran', ''),
                    budget.get('sumber_anggaran_lainnya', ''),
                    budget.get('jumlah_anggaran', 0),
                    budget.get('nama_akun_pengeluaran', ''),
                    budget.get('sumber_pembiayaan', '')
                )
                cursor.execute(budget_query, budget_params)

        # Insert evaluation jika ada
        evaluation = data.get('evaluation', {})
        if evaluation:
            eval_query = """
                INSERT INTO program_kerja_k_kategorial_evaluation
                (id_program_kerja_k_kategorial, evaluasi_program, status,
                 tindak_lanjut, keterangan_evaluasi, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            eval_params = (
                program_id,
                evaluation.get('evaluasi_program', ''),
                evaluation.get('status', 'Direncanakan'),
                evaluation.get('tindak_lanjut', ''),
                evaluation.get('keterangan_evaluasi', '')
            )
            cursor.execute(eval_query, eval_params)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "data": {"id": program_id},
            "message": "Program kerja K. Kategorial berhasil ditambahkan"
        }), 201

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>', methods=['PUT'])
def update_program_kerja_k_kategorial(program_id):
    """Update program kerja K. Kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    try:
        from config import get_db_connection
        connection = get_db_connection()

        if not connection:
            return error_response("Database tidak tersedia", 500)

        data = request.get_json()

        # Check if program exists
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_program_kerja_k_kategorial FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            connection.close()
            return error_response("Program kerja tidak ditemukan", 404)

        # Hitung jumlah dan total
        quantity = data.get('quantity', 0)
        frekuensi = data.get('frekuensi', 1)
        harga_satuan = data.get('harga_satuan', 0)

        # Convert to numeric
        try:
            quantity = float(quantity) if quantity else 0
            frekuensi = int(frekuensi) if frekuensi else 1
            harga_satuan = float(harga_satuan) if harga_satuan else 0
        except (ValueError, TypeError):
            quantity = 0
            frekuensi = 1
            harga_satuan = 0

        jumlah = quantity * frekuensi
        total = jumlah * harga_satuan

        # Update program
        query = """
            UPDATE program_kerja_k_kategorial
            SET program_kerja = %s, subyek_sasaran = %s, indikator_pencapaian = %s,
                model_bentuk_metode = %s, materi = %s, tempat = %s, waktu = %s,
                pic = %s, perincian = %s, quantity = %s, satuan = %s, harga_satuan = %s,
                frekuensi = %s, jumlah = %s, total = %s, keterangan = %s, updated_at = NOW()
            WHERE id_program_kerja_k_kategorial = %s
        """

        params = (
            data.get('program_kerja', ''),
            data.get('subyek_sasaran', ''),
            data.get('indikator_pencapaian', ''),
            data.get('model_bentuk_metode', ''),
            data.get('materi', ''),
            data.get('tempat', ''),
            data.get('waktu', ''),
            data.get('pic', ''),
            data.get('perincian', ''),
            quantity,
            data.get('satuan', ''),
            harga_satuan,
            frekuensi,
            jumlah,
            total,
            data.get('keterangan', ''),
            program_id
        )

        cursor.execute(query, params)

        # Update budget sources - delete old and insert new
        cursor.execute("DELETE FROM program_kerja_k_kategorial_budget WHERE id_program_kerja_k_kategorial = %s", (program_id,))

        budgets = data.get('budgets', [])
        if budgets:
            budget_query = """
                INSERT INTO program_kerja_k_kategorial_budget
                (id_program_kerja_k_kategorial, sumber_anggaran, sumber_anggaran_lainnya,
                 jumlah_anggaran, nama_akun_pengeluaran, sumber_pembiayaan, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            for budget in budgets:
                budget_params = (
                    program_id,
                    budget.get('sumber_anggaran', ''),
                    budget.get('sumber_anggaran_lainnya', ''),
                    budget.get('jumlah_anggaran', 0),
                    budget.get('nama_akun_pengeluaran', ''),
                    budget.get('sumber_pembiayaan', '')
                )
                cursor.execute(budget_query, budget_params)

        # Update evaluation - delete old and insert new
        cursor.execute("DELETE FROM program_kerja_k_kategorial_evaluation WHERE id_program_kerja_k_kategorial = %s", (program_id,))

        evaluation = data.get('evaluation', {})
        if evaluation:
            eval_query = """
                INSERT INTO program_kerja_k_kategorial_evaluation
                (id_program_kerja_k_kategorial, evaluasi_program, status,
                 tindak_lanjut, keterangan_evaluasi, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            eval_params = (
                program_id,
                evaluation.get('evaluasi_program', ''),
                evaluation.get('status', 'Direncanakan'),
                evaluation.get('tindak_lanjut', ''),
                evaluation.get('keterangan_evaluasi', '')
            )
            cursor.execute(eval_query, eval_params)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "data": None,
            "message": "Program kerja K. Kategorial berhasil diperbarui"
        }), 200

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>', methods=['DELETE'])
def delete_program_kerja_k_kategorial(program_id):
    """Delete program kerja K. Kategorial"""
    status_check = check_api_enabled()
    if status_check:
        return status_check

    try:
        from config import get_db_connection
        connection = get_db_connection()

        if not connection:
            return error_response("Database tidak tersedia", 500)

        # Check if program exists
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_program_kerja_k_kategorial FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            connection.close()
            return error_response("Program kerja tidak ditemukan", 404)

        # Delete (cascade akan menghapus budget dan evaluation juga jika ada ON DELETE CASCADE)
        cursor.execute("DELETE FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "status": "success",
            "data": None,
            "message": "Program kerja K. Kategorial berhasil dihapus"
        }), 200

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)
