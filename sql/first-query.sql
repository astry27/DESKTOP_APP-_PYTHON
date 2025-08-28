-- Path: sql/database_schema_final.sql

CREATE TABLE IF NOT EXISTS admin (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS pengguna (
    id_pengguna INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    peran ENUM('operator', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS jemaat (
    id_jemaat INT AUTO_INCREMENT PRIMARY KEY,
    nama_lengkap VARCHAR(100) NOT NULL,
    alamat TEXT,
    no_telepon VARCHAR(20),
    email VARCHAR(100),
    tanggal_lahir DATE,
    jenis_kelamin ENUM('Laki-laki', 'Perempuan'),
    status_pernikahan ENUM('Belum Menikah', 'Menikah', 'Duda', 'Janda') DEFAULT 'Belum Menikah',
    pekerjaan VARCHAR(100),
    pendidikan VARCHAR(100),
    baptis_tanggal DATE,
    baptis_tempat VARCHAR(100),
    komuni_tanggal DATE,
    komuni_tempat VARCHAR(100),
    krisma_tanggal DATE,
    krisma_tempat VARCHAR(100),
    nama_ayah VARCHAR(100),
    nama_ibu VARCHAR(100),
    lingkungan VARCHAR(50),
    wilayah VARCHAR(50),
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kegiatan (
    id_kegiatan INT AUTO_INCREMENT PRIMARY KEY,
    nama_kegiatan VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    lokasi VARCHAR(200),
    tanggal_mulai DATE NOT NULL,
    tanggal_selesai DATE NOT NULL,
    waktu_mulai TIME,
    waktu_selesai TIME,
    penanggungjawab VARCHAR(100),
    kategori ENUM('Misa', 'Doa', 'Sosial', 'Pendidikan', 'Lainnya') DEFAULT 'Lainnya',
    status ENUM('Direncanakan', 'Berlangsung', 'Selesai', 'Dibatalkan') DEFAULT 'Direncanakan',
    max_peserta INT,
    biaya DECIMAL(10, 2) DEFAULT 0,
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pengumuman (
    id_pengumuman INT AUTO_INCREMENT PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    isi TEXT NOT NULL,
    tanggal_mulai DATE NOT NULL,
    tanggal_selesai DATE NOT NULL,
    kategori ENUM('Umum', 'Liturgi', 'Kegiatan', 'Sosial', 'Urgent') DEFAULT 'Umum',
    prioritas ENUM('Rendah', 'Normal', 'Tinggi', 'Urgent') DEFAULT 'Normal',
    is_active BOOLEAN DEFAULT TRUE,
    dibuat_oleh_admin INT,
    dibuat_oleh_pengguna INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dibuat_oleh_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (dibuat_oleh_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS keuangan (
    id_keuangan INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE NOT NULL,
    kategori ENUM('Pemasukan', 'Pengeluaran') NOT NULL,
    sub_kategori VARCHAR(100),
    deskripsi TEXT NOT NULL,
    jumlah DECIMAL(10, 2) NOT NULL,
    metode_pembayaran ENUM('Tunai', 'Transfer', 'Cek', 'Lainnya') DEFAULT 'Tunai',
    nomor_referensi VARCHAR(50),
    penanggung_jawab VARCHAR(100),
    bukti_file VARCHAR(255),
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pesan (
    id_pesan INT AUTO_INCREMENT PRIMARY KEY,
    pengirim_admin INT NULL,
    pengirim_pengguna INT NULL,
    pesan TEXT NOT NULL,
    is_broadcast BOOLEAN DEFAULT FALSE,
    broadcast_type ENUM('all', 'specific_client', 'admin_only') DEFAULT 'specific_client',
    target VARCHAR(45) NULL,
    waktu_kirim TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Terkirim', 'Dibaca', 'Error') DEFAULT 'Terkirim',
    FOREIGN KEY (pengirim_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (pengirim_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS dokumen (
    id_dokumen INT AUTO_INCREMENT PRIMARY KEY,
    nama_dokumen VARCHAR(200) NOT NULL,
    jenis_dokumen ENUM('Administrasi', 'Keanggotaan', 'Keuangan', 'Liturgi', 'Legalitas') NOT NULL DEFAULT 'Administrasi',
    file_path VARCHAR(500) NOT NULL,
    ukuran_file BIGINT,
    tipe_file VARCHAR(50),
    kategori ENUM('Surat', 'Laporan', 'Foto', 'Video', 'Audio', 'Lainnya') DEFAULT 'Lainnya',
    keterangan TEXT,
    uploaded_by_admin INT,
    uploaded_by_pengguna INT,
    uploaded_by_name VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS log_aktivitas (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_admin INT NULL,
    id_pengguna INT NULL,
    aktivitas VARCHAR(200) NOT NULL,
    detail TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS api_service_config (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    api_enabled BOOLEAN DEFAULT FALSE,
    last_enabled_by_admin INT,
    last_enabled_by_pengguna INT,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (last_enabled_by_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (last_enabled_by_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS client_connections (
    id_connection INT AUTO_INCREMENT PRIMARY KEY,
    client_ip VARCHAR(45) NOT NULL,
    hostname VARCHAR(100),
    status ENUM('Terhubung', 'Terputus') DEFAULT 'Terhubung',
    connect_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disconnect_time TIMESTAMP NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS server_sessions (
    id_session INT AUTO_INCREMENT PRIMARY KEY,
    server_host VARCHAR(100) NOT NULL,
    server_port INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('Running', 'Stopped') DEFAULT 'Running',
    started_by_admin INT,
    started_by_pengguna INT,
    FOREIGN KEY (started_by_admin) REFERENCES admin(id_admin) ON DELETE SET NULL,
    FOREIGN KEY (started_by_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE SET NULL
);

INSERT INTO admin (username, password, nama_lengkap, email)
VALUES (
    'admin',
    SHA2('admin123', 256),
    'Administrator Gereja',
    'admin@gereja.com'
);

INSERT INTO pengguna (username, password, nama_lengkap, email, peran)
VALUES (
    'operator',
    SHA2('operator123', 256),
    'Operator Sistem',
    'operator@gereja.com',
    'operator'
),
(
    'user',
    SHA2('user123', 256),
    'User Default',
    'user@gmail.com',
    'user'
);

INSERT INTO api_service_config (api_enabled) 
VALUES (FALSE);

CREATE INDEX idx_admin_username ON admin(username);
CREATE INDEX idx_pengguna_username ON pengguna(username);
CREATE INDEX idx_jemaat_nama ON jemaat(nama_lengkap);
CREATE INDEX idx_jemaat_lingkungan ON jemaat(lingkungan);
CREATE INDEX idx_jemaat_wilayah ON jemaat(wilayah);
CREATE INDEX idx_kegiatan_tanggal ON kegiatan(tanggal_mulai, tanggal_selesai);
CREATE INDEX idx_pengumuman_tanggal ON pengumuman(tanggal_mulai, tanggal_selesai);
CREATE INDEX idx_pengumuman_active ON pengumuman(is_active);
CREATE INDEX idx_keuangan_tanggal ON keuangan(tanggal);
CREATE INDEX idx_keuangan_kategori ON keuangan(kategori);
CREATE INDEX idx_pesan_waktu ON pesan(waktu_kirim);
CREATE INDEX idx_log_timestamp ON log_aktivitas(timestamp);
CREATE INDEX idx_dokumen_jenis ON dokumen(jenis_dokumen);
CREATE INDEX idx_dokumen_tipe ON dokumen(tipe_file);
CREATE INDEX idx_dokumen_upload_date ON dokumen(upload_date);
CREATE INDEX idx_client_ip ON client_connections(client_ip);
CREATE INDEX idx_client_status ON client_connections(status);
CREATE INDEX idx_server_status ON server_sessions(status);

CREATE VIEW v_statistik_jemaat AS
SELECT 
    COUNT(*) as total_jemaat,
    COUNT(CASE WHEN jenis_kelamin = 'Laki-laki' THEN 1 END) as total_laki,
    COUNT(CASE WHEN jenis_kelamin = 'Perempuan' THEN 1 END) as total_perempuan,
    COUNT(DISTINCT lingkungan) as total_lingkungan,
    COUNT(DISTINCT wilayah) as total_wilayah
FROM jemaat;

CREATE VIEW v_kegiatan_mendatang AS
SELECT 
    id_kegiatan,
    nama_kegiatan,
    lokasi,
    tanggal_mulai,
    tanggal_selesai,
    waktu_mulai,
    waktu_selesai,
    penanggungjawab,
    kategori,
    DATEDIFF(tanggal_mulai, CURDATE()) as hari_tersisa
FROM kegiatan
WHERE tanggal_mulai >= CURDATE()
    AND status = 'Direncanakan'
ORDER BY tanggal_mulai;

CREATE VIEW v_pengumuman_aktif AS
SELECT 
    id_pengumuman,
    judul,
    isi,
    tanggal_mulai,
    tanggal_selesai,
    kategori,
    prioritas
FROM pengumuman
WHERE is_active = TRUE
    AND CURDATE() BETWEEN tanggal_mulai AND tanggal_selesai
ORDER BY prioritas DESC, tanggal_mulai DESC;

CREATE VIEW v_laporan_keuangan_bulanan AS
SELECT 
    YEAR(tanggal) as tahun,
    MONTH(tanggal) as bulan,
    kategori,
    SUM(jumlah) as total,
    COUNT(*) as jumlah_transaksi
FROM keuangan
GROUP BY YEAR(tanggal), MONTH(tanggal), kategori
ORDER BY tahun DESC, bulan DESC;

CREATE VIEW v_active_clients AS
SELECT 
    client_ip,
    hostname,
    connect_time,
    last_activity,
    TIMESTAMPDIFF(MINUTE, last_activity, NOW()) as minutes_inactive
FROM client_connections 
WHERE status = 'Terhubung'
ORDER BY last_activity DESC;

CREATE VIEW v_current_server_status AS
SELECT 
    s.*,
    CASE 
        WHEN s.end_time IS NULL THEN TIMESTAMPDIFF(SECOND, s.start_time, NOW())
        ELSE TIMESTAMPDIFF(SECOND, s.start_time, s.end_time)
    END as uptime_seconds
FROM server_sessions s
WHERE s.status = 'Running' 
ORDER BY s.start_time DESC 
LIMIT 1;