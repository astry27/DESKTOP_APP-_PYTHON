-- Migration 13: Fix pengumuman table cleanup (safer version)
-- Menangani masalah jika migration 12 gagal atau tidak lengkap
-- Struktur final: id_pengumuman, judul, isi, sasaran, pembuat, penanggung_jawab, is_active, created_at, updated_at

USE `entf7819_db-client-server`;

-- 1. Backup data pembuat jika kolom dibuat_oleh_admin/dibuat_oleh_pengguna masih ada
UPDATE pengumuman p
LEFT JOIN admin a ON p.dibuat_oleh_admin = a.id_admin
LEFT JOIN pengguna u ON p.dibuat_oleh_pengguna = u.id_pengguna
SET p.pembuat = COALESCE(
    p.pembuat,
    a.nama_lengkap,
    u.nama_lengkap,
    'Administrator'
)
WHERE (p.pembuat IS NULL OR p.pembuat = '')
AND (p.dibuat_oleh_admin IS NOT NULL OR p.dibuat_oleh_pengguna IS NOT NULL);

-- 2. Tambah kolom penanggung_jawab jika belum ada
SET @check_col = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'penanggung_jawab');
SET @sql = IF(@check_col = 0,
    'ALTER TABLE pengumuman ADD COLUMN penanggung_jawab VARCHAR(100) DEFAULT NULL',
    'SELECT "penanggung_jawab already exists" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 3. Set default penanggung_jawab dari pembuat untuk data existing
UPDATE pengumuman
SET penanggung_jawab = COALESCE(penanggung_jawab, pembuat, 'Administrator')
WHERE penanggung_jawab IS NULL OR penanggung_jawab = '';

-- 4. Pastikan kolom sasaran terisi
UPDATE pengumuman
SET sasaran = 'Umum'
WHERE sasaran IS NULL OR sasaran = '' OR sasaran = 'Semua Jemaat';

-- 5. Hapus kolom lama satu per satu dengan pengecekan

-- Drop tanggal
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'tanggal');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN tanggal', 'SELECT "tanggal already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop tanggal_mulai
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'tanggal_mulai');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN tanggal_mulai', 'SELECT "tanggal_mulai already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop tanggal_selesai
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'tanggal_selesai');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN tanggal_selesai', 'SELECT "tanggal_selesai already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop kategori
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'kategori');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN kategori', 'SELECT "kategori already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop prioritas
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'prioritas');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN prioritas', 'SELECT "prioritas already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop foreign key untuk dibuat_oleh_admin (jika ada)
SET @fk = (SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_admin' AND REFERENCED_TABLE_NAME IS NOT NULL LIMIT 1);
SET @sql = IF(@fk IS NOT NULL,
    CONCAT('ALTER TABLE pengumuman DROP FOREIGN KEY ', @fk),
    'SELECT "No FK for dibuat_oleh_admin"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop dibuat_oleh_admin
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'dibuat_oleh_admin');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN dibuat_oleh_admin', 'SELECT "dibuat_oleh_admin already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop foreign key untuk dibuat_oleh_pengguna (jika ada)
SET @fk = (SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'dibuat_oleh_pengguna' AND REFERENCED_TABLE_NAME IS NOT NULL LIMIT 1);
SET @sql = IF(@fk IS NOT NULL,
    CONCAT('ALTER TABLE pengumuman DROP FOREIGN KEY ', @fk),
    'SELECT "No FK for dibuat_oleh_pengguna"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop dibuat_oleh_pengguna
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND COLUMN_NAME = 'dibuat_oleh_pengguna');
SET @sql = IF(@check > 0, 'ALTER TABLE pengumuman DROP COLUMN dibuat_oleh_pengguna', 'SELECT "dibuat_oleh_pengguna already dropped"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 6. Pastikan kolom yang tersisa memiliki tipe data yang benar
ALTER TABLE pengumuman
MODIFY COLUMN judul VARCHAR(200) NOT NULL,
MODIFY COLUMN isi TEXT NOT NULL,
MODIFY COLUMN sasaran VARCHAR(100) NOT NULL DEFAULT 'Umum',
MODIFY COLUMN pembuat VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN penanggung_jawab VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1,
MODIFY COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
MODIFY COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 7. Tambah index untuk performa (hanya jika belum ada)
SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND INDEX_NAME = 'idx_pengumuman_penanggung_jawab');
SET @sql = IF(@check = 0,
    'CREATE INDEX idx_pengumuman_penanggung_jawab ON pengumuman(penanggung_jawab)',
    'SELECT "Index idx_pengumuman_penanggung_jawab exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND INDEX_NAME = 'idx_pengumuman_pembuat');
SET @sql = IF(@check = 0,
    'CREATE INDEX idx_pengumuman_pembuat ON pengumuman(pembuat)',
    'SELECT "Index idx_pengumuman_pembuat exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND INDEX_NAME = 'idx_pengumuman_sasaran');
SET @sql = IF(@check = 0,
    'CREATE INDEX idx_pengumuman_sasaran ON pengumuman(sasaran)',
    'SELECT "Index idx_pengumuman_sasaran exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND INDEX_NAME = 'idx_pengumuman_created_at');
SET @sql = IF(@check = 0,
    'CREATE INDEX idx_pengumuman_created_at ON pengumuman(created_at)',
    'SELECT "Index idx_pengumuman_created_at exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @check = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pengumuman' AND INDEX_NAME = 'idx_pengumuman_is_active');
SET @sql = IF(@check = 0,
    'CREATE INDEX idx_pengumuman_is_active ON pengumuman(is_active)',
    'SELECT "Index idx_pengumuman_is_active exists"');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Verification: Show final table structure
SELECT 'Migration 13 completed - Final structure:' AS info;
SHOW COLUMNS FROM pengumuman;

-- Show sample data
SELECT
    id_pengumuman,
    judul,
    LEFT(isi, 30) AS isi_preview,
    sasaran,
    pembuat,
    penanggung_jawab,
    is_active,
    created_at,
    updated_at
FROM pengumuman
ORDER BY created_at DESC
LIMIT 3;
