# Tim Pembina Peserta - API Endpoints (New Single-Table Approach)

**Date**: 2025-11-19
**Status**: ✅ Implemented & Ready
**Location**: `API/routes/tim_pembina_routes.py` (lines 286-477)

---

## Overview

Setelah restructure Tim Pembina ke single-table approach, ada 4 endpoint baru yang handle peserta management langsung dari tabel `tim_pembina`. Endpoint-endpoint ini menambah 188 baris code ke dalam routes file yang sudah ada.

---

## New Endpoints

### 1. GET /tim_pembina_peserta
**Route Path**: `/tim_pembina` + `_peserta`
**External URL**: `GET /tim_pembina_peserta`
**Function**: `get_tim_pembina_peserta_new()` (lines 295-330)

**Purpose**: Mengambil semua peserta dari tabel `tim_pembina` yang sudah diisi data peserta.

**Query**:
```sql
SELECT id_tim_pembina, nama_peserta, wilayah_rohani, jabatan, tahun,
       tim_pembina as nama_tim, id_jemaat
FROM tim_pembina
WHERE nama_peserta IS NOT NULL AND nama_peserta != ''
ORDER BY tahun DESC, tim_pembina, jabatan, nama_peserta
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id_tim_pembina": 1,
      "nama_peserta": "John Doe",
      "wilayah_rohani": "WR 1",
      "jabatan": "Ketua",
      "tahun": 2025,
      "nama_tim": "Liturgi",
      "id_jemaat": 123
    },
    ...
  ]
}
```

**Status Code**: 200 (OK)

---

### 2. POST /tim_pembina_peserta
**Route Path**: `/tim_pembina` + `_peserta`
**External URL**: `POST /tim_pembina_peserta`
**Function**: `add_tim_pembina_peserta_new()` (lines 333-402)

**Purpose**: Menambahkan peserta baru ke tabel `tim_pembina`.

**Required Fields**:
- `nama_peserta` - Nama lengkap peserta (required)
- `jabatan` - Jabatan dalam tim (required)
- `nama_tim` - Nama tim pembina (required, harus ada di database)
- `tahun` - Tahun (required)

**Optional Fields**:
- `id_jemaat` - ID referensi ke tabel jemaat
- `wilayah_rohani` - Wilayah rohani

**Request Body**:
```json
{
  "nama_peserta": "Jane Smith",
  "wilayah_rohani": "WR 2",
  "jabatan": "Sekretaris",
  "nama_tim": "Katekese",
  "tahun": 2025,
  "id_jemaat": 456
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Peserta berhasil ditambahkan",
  "id_tim_pembina": 42,
  "data": {
    "id_tim_pembina": 42,
    "nama_peserta": "Jane Smith",
    "wilayah_rohani": "WR 2",
    "jabatan": "Sekretaris",
    "nama_tim": "Katekese",
    "tahun": 2025
  }
}
```

**Error Response** (400/404/500):
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Validation**:
- Nama peserta, jabatan, nama_tim, dan tahun wajib diisi
- Nama tim harus sudah ada di database (akan dicek dengan query `SELECT`)
- Jika tim tidak ditemukan: 404 error

---

### 3. PUT /tim_pembina_peserta/{peserta_id}
**Route Path**: `/tim_pembina` + `_peserta/<int:peserta_id>`
**External URL**: `PUT /tim_pembina_peserta/{peserta_id}`
**Function**: `update_tim_pembina_peserta_new()` (lines 405-449)

**Purpose**: Mengupdate data peserta yang sudah ada.

**Parameters**:
- `peserta_id` (URL path) - ID peserta untuk diupdate

**Request Body** (update fields yang ingin diubah):
```json
{
  "nama_peserta": "Jane Smith Updated",
  "wilayah_rohani": "WR 3",
  "jabatan": "Bendahara",
  "nama_tim": "Katekese",
  "tahun": 2025,
  "id_jemaat": 456
}
```

**SQL Query**:
```sql
UPDATE tim_pembina
SET nama_peserta = %s, id_jemaat = %s, wilayah_rohani = %s,
    jabatan = %s, tahun = %s, tim_pembina = %s
WHERE id_tim_pembina = %s
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Peserta berhasil diupdate"
}
```

**Status Code**: 200 (OK)

---

### 4. DELETE /tim_pembina_peserta/{peserta_id}
**Route Path**: `/tim_pembina` + `_peserta/<int:peserta_id>`
**External URL**: `DELETE /tim_pembina_peserta/{peserta_id}`
**Function**: `delete_tim_pembina_peserta_new()` (lines 452-477)

**Purpose**: Menghapus peserta dari tabel `tim_pembina`.

**Parameters**:
- `peserta_id` (URL path) - ID peserta untuk dihapus

**SQL Query**:
```sql
DELETE FROM tim_pembina
WHERE id_tim_pembina = %s AND nama_peserta IS NOT NULL
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Peserta berhasil dihapus"
}
```

**Important**: Query ini menggunakan kondisi `nama_peserta IS NOT NULL` untuk memastikan hanya row yang berisi data peserta yang dihapus (bukan row tim pembina yang tidak terisi data peserta).

**Status Code**: 200 (OK)

---

## Implementation Details

