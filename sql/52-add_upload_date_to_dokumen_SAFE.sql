-- Migration 52: Restructure dokumen table to match upload form fields
-- Purpose: Add missing columns to dokumen table for proper upload functionality
-- Database: entf7819_db-client-server
-- Created: 2025-11-26
-- Safe for MariaDB/MySQL 5.7+

-- Step 1: Ensure upload_date column exists
-- This is critical for the API ordering
-- Syntax: ALTER TABLE table_name ADD COLUMN column_name type DEFAULT value;
ALTER TABLE dokumen
ADD COLUMN upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Step 2: Ensure kategori_file column exists (if needed for advanced features)
-- Categories: Surat, Laporan, Foto, Video, Audio, Lainnya
ALTER TABLE dokumen
ADD COLUMN kategori_file VARCHAR(100) DEFAULT 'Lainnya';

-- Step 3: Ensure keterangan_lengkap column exists (extended description)
ALTER TABLE dokumen
ADD COLUMN keterangan_lengkap TEXT;

-- Step 4: Verify all columns were added
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'dokumen'
ORDER BY ORDINAL_POSITION;

-- Expected output shows:
-- - id_dokumen (INT)
-- - nama_dokumen (VARCHAR)
-- - jenis_dokumen (ENUM)
-- - file_path (VARCHAR)
-- - ukuran_file (BIGINT)
-- - tipe_file (VARCHAR)
-- - kategori (ENUM) - original field
-- - keterangan (TEXT) - original field
-- - uploaded_by_admin (INT)
-- - uploaded_by_pengguna (INT)
-- - uploaded_by_name (VARCHAR)
-- - upload_date (TIMESTAMP) ✅ NEWLY ADDED
-- - kategori_file (VARCHAR) ✅ NEWLY ADDED
-- - keterangan_lengkap (TEXT) ✅ NEWLY ADDED
