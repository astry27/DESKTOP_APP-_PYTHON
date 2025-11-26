-- Migration 16: Remove unnecessary columns from struktur table
-- Description: Menghapus kolom yang tidak diperlukan dari tabel struktur
-- Date: 2025-10-20

-- Remove unused columns from struktur table one by one (safer approach)
-- Check and drop each column individually to avoid errors

-- Drop gelar_depan if exists
SET @dbname = DATABASE();
SET @tablename = 'struktur';
SET @columnname = 'gelar_depan';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN gelar_depan;',
  'SELECT ''Column gelar_depan does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop gelar_belakang if exists
SET @columnname = 'gelar_belakang';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN gelar_belakang;',
  'SELECT ''Column gelar_belakang does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop tanggal_lahir if exists
SET @columnname = 'tanggal_lahir';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN tanggal_lahir;',
  'SELECT ''Column tanggal_lahir does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop status_klerus if exists
SET @columnname = 'status_klerus';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN status_klerus;',
  'SELECT ''Column status_klerus does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop level_hierarki if exists
SET @columnname = 'level_hierarki';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN level_hierarki;',
  'SELECT ''Column level_hierarki does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop bidang_pelayanan if exists
SET @columnname = 'bidang_pelayanan';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN bidang_pelayanan;',
  'SELECT ''Column bidang_pelayanan does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop tanggal_mulai_jabatan if exists
SET @columnname = 'tanggal_mulai_jabatan';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN tanggal_mulai_jabatan;',
  'SELECT ''Column tanggal_mulai_jabatan does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop tanggal_berakhir_jabatan if exists
SET @columnname = 'tanggal_berakhir_jabatan';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN tanggal_berakhir_jabatan;',
  'SELECT ''Column tanggal_berakhir_jabatan does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop deskripsi_tugas if exists
SET @columnname = 'deskripsi_tugas';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN deskripsi_tugas;',
  'SELECT ''Column deskripsi_tugas does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop alamat if exists
SET @columnname = 'alamat';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE struktur DROP COLUMN alamat;',
  'SELECT ''Column alamat does not exist, skipping...'';'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Verify the changes - show remaining columns
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'struktur'
ORDER BY ORDINAL_POSITION;
