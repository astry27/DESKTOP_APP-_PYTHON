-- Migration: Update struktur tabel keuangan_kategorial
-- File: sql/migration_keuangan_kategorial_schema.sql
-- Tanggal: 2025-12-01

-- Cek struktur tabel yang ada
DESCRIBE keuangan_kategorial;

-- Jika tabel tidak ada, buat baru
CREATE TABLE IF NOT EXISTS `keuangan_kategorial` (
  `id_keuangan_kategorial` INT(11) NOT NULL AUTO_INCREMENT,
  `tanggal` DATE NOT NULL,
  `kategori` VARCHAR(50) NOT NULL COMMENT 'Pemasukan/Pengeluaran',
  `sub_kategori` VARCHAR(100) DEFAULT NULL COMMENT 'Kategori detail seperti Kolekte, Persembahan, dll',
  `keterangan` TEXT DEFAULT NULL,
  `jumlah` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `created_by_admin` INT(11) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_keuangan_kategorial`),
  KEY `idx_tanggal` (`tanggal`),
  KEY `idx_kategori` (`kategori`),
  KEY `idx_created_by_admin` (`created_by_admin`),
  CONSTRAINT `fk_keuangan_kategorial_admin`
    FOREIGN KEY (`created_by_admin`)
    REFERENCES `admin` (`id_admin`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Jika tabel sudah ada tapi kolom kurang, tambahkan kolom yang hilang:

-- Cek dan tambahkan kolom sub_kategori jika belum ada
SET @col_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'keuangan_kategorial'
    AND COLUMN_NAME = 'sub_kategori'
);

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `keuangan_kategorial` ADD COLUMN `sub_kategori` VARCHAR(100) DEFAULT NULL COMMENT "Kategori detail" AFTER `kategori`',
  'SELECT "Column sub_kategori already exists" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Cek dan tambahkan kolom created_by_admin jika belum ada
SET @col_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'keuangan_kategorial'
    AND COLUMN_NAME = 'created_by_admin'
);

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `keuangan_kategorial` ADD COLUMN `created_by_admin` INT(11) DEFAULT NULL AFTER `jumlah`',
  'SELECT "Column created_by_admin already exists" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Cek dan tambahkan kolom updated_at jika belum ada
SET @col_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'keuangan_kategorial'
    AND COLUMN_NAME = 'updated_at'
);

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `keuangan_kategorial` ADD COLUMN `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER `created_at`',
  'SELECT "Column updated_at already exists" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tampilkan struktur tabel final
DESCRIBE keuangan_kategorial;

-- Tampilkan sample data
SELECT * FROM keuangan_kategorial LIMIT 5;
