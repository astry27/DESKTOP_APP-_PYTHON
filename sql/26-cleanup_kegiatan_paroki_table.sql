-- =====================================================
-- SCRIPT: Cleanup tabel kegiatan_paroki
-- PERUBAHAN:
-- 1. Rename kolom 'tanggal_mulai' menjadi 'tanggal_kegiatan'
-- 2. Rename kolom 'waktu_mulai' menjadi 'waktu_kegiatan'
-- 3. Hapus kolom 'tanggal_selesai'
-- 4. Hapus kolom 'waktu_selesai'
-- 5. Hapus kolom 'max_peserta'
-- 6. Hapus kolom 'user_id'
-- 7. Hapus kolom 'deskripsi'
-- =====================================================

-- Rename tanggal_mulai to tanggal_kegiatan
ALTER TABLE kegiatan_paroki
  CHANGE COLUMN tanggal_mulai tanggal_kegiatan DATE;

-- Rename waktu_mulai to waktu_kegiatan
ALTER TABLE kegiatan_paroki
  CHANGE COLUMN waktu_mulai waktu_kegiatan TIME;

-- Drop tanggal_selesai column jika ada
ALTER TABLE kegiatan_paroki
  DROP COLUMN IF EXISTS tanggal_selesai;

-- Drop waktu_selesai column jika ada
ALTER TABLE kegiatan_paroki
  DROP COLUMN IF EXISTS waktu_selesai;

-- Drop max_peserta column jika ada
ALTER TABLE kegiatan_paroki
  DROP COLUMN IF EXISTS max_peserta;

-- Drop user_id column jika ada
ALTER TABLE kegiatan_paroki
  DROP COLUMN IF EXISTS user_id;

-- Drop deskripsi column jika ada
ALTER TABLE kegiatan_paroki
  DROP COLUMN IF EXISTS deskripsi;

-- Verify structure
SELECT 'Kolom-kolom berhasil di-update pada tabel kegiatan_paroki' as status;

-- Show updated table structure
DESCRIBE kegiatan_paroki;
