-- Migration 58: Verify and fix program_kerja_wr table structure
-- Purpose: Ensure table has correct columns and no unnecessary fields

-- Verify table structure
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'program_kerja_wr'
ORDER BY ORDINAL_POSITION;

-- Expected columns:
-- id_program_kerja_wr (PRIMARY KEY)
-- kategori (VARCHAR)
-- estimasi_waktu (VARCHAR) - nama bulan
-- judul (VARCHAR)
-- sasaran (TEXT)
-- penanggung_jawab (VARCHAR)
-- anggaran (DECIMAL)
-- sumber_anggaran (VARCHAR)
-- keterangan (TEXT)
-- reported_by (INT) - foreign key to pengguna.id_pengguna
-- status (ENUM or VARCHAR)
-- created_at (TIMESTAMP)
-- updated_at (TIMESTAMP)

-- Note: wilayah_rohani_id should NOT exist (removed in migration 57)
