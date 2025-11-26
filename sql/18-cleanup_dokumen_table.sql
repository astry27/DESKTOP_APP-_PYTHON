-- Migration 18: Add updated_at column to dokumen table
-- Menambahkan kolom updated_at untuk tracking perubahan

USE `entf7819_db-client-server`;

-- ========================================
-- CEK STRUKTUR SEBELUM MIGRATION
-- ========================================

SELECT 'Struktur tabel dokumen SEBELUM migration:' AS info;
SHOW COLUMNS FROM dokumen;

-- ========================================
-- STEP: Add updated_at column
-- ========================================

-- Tambahkan kolom updated_at setelah kolom upload_date (atau created_at jika sudah ada)
-- Kolom ini akan otomatis update setiap kali ada perubahan data
ALTER TABLE dokumen
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- ========================================
-- VERIFIKASI HASIL
-- ========================================

SELECT 'Struktur tabel dokumen SETELAH migration:' AS info;
SHOW COLUMNS FROM dokumen;

SELECT 'Migration 18 selesai - Kolom updated_at berhasil ditambahkan!' AS info;
