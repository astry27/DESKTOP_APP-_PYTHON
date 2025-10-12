-- Migration 9: Add missing fields to pengumuman table
-- Menambahkan kolom tanggal, sasaran, dan pembuat untuk pengumuman

USE `entf7819_db-client-server`;

-- Add tanggal column (single date for announcement) if not exists
SET @dbname = 'entf7819_db-client-server';
SET @tablename = 'pengumuman';
SET @columnname = 'tanggal';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " DATE NULL AFTER isi")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add sasaran column (target audience/purpose) if not exists
SET @columnname = 'sasaran';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " VARCHAR(200) NULL AFTER tanggal")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add pembuat column (creator name from input) if not exists
SET @columnname = 'pembuat';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " VARCHAR(100) NULL AFTER sasaran")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Update existing records to use tanggal_mulai as tanggal
UPDATE pengumuman
SET tanggal = tanggal_mulai
WHERE tanggal IS NULL;

-- Update existing records to set default sasaran
UPDATE pengumuman
SET sasaran = kategori
WHERE sasaran IS NULL OR sasaran = '';

-- Update existing records to set pembuat from admin or user
UPDATE pengumuman p
LEFT JOIN admin a ON p.dibuat_oleh_admin = a.id_admin
LEFT JOIN pengguna u ON p.dibuat_oleh_pengguna = u.id_pengguna
SET p.pembuat = COALESCE(a.username, u.username, 'System')
WHERE p.pembuat IS NULL OR p.pembuat = '';

-- Make tanggal NOT NULL after updating existing records
ALTER TABLE pengumuman
MODIFY COLUMN tanggal DATE NOT NULL;

-- Make sasaran NOT NULL after updating existing records
ALTER TABLE pengumuman
MODIFY COLUMN sasaran VARCHAR(200) NOT NULL DEFAULT 'Umum';

-- Make pembuat NOT NULL after updating existing records
ALTER TABLE pengumuman
MODIFY COLUMN pembuat VARCHAR(100) NOT NULL DEFAULT 'Administrator';

-- Create index for better query performance if not exists
SET @indexname = 'idx_pengumuman_tanggal';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (index_name = @indexname)
  ) > 0,
  "SELECT 1",
  CONCAT("CREATE INDEX ", @indexname, " ON ", @tablename, "(tanggal)")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @indexname = 'idx_pengumuman_sasaran';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (index_name = @indexname)
  ) > 0,
  "SELECT 1",
  CONCAT("CREATE INDEX ", @indexname, " ON ", @tablename, "(sasaran)")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;
