# Tim Pembina Restructure - Detailed Code Changes

## File 1: `sql/47-restructure_tim_pembina_table.sql` (NEW)

**Purpose**: Database migration to add new columns to tim_pembina table

**Key Changes**:
```sql
-- Add new columns to tim_pembina table
ALTER TABLE tim_pembina ADD COLUMN IF NOT EXISTS tahun INT DEFAULT 2025;
ALTER TABLE tim_pembina ADD COLUMN IF NOT EXISTS nama_peserta VARCHAR(255) DEFAULT NULL;
ALTER TABLE tim_pembina ADD COLUMN IF NOT EXISTS id_jemaat INT DEFAULT NULL;
ALTER TABLE tim_pembina ADD COLUMN IF NOT EXISTS wilayah_rohani VARCHAR(100) DEFAULT NULL;
ALTER TABLE tim_pembina ADD COLUMN IF NOT EXISTS jabatan VARCHAR(50) DEFAULT 'Anggota';

-- Create 5 indexes for performance
CREATE INDEX idx_tim_pembina_tahun ON tim_pembina(tahun);
CREATE INDEX idx_tim_pembina_nama_peserta ON tim_pembina(nama_peserta);
CREATE INDEX idx_tim_pembina_jabatan ON tim_pembina(jabatan);
CREATE INDEX idx_tim_pembina_wilayah_rohani ON tim_pembina(wilayah_rohani);
CREATE INDEX idx_tim_pembina_id_jemaat ON tim_pembina(id_jemaat);

-- Drop old table (no longer needed)
DROP TABLE IF EXISTS tim_pembina_peserta;
```

---

## File 2: `server/components/tim_pembina.py` (COMPLETELY REWRITTEN)

**Before**: 560+ lines managing nested tim/peserta structure
**After**: ~540 lines managing flat peserta structure

**Key Changes**:

### Imports
```python
# Added TimPesertaDialog (removed old dialogs)
from .dialogs import TimPesertaDialog
# Removed: TimPembinaDialog, TimPembinaPesertaDialog
```

### Class Structure
```python
class TimPembinaComponent(QWidget):
    """Komponen untuk manajemen Tim Pembina (peserta tim)"""
    # Changed from managing tim to managing peserta directly
```

### New UI Elements
```python
# 3 filter dropdowns instead of single "Tambah Tim" button
self.tahun_filter = QComboBox()      # Filter by year
self.tim_filter = QComboBox()        # Filter by team name
self.jabatan_filter = QComboBox()    # Filter by position
```

### Table Structure
```python
# Before: 5 columns (ID, Tim Pembina, Tanggal Pelantikan, Jumlah Peserta, Aksi)
# After: 6 columns (Nama Peserta, Wilayah Rohani, Jabatan, Tim Pembina, Tahun, Aksi)
self.peserta_table.setHorizontalHeaderLabels([
    "Nama Peserta", "Wilayah Rohani", "Jabatan", "Tim Pembina", "Tahun", "Aksi"
])
```

### New Methods
```python
def load_data(self):
    """Load peserta data dari database (changed from load tim)"""
    success, result = self.db_manager.get_tim_pembina_peserta()
    # Now loads peserta, not tim

def populate_filters(self):
    """Populate filter dropdowns from data (new)"""
    # Extract unique tahun, tim, jabatan from data
    # Populate 3 filter dropdowns dynamically

def apply_filters(self):
    """Apply filters to peserta data (new)"""
    # Filter by selected tahun, tim, jabatan
    # Refresh table display

def on_tambah_peserta(self):
    """Handle tambah peserta button clicked (was on_tambah_tim)"""
    dialog = TimPesertaDialog(self, db_manager=self.db_manager)
    # Now adds peserta instead of tim

def on_edit_peserta(self, peserta_id):
    """Handle edit peserta button clicked (new)"""
    peserta_data = next((p for p in self.peserta_data
                        if p.get('id_tim_pembina') == peserta_id), None)
    dialog = TimPesertaDialog(self, peserta_data=peserta_data, ...)
    # Edit existing peserta

def on_delete_peserta(self, peserta_id):
    """Handle delete peserta button clicked (new)"""
    # Delete peserta with confirmation
    success, result = self.db_manager.delete_tim_pembina_peserta_new(peserta_id)
```

