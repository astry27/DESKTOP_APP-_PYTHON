-- Migration 10: Fix dokumen table - ensure jenis_dokumen has values
-- Memastikan kolom jenis_dokumen terisi dengan benar

USE `entf7819_db-client-server`;

-- Update existing records where jenis_dokumen is NULL or empty
-- Set default based on kategori or set to 'Administrasi' as default
UPDATE dokumen
SET jenis_dokumen = CASE
    WHEN kategori = 'Surat' THEN 'Administrasi'
    WHEN kategori = 'Laporan' THEN 'Keuangan'
    WHEN kategori = 'Foto' THEN 'Liturgi'
    WHEN kategori = 'Video' THEN 'Liturgi'
    WHEN kategori = 'Audio' THEN 'Liturgi'
    ELSE 'Administrasi'
END
WHERE jenis_dokumen IS NULL OR jenis_dokumen = '';

-- Ensure jenis_dokumen has a proper default value
ALTER TABLE dokumen
MODIFY COLUMN jenis_dokumen ENUM('Administrasi', 'Keanggotaan', 'Keuangan', 'Liturgi', 'Legalitas')
NOT NULL DEFAULT 'Administrasi';
