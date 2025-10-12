-- =====================================================
-- SCRIPT: Membuat tabel program_kerja
-- AMAN: Hanya membuat tabel baru, tidak mengubah yang ada
-- =====================================================

-- Cek dan buat tabel program_kerja jika belum ada
CREATE TABLE IF NOT EXISTS program_kerja (
    id_program_kerja INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE NOT NULL,
    judul VARCHAR(200) NOT NULL,
    sasaran VARCHAR(200) DEFAULT '',
    penanggung_jawab VARCHAR(100) DEFAULT '',
    anggaran VARCHAR(50) DEFAULT '',
    sumber_anggaran VARCHAR(100) DEFAULT 'Kas Gereja',
    kategori VARCHAR(100) DEFAULT '',
    lokasi VARCHAR(200) DEFAULT '',
    deskripsi TEXT,
    waktu VARCHAR(50) DEFAULT '',
    status VARCHAR(50) DEFAULT 'Direncanakan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_tanggal (tanggal),
    INDEX idx_status (status),
    INDEX idx_kategori (kategori)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabel untuk manajemen program kerja tahunan';

-- Cek apakah tabel berhasil dibuat
SELECT 'Tabel program_kerja berhasil dibuat atau sudah ada' as status;

-- Tampilkan struktur tabel untuk konfirmasi
DESCRIBE program_kerja;