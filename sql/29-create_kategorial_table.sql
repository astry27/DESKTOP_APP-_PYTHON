-- Migration 29: Create Komunitas Kategorial Table
-- Table untuk manajemen Pengurus Komunitas Kategorial di gereja

CREATE TABLE IF NOT EXISTS kategorial (
    id_kategorial INT AUTO_INCREMENT PRIMARY KEY,

    -- Identifikasi
    kelompok_kategorial VARCHAR(50) NOT NULL,
    kelompok_kategorial_lainnya VARCHAR(100),

    -- Data Pribadi
    nama_lengkap VARCHAR(150) NOT NULL,
    jabatan VARCHAR(100),
    no_hp VARCHAR(20),
    email VARCHAR(100),
    alamat TEXT,

    -- Organisasi
    wilayah_rohani VARCHAR(100),
    masa_jabatan VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Aktif',

    -- File
    foto_path VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_kelompok (kelompok_kategorial),
    INDEX idx_nama (nama_lengkap),
    INDEX idx_status (status),
    INDEX idx_wilayah (wilayah_rohani)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some default komunitaskategorial options for dropdown
-- (These are reference data, adjust as needed)
