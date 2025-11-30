-- Migration 55: Add Ukuran File Column to Dokumen Table
-- Date: 2025-11-26
-- Purpose: Add column to store automatic file size from uploaded documents
-- Changes: Add ukuran_file column with automatic size detection

-- Add ukuran_file column if it doesn't exist
ALTER TABLE dokumen
ADD COLUMN IF NOT EXISTS ukuran_file BIGINT DEFAULT 0 COMMENT 'Ukuran file dalam bytes - otomatis terisi saat upload' AFTER file_path;

-- Create index for better query performance
ALTER TABLE dokumen
ADD INDEX IF NOT EXISTS idx_ukuran_file (ukuran_file);

-- Set default value for existing records if needed
UPDATE dokumen
SET ukuran_file = 0
WHERE ukuran_file IS NULL;

-- Verify the column structure
-- SELECT id_dokumen, nama_dokumen, file_path, ukuran_file
-- FROM dokumen
-- LIMIT 5;
