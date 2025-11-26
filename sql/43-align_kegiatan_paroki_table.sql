-- =====================================================
-- MIGRATION: Align kegiatan (Paroki) table with UI
-- DATE: 2025-11-11
-- PURPOSE: Add missing column and align field names
-- =====================================================

-- Add sasaran_kegiatan column if not exists
ALTER TABLE kegiatan
ADD COLUMN IF NOT EXISTS sasaran_kegiatan text DEFAULT NULL COMMENT 'Sasaran/subjek kegiatan';

-- Rename penanggungjawab to penanggung_jawab for consistency
ALTER TABLE kegiatan
CHANGE COLUMN penanggungjawab penanggung_jawab varchar(100) DEFAULT NULL COMMENT 'Penanggung jawab kegiatan';

-- Verify structure
DESCRIBE kegiatan;
