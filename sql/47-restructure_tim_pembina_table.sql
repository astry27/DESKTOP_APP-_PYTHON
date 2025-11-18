-- Migration: Restructure tim_pembina table untuk simplifikasi struktur
-- Purpose: Mengubah tim_pembina menjadi single table dengan peserta inline
-- Date: 2025-11-19
-- Path: sql/47-restructure_tim_pembina_table.sql

-- ========== STEP 1: Add new columns to tim_pembina untuk peserta ==========

ALTER TABLE tim_pembina
ADD COLUMN IF NOT EXISTS tahun INT DEFAULT 2025 AFTER tim_pembina_lainnya,
ADD COLUMN IF NOT EXISTS nama_peserta VARCHAR(255) DEFAULT NULL COMMENT 'Nama lengkap peserta (dari umat)',
ADD COLUMN IF NOT EXISTS id_jemaat INT DEFAULT NULL COMMENT 'ID dari tabel umat' AFTER nama_peserta,
ADD COLUMN IF NOT EXISTS wilayah_rohani VARCHAR(100) DEFAULT NULL AFTER id_jemaat,
ADD COLUMN IF NOT EXISTS jabatan VARCHAR(50) DEFAULT 'Anggota' AFTER wilayah_rohani;

-- ========== STEP 2: Create indexes untuk performance ==========

CREATE INDEX IF NOT EXISTS idx_tim_pembina_tahun ON tim_pembina(tahun);
CREATE INDEX IF NOT EXISTS idx_tim_pembina_nama_peserta ON tim_pembina(nama_peserta);
CREATE INDEX IF NOT EXISTS idx_tim_pembina_jabatan ON tim_pembina(jabatan);
CREATE INDEX IF NOT EXISTS idx_tim_pembina_wilayah_rohani ON tim_pembina(wilayah_rohani);
CREATE INDEX IF NOT EXISTS idx_tim_pembina_id_jemaat ON tim_pembina(id_jemaat);

-- ========== STEP 3: Backup data lama ke tim_pembina_peserta jika diperlukan ==========

-- Data lama sudah tersimpan di tim_pembina_peserta, tidak ada data untuk migrate ke struktur baru

-- ========== STEP 4: Drop old tim_pembina_peserta table (TIDAK DIPAKAI LAGI) ==========

DROP TABLE IF EXISTS tim_pembina_peserta;

-- ========== STEP 5: Normalize existing tim_pembina data ==========

-- Set default tahun untuk records lama
UPDATE tim_pembina SET tahun = 2025 WHERE tahun IS NULL OR tahun = 0;

-- ========== STEP 6: Update column comments ==========

ALTER TABLE tim_pembina MODIFY COLUMN tim_pembina VARCHAR(100) NOT NULL COMMENT 'Nama Tim Pembina (atau Lainnya untuk custom)';
ALTER TABLE tim_pembina MODIFY COLUMN tanggal_pelantikan DATE DEFAULT NULL COMMENT 'Tanggal pelantikan tim';
ALTER TABLE tim_pembina MODIFY COLUMN keterangan TEXT DEFAULT NULL COMMENT 'Keterangan tim atau peserta';

-- ========== STEP 7: Verify final structure ==========

-- SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tim_pembina' ORDER BY ORDINAL_POSITION;
