from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime

broadcast_bp = Blueprint('broadcast', __name__, url_prefix='/broadcast')

@broadcast_bp.route('/jemaat', methods=['POST'])
def broadcast_jemaat():
    data = request.get_json()
    admin_id = data.get('admin_id')
    selected_ids = data.get('selected_ids', [])
    
    if not admin_id:
        return jsonify({'status': 'error', 'message': 'Admin ID required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if selected_ids:
            placeholders = ','.join(['%s'] * len(selected_ids))
            query = f"""
                SELECT id_jemaat, nama_lengkap, tanggal_lahir, alamat, no_telepon, 
                       email, status_pernikahan, status_keanggotaan, created_at, updated_at
                FROM jemaat 
                WHERE id_jemaat IN ({placeholders})
                ORDER BY created_at DESC
            """
            cursor.execute(query, selected_ids)
        else:
            cursor.execute("""
                SELECT id_jemaat, nama_lengkap, tanggal_lahir, alamat, no_telepon, 
                       email, status_pernikahan, status_keanggotaan, created_at, updated_at
                FROM jemaat 
                ORDER BY created_at DESC
            """)
        result = cursor.fetchall()
        
        for jemaat in result:
            if jemaat.get('tanggal_lahir'):  # type: ignore
                jemaat['tanggal_lahir'] = jemaat['tanggal_lahir'].strftime('%Y-%m-%d')  # type: ignore
            if jemaat.get('created_at'):  # type: ignore
                jemaat['created_at'] = jemaat['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if jemaat.get('updated_at'):  # type: ignore
                jemaat['updated_at'] = jemaat['updated_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
        
        return jsonify({
            'status': 'success',
            'message': f'Data jemaat berhasil dibroadcast ke client',
            'data': result,
            'total': len(result),
            'broadcast_by': admin_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        connection.close()

@broadcast_bp.route('/jemaat', methods=['GET'])
def get_broadcast_jemaat():
    return jsonify({
        'status': 'success',
        'data': [],
        'total': 0,
        'message': 'No broadcast data available. Admin must broadcast first.'
    })

@broadcast_bp.route('/kegiatan', methods=['GET'])
def get_broadcast_kegiatan():
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_kegiatan, nama_kegiatan, deskripsi, tanggal_mulai, 
                   tanggal_selesai, lokasi, penanggungjawab, status, 
                   kategori, biaya, created_at, updated_at
            FROM kegiatan 
            WHERE status IN ('Direncanakan', 'Berlangsung')
            ORDER BY tanggal_mulai ASC
        """)
        result = cursor.fetchall()
        
        for kegiatan in result:
            if kegiatan.get('tanggal_mulai'):  # type: ignore
                kegiatan['tanggal_mulai'] = kegiatan['tanggal_mulai'].strftime('%Y-%m-%d')  # type: ignore
            if kegiatan.get('tanggal_selesai'):  # type: ignore
                kegiatan['tanggal_selesai'] = kegiatan['tanggal_selesai'].strftime('%Y-%m-%d')  # type: ignore
            if kegiatan.get('created_at'):  # type: ignore
                kegiatan['created_at'] = kegiatan['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if kegiatan.get('updated_at'):  # type: ignore
                kegiatan['updated_at'] = kegiatan['updated_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if kegiatan.get('biaya'):  # type: ignore
                kegiatan['biaya'] = float(kegiatan['biaya'])  # type: ignore
        
        return jsonify({
            'status': 'success',
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        connection.close()

@broadcast_bp.route('/keuangan', methods=['GET'])
def get_broadcast_keuangan():
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_keuangan, tanggal, kategori, sub_kategori, deskripsi, 
                   jumlah, metode_pembayaran, penanggung_jawab, created_at, updated_at
            FROM keuangan 
            ORDER BY tanggal DESC
            LIMIT 100
        """)
        result = cursor.fetchall()
        
        for keuangan in result:
            if keuangan.get('tanggal'):  # type: ignore
                keuangan['tanggal'] = keuangan['tanggal'].strftime('%Y-%m-%d')  # type: ignore
            if keuangan.get('created_at'):  # type: ignore
                keuangan['created_at'] = keuangan['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if keuangan.get('updated_at'):  # type: ignore
                keuangan['updated_at'] = keuangan['updated_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if keuangan.get('jumlah'):  # type: ignore
                keuangan['jumlah'] = float(keuangan['jumlah'])  # type: ignore
        
        return jsonify({
            'status': 'success',
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        connection.close()

@broadcast_bp.route('/dokumen', methods=['GET'])
def get_broadcast_dokumen():
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_dokumen, nama_dokumen, file_path, ukuran_file,
                   tipe_file, jenis_dokumen, kategori, keterangan,
                   uploaded_by_admin, uploaded_by_pengguna, uploaded_by_name,
                   created_at, updated_at
            FROM dokumen
            ORDER BY created_at DESC
        """)
        result = cursor.fetchall()
        
        for dokumen in result:
            if dokumen.get('created_at'):  # type: ignore
                dokumen['created_at'] = dokumen['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if dokumen.get('updated_at'):  # type: ignore
                dokumen['updated_at'] = dokumen['updated_at'].strftime('%Y-%m-%d %H:%M:%S')  # type: ignore
            if dokumen.get('ukuran_file'):  # type: ignore
                dokumen['ukuran_file'] = int(dokumen['ukuran_file'])  # type: ignore
        
        return jsonify({
            'status': 'success',
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        connection.close()