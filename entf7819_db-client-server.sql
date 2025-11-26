-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Nov 12, 2025 at 07:11 PM
-- Server version: 10.11.14-MariaDB-cll-lve
-- PHP Version: 8.4.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `entf7819_db-client-server`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id_admin` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `peran` enum('Admin','Operator','User') DEFAULT 'User',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id_admin`, `username`, `password`, `nama_lengkap`, `email`, `peran`, `is_active`, `created_at`, `updated_at`, `last_login`) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator Gereja', 'admin@gereja.com', 'Admin', 1, '2025-06-15 14:16:27', '2025-11-11 12:57:32', '2025-11-11 13:57:29'),
(2, 'asdf', '2413fb3709b05939f04cf2e92f7d0897fc2596f9ad0b8a9ea855c7bfebaae892', 'asdf', 'asdf@gmail.com', 'User', 1, '2025-09-30 13:22:10', '2025-09-30 14:10:52', '2025-09-30 14:10:52'),
(3, 'astry', '2413fb3709b05939f04cf2e92f7d0897fc2596f9ad0b8a9ea855c7bfebaae892', 'astry', 'astry@gmail.com', 'User', 1, '2025-10-29 15:28:14', '2025-10-29 15:29:06', '2025-10-29 16:29:09');

-- --------------------------------------------------------

--
-- Table structure for table `api_service_config`
--

