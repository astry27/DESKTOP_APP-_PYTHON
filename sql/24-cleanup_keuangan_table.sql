-- =====================================================
-- SCRIPT: Cleanup tabel keuangan
-- PERUBAHAN:
-- 1. Hapus kolom 'no_referensi'
-- 2. Hapus kolom 'bukti_file'
-- 3. Hapus kolom 'metode_pembayaran'
-- 4. Hapus kolom 'penanggung_jawab'
-- 5. Hapus kolom 'deskripsi'
-- =====================================================

-- Drop no_referensi column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS no_referensi;

-- Drop bukti_file column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS bukti_file;

-- Drop metode_pembayaran column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS metode_pembayaran;

-- Drop penanggung_jawab column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS penanggung_jawab;

-- Drop deskripsi column jika ada
ALTER TABLE keuangan
  DROP COLUMN IF EXISTS deskripsi;

-- Verify structure
SELECT 'Kolom-kolom berhasil dihapus dari tabel keuangan' as status;

-- Show updated table structure
DESCRIBE keuangan;
