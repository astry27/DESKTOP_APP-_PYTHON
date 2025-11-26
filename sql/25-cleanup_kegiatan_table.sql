-- =====================================================
-- SCRIPT: Cleanup tabel kegiatan_wr
-- PERUBAHAN:
-- 1. Hapus kolom 'tanggal_selesai'
-- 2. Hapus kolom 'waktu_selesai'
-- 3. Hapus kolom 'deskripsi'
-- =====================================================

-- Drop tanggal_selesai column jika ada
ALTER TABLE kegiatan_wr
  DROP COLUMN IF EXISTS tanggal_selesai;

-- Drop waktu_selesai column jika ada
ALTER TABLE kegiatan_wr
  DROP COLUMN IF EXISTS waktu_selesai;

-- Drop deskripsi column jika ada
ALTER TABLE kegiatan_wr
  DROP COLUMN IF EXISTS deskripsi;

-- Verify structure
SELECT 'Kolom-kolom berhasil dihapus dari tabel kegiatan_wr' as status;

-- Show updated table structure
DESCRIBE kegiatan_wr;