CREATE TABLE `api_service_config` (
  `id_config` int(11) NOT NULL,
  `api_enabled` tinyint(1) DEFAULT 0,
  `last_enabled_by_admin` int(11) DEFAULT NULL,
  `last_enabled_by_pengguna` int(11) DEFAULT NULL,
  `last_modified` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `api_service_config`
--

INSERT INTO `api_service_config` (`id_config`, `api_enabled`, `last_enabled_by_admin`, `last_enabled_by_pengguna`, `last_modified`, `created_at`) VALUES
(1, 1, NULL, NULL, '2025-06-16 03:58:17', '2025-06-15 14:16:27');

-- --------------------------------------------------------

--
-- Table structure for table `aset`
--

CREATE TABLE `aset` (
  `id_aset` int(11) NOT NULL,
  `kode_aset` varchar(50) NOT NULL,
  `nama_aset` varchar(200) NOT NULL,
  `jenis_aset` varchar(50) NOT NULL,
  `kategori` varchar(50) NOT NULL,
  `merk_tipe` varchar(100) DEFAULT NULL,
  `tahun_perolehan` int(11) DEFAULT NULL,
  `sumber_perolehan` varchar(100) NOT NULL,
  `nilai` decimal(15,2) DEFAULT 0.00,
  `kondisi` varchar(50) NOT NULL,
  `lokasi` varchar(100) NOT NULL,
  `status` varchar(50) NOT NULL,
  `penanggung_jawab` varchar(100) DEFAULT NULL,
  `keterangan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `aset`
--

INSERT INTO `aset` (`id_aset`, `kode_aset`, `nama_aset`, `jenis_aset`, `kategori`, `merk_tipe`, `tahun_perolehan`, `sumber_perolehan`, `nilai`, `kondisi`, `lokasi`, `status`, `penanggung_jawab`, `keterangan`, `created_at`, `updated_at`) VALUES
(1, 'SFGH-12', 'SS', 'Bergerak', 'Tanah', 'SS', 2025, 'Pembelian', 2000000.00, 'Baik', 'Gereja Utama', 'Aktif', 'ASS', 'AAASS', '2025-11-05 08:07:40', '2025-11-05 08:07:40');

-- --------------------------------------------------------

--
-- Table structure for table `buku_kronik`
--

CREATE TABLE `buku_kronik` (
  `id_kronik` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `peristiwa` varchar(255) NOT NULL,
  `keterangan` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabel untuk pencatatan peristiwa/kejadian gereja';

-- --------------------------------------------------------

--
-- Table structure for table `client_connections`
--

CREATE TABLE `client_connections` (
  `id_connection` int(11) NOT NULL,
  `client_ip` varchar(45) NOT NULL,
  `hostname` varchar(100) DEFAULT NULL,
  `status` enum('Terhubung','Terputus') DEFAULT 'Terhubung',
  `connect_time` timestamp NULL DEFAULT current_timestamp(),
  `disconnect_time` timestamp NULL DEFAULT NULL,
  `last_activity` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `client_connections`
--

INSERT INTO `client_connections` (`id_connection`, `client_ip`, `hostname`, `status`, `connect_time`, `disconnect_time`, `last_activity`) VALUES
(76, '192.168.1.200', 'TEST-CLIENT-001', 'Terputus', '2025-11-04 14:12:21', '2025-11-04 14:14:25', '2025-11-04 14:14:25'),
(77, '192.168.1.210', 'WORKSTATION-CONTROL-TEST', 'Terputus', '2025-11-04 14:17:34', '2025-11-04 14:19:36', '2025-11-04 14:19:36'),
(78, '192.168.1.999', 'FINAL-VERIFY-CLIENT', 'Terputus', '2025-11-04 14:18:34', '2025-11-04 14:20:37', '2025-11-04 14:20:37'),
(79, '192.168.1.111', 'LIVE-TEST-CLIENT', 'Terputus', '2025-11-04 14:39:07', '2025-11-04 14:41:09', '2025-11-04 14:41:09'),
(80, '192.168.1.222', 'DEBUG-TEST-CLIENT', 'Terputus', '2025-11-04 14:41:50', '2025-11-04 14:44:03', '2025-11-04 14:44:03'),
(81, '10.1.3.172', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-05 07:42:04', '2025-11-05 07:44:10', '2025-11-05 07:44:10');

-- --------------------------------------------------------

--
-- Table structure for table `dokumen`
--

CREATE TABLE `dokumen` (
  `id_dokumen` int(11) NOT NULL,
  `nama_dokumen` varchar(200) NOT NULL,
  `ukuran_file` bigint(20) DEFAULT NULL,
  `tipe_file` varchar(50) DEFAULT NULL,
  `jenis_dokumen` enum('Administrasi','Keanggotaan','Keuangan','Liturgi','Legalitas') NOT NULL DEFAULT 'Administrasi',
  `file_path` varchar(500) NOT NULL DEFAULT '',
  `keterangan` text DEFAULT NULL,
  `uploaded_by_admin` int(11) DEFAULT NULL,
  `uploaded_by_pengguna` int(11) DEFAULT NULL,
  `uploaded_by_name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `dokumen`
--

INSERT INTO `dokumen` (`id_dokumen`, `nama_dokumen`, `ukuran_file`, `tipe_file`, `jenis_dokumen`, `file_path`, `keterangan`, `uploaded_by_admin`, `uploaded_by_pengguna`, `uploaded_by_name`, `created_at`, `updated_at`) VALUES
(3, 'Catatan Desain.pdf', 47678, NULL, 'Administrasi', '', '', NULL, NULL, NULL, '2025-09-29 14:37:25', '2025-10-21 19:37:19'),
(5, 'Bukti Pendaftaran_MAYDUPI ASTRI TURNIP_Optimasi Instagram dengan Insight.pdf', 412216, NULL, 'Administrasi', '', '', NULL, NULL, NULL, '2025-09-29 14:37:25', '2025-10-21 19:37:19'),
(7, 'Daftar_Jemaat_2025-03-19.xls', 1653, NULL, 'Administrasi', '', '', NULL, NULL, NULL, '2025-09-29 14:37:25', '2025-10-21 19:37:19'),
(9, 'PROMPT.docx', 15951, NULL, 'Administrasi', '', '', NULL, NULL, NULL, '2025-10-01 06:17:37', '2025-10-21 19:37:19'),
(11, 'DOW30.csv', 1247332, NULL, 'Keuangan', '', '', NULL, NULL, 'Administrator', '2025-10-19 15:55:04', '2025-10-21 19:37:19');

-- --------------------------------------------------------

--
-- Stand-in structure for view `files`
-- (See below for the actual view)
--
CREATE TABLE `files` (
);

-- --------------------------------------------------------

--
-- Table structure for table `jemaat`
--

CREATE TABLE `jemaat` (
  `id_jemaat` int(11) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `nik` varchar(20) DEFAULT NULL COMMENT 'Nomor Identitas Kependudukan',
  `nama_keluarga` varchar(100) DEFAULT NULL,
  `no_kk` varchar(20) DEFAULT NULL COMMENT 'Nomor Kartu Keluarga',
  `alamat` text DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `tempat_lahir` varchar(100) DEFAULT NULL,
  `umur` int(11) DEFAULT NULL,
  `status_kekatolikan` varchar(100) DEFAULT NULL,
  `kategori` varchar(50) DEFAULT NULL,
  `hubungan_keluarga` varchar(50) DEFAULT NULL,
  `jenis_kelamin` enum('Laki-laki','Perempuan') DEFAULT NULL,
  `status_menikah` varchar(50) DEFAULT NULL,
  `status_perkawinan` varchar(50) DEFAULT NULL,
  `keuskupan` varchar(100) DEFAULT NULL,
  `paroki` varchar(100) DEFAULT NULL,
  `kota_perkawinan` varchar(100) DEFAULT NULL,
  `tanggal_perkawinan` date DEFAULT NULL,
  `status_perkawinan_detail` varchar(100) DEFAULT NULL,
  `status_keanggotaan` varchar(50) DEFAULT 'Aktif',
  `wr_tujuan` varchar(100) DEFAULT NULL,
  `paroki_tujuan` varchar(100) DEFAULT NULL,
  `jenis_pekerjaan` varchar(100) DEFAULT NULL,
  `detail_pekerjaan` text DEFAULT NULL,
  `pendidikan_terakhir` varchar(100) DEFAULT NULL,
  `nama_babtis` varchar(100) DEFAULT NULL,
  `status_babtis` varchar(50) DEFAULT NULL,
  `status_ekaristi` varchar(50) DEFAULT NULL,
  `status_krisma` varchar(50) DEFAULT NULL,
  `wilayah_rohani` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by_pengguna` int(11) DEFAULT NULL,
  `tanggal_babtis` date DEFAULT NULL,
  `tempat_babtis` varchar(100) DEFAULT NULL,
  `tanggal_komuni` date DEFAULT NULL,
  `tempat_komuni` varchar(100) DEFAULT NULL,
  `tanggal_krisma` date DEFAULT NULL,
  `tempat_krisma` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `jemaat`
--

INSERT INTO `jemaat` (`id_jemaat`, `nama_lengkap`, `nik`, `nama_keluarga`, `no_kk`, `alamat`, `email`, `tanggal_lahir`, `tempat_lahir`, `umur`, `status_kekatolikan`, `kategori`, `hubungan_keluarga`, `jenis_kelamin`, `status_menikah`, `status_perkawinan`, `keuskupan`, `paroki`, `kota_perkawinan`, `tanggal_perkawinan`, `status_perkawinan_detail`, `status_keanggotaan`, `wr_tujuan`, `paroki_tujuan`, `jenis_pekerjaan`, `detail_pekerjaan`, `pendidikan_terakhir`, `nama_babtis`, `status_babtis`, `status_ekaristi`, `status_krisma`, `wilayah_rohani`, `created_at`, `updated_at`, `created_by_pengguna`, `tanggal_babtis`, `tempat_babtis`, `tanggal_komuni`, `tempat_komuni`, `tanggal_krisma`, `tempat_krisma`) VALUES
(12, 'Test User', NULL, 'Keluarga Test', NULL, 'Test Address', 'test@test.com', '2025-10-31', 'Jakarta', 34, NULL, 'KBK', 'Kepala Keluarga', 'Laki-laki', 'Sudah Menikah', '', '', '', '', '0000-00-00', NULL, 'Aktif', '', '', 'Bekerja', 'Programmer', 'S1', 'Test Baptis', 'Sudah', 'Sudah', 'Sudah', 'WR Test', '2025-10-01 03:49:57', '2025-10-31 01:40:58', 1, '1990-06-01', 'Gereja Test', '1998-06-01', 'Gereja Test', '2000-06-01', 'Gereja Test'),
(13, 'Test User', NULL, 'Keluarga Test', NULL, 'Test Address', 'test@test.com', '1990-01-01', 'Jakarta', 34, NULL, 'KBK', 'Kepala Keluarga', 'Laki-laki', 'Sudah Menikah', '', '', '', '', NULL, NULL, 'Aktif', '', '', 'Bekerja', 'Programmer', 'S1', 'Test Baptis', 'Sudah', 'Sudah', 'Sudah', 'WR Test', '2025-10-01 03:50:09', '2025-10-01 03:50:09', 1, '1990-06-01', 'Gereja Test', '1998-06-01', 'Gereja Test', '2000-06-01', 'Gereja Test'),
(20, 'ad', NULL, NULL, NULL, 'adf', NULL, '2025-10-31', NULL, NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Aktif', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-10-30 20:44:49', '2025-10-30 20:44:49', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 'ada', NULL, 'adaa', NULL, 'testt', NULL, '2011-01-01', 'adaa', NULL, NULL, NULL, NULL, 'Laki-laki', NULL, 'Belum', NULL, NULL, NULL, NULL, NULL, 'Aktif', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-10-30 20:58:00', '2025-10-30 21:47:37', 3, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 'test', NULL, NULL, NULL, NULL, NULL, '2011-11-11', NULL, NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Aktif', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-10-30 21:44:27', '2025-10-30 22:14:44', 3, NULL, NULL, NULL, NULL, NULL, NULL),
(23, 'ass', NULL, NULL, NULL, NULL, NULL, '2025-10-31', NULL, NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Aktif', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-10-30 22:16:12', '2025-10-30 22:16:12', 3, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 'ss', NULL, 'sss', NULL, 'sss', 'ss', '2025-11-05', 'ssss', NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, '2025-11-05', NULL, 'Pilih Status', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'ST. ALOYSIUS GONZAGA', '2025-11-05 07:16:18', '2025-11-05 07:17:56', 3, '2025-11-05', NULL, '2025-11-05', NULL, '2025-11-05', NULL),
(25, 'aa', NULL, NULL, NULL, NULL, NULL, '2025-11-05', NULL, NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Aktif', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-11-05 07:17:41', '2025-11-05 07:17:41', 3, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 'cccc', NULL, 'cccc', NULL, NULL, NULL, '2025-11-05', 'cccc', NULL, NULL, NULL, NULL, 'Laki-laki', NULL, NULL, NULL, NULL, NULL, '2025-11-05', NULL, 'Pilih Status', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'ST. YOHANES BAPTISTA DE LA SALLE', '2025-11-05 08:31:27', '2025-11-05 08:32:10', 3, '2025-11-05', NULL, '2025-11-05', NULL, '2025-11-05', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `kategorial`
--

CREATE TABLE `kategorial` (
  `id_kategorial` int(11) NOT NULL,
  `kelompok_kategorial` varchar(50) NOT NULL,
  `kelompok_kategorial_lainnya` varchar(100) DEFAULT NULL,
  `nama_lengkap` varchar(150) NOT NULL,
  `jenis_kelamin` varchar(50) DEFAULT NULL,
  `jabatan` varchar(100) DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `wilayah_rohani` varchar(100) DEFAULT NULL,
  `masa_jabatan` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Aktif',
  `foto_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `kategorial`
--

INSERT INTO `kategorial` (`id_kategorial`, `kelompok_kategorial`, `kelompok_kategorial_lainnya`, `nama_lengkap`, `jenis_kelamin`, `jabatan`, `no_hp`, `email`, `alamat`, `wilayah_rohani`, `masa_jabatan`, `status`, `foto_path`, `created_at`, `updated_at`) VALUES
(1, 'PPA', '', 'tess', '', 'tess', 'tess', 'tess', 'tess', 'ST. BLASIUS', '2025-2026', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_6200b6bd_20251105_130023.jpeg', '2025-11-05 06:00:26', '2025-11-05 06:38:11');

-- --------------------------------------------------------

--
-- Table structure for table `kegiatan`
--

CREATE TABLE `kegiatan` (
  `id_kegiatan` int(11) NOT NULL,
  `nama_kegiatan` varchar(200) NOT NULL,
  `lokasi` varchar(200) DEFAULT NULL,
  `tanggal_kegiatan` date DEFAULT NULL,
  `waktu_kegiatan` time DEFAULT NULL,
  `penanggung_jawab` varchar(100) DEFAULT NULL COMMENT 'Penanggung jawab kegiatan',
  `kategori` enum('Misa','Doa','Sosial','Pendidikan','Ibadah','Katekese','Rohani','Administratif','Lainnya') DEFAULT 'Lainnya',
  `status` enum('Direncanakan','Berlangsung','Selesai','Dibatalkan') DEFAULT 'Direncanakan',
  `biaya` decimal(10,2) DEFAULT 0.00,
  `keterangan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by_pengguna` int(11) DEFAULT NULL,
  `sasaran_kegiatan` text DEFAULT NULL COMMENT 'Sasaran/subjek kegiatan'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `kegiatan`
--

INSERT INTO `kegiatan` (`id_kegiatan`, `nama_kegiatan`, `lokasi`, `tanggal_kegiatan`, `waktu_kegiatan`, `penanggung_jawab`, `kategori`, `status`, `biaya`, `keterangan`, `created_at`, `updated_at`, `created_by_pengguna`, `sasaran_kegiatan`) VALUES
(16, 'sdch', 'xfcjg', '2025-10-07', NULL, 'dufigoh', 'Lainnya', 'Direncanakan', 0.00, NULL, '2025-10-06 19:11:54', '2025-10-06 19:11:54', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `kegiatan_wr`
--

CREATE TABLE `kegiatan_wr` (
  `id_kegiatan_wr` int(11) NOT NULL,
  `kategori` enum('Misa','Doa','Sosial','Pendidikan','Ibadah','Katekese','Rohani','Administratif','Lainnya') NOT NULL DEFAULT 'Lainnya',
  `nama_kegiatan` varchar(200) NOT NULL,
  `sasaran_kegiatan` text DEFAULT NULL,
  `tujuan_kegiatan` text DEFAULT NULL,
  `tempat_kegiatan` varchar(200) NOT NULL,
  `tanggal_pelaksanaan` date NOT NULL,
  `waktu_mulai` time NOT NULL,
  `penanggung_jawab` varchar(100) NOT NULL,
  `status_kegiatan` enum('Direncanakan','Berlangsung','Selesai','Dibatalkan') NOT NULL DEFAULT 'Direncanakan',
  `keterangan` text DEFAULT NULL,
  `user_id` int(11) NOT NULL COMMENT 'ID pengguna yang menginput kegiatan',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabel kegiatan yang diinput oleh client/warga (WR)';

--
-- Dumping data for table `kegiatan_wr`
--

INSERT INTO `kegiatan_wr` (`id_kegiatan_wr`, `kategori`, `nama_kegiatan`, `sasaran_kegiatan`, `tujuan_kegiatan`, `tempat_kegiatan`, `tanggal_pelaksanaan`, `waktu_mulai`, `penanggung_jawab`, `status_kegiatan`, `keterangan`, `user_id`, `created_at`, `updated_at`) VALUES
(4, 'Misa', 'ASF', 'ADV', 'ADVSGV', 'GSFG', '2025-10-07', '02:09:00', 'FSFGF', 'Direncanakan', '', 6, '2025-10-06 18:09:58', '2025-10-06 18:09:58'),
(5, 'Misa', '21err', 'getrnh', 'htn', 'ryhj', '2025-10-07', '03:14:00', 'yhj', 'Direncanakan', '', 6, '2025-10-06 19:14:26', '2025-10-06 19:14:26'),
(6, 'Misa', 'adfd', 'adfa', 'aeg', 'aegr', '2025-10-09', '00:20:00', 'aegr', 'Direncanakan', '', 3, '2025-10-08 16:20:35', '2025-10-08 16:20:35'),
(7, 'Doa', 'aa', 'aa', 'aaa', 'aa', '2025-10-30', '16:29:00', 'aa', 'Direncanakan', 'aa', 3, '2025-10-30 08:29:22', '2025-10-30 08:29:22'),
(8, 'Misa', 'tess', 'tess', 'tess', 'tess', '2025-11-05', '13:53:00', 'tess', 'Direncanakan', 'tess', 3, '2025-11-05 05:53:57', '2025-11-05 05:53:57');

-- --------------------------------------------------------

--
-- Table structure for table `keuangan`
--

CREATE TABLE `keuangan` (
  `id_keuangan` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `kategori` enum('Pemasukan','Pengeluaran') NOT NULL,
  `sub_kategori` varchar(100) DEFAULT NULL,
  `jumlah` decimal(10,2) NOT NULL,
  `keterangan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by_pengguna` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `keuangan`
--

INSERT INTO `keuangan` (`id_keuangan`, `tanggal`, `kategori`, `sub_kategori`, `jumlah`, `keterangan`, `created_at`, `updated_at`, `created_by_pengguna`) VALUES
(15, '2025-10-05', 'Pemasukan', 'Kolekte', 1000000.00, 'passs', '2025-10-05 14:22:09', '2025-10-05 14:22:09', 6),
(16, '2025-10-05', 'Pengeluaran', 'Donasi', 200000.00, 'sosial', '2025-10-05 14:29:20', '2025-10-05 14:29:20', 6),
(18, '2025-10-06', 'Pemasukan', 'Operasional', 500000.00, 'asdfff', '2025-10-05 20:12:30', '2025-10-05 20:12:30', 3),
(19, '2025-10-06', 'Pemasukan', 'Kolekte', 250000.00, 'asdf', '2025-10-06 15:26:41', '2025-10-06 15:26:41', 6),
(23, '2025-10-30', 'Pengeluaran', 'Donasi', 100000.00, 'donasi pemabngunan', '2025-10-30 06:57:47', '2025-10-30 06:57:47', 3),
(28, '2025-11-05', 'Pemasukan', 'Kolekte', 100000.00, '', '2025-11-05 08:04:49', '2025-11-05 08:04:49', 3);

-- --------------------------------------------------------

--
-- Table structure for table `keuangan_kategorial`
--

CREATE TABLE `keuangan_kategorial` (
  `id_keuangan_kategorial` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `jenis` enum('Pemasukan','Pengeluaran') NOT NULL,
  `kategori` varchar(100) NOT NULL,
  `keterangan` text DEFAULT NULL,
  `jumlah` decimal(15,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by_admin` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `k_binaan`
--

CREATE TABLE `k_binaan` (
  `id_binaan` int(11) NOT NULL,
  `kelompok_binaan` varchar(100) NOT NULL,
  `kelompok_binaan_lainnya` varchar(100) DEFAULT NULL,
  `nama_lengkap` varchar(150) NOT NULL,
  `jenis_kelamin` varchar(50) DEFAULT NULL,
  `jabatan` varchar(100) DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `wilayah_rohani` varchar(100) DEFAULT NULL,
  `masa_jabatan` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Aktif',
  `foto_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `k_binaan`
--

INSERT INTO `k_binaan` (`id_binaan`, `kelompok_binaan`, `kelompok_binaan_lainnya`, `nama_lengkap`, `jenis_kelamin`, `jabatan`, `no_hp`, `email`, `alamat`, `wilayah_rohani`, `masa_jabatan`, `status`, `foto_path`, `created_at`, `updated_at`) VALUES
(1, 'Perkawinan', '', 'tess', 'Perempuan', '', '', '', '', 'ST. CORNELIUS', '1234', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_a523585d_20251105_133727.jpg', '2025-11-05 06:37:43', '2025-11-05 06:37:43');

-- --------------------------------------------------------

--
-- Stand-in structure for view `log_activities`
-- (See below for the actual view)
--
CREATE TABLE `log_activities` (
`id_log` int(11)
,`id_admin` int(11)
,`aktivitas` varchar(200)
,`detail` text
,`ip_address` varchar(45)
,`timestamp` timestamp
);

-- --------------------------------------------------------

--
-- Table structure for table `log_aktivitas`
--

CREATE TABLE `log_aktivitas` (
  `id_log` int(11) NOT NULL,
  `id_admin` int(11) DEFAULT NULL,
  `id_pengguna` int(11) DEFAULT NULL,
  `aktivitas` varchar(200) NOT NULL,
  `detail` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `log_aktivitas`
--

INSERT INTO `log_aktivitas` (`id_log`, `id_admin`, `id_pengguna`, `aktivitas`, `detail`, `ip_address`, `timestamp`) VALUES
(1, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 14:58:18'),
(2, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 14:58:34'),
(3, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 15:07:22'),
(4, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:07:33'),
(5, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:10:58'),
(6, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 15:14:12'),
(7, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:14:23'),
(8, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:22:23'),
(9, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 15:22:29'),
(10, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:23:54'),
(11, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 15:26:04'),
(12, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:26:15'),
(13, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 15:44:14'),
(14, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:44:27'),
(15, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:50:40'),
(16, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:52:41'),
(17, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 15:55:21'),
(18, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 16:02:48'),
(19, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 16:03:21'),
(20, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 16:03:31'),
(21, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 16:06:02'),
(22, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 16:06:13'),
(23, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-29 16:06:24'),
(24, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 16:16:17'),
(25, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-29 16:25:06'),
(26, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-30 05:05:04'),
(27, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-30 05:06:38'),
(28, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-30 05:33:26'),
(29, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-30 13:21:47'),
(30, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-30 14:48:03'),
(31, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-09-30 15:00:49'),
(32, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-09-30 15:57:34'),
(33, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-01 01:34:37'),
(34, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-01 01:35:40'),
(35, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-01 01:38:07'),
(36, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-01 01:38:20'),
(37, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-01 03:28:09'),
(38, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-01 04:00:13'),
(39, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-01 04:01:05'),
(40, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-01 05:04:19'),
(41, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-03 15:52:26'),
(42, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-03 16:31:11'),
(43, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-03 18:38:44'),
(44, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-03 18:41:23'),
(45, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-03 18:50:05'),
(46, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 14:18:13'),
(47, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-05 14:25:41'),
(48, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 14:26:24'),
(49, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 15:37:00'),
(50, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 19:54:44'),
(51, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 20:10:11'),
(52, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-05 21:07:28'),
(53, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-05 21:48:00'),
(54, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 11:47:14'),
(55, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-06 12:05:28'),
(56, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 15:15:13'),
(57, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 16:06:04'),
(58, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 16:49:05'),
(59, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 18:19:40'),
(60, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 18:24:28'),
(61, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 18:41:15'),
(62, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 18:50:52'),
(63, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 19:11:02'),
(64, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-06 19:20:39'),
(65, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-06 19:20:59'),
(66, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-06 19:22:22'),
(67, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 16:15:33'),
(68, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 16:48:40'),
(69, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 17:00:52'),
(70, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 17:22:26'),
(71, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-08 17:32:34'),
(72, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 17:32:57'),
(73, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 17:43:29'),
(74, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 17:56:30'),
(75, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 18:07:10'),
(76, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 18:17:14'),
(77, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-08 18:42:16'),
(78, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 18:42:40'),
(79, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 18:46:39'),
(80, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-08 19:09:20'),
(81, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-08 19:10:37'),
(82, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 03:48:36'),
(83, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-09 04:53:23'),
(84, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 04:53:49'),
(85, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 15:11:23'),
(86, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 15:58:36'),
(87, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 16:26:09'),
(88, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-09 16:33:09'),
(89, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 16:33:53'),
(90, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 16:42:59'),
(91, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 16:58:08'),
(92, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-09 17:23:08'),
(93, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 17:23:35'),
(94, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 17:47:23'),
(95, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-09 17:53:42'),
(96, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 17:54:08'),
(97, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 18:24:18'),
(98, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 18:36:18'),
(99, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 18:47:00'),
(100, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-09 18:49:46'),
(101, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-09 19:07:01'),
(102, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 12:34:32'),
(103, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 12:58:50'),
(104, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-12 13:10:10'),
(105, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 14:22:50'),
(106, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 14:35:15'),
(107, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 14:45:20'),
(108, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 15:21:50'),
(109, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 16:23:59'),
(110, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 17:50:50'),
(111, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-12 18:05:03'),
(112, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-12 18:05:34'),
(113, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 14:37:35'),
(114, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 15:58:33'),
(115, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 16:13:14'),
(116, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 16:32:23'),
(117, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 16:48:12'),
(118, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-13 16:57:48'),
(119, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-19 12:45:34'),
(120, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-19 13:15:10'),
(121, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-19 18:09:01'),
(122, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-19 18:33:27'),
(123, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-19 18:40:43'),
(124, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-19 18:42:49'),
(125, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 14:43:58'),
(126, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-20 14:54:18'),
(127, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 14:56:04'),
(128, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 15:38:59'),
(129, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 15:52:59'),
(130, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 15:56:14'),
(131, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 16:18:42'),
(132, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 17:11:20'),
(133, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 17:37:44'),
(134, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-20 17:44:15'),
(135, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-21 17:13:44'),
(136, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-21 18:16:29'),
(137, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-21 19:04:42'),
(138, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-21 19:05:39'),
(139, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-21 20:01:12'),
(140, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-21 20:24:29'),
(141, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 10:58:19'),
(142, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 11:17:56'),
(143, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 12:51:27'),
(144, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 15:15:02'),
(145, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 16:21:58'),
(146, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 16:27:03'),
(147, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 18:33:03'),
(148, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 18:54:13'),
(149, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 18:54:40'),
(150, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 19:22:16'),
(151, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 19:23:15'),
(152, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 19:29:57'),
(153, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 19:31:12'),
(154, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 19:46:44'),
(155, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-23 19:47:24'),
(156, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-23 19:54:22'),
(157, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 12:39:06'),
(158, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 13:48:12'),
(159, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 15:18:37'),
(160, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-10-29 15:28:28'),
(161, 3, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 15:29:15'),
(162, 3, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-29 17:10:26'),
(163, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 17:29:20'),
(164, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 17:45:18'),
(165, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 19:41:00'),
(166, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-29 20:05:36'),
(167, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-30 06:35:15'),
(168, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-30 07:54:58'),
(169, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-30 19:52:02'),
(170, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-31 00:28:19'),
(171, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-31 02:39:30'),
(172, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-31 13:51:11'),
(173, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-10-31 14:02:28'),
(174, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-10-31 14:46:49'),
(175, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-02 16:21:37'),
(176, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-02 16:41:48'),
(177, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 13:19:05'),
(178, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-04 13:33:49'),
(179, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 13:34:18'),
(180, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 13:50:32'),
(181, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 14:06:02'),
(182, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 14:23:05'),
(183, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 14:49:02'),
(184, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-04 15:07:58'),
(185, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 03:50:01'),
(186, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 04:36:48'),
(187, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 05:47:33'),
(188, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 05:55:05'),
(189, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 06:27:02'),
(190, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 06:33:33'),
(191, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 06:55:58'),
(192, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 07:22:06'),
(193, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 07:34:53'),
(194, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 07:42:46'),
(195, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-05 07:51:02'),
(196, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 07:53:17'),
(197, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 08:06:40'),
(198, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 08:30:48'),
(199, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-05 10:08:43'),
(200, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-05 11:35:20'),
(201, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-06 05:55:44'),
(202, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-06 06:13:40'),
(203, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-07 13:29:19'),
(204, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-07 13:51:42'),
(205, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-07 14:30:11'),
(206, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-07 15:16:41'),
(207, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-07 15:17:21'),
(208, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-07 15:51:11'),
(209, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-08 10:13:56'),
(210, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-11 12:24:44'),
(211, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-11 12:59:12');

-- --------------------------------------------------------

--
-- Table structure for table `pengguna`
--

CREATE TABLE `pengguna` (
  `id_pengguna` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `peran` enum('operator','user') DEFAULT 'user',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `pengguna`
--

INSERT INTO `pengguna` (`id_pengguna`, `username`, `password`, `nama_lengkap`, `email`, `peran`, `is_active`, `created_at`, `updated_at`, `last_login`) VALUES
(3, 'asdf', '2413fb3709b05939f04cf2e92f7d0897fc2596f9ad0b8a9ea855c7bfebaae892', 'asdf', 'asdf@gmail.com', 'user', 1, '2025-09-30 14:17:39', '2025-11-08 07:01:32', '2025-11-08 07:01:32'),
(5, 'qwer', '70f98078fb2c7d7bfb3ae17330b91eaa018110b03896979b4c88bfaed3805906', 'qwer', 'qwer@gmail.com', 'user', 1, '2025-10-01 01:40:51', '2025-11-04 13:00:56', '2025-11-04 13:00:56'),
(6, 'user', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'user client', 'user@gmail.com', 'user', 1, '2025-10-01 05:19:54', '2025-10-06 19:15:33', '2025-10-06 19:15:33');

-- --------------------------------------------------------

--
-- Table structure for table `pengumuman`
--

CREATE TABLE `pengumuman` (
  `id_pengumuman` int(11) NOT NULL,
  `judul` varchar(200) NOT NULL,
  `isi` text NOT NULL,
  `sasaran` varchar(100) NOT NULL DEFAULT 'Umum',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `pembuat` varchar(100) NOT NULL DEFAULT 'Administrator',
  `penanggung_jawab` varchar(100) NOT NULL DEFAULT 'Administrator',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `pengumuman`
--

INSERT INTO `pengumuman` (`id_pengumuman`, `judul`, `isi`, `sasaran`, `is_active`, `pembuat`, `penanggung_jawab`, `created_at`, `updated_at`) VALUES
(9, 'asxa', 'safcdf', 'Umum', 1, 'admin', 'SAYAA', '2025-10-08 17:59:58', '2025-10-09 16:38:22'),
(20, 'AQSWSWD', 'WDXDSDAS\nASDXSD : ASD\nDSCD :ASDA', 'OMK', 1, 'Administrator', 'sAYA', '2025-10-09 16:37:50', '2025-10-09 16:37:50'),
(21, 'sawdefv', 'wvsebgrhnmky,', 'Umum', 1, 'Administrator', 'asdasdcd', '2025-10-09 16:44:21', '2025-10-09 16:44:21'),
(23, 'Test Pengumuman Baru', 'Ini adalah tes pengumuman untuk validasi struktur database baru. Tanggal otomatis dari created_at.', 'Umum', 1, 'Administrator', 'Bapak Pendeta', '2025-10-09 17:03:30', '2025-10-09 17:03:30'),
(26, 'fdsaesrdf', 'Syalom, Umat Terkasih!\nMari bersama-sama merawat rumah Tuhan kita. Kami mengundang seluruh jemaat untuk ikut dalam kegiatan Gotong Royong pada:\n\nHari/Tanggal	: Sabtu, 18 Oktober 2025 \nWaktu	: 08:00 Pagi - Selesai \nTempat	: Lingkungan Gereja\n\nKehadiran Saudara/i adalah berkat bagi kita semua. Tuhan memberkati!', 'Umum', 1, 'Administrator', 'asdfghj', '2025-10-09 17:34:29', '2025-10-31 14:14:02');

-- --------------------------------------------------------

--
-- Table structure for table `program_kerja`
--

CREATE TABLE `program_kerja` (
  `id_program_kerja` int(11) NOT NULL,
  `estimasi_waktu` varchar(20) DEFAULT '',
  `judul` varchar(200) NOT NULL,
  `sasaran` varchar(200) DEFAULT '',
  `penanggung_jawab` varchar(100) DEFAULT '',
  `anggaran` varchar(50) DEFAULT '',
  `sumber_anggaran` varchar(100) DEFAULT 'Kas Gereja',
  `kategori` varchar(100) DEFAULT '',
  `keterangan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabel untuk manajemen program kerja tahunan';

--
-- Dumping data for table `program_kerja`
--

INSERT INTO `program_kerja` (`id_program_kerja`, `estimasi_waktu`, `judul`, `sasaran`, `penanggung_jawab`, `anggaran`, `sumber_anggaran`, `kategori`, `keterangan`, `created_at`, `updated_at`) VALUES
(2, '2025-09-30', 'asdf', 'asdfasdfasdf', 'asdf', '123', 'Kas Gereja', '', '', '2025-09-30 05:05:18', '2025-09-30 05:05:35'),
(3, '2025-10-01', 'rosario', 'Umat', 'umat', '2000000', 'Kas Gereja', '', '', '2025-10-01 06:10:30', '2025-10-01 06:10:30'),
(4, '2025-10-07', 'ghbj', 'hjnk', 'ghb', 'fgvb', 'Kas Gereja', '', '', '2025-10-06 18:51:52', '2025-10-06 18:51:52');

-- --------------------------------------------------------

--
-- Table structure for table `program_kerja_k_kategorial`
--

CREATE TABLE `program_kerja_k_kategorial` (
  `id_program_kerja_k_kategorial` int(11) NOT NULL,
  `program_kerja` varchar(255) NOT NULL COMMENT 'Nama program kerja',
  `subyek_sasaran` varchar(255) NOT NULL COMMENT 'Subyek/sasaran program',
  `indikator_pencapaian` text DEFAULT NULL COMMENT 'Indikator pencapaian program',
  `model_bentuk_metode` text DEFAULT NULL COMMENT 'Model, bentuk dan metode pelaksanaan',
  `materi` varchar(255) DEFAULT NULL COMMENT 'Materi yang akan disampaikan',
  `tempat` varchar(255) DEFAULT NULL COMMENT 'Lokasi pelaksanaan program',
  `waktu` varchar(100) DEFAULT NULL COMMENT 'Waktu pelaksanaan (tanggal/bulan/jam)',
  `pic` varchar(100) DEFAULT NULL COMMENT 'Person In Charge (Penanggung Jawab)',
  `perincian` text DEFAULT NULL COMMENT 'Perincian detail program',
  `quantity` int(11) DEFAULT NULL COMMENT 'Jumlah/quantity',
  `satuan` varchar(50) DEFAULT NULL COMMENT 'Satuan (orang, paket, set, dll)',
  `harga_satuan` decimal(15,2) DEFAULT 0.00 COMMENT 'Harga per satuan (Rp)',
  `frekuensi` int(11) DEFAULT 1 COMMENT 'Frekuensi pelaksanaan',
  `jumlah` decimal(15,2) DEFAULT 0.00 COMMENT 'Jumlah total (quantity x frekuensi)',
  `total` decimal(15,2) DEFAULT 0.00 COMMENT 'Total biaya (jumlah x harga_satuan)',
  `keterangan` text DEFAULT NULL COMMENT 'Keterangan tambahan',
  `created_by` int(11) DEFAULT NULL COMMENT 'User/Admin ID yang membuat',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja K. Kategorial (Kategorial Church Programs)';

-- --------------------------------------------------------

--
-- Table structure for table `program_kerja_k_kategorial_budget`
--

CREATE TABLE `program_kerja_k_kategorial_budget` (
  `id_budget` int(11) NOT NULL,
  `id_program_kerja_k_kategorial` int(11) NOT NULL,
  `sumber_anggaran` varchar(100) NOT NULL COMMENT 'Sumber anggaran: KK (Komisi), WR (Wilayah Rohani), Paroki, Swadaya, Lainnya',
  `sumber_anggaran_lainnya` varchar(255) DEFAULT NULL COMMENT 'Keterangan jika sumber anggaran adalah Lainnya',
  `jumlah_anggaran` decimal(15,2) NOT NULL COMMENT 'Jumlah anggaran dari sumber ini',
  `nama_akun_pengeluaran` varchar(255) DEFAULT NULL COMMENT 'Nama akun pengeluaran',
  `sumber_pembiayaan` varchar(255) DEFAULT NULL COMMENT 'Sumber pembiayaan',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Budget sources for K. Kategorial programs';

-- --------------------------------------------------------

--
-- Table structure for table `program_kerja_k_kategorial_evaluation`
--

CREATE TABLE `program_kerja_k_kategorial_evaluation` (
  `id_evaluation` int(11) NOT NULL,
  `id_program_kerja_k_kategorial` int(11) NOT NULL,
  `evaluasi_program` varchar(50) DEFAULT NULL COMMENT 'Hasil evaluasi: <50%, 50-69%, 70-84%, 85-100%, Risiko',
  `status` varchar(50) DEFAULT 'Direncanakan' COMMENT 'Status program: Direncanakan, Berlangsung, Selesai, Dibatalkan',
  `tindak_lanjut` text DEFAULT NULL COMMENT 'Tindak lanjut dari evaluasi',
  `keterangan_evaluasi` text DEFAULT NULL COMMENT 'Keterangan evaluasi',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Evaluation data for K. Kategorial programs';

-- --------------------------------------------------------

--
-- Table structure for table `program_kerja_wr`
--

CREATE TABLE `program_kerja_wr` (
  `id_program_kerja_wr` int(11) NOT NULL,
  `kategori` varchar(100) NOT NULL COMMENT 'Kategori program: Ibadah, Doa, Katekese, Sosial, Rohani, Administratif, Perayaan, Lainnya',
  `estimasi_waktu` varchar(50) NOT NULL COMMENT 'Bulan estimasi: Januari-Desember',
  `judul` varchar(255) NOT NULL COMMENT 'Judul/nama program kerja',
  `sasaran` varchar(255) DEFAULT NULL COMMENT 'Target/sasaran program atau tokoh yang dituju',
  `penanggung_jawab` varchar(100) DEFAULT NULL COMMENT 'PIC (Person In Charge)',
  `anggaran` decimal(15,2) DEFAULT 0.00 COMMENT 'Jumlah anggaran dalam Rp',
  `sumber_anggaran` varchar(100) DEFAULT NULL COMMENT 'Sumber anggaran: Kas Gereja, Donasi Jemaat, Sponsor External, Dana Komisi, APBG, Kolekte Khusus, Lainnya',
  `keterangan` text DEFAULT NULL COMMENT 'Keterangan/deskripsi lengkap program kerja',
  `wilayah_rohani_id` int(11) DEFAULT NULL COMMENT 'ID Wilayah Rohani (Pastoral Area) yang melaporkan program',
  `reported_by` int(11) DEFAULT NULL COMMENT 'User ID WR yang melaporkan',
  `status` varchar(50) DEFAULT 'Direncanakan' COMMENT 'Status: Direncanakan, Berlangsung, Selesai, Dibatalkan',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja WR (Pastoral Area Work Programs)';

-- --------------------------------------------------------

--
-- Table structure for table `struktur`
--

CREATE TABLE `struktur` (
  `id_struktur` int(11) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `jenis_kelamin` varchar(20) DEFAULT NULL CHECK (`jenis_kelamin` in ('Laki-laki','Perempuan')),
  `wilayah_rohani` varchar(100) DEFAULT NULL,
  `jabatan_utama` varchar(100) NOT NULL,
  `status_aktif` varchar(50) DEFAULT 'Aktif' CHECK (`status_aktif` in ('Aktif','Tidak Aktif','Cuti')),
  `email` varchar(100) DEFAULT NULL,
  `telepon` varchar(20) DEFAULT NULL,
  `foto_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `periode` varchar(9) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `struktur`
--

INSERT INTO `struktur` (`id_struktur`, `nama_lengkap`, `jenis_kelamin`, `wilayah_rohani`, `jabatan_utama`, `status_aktif`, `email`, `telepon`, `foto_path`, `created_at`, `updated_at`, `periode`) VALUES
(1, 'Romo Andreas Simatupang', NULL, 'None', 'Pastor Paroki', 'Aktif', 'pastor@gereja.com', '081234567890', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_d0019fe5_20250929_225104.jpg', '2025-09-29 14:59:49', '2025-09-29 15:51:07', NULL),
(2, 'Test Admin', NULL, 'Wilayah Santo Yusuf', 'Pastor Paroki', 'Aktif', 'test@gereja.com', '081234567890', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_9d2906ab_20250929_231409.jpg', '2025-09-29 15:07:04', '2025-09-29 16:14:14', NULL),
(4, 'maydupi', NULL, 'May', 'May', 'Aktif', 'may@gmail.com', '05784564586', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_87c16c00_20250929_224441.jpg', '2025-09-29 15:15:36', '2025-09-29 15:44:44', NULL),
(6, 'saya', 'Laki-laki', 'WR1', 'Sekrtaris', 'Aktif', '', '', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_aee48c1d_20251020_011201.jpg', '2025-10-19 18:12:05', '2025-10-19 18:12:05', '2025-2027'),
(7, 'Lukas', 'Laki-laki', 'ST. Maria', 'Koordinator', 'Aktif', 'lukas@gmail.com', '08787654321', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_8af53fab_20251105_125727.jpg', '2025-11-05 05:57:31', '2025-11-05 06:38:50', '20252-207');

-- --------------------------------------------------------

--
-- Table structure for table `tim_pembina`
--

CREATE TABLE `tim_pembina` (
  `id_tim_pembina` int(11) NOT NULL,
  `tim_pembina` varchar(100) NOT NULL,
  `tanggal_pelantikan` date DEFAULT NULL,
  `keterangan` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `tim_pembina_lainnya` varchar(100) DEFAULT NULL COMMENT 'Custom tim pembina value ketika user memilih Lainnya dari dropdown'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tim_pembina`
--

INSERT INTO `tim_pembina` (`id_tim_pembina`, `tim_pembina`, `tanggal_pelantikan`, `keterangan`, `created_at`, `updated_at`, `tim_pembina_lainnya`) VALUES
(1, 'Liturgi', '2025-11-07', '', '2025-11-07 15:29:27', '2025-11-07 15:29:27', NULL),
(2, 'Lainnya', '2025-11-07', 'tesss', '2025-11-07 15:30:06', '2025-11-07 15:30:06', 'tesss');

-- --------------------------------------------------------

--
-- Table structure for table `tim_pembina_peserta`
--

CREATE TABLE `tim_pembina_peserta` (
  `id_peserta` int(11) NOT NULL,
  `id_tim_pembina` int(11) NOT NULL,
  `id_jemaat` int(11) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `wilayah_rohani` varchar(100) NOT NULL,
  `jabatan` varchar(50) NOT NULL,
  `koordinator_bidang` varchar(100) DEFAULT NULL COMMENT 'Filled when jabatan=Koordinator',
  `sie_bidang` varchar(100) DEFAULT NULL COMMENT 'Filled when jabatan=Anggota Sie',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Stand-in structure for view `user_sessions`
-- (See below for the actual view)
--
CREATE TABLE `user_sessions` (
`session_id` varchar(19)
,`client_ip` varchar(45)
,`hostname` varchar(100)
,`user_id` binary(0)
,`connect_time` timestamp
,`last_activity` timestamp
,`status` varchar(12)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_active_clients`
-- (See below for the actual view)
--
CREATE TABLE `v_active_clients` (
`client_ip` varchar(45)
,`hostname` varchar(100)
,`connect_time` timestamp
,`last_activity` timestamp
,`minutes_inactive` bigint(21)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_current_server_status`
-- (See below for the actual view)
--
CREATE TABLE `v_current_server_status` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_kegiatan_mendatang`
-- (See below for the actual view)
--
CREATE TABLE `v_kegiatan_mendatang` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_kegiatan_wr_detail`
-- (See below for the actual view)
--
CREATE TABLE `v_kegiatan_wr_detail` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_kegiatan_wr_mendatang`
-- (See below for the actual view)
--
CREATE TABLE `v_kegiatan_wr_mendatang` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_laporan_keuangan_bulanan`
-- (See below for the actual view)
--
CREATE TABLE `v_laporan_keuangan_bulanan` (
`tahun` int(5)
,`bulan` int(3)
,`kategori` enum('Pemasukan','Pengeluaran')
,`total` decimal(32,2)
,`jumlah_transaksi` bigint(21)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_pengumuman_aktif`
-- (See below for the actual view)
--
CREATE TABLE `v_pengumuman_aktif` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_statistik_jemaat`
-- (See below for the actual view)
--
CREATE TABLE `v_statistik_jemaat` (
);

-- --------------------------------------------------------

--
-- Table structure for table `wilayah_rohani`
--

CREATE TABLE `wilayah_rohani` (
  `id_wilayah` int(11) NOT NULL,
  `wilayah_rohani` varchar(100) NOT NULL,
  `nama_lengkap` varchar(150) NOT NULL,
  `jenis_kelamin` varchar(50) DEFAULT NULL,
  `jabatan` varchar(100) DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `masa_jabatan` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Aktif',
  `foto_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `wilayah_rohani`
--

INSERT INTO `wilayah_rohani` (`id_wilayah`, `wilayah_rohani`, `nama_lengkap`, `jenis_kelamin`, `jabatan`, `no_hp`, `email`, `alamat`, `masa_jabatan`, `status`, `foto_path`, `created_at`, `updated_at`) VALUES
(1, 'ST. YOHANES BAPTISTA DE LA SALLE', 'Maria', 'Perempuan', 'Bendahara', '23456789', '', 'tesssfv', '2025-2027', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_8691bd30_20251105_125838.jpg', '2025-11-05 05:58:42', '2025-11-05 06:38:29');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id_admin`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_admin_username` (`username`);

--
-- Indexes for table `api_service_config`
--
ALTER TABLE `api_service_config`
  ADD PRIMARY KEY (`id_config`),
  ADD KEY `last_enabled_by_admin` (`last_enabled_by_admin`),
  ADD KEY `last_enabled_by_pengguna` (`last_enabled_by_pengguna`);

--
-- Indexes for table `aset`
--
ALTER TABLE `aset`
  ADD PRIMARY KEY (`id_aset`),
  ADD UNIQUE KEY `kode_aset` (`kode_aset`);

--
-- Indexes for table `buku_kronik`
--
ALTER TABLE `buku_kronik`
  ADD PRIMARY KEY (`id_kronik`),
  ADD KEY `idx_tanggal` (`tanggal`),
  ADD KEY `idx_created_by` (`created_by`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `client_connections`
--
ALTER TABLE `client_connections`
  ADD PRIMARY KEY (`id_connection`),
  ADD KEY `idx_client_ip` (`client_ip`),
  ADD KEY `idx_client_status` (`status`);

--
-- Indexes for table `dokumen`
--
ALTER TABLE `dokumen`
  ADD PRIMARY KEY (`id_dokumen`),
  ADD KEY `fk_dokumen_pengguna` (`uploaded_by_pengguna`);

--
-- Indexes for table `jemaat`
--
ALTER TABLE `jemaat`
  ADD PRIMARY KEY (`id_jemaat`),
  ADD KEY `idx_jemaat_nama` (`nama_lengkap`),
  ADD KEY `idx_jemaat_wilayah_rohani` (`wilayah_rohani`),
  ADD KEY `idx_jemaat_status_keanggotaan` (`status_keanggotaan`),
  ADD KEY `idx_status_kekatolikan` (`status_kekatolikan`);

--
-- Indexes for table `kategorial`
--
ALTER TABLE `kategorial`
  ADD PRIMARY KEY (`id_kategorial`),
  ADD KEY `idx_kelompok` (`kelompok_kategorial`),
  ADD KEY `idx_nama` (`nama_lengkap`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_wilayah` (`wilayah_rohani`),
  ADD KEY `idx_jenis_kelamin` (`jenis_kelamin`);

--
-- Indexes for table `kegiatan`
--
ALTER TABLE `kegiatan`
  ADD PRIMARY KEY (`id_kegiatan`),
  ADD KEY `idx_kegiatan_tanggal` (`tanggal_kegiatan`);

--
-- Indexes for table `kegiatan_wr`
--
ALTER TABLE `kegiatan_wr`
  ADD PRIMARY KEY (`id_kegiatan_wr`),
  ADD KEY `idx_kegiatan_wr_user` (`user_id`),
  ADD KEY `idx_kegiatan_wr_kategori` (`kategori`),
  ADD KEY `idx_kegiatan_wr_tanggal` (`tanggal_pelaksanaan`),
  ADD KEY `idx_kegiatan_wr_status` (`status_kegiatan`),
  ADD KEY `idx_kegiatan_wr_composite` (`user_id`,`tanggal_pelaksanaan` DESC);

--
-- Indexes for table `keuangan`
--
ALTER TABLE `keuangan`
  ADD PRIMARY KEY (`id_keuangan`),
  ADD KEY `idx_keuangan_tanggal` (`tanggal`),
  ADD KEY `idx_keuangan_kategori` (`kategori`);

--
-- Indexes for table `keuangan_kategorial`
--
ALTER TABLE `keuangan_kategorial`
  ADD PRIMARY KEY (`id_keuangan_kategorial`),
  ADD KEY `idx_tanggal` (`tanggal`),
  ADD KEY `idx_jenis` (`jenis`),
  ADD KEY `idx_kategori` (`kategori`),
  ADD KEY `idx_created_by_admin` (`created_by_admin`);

--
-- Indexes for table `k_binaan`
--
ALTER TABLE `k_binaan`
  ADD PRIMARY KEY (`id_binaan`),
  ADD KEY `idx_kelompok` (`kelompok_binaan`),
  ADD KEY `idx_nama` (`nama_lengkap`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  ADD PRIMARY KEY (`id_log`),
  ADD KEY `id_admin` (`id_admin`),
  ADD KEY `id_pengguna` (`id_pengguna`),
  ADD KEY `idx_log_timestamp` (`timestamp`);

--
-- Indexes for table `pengguna`
--
ALTER TABLE `pengguna`
  ADD PRIMARY KEY (`id_pengguna`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_pengguna_username` (`username`);

--
-- Indexes for table `pengumuman`
--
ALTER TABLE `pengumuman`
  ADD PRIMARY KEY (`id_pengumuman`),
  ADD KEY `idx_pengumuman_active` (`is_active`),
  ADD KEY `idx_pengumuman_sasaran` (`sasaran`),
  ADD KEY `idx_pengumuman_penanggung_jawab` (`penanggung_jawab`),
  ADD KEY `idx_pengumuman_pembuat` (`pembuat`),
  ADD KEY `idx_pengumuman_created_at` (`created_at`),
  ADD KEY `idx_pengumuman_is_active` (`is_active`);

--
-- Indexes for table `program_kerja`
--
ALTER TABLE `program_kerja`
  ADD PRIMARY KEY (`id_program_kerja`),
  ADD KEY `idx_kategori` (`kategori`),
  ADD KEY `idx_estimasi_waktu` (`estimasi_waktu`);

--
-- Indexes for table `program_kerja_k_kategorial`
--
ALTER TABLE `program_kerja_k_kategorial`
  ADD PRIMARY KEY (`id_program_kerja_k_kategorial`),
  ADD KEY `idx_program_kerja` (`program_kerja`),
  ADD KEY `idx_created_by` (`created_by`);

--
-- Indexes for table `program_kerja_k_kategorial_budget`
--
ALTER TABLE `program_kerja_k_kategorial_budget`
  ADD PRIMARY KEY (`id_budget`),
  ADD KEY `idx_program_id` (`id_program_kerja_k_kategorial`),
  ADD KEY `idx_sumber_anggaran` (`sumber_anggaran`);

--
-- Indexes for table `program_kerja_k_kategorial_evaluation`
--
ALTER TABLE `program_kerja_k_kategorial_evaluation`
  ADD PRIMARY KEY (`id_evaluation`),
  ADD KEY `idx_program_id` (`id_program_kerja_k_kategorial`);

--
-- Indexes for table `program_kerja_wr`
--
ALTER TABLE `program_kerja_wr`
  ADD PRIMARY KEY (`id_program_kerja_wr`),
  ADD KEY `idx_kategori` (`kategori`),
  ADD KEY `idx_estimasi_waktu` (`estimasi_waktu`),
  ADD KEY `idx_wilayah_rohani_id` (`wilayah_rohani_id`),
  ADD KEY `idx_reported_by` (`reported_by`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `struktur`
--
ALTER TABLE `struktur`
  ADD PRIMARY KEY (`id_struktur`),
  ADD KEY `idx_struktur_jabatan` (`jabatan_utama`),
  ADD KEY `idx_struktur_periode` (`periode`);

--
-- Indexes for table `tim_pembina`
--
ALTER TABLE `tim_pembina`
  ADD PRIMARY KEY (`id_tim_pembina`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `idx_tim_pembina` (`tim_pembina`);

--
-- Indexes for table `tim_pembina_peserta`
--
ALTER TABLE `tim_pembina_peserta`
  ADD PRIMARY KEY (`id_peserta`),
  ADD UNIQUE KEY `unique_tim_peserta` (`id_tim_pembina`,`id_jemaat`),
  ADD KEY `idx_id_tim` (`id_tim_pembina`),
  ADD KEY `idx_id_jemaat` (`id_jemaat`),
  ADD KEY `idx_jabatan` (`jabatan`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `wilayah_rohani`
--
ALTER TABLE `wilayah_rohani`
  ADD PRIMARY KEY (`id_wilayah`),
  ADD KEY `idx_wilayah` (`wilayah_rohani`),
  ADD KEY `idx_nama` (`nama_lengkap`),
  ADD KEY `idx_status` (`status`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id_admin` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `api_service_config`
--
ALTER TABLE `api_service_config`
  MODIFY `id_config` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `aset`
--
ALTER TABLE `aset`
  MODIFY `id_aset` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `buku_kronik`
--
ALTER TABLE `buku_kronik`
  MODIFY `id_kronik` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `client_connections`
--
ALTER TABLE `client_connections`
  MODIFY `id_connection` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=82;

--
-- AUTO_INCREMENT for table `dokumen`
--
ALTER TABLE `dokumen`
  MODIFY `id_dokumen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `jemaat`
--
ALTER TABLE `jemaat`
  MODIFY `id_jemaat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `kategorial`
--
ALTER TABLE `kategorial`
  MODIFY `id_kategorial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `kegiatan`
--
ALTER TABLE `kegiatan`
  MODIFY `id_kegiatan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `kegiatan_wr`
--
ALTER TABLE `kegiatan_wr`
  MODIFY `id_kegiatan_wr` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `keuangan`
--
ALTER TABLE `keuangan`
  MODIFY `id_keuangan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `keuangan_kategorial`
--
ALTER TABLE `keuangan_kategorial`
  MODIFY `id_keuangan_kategorial` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `k_binaan`
--
ALTER TABLE `k_binaan`
  MODIFY `id_binaan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  MODIFY `id_log` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=212;

--
-- AUTO_INCREMENT for table `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `pengumuman`
--
ALTER TABLE `pengumuman`
  MODIFY `id_pengumuman` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `program_kerja`
--
ALTER TABLE `program_kerja`
  MODIFY `id_program_kerja` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `program_kerja_k_kategorial`
--
ALTER TABLE `program_kerja_k_kategorial`
  MODIFY `id_program_kerja_k_kategorial` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `program_kerja_k_kategorial_budget`
--
ALTER TABLE `program_kerja_k_kategorial_budget`
  MODIFY `id_budget` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `program_kerja_k_kategorial_evaluation`
--
ALTER TABLE `program_kerja_k_kategorial_evaluation`
  MODIFY `id_evaluation` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `program_kerja_wr`
--
ALTER TABLE `program_kerja_wr`
  MODIFY `id_program_kerja_wr` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `struktur`
--
ALTER TABLE `struktur`
  MODIFY `id_struktur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tim_pembina`
--
ALTER TABLE `tim_pembina`
  MODIFY `id_tim_pembina` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tim_pembina_peserta`
--
ALTER TABLE `tim_pembina_peserta`
  MODIFY `id_peserta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `wilayah_rohani`
--
ALTER TABLE `wilayah_rohani`
  MODIFY `id_wilayah` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

-- --------------------------------------------------------

--
-- Structure for view `files`
--
DROP TABLE IF EXISTS `files`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `files`  AS SELECT `dokumen`.`id_dokumen` AS `id_dokumen`, `dokumen`.`nama_dokumen` AS `nama_dokumen`, `dokumen`.`jenis_dokumen` AS `jenis_dokumen`, coalesce(`dokumen`.`ukuran_file`,0) AS `ukuran_file`, `dokumen`.`tipe_file` AS `tipe_file`, `dokumen`.`file_path` AS `file_path`, `dokumen`.`uploaded_by_admin` AS `uploaded_by_admin`, `dokumen`.`uploaded_by_pengguna` AS `uploaded_by_pengguna`, `dokumen`.`uploaded_by_name` AS `uploaded_by_name`, `dokumen`.`upload_date` AS `upload_date`, `dokumen`.`created_at` AS `created_at` FROM `dokumen` ;

-- --------------------------------------------------------

--
-- Structure for view `log_activities`
--
DROP TABLE IF EXISTS `log_activities`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `log_activities`  AS SELECT `log_aktivitas`.`id_log` AS `id_log`, `log_aktivitas`.`id_admin` AS `id_admin`, `log_aktivitas`.`aktivitas` AS `aktivitas`, `log_aktivitas`.`detail` AS `detail`, `log_aktivitas`.`ip_address` AS `ip_address`, `log_aktivitas`.`timestamp` AS `timestamp` FROM `log_aktivitas` ;

-- --------------------------------------------------------

--
-- Structure for view `user_sessions`
--
DROP TABLE IF EXISTS `user_sessions`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `user_sessions`  AS SELECT concat('session_',`client_connections`.`id_connection`) AS `session_id`, `client_connections`.`client_ip` AS `client_ip`, `client_connections`.`hostname` AS `hostname`, NULL AS `user_id`, `client_connections`.`connect_time` AS `connect_time`, `client_connections`.`last_activity` AS `last_activity`, CASE WHEN `client_connections`.`status` = 'Terhubung' THEN 'active' WHEN `client_connections`.`status` = 'Terputus' THEN 'disconnected' ELSE 'inactive' END AS `status` FROM `client_connections` ;

-- --------------------------------------------------------

--
-- Structure for view `v_active_clients`
--
DROP TABLE IF EXISTS `v_active_clients`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_active_clients`  AS SELECT `client_connections`.`client_ip` AS `client_ip`, `client_connections`.`hostname` AS `hostname`, `client_connections`.`connect_time` AS `connect_time`, `client_connections`.`last_activity` AS `last_activity`, timestampdiff(MINUTE,`client_connections`.`last_activity`,current_timestamp()) AS `minutes_inactive` FROM `client_connections` WHERE `client_connections`.`status` = 'Terhubung' ORDER BY `client_connections`.`last_activity` DESC ;

-- --------------------------------------------------------

--
-- Structure for view `v_current_server_status`
--
DROP TABLE IF EXISTS `v_current_server_status`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_current_server_status`  AS SELECT `s`.`id_session` AS `id_session`, `s`.`server_host` AS `server_host`, `s`.`server_port` AS `server_port`, `s`.`start_time` AS `start_time`, `s`.`end_time` AS `end_time`, `s`.`status` AS `status`, `s`.`started_by_admin` AS `started_by_admin`, `s`.`started_by_pengguna` AS `started_by_pengguna`, CASE WHEN `s`.`end_time` is null THEN timestampdiff(SECOND,`s`.`start_time`,current_timestamp()) ELSE timestampdiff(SECOND,`s`.`start_time`,`s`.`end_time`) END AS `uptime_seconds` FROM `server_sessions` AS `s` WHERE `s`.`status` = 'Running' ORDER BY `s`.`start_time` DESC LIMIT 0, 1 ;

-- --------------------------------------------------------

--
-- Structure for view `v_kegiatan_mendatang`
--
DROP TABLE IF EXISTS `v_kegiatan_mendatang`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_kegiatan_mendatang`  AS SELECT `kegiatan`.`id_kegiatan` AS `id_kegiatan`, `kegiatan`.`nama_kegiatan` AS `nama_kegiatan`, `kegiatan`.`lokasi` AS `lokasi`, `kegiatan`.`tanggal_mulai` AS `tanggal_mulai`, `kegiatan`.`tanggal_selesai` AS `tanggal_selesai`, `kegiatan`.`waktu_mulai` AS `waktu_mulai`, `kegiatan`.`waktu_selesai` AS `waktu_selesai`, `kegiatan`.`penanggungjawab` AS `penanggungjawab`, `kegiatan`.`kategori` AS `kategori`, to_days(`kegiatan`.`tanggal_mulai`) - to_days(curdate()) AS `hari_tersisa` FROM `kegiatan` WHERE `kegiatan`.`tanggal_mulai` >= curdate() AND `kegiatan`.`status` = 'Direncanakan' ORDER BY `kegiatan`.`tanggal_mulai` ASC ;

-- --------------------------------------------------------

--
-- Structure for view `v_kegiatan_wr_detail`
--
DROP TABLE IF EXISTS `v_kegiatan_wr_detail`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_kegiatan_wr_detail`  AS SELECT `kw`.`id_kegiatan_wr` AS `id_kegiatan_wr`, `kw`.`kategori` AS `kategori`, `kw`.`nama_kegiatan` AS `nama_kegiatan`, `kw`.`sasaran_kegiatan` AS `sasaran_kegiatan`, `kw`.`tujuan_kegiatan` AS `tujuan_kegiatan`, `kw`.`tempat_kegiatan` AS `tempat_kegiatan`, `kw`.`tanggal_pelaksanaan` AS `tanggal_pelaksanaan`, `kw`.`tanggal_selesai` AS `tanggal_selesai`, `kw`.`waktu_mulai` AS `waktu_mulai`, `kw`.`waktu_selesai` AS `waktu_selesai`, `kw`.`penanggung_jawab` AS `penanggung_jawab`, `kw`.`status_kegiatan` AS `status_kegiatan`, `kw`.`deskripsi` AS `deskripsi`, `kw`.`keterangan` AS `keterangan`, `kw`.`user_id` AS `user_id`, `p`.`username` AS `username`, `p`.`nama_lengkap` AS `nama_lengkap`, `p`.`peran` AS `peran`, `kw`.`created_at` AS `created_at`, `kw`.`updated_at` AS `updated_at`, dayname(`kw`.`tanggal_pelaksanaan`) AS `nama_hari`, to_days(`kw`.`tanggal_pelaksanaan`) - to_days(curdate()) AS `hari_tersisa` FROM (`kegiatan_wr` `kw` left join `pengguna` `p` on(`kw`.`user_id` = `p`.`id_pengguna`)) ORDER BY `kw`.`tanggal_pelaksanaan` DESC ;

-- --------------------------------------------------------

--
-- Structure for view `v_kegiatan_wr_mendatang`
--
DROP TABLE IF EXISTS `v_kegiatan_wr_mendatang`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_kegiatan_wr_mendatang`  AS SELECT `kw`.`id_kegiatan_wr` AS `id_kegiatan_wr`, `kw`.`kategori` AS `kategori`, `kw`.`nama_kegiatan` AS `nama_kegiatan`, `kw`.`sasaran_kegiatan` AS `sasaran_kegiatan`, `kw`.`tujuan_kegiatan` AS `tujuan_kegiatan`, `kw`.`tempat_kegiatan` AS `tempat_kegiatan`, `kw`.`tanggal_pelaksanaan` AS `tanggal_pelaksanaan`, `kw`.`tanggal_selesai` AS `tanggal_selesai`, `kw`.`waktu_mulai` AS `waktu_mulai`, `kw`.`waktu_selesai` AS `waktu_selesai`, `kw`.`penanggung_jawab` AS `penanggung_jawab`, `kw`.`status_kegiatan` AS `status_kegiatan`, `kw`.`deskripsi` AS `deskripsi`, `kw`.`user_id` AS `user_id`, `p`.`username` AS `username`, `p`.`nama_lengkap` AS `nama_lengkap`, to_days(`kw`.`tanggal_pelaksanaan`) - to_days(curdate()) AS `hari_tersisa` FROM (`kegiatan_wr` `kw` left join `pengguna` `p` on(`kw`.`user_id` = `p`.`id_pengguna`)) WHERE `kw`.`tanggal_pelaksanaan` >= curdate() AND `kw`.`status_kegiatan` in ('Direncanakan','Berlangsung') ORDER BY `kw`.`tanggal_pelaksanaan` ASC ;

-- --------------------------------------------------------

--
-- Structure for view `v_laporan_keuangan_bulanan`
--
DROP TABLE IF EXISTS `v_laporan_keuangan_bulanan`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_laporan_keuangan_bulanan`  AS SELECT year(`keuangan`.`tanggal`) AS `tahun`, month(`keuangan`.`tanggal`) AS `bulan`, `keuangan`.`kategori` AS `kategori`, sum(`keuangan`.`jumlah`) AS `total`, count(0) AS `jumlah_transaksi` FROM `keuangan` GROUP BY year(`keuangan`.`tanggal`), month(`keuangan`.`tanggal`), `keuangan`.`kategori` ORDER BY year(`keuangan`.`tanggal`) DESC, month(`keuangan`.`tanggal`) DESC ;

-- --------------------------------------------------------

--
-- Structure for view `v_pengumuman_aktif`
--
DROP TABLE IF EXISTS `v_pengumuman_aktif`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_pengumuman_aktif`  AS SELECT `pengumuman`.`id_pengumuman` AS `id_pengumuman`, `pengumuman`.`judul` AS `judul`, `pengumuman`.`isi` AS `isi`, `pengumuman`.`tanggal_mulai` AS `tanggal_mulai`, `pengumuman`.`tanggal_selesai` AS `tanggal_selesai`, `pengumuman`.`kategori` AS `kategori`, `pengumuman`.`prioritas` AS `prioritas` FROM `pengumuman` WHERE `pengumuman`.`is_active` = 1 AND curdate() between `pengumuman`.`tanggal_mulai` and `pengumuman`.`tanggal_selesai` ORDER BY `pengumuman`.`prioritas` DESC, `pengumuman`.`tanggal_mulai` DESC ;

-- --------------------------------------------------------

--
-- Structure for view `v_statistik_jemaat`
--
DROP TABLE IF EXISTS `v_statistik_jemaat`;

CREATE ALGORITHM=UNDEFINED DEFINER=`entf7819`@`localhost` SQL SECURITY DEFINER VIEW `v_statistik_jemaat`  AS SELECT count(0) AS `total_jemaat`, count(case when `jemaat`.`jenis_kelamin` = 'Laki-laki' then 1 end) AS `total_laki`, count(case when `jemaat`.`jenis_kelamin` = 'Perempuan' then 1 end) AS `total_perempuan`, count(distinct `jemaat`.`lingkungan`) AS `total_lingkungan`, count(distinct `jemaat`.`wilayah`) AS `total_wilayah` FROM `jemaat` ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `api_service_config`
--
ALTER TABLE `api_service_config`
  ADD CONSTRAINT `api_service_config_ibfk_1` FOREIGN KEY (`last_enabled_by_admin`) REFERENCES `admin` (`id_admin`) ON DELETE SET NULL,
  ADD CONSTRAINT `api_service_config_ibfk_2` FOREIGN KEY (`last_enabled_by_pengguna`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE SET NULL;

--
-- Constraints for table `dokumen`
--
ALTER TABLE `dokumen`
  ADD CONSTRAINT `fk_dokumen_admin` FOREIGN KEY (`uploaded_by_admin`) REFERENCES `admin` (`id_admin`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_dokumen_pengguna` FOREIGN KEY (`uploaded_by_pengguna`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE SET NULL;

--
-- Constraints for table `kegiatan_wr`
--
ALTER TABLE `kegiatan_wr`
  ADD CONSTRAINT `fk_kegiatan_wr_user` FOREIGN KEY (`user_id`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE;

--
-- Constraints for table `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  ADD CONSTRAINT `log_aktivitas_ibfk_1` FOREIGN KEY (`id_admin`) REFERENCES `admin` (`id_admin`) ON DELETE SET NULL,
  ADD CONSTRAINT `log_aktivitas_ibfk_2` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE SET NULL;

--
-- Constraints for table `program_kerja_k_kategorial_budget`
--
ALTER TABLE `program_kerja_k_kategorial_budget`
  ADD CONSTRAINT `program_kerja_k_kategorial_budget_ibfk_1` FOREIGN KEY (`id_program_kerja_k_kategorial`) REFERENCES `program_kerja_k_kategorial` (`id_program_kerja_k_kategorial`) ON DELETE CASCADE;

--
-- Constraints for table `program_kerja_k_kategorial_evaluation`
--
ALTER TABLE `program_kerja_k_kategorial_evaluation`
  ADD CONSTRAINT `program_kerja_k_kategorial_evaluation_ibfk_1` FOREIGN KEY (`id_program_kerja_k_kategorial`) REFERENCES `program_kerja_k_kategorial` (`id_program_kerja_k_kategorial`) ON DELETE CASCADE;

--
-- Constraints for table `tim_pembina_peserta`
--
ALTER TABLE `tim_pembina_peserta`
  ADD CONSTRAINT `tim_pembina_peserta_ibfk_1` FOREIGN KEY (`id_tim_pembina`) REFERENCES `tim_pembina` (`id_tim_pembina`) ON DELETE CASCADE,
  ADD CONSTRAINT `tim_pembina_peserta_ibfk_2` FOREIGN KEY (`id_jemaat`) REFERENCES `jemaat` (`id_jemaat`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
