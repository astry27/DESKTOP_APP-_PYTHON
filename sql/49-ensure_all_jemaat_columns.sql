-- Migration: 49-ensure_all_jemaat_columns.sql
-- Tujuan: Memastikan semua kolom yang diperlukan ada di tabel jemaat
-- User: Admin
-- Date: 2025-11-20

-- Check current schema dan tambahkan kolom yang hilang

-- Kolom Data Pribadi
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS wilayah_rohani VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS nama_keluarga VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS no_kk VARCHAR(16) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS nik VARCHAR(16) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tempat_lahir VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS umur INT NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_kekatolikan VARCHAR(100) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS kategori VARCHAR(50) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS hubungan_keluarga VARCHAR(100) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS pendidikan_terakhir VARCHAR(50) NULL;

-- Sakramen Babtis
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_babtis VARCHAR(50) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tanggal_babtis DATE NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tempat_babtis VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS nama_babtis VARCHAR(100) NULL;

-- Sakramen Ekaristi
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_ekaristi VARCHAR(50) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tanggal_komuni DATE NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tempat_komuni VARCHAR(255) NULL;

-- Sakramen Krisma
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_krisma VARCHAR(50) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tanggal_krisma DATE NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tempat_krisma VARCHAR(255) NULL;

-- Sakramen Perkawinan
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_perkawinan VARCHAR(50) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS keuskupan VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS paroki VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS kota_perkawinan VARCHAR(100) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS tanggal_perkawinan DATE NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_perkawinan_detail VARCHAR(100) NULL;

-- Status dan Lainnya
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS status_keanggotaan VARCHAR(50) NULL DEFAULT 'Aktif';
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS wr_tujuan VARCHAR(255) NULL;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS paroki_tujuan VARCHAR(255) NULL;

-- Index untuk performa
ALTER TABLE jemaat ADD INDEX IF NOT EXISTS idx_wilayah_rohani (wilayah_rohani);
ALTER TABLE jemaat ADD INDEX IF NOT EXISTS idx_kategori (kategori);
ALTER TABLE jemaat ADD INDEX IF NOT EXISTS idx_tanggal_lahir (tanggal_lahir);
ALTER TABLE jemaat ADD INDEX IF NOT EXISTS idx_status_keanggotaan (status_keanggotaan);

-- Verify
SELECT COUNT(DISTINCT COLUMN_NAME) as total_columns FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'jemaat';