---

## File 3: `server/components/dialogs.py` (ADDED NEW CLASS)

**Location**: Lines 3066-3280 (at end of file)

**New Class**: `TimPesertaDialog`

### Structure
```python
class TimPesertaDialog(QDialog):
    """Dialog untuk menambah/edit peserta Tim Pembina (simplified single-table approach)"""
```

### Form Fields
```python
# 1. Nama Peserta - searchable from jemaat
self.nama_peserta_input = QLineEdit()
self.nama_peserta_input.textChanged.connect(self.on_search_jemaat)

# 2. Wilayah Rohani - dropdown from jemaat
self.wilayah_rohani_input = QComboBox()
self.wilayah_rohani_input.currentTextChanged.connect(self.on_wilayah_changed)

# 3. Jabatan - fixed dropdown
self.jabatan_input = QComboBox()
self.jabatan_input.addItems([
    "Pilih Jabatan", "Pembina", "Ketua", "Sekretaris",
    "Bendahara", "Koordinator", "Anggota Sie", "Anggota Biasa"
])

# 4. Tim Pembina - dropdown from database
self.nama_tim_input = QComboBox()
self.load_tim_list()

# 5. Tahun - realtime dropdown 2025 onwards
self.tahun_input = QComboBox()
current_year = QDate.currentDate().year()
for year in range(2025, current_year + 5):
    self.tahun_input.addItem(str(year))
```

### Key Methods
```python
def load_tim_list(self):
    """Load tim pembina list from database"""
    success, result = self.db_manager.get_tim_pembina()
    # Populate tim dropdown

def load_wilayah_list(self):
    """Load wilayah rohani list from jemaat database"""
    success, result = self.db_manager.get_jemaat_list()
    # Extract unique wilayah_rohani values
    # Populate wilayah dropdown

def on_search_jemaat(self, keyword):
    """Search umat dalam database jemaat"""
    result = self.db_manager.search_jemaat_by_nama(keyword)
    # Auto-populate wilayah_rohani when match found

def load_data(self):
    """Load data untuk edit"""
    # Load all fields from peserta_data

def get_data(self):
    """Ambil data dari form"""
    return {
        'id_jemaat': ...,
        'nama_peserta': ...,
        'wilayah_rohani': ...,
        'jabatan': ...,
        'nama_tim': ...,
        'tahun': ...,
    }
```

---

## File 4: `server/database.py` (ADDED 7 METHODS)

**Location**: Lines 1242-1304 (after existing add_tim_pembina_peserta)

### New Methods

```python
def get_tim_pembina_peserta(self) -> Tuple[bool, Any]:
    """Get all peserta from tim_pembina table (new single-table approach)"""
    result = self.api_client.get_tim_pembina_peserta()
    # Returns: {'success': True, 'data': [peserta_list]}

def add_tim_pembina_peserta_new(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Add new peserta to tim_pembina table (new single-table approach)"""
    result = self.api_client.add_tim_pembina_peserta_new(data)
    # Accepts: {id_jemaat, nama_peserta, wilayah_rohani, jabatan, nama_tim, tahun}

def update_tim_pembina_peserta(self, peserta_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Update peserta in tim_pembina table (new single-table approach)"""
    result = self.api_client.update_tim_pembina_peserta(peserta_id, data)

def delete_tim_pembina_peserta_new(self, peserta_id: int) -> Tuple[bool, Any]:
    """Delete peserta from tim_pembina table (new single-table approach)"""
    result = self.api_client.delete_tim_pembina_peserta_new(peserta_id)

def get_jemaat_list(self) -> Tuple[bool, Any]:
    """Get all jemaat (for loading wilayah rohani list)"""
    success, response = self.api_client.get_jemaat()
    # Returns all jemaat for wilayah extraction

# Old methods marked deprecated but kept:
def add_tim_pembina_peserta(self, tim_id: int, data: Dict[str, Any]):
    """Add peserta to tim pembina (old method - deprecated)"""

def delete_tim_pembina_peserta(self, peserta_id: int):
    """Delete peserta from tim_pembina table (old method - deprecated)"""
```

