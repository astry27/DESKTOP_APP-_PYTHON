-- Migration 52: Restructure dokumen table to match upload form fields
-- Purpose: Ensure database schema matches the upload dialog fields
-- Created: 2025-11-26

-- Step 1: Check current table structure
-- DESCRIBE dokumen;

-- Step 2: Add missing columns if they don't exist

-- Add upload_date column (untuk sorting dan audit trail)
ALTER TABLE dokumen ADD COLUMN IF NOT EXISTS upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add kategori column (Surat, Laporan, Foto, Video, Audio, Lainnya)
ALTER TABLE dokumen ADD COLUMN IF NOT EXISTS kategori_file VARCHAR(100) DEFAULT 'Lainnya';

-- Add keterangan column (deskripsi dokumen)
ALTER TABLE dokumen ADD COLUMN IF NOT EXISTS keterangan_lengkap TEXT;

-- Step 3: Verify all required columns exist
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'dokumen'
ORDER BY ORDINAL_POSITION;
