-- Migration 32: Add jenis_kelamin column to kategorial table
-- Created: 2025-11-05

ALTER TABLE kategorial
ADD COLUMN jenis_kelamin VARCHAR(50) DEFAULT NULL AFTER nama_lengkap;

ALTER TABLE kategorial
ADD INDEX idx_jenis_kelamin (jenis_kelamin);
