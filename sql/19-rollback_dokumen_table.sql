-- Migration 19: Rollback dokumen table to original structure
-- Mengembalikan tabel dokumen ke struktur semula

USE `entf7819_db-client-server`;

-- ========================================
-- CEK STRUKTUR SEBELUM ROLLBACK
-- ========================================

SELECT 'Struktur tabel dokumen SEBELUM rollback:' AS info;
SHOW COLUMNS FROM dokumen;

-- ========================================
-- STEP 1: Rename created_at back to upload_date
-- ========================================

ALTER TABLE dokumen CHANGE COLUMN created_at upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ========================================
-- STEP 2: Drop updated_at column
-- ========================================

ALTER TABLE dokumen DROP COLUMN updated_at;

-- ========================================
-- STEP 3: Add back deleted columns
-- ========================================

-- Add file_path column
ALTER TABLE dokumen ADD COLUMN file_path VARCHAR(500) NOT NULL DEFAULT '' AFTER jenis_dokumen;

-- Add kategori column
ALTER TABLE dokumen ADD COLUMN kategori ENUM('Surat', 'Laporan', 'Foto', 'Video', 'Audio', 'Lainnya') DEFAULT 'Lainnya' AFTER tipe_file;

-- Add uploaded_by_admin column
ALTER TABLE dokumen ADD COLUMN uploaded_by_admin INT AFTER keterangan;

-- Add uploaded_by_pengguna column
ALTER TABLE dokumen ADD COLUMN uploaded_by_pengguna INT AFTER uploaded_by_admin;

-- ========================================
-- STEP 4: Re-add foreign key constraints
-- ========================================

ALTER TABLE dokumen
ADD CONSTRAINT fk_dokumen_admin
FOREIGN KEY (uploaded_by_admin) REFERENCES admin(id_admin) ON DELETE SET NULL;

ALTER TABLE dokumen
ADD CONSTRAINT fk_dokumen_pengguna
FOREIGN KEY (uploaded_by_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL;

-- ========================================
-- VERIFIKASI HASIL
-- ========================================

SELECT 'Struktur tabel dokumen SETELAH rollback:' AS info;
SHOW COLUMNS FROM dokumen;

SELECT 'Migration 19 selesai - Tabel dokumen dikembalikan ke struktur semula!' AS info;
