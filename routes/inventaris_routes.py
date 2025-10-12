# Path: routes/inventaris_routes.py

from flask import Blueprint, jsonify, request
from config import get_db_connection
import datetime
import os

inventaris_bp = Blueprint('inventaris', __name__, url_prefix='/inventaris')

API_STATUS_FILE = 'api_status.txt'

def get_api_status():
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
    if not get_api_status():
        return jsonify({
            'status': 'error', 
            'message': 'API sedang dinonaktifkan'
        }), 503
    return None

@inventaris_bp.route('', methods=['GET'])
def get_inventaris():
    """Ambil semua data inventaris"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        limit = request.args.get('limit', 1000, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '')
        kategori = request.args.get('kategori', '')
        kondisi = request.args.get('kondisi', '')
        lokasi = request.args.get('lokasi', '')
        
        cursor = connection.cursor(dictionary=True)
        
        # Build query dengan filter
        base_query = "SELECT * FROM inventaris WHERE 1=1"
        params = []
        
        if search:
            base_query += """ AND (
                kode_barang LIKE %s OR 
                nama_barang LIKE %s OR 
                merk LIKE %s OR
                supplier LIKE %s OR
                penanggung_jawab LIKE %s OR
                lokasi LIKE %s
            )"""
            search_param = f'%{search}%'
            params.extend([search_param] * 6)
        
        if kategori:
            base_query += " AND kategori = %s"
            params.append(kategori)
            
        if kondisi:
            base_query += " AND kondisi = %s"
            params.append(kondisi)
            
        if lokasi:
            base_query += " AND lokasi = %s"
            params.append(lokasi)
        
        base_query += " ORDER BY nama_barang ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        inventaris_list = cursor.fetchall()
        
        # Get total count untuk pagination
        count_query = "SELECT COUNT(*) as total FROM inventaris WHERE 1=1"
        count_params = []
        
        if search:
            count_query += """ AND (
                kode_barang LIKE %s OR 
                nama_barang LIKE %s OR 
                merk LIKE %s OR
                supplier LIKE %s OR
                penanggung_jawab LIKE %s OR
                lokasi LIKE %s
            )"""
            count_params.extend([search_param] * 6)
            
        if kategori:
            count_query += " AND kategori = %s"
            count_params.append(kategori)
            
        if kondisi:
            count_query += " AND kondisi = %s"
            count_params.append(kondisi)
            
        if lokasi:
            count_query += " AND lokasi = %s"
            count_params.append(lokasi)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        # Convert dates dan decimals untuk JSON serialization
        for item in inventaris_list:
            if item.get('tanggal_beli'):
                item['tanggal_beli'] = item['tanggal_beli'].isoformat()
            if item.get('harga_satuan'):
                item['harga_satuan'] = float(item['harga_satuan'])
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'data': inventaris_list,
            'total': total,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        print(f"Error getting inventaris: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('', methods=['POST'])
def add_inventaris():
    """Tambah data inventaris baru"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        data = request.get_json()
        
        # Validasi required fields
        required_fields = ['kode_barang', 'nama_barang']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error', 
                    'message': f'Field {field} diperlukan'
                }), 400
        
        cursor = connection.cursor()
        
        # Check if kode_barang sudah ada
        cursor.execute("SELECT id_inventaris FROM inventaris WHERE kode_barang = %s", (data.get('kode_barang'),))
        if cursor.fetchone():
            return jsonify({
                'status': 'error', 
                'message': 'Kode barang sudah ada'
            }), 400
        
        insert_query = """
        INSERT INTO inventaris (
            kode_barang, nama_barang, kategori, merk, jumlah, satuan,
            harga_satuan, tanggal_beli, supplier, kondisi, lokasi,
            penanggung_jawab, keterangan
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        params = (
            data.get('kode_barang'),
            data.get('nama_barang'),
            data.get('kategori'),
            data.get('merk'),
            data.get('jumlah', 0),
            data.get('satuan'),
            data.get('harga_satuan'),
            data.get('tanggal_beli'),
            data.get('supplier'),
            data.get('kondisi', 'Baik'),
            data.get('lokasi'),
            data.get('penanggung_jawab'),
            data.get('keterangan')
        )
        
        cursor.execute(insert_query, params)
        connection.commit()
        
        inventaris_id = cursor.lastrowid
        
        return jsonify({
            'status': 'success',
            'message': 'Data inventaris berhasil ditambahkan',
            'id': inventaris_id
        })
        
    except Exception as e:
        print(f"Error adding inventaris: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/<int:inventaris_id>', methods=['GET'])
def get_inventaris_by_id(inventaris_id):
    """Ambil data inventaris berdasarkan ID"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventaris WHERE id_inventaris = %s", (inventaris_id,))
        inventaris = cursor.fetchone()
        
        if not inventaris:
            return jsonify({'status': 'error', 'message': 'Data inventaris tidak ditemukan'}), 404
        
        # Convert dates dan decimals
        if inventaris.get('tanggal_beli'):
            inventaris['tanggal_beli'] = inventaris['tanggal_beli'].isoformat()
        if inventaris.get('harga_satuan'):
            inventaris['harga_satuan'] = float(inventaris['harga_satuan'])
        if inventaris.get('created_at'):
            inventaris['created_at'] = inventaris['created_at'].isoformat()
        if inventaris.get('updated_at'):
            inventaris['updated_at'] = inventaris['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'data': inventaris
        })
        
    except Exception as e:
        print(f"Error getting inventaris by ID: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/<int:inventaris_id>', methods=['PUT'])
def update_inventaris(inventaris_id):
    """Update data inventaris"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        data = request.get_json()
        
        cursor = connection.cursor()
        
        # Check if inventaris exists
        cursor.execute("SELECT id_inventaris FROM inventaris WHERE id_inventaris = %s", (inventaris_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Data inventaris tidak ditemukan'}), 404
        
        # Check jika kode_barang diubah, pastikan tidak conflict
        if data.get('kode_barang'):
            cursor.execute(
                "SELECT id_inventaris FROM inventaris WHERE kode_barang = %s AND id_inventaris != %s", 
                (data.get('kode_barang'), inventaris_id)
            )
            if cursor.fetchone():
                return jsonify({
                    'status': 'error', 
                    'message': 'Kode barang sudah ada'
                }), 400
        
        update_query = """
        UPDATE inventaris SET
            kode_barang = %s, nama_barang = %s, kategori = %s, merk = %s,
            jumlah = %s, satuan = %s, harga_satuan = %s, tanggal_beli = %s,
            supplier = %s, kondisi = %s, lokasi = %s, penanggung_jawab = %s,
            keterangan = %s, updated_at = NOW()
        WHERE id_inventaris = %s
        """
        
        params = (
            data.get('kode_barang'),
            data.get('nama_barang'),
            data.get('kategori'),
            data.get('merk'),
            data.get('jumlah', 0),
            data.get('satuan'),
            data.get('harga_satuan'),
            data.get('tanggal_beli'),
            data.get('supplier'),
            data.get('kondisi', 'Baik'),
            data.get('lokasi'),
            data.get('penanggung_jawab'),
            data.get('keterangan'),
            inventaris_id
        )
        
        cursor.execute(update_query, params)
        connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Data inventaris berhasil diupdate'
        })
        
    except Exception as e:
        print(f"Error updating inventaris: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/<int:inventaris_id>', methods=['DELETE'])
def delete_inventaris(inventaris_id):
    """Hapus data inventaris"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if inventaris exists
        cursor.execute("SELECT nama_barang FROM inventaris WHERE id_inventaris = %s", (inventaris_id,))
        inventaris = cursor.fetchone()
        if not inventaris:
            return jsonify({'status': 'error', 'message': 'Data inventaris tidak ditemukan'}), 404
        
        cursor.execute("DELETE FROM inventaris WHERE id_inventaris = %s", (inventaris_id,))
        connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Data inventaris {inventaris[0]} berhasil dihapus'
        })
        
    except Exception as e:
        print(f"Error deleting inventaris: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/statistics', methods=['GET'])
def get_inventaris_statistics():
    """Ambil statistik inventaris"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total barang
        cursor.execute("SELECT COUNT(*) as total_barang, SUM(jumlah) as total_unit FROM inventaris")
        total_stats = cursor.fetchone()
        
        # Total nilai inventaris
        cursor.execute("SELECT SUM(jumlah * COALESCE(harga_satuan, 0)) as total_nilai FROM inventaris")
        total_nilai = cursor.fetchone()['total_nilai'] or 0
        
        # Barang per kategori
        cursor.execute("""
            SELECT kategori, COUNT(*) as jumlah_item, SUM(jumlah) as total_unit
            FROM inventaris 
            WHERE kategori IS NOT NULL
            GROUP BY kategori 
            ORDER BY jumlah_item DESC
        """)
        per_kategori = cursor.fetchall()
        
        # Barang per kondisi
        cursor.execute("""
            SELECT kondisi, COUNT(*) as jumlah
            FROM inventaris 
            GROUP BY kondisi 
            ORDER BY jumlah DESC
        """)
        per_kondisi = cursor.fetchall()
        
        # Barang per lokasi
        cursor.execute("""
            SELECT lokasi, COUNT(*) as jumlah
            FROM inventaris 
            WHERE lokasi IS NOT NULL
            GROUP BY lokasi 
            ORDER BY jumlah DESC
            LIMIT 10
        """)
        per_lokasi = cursor.fetchall()
        
        # Barang dengan stok rendah (kurang dari 5)
        cursor.execute("""
            SELECT kode_barang, nama_barang, jumlah, satuan
            FROM inventaris 
            WHERE jumlah < 5
            ORDER BY jumlah ASC
            LIMIT 10
        """)
        stok_rendah = cursor.fetchall()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_barang': total_stats['total_barang'],
                'total_unit': total_stats['total_unit'],
                'total_nilai': float(total_nilai),
                'per_kategori': per_kategori,
                'per_kondisi': per_kondisi,
                'per_lokasi': per_lokasi,
                'stok_rendah': stok_rendah
            }
        })
        
    except Exception as e:
        print(f"Error getting inventaris statistics: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/kategori', methods=['GET'])
def get_inventaris_categories():
    """Ambil daftar kategori inventaris yang ada"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT kategori 
            FROM inventaris 
            WHERE kategori IS NOT NULL AND kategori != ''
            ORDER BY kategori
        """)
        categories = [row[0] for row in cursor.fetchall()]
        
        return jsonify({
            'status': 'success',
            'data': categories
        })
        
    except Exception as e:
        print(f"Error getting inventaris categories: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@inventaris_bp.route('/lokasi', methods=['GET'])
def get_inventaris_locations():
    """Ambil daftar lokasi inventaris yang ada"""
    status_check = check_api_enabled()
    if status_check:
        return status_check
        
    connection = get_db_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT lokasi 
            FROM inventaris 
            WHERE lokasi IS NOT NULL AND lokasi != ''
            ORDER BY lokasi
        """)
        locations = [row[0] for row in cursor.fetchall()]
        
        return jsonify({
            'status': 'success',
            'data': locations
        })
        
    except Exception as e:
        print(f"Error getting inventaris locations: {e}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()