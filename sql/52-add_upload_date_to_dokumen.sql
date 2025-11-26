-- Migration: Add upload_date column to dokumen table
-- Purpose: Fix dokumen API endpoint error - column missing in production
-- Database: entf7819_db-client-server
-- Created: 2025-11-26

-- Method 1: Try modern syntax first (MySQL 8.0.1+)
-- This will work if server supports it
ALTER TABLE dokumen
ADD COLUMN IF NOT EXISTS upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- If above fails, use this alternative (compatible with older MySQL):
-- ALTER TABLE dokumen
-- ADD COLUMN upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Verify the column was added successfully
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'dokumen' AND COLUMN_NAME = 'upload_date';
