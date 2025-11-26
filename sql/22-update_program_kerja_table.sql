-- =====================================================
-- SCRIPT: Update tabel program_kerja
-- PERUBAHAN:
-- 1. Rename kolom 'tanggal' menjadi 'estimasi_waktu' (bulan)
-- 2. Hapus kolom 'waktu'
-- 3. Hapus kolom 'lokasi'
-- 4. Hapus kolom 'status'
-- =====================================================

-- Rename tanggal column to estimasi_waktu and change type to VARCHAR for months
ALTER TABLE program_kerja
  CHANGE COLUMN tanggal estimasi_waktu VARCHAR(20) DEFAULT '';

-- Drop waktu column
ALTER TABLE program_kerja
  DROP COLUMN IF EXISTS waktu;

-- Drop lokasi column
ALTER TABLE program_kerja
  DROP COLUMN IF EXISTS lokasi;

-- Drop status column
ALTER TABLE program_kerja
  DROP COLUMN IF EXISTS status;

-- Update indexes after column changes
ALTER TABLE program_kerja
  DROP INDEX IF EXISTS idx_tanggal;

ALTER TABLE program_kerja
  ADD INDEX idx_estimasi_waktu (estimasi_waktu);

-- Verify structure
SELECT 'Tabel program_kerja berhasil diupdate' as status;

-- Show updated table structure
DESCRIBE program_kerja;
