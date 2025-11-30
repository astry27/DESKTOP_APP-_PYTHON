-- Migration 59: Change estimasi_waktu from VARCHAR to DATE in program_kerja_wr table
-- This changes the column from month names (e.g., "Januari") to actual dates (e.g., "2024-01-15")
-- Format in application will be dd/mm/yyyy

-- Use the correct database name (check if it's with underscore or hyphen)
USE `entf7819_db-client-server`;

-- Step 1: Check if table exists and show current structure
SELECT 'Checking current table structure...' AS step;
DESCRIBE program_kerja_wr;

-- Step 2: Add new column tanggal_pelaksanaan as DATE (only if not exists)
SELECT 'Adding new column tanggal_pelaksanaan...' AS step;

SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'program_kerja_wr'
    AND COLUMN_NAME = 'tanggal_pelaksanaan'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE program_kerja_wr ADD COLUMN tanggal_pelaksanaan DATE NULL AFTER estimasi_waktu',
    'SELECT "Column tanggal_pelaksanaan already exists, skipping..." AS notice'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 3: Migrate existing data (convert month names to first day of current year's month)
SELECT 'Migrating existing data...' AS step;

UPDATE program_kerja_wr
SET tanggal_pelaksanaan = CASE estimasi_waktu
    WHEN 'Januari' THEN CONCAT(YEAR(CURDATE()), '-01-01')
    WHEN 'Februari' THEN CONCAT(YEAR(CURDATE()), '-02-01')
    WHEN 'Maret' THEN CONCAT(YEAR(CURDATE()), '-03-01')
    WHEN 'April' THEN CONCAT(YEAR(CURDATE()), '-04-01')
    WHEN 'Mei' THEN CONCAT(YEAR(CURDATE()), '-05-01')
    WHEN 'Juni' THEN CONCAT(YEAR(CURDATE()), '-06-01')
    WHEN 'Juli' THEN CONCAT(YEAR(CURDATE()), '-07-01')
    WHEN 'Agustus' THEN CONCAT(YEAR(CURDATE()), '-08-01')
    WHEN 'September' THEN CONCAT(YEAR(CURDATE()), '-09-01')
    WHEN 'Oktober' THEN CONCAT(YEAR(CURDATE()), '-10-01')
    WHEN 'November' THEN CONCAT(YEAR(CURDATE()), '-11-01')
    WHEN 'Desember' THEN CONCAT(YEAR(CURDATE()), '-12-01')
    ELSE tanggal_pelaksanaan  -- Keep existing value if already a date
END
WHERE estimasi_waktu IS NOT NULL
  AND tanggal_pelaksanaan IS NULL;

-- Step 4: Show data before dropping old column
SELECT 'Preview of data (first 5 rows):' AS step;
SELECT id_program_kerja_wr, judul, estimasi_waktu, tanggal_pelaksanaan
FROM program_kerja_wr
LIMIT 5;

-- Step 5: Drop old estimasi_waktu column
SELECT 'Dropping old estimasi_waktu column...' AS step;

SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'program_kerja_wr'
    AND COLUMN_NAME = 'estimasi_waktu'
);

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE program_kerja_wr DROP COLUMN estimasi_waktu',
    'SELECT "Column estimasi_waktu already dropped, skipping..." AS notice'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 6: Rename tanggal_pelaksanaan to estimasi_waktu (keeping same column name for compatibility)
SELECT 'Renaming tanggal_pelaksanaan to estimasi_waktu...' AS step;

SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'program_kerja_wr'
    AND COLUMN_NAME = 'tanggal_pelaksanaan'
);

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE program_kerja_wr CHANGE COLUMN tanggal_pelaksanaan estimasi_waktu DATE NULL',
    'SELECT "Column tanggal_pelaksanaan does not exist, skipping rename..." AS notice'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 7: Add index on estimasi_waktu for better query performance (if not exists)
SELECT 'Adding index on estimasi_waktu...' AS step;

SET @index_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'entf7819_db-client-server'
    AND TABLE_NAME = 'program_kerja_wr'
    AND INDEX_NAME = 'idx_estimasi_waktu'
);

SET @sql = IF(@index_exists = 0,
    'ALTER TABLE program_kerja_wr ADD INDEX idx_estimasi_waktu (estimasi_waktu)',
    'SELECT "Index idx_estimasi_waktu already exists, skipping..." AS notice'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 8: Verify the changes
SELECT 'Migration 59 completed successfully!' AS status;
SELECT '========================================' AS separator;
SELECT 'Final table structure:' AS info;
DESCRIBE program_kerja_wr;

SELECT '========================================' AS separator;
SELECT 'Sample data (first 5 rows):' AS info;
SELECT id_program_kerja_wr, judul, estimasi_waktu, kategori, status
FROM program_kerja_wr
LIMIT 5;
