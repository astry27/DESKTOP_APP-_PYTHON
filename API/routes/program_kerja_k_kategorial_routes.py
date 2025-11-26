# Path: routes/program_kerja_k_kategorial_routes.py
# Routes untuk Program Kerja K. Kategorial

from flask import Blueprint, request, jsonify, session
from typing import Tuple, Dict, Any
import datetime

# Blueprint
program_kerja_k_kategorial_bp = Blueprint('program_kerja_k_kategorial', __name__, url_prefix='/program-kerja-k-kategorial')


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

@program_kerja_k_kategorial_bp.route('', methods=['GET'])
def get_program_kerja_k_kategorial_list():
    """Get list of program kerja K. Kategorial"""
    try:
        if not check_user_logged_in():
            return error_response("User tidak terautentikasi", 401)

        from config import get_db
        db = get_db()

        user_id = get_current_user_id()
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
            WHERE created_by = %s
        """
        params = [user_id]

        if search:
            query += " AND (program_kerja LIKE %s OR subyek_sasaran LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY created_at DESC"

        cursor = db.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Format hasil
        programs = []
        for row in rows:
            program = {
                'id_program_kerja_k_kategorial': row[0],
                'program_kerja': row[1],
                'subyek_sasaran': row[2],
                'indikator_pencapaian': row[3],
                'model_bentuk_metode': row[4],
                'materi': row[5],
                'tempat': row[6],
                'waktu': row[7],
                'pic': row[8],
                'perincian': row[9],
                'quantity': row[10],
                'satuan': row[11],
                'harga_satuan': float(row[12]) if row[12] else 0,
                'frekuensi': row[13],
                'jumlah': float(row[14]) if row[14] else 0,
                'total': float(row[15]) if row[15] else 0,
                'keterangan': row[16],
                'created_by': row[17],
                'created_at': row[18].isoformat() if row[18] else None,
                'updated_at': row[19].isoformat() if row[19] else None
            }
            programs.append(program)

        cursor.close()

        return success_response({"data": programs}, "Program kerja K. Kategorial berhasil dimuat")

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
    try:
        if not check_user_logged_in():
            return error_response("User tidak terautentikasi", 401)

        from config import get_db
        db = get_db()

        user_id = get_current_user_id()
        data = request.get_json()

        # Validasi input
        if not data.get('program_kerja'):
            return error_response("Program kerja tidak boleh kosong")

        # Hitung jumlah dan total
        quantity = data.get('quantity', 0)
        frekuensi = data.get('frekuensi', 1)
        harga_satuan = data.get('harga_satuan', 0)
        jumlah = quantity * frekuensi if quantity and frekuensi else 0
        total = jumlah * harga_satuan if jumlah and harga_satuan else 0

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
            user_id
        )

        cursor = db.cursor()
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

        db.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "data": None,
            "message": "Program kerja K. Kategorial berhasil ditambahkan"
        }), 201

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>', methods=['PUT'])
def update_program_kerja_k_kategorial(program_id):
    """Update program kerja K. Kategorial"""
    try:
        if not check_user_logged_in():
            return error_response("User tidak terautentikasi", 401)

        from config import get_db
        db = get_db()

        user_id = get_current_user_id()
        data = request.get_json()

        # Check ownership
        cursor = db.cursor()
        cursor.execute("SELECT created_by FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return error_response("Program kerja tidak ditemukan", 404)

        if result[0] != user_id:
            cursor.close()
            return error_response("Anda hanya dapat mengedit program kerja yang Anda buat", 403)

        # Hitung jumlah dan total
        quantity = data.get('quantity', 0)
        frekuensi = data.get('frekuensi', 1)
        harga_satuan = data.get('harga_satuan', 0)
        jumlah = quantity * frekuensi if quantity and frekuensi else 0
        total = jumlah * harga_satuan if jumlah and harga_satuan else 0

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

        db.commit()
        cursor.close()

        return success_response(None, "Program kerja K. Kategorial berhasil diperbarui")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)


@program_kerja_k_kategorial_bp.route('/<int:program_id>', methods=['DELETE'])
def delete_program_kerja_k_kategorial(program_id):
    """Delete program kerja K. Kategorial"""
    try:
        if not check_user_logged_in():
            return error_response("User tidak terautentikasi", 401)

        from config import get_db
        db = get_db()

        user_id = get_current_user_id()

        # Check ownership
        cursor = db.cursor()
        cursor.execute("SELECT created_by FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return error_response("Program kerja tidak ditemukan", 404)

        if result[0] != user_id:
            cursor.close()
            return error_response("Anda hanya dapat menghapus program kerja yang Anda buat", 403)

        # Delete (cascade akan menghapus budget dan evaluation juga)
        cursor.execute("DELETE FROM program_kerja_k_kategorial WHERE id_program_kerja_k_kategorial = %s", (program_id,))
        db.commit()
        cursor.close()

        return success_response(None, "Program kerja K. Kategorial berhasil dihapus")

    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)
