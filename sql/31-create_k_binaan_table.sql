-- Migration 31: Create k_binaan table for Kelompok Binaan
-- Created: 2025-11-05

CREATE TABLE IF NOT EXISTS k_binaan (
    id_binaan INT AUTO_INCREMENT PRIMARY KEY,
    kelompok_binaan VARCHAR(100) NOT NULL,
    kelompok_binaan_lainnya VARCHAR(100),
    nama_lengkap VARCHAR(150) NOT NULL,
    jenis_kelamin VARCHAR(50),
    jabatan VARCHAR(100),
    no_hp VARCHAR(20),
    email VARCHAR(100),
    alamat TEXT,
    wilayah_rohani VARCHAR(100),
    masa_jabatan VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Aktif',
    foto_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_kelompok (kelompok_binaan),
    INDEX idx_nama (nama_lengkap),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
