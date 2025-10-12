-- Migration 14: Drop kolom tanggal dari tabel pengumuman
-- Menghapus kolom tanggal yang masih tersisa setelah migration sebelumnya

USE `entf7819_db-client-server`;

-- Check dan drop kolom tanggal jika masih ada
SET @check_col = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'pengumuman'
    AND COLUMN_NAME = 'tanggal'
);

SET @sql = IF(@check_col > 0,
    'ALTER TABLE pengumuman DROP COLUMN tanggal',
    'SELECT "Column tanggal already dropped or does not exist" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verification: Show completion message
SELECT 'Migration 14 completed - Kolom tanggal dihapus' AS status;
