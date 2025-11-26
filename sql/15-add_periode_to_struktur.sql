-- Migration 15: Add periode column to struktur table
-- Description: Menambahkan kolom periode untuk menyimpan periode jabatan pengurus (format: YYYY-YYYY)
-- Date: 2025-01-20

-- Add periode column to struktur table
ALTER TABLE struktur
ADD COLUMN periode VARCHAR(9) NULL;

-- Add index for better query performance when filtering by periode
CREATE INDEX idx_struktur_periode ON struktur(periode);

-- Update existing records with default periode (optional - sesuaikan dengan kebutuhan)
-- UPDATE struktur SET periode = '2024-2027' WHERE periode IS NULL OR periode = '';

-- Verify the changes
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'struktur' AND COLUMN_NAME = 'periode';
