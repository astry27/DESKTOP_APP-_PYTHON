-- Migration 36: Restructure tim_pembina table untuk implementasi dropdown Tim Pembina
-- Date: 2025-11-06
-- Purpose: Cleanup dan persiapan tabel tim_pembina untuk dropdown functionality
--
-- Struktur Final tim_pembina table:
--   id_tim_pembina (PK)
--   tim_pembina (VARCHAR) - Dropdown: Liturgi, Katekese, Perkawinan, Keluarga, Konsultasi, Lainnya
--   tanggal_pelantikan (DATE)
--   keterangan (TEXT)
--   created_at (TIMESTAMP)
--   updated_at (TIMESTAMP)
--
-- Custom "Lainnya" values akan disimpan di tabel terpisah: tim_pembina_lainnya

USE entf7819_db-client-server;

-- 1. Drop kolom yang tidak diperlukan
ALTER TABLE tim_pembina DROP COLUMN IF EXISTS akronim;
ALTER TABLE tim_pembina DROP COLUMN IF EXISTS bidang_pelayanan;
ALTER TABLE tim_pembina DROP COLUMN IF EXISTS jenis_pelayanan;
ALTER TABLE tim_pembina DROP COLUMN IF EXISTS jenis_pelayanan_lain;

-- 2. Rename tanggal_pembentukan ke tanggal_pelantikan
ALTER TABLE tim_pembina CHANGE COLUMN IF EXISTS tanggal_pembentukan tanggal_pelantikan DATE DEFAULT NULL;

-- 3. Rename nama_tim ke tim_pembina (ini adalah kolom dropdown dengan nilai predefined)
ALTER TABLE tim_pembina CHANGE COLUMN IF EXISTS nama_tim tim_pembina VARCHAR(100) NOT NULL;

-- 4. Update indexes
ALTER TABLE tim_pembina DROP INDEX IF EXISTS idx_nama_tim;
ALTER TABLE tim_pembina DROP INDEX IF EXISTS idx_bidang_pelayanan;
ALTER TABLE tim_pembina DROP INDEX IF EXISTS idx_jenis_pelayanan;
ALTER TABLE tim_pembina ADD INDEX IF NOT EXISTS idx_tim_pembina (tim_pembina);
