-- =====================================================
-- SCRIPT: Remove nomor_referensi column dari tabel keuangan
-- PERUBAHAN:
-- 1. Hapus kolom 'nomor_referensi'
-- =====================================================

-- Drop nomor_referensi column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS nomor_referensi;

-- Verify structure
SELECT 'Kolom nomor_referensi berhasil dihapus dari tabel keuangan' as status;

-- Show updated table structure
DESCRIBE keuangan;