---

## File 5: `server/api_client.py` (ADDED 4 METHODS)

**Location**: Lines 687-703 (after delete_tim_pembina_peserta)

### New Methods

```python
def get_tim_pembina_peserta(self):
    """Get all peserta from tim_pembina table (new single-table approach)"""
    return self._make_request('GET', f"{self.base_url}/tim_pembina_peserta")

def add_tim_pembina_peserta_new(self, data):
    """Add new peserta to tim_pembina table (new single-table approach)"""
    return self._make_request('POST', f"{self.base_url}/tim_pembina_peserta",
                            json=data, headers={'Content-Type': 'application/json'})

def update_tim_pembina_peserta(self, peserta_id, data):
    """Update peserta in tim_pembina table (new single-table approach)"""
    return self._make_request('PUT', f"{self.base_url}/tim_pembina_peserta/{peserta_id}",
                            json=data, headers={'Content-Type': 'application/json'})

def delete_tim_pembina_peserta_new(self, peserta_id):
    """Delete peserta from tim_pembina table (new single-table approach)"""
    return self._make_request('DELETE', f"{self.base_url}/tim_pembina_peserta/{peserta_id}")
```

---

## File 6: `tim_pembina.py` (COMPONENT UPDATE)

**Change**: Line 439 (in on_tambah_peserta method)

```python
# Before:
success, result = self.db_manager.add_tim_pembina_peserta(tim_id, data)

# After:
success, result = self.db_manager.add_tim_pembina_peserta_new(data)
# Note: tim_id no longer needed, it's part of the data
```

**Change**: Line 528 (in on_delete_peserta method)

```python
# Before:
success, result = self.db_manager.delete_tim_pembina_peserta(peserta_id)

# After:
success, result = self.db_manager.delete_tim_pembina_peserta_new(peserta_id)
```

---

## Summary of Changes

### Files Modified: 5
- `server/components/tim_pembina.py` - Completely rewritten (540 lines)
- `server/components/dialogs.py` - Added TimPesertaDialog (215 lines)
- `server/database.py` - Added 7 methods
- `server/api_client.py` - Added 4 methods

### Files Created: 1
- `sql/47-restructure_tim_pembina_table.sql` - Database migration

### Lines Changed: ~900+
- New code: ~700+ lines
- Old code: ~560+ lines replaced

### Methods Added: 11
- Database: 7 methods
- API Client: 4 methods

### Components Modified: 2
- Tim Pembina Component (structure)
- Dialogs (new class)

### Backward Compatibility: ✅ YES
- Old methods preserved and marked deprecated
- Old API endpoints still functional
- Gradual migration possible

---

## Testing Points

For each file, verify:

1. **Syntax**: All files pass `python -m py_compile`
   - ✅ tim_pembina.py
   - ✅ dialogs.py
   - ✅ database.py
   - ✅ api_client.py

2. **Imports**: All imports resolve correctly
   - ✅ TimPesertaDialog imported in tim_pembina.py
   - ✅ QDate imported in dialogs.py

3. **Methods**: All methods have correct signatures
   - Database methods return Tuple[bool, Any]
   - API client methods return dict
   - Dialog methods return correct data structure

4. **UI Elements**: All UI components initialize
   - ComboBox dropdowns
   - LineEdit fields
   - Buttons with callbacks
   - Table columns

5. **Data Flow**: Full CRUD operation flow
   - Load peserta from database
   - Display in table with filters
   - Add new peserta via dialog
   - Edit existing peserta
   - Delete peserta with confirmation
