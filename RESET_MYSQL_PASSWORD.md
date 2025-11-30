# Cara Reset Password MySQL Root di Windows

## Langkah 1: Stop MySQL Service
1. Buka Command Prompt sebagai **Administrator**
2. Jalankan command:
```cmd
net stop MySQL80
```

## Langkah 2: Start MySQL dengan Mode Skip Grant Tables
1. Buka Command Prompt baru sebagai **Administrator**
2. Cari lokasi instalasi MySQL (biasanya di `C:\Program Files\MySQL\MySQL Server 8.0\bin`)
3. Jalankan command:
```cmd
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
mysqld --console --skip-grant-tables --shared-memory
```
4. **JANGAN TUTUP WINDOW INI** - biarkan tetap running

## Langkah 3: Connect ke MySQL dan Reset Password
1. Buka Command Prompt **BARU** (yang ketiga) sebagai **Administrator**
2. Jalankan command:
```cmd
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
mysql -u root
```

3. Di MySQL prompt, jalankan query ini (ganti `new_password_here` dengan password yang Anda inginkan):

**Untuk MySQL 8.0:**
```sql
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password_here';
FLUSH PRIVILEGES;
exit
```

**ATAU jika ingin tanpa password (tidak disarankan):**
```sql
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '';
FLUSH PRIVILEGES;
exit
```

## Langkah 4: Restart MySQL Normal
1. Kembali ke window mysqld yang running (Langkah 2), tekan `Ctrl+C` untuk stop
2. Start MySQL service normal:
```cmd
net start MySQL80
```

## Langkah 5: Test Koneksi
Test dengan password baru:
```cmd
mysql -u root -p
```
Masukkan password yang baru Anda set.

## Langkah 6: Update .env File
Setelah berhasil, update file `.env` di project:
```env
DB_PASSWORD=new_password_here
```

Atau jika tanpa password:
```env
DB_PASSWORD=
```

---

## Troubleshooting

### Jika lokasi MySQL berbeda:
Cari lokasi MySQL dengan cara:
1. Buka Services (tekan `Win+R`, ketik `services.msc`)
2. Cari service "MySQL80"
3. Klik kanan > Properties
4. Lihat "Path to executable" untuk tahu lokasi instalasi MySQL

### Jika error "mysqld is not recognized":
Tambahkan path MySQL ke environment variable atau gunakan full path:
```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --console --skip-grant-tables --shared-memory
```
