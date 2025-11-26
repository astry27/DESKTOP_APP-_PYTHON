-- Migration 45: Fix keuangan_kategorial table structure
-- Rename columns to match keuangan table: jenis->kategori, kategori->sub_kategori

ALTER TABLE keuangan_kategorial
CHANGE COLUMN jenis kategori ENUM('Pemasukan', 'Pengeluaran') NOT NULL;

ALTER TABLE keuangan_kategorial
CHANGE COLUMN kategori sub_kategori VARCHAR(100) NOT NULL;
