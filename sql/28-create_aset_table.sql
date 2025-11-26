-- Migration 28: Create aset table
-- Simple and clean SQL without any complex features

CREATE TABLE aset (
    id_aset INT PRIMARY KEY AUTO_INCREMENT,
    kode_aset VARCHAR(50) NOT NULL UNIQUE,
    nama_aset VARCHAR(200) NOT NULL,
    jenis_aset VARCHAR(50) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    merk_tipe VARCHAR(100),
    tahun_perolehan INT,
    sumber_perolehan VARCHAR(100) NOT NULL,
    nilai DECIMAL(15, 2) DEFAULT 0,
    kondisi VARCHAR(50) NOT NULL,
    lokasi VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    penanggung_jawab VARCHAR(100),
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
