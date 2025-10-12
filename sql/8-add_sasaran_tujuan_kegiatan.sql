-- Migration 8: Add sasaran_kegiatan and tujuan_kegiatan columns to kegiatan_wr table
-- Date: 2025-01-07
-- Description: Menambahkan kolom Sasaran Kegiatan dan Tujuan Kegiatan pada tabel kegiatan_wr

USE `entf7819_db-client-server`;

-- Drop views first to avoid dependency issues
DROP VIEW IF EXISTS `v_kegiatan_wr_detail`;
DROP VIEW IF EXISTS `v_kegiatan_wr_mendatang`;

-- Check and add sasaran_kegiatan column if not exists
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = DATABASE()
    AND table_name = 'kegiatan_wr'
    AND column_name = 'sasaran_kegiatan'
);

SET @query = IF(@col_exists = 0,
    'ALTER TABLE kegiatan_wr ADD COLUMN sasaran_kegiatan TEXT NULL AFTER nama_kegiatan',
    'SELECT "Column sasaran_kegiatan already exists" AS msg'
);

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add tujuan_kegiatan column if not exists
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = DATABASE()
    AND table_name = 'kegiatan_wr'
    AND column_name = 'tujuan_kegiatan'
);

SET @query = IF(@col_exists = 0,
    'ALTER TABLE kegiatan_wr ADD COLUMN tujuan_kegiatan TEXT NULL AFTER sasaran_kegiatan',
    'SELECT "Column tujuan_kegiatan already exists" AS msg'
);

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Recreate view v_kegiatan_wr_detail with new columns
CREATE VIEW `v_kegiatan_wr_detail` AS
SELECT
    kw.id_kegiatan_wr,
    kw.kategori,
    kw.nama_kegiatan,
    kw.sasaran_kegiatan,
    kw.tujuan_kegiatan,
    kw.tempat_kegiatan,
    kw.tanggal_pelaksanaan,
    kw.tanggal_selesai,
    kw.waktu_mulai,
    kw.waktu_selesai,
    kw.penanggung_jawab,
    kw.status_kegiatan,
    kw.deskripsi,
    kw.keterangan,
    kw.user_id,
    p.username,
    p.nama_lengkap,
    p.peran,
    kw.created_at,
    kw.updated_at,
    DAYNAME(kw.tanggal_pelaksanaan) as nama_hari,
    DATEDIFF(kw.tanggal_pelaksanaan, CURDATE()) as hari_tersisa
FROM kegiatan_wr kw
LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
ORDER BY kw.tanggal_pelaksanaan DESC;

-- Recreate view v_kegiatan_wr_mendatang for upcoming activities
CREATE VIEW `v_kegiatan_wr_mendatang` AS
SELECT
    kw.id_kegiatan_wr,
    kw.kategori,
    kw.nama_kegiatan,
    kw.sasaran_kegiatan,
    kw.tujuan_kegiatan,
    kw.tempat_kegiatan,
    kw.tanggal_pelaksanaan,
    kw.tanggal_selesai,
    kw.waktu_mulai,
    kw.waktu_selesai,
    kw.penanggung_jawab,
    kw.status_kegiatan,
    kw.deskripsi,
    kw.user_id,
    p.username,
    p.nama_lengkap,
    DATEDIFF(kw.tanggal_pelaksanaan, CURDATE()) as hari_tersisa
FROM kegiatan_wr kw
LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
WHERE kw.tanggal_pelaksanaan >= CURDATE()
  AND kw.status_kegiatan IN ('Direncanakan', 'Berlangsung')
ORDER BY kw.tanggal_pelaksanaan ASC;

-- Show success message
SELECT 'Migration 8 completed successfully - sasaran_kegiatan and tujuan_kegiatan columns added' AS Status;
