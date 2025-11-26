-- Migration 33: Add status_kekatolikan column to jemaat table
-- Created: 2025-11-05

ALTER TABLE jemaat
ADD COLUMN status_kekatolikan VARCHAR(100) DEFAULT NULL AFTER umur;

ALTER TABLE jemaat
ADD INDEX idx_status_kekatolikan (status_kekatolikan);
