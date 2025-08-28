-- Update schema for enhanced jemaat functionality
-- Path: sql/update_jemaat_schema.sql

-- Add new columns to jemaat table
ALTER TABLE jemaat 
ADD COLUMN IF NOT EXISTS wilayah_rohani VARCHAR(100),
ADD COLUMN IF NOT EXISTS nama_keluarga VARCHAR(100),
ADD COLUMN IF NOT EXISTS tempat_lahir VARCHAR(100),
ADD COLUMN IF NOT EXISTS hubungan_keluarga ENUM('Kepala Keluarga', 'Istri', 'Anak', 'Famili lain') DEFAULT 'Kepala Keluarga',
ADD COLUMN IF NOT EXISTS pendidikan_terakhir ENUM('SD', 'SMP', 'SMA', 'SMK', 'S1', 'S2', 'S3') DEFAULT 'SMA',
ADD COLUMN IF NOT EXISTS jenis_pekerjaan ENUM('Pelajar', 'Bekerja', 'Tidak Bekerja') DEFAULT 'Bekerja',
ADD COLUMN IF NOT EXISTS detail_pekerjaan VARCHAR(200),

-- Sakramen Babtis
ADD COLUMN IF NOT EXISTS status_babtis ENUM('Belum', 'Sudah') DEFAULT 'Belum',
ADD COLUMN IF NOT EXISTS tempat_babtis VARCHAR(200),
ADD COLUMN IF NOT EXISTS tanggal_babtis DATE,
ADD COLUMN IF NOT EXISTS nama_babtis VARCHAR(100),

-- Sakramen Ekaristi  
ADD COLUMN IF NOT EXISTS status_ekaristi ENUM('Belum', 'Sudah') DEFAULT 'Belum',
ADD COLUMN IF NOT EXISTS tempat_komuni VARCHAR(200),
ADD COLUMN IF NOT EXISTS tanggal_komuni DATE,

-- Sakramen Perkawinan
ADD COLUMN IF NOT EXISTS status_perkawinan ENUM('Belum', 'Sudah') DEFAULT 'Belum',
ADD COLUMN IF NOT EXISTS keuskupan VARCHAR(200),
ADD COLUMN IF NOT EXISTS paroki VARCHAR(200),
ADD COLUMN IF NOT EXISTS kota_perkawinan VARCHAR(200),
ADD COLUMN IF NOT EXISTS tanggal_perkawinan DATE,
ADD COLUMN IF NOT EXISTS status_perkawinan_detail ENUM('Sipil', 'Gereja', 'Sipil dan Gereja'),

-- Status
ADD COLUMN IF NOT EXISTS status_keanggotaan ENUM('Aktif', 'Pindah', 'Meninggal Dunia', 'Tidak Aktif') DEFAULT 'Aktif';

-- Update jenis_kelamin to match new format (L/P instead of Laki-laki/Perempuan)
ALTER TABLE jemaat MODIFY COLUMN jenis_kelamin ENUM('L', 'P', 'Laki-laki', 'Perempuan') DEFAULT 'L';

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_jemaat_wilayah_rohani ON jemaat(wilayah_rohani);
CREATE INDEX IF NOT EXISTS idx_jemaat_nama_keluarga ON jemaat(nama_keluarga);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_keanggotaan ON jemaat(status_keanggotaan);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_babtis ON jemaat(status_babtis);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_ekaristi ON jemaat(status_ekaristi);
CREATE INDEX IF NOT EXISTS idx_jemaat_status_perkawinan ON jemaat(status_perkawinan);

-- Update existing view to include new fields
DROP VIEW IF EXISTS v_statistik_jemaat;
CREATE VIEW v_statistik_jemaat AS
SELECT 
    COUNT(*) as total_jemaat,
    COUNT(CASE WHEN jenis_kelamin IN ('L', 'Laki-laki') THEN 1 END) as total_laki,
    COUNT(CASE WHEN jenis_kelamin IN ('P', 'Perempuan') THEN 1 END) as total_perempuan,
    COUNT(DISTINCT lingkungan) as total_lingkungan,
    COUNT(DISTINCT wilayah) as total_wilayah,
    COUNT(DISTINCT wilayah_rohani) as total_wilayah_rohani,
    COUNT(CASE WHEN status_babtis = 'Sudah' THEN 1 END) as total_sudah_babtis,
    COUNT(CASE WHEN status_ekaristi = 'Sudah' THEN 1 END) as total_sudah_ekaristi,
    COUNT(CASE WHEN status_perkawinan = 'Sudah' THEN 1 END) as total_sudah_menikah,
    COUNT(CASE WHEN status_keanggotaan = 'Aktif' THEN 1 END) as total_aktif
FROM jemaat;