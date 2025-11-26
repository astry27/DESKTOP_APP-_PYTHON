-- Migration 34: Create tim_pembina and tim_pembina_peserta tables
-- Created: 2025-11-05
-- Description: Tables for managing pastoral team (Tim Pembina) with team members

-- Create tim_pembina table
CREATE TABLE IF NOT EXISTS tim_pembina (
    id_tim_pembina INT AUTO_INCREMENT PRIMARY KEY,
    nama_tim VARCHAR(100) NOT NULL UNIQUE,
    akronim VARCHAR(20) DEFAULT NULL,
    bidang_pelayanan VARCHAR(100) NOT NULL,
    tanggal_pembentukan DATE NOT NULL,
    keterangan TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nama_tim (nama_tim),
    INDEX idx_bidang_pelayanan (bidang_pelayanan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create tim_pembina_peserta table (team members)
CREATE TABLE IF NOT EXISTS tim_pembina_peserta (
    id_peserta INT AUTO_INCREMENT PRIMARY KEY,
    id_tim_pembina INT NOT NULL,
    id_jemaat INT NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    wilayah_rohani VARCHAR(100) NOT NULL,
    jabatan VARCHAR(50) NOT NULL,
    koordinator_bidang VARCHAR(100) DEFAULT NULL COMMENT 'Filled when jabatan=Koordinator',
    sie_bidang VARCHAR(100) DEFAULT NULL COMMENT 'Filled when jabatan=Anggota Sie',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tim_pembina) REFERENCES tim_pembina(id_tim_pembina) ON DELETE CASCADE,
    FOREIGN KEY (id_jemaat) REFERENCES jemaat(id_jemaat) ON DELETE CASCADE,
    INDEX idx_id_tim (id_tim_pembina),
    INDEX idx_id_jemaat (id_jemaat),
    INDEX idx_jabatan (jabatan),
    UNIQUE KEY unique_tim_peserta (id_tim_pembina, id_jemaat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add index for faster queries
ALTER TABLE tim_pembina ADD INDEX idx_created_at (created_at);
ALTER TABLE tim_pembina_peserta ADD INDEX idx_created_at (created_at);

-- Migration success message
SELECT 'Migration 34 COMPLETED SUCCESSFULLY!' AS 'Status',
       'tim_pembina table created with fields: id_tim_pembina, nama_tim, akronim, bidang_pelayanan, tanggal_pembentukan, keterangan' AS 'tim_pembina',
       'tim_pembina_peserta table created with fields: id_peserta, id_tim_pembina, id_jemaat, nama_lengkap, wilayah_rohani, jabatan, koordinator_bidang, sie_bidang' AS 'tim_pembina_peserta';
