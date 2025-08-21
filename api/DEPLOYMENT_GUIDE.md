# Path: api/DEPLOYMENT_GUIDE.md

# Flask API Deployment Guide untuk Shared Hosting

Panduan lengkap untuk deploy Flask API manajemen Gereja Katolik ke shared hosting enternal.my.id

## Prerequisites

1. **Shared Hosting Requirements:**
   - Python 3.8+ support
   - MySQL database
   - SSL Certificate (HTTPS)
   - .htaccess support
   - Domain: enternal.my.id/flask

2. **Local Development:**
   - Python 3.8+
   - MySQL 5.7+
   - Git

## Step 1: Persiapan Database

### 1.1 Buat Database di cPanel
```sql
-- Nama database: enternal_gereja_api
-- Username: enternal_gereja
-- Password: [your_secure_password]
```

### 1.2 Import Schema Database
```bash
# Via phpMyAdmin atau MySQL command line
mysql -u enternal_gereja -p enternal_gereja_api < api_schema.sql
```

## Step 2: Konfigurasi Environment

### 2.1 Edit Configuration
Edit file `config.py`:

```python
class ProductionConfig(Config):
    # Database untuk production
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://enternal_gereja:YOUR_PASSWORD@localhost/enternal_gereja_api'
    
    # Secret key untuk production
    SECRET_KEY = 'your-very-secure-secret-key-here'
    
    # CORS untuk domain production
    CORS_ORIGINS = [
        'https://enternal.my.id',
        'https://www.enternal.my.id'
    ]
```

### 2.2 Set Environment Variables
Buat file `.env` (jangan commit ke Git):

```bash
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://enternal_gereja:YOUR_PASSWORD@localhost/enternal_gereja_api
SECRET_KEY=your-very-secure-secret-key-here
```

## Step 3: Upload Files ke Shared Hosting

### 3.1 Struktur Directory di Server
```
public_html/
└── flask/
    ├── app.py
    ├── wsgi.py
    ├── config.py
    ├── init_db.py
    ├── requirements.txt
    ├── .htaccess
    ├── .env
    ├── models/
    │   ├── __init__.py
    │   ├── server_registry.py
    │   ├── api_log.py
    │   └── user_session.py
    └── routes/
        ├── __init__.py
        ├── auth.py
        ├── server_management.py
        ├── data_access.py
        └── monitoring.py
```

### 3.2 Upload via FTP/cPanel File Manager
1. Zip semua file API
2. Upload ke `/public_html/flask/`
3. Extract files
4. Set permissions untuk directory (755)

## Step 4: Install Dependencies

### 4.1 Via SSH (jika tersedia)
```bash
cd /public_html/flask
pip install -r requirements.txt --user
```

### 4.2 Via cPanel Python App (alternative)
1. Buka cPanel → Python App
2. Create New App
3. Set Application Root: `/public_html/flask`
4. Set Application URL: `enternal.my.id/flask`
5. Install dependencies dari requirements.txt

## Step 5: Database Initialization

### 5.1 Initialize Database
```bash
cd /public_html/flask
python init_db.py init
```

### 5.2 Verify Database
```bash
python init_db.py verify
```

## Step 6: Test Deployment

### 6.1 Test Health Endpoint
```bash
curl https://enternal.my.id/flask/api/health
```

Expected response:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-20T10:30:00",
    "version": "1.0.0"
}
```

### 6.2 Test API Endpoints
```bash
# Test login
curl -X POST https://enternal.my.id/flask/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "server_host": "192.168.1.100",
    "server_port": 9000
  }'
```

## Step 7: Security Configuration

### 7.1 File Permissions
```bash
chmod 644 *.py
chmod 644 .htaccess
chmod 600 .env
chmod 755 models/
chmod 755 routes/
```

### 7.2 Hide Sensitive Files
Pastikan `.htaccess` sudah configured untuk hide:
- `.env` files
- `.py` source files dari direct access
- Log files
- Configuration files

## Step 8: Monitoring & Maintenance

### 8.1 Setup Logging
```python
# Tambahkan di config.py
LOG_FILE = '/home/username/logs/flask_api.log'
LOG_LEVEL = 'INFO'
```

### 8.2 Database Backup Schedule
```bash
# Setup cron job untuk backup harian
0 2 * * * mysqldump -u enternal_gereja -p enternal_gereja_api > /home/username/backups/api_backup_$(date +\%Y\%m\%d).sql
```

### 8.3 Cleanup Old Data
```bash
# Weekly cleanup cron job
0 3 * * 0 cd /public_html/flask && python init_db.py cleanup
```

## Step 9: SSL & Domain Configuration

### 9.1 SSL Certificate
Pastikan SSL certificate sudah terinstall untuk domain enternal.my.id

### 9.2 Force HTTPS
Tambahkan di `.htaccess`:
```apache
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

## Step 10: Integration dengan Server Lokal

### 10.1 Update Server Code
Ganti server HTTP code dengan `FlaskServerAPI` class:

```python
# Path: server/main_http_refactored.py
from server_http_flask import FlaskServerAPI

# Ganti ServerAPI dengan FlaskServerAPI
self.server_api = FlaskServerAPI(host, port, self.db)
```

### 10.2 Register Server
```python
# Di server lokal
success, message = server_api.register_to_flask_api(
    username="admin",
    password="admin123", 
    server_name="Gereja Santa Maria",
    church_name="Paroki Santa Maria Ratu Damai"
)
```

## Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   - Check error logs: `/home/username/logs/error_log`
   - Verify database connection
   - Check file permissions

2. **Database Connection Failed**
   - Verify database credentials
   - Check MySQL service status
   - Test connection manually

3. **Import Errors**
   - Ensure all dependencies installed
   - Check Python path
   - Verify file structure

4. **CORS Issues**
   - Update CORS_ORIGINS in config
   - Check .htaccess CORS headers
   - Verify domain configuration

### Debug Mode
```python
# Temporary enable debug (remove for production)
application.config['DEBUG'] = True
```

## Maintenance Commands

```bash
# Check API status
curl https://enternal.my.id/flask/api/health

# View recent logs
tail -f /home/username/logs/flask_api.log

# Database maintenance
python init_db.py cleanup

# Update application
git pull origin main
pip install -r requirements.txt --user
```

## Security Checklist

- [ ] Database credentials secured
- [ ] Secret key is strong and unique
- [ ] SSL certificate installed
- [ ] HTTPS enforced
- [ ] Sensitive files hidden
- [ ] File permissions correct
- [ ] CORS properly configured
- [ ] Error logging enabled
- [ ] Backup schedule setup
- [ ] Monitoring configured

## Performance Optimization

1. **Database Optimization**
   - Regular OPTIMIZE TABLE
   - Monitor slow queries
   - Index optimization

2. **Caching**
   - Enable Flask-Caching
   - Use Redis if available
   - Cache static responses

3. **Monitoring**
   - Setup response time monitoring
   - Monitor API usage
   - Track error rates

## Support

Jika mengalami masalah deployment:

1. Check logs terlebih dahulu
2. Verify semua configuration
3. Test endpoints secara individual
4. Contact hosting support jika diperlukan

## Update Procedure

1. Backup current files dan database
2. Upload new files
3. Run database migrations jika ada
4. Test functionality
5. Monitor for errors

---

**Note:** Selalu backup data sebelum melakukan deployment atau update!