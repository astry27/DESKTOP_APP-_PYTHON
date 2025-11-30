-- Migration 54: Cleanup Dokumen Table - Remove Obsolete Columns
-- Date: 2025-11-26
-- Purpose: Remove columns that are no longer needed or have been consolidated
-- Changes: Drop redundant and obsolete columns from dokumen table

-- Verify columns exist before dropping them
-- This uses safe DROP COLUMN IF EXISTS syntax to prevent errors

ALTER TABLE dokumen
DROP COLUMN IF EXISTS ukuran_file,
DROP COLUMN IF EXISTS tipe_file,
DROP COLUMN IF EXISTS jenis_dokumen,
DROP COLUMN IF EXISTS keterangan_lengkap,
DROP COLUMN IF EXISTS uploaded_by_pengguna,
DROP COLUMN IF EXISTS uploaded_by_name,
DROP COLUMN IF EXISTS jenis_dokumen_old;

-- Verify the remaining table structure
-- Expected columns after cleanup:
-- id_dokumen, nama_dokumen, file_path, keterangan, kategori_file,
-- upload_date, uploaded_by_admin, created_at, updated_at, bentuk_dokumen

-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'dokumen'
-- ORDER BY ORDINAL_POSITION;
