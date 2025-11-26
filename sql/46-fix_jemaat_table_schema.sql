-- Migration: Fix jemaat table schema to match UI requirements
-- Purpose: Standardize data types and ensure all data displays correctly
-- Date: 2025-11-19
-- Path: sql/46-fix_jemaat_table_schema.sql

-- ========== STEP 1: Fix column data types to match storage ==========

-- Note: Most columns are already present in database as VARCHAR
-- We will keep them as VARCHAR for backward compatibility
-- but ensure they accept proper enum values

-- Normalize status columns - update existing invalid values first
UPDATE jemaat SET status_keanggotaan = 'Aktif' WHERE status_keanggotaan = 'Pilih Status' OR status_keanggotaan IS NULL;
UPDATE jemaat SET status_babtis = 'Belum' WHERE status_babtis IS NULL;
UPDATE jemaat SET status_ekaristi = 'Belum' WHERE status_ekaristi IS NULL;
UPDATE jemaat SET status_krisma = 'Belum' WHERE status_krisma IS NULL;

-- ========== STEP 2: Verify all required columns exist ==========

-- Data Pribadi columns - all should already exist from backup
-- Verifying core columns:
-- - id_jemaat (PRIMARY KEY)
-- - nama_lengkap
-- - nik
-- - nama_keluarga
-- - no_kk
-- - alamat
-- - email
-- - tanggal_lahir
-- - tempat_lahir
-- - umur
-- - status_kekatolikan
-- - kategori
-- - hubungan_keluarga
-- - jenis_kelamin
-- - status_menikah
-- - wilayah_rohani
-- - jenis_pekerjaan
-- - detail_pekerjaan
-- - pendidikan_terakhir

-- Sacrament columns - all should already exist from backup
-- Babtis:
-- - status_babtis
-- - tempat_babtis
-- - tanggal_babtis
-- - nama_babtis

-- Ekaristi:
-- - status_ekaristi
-- - tempat_komuni
-- - tanggal_komuni

-- Krisma:
-- - status_krisma
-- - tempat_krisma
-- - tanggal_krisma

-- Perkawinan:
-- - status_perkawinan
-- - keuskupan
-- - paroki
-- - kota_perkawinan
-- - tanggal_perkawinan
-- - status_perkawinan_detail

-- Status columns:
-- - status_keanggotaan
-- - wr_tujuan
-- - paroki_tujuan

-- Timestamps and tracking:
-- - created_at
-- - updated_at
-- - created_by_pengguna

-- ========== STEP 3: Add missing columns if not already present ==========

-- Check and add no_telepon if missing (for backward compatibility)
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS no_telepon VARCHAR(20) AFTER email;

-- ========== STEP 4: Create or update indexes for performance ==========

CREATE INDEX IF NOT EXISTS idx_jemaat_nama_lengkap ON jemaat(nama_lengkap);
CREATE INDEX IF NOT EXISTS idx_jemaat_wilayah_rohani ON jemaat(wilayah_rohani);
CREATE INDEX IF NOT EXISTS idx_jemaat_nama_keluarga ON jemaat(nama_keluarga);
CREATE INDEX IF NOT EXISTS idx_jemaat_no_kk ON jemaat(no_kk);
CREATE INDEX IF NOT EXISTS idx_jemaat_nik ON jemaat(nik);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_keanggotaan ON jemaat(status_keanggotaan);
CREATE INDEX IF NOT EXISTS idx_jemaat_kategori ON jemaat(kategori);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_babtis ON jemaat(status_babtis);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_ekaristi ON jemaat(status_ekaristi);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_krisma ON jemaat(status_krisma);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_perkawinan ON jemaat(status_perkawinan);
CREATE INDEX IF NOT EXISTS idx_jemaat_created_by_pengguna ON jemaat(created_by_pengguna);
CREATE INDEX IF NOT EXISTS idx_jemaat_created_at ON jemaat(created_at);

-- ========== STEP 5: Ensure foreign key for created_by_pengguna ==========

-- Foreign key constraint sudah ada dari setup database awal
-- Tidak perlu menambahkan ulang untuk menghindari duplicate constraint error

-- ========== STEP 6: Data normalization ==========

-- Normalize status values in existing data
UPDATE jemaat SET status_babtis = 'Belum' WHERE status_babtis IS NULL OR status_babtis = '' OR status_babtis NOT IN ('Belum', 'Sudah');
UPDATE jemaat SET status_ekaristi = 'Belum' WHERE status_ekaristi IS NULL OR status_ekaristi = '' OR status_ekaristi NOT IN ('Belum', 'Sudah');
UPDATE jemaat SET status_krisma = 'Belum' WHERE status_krisma IS NULL OR status_krisma = '' OR status_krisma NOT IN ('Belum', 'Sudah');
UPDATE jemaat SET status_perkawinan = 'Belum' WHERE status_perkawinan IS NULL OR status_perkawinan = '' OR status_perkawinan NOT IN ('Belum', 'Sudah');
UPDATE jemaat SET status_keanggotaan = 'Aktif' WHERE status_keanggotaan IS NULL OR status_keanggotaan = '' OR status_keanggotaan NOT IN ('Aktif', 'Menetap', 'Pindah', 'Meninggal', 'Tidak Aktif');

-- Normalize gender values (keep consistency)
UPDATE jemaat SET jenis_kelamin = 'Laki-laki' WHERE jenis_kelamin = 'L' OR jenis_kelamin = 'l';
UPDATE jemaat SET jenis_kelamin = 'Perempuan' WHERE jenis_kelamin = 'P' OR jenis_kelamin = 'p';
UPDATE jemaat SET jenis_kelamin = 'Laki-laki' WHERE jenis_kelamin IS NULL OR jenis_kelamin = '';

-- Normalize kategori values - ensure valid category
UPDATE jemaat SET kategori = 'Anak-anak' WHERE kategori IS NULL OR kategori = '' OR kategori NOT IN ('Balita', 'Anak-anak', 'Remaja', 'OMK', 'KBK', 'KIK', 'Lansia');

-- Normalize status_kekatolikan
UPDATE jemaat SET status_kekatolikan = 'Katolik' WHERE status_kekatolikan IS NULL OR status_kekatolikan = '' OR status_kekatolikan NOT IN ('Katolik', 'Calon Katolik', 'Lain-lain');

-- Normalize hubungan_keluarga
UPDATE jemaat SET hubungan_keluarga = 'Kepala Keluarga' WHERE hubungan_keluarga IS NULL OR hubungan_keluarga = '';

-- Normalize status_menikah
UPDATE jemaat SET status_menikah = 'Belum Menikah' WHERE status_menikah IS NULL OR status_menikah = '';

-- Normalize pendidikan_terakhir
UPDATE jemaat SET pendidikan_terakhir = 'SMA' WHERE pendidikan_terakhir IS NULL OR pendidikan_terakhir = '';

-- Normalize jenis_pekerjaan
UPDATE jemaat SET jenis_pekerjaan = 'Bekerja' WHERE jenis_pekerjaan IS NULL OR jenis_pekerjaan = '';

-- ========== STEP 7: Verify column order and structure ==========
-- Final verification can be done with:
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'jemaat'
-- ORDER BY ORDINAL_POSITION;
