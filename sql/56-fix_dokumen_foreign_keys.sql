-- Migration 56: Fix Dokumen Table Foreign Keys
-- Date: 2025-11-26
-- Purpose: Drop problematic foreign key constraints and clean dokumen table for proper upload

-- First, disable foreign key checks
SET FOREIGN_KEY_CHECKS=0;

-- Check if the problematic column exists and drop it if needed
-- The production database has an issue with uploaded_by_pengguna constraint
-- but the column may not exist in the CREATE TABLE statement

-- Drop foreign key for pengguna if it exists
ALTER TABLE dokumen DROP FOREIGN KEY IF EXISTS `fk_dokumen_pengguna`;

-- Verify the table structure - should have these columns:
-- id_dokumen, nama_dokumen, bentuk_dokumen, kategori_file, file_path,
-- ukuran_file, keterangan, upload_date, uploaded_by_admin, created_at, updated_at

-- Re-enable foreign key checksjhkas
SET FOREIGN_KEY_CHECKS=1;

-- Verify the constraints after cleanup
-- SHOW CREATE TABLE dokumen;
