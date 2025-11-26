-- Migration: Add umur (age) column to jemaat table
-- Purpose: Ensure umur field exists and can be stored for display
-- Date: 2025-11-20
-- Path: sql/48-add_umur_column_to_jemaat.sql

-- Add umur column if it doesn't exist
-- The column will store the calculated age from tanggal_lahir
-- Type: VARCHAR(3) to store age values like "25", "30", etc.
-- Position: After tanggal_lahir

ALTER TABLE jemaat
ADD COLUMN IF NOT EXISTS umur VARCHAR(3)
AFTER tanggal_lahir;

-- Add index for better performance when filtering by age
CREATE INDEX IF NOT EXISTS idx_jemaat_umur ON jemaat(umur);

-- Optional: Update existing records with calculated age from tanggal_lahir
-- This will calculate age for existing records that don't have umur set
UPDATE jemaat
SET umur = TIMESTAMPDIFF(YEAR, tanggal_lahir, CURDATE())
WHERE tanggal_lahir IS NOT NULL
  AND (umur IS NULL OR umur = '');
