-- Migration 57: Remove wilayah_rohani_id from program_kerja_wr table (if exists)
-- Purpose: Clean up unnecessary column and ensure proper table structure

-- Drop foreign key constraint if exists
SET @constraint_name = (
    SELECT CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'program_kerja_wr'
    AND COLUMN_NAME = 'wilayah_rohani_id'
    AND CONSTRAINT_NAME != 'PRIMARY'
    LIMIT 1
);

SET @sql = IF(@constraint_name IS NOT NULL,
    CONCAT('ALTER TABLE program_kerja_wr DROP FOREIGN KEY ', @constraint_name),
    'SELECT "No foreign key constraint found"');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Drop column if exists
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'program_kerja_wr'
    AND COLUMN_NAME = 'wilayah_rohani_id'
);

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE program_kerja_wr DROP COLUMN wilayah_rohani_id',
    'SELECT "Column wilayah_rohani_id does not exist"');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
