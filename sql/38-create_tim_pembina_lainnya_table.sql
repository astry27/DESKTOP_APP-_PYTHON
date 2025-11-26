-- Migration 38: Add tim_pembina_lainnya column ke tabel tim_pembina
-- Date: 2025-11-06
-- Purpose: Menambah kolom untuk menyimpan custom value ketika user memilih "Lainnya" dari dropdown
--
-- Struktur:
--   - Column tim_pembina: Dropdown value (Liturgi, Katekese, Perkawinan, Keluarga, Konsultasi, Lainnya)
--   - Column tim_pembina_lainnya: Custom value ketika tim_pembina = 'Lainnya'

USE entf7819_db-client-server;

-- Add tim_pembina_lainnya column untuk menyimpan custom value ketika user pilih "Lainnya"
ALTER TABLE tim_pembina
ADD COLUMN tim_pembina_lainnya VARCHAR(100) DEFAULT NULL COMMENT 'Custom tim pembina value ketika user memilih Lainnya dari dropdown';
