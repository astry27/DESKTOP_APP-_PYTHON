-- =====================================================
-- SCRIPT: Update tabel program_kerja
-- PERUBAHAN:
-- 1. Rename kolom 'deskripsi' menjadi 'keterangan'
-- =====================================================

-- Rename deskripsi column to keterangan
ALTER TABLE program_kerja
  CHANGE COLUMN deskripsi keterangan TEXT;

-- Verify structure
SELECT 'Kolom deskripsi berhasil direname menjadi keterangan' as status;

-- Show updated table structure
DESCRIBE program_kerja;
