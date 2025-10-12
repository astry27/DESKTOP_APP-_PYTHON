-- Migration 12: Cleanup pengumuman table structure
-- Menghapus kolom yang tidak digunakan di UI dan menyederhanakan struktur tabel
-- UI Components: Tanggal (dari created_at), Pembuat, Sasaran/Tujuan, Judul Pengumuman, Isi Pengumuman, Penanggung Jawab

USE `entf7819_db-client-server`;

-- 1. Backup data penting sebelum menghapus kolom
-- Update kolom pembuat dari relasi admin/pengguna jika masih NULL
UPDATE pengumuman p
LEFT JOIN admin a ON p.dibuat_oleh_admin = a.id_admin
LEFT JOIN pengguna u ON p.dibuat_oleh_pengguna = u.id_pengguna
SET p.pembuat = COALESCE(
    p.pembuat,
    a.nama_lengkap,
    u.nama_lengkap,
    'Administrator'
)
WHERE p.pembuat IS NULL OR p.pembuat = '';

-- 2. Tambah kolom penanggung_jawab jika belum ada
-- Check if column exists first, if not add it
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'penanggung_jawab'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE pengumuman ADD COLUMN penanggung_jawab VARCHAR(100) DEFAULT NULL',
    'SELECT "Column penanggung_jawab already exists" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Set default penanggung_jawab sama dengan pembuat untuk data existing
UPDATE pengumuman
SET penanggung_jawab = COALESCE(pembuat, 'Administrator')
WHERE penanggung_jawab IS NULL;

-- 4. Pastikan kolom sasaran terisi dengan default 'Umum' jika masih kosong
UPDATE pengumuman
SET sasaran = 'Umum'
WHERE sasaran IS NULL OR sasaran = '' OR sasaran = 'Semua Jemaat';

-- 5. Hapus kolom yang tidak digunakan di UI
-- Menghapus: tanggal_mulai, tanggal_selesai, kategori, prioritas, dibuat_oleh_admin, dibuat_oleh_pengguna
-- MySQL/MariaDB tidak mendukung IF EXISTS untuk DROP COLUMN, jadi kita cek dan hapus satu per satu

-- Drop tanggal_mulai
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'tanggal_mulai');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN tanggal_mulai', 'SELECT "tanggal_mulai already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop tanggal_selesai
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'tanggal_selesai');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN tanggal_selesai', 'SELECT "tanggal_selesai already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop kategori
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'kategori');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN kategori', 'SELECT "kategori already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop prioritas
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'prioritas');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN prioritas', 'SELECT "prioritas already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop foreign key constraint for dibuat_oleh_admin if exists
SET @check_fk = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_admin'
    AND REFERENCED_TABLE_NAME IS NOT NULL);
SET @fk_name = (SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_admin'
    AND REFERENCED_TABLE_NAME IS NOT NULL LIMIT 1);
SET @sql = IF(@check_fk > 0, CONCAT('ALTER TABLE pengumuman DROP FOREIGN KEY ', @fk_name), 'SELECT "No FK for dibuat_oleh_admin" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop dibuat_oleh_admin
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'dibuat_oleh_admin');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN dibuat_oleh_admin', 'SELECT "dibuat_oleh_admin already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop foreign key constraint for dibuat_oleh_pengguna if exists
SET @check_fk = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_pengguna'
    AND REFERENCED_TABLE_NAME IS NOT NULL);
SET @fk_name = (SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_pengguna'
    AND REFERENCED_TABLE_NAME IS NOT NULL LIMIT 1);
SET @sql = IF(@check_fk > 0, CONCAT('ALTER TABLE pengumuman DROP FOREIGN KEY ', @fk_name), 'SELECT "No FK for dibuat_oleh_pengguna" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop dibuat_oleh_pengguna
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server' AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'dibuat_oleh_pengguna');
SET @sql = IF(@check_col > 0, 'ALTER TABLE pengumuman DROP COLUMN dibuat_oleh_pengguna', 'SELECT "dibuat_oleh_pengguna already dropped" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 6. Pastikan kolom yang tersisa memiliki tipe data dan default yang sesuai
ALTER TABLE pengumuman
MODIFY COLUMN judul VARCHAR(200) NOT NULL,
MODIFY COLUMN isi TEXT NOT NULL,
MODIFY COLUMN sasaran VARCHAR(100) NOT NULL DEFAULT 'Umum',
MODIFY COLUMN pembuat VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN penanggung_jawab VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1,
MODIFY COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
MODIFY COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 7. Add index untuk performa query
CREATE INDEX IF NOT EXISTS idx_pengumuman_penanggung_jawab ON pengumuman(penanggung_jawab);
CREATE INDEX IF NOT EXISTS idx_pengumuman_pembuat ON pengumuman(pembuat);
CREATE INDEX IF NOT EXISTS idx_pengumuman_sasaran ON pengumuman(sasaran);
CREATE INDEX IF NOT EXISTS idx_pengumuman_created_at ON pengumuman(created_at);
CREATE INDEX IF NOT EXISTS idx_pengumuman_is_active ON pengumuman(is_active);

-- Verification: Show table structure
SELECT 'Struktur tabel pengumuman setelah migration:' AS info;
SHOW COLUMNS FROM pengumuman;

-- Verification: Show sample data
SELECT
    id_pengumuman,
    judul,
    pembuat,
    penanggung_jawab,
    sasaran,
    LEFT(isi, 50) AS isi_preview,
    is_active,
    DATE_FORMAT(created_at, '%W, %d %M %Y') AS tanggal_display,
    created_at
FROM pengumuman
ORDER BY created_at DESC
LIMIT 5;
