-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 04, 2025 at 12:46 AM
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
(1, 'admin', '15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225', 'Administrator Gereja', 'admin@gereja.com', 'Admin', 1, '2025-06-15 14:16:27', '2025-12-03 17:14:50', '2025-12-03 18:14:49'),
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
(1, 'SFGH-01', 'Mobil', 'Bergerak', 'Kendaraan', 'Toyota', 2020, 'Pembelian', 0.00, 'Baik', 'Pastoran', 'Aktif', 'Pastoran', 'Mobil Pastoran', '2025-11-05 08:07:40', '2025-11-30 20:00:33'),
(2, 'ASD-01', 'Tanah', 'Bergerak', 'Tanah', '', 1995, 'Pembelian', 0.00, 'Baik', 'Pastoran', 'Aktif', 'Pastoran', '', '2025-11-18 14:53:24', '2025-11-30 19:58:56');

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

--
-- Dumping data for table `buku_kronik`
--

INSERT INTO `buku_kronik` (`id_kronik`, `tanggal`, `peristiwa`, `keterangan`, `created_by`, `created_at`, `updated_at`) VALUES
(1, '2025-11-01', 'asdfghj', '', 1, '2025-11-18 22:49:39', '2025-11-26 14:43:57'),
(2, '2025-11-27', 'asdf', '', 1, '2025-11-19 00:10:54', '2025-11-26 14:43:38'),
(3, '2025-11-19', 'asdfghjkm', 'sdyguoh', 1, '2025-11-19 02:41:06', '2025-11-19 02:41:06'),
(5, '2025-11-26', 'misaQWSX S RFTVGUHJYTIJKUYKOIUPOLIP;OI[\']PO]\'O[P\']P] SD', '', 1, '2025-11-25 16:12:57', '2025-11-26 14:41:36'),
(6, '2025-11-26', 'Jemaat → tim_pembina_peserta\nSatu data jemaat dapat dicatat sebagai peserta pada beberapa tim pembina (misalnya periode atau peran berbeda). Relasi ini ditunjukkan oleh kolom id_jemaat (FK) pada tabel tim_pembina_peserta yang mengacu pada id_jemaat (PK) p', 'WESRTGJemaat → tim_pembina_peserta\nSatu data jemaat dapat dicatat sebagai peserta pada beberapa tim pembina (misalnya periode atau peran berbeda). Relasi ini ditunjukkan oleh kolom id_jemaat (FK) pada tabel tim_pembina_peserta yang mengacu pada id_jemaat (PK) pada tabel jemaat .', 1, '2025-11-26 14:41:50', '2025-12-01 05:20:21'),
(8, '2025-12-01', 'Digital', 'Digitalisasi arsip pada sistem membantu mengurangi risiko kehilangan dokumen, meningkatkan kerapian penyimpanan, serta memudahkan pencarian dan penelusuran data ketika diperlukan.', 1, '2025-12-01 09:34:49', '2025-12-01 09:34:49');

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
(81, '10.1.3.172', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-05 07:42:04', '2025-11-05 07:44:10', '2025-11-05 07:44:10'),
(82, '10.1.13.249', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-18 13:20:30', '2025-11-18 13:33:44', '2025-11-18 13:33:44'),
(83, '10.1.13.249', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-18 20:09:51', '2025-11-19 00:21:13', '2025-11-19 00:21:13'),
(84, '192.168.1.100', 'SECOND-POWER', 'Terputus', '2025-11-21 03:57:40', '2025-11-21 03:59:46', '2025-11-21 03:59:46'),
(85, '10.1.13.249', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-21 04:39:57', '2025-11-21 04:40:11', '2025-11-21 04:40:11'),
(86, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-26 17:31:04', '2025-11-27 10:14:06', '2025-11-27 10:14:06'),
(87, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-27 14:17:42', '2025-11-28 01:22:54', '2025-11-28 01:22:54'),
(88, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 01:32:42', '2025-11-28 02:54:03', '2025-11-28 02:54:03'),
(89, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 03:02:16', '2025-11-28 03:41:56', '2025-11-28 03:41:56'),
(90, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 03:42:03', '2025-11-28 03:56:53', '2025-11-28 03:56:53'),
(91, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 03:57:20', '2025-11-28 03:58:02', '2025-11-28 03:58:02'),
(92, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 03:58:16', '2025-11-28 04:33:40', '2025-11-28 04:33:40'),
(93, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 04:34:03', '2025-11-28 05:41:53', '2025-11-28 05:41:53'),
(94, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-28 05:43:59', '2025-11-29 01:05:28', '2025-11-29 01:05:28'),
(95, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 08:29:32', '2025-11-30 10:25:34', '2025-11-30 10:25:34'),
(96, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 10:25:47', '2025-11-30 10:49:43', '2025-11-30 10:49:43'),
(97, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 10:54:43', '2025-11-30 11:17:54', '2025-11-30 11:17:54'),
(98, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 11:22:16', '2025-11-30 11:28:31', '2025-11-30 11:28:31'),
(99, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 11:29:51', '2025-11-30 12:20:02', '2025-11-30 12:20:02'),
(100, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 12:22:29', '2025-11-30 13:10:43', '2025-11-30 13:10:43'),
(101, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 13:43:41', '2025-11-30 14:54:33', '2025-11-30 14:54:33'),
(102, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 14:56:27', '2025-11-30 15:32:03', '2025-11-30 15:32:03'),
(103, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 15:40:19', '2025-11-30 16:35:59', '2025-11-30 16:35:59'),
(104, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 16:45:45', '2025-11-30 17:11:04', '2025-11-30 17:11:04'),
(105, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 17:20:48', '2025-11-30 17:47:50', '2025-11-30 17:47:50'),
(106, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-11-30 18:03:45', '2025-12-01 11:50:43', '2025-12-01 11:50:43'),
(107, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-12-02 01:05:44', '2025-12-02 03:16:11', '2025-12-02 03:16:11'),
(108, '10.1.14.205', 'SECOND-POWER-CLIENT', 'Terputus', '2025-12-02 03:28:49', '2025-12-02 16:29:04', '2025-12-02 16:29:04'),
(109, '10.1.4.240', 'SECOND-POWER-CLIENT', 'Terputus', '2025-12-03 00:44:53', '2025-12-03 02:47:08', '2025-12-03 02:47:08'),
(110, '10.252.199.59', 'SECOND-POWER-CLIENT', 'Terputus', '2025-12-03 05:29:33', '2025-12-03 05:45:21', '2025-12-03 05:45:21'),
(111, '10.252.199.59', 'SECOND-POWER-CLIENT', 'Terputus', '2025-12-03 05:57:08', '2025-12-03 06:46:44', '2025-12-03 06:46:44'),
(112, '10.1.4.73', 'SECOND-POWER-CLIENT', 'Terhubung', '2025-12-03 14:13:03', NULL, '2025-12-03 17:45:48'),
(113, '10.158.244.94', 'DESKTOP-HU57NJ0-CLIENT', 'Terputus', '2025-12-03 16:22:18', '2025-12-03 16:55:33', '2025-12-03 16:55:33'),
(114, '10.158.244.94', 'DESKTOP-HU57NJ0-CLIENT', 'Terputus', '2025-12-03 16:56:46', '2025-12-03 17:30:31', '2025-12-03 17:30:31'),
(115, '10.158.244.94', 'DESKTOP-HU57NJ0-CLIENT', 'Terhubung', '2025-12-03 17:30:52', NULL, '2025-12-03 17:45:59');

-- --------------------------------------------------------

--
-- Table structure for table `dokumen`
--

CREATE TABLE `dokumen` (
  `id_dokumen` int(11) NOT NULL,
  `nama_dokumen` varchar(200) NOT NULL,
  `bentuk_dokumen` varchar(100) DEFAULT NULL COMMENT 'Bentuk/tipe dokumen (Surat, Laporan, dll)',
  `kategori_file` varchar(100) DEFAULT 'Lainnya' COMMENT 'Kategori/bentuk file dari upload dialog',
  `file_path` varchar(500) NOT NULL DEFAULT '',
  `ukuran_file` bigint(20) DEFAULT 0 COMMENT 'Ukuran file dalam bytes - otomatis terisi saat upload',
  `keterangan` text DEFAULT NULL,
  `upload_date` timestamp NULL DEFAULT current_timestamp() COMMENT 'Tanggal dan waktu upload dokumen',
  `uploaded_by_admin` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `dokumen`
--

INSERT INTO `dokumen` (`id_dokumen`, `nama_dokumen`, `bentuk_dokumen`, `kategori_file`, `file_path`, `ukuran_file`, `keterangan`, `upload_date`, `uploaded_by_admin`, `created_at`, `updated_at`) VALUES
(26, '5.-Greatist-.jpg', 'Publikasi/Media (poster, brosur, banner, konten medsos)', 'Publikasi/Media (poster, brosur, banner, konten medsos)', 'uploads/dokumen/dokumen_63b4d2b8_20251126_223245.jpg', 21907, 'qwert', '2025-11-26 15:32:45', NULL, '2025-11-26 15:32:45', '2025-11-26 15:32:45'),
(27, 'gariss hvs.pdf', 'Lainnya', 'Lainnya', 'uploads/dokumen/dokumen_a5258d32_20251126_225835.pdf', 48403, '', '2025-11-26 15:58:35', NULL, '2025-11-26 15:58:35', '2025-11-26 15:58:35'),
(28, '41867ebf52277e6b72131f78d9807d88.jpg', 'Arsip Dokumentasi', 'Arsip Digital & Media', 'uploads/dokumen/dokumen_2f837f87_20251126_233415.jpg', 36334, 'dsdxcvcsdfg', '2025-11-26 16:34:15', 1, '2025-11-26 16:34:15', '2025-11-26 16:34:15'),
(29, '41867ebf52277e6b72131f78d9807d88.jpg', 'Arsip Dokumentasi', 'Arsip Digital & Media', 'uploads/dokumen/dokumen_2f3e51dd_20251201_031803.jpg', 36334, 'aaaaa', '2025-11-30 20:18:03', 1, '2025-11-30 20:18:03', '2025-11-30 20:18:03');

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
  `no_telepon` varchar(20) DEFAULT NULL,
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
  `status_keanggotaan` varchar(50) DEFAULT 'Aktif' COMMENT 'Status: Aktif, Menetap, Pindah, Meninggal, Tidak Aktif',
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

INSERT INTO `jemaat` (`id_jemaat`, `nama_lengkap`, `nik`, `nama_keluarga`, `no_kk`, `alamat`, `email`, `no_telepon`, `tanggal_lahir`, `tempat_lahir`, `umur`, `status_kekatolikan`, `kategori`, `hubungan_keluarga`, `jenis_kelamin`, `status_menikah`, `status_perkawinan`, `keuskupan`, `paroki`, `kota_perkawinan`, `tanggal_perkawinan`, `status_perkawinan_detail`, `status_keanggotaan`, `wr_tujuan`, `paroki_tujuan`, `jenis_pekerjaan`, `detail_pekerjaan`, `pendidikan_terakhir`, `nama_babtis`, `status_babtis`, `status_ekaristi`, `status_krisma`, `wilayah_rohani`, `created_at`, `updated_at`, `created_by_pengguna`, `tanggal_babtis`, `tempat_babtis`, `tanggal_komuni`, `tempat_komuni`, `tanggal_krisma`, `tempat_krisma`) VALUES
(71, 'Maydupi Astri Turnip', '9709653423198054', 'Cemara', '9765432875008432', 'Walian I', 'maymaymay@gmail.com', '081245647865', '2000-11-11', 'Jakarta', 25, 'Kelahiran', 'OMK', 'Anak', 'Perempuan', 'Belum Menikah', 'Belum', NULL, NULL, NULL, NULL, NULL, 'Menetap', NULL, NULL, 'Pelajar', NULL, 'SMK', NULL, 'Sudah', 'Sudah', 'Sudah', 'ST. YOHANES MARIA VIANNEY', '2025-12-02 01:35:00', '2025-12-02 01:35:00', 1, NULL, NULL, NULL, NULL, NULL, NULL),
(72, 'Elora Indriani', '97460755431097543', 'Cemara', '98764865378087', 'Tondano', NULL, NULL, '2003-12-02', 'Malang', 22, 'Kelahiran', 'OMK', 'Anak', 'Perempuan', 'Belum Menikah', NULL, NULL, NULL, NULL, '2025-12-02', NULL, 'Pilih Status', NULL, NULL, 'Pelajar', NULL, 'S1', NULL, NULL, NULL, NULL, 'ST. YOHANES BAPTISTA DE LA SALLE', '2025-12-02 04:17:20', '2025-12-02 04:17:20', 3, '2025-12-02', NULL, '2025-12-02', NULL, '2025-12-02', NULL),
(76, 'testt', '9876540087654309', 'testt', '8769654367908700', 'testtt', 'testt@gmail.com', NULL, '2007-12-03', 'testt', 18, 'Kelahiran', 'OMK', 'Anak', 'Laki-laki', 'Belum Menikah', 'Belum', NULL, NULL, NULL, '2025-12-03', NULL, 'Menetap', NULL, NULL, 'Pelajar', NULL, 'SMA', 'testt', 'Sudah', 'Sudah', 'Sudah', 'ST. ALOYSIUS GONZAGA', '2025-12-03 06:05:40', '2025-12-03 06:05:40', 3, '2009-12-03', 'testt', '2019-12-03', 'testt', '2024-12-03', 'testt'),
(77, 'Star', '9876509875300760', 'Star', '9876500054326789', NULL, NULL, NULL, '2000-12-03', 'Star', 25, 'Kelahiran', 'OMK', NULL, 'Perempuan', NULL, NULL, NULL, NULL, NULL, '2025-12-03', NULL, 'Pilih Status', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'ST. YOHANES BAPTISTA DE LA SALLE', '2025-12-03 06:15:21', '2025-12-03 06:15:21', 3, '2025-12-03', NULL, '2025-12-03', NULL, '2025-12-03', NULL),
(78, 'asdf', 'asdf', 'asdf', 'asdf', 'asdf', 'asdf', 'asdf', '2025-12-04', 'asdf', 0, 'Babtisan', 'Lansia', 'Istri', 'Laki-laki', 'Belum Menikah', 'Sudah', 'asdf', 'asdf', 'asdf', '2025-12-01', 'Sipil dan Gereja', 'Pindah', NULL, NULL, 'Pelajar', NULL, 'SD', NULL, 'Belum', 'Sudah', 'Sudah', 'ST. YOHANES BAPTISTA DE LA SALLE', '2025-12-03 16:23:54', '2025-12-03 16:23:54', 3, '2025-12-04', NULL, '2025-12-04', 'asdf', '2025-12-04', 'asdf'),
(79, 'eqweqw', 'eqweqw', 'asdfasdfasdf', 'qweqw', 'fsdfsd', 'fsdfs', 'dfsfd', '2025-12-04', 'eqweqweq', 0, 'Kelahiran', 'Anak-anak', 'Kepala Keluarga', 'Perempuan', 'Sudah Menikah', 'Sudah', 'sdf', 'sdf', 'sdfsdfs', '2025-12-04', 'Gereja', 'Pilih Status', NULL, NULL, 'Bekerja', 'sdfsd', 'SMP', NULL, 'Belum', 'Belum', 'Sudah', 'ST. BONIFASIUS', '2025-12-03 16:58:11', '2025-12-03 17:01:40', 5, '2025-12-04', 'sd', '2025-12-04', NULL, '2025-12-04', 'sdfsdf');

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
(1, 'OMK', '', 'tess', 'Perempuan', 'tess', 'tess', 'tess', 'tess', 'ST. BLASIUS', '2025-2026', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_6200b6bd_20251105_130023.jpeg', '2025-11-05 06:00:26', '2025-11-18 16:30:02'),
(2, 'KMK', '', 'asdf', 'Perempuan', 'asdfg', '12345678', 'asdfghjk', 'werh', 'STA. AGNES', '2025-2-27', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_de4192a8_20251118_232711.jpg', '2025-11-18 16:27:14', '2025-11-18 16:27:14');

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
(18, 'Jumat Salve', 'Gereja Paroki', '2025-12-05', '18:00:00', 'WR. Santo Gregorius', 'Misa', 'Direncanakan', 0.00, 'Merayakan jumat minggu pertama masa adven', '2025-11-30 20:21:30', '2025-11-30 20:21:30', NULL, 'Seluruh Umat');

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
(11, 'Doa', 'asdf', 'asd', 'asdf', 'asdf', '2027-11-28', '10:00:00', 'asdf', 'Berlangsung', 'asdaf', 3, '2025-11-28 05:46:22', '2025-11-30 12:23:55'),
(12, 'Sosial', 'aaa', 'aaa', 'aaa', 'aaa', '2025-11-30', '08:00:00', 'aaa', 'Direncanakan', 'aaa', 3, '2025-11-30 09:54:22', '2025-11-30 09:54:22'),
(13, 'Misa', 'asdf', 'asdf', 'asd', 'asd', '2025-11-30', '20:00:00', 'asdadf', 'Direncanakan', 'asdfghj', 3, '2025-11-30 10:18:53', '2025-11-30 10:18:53'),
(14, 'Misa', 'ada', 'asd', 'ad', 'asd', '2026-11-30', '20:07:00', 'ad', 'Direncanakan', 'asfgf', 3, '2025-11-30 12:07:58', '2025-11-30 12:07:58'),
(15, 'Misa', 'asd', 'asgdh', 'asg', 'aff', '2026-11-30', '20:22:00', 'qqqqq', 'Direncanakan', 'qqqqqqqqqqqqqqqqqqqqqqqq', 3, '2025-11-30 12:23:23', '2025-11-30 12:23:23'),
(16, 'Misa', 'AAA', 'AAA', 'AAA', 'AAAA', '2025-12-01', '03:50:00', 'AAAAAAAAAS', 'Direncanakan', 'AAA', 3, '2025-11-30 19:51:14', '2025-11-30 19:51:14');

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
(19, '2025-10-06', 'Pemasukan', 'Kolekte', 250000.00, 'asdf', '2025-10-06 15:26:41', '2025-10-06 15:26:41', 6),
(23, '2025-10-30', 'Pengeluaran', 'Donasi', 100000.00, 'donasi pemabngunan', '2025-10-30 06:57:47', '2025-10-30 06:57:47', 3),
(29, '2025-11-17', 'Pemasukan', 'Kolekte', 100000.00, '', '2025-11-17 15:16:47', '2025-11-17 15:16:47', 3),
(30, '2025-12-01', 'Pengeluaran', 'Donasi', 12345678.00, 'qqereqt', '2025-11-30 18:55:13', '2025-11-30 18:55:13', 3),
(31, '2025-12-01', 'Pemasukan', 'Kolekte', 99999999.99, '', '2025-11-30 19:30:38', '2025-11-30 19:30:38', 3),
(32, '2025-12-01', 'Pengeluaran', 'Donasi', 111111.00, 'a2qedd', '2025-11-30 19:41:59', '2025-11-30 19:41:59', 3),
(33, '2025-12-01', 'Pemasukan', 'Kolekte', 222222.00, '', '2025-11-30 20:39:24', '2025-11-30 20:39:24', 3);

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

--
-- Dumping data for table `keuangan_kategorial`
--

INSERT INTO `keuangan_kategorial` (`id_keuangan_kategorial`, `tanggal`, `jenis`, `kategori`, `keterangan`, `jumlah`, `created_at`, `updated_at`, `created_by_admin`) VALUES
(1, '2025-12-01', 'Pemasukan', 'Persembahan', '', 200000.00, '2025-11-30 20:57:36', '2025-11-30 20:57:36', 1);

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
(1, 'PPA', '', 'tess', 'Perempuan', 'asdfv', '087865432345', 'qwer@gmail.com', 'qwer', 'ST. CORNELIUS', '2025-2090', 'Aktif', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_a523585d_20251105_133727.jpg', '2025-11-05 06:37:43', '2025-11-20 17:15:11');

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
(211, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-11 12:59:12'),
(212, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 15:26:05'),
(213, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 15:54:11'),
(214, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 15:57:22'),
(215, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 16:04:44'),
(216, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 16:16:58'),
(217, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 16:31:07'),
(218, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 16:42:18'),
(219, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 16:55:21'),
(220, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 17:09:31'),
(221, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-12 17:20:39'),
(222, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-12 17:27:58'),
(223, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-12 17:28:40'),
(224, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-14 13:07:15'),
(225, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 10:00:22'),
(226, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-16 10:03:05'),
(227, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 10:15:55'),
(228, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 11:14:04'),
(229, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 11:45:02'),
(230, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 15:15:57'),
(231, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 15:35:51'),
(232, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 15:54:07'),
(233, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:01:56'),
(234, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-16 16:02:05'),
(235, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:11:15'),
(236, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:17:10'),
(237, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:24:39'),
(238, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:46:31'),
(239, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 16:55:02'),
(240, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:02:32'),
(241, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:08:59'),
(242, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:16:42'),
(243, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:24:30'),
(244, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:29:19'),
(245, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:37:57'),
(246, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:41:39'),
(247, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 17:51:10'),
(248, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 18:15:42'),
(249, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 18:26:49'),
(250, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 18:41:32'),
(251, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 19:25:38'),
(252, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-16 19:36:00'),
(253, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-16 19:59:44'),
(254, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-16 19:59:51'),
(255, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 08:10:57'),
(256, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 08:23:28'),
(257, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-17 08:23:43'),
(258, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 08:28:50'),
(259, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-17 08:28:53'),
(260, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 08:34:20'),
(261, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-17 08:34:24'),
(262, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 08:35:35'),
(263, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 09:00:39'),
(264, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 09:46:50'),
(265, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 10:00:18'),
(266, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 10:13:00'),
(267, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 10:59:48'),
(268, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 11:11:33'),
(269, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 13:32:23'),
(270, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 13:54:57'),
(271, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-17 13:55:00'),
(272, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-17 14:43:31'),
(273, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 12:56:22'),
(274, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 13:34:03'),
(275, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 14:41:24'),
(276, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-18 14:41:33'),
(277, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 14:42:04'),
(278, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 20:08:43'),
(279, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-18 21:18:49'),
(280, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 21:19:11'),
(281, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-18 22:20:56'),
(282, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 22:21:49'),
(283, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-18 23:52:24'),
(284, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-19 00:21:03'),
(285, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 01:48:08'),
(286, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 02:16:18'),
(287, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 02:27:47'),
(288, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 06:44:22'),
(289, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 07:12:05'),
(290, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 07:37:01'),
(291, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 08:15:30'),
(292, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 08:33:34'),
(293, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-19 08:50:09'),
(294, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 07:29:57'),
(295, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 07:40:39'),
(296, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 10:08:45'),
(297, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 10:19:50'),
(298, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 10:53:39'),
(299, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 11:26:33'),
(300, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-20 12:50:59'),
(301, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 12:52:21'),
(302, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 16:57:35'),
(303, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-20 17:37:46'),
(304, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-20 17:38:03'),
(305, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 02:52:08'),
(306, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-21 03:45:52'),
(307, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 03:46:15'),
(308, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 04:29:13'),
(309, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 06:14:22'),
(310, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 06:45:12'),
(311, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 08:42:10'),
(312, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 10:03:18'),
(313, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-21 10:19:26'),
(314, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 10:20:26'),
(315, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-21 12:59:29'),
(316, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 13:01:14'),
(317, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 14:10:57'),
(318, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 14:35:35'),
(319, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 14:52:57'),
(320, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-21 16:59:56'),
(321, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-22 03:07:09'),
(322, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-24 11:10:32'),
(323, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-24 18:20:33'),
(324, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-24 18:23:00'),
(325, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-24 18:31:45'),
(326, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-25 06:52:39'),
(327, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-25 10:30:27'),
(328, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-25 13:09:02'),
(329, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 06:02:00'),
(330, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-26 06:02:37'),
(331, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 08:32:34'),
(332, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 10:46:40'),
(333, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 12:54:12'),
(334, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 13:21:55'),
(335, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 14:23:09'),
(336, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 14:55:58'),
(337, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 15:31:57'),
(338, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 15:39:54'),
(339, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 15:56:54'),
(340, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:11:25'),
(341, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:15:24'),
(342, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:21:24'),
(343, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:24:27'),
(344, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-26 16:38:59'),
(345, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:39:20'),
(346, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 16:48:52'),
(347, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-26 17:23:14'),
(348, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 17:23:49'),
(349, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 17:58:24'),
(350, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 18:01:45'),
(351, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 18:15:03'),
(352, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 18:36:10'),
(353, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 18:45:06'),
(354, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-26 18:53:58'),
(355, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 01:58:07'),
(356, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 02:07:10'),
(357, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 02:14:10'),
(358, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 02:38:32'),
(359, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 04:03:51'),
(360, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 04:12:29'),
(361, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 13:08:43'),
(362, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-27 14:17:13'),
(363, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 01:22:59'),
(364, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 02:54:11'),
(365, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 03:44:01'),
(366, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 04:34:08'),
(367, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 05:40:59'),
(368, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-28 06:22:20'),
(369, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 08:28:56'),
(370, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 08:46:17'),
(371, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 08:54:52'),
(372, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 09:59:29'),
(373, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 10:58:54'),
(374, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 10:59:27'),
(375, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:15:01'),
(376, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:18:07'),
(377, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:24:46'),
(378, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:33:14'),
(379, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:35:23'),
(380, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 11:41:03'),
(381, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 12:30:02'),
(382, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 13:09:33'),
(383, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 13:25:21'),
(384, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 13:37:00'),
(385, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 13:37:57'),
(386, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 15:53:57'),
(387, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 16:39:38'),
(388, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 17:05:10'),
(389, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 17:05:34'),
(390, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 17:05:58'),
(391, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 17:06:24'),
(392, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-11-30 17:47:58'),
(393, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 18:03:38'),
(394, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 19:04:42'),
(395, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 19:43:10'),
(396, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 20:56:53'),
(397, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 21:51:38'),
(398, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-11-30 23:50:19'),
(399, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-12-01 00:08:01'),
(400, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 00:09:49'),
(401, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 01:09:35'),
(402, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 05:16:29'),
(403, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 06:15:02'),
(404, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-12-01 07:20:05'),
(405, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 07:20:59'),
(406, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 07:26:48'),
(407, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-12-01 07:34:20'),
(408, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 07:34:56'),
(409, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 07:43:08'),
(410, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 07:44:53'),
(411, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 08:15:22'),
(412, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 09:30:56'),
(413, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-01 23:53:59'),
(414, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 00:07:54'),
(415, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 00:17:22'),
(416, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 00:50:56'),
(417, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 00:57:10'),
(418, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 01:28:07'),
(419, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 03:23:32'),
(420, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 16:29:12'),
(421, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-02 16:29:52'),
(422, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 16:36:24'),
(423, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-02 16:40:05'),
(424, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 16:40:12'),
(425, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 19:32:43'),
(426, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 19:39:16'),
(427, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 19:44:40'),
(428, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 19:47:11'),
(429, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 20:05:36'),
(430, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-02 20:14:24'),
(431, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-03 00:39:38'),
(432, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 00:40:23'),
(433, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 00:51:47'),
(434, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-03 01:20:28'),
(435, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 01:23:01'),
(436, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 01:28:46'),
(437, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 01:33:37'),
(438, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 01:40:05'),
(439, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-12-03 01:40:22'),
(440, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 01:44:07'),
(441, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 02:04:23'),
(442, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 05:28:37'),
(443, 1, NULL, 'Application Closed', 'Administrator menutup aplikasi', '127.0.0.1', '2025-12-03 06:46:37'),
(444, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 17:01:07'),
(445, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 17:12:02'),
(446, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-03 17:12:41'),
(447, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 17:13:10'),
(448, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-03 17:13:34'),
(449, 1, NULL, 'Login berhasil', 'Administrator login ke sistem', '127.0.0.1', '2025-12-03 17:14:50'),
(450, 1, NULL, 'Logout', 'Administrator logout dari sistem', '127.0.0.1', '2025-12-03 17:15:50');

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
(3, 'asdf', '2413fb3709b05939f04cf2e92f7d0897fc2596f9ad0b8a9ea855c7bfebaae892', 'asdf', 'asdf@gmail.com', 'user', 1, '2025-09-30 14:17:39', '2025-12-03 17:30:44', '2025-12-03 17:30:44'),
(5, 'qwer', '70f98078fb2c7d7bfb3ae17330b91eaa018110b03896979b4c88bfaed3805906', 'qwer', 'qwer@gmail.com', 'user', 1, '2025-10-01 01:40:51', '2025-12-03 16:56:38', '2025-12-03 16:56:38'),
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
(27, 'Pertemuan', 'harap seluruh OMK melakukan pertemuan', 'OMK', 1, 'Administrator', 'OMK', '2025-11-18 15:09:33', '2025-11-18 15:09:33'),
(29, 'Misa', 'Jumat, 05 Desember 2025 akan diadakan misa jumat pertama, yang akan dipimpin oleh pastor paroki. Misa dimulai pada pukul 18.00 WITA di Gereja Paroki.', 'Umum', 1, 'Administrator', 'Bidang Liturgi', '2025-11-30 20:23:59', '2025-11-30 20:23:59');

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
(3, 'Januari', 'rosario', 'Umat', 'umat', '2000000', 'Kas Gereja', 'Administratif', '', '2025-10-01 06:10:30', '2025-11-26 16:30:50'),
(8, '2025-12-01', 'Misa Natal 2025', 'Seluruh Umat Paroki', 'Tim Liturgi', '5000000', 'Kas Gereja', 'Ibadah', 'Perayaan Misa Natal tahun 2025', '2025-11-27 13:14:46', '2025-11-27 13:14:46'),
(9, '2025-01-01', 'Tahun Baru 2025', 'Seluruh Umat', 'Dewan Pastoral Paroki', '3000000', 'APBG', 'Perayaan', 'Misa Syukur Tahun Baru', '2025-11-27 13:15:20', '2025-11-27 13:15:20');

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

--
-- Dumping data for table `program_kerja_k_kategorial`
--

INSERT INTO `program_kerja_k_kategorial` (`id_program_kerja_k_kategorial`, `program_kerja`, `subyek_sasaran`, `indikator_pencapaian`, `model_bentuk_metode`, `materi`, `tempat`, `waktu`, `pic`, `perincian`, `quantity`, `satuan`, `harga_satuan`, `frekuensi`, `jumlah`, `total`, `keterangan`, `created_by`, `created_at`, `updated_at`) VALUES
(2, 'aa', 'aa', 'aa', 'aa', 'aa', 'aa', '12/12/2025', 'aa', 'aa', 12, '1', 5.00, 1, 12.00, 60.00, 'aaa', NULL, '2025-12-01 03:26:09', '2025-12-01 03:26:09'),
(3, 'a', 'aa', 'aa', 'aa', 'aa', 'aaa', '01/12/2025', 'aa', 'aa', 111, '1', 11.00, 11111, 1233321.00, 13566531.00, 'asahttps://enternal.my.id/flask/keuangan-kategorial', NULL, '2025-12-01 05:26:40', '2025-12-01 05:26:40'),
(4, 'aaa', 'aa', '', 'aa', 'aa', 'aa', '01/12/2025', '', '', 0, '', 0.00, 1, 0.00, 0.00, '', NULL, '2025-12-01 06:17:35', '2025-12-01 06:17:35'),
(5, 'asdfg', 'sdfghb', 'asdfghj', '', '', '', '01/12/2025', '', '', 0, '', 0.00, 1, 0.00, 0.00, '', NULL, '2025-12-01 09:37:03', '2025-12-01 09:37:03');

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
  `reported_by` int(11) DEFAULT NULL COMMENT 'User ID WR yang melaporkan',
  `status` varchar(50) DEFAULT 'Direncanakan' COMMENT 'Status: Direncanakan, Berlangsung, Selesai, Dibatalkan',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja WR (Pastoral Area Work Programs)';

--
-- Dumping data for table `program_kerja_wr`
--

INSERT INTO `program_kerja_wr` (`id_program_kerja_wr`, `kategori`, `estimasi_waktu`, `judul`, `sasaran`, `penanggung_jawab`, `anggaran`, `sumber_anggaran`, `keterangan`, `reported_by`, `status`, `created_at`, `updated_at`) VALUES
(1, 'Rohani', 'Februari', 'Updated Program Kerja', 'Youth', 'Pak Budi', 1000000.00, 'APBG', 'Program sudah diupdate', 1, 'pending', '2025-11-28 03:02:14', '2025-11-28 03:02:35'),
(6, 'Doa', '2025-11-30', 'aa', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaddarrrrrrrrrrrrrrrrrrrrrrrrrrrr', 'aa', 0.00, 'Kas Gereja', 'Riwayat menampilkan rekam jejak aktivitas pengguna maupun perubahan data yang terjadi di dalam sistem. Keberadaan menu ini membantu proses penelusuran, pengawasan, dan kontrol sehingga ketertiban serta akuntabilitas data dapat tetap terjaga.', 3, 'pending', '2025-11-30 10:29:47', '2025-11-30 10:46:15'),
(7, 'Sosial', '2026-02-01', 'Berbagi Kasih', 'Seluruh Umat', 'Bidang Humas', 300000.00, 'Donasi Jemaat', 'Berbasi kasih kepada orang orang yang membutuhkan', 3, 'pending', '2025-11-30 20:29:10', '2025-11-30 20:29:10');

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
(1, 'Romo Andreas Simatupang', 'Laki-laki', 'ST. ALOYSIUS GONZAGA', 'Pastor Paroki', 'Aktif', 'pastor@gereja.com', '081234567890', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_d0019fe5_20250929_225104.jpg', '2025-09-29 14:59:49', '2025-11-18 16:28:36', 'None'),
(2, 'Test Admin', NULL, 'Wilayah Santo Yusuf', 'Pastor Paroki', 'Aktif', 'test@gereja.com', '081234567890', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_9d2906ab_20250929_231409.jpg', '2025-09-29 15:07:04', '2025-09-29 16:14:14', NULL),
(4, 'maydupi', 'Perempuan', 'ST. ALBERTUS AGUNG', 'May', 'Aktif', 'may@gmail.com', '05784564586', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_87c16c00_20250929_224441.jpg', '2025-09-29 15:15:36', '2025-11-18 16:28:19', 'None'),
(6, 'saya', 'Laki-laki', 'WR1', 'Sekrtaris', 'Aktif', '', '', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_aee48c1d_20251020_011201.jpg', '2025-10-19 18:12:05', '2025-10-19 18:12:05', '2025-2027'),
(7, 'Lukas', 'Laki-laki', 'ST. Maria', 'Koordinator', 'Aktif', 'lukas@gmail.com', '08787654321', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_8af53fab_20251105_125727.jpg', '2025-11-05 05:57:31', '2025-11-05 06:38:50', '20252-207'),
(8, 'aaaaaaaa', 'Laki-laki', 'ST. DOMINICO SAVIO', 'koordi', 'Aktif', 'aaaaa@gmail.com', '081234567890', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_4140fd52_20251118_222054.jpg', '2025-11-18 15:21:10', '2025-11-18 15:21:10', '2025-2027'),
(9, 'qwer', 'Laki-laki', 'ST. DOMINICO SAVIO', 'qwer', 'Aktif', 'qwert@gmail.com', '082276543212', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_5656cb12_20251121_001137.jpg', '2025-11-20 17:11:40', '2025-11-20 17:11:40', '2025-2070'),
(10, 'aku', 'Perempuan', 'ST. DOMINICO SAVIO', 'aa', 'Aktif', '', '', 'https://enternal.my.id/flask/uploads/struktur/struktur_new_5ed01409_20251126_202339.jpg', '2025-11-26 13:23:44', '2025-11-26 13:23:44', '2025-2026');

-- --------------------------------------------------------

--
-- Table structure for table `tim_pembina_peserta`
--

CREATE TABLE `tim_pembina_peserta` (
  `id_tim_pembina` int(11) NOT NULL,
  `nama_peserta` varchar(255) NOT NULL,
  `is_manual_entry` tinyint(1) DEFAULT 0,
  `id_jemaat` int(11) DEFAULT NULL,
  `tim_pembina` enum('Liturgi','Katekese','Perkawinan','Keluarga','Konsultasi','Lainnya') NOT NULL,
  `tim_pembina_lainnya` varchar(255) DEFAULT NULL,
  `wilayah_rohani` varchar(255) NOT NULL,
  `jabatan` enum('Pembina','Ketua','Sekretaris','Bendahara','Koordinator','Anggota Sie','Anggota Biasa') NOT NULL,
  `tahun` year(4) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tim_pembina_peserta`
--

INSERT INTO `tim_pembina_peserta` (`id_tim_pembina`, `nama_peserta`, `is_manual_entry`, `id_jemaat`, `tim_pembina`, `tim_pembina_lainnya`, `wilayah_rohani`, `jabatan`, `tahun`, `created_at`, `updated_at`) VALUES
(4, 'Maydupi Astri Turnip', 0, 71, 'Liturgi', NULL, 'ST. YOHANES MARIA VIANNEY', 'Anggota Biasa', '2025', '2025-12-02 03:51:49', '2025-12-02 03:51:49');

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
  ADD KEY `idx_ukuran_file` (`ukuran_file`);

--
-- Indexes for table `jemaat`
--
ALTER TABLE `jemaat`
  ADD PRIMARY KEY (`id_jemaat`),
  ADD KEY `idx_jemaat_nama` (`nama_lengkap`),
  ADD KEY `idx_jemaat_wilayah_rohani` (`wilayah_rohani`),
  ADD KEY `idx_jemaat_status_keanggotaan` (`status_keanggotaan`),
  ADD KEY `idx_status_kekatolikan` (`status_kekatolikan`),
  ADD KEY `idx_jemaat_nama_lengkap` (`nama_lengkap`),
  ADD KEY `idx_jemaat_nama_keluarga` (`nama_keluarga`),
  ADD KEY `idx_jemaat_no_kk` (`no_kk`),
  ADD KEY `idx_jemaat_nik` (`nik`),
  ADD KEY `idx_jemaat_kategori` (`kategori`),
  ADD KEY `idx_jemaat_status_babtis` (`status_babtis`),
  ADD KEY `idx_jemaat_status_ekaristi` (`status_ekaristi`),
  ADD KEY `idx_jemaat_status_krisma` (`status_krisma`),
  ADD KEY `idx_jemaat_status_perkawinan` (`status_perkawinan`),
  ADD KEY `idx_jemaat_created_by_pengguna` (`created_by_pengguna`),
  ADD KEY `idx_jemaat_created_at` (`created_at`);

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
-- Indexes for table `tim_pembina_peserta`
--
ALTER TABLE `tim_pembina_peserta`
  ADD PRIMARY KEY (`id_tim_pembina`),
  ADD KEY `id_jemaat` (`id_jemaat`),
  ADD KEY `idx_tim_pembina` (`tim_pembina`),
  ADD KEY `idx_wilayah_rohani` (`wilayah_rohani`),
  ADD KEY `idx_jabatan` (`jabatan`),
  ADD KEY `idx_tahun` (`tahun`),
  ADD KEY `idx_nama_peserta` (`nama_peserta`);

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
  MODIFY `id_aset` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `buku_kronik`
--
ALTER TABLE `buku_kronik`
  MODIFY `id_kronik` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `client_connections`
--
ALTER TABLE `client_connections`
  MODIFY `id_connection` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=116;

--
-- AUTO_INCREMENT for table `dokumen`
--
ALTER TABLE `dokumen`
  MODIFY `id_dokumen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `jemaat`
--
ALTER TABLE `jemaat`
  MODIFY `id_jemaat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;

--
-- AUTO_INCREMENT for table `kategorial`
--
ALTER TABLE `kategorial`
  MODIFY `id_kategorial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `kegiatan`
--
ALTER TABLE `kegiatan`
  MODIFY `id_kegiatan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `kegiatan_wr`
--
ALTER TABLE `kegiatan_wr`
  MODIFY `id_kegiatan_wr` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `keuangan`
--
ALTER TABLE `keuangan`
  MODIFY `id_keuangan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `keuangan_kategorial`
--
ALTER TABLE `keuangan_kategorial`
  MODIFY `id_keuangan_kategorial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `k_binaan`
--
ALTER TABLE `k_binaan`
  MODIFY `id_binaan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  MODIFY `id_log` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=451;

--
-- AUTO_INCREMENT for table `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `pengumuman`
--
ALTER TABLE `pengumuman`
  MODIFY `id_pengumuman` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `program_kerja`
--
ALTER TABLE `program_kerja`
  MODIFY `id_program_kerja` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `program_kerja_k_kategorial`
--
ALTER TABLE `program_kerja_k_kategorial`
  MODIFY `id_program_kerja_k_kategorial` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

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
  MODIFY `id_program_kerja_wr` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `struktur`
--
ALTER TABLE `struktur`
  MODIFY `id_struktur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tim_pembina_peserta`
--
ALTER TABLE `tim_pembina_peserta`
  MODIFY `id_tim_pembina` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

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
  ADD CONSTRAINT `fk_dokumen_admin` FOREIGN KEY (`uploaded_by_admin`) REFERENCES `admin` (`id_admin`) ON DELETE SET NULL;

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
  ADD CONSTRAINT `tim_pembina_peserta_ibfk_1` FOREIGN KEY (`id_jemaat`) REFERENCES `jemaat` (`id_jemaat`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
