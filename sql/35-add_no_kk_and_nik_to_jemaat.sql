-- Migration 35: Add No. KK (Nomor Kartu Keluarga) and NIK (Nomor Identitas Kependudukan) to jemaat table
-- Date: 2025-11-06

USE entf7819_db-client-server;

-- Add No. KK column after nama_keluarga
ALTER TABLE jemaat
ADD COLUMN no_kk VARCHAR(20) NULL COMMENT 'Nomor Kartu Keluarga' AFTER nama_keluarga;

-- Add NIK column after nama_lengkap
ALTER TABLE jemaat
ADD COLUMN nik VARCHAR(20) NULL COMMENT 'Nomor Identitas Kependudukan' AFTER nama_lengkap;

-- Verify the changes
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_COMMENT
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
-- AND TABLE_NAME = 'jemaat'
-- ORDER BY ORDINAL_POSITION;
