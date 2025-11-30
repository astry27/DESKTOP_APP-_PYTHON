-- Migration 53: Update Dokumen Table - Complete Structure
-- Date: 2025-11-26
-- Purpose: Update dokumen table structure to support all upload dialog fields
-- Changes: Add missing columns, remove obsolete columns, standardize naming

-- Check existing columns and add missing ones
ALTER TABLE dokumen
ADD COLUMN IF NOT EXISTS bentuk_dokumen VARCHAR(100) COMMENT 'Bentuk/tipe dokumen (Surat, Laporan, dll)' AFTER jenis_dokumen,
ADD COLUMN IF NOT EXISTS kategori_file VARCHAR(100) DEFAULT 'Lainnya' COMMENT 'Kategori/bentuk file dari upload dialog' AFTER bentuk_dokumen,
ADD COLUMN IF NOT EXISTS keterangan_lengkap TEXT COMMENT 'Keterangan panjang dari user' AFTER keterangan,
ADD COLUMN IF NOT EXISTS upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Tanggal dan waktu upload dokumen' AFTER keterangan_lengkap;

-- Update jenis_dokumen ENUM to match upload dialog categories
-- First backup existing data into temp column
ALTER TABLE dokumen
ADD COLUMN IF NOT EXISTS jenis_dokumen_old VARCHAR(100);

UPDATE dokumen SET jenis_dokumen_old = jenis_dokumen WHERE jenis_dokumen_old IS NULL;

-- Modify the enum column - this recreates the column with new values
ALTER TABLE dokumen
MODIFY COLUMN jenis_dokumen VARCHAR(100) DEFAULT 'Dokumen Lainnya'
COMMENT 'Kategori dokumen (Sakramental, Umat, Administrasi, Keuangan, dll)';

-- Add index for better query performance
ALTER TABLE dokumen
ADD INDEX IF NOT EXISTS idx_jenis_dokumen (jenis_dokumen),
ADD INDEX IF NOT EXISTS idx_bentuk_dokumen (bentuk_dokumen),
ADD INDEX IF NOT EXISTS idx_kategori_file (kategori_file),
ADD INDEX IF NOT EXISTS idx_upload_date (upload_date);

-- Verify the table structure
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'dokumen'
-- ORDER BY ORDINAL_POSITION;
