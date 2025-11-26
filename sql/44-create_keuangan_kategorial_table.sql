CREATE TABLE IF NOT EXISTS keuangan_kategorial (
  id_keuangan_kategorial INT AUTO_INCREMENT PRIMARY KEY,
  tanggal DATE NOT NULL,
  kategori ENUM('Pemasukan', 'Pengeluaran') NOT NULL,
  sub_kategori VARCHAR(100) NOT NULL,
  keterangan TEXT,
  jumlah DECIMAL(15, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by_admin INT,
  KEY idx_tanggal (tanggal),
  KEY idx_kategori (kategori),
  KEY idx_sub_kategori (sub_kategori),
  KEY idx_created_by_admin (created_by_admin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
