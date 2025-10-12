-- Migration: Create kegiatan_wr table for client/warga input
-- Date: 2025-01-07
-- Description: Tabel terpisah untuk kegiatan yang diinput oleh client/warga (WR)

-- Drop table if exists
DROP TABLE IF EXISTS `kegiatan_wr`;

-- Create kegiatan_wr table
CREATE TABLE `kegiatan_wr` (
  `id_kegiatan_wr` int(11) NOT NULL AUTO_INCREMENT,
  `kategori` enum('Misa','Doa','Sosial','Pendidikan','Ibadah','Katekese','Rohani','Administratif','Lainnya') NOT NULL DEFAULT 'Lainnya',
  `nama_kegiatan` varchar(200) NOT NULL,
  `tempat_kegiatan` varchar(200) NOT NULL,
  `tanggal_pelaksanaan` date NOT NULL,
  `tanggal_selesai` date DEFAULT NULL,
  `waktu_mulai` time NOT NULL,
  `waktu_selesai` time DEFAULT NULL,
  `penanggung_jawab` varchar(100) NOT NULL,
  `status_kegiatan` enum('Direncanakan','Berlangsung','Selesai','Dibatalkan') NOT NULL DEFAULT 'Direncanakan',
  `deskripsi` text DEFAULT NULL,
  `keterangan` text DEFAULT NULL,
  `user_id` int(11) NOT NULL COMMENT 'ID pengguna yang menginput kegiatan',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_kegiatan_wr`),
  KEY `idx_kegiatan_wr_user` (`user_id`),
  KEY `idx_kegiatan_wr_kategori` (`kategori`),
  KEY `idx_kegiatan_wr_tanggal` (`tanggal_pelaksanaan`),
  KEY `idx_kegiatan_wr_status` (`status_kegiatan`),
  CONSTRAINT `fk_kegiatan_wr_user` FOREIGN KEY (`user_id`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabel kegiatan yang diinput oleh client/warga (WR)';

-- Add index for performance
CREATE INDEX idx_kegiatan_wr_composite ON kegiatan_wr(user_id, tanggal_pelaksanaan DESC);

-- Insert sample data for testing
INSERT INTO `kegiatan_wr` (
  `kategori`,
  `nama_kegiatan`,
  `tempat_kegiatan`,
  `tanggal_pelaksanaan`,
  `tanggal_selesai`,
  `waktu_mulai`,
  `waktu_selesai`,
  `penanggung_jawab`,
  `status_kegiatan`,
  `deskripsi`,
  `keterangan`,
  `user_id`
) VALUES
(
  'Misa',
  'Misa Minggu Keluarga',
  'Gereja St. Paulus',
  '2025-01-12',
  '2025-01-12',
  '08:00:00',
  '10:00:00',
  'Romo Petrus',
  'Direncanakan',
  'Misa khusus untuk keluarga-keluarga di wilayah rohani',
  'Mohon kehadiran semua anggota keluarga',
  3
),
(
  'Doa',
  'Doa Rosario Harian',
  'Kapel Maria',
  '2025-01-13',
  '2025-01-13',
  '18:00:00',
  '19:00:00',
  'Ibu Maria',
  'Direncanakan',
  'Doa rosario rutin setiap hari Senin',
  'Terbuka untuk umum',
  3
),
(
  'Sosial',
  'Bakti Sosial Panti Asuhan',
  'Panti Asuhan Kasih',
  '2025-01-18',
  '2025-01-18',
  '09:00:00',
  '15:00:00',
  'Bapak Yohanes',
  'Direncanakan',
  'Kegiatan sosial membantu panti asuhan',
  'Membawa donasi pakaian dan makanan',
  6
);

-- Create view for easy access to kegiatan_wr with user information
CREATE OR REPLACE VIEW v_kegiatan_wr_detail AS
SELECT
  kw.id_kegiatan_wr,
  kw.kategori,
  kw.nama_kegiatan,
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
  p.email,
  p.peran,
  kw.created_at,
  kw.updated_at,
  -- Format tanggal dengan nama hari (dalam query)
  DAYNAME(kw.tanggal_pelaksanaan) as nama_hari,
  -- Hitung hari tersisa
  DATEDIFF(kw.tanggal_pelaksanaan, CURDATE()) as hari_tersisa
FROM kegiatan_wr kw
LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
ORDER BY kw.tanggal_pelaksanaan ASC;

-- Create view for upcoming kegiatan_wr
CREATE OR REPLACE VIEW v_kegiatan_wr_mendatang AS
SELECT
  kw.id_kegiatan_wr,
  kw.kategori,
  kw.nama_kegiatan,
  kw.tempat_kegiatan,
  kw.tanggal_pelaksanaan,
  kw.waktu_mulai,
  kw.waktu_selesai,
  kw.penanggung_jawab,
  kw.status_kegiatan,
  p.username,
  p.nama_lengkap,
  DATEDIFF(kw.tanggal_pelaksanaan, CURDATE()) as hari_tersisa
FROM kegiatan_wr kw
LEFT JOIN pengguna p ON kw.user_id = p.id_pengguna
WHERE kw.tanggal_pelaksanaan >= CURDATE()
  AND kw.status_kegiatan IN ('Direncanakan', 'Berlangsung')
ORDER BY kw.tanggal_pelaksanaan ASC
LIMIT 10;

-- Grant permissions (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON kegiatan_wr TO 'your_user'@'localhost';
-- GRANT SELECT ON v_kegiatan_wr_detail TO 'your_user'@'localhost';
-- GRANT SELECT ON v_kegiatan_wr_mendatang TO 'your_user'@'localhost';
