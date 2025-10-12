-- Migration: Add user_id column to kegiatan table for user isolation
-- Date: 2025-10-05

-- Add user_id column to kegiatan table
ALTER TABLE kegiatan
ADD COLUMN IF NOT EXISTS user_id INT NULL AFTER keterangan;

-- Add foreign key constraint to pengguna table (if exists)
-- This will ensure data integrity
-- Note: Uncomment if you want to enforce foreign key constraint
-- ALTER TABLE kegiatan
-- ADD CONSTRAINT fk_kegiatan_user
-- FOREIGN KEY (user_id) REFERENCES pengguna(id_pengguna)
-- ON DELETE SET NULL
-- ON UPDATE CASCADE;

-- Update kategori ENUM to include more options
ALTER TABLE kegiatan
MODIFY COLUMN kategori ENUM('Misa', 'Doa', 'Sosial', 'Pendidikan', 'Ibadah', 'Katekese', 'Rohani', 'Administratif', 'Lainnya') DEFAULT 'Lainnya';

-- Create index on user_id for better query performance
CREATE INDEX IF NOT EXISTS idx_kegiatan_user_id ON kegiatan(user_id);

-- Create index on tanggal_mulai for better date-based queries
CREATE INDEX IF NOT EXISTS idx_kegiatan_tanggal ON kegiatan(tanggal_mulai);
