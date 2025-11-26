-- Migration 30: Create wilayah_rohani table for Pengurus Wilayah Rohani
-- Created: 2025-11-05

CREATE TABLE IF NOT EXISTS wilayah_rohani (
    id_wilayah INT AUTO_INCREMENT PRIMARY KEY,
    wilayah_rohani VARCHAR(100) NOT NULL,
    nama_lengkap VARCHAR(150) NOT NULL,
    jenis_kelamin VARCHAR(50),
    jabatan VARCHAR(100),
    no_hp VARCHAR(20),
    email VARCHAR(100),
    alamat TEXT,
    masa_jabatan VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Aktif',
    foto_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_wilayah (wilayah_rohani),
    INDEX idx_nama (nama_lengkap),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
