# Client Dokumen Component - UI Table Update

## Perubahan yang Dilakukan

### Tanggal: 2024
### File: `client/components/dokumen_component.py`

---

## Daftar Perubahan

### 1. **Struktur Kolom Table (Line 124-146)**

#### SEBELUM:
```python
setHorizontalHeaderLabels([
    "Nama Dokumen",      # [0]
    "Jenis Dokumen",     # [1]
    "Keterangan",        # [2]
    "Ukuran",            # [3]
    "Tipe File",         # [4]
    "Upload By",         # [5]
    "Tanggal Upload",    # [6]
])
```

#### SESUDAH:
```python
setHorizontalHeaderLabels([
    "Nama Dokumen",      # [0]
    "Kategori",          # [1] (diubah dari "Jenis Dokumen")
    "Bentuk",            # [2] (baru, kolom tambahan)
    "Ukuran",            # [3]
    "Keterangan",        # [4] (dipindahkan dari posisi [2])
    "Upload By",         # [5]
    "Tanggal Upload",    # [6]
])
```

#### Column Width Update:
```python
# SEBELUM:
setColumnWidth(0, 220)  # Nama Dokumen
setColumnWidth(1, 140)  # Jenis Dokumen
setColumnWidth(2, 240)  # Keterangan
setColumnWidth(3, 110)  # Ukuran
setColumnWidth(4, 120)  # Tipe File
setColumnWidth(5, 160)  # Upload By
setColumnWidth(6, 150)  # Tanggal Upload

# SESUDAH:
setColumnWidth(0, 200)  # Nama Dokumen
setColumnWidth(1, 140)  # Kategori
setColumnWidth(2, 140)  # Bentuk
setColumnWidth(3, 100)  # Ukuran
setColumnWidth(4, 150)  # Keterangan
setColumnWidth(5, 120)  # Upload By
setColumnWidth(6, 140)  # Tanggal Upload
```

---

### 2. **Data Mapping dalam on_files_loaded() (Line 189-227)**

#### SEBELUM:
```python
document_name = self._resolve_document_name(file_info)
jenis_dokumen = self._resolve_document_category(file_info)
description_text, description_tooltip = self._resolve_description(file_info)
size_display = self._format_file_size(file_info)
type_display, raw_type = self._resolve_file_type(file_info)
uploader = self._resolve_uploader(file_info)
upload_date = self._resolve_upload_date(file_info)

# Column mapping:
# [0] Nama Dokumen → document_name
# [1] Jenis Dokumen → jenis_dokumen
# [2] Keterangan → description_text
# [3] Ukuran → size_display
# [4] Tipe File → type_display
# [5] Upload By → uploader
# [6] Tanggal Upload → upload_date
```

#### SESUDAH:
```python
document_name = self._resolve_document_name(file_info)
kategori_dokumen = self._resolve_document_category(file_info)
bentuk_dokumen = self._resolve_bentuk_dokumen(file_info)  # NEW
size_display = self._format_file_size(file_info)
description_text, description_tooltip = self._resolve_description(file_info)
uploader = self._resolve_uploader(file_info)
upload_date = self._resolve_upload_date(file_info)

# Column mapping:
# [0] Nama Dokumen → document_name
# [1] Kategori → kategori_dokumen
# [2] Bentuk → bentuk_dokumen (NEW)
# [3] Ukuran → size_display
# [4] Keterangan → description_text (MOVED)
# [5] Upload By → uploader
# [6] Tanggal Upload → upload_date
```

---

### 3. **Penambahan Helper Method (Line 353-362)**

Menambahkan method baru untuk resolve bentuk dokumen:

```python
def _resolve_bentuk_dokumen(self, file_info):
    """Resolve bentuk dokumen dari berbagai kemungkinan field names"""
    bentuk_keys = [
        'bentuk_dokumen', 'bentuk', 'form', 'document_form',
        'kategori_file'
    ]
    for key in bentuk_keys:
        value = file_info.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "-"
```

---

### 4. **Update _resolve_document_category() (Line 342-351)**

Menambahkan 'kategori_file' ke dalam priority keys:

```python
# SEBELUM:
category_keys = [
    'jenis_dokumen', 'document_type', 'kategori', 'category',
    'type', 'doc_type', 'document_category'
]

# SESUDAH:
category_keys = [
    'kategori_file', 'jenis_dokumen', 'document_type', 'kategori', 'category',
    'type', 'doc_type', 'document_category'
]
```

---

## Alignment dengan Server

Struktur kolom sekarang **sesuai persis dengan server** `server/components/dokumen.py`:

### Server Columns (dengan Aksi):
1. Nama Dokumen
2. Kategori
3. Bentuk
4. Ukuran
5. Keterangan
6. Upload By
7. Tanggal Upload
8. **Aksi** (hanya server)

### Client Columns (tanpa Aksi):
1. Nama Dokumen
2. Kategori
3. Bentuk
4. Ukuran
5. Keterangan
6. Upload By
7. Tanggal Upload

---

## Field Mapping untuk API Response

Client sekarang siap menerima field dari server:

| No | Column | API Field Names (Priority) |
|---|---|---|
| 1 | Nama Dokumen | nama_dokumen, document_name, name, file_name, filename, original_name, path |
| 2 | Kategori | kategori_file, jenis_dokumen, document_type, kategori, category, type |
| 3 | Bentuk | bentuk_dokumen, bentuk, form, document_form, kategori_file |
| 4 | Ukuran | ukuran_file, file_size, size |
| 5 | Keterangan | keterangan, description, deskripsi, notes, remark, catatan |
| 6 | Upload By | uploaded_by_name, uploaded_by, uploader, user_name |
| 7 | Tanggal Upload | tanggal_upload, upload_date, created_at, date_uploaded |

---

## Testing Checklist

- [ ] Tabel menampilkan 7 kolom dengan urutan yang benar
- [ ] Kolom widths sesuai (200, 140, 140, 100, 150, 120, 140)
- [ ] Data dimapping ke kolom yang benar
- [ ] Header terlihat jelas
- [ ] Data dari API ditampilkan dengan benar di setiap kolom
- [ ] Fungsi Download dan Refresh masih bekerja
- [ ] Tidak ada perubahan pada logic CRUD, hanya UI/display

---

## Notes

- Kolom "Tipe File" dihapus karena sudah tercakup dalam kolom "Bentuk"
- Kolom "Aksi" tidak ditambahkan di client (sesuai requirement)
- Helper method `_resolve_file_type()` tidak digunakan lagi
- Perubahan ini HANYA affect tampilan tabel, tidak ada perubahan pada API communication atau CRUD logic