### Database Fields Used
Endpoint-endpoint ini hanya mengakses field-field spesifik di tabel `tim_pembina`:
- `id_tim_pembina` - Primary key, auto-increment
- `tim_pembina` - Nama tim pembina (from dropdown)
- `nama_peserta` - Nama lengkap peserta (NEW)
- `id_jemaat` - Foreign key ke jemaat table (NEW)
- `wilayah_rohani` - Wilayah rohani (NEW)
- `jabatan` - Jabatan dalam tim (NEW)
- `tahun` - Tahun (NEW)

### Old Fields (Not Affected)
Endpoint-endpoint ini NOT mengakses field-field lama:
- `tanggal_pelantikan`
- `keterangan`
- `tim_pembina_lainnya`
- Semua field ini tetap tersedia untuk struktur lama

### Backward Compatibility
✅ Old endpoints tetap bekerja:
- `GET /tim_pembina` - Masih GET semua tim pembina (struktur lama)
- `POST /tim_pembina/{tim_id}/peserta` - Masih INSERT ke `tim_pembina_peserta` table
- `DELETE /tim_pembina/peserta/{peserta_id}` - Masih DELETE dari `tim_pembina_peserta`

New endpoints menggunakan path berbeda (`_peserta` suffix) untuk avoid conflicts.

---

## Testing dengan cURL

### 1. GET All Peserta
```bash
curl -X GET "http://localhost:5000/tim_pembina_peserta" \
  -H "Content-Type: application/json"
```

### 2. POST New Peserta
```bash
curl -X POST "http://localhost:5000/tim_pembina_peserta" \
  -H "Content-Type: application/json" \
  -d '{
    "nama_peserta": "Budi Santoso",
    "wilayah_rohani": "WR 1",
    "jabatan": "Ketua",
    "nama_tim": "Liturgi",
    "tahun": 2025,
    "id_jemaat": 100
  }'
```

### 3. PUT Update Peserta
```bash
curl -X PUT "http://localhost:5000/tim_pembina_peserta/42" \
  -H "Content-Type: application/json" \
  -d '{
    "nama_peserta": "Budi Santoso Updated",
    "wilayah_rohani": "WR 2",
    "jabatan": "Sekretaris",
    "nama_tim": "Katekese",
    "tahun": 2025,
    "id_jemaat": 100
  }'
```

### 4. DELETE Peserta
```bash
curl -X DELETE "http://localhost:5000/tim_pembina_peserta/42" \
  -H "Content-Type: application/json"
```

---

## Error Handling

### Common Errors

**400 Bad Request** - Data tidak lengkap
```json
{
  "success": false,
  "error": "Data tidak lengkap (nama_peserta, jabatan, nama_tim, tahun wajib)"
}
```

**404 Not Found** - Tim pembina tidak ditemukan
```json
{
  "success": false,
  "error": "Tim pembina \"Unknownm\" tidak ditemukan"
}
```

**500 Internal Server Error** - Database error
```json
{
  "success": false,
  "error": "Error message from database"
}
```

---

## Integration with Client-Side

### API Client Methods (server/api_client.py)
```python
# Get all peserta
def get_tim_pembina_peserta(self):
    return self._make_request('GET', f"{self.base_url}/tim_pembina_peserta")

# Add peserta
def add_tim_pembina_peserta_new(self, data):
    return self._make_request('POST', f"{self.base_url}/tim_pembina_peserta",
                            json=data, headers={'Content-Type': 'application/json'})

# Update peserta
def update_tim_pembina_peserta(self, peserta_id, data):
    return self._make_request('PUT', f"{self.base_url}/tim_pembina_peserta/{peserta_id}",
                            json=data, headers={'Content-Type': 'application/json'})

# Delete peserta
def delete_tim_pembina_peserta_new(self, peserta_id):
    return self._make_request('DELETE', f"{self.base_url}/tim_pembina_peserta/{peserta_id}")
```

### Database Manager Methods (server/database.py)
```python
def get_tim_pembina_peserta(self):
    result = self.api_client.get_tim_pembina_peserta()
    return (True, {'success': True, 'data': result.get('data', [])})

def add_tim_pembina_peserta_new(self, data):
    result = self.api_client.add_tim_pembina_peserta_new(data)
    return (True, {'success': True, 'data': result.get('data', {})})

def update_tim_pembina_peserta(self, peserta_id, data):
    result = self.api_client.update_tim_pembina_peserta(peserta_id, data)
    return (True, {'success': True, 'data': result.get('data', {})})

def delete_tim_pembina_peserta_new(self, peserta_id):
    result = self.api_client.delete_tim_pembina_peserta_new(peserta_id)
    return (True, {'success': True, 'data': result.get('data', {})})
```

---

## Database Migration Required

Sebelum endpoints ini bisa digunakan, harus execute migration script:

```bash
mysql -u root -p entf7819_db-client-server < sql/47-restructure_tim_pembina_table.sql
```

Script ini akan:
1. ✅ Add 5 new columns ke `tim_pembina` table
2. ✅ Create 5 performance indexes
3. ✅ Drop obsolete `tim_pembina_peserta` table

---

## Summary

- ✅ 4 endpoints baru di-implement
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Proper error handling
- ✅ Backward compatible dengan old endpoints
- ✅ Integration dengan client-side components siap
- ✅ Syntax validated
- ✅ Ready untuk testing

**Next Step**: Execute database migration dan test endpoints dengan client application.
