-- Migration: Create program_kerja_dpp and program_kerja_wr tables
-- This migration creates two separate tables for work programs:
-- 1. program_kerja_dpp: Work programs managed by DPP (Dewan Pengurus Paroki/Parish Council)
-- 2. program_kerja_wr: Work programs reported by WR (Wilayah Rohani/Pastoral Areas)

-- Table: program_kerja_dpp
-- Contains work programs created and managed by the parish council (DPP)
CREATE TABLE IF NOT EXISTS program_kerja_dpp (
    id_program_kerja_dpp INT AUTO_INCREMENT PRIMARY KEY,
    kategori VARCHAR(100) NOT NULL COMMENT 'Kategori program: Ibadah, Doa, Katekese, Sosial, Rohani, Administratif, Perayaan, Lainnya',
    estimasi_waktu VARCHAR(50) NOT NULL COMMENT 'Bulan estimasi: Januari-Desember',
    judul VARCHAR(255) NOT NULL COMMENT 'Judul/nama program kerja',
    sasaran VARCHAR(255) COMMENT 'Target/sasaran program atau tokoh yang dituju',
    penanggung_jawab VARCHAR(100) COMMENT 'PIC (Person In Charge)',
    anggaran DECIMAL(15, 2) DEFAULT 0 COMMENT 'Jumlah anggaran dalam Rp',
    sumber_anggaran VARCHAR(100) COMMENT 'Sumber anggaran: Kas Gereja, Donasi Jemaat, Sponsor External, Dana Komisi, APBG, Kolekte Khusus, Lainnya',
    keterangan TEXT COMMENT 'Keterangan/deskripsi lengkap program kerja',
    created_by INT COMMENT 'Admin ID yang membuat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_kategori (kategori),
    INDEX idx_estimasi_waktu (estimasi_waktu),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja DPP (Parish Council Work Programs)';

-- Table: program_kerja_wr
-- Contains work programs reported by WR (pastoral areas/regions)
CREATE TABLE IF NOT EXISTS program_kerja_wr (
    id_program_kerja_wr INT AUTO_INCREMENT PRIMARY KEY,
    kategori VARCHAR(100) NOT NULL COMMENT 'Kategori program: Ibadah, Doa, Katekese, Sosial, Rohani, Administratif, Perayaan, Lainnya',
    estimasi_waktu VARCHAR(50) NOT NULL COMMENT 'Bulan estimasi: Januari-Desember',
    judul VARCHAR(255) NOT NULL COMMENT 'Judul/nama program kerja',
    sasaran VARCHAR(255) COMMENT 'Target/sasaran program atau tokoh yang dituju',
    penanggung_jawab VARCHAR(100) COMMENT 'PIC (Person In Charge)',
    anggaran DECIMAL(15, 2) DEFAULT 0 COMMENT 'Jumlah anggaran dalam Rp',
    sumber_anggaran VARCHAR(100) COMMENT 'Sumber anggaran: Kas Gereja, Donasi Jemaat, Sponsor External, Dana Komisi, APBG, Kolekte Khusus, Lainnya',
    keterangan TEXT COMMENT 'Keterangan/deskripsi lengkap program kerja',
    wilayah_rohani_id INT COMMENT 'ID Wilayah Rohani (Pastoral Area) yang melaporkan program',
    reported_by INT COMMENT 'User ID WR yang melaporkan',
    status VARCHAR(50) DEFAULT 'Direncanakan' COMMENT 'Status: Direncanakan, Berlangsung, Selesai, Dibatalkan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_kategori (kategori),
    INDEX idx_estimasi_waktu (estimasi_waktu),
    INDEX idx_wilayah_rohani_id (wilayah_rohani_id),
    INDEX idx_reported_by (reported_by),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja WR (Pastoral Area Work Programs)';
