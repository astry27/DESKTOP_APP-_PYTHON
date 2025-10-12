-- Migration 11: Cleanup pengumuman table structure
-- Menghapus kolom yang tidak digunakan di UI dan menyederhanakan struktur tabel
-- UI Components: Tanggal (dari created_at), Pembuat, Sasaran/Tujuan, Judul Pengumuman, Isi Pengumuman, Penanggung Jawab

USE `entf7819_db-client-server`;

-- 1. Backup data penting sebelum menghapus kolom
-- Update kolom pembuat dari relasi admin/pengguna jika masih NULL
UPDATE pengumuman p
LEFT JOIN admin a ON p.dibuat_oleh_admin = a.id_admin
LEFT JOIN pengguna u ON p.dibuat_oleh_pengguna = u.id_pengguna
SET p.pembuat = COALESCE(
    p.pembuat,
    a.nama_lengkap,
    u.nama_lengkap,
    'Administrator'
)
WHERE p.pembuat IS NULL OR p.pembuat = '';

-- 2. Tambah kolom penanggung_jawab jika belum ada
ALTER TABLE pengumuman
ADD COLUMN IF NOT EXISTS penanggung_jawab VARCHAR(100) DEFAULT NULL;

-- 3. Set default penanggung_jawab sama dengan pembuat untuk data existing
UPDATE pengumuman
SET penanggung_jawab = COALESCE(pembuat, 'Administrator')
WHERE penanggung_jawab IS NULL;

-- 4. Pastikan kolom sasaran terisi dengan default 'Umum' jika masih kosong
UPDATE pengumuman
SET sasaran = 'Umum'
WHERE sasaran IS NULL OR sasaran = '' OR sasaran = 'Semua Jemaat';

-- 5. Hapus kolom yang tidak digunakan di UI
-- Menghapus: tanggal_mulai, tanggal_selesai, kategori, prioritas, dibuat_oleh_admin, dibuat_oleh_pengguna
ALTER TABLE pengumuman
DROP COLUMN IF EXISTS tanggal_mulai,
DROP COLUMN IF EXISTS tanggal_selesai,
DROP COLUMN IF EXISTS kategori,
DROP COLUMN IF EXISTS prioritas,
DROP COLUMN IF EXISTS dibuat_oleh_admin,
DROP COLUMN IF EXISTS dibuat_oleh_pengguna;

-- 6. Pastikan kolom yang tersisa memiliki tipe data dan default yang sesuai
ALTER TABLE pengumuman
MODIFY COLUMN judul VARCHAR(200) NOT NULL,
MODIFY COLUMN isi TEXT NOT NULL,
MODIFY COLUMN sasaran VARCHAR(100) NOT NULL DEFAULT 'Umum',
MODIFY COLUMN pembuat VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN penanggung_jawab VARCHAR(100) NOT NULL DEFAULT 'Administrator',
MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1,
MODIFY COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
MODIFY COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 7. Add index untuk performa query
CREATE INDEX IF NOT EXISTS idx_pengumuman_penanggung_jawab ON pengumuman(penanggung_jawab);
CREATE INDEX IF NOT EXISTS idx_pengumuman_pembuat ON pengumuman(pembuat);
CREATE INDEX IF NOT EXISTS idx_pengumuman_sasaran ON pengumuman(sasaran);
CREATE INDEX IF NOT EXISTS idx_pengumuman_created_at ON pengumuman(created_at);
CREATE INDEX IF NOT EXISTS idx_pengumuman_is_active ON pengumuman(is_active);

-- Verification: Show table structure
SELECT 'Struktur tabel pengumuman setelah migration:' AS info;
SHOW COLUMNS FROM pengumuman;

-- Verification: Show sample data
SELECT
    id_pengumuman,
    judul,
    pembuat,
    penanggung_jawab,
    sasaran,
    LEFT(isi, 50) AS isi_preview,
    is_active,
    DATE_FORMAT(created_at, '%W, %d %M %Y') AS tanggal_display,
    created_at
FROM pengumuman
ORDER BY created_at DESC
LIMIT 5;
