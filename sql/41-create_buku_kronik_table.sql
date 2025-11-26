-- SQL Migration: Create Buku Kronik Table
-- Description: Tabel untuk menyimpan pencatatan peristiwa/kejadian di gereja
-- Date: 2025-11-11

-- Drop table if exists (for fresh migration)
DROP TABLE IF EXISTS buku_kronik;

-- Create buku_kronik table
CREATE TABLE buku_kronik (
    id_kronik INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE NOT NULL,
    peristiwa VARCHAR(255) NOT NULL,
    keterangan TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tanggal (tanggal),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add comment to table
ALTER TABLE buku_kronik COMMENT='Tabel untuk pencatatan peristiwa/kejadian gereja';

-- Add comments to columns
ALTER TABLE buku_kronik MODIFY COLUMN id_kronik INT AUTO_INCREMENT COMMENT='ID unik kronik';
ALTER TABLE buku_kronik MODIFY COLUMN tanggal DATE NOT NULL COMMENT='Tanggal peristiwa terjadi';
ALTER TABLE buku_kronik MODIFY COLUMN peristiwa VARCHAR(255) NOT NULL COMMENT='Nama/deskripsi peristiwa (wajib ada)';
ALTER TABLE buku_kronik MODIFY COLUMN keterangan TEXT COMMENT='Deskripsi detail peristiwa (opsional)';
ALTER TABLE buku_kronik MODIFY COLUMN created_by INT COMMENT='User ID yang membuat entry';
ALTER TABLE buku_kronik MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT='Waktu entry dibuat';
ALTER TABLE buku_kronik MODIFY COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT='Waktu entry terakhir diubah';
