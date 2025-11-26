-- Create tim_pembina_peserta table
-- This table stores information about church team members (Tim Pembina)

CREATE TABLE IF NOT EXISTS tim_pembina_peserta (
    id_tim_pembina INT AUTO_INCREMENT PRIMARY KEY,
    nama_peserta VARCHAR(255) NOT NULL,
    is_manual_entry BOOLEAN DEFAULT FALSE,
    id_jemaat INT NULL,
    tim_pembina ENUM('Liturgi', 'Katekese', 'Perkawinan', 'Keluarga', 'Konsultasi', 'Lainnya') NOT NULL,
    tim_pembina_lainnya VARCHAR(255) NULL,
    wilayah_rohani VARCHAR(255) NOT NULL,
    jabatan ENUM('Pembina', 'Ketua', 'Sekretaris', 'Bendahara', 'Koordinator', 'Anggota Sie', 'Anggota Biasa') NOT NULL,
    tahun YEAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_jemaat) REFERENCES jemaat(id_jemaat) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create index for faster searching
CREATE INDEX idx_tim_pembina ON tim_pembina_peserta(tim_pembina);
CREATE INDEX idx_wilayah_rohani ON tim_pembina_peserta(wilayah_rohani);
CREATE INDEX idx_jabatan ON tim_pembina_peserta(jabatan);
CREATE INDEX idx_tahun ON tim_pembina_peserta(tahun);
CREATE INDEX idx_nama_peserta ON tim_pembina_peserta(nama_peserta);
