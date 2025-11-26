-- Migration 20: Rename upload_date to created_at and add updated_at
-- Mengubah nama kolom upload_date menjadi created_at dan menambahkan updated_at

USE `entf7819_db-client-server`;

-- ========================================
-- CEK STRUKTUR SEBELUM MIGRATION
-- ========================================

SELECT 'Struktur tabel dokumen SEBELUM migration:' AS info;
SHOW COLUMNS FROM dokumen;

-- ========================================
-- STEP 1: Rename upload_date to created_at
-- ========================================

ALTER TABLE dokumen
CHANGE COLUMN upload_date created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ========================================
-- STEP 2: Add updated_at column
-- ========================================

ALTER TABLE dokumen
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- ========================================
-- VERIFIKASI HASIL
-- ========================================

SELECT 'Struktur tabel dokumen SETELAH migration:' AS info;
SHOW COLUMNS FROM dokumen;

SELECT 'Migration 20 selesai!' AS info;
SELECT 'Kolom upload_date telah diubah menjadi created_at' AS info;
SELECT 'Kolom updated_at telah ditambahkan' AS info;
