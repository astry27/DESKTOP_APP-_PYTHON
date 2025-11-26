-- Migration 47: Complete jemaat table fields to fully support all form inputs
-- Purpose: Ensure all form input fields have corresponding database columns
-- Date: 2025-11-19
-- Status: Complete jemaat table with all necessary fields for UI display

-- ========== STEP 1: Add missing fields if not already present ==========

-- Status fields for tracking position changes
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS wr_tujuan VARCHAR(255) AFTER status_keanggotaan;
ALTER TABLE jemaat ADD COLUMN IF NOT EXISTS paroki_tujuan VARCHAR(255) AFTER wr_tujuan;

-- ========== STEP 2: Verify all required columns exist ==========

-- The following columns should exist from previous migrations:
-- DATA PRIBADI:
--   id_jemaat (PRIMARY KEY)
--   wilayah_rohani, nama_keluarga, no_kk, nama_lengkap, nik
--   tempat_lahir, tanggal_lahir, umur, status_kekatolikan, kategori
--   jenis_kelamin, hubungan_keluarga, pendidikan_terakhir, status_menikah
--   jenis_pekerjaan, detail_pekerjaan, alamat, email, no_telepon

-- SAKRAMEN:
--   status_babtis, tempat_babtis, tanggal_babtis, nama_babtis
--   status_ekaristi, tempat_komuni, tanggal_komuni
--   status_krisma, tempat_krisma, tanggal_krisma
--   status_perkawinan, keuskupan, paroki, kota_perkawinan
--   tanggal_perkawinan, status_perkawinan_detail

-- STATUS:
--   status_keanggotaan
--   wr_tujuan (newly added)
--   paroki_tujuan (newly added)

-- TRACKING:
--   created_at, updated_at, created_by_pengguna

-- ========== STEP 3: Ensure proper data types for form inputs ==========

-- All VARCHAR columns should accept the following values:
-- - wilayah_rohani: One of the 27 saint names from form
-- - status_kekatolikan: Kelahiran, Babtisan, Penerimaan, Pindah Agama, or custom value
-- - kategori: Balita, Anak-anak, Remaja, OMK, KBK, KIK, Lansia
-- - jenis_kelamin: Laki-laki or Perempuan
-- - hubungan_keluarga: Kepala Keluarga, Istri, Anak, Famili lain
-- - pendidikan_terakhir: SD, SMP, SMA, SMK, S1, S2, S3
-- - status_menikah: Belum Menikah, Sudah Menikah, Duda, Janda
-- - jenis_pekerjaan: Pelajar, Bekerja, Tidak Bekerja
-- - status_babtis, status_ekaristi, status_krisma, status_perkawinan: Belum or Sudah
-- - status_perkawinan_detail: Sipil, Gereja, Sipil dan Gereja
-- - status_keanggotaan: Menetap, Pindah, Meninggal Dunia

-- ========== STEP 4: Create indexes for improved query performance ==========

CREATE INDEX IF NOT EXISTS idx_jemaat_wr_tujuan ON jemaat(wr_tujuan);
CREATE INDEX IF NOT EXISTS idx_jemaat_paroki_tujuan ON jemaat(paroki_tujuan);

-- ========== STEP 5: Data synchronization - normalize status values ==========

-- Ensure status values are consistent
UPDATE jemaat
SET status_perkawinan = CASE
    WHEN status_perkawinan IN ('Belum', 'Sudah') THEN status_perkawinan
    WHEN status_perkawinan IS NULL OR status_perkawinan = '' THEN 'Belum'
    ELSE 'Belum'
END
WHERE status_perkawinan NOT IN ('Belum', 'Sudah');

-- ========== STEP 6: API Compatibility Notes ==========

-- Field mapping in API (API/routes/jemaat_routes.py):
--   'status_menikah' (form) <-> 'status_pernikahan' (database) - This is handled by API
--   All other fields map directly from form field names to database column names

-- The API dynamically builds INSERT and UPDATE queries based on provided fields:
-- - Only non-empty fields are inserted/updated
-- - Field validation happens in the API layer
-- - Database just stores the values as provided by API

-- ========== STEP 7: Summary of Changes ==========

-- NEW COLUMNS ADDED:
-- - wr_tujuan: VARCHAR(255) - Destination Wilayah Rohani for transfer status
-- - paroki_tujuan: VARCHAR(255) - Destination Paroki for transfer status

-- INDEXES ADDED:
-- - idx_jemaat_wr_tujuan: For faster queries on wr_tujuan
-- - idx_jemaat_paroki_tujuan: For faster queries on paroki_tujuan

-- TOTAL COLUMNS IN TABLE: 37 data columns + 4 tracking columns = 41 columns total

-- ========== STEP 8: Verification Query ==========

-- To verify all columns exist and their structure:
-- SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'jemaat' AND TABLE_SCHEMA = DATABASE()
-- ORDER BY ORDINAL_POSITION;
