-- Add foto_profil column to pengguna table
ALTER TABLE `pengguna`
ADD COLUMN `foto_profil` VARCHAR(255) DEFAULT NULL AFTER `email`;

-- Add foto_profil column to admin table
ALTER TABLE `admin`
ADD COLUMN `foto_profil` VARCHAR(255) DEFAULT NULL AFTER `email`;
