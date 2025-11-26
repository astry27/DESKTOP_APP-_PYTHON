-- Migration 21: Cleanup jemaat table - remove unused/duplicate columns
-- Menghapus kolom yang tidak digunakan di UI atau duplikat, mempertahankan created_at dan updated_at

USE `entf7819_db-client-server`;

-- ========================================
-- KOLOM YANG DIGUNAKAN DI UI (35 kolom data + created_at + updated_at + id_jemaat):
-- ========================================
-- 1. wilayah_rohani
-- 2. nama_keluarga
-- 3. nama_lengkap
-- 4. tempat_lahir
-- 5. tanggal_lahir
-- 6. umur
-- 7. kategori
-- 8. jenis_kelamin
-- 9. hubungan_keluarga
-- 10. pendidikan_terakhir
-- 11. status_menikah
-- 12. jenis_pekerjaan
-- 13. detail_pekerjaan
-- 14. alamat
-- 15. email
-- 16. status_babtis
-- 17. tempat_babtis
-- 18. tanggal_babtis
-- 19. nama_babtis
-- 20. status_ekaristi
-- 21. tempat_komuni
-- 22. tanggal_komuni
-- 23. status_krisma
-- 24. tempat_krisma
-- 25. tanggal_krisma
-- 26. status_perkawinan
-- 27. keuskupan
-- 28. paroki
-- 29. kota_perkawinan
-- 30. tanggal_perkawinan
-- 31. status_perkawinan_detail
-- 32. status_keanggotaan
-- 33. wr_tujuan
-- 34. paroki_tujuan
-- 35. created_by_pengguna
-- 36. created_at (TETAP DIPERTAHANKAN)
-- 37. updated_at (TETAP DIPERTAHANKAN)

-- ========================================
-- KOLOM YANG TIDAK DIGUNAKAN/DUPLIKAT (akan dihapus):
-- ========================================
-- - no_telepon (duplikat dengan email)
-- - pekerjaan (duplikat dengan jenis_pekerjaan + detail_pekerjaan)
-- - pendidikan (duplikat dengan pendidikan_terakhir)
-- - baptis_tanggal (duplikat dengan tanggal_babtis)
-- - baptis_tempat (duplikat dengan tempat_babtis)
-- - komuni_tanggal (duplikat dengan tanggal_komuni)
-- - komuni_tempat (duplikat dengan tempat_komuni)
-- - krisma_tanggal (duplikat dengan tanggal_krisma)
-- - krisma_tempat (duplikat dengan tempat_krisma)
-- - nama_ayah (tidak ada di UI)
-- - nama_ibu (tidak ada di UI)
-- - lingkungan (duplikat dengan wilayah_rohani)
-- - wilayah (duplikat dengan wilayah_rohani)
-- - keterangan (tidak ada di UI)
-- - status_pernikahan (duplikat dengan status_menikah + status_perkawinan_detail)
-- - tanggal_bergabung (tidak ada di UI)

-- ========================================
-- CEK STRUKTUR SEBELUM MIGRATION
-- ========================================

SELECT 'Struktur tabel jemaat SEBELUM migration:' AS info;
SHOW COLUMNS FROM jemaat;

-- ========================================
-- STEP: Drop Unused/Duplicate Columns
-- Jalankan satu per satu, abaikan error jika kolom tidak ada
-- ========================================

-- Drop no_telepon (duplikat dengan email)
ALTER TABLE jemaat DROP COLUMN IF EXISTS no_telepon;

-- Drop pekerjaan (duplikat dengan jenis_pekerjaan + detail_pekerjaan)
ALTER TABLE jemaat DROP COLUMN IF EXISTS pekerjaan;

-- Drop pendidikan (duplikat dengan pendidikan_terakhir)
ALTER TABLE jemaat DROP COLUMN IF EXISTS pendidikan;

-- Drop baptis_tanggal (duplikat dengan tanggal_babtis)
ALTER TABLE jemaat DROP COLUMN IF EXISTS baptis_tanggal;

-- Drop baptis_tempat (duplikat dengan tempat_babtis)
ALTER TABLE jemaat DROP COLUMN IF EXISTS baptis_tempat;

-- Drop komuni_tanggal (duplikat dengan tanggal_komuni)
ALTER TABLE jemaat DROP COLUMN IF EXISTS komuni_tanggal;

-- Drop komuni_tempat (duplikat dengan tempat_komuni)
ALTER TABLE jemaat DROP COLUMN IF EXISTS komuni_tempat;

-- Drop krisma_tanggal (duplikat dengan tanggal_krisma)
ALTER TABLE jemaat DROP COLUMN IF EXISTS krisma_tanggal;

-- Drop krisma_tempat (duplikat dengan tempat_krisma)
ALTER TABLE jemaat DROP COLUMN IF EXISTS krisma_tempat;

-- Drop nama_ayah (tidak ada di UI)
ALTER TABLE jemaat DROP COLUMN IF EXISTS nama_ayah;

-- Drop nama_ibu (tidak ada di UI)
ALTER TABLE jemaat DROP COLUMN IF EXISTS nama_ibu;

-- Drop lingkungan (duplikat dengan wilayah_rohani)
ALTER TABLE jemaat DROP COLUMN IF EXISTS lingkungan;

-- Drop wilayah (duplikat dengan wilayah_rohani)
ALTER TABLE jemaat DROP COLUMN IF EXISTS wilayah;

-- Drop keterangan (tidak ada di UI)
ALTER TABLE jemaat DROP COLUMN IF EXISTS keterangan;

-- Drop status_pernikahan (duplikat dengan status_menikah + status_perkawinan_detail)
ALTER TABLE jemaat DROP COLUMN IF EXISTS status_pernikahan;

-- Drop tanggal_bergabung (tidak ada di UI)
ALTER TABLE jemaat DROP COLUMN IF EXISTS tanggal_bergabung;

-- ========================================
-- VERIFIKASI HASIL
-- ========================================

SELECT 'Struktur tabel jemaat SETELAH migration:' AS info;
SHOW COLUMNS FROM jemaat;

SELECT 'Migration 21 selesai!' AS info;
SELECT 'Total 16 kolom tidak terpakai/duplikat telah dihapus' AS info;
SELECT 'Kolom created_at dan updated_at tetap dipertahankan' AS info;
