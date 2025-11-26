-- Migration 17: Cleanup jemaat table - remove unused columns
-- Menghapus kolom yang tidak digunakan di UI tabel layout, mempertahankan yang digunakan

USE `entf7819_db-client-server`;

-- Kolom yang DIGUNAKAN di UI (berdasarkan tabel layout):
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
-- 15. email (email/no_hp digabung)
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
-- 29. kota_perkawinan (Kota)
-- 30. tanggal_perkawinan
-- 31. status_pernikahan (Status Perkawinan Detail)
-- 32. status_keanggotaan
-- 33. wr_tujuan
-- 34. paroki_tujuan
-- 35. created_by_pengguna (Created By Pengguna)
-- 36. created_at (TETAP DIPERTAHANKAN)
-- 37. updated_at (TETAP DIPERTAHANKAN)

-- Kolom yang TIDAK DIGUNAKAN di UI dan akan DIHAPUS:
-- - no_telepon (sudah ada email yang menampung email/no_hp)
-- - pekerjaan (sudah ada jenis_pekerjaan dan detail_pekerjaan)
-- - pendidikan (sudah ada pendidikan_terakhir)
-- - baptis_tanggal (sudah ada tanggal_babtis)
-- - baptis_tempat (sudah ada tempat_babtis)
-- - komuni_tanggal (sudah ada tanggal_komuni)
-- - komuni_tempat (sudah ada tempat_komuni)
-- - krisma_tanggal (sudah ada tanggal_krisma)
-- - krisma_tempat (sudah ada tempat_krisma)
-- - nama_ayah (tidak ada di UI)
-- - nama_ibu (tidak ada di UI)
-- - lingkungan (tidak ada di UI, sudah ada wilayah_rohani)
-- - wilayah (tidak ada di UI, sudah ada wilayah_rohani)
-- - keterangan (tidak ada di UI)
-- - tanggal_bergabung (tidak ada di UI)

-- ========================================
-- CEK STRUKTUR SEBELUM MIGRATION
-- ========================================

SELECT 'Struktur tabel jemaat SEBELUM migration:' AS info;
SHOW COLUMNS FROM jemaat;

-- ========================================
-- STEP: Drop Unused Columns
-- Jalankan satu per satu, abaikan error jika kolom tidak ada
-- ========================================

-- Drop no_telepon
ALTER TABLE jemaat DROP COLUMN no_telepon;

-- Drop pekerjaan
ALTER TABLE jemaat DROP COLUMN pekerjaan;

-- Drop pendidikan
ALTER TABLE jemaat DROP COLUMN pendidikan;

-- Drop baptis_tanggal
ALTER TABLE jemaat DROP COLUMN baptis_tanggal;

-- Drop baptis_tempat
ALTER TABLE jemaat DROP COLUMN baptis_tempat;

-- Drop komuni_tanggal
ALTER TABLE jemaat DROP COLUMN komuni_tanggal;

-- Drop komuni_tempat
ALTER TABLE jemaat DROP COLUMN komuni_tempat;

-- Drop krisma_tanggal
ALTER TABLE jemaat DROP COLUMN krisma_tanggal;

-- Drop krisma_tempat
ALTER TABLE jemaat DROP COLUMN krisma_tempat;

-- Drop nama_ayah
ALTER TABLE jemaat DROP COLUMN nama_ayah;

-- Drop nama_ibu
ALTER TABLE jemaat DROP COLUMN nama_ibu;

-- Drop lingkungan
ALTER TABLE jemaat DROP COLUMN lingkungan;

-- Drop wilayah
ALTER TABLE jemaat DROP COLUMN wilayah;

-- Drop keterangan
ALTER TABLE jemaat DROP COLUMN keterangan;

-- Drop tanggal_bergabung
ALTER TABLE jemaat DROP COLUMN tanggal_bergabung;

-- ========================================
-- VERIFIKASI HASIL
-- ========================================

SELECT 'Struktur tabel jemaat SETELAH migration:' AS info;
SHOW COLUMNS FROM jemaat;

SELECT 'Migration 17 selesai!' AS info;
SELECT 'Kolom yang DIPERTAHANKAN (termasuk created_at dan updated_at):' AS info;
