-- Migration: Create program_kerja_k_kategorial table
-- This migration creates the program_kerja_k_kategorial table for K. Kategorial work programs

-- Table: program_kerja_k_kategorial
-- Contains detailed work programs for K. Kategorial (Kategorial Gereja)
CREATE TABLE IF NOT EXISTS program_kerja_k_kategorial (
    id_program_kerja_k_kategorial INT AUTO_INCREMENT PRIMARY KEY,
    program_kerja VARCHAR(255) NOT NULL COMMENT 'Nama program kerja',
    subyek_sasaran VARCHAR(255) NOT NULL COMMENT 'Subyek/sasaran program',
    indikator_pencapaian TEXT COMMENT 'Indikator pencapaian program',
    model_bentuk_metode TEXT COMMENT 'Model, bentuk dan metode pelaksanaan',
    materi VARCHAR(255) COMMENT 'Materi yang akan disampaikan',
    tempat VARCHAR(255) COMMENT 'Lokasi pelaksanaan program',
    waktu VARCHAR(100) COMMENT 'Waktu pelaksanaan (tanggal/bulan/jam)',
    pic VARCHAR(100) COMMENT 'Person In Charge (Penanggung Jawab)',
    perincian TEXT COMMENT 'Perincian detail program',
    quantity INT COMMENT 'Jumlah/quantity',
    satuan VARCHAR(50) COMMENT 'Satuan (orang, paket, set, dll)',
    harga_satuan DECIMAL(15, 2) DEFAULT 0 COMMENT 'Harga per satuan (Rp)',
    frekuensi INT DEFAULT 1 COMMENT 'Frekuensi pelaksanaan',
    jumlah DECIMAL(15, 2) DEFAULT 0 COMMENT 'Jumlah total (quantity x frekuensi)',
    total DECIMAL(15, 2) DEFAULT 0 COMMENT 'Total biaya (jumlah x harga_satuan)',
    keterangan TEXT COMMENT 'Keterangan tambahan',
    created_by INT COMMENT 'User/Admin ID yang membuat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_program_kerja (program_kerja),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Program Kerja K. Kategorial (Kategorial Church Programs)';

-- Table: program_kerja_k_kategorial_budget
-- Stores multiple budget sources for each program (many-to-many relationship)
CREATE TABLE IF NOT EXISTS program_kerja_k_kategorial_budget (
    id_budget INT AUTO_INCREMENT PRIMARY KEY,
    id_program_kerja_k_kategorial INT NOT NULL,
    sumber_anggaran VARCHAR(100) NOT NULL COMMENT 'Sumber anggaran: KK (Komisi), WR (Wilayah Rohani), Paroki, Swadaya, Lainnya',
    sumber_anggaran_lainnya VARCHAR(255) COMMENT 'Keterangan jika sumber anggaran adalah Lainnya',
    jumlah_anggaran DECIMAL(15, 2) NOT NULL COMMENT 'Jumlah anggaran dari sumber ini',
    nama_akun_pengeluaran VARCHAR(255) COMMENT 'Nama akun pengeluaran',
    sumber_pembiayaan VARCHAR(255) COMMENT 'Sumber pembiayaan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_program_kerja_k_kategorial) REFERENCES program_kerja_k_kategorial(id_program_kerja_k_kategorial) ON DELETE CASCADE,
    INDEX idx_program_id (id_program_kerja_k_kategorial),
    INDEX idx_sumber_anggaran (sumber_anggaran)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Budget sources for K. Kategorial programs';

-- Table: program_kerja_k_kategorial_evaluation
-- Stores evaluation data for each program
CREATE TABLE IF NOT EXISTS program_kerja_k_kategorial_evaluation (
    id_evaluation INT AUTO_INCREMENT PRIMARY KEY,
    id_program_kerja_k_kategorial INT NOT NULL,
    evaluasi_program VARCHAR(50) COMMENT 'Hasil evaluasi: <50%, 50-69%, 70-84%, 85-100%, Risiko',
    status VARCHAR(50) DEFAULT 'Direncanakan' COMMENT 'Status program: Direncanakan, Berlangsung, Selesai, Dibatalkan',
    tindak_lanjut TEXT COMMENT 'Tindak lanjut dari evaluasi',
    keterangan_evaluasi TEXT COMMENT 'Keterangan evaluasi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_program_kerja_k_kategorial) REFERENCES program_kerja_k_kategorial(id_program_kerja_k_kategorial) ON DELETE CASCADE,
    INDEX idx_program_id (id_program_kerja_k_kategorial)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Evaluation data for K. Kategorial programs';
