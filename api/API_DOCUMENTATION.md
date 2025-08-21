# Path: api/API_DOCUMENTATION.md

# Flask API Documentation - Gereja Katolik Management System

API untuk manajemen akses Client-Server aplikasi Gereja Katolik yang di-host di enternal.my.id/flask

## Base URL
```
https://enternal.my.id/flask
```

## Authentication

Semua endpoint (kecuali login dan health check) memerlukan Bearer token authentication.

### Headers
```
Authorization: Bearer <token>
Content-Type: application/json
```

## Error Responses

Semua error response menggunakan format:
```json
{
    "success": false,
    "error": "Error message description",
    "status_code": 400
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `408` - Request Timeout
- `500` - Internal Server Error
- `503` - Service Unavailable

---

# Authentication Endpoints

## POST /api/auth/login

Login ke sistem dengan menggunakan kredensial server lokal.

### Request Body
```json
{
    "username": "admin",
    "password": "admin123",
    "server_host": "192.168.1.100",
    "server_port": 9000
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "nama_lengkap": "Administrator",
        "peran": "admin"
    },
    "server_info": {
        "host": "192.168.1.100",
        "port": 9000
    },
    "expires_at": "2024-01-21T10:30:00Z"
}
```

### Error Response (401)
```json
{
    "success": false,
    "error": "Invalid credentials"
}
```

---

## POST /api/auth/logout

Logout dari sistem dan invalidate token.

### Headers Required
```
Authorization: Bearer <token>
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Logout successful"
}
```

---

## POST /api/auth/refresh

Refresh JWT token untuk extend session.

### Headers Required
```
Authorization: Bearer <token>
```

### Success Response (200)
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-01-21T10:30:00Z"
}
```

---

## POST /api/auth/verify

Verify token validity.

### Headers Required
```
Authorization: Bearer <token>
```

### Success Response (200)
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "username": "admin"
    },
    "server_info": {
        "host": "192.168.1.100",
        "port": 9000
    },
    "expires_at": "2024-01-21T10:30:00Z"
}
```

---

# Server Management Endpoints

## POST /api/server/start

Start server lokal melalui API.

### Request Body
```json
{
    "server_host": "192.168.1.100",
    "server_port": 9000,
    "config": {
        "max_connections": 100,
        "timeout": 30
    }
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Server started successfully",
    "server_info": {
        "id": 1,
        "server_name": "Gereja Santa Maria",
        "status": "online",
        "host": "192.168.1.100",
        "port": 9000
    }
}
```

---

## POST /api/server/stop

Stop server lokal melalui API.

### Request Body
```json
{
    "server_host": "192.168.1.100",
    "server_port": 9000
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Server stopped successfully",
    "server_info": {
        "status": "offline"
    }
}
```

---

## POST /api/server/restart

Restart server lokal melalui API.

### Request Body
```json
{
    "server_host": "192.168.1.100",
    "server_port": 9000,
    "config": {
        "max_connections": 100
    }
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Server restarted successfully"
}
```

---

## GET /api/server/status

Get status server lokal.

### Query Parameters
- `host` (required) - Server host
- `port` (required) - Server port

### Success Response (200)
```json
{
    "server_info": {
        "id": 1,
        "server_name": "Gereja Santa Maria",
        "status": "online",
        "last_ping": "2024-01-20T10:30:00Z"
    },
    "server_data": {
        "status": "healthy",
        "uptime": 3600,
        "connections": 5
    },
    "is_online": true
}
```

---

# Data Access Endpoints

## GET /api/data/jemaat

Get data jemaat dari server lokal.

### Query Parameters
- `limit` (optional) - Limit results (default: 100)
- `offset` (optional) - Offset for pagination (default: 0)
- `search` (optional) - Search keyword

### Success Response (200)
```json
{
    "success": true,
    "data": [
        {
            "id_jemaat": 1,
            "nama_lengkap": "Yohanes Baptista",
            "alamat": "Jl. Merdeka No. 123",
            "no_telepon": "081234567890",
            "email": "yohanes@example.com",
            "tanggal_lahir": "1980-01-15",
            "jenis_kelamin": "Laki-laki"
        }
    ],
    "total": 1
}
```

---

## POST /api/data/jemaat

Tambah data jemaat baru.

### Request Body
```json
{
    "nama_lengkap": "Maria Magdalena",
    "alamat": "Jl. Sudirman No. 456",
    "no_telepon": "081234567891",
    "email": "maria@example.com",
    "tanggal_lahir": "1985-03-20",
    "jenis_kelamin": "Perempuan"
}
```

### Success Response (201)
```json
{
    "success": true,
    "message": "Jemaat added successfully",
    "id": 2
}
```

---

## PUT /api/data/jemaat/{id}

Update data jemaat.

### URL Parameters
- `id` (required) - ID jemaat

### Request Body
```json
{
    "nama_lengkap": "Maria Magdalena Updated",
    "alamat": "Jl. Sudirman No. 456",
    "no_telepon": "081234567891",
    "email": "maria.updated@example.com",
    "tanggal_lahir": "1985-03-20",
    "jenis_kelamin": "Perempuan"
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Jemaat updated successfully"
}
```

---

## GET /api/data/kegiatan

Get data kegiatan dari server lokal.

### Query Parameters
- `limit` (optional) - Limit results (default: 100)
- `offset` (optional) - Offset for pagination (default: 0)
- `start_date` (optional) - Filter start date (YYYY-MM-DD)
- `end_date` (optional) - Filter end date (YYYY-MM-DD)

### Success Response (200)
```json
{
    "success": true,
    "data": [
        {
            "id_kegiatan": 1,
            "nama_kegiatan": "Misa Harian",
            "deskripsi": "Misa harian pagi",
            "lokasi": "Gereja Utama",
            "tanggal_mulai": "2024-01-20",
            "tanggal_selesai": "2024-01-20",
            "waktu_mulai": "06:00:00",
            "waktu_selesai": "07:00:00",
            "penanggungjawab": "Pastor Kepala"
        }
    ],
    "total": 1
}
```

---

## POST /api/data/kegiatan

Tambah kegiatan baru.

### Request Body
```json
{
    "nama_kegiatan": "Rapat Dewan Paroki",
    "deskripsi": "Rapat bulanan dewan paroki", 
    "lokasi": "Aula Paroki",
    "tanggal_mulai": "2024-01-25",
    "tanggal_selesai": "2024-01-25",
    "waktu_mulai": "19:00:00",
    "waktu_selesai": "21:00:00",
    "penanggungjawab": "Ketua Dewan"
}
```

### Success Response (201)
```json
{
    "success": true,
    "message": "Kegiatan added successfully",
    "id": 2
}
```

---

## GET /api/data/pengumuman

Get data pengumuman dari server lokal.

### Query Parameters
- `limit` (optional) - Limit results (default: 10)
- `offset` (optional) - Offset for pagination (default: 0)
- `active_only` (optional) - Filter active only (default: true)

### Success Response (200)
```json
{
    "success": true,
    "data": [
        {
            "id_pengumuman": 1,
            "judul": "Jadwal Misa Minggu",
            "isi": "Jadwal Misa Minggu: Sabtu 17:00, Minggu 06:00, 08:00, 10:00, 17:00",
            "tanggal_mulai": "2024-01-20",
            "tanggal_selesai": "2024-02-20",
            "kategori": "Liturgi",
            "prioritas": "Normal"
        }
    ],
    "total": 1
}
```

---

## GET /api/data/keuangan

Get data keuangan dari server lokal.

### Query Parameters
- `limit` (optional) - Limit results (default: 100)
- `offset` (optional) - Offset for pagination (default: 0)
- `category` (optional) - Filter by category (Pemasukan/Pengeluaran)

### Success Response (200)
```json
{
    "success": true,
    "data": [
        {
            "id_keuangan": 1,
            "tanggal": "2024-01-19",
            "kategori": "Pemasukan",
            "sub_kategori": "Kolekte",
            "deskripsi": "Kolekte Misa Minggu",
            "jumlah": 2500000.00,
            "penanggung_jawab": "Bendahara"
        }
    ],
    "total": 1
}
```

---

## GET /api/data/dashboard

Get data dashboard dari server lokal.

### Success Response (200)
```json
{
    "success": true,
    "data": {
        "statistics": {
            "total_jemaat": 125,
            "total_kegiatan": 15,
            "total_pengumuman": 3
        },
        "recent_activities": [],
        "server_info": {
            "uptime": 3600,
            "status": "running"
        }
    }
}
```

---

## POST /api/data/backup

Backup database di server lokal.

### Request Body
```json
{
    "backup_type": "full",
    "include_data": true,
    "compress": true
}
```

### Success Response (200)
```json
{
    "success": true,
    "message": "Backup completed successfully",
    "backup_file": "backup_20240120_103000.sql",
    "file_size": "2.5MB"
}
```

---

# Monitoring Endpoints

## GET /api/monitoring/servers

Get status semua server yang terdaftar.

### Success Response (200)
```json
{
    "servers": [
        {
            "id": 1,
            "server_name": "Gereja Santa Maria",
            "church_name": "Paroki Santa Maria Ratu Damai",
            "host": "192.168.1.100",
            "port": 9000,
            "status": "online",
            "last_ping": "2024-01-20T10:30:00Z",
            "is_online": true,
            "health_data": {
                "status": "healthy",
                "uptime": 3600
            }
        }
    ],
    "statistics": {
        "total": 1,
        "online": 1,
        "offline": 0,
        "uptime_percentage": 100.0
    }
}
```

---

## GET /api/monitoring/logs

Get log aktivitas API.

### Query Parameters
- `limit` (optional) - Limit results (default: 50)
- `offset` (optional) - Offset for pagination (default: 0)
- `action` (optional) - Filter by action
- `level` (optional) - Filter by level (INFO/WARNING/ERROR/CRITICAL)
- `user_id` (optional) - Filter by user ID

### Success Response (200)
```json
{
    "logs": [
        {
            "id": 1,
            "user_id": 1,
            "action": "LOGIN",
            "details": "User admin logged in via server 192.168.1.100:9000",
            "ip_address": "203.142.74.10",
            "level": "INFO",
            "created_at": "2024-01-20T10:30:00Z"
        }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0,
    "has_more": false
}
```

---

## GET /api/monitoring/analytics

Get analytics data.

### Query Parameters
- `days` (optional) - Number of days for analytics (default: 7)

### Success Response (200)
```json
{
    "time_range": {
        "start_date": "2024-01-13T10:30:00Z",
        "end_date": "2024-01-20T10:30:00Z",
        "days": 7
    },
    "server_statistics": {
        "total_servers": 1,
        "online_servers": 1,
        "offline_servers": 0,
        "uptime_percentage": 100.0
    },
    "activity_statistics": {
        "total_activities": 25,
        "unique_actions": 8,
        "error_rate": 2.5,
        "active_users": 3
    },
    "activity_breakdown": {
        "by_action": {
            "LOGIN": 5,
            "GET_JEMAAT": 8,
            "GET_KEGIATAN": 4
        },
        "by_day": {
            "2024-01-20": 10,
            "2024-01-19": 8
        }
    },
    "top_actions": [
        ["GET_JEMAAT", 8],
        ["LOGIN", 5],
        ["GET_KEGIATAN", 4]
    ]
}
```

---

## GET /api/monitoring/alerts

Get system alerts.

### Success Response (200)
```json
{
    "alerts": [
        {
            "type": "server_offline",
            "severity": "high",
            "message": "Server Gereja Santa Maria has been offline for 15 minutes",
            "server_id": 1,
            "timestamp": "2024-01-20T10:15:00Z"
        },
        {
            "type": "api_error",
            "severity": "medium",
            "message": "API Error: GET_JEMAAT - Database connection timeout",
            "log_id": 123,
            "timestamp": "2024-01-20T10:25:00Z"
        }
    ],
    "total": 2,
    "critical_count": 1,
    "warning_count": 1
}
```

---

# Utility Endpoints

## GET /api/health

Health check endpoint (tidak memerlukan authentication).

### Success Response (200)
```json
{
    "status": "healthy",
    "timestamp": "2024-01-20T10:30:00Z",
    "version": "1.0.0"
}
```

---

## POST /api/servers/register

Register server lokal ke API (requires authentication).

### Request Body
```json
{
    "server_name": "Gereja Santa Maria",
    "host": "192.168.1.100",
    "port": 9000,
    "church_name": "Paroki Santa Maria Ratu Damai"
}
```

### Success Response (200)
```json
{
    "message": "Server registered successfully",
    "server_id": 1,
    "status": "online"
}
```

---

## POST /api/servers/{id}/ping

Ping server untuk update status (requires authentication).

### URL Parameters
- `id` (required) - Server ID

### Success Response (200)
```json
{
    "message": "Ping received",
    "server_id": 1,
    "status": "online"
}
```

---

# Client Integration Example

## Python Client Example

```python
from api_client import FlaskAPIClient

# Initialize client
client = FlaskAPIClient("https://enternal.my.id/flask")

# Login
success, message = client.login("admin", "admin123", "192.168.1.100", 9000)

if success:
    # Get jemaat data
    success, data = client.get_jemaat(limit=50, search="Yohanes")
    
    if success:
        jemaat_list = data['data']
        print(f"Found {len(jemaat_list)} jemaat")
    
    # Add new jemaat
    new_jemaat = {
        "nama_lengkap": "Petrus Simon",
        "alamat": "Jl. Gatot Subroto No. 789",
        "email": "petrus@example.com"
    }
    
    success, result = client.add_jemaat(new_jemaat)
    
    # Logout
    client.logout()
```

## JavaScript/Browser Example

```javascript
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('api_token');
    }
    
    async login(username, password, serverHost, serverPort) {
        const response = await fetch(`${this.baseURL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password,
                server_host: serverHost,
                server_port: serverPort
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.token = data.token;
            localStorage.setItem('api_token', this.token);
        }
        
        return data;
    }
    
    async getJemaat(limit = 100, offset = 0) {
        const response = await fetch(
            `${this.baseURL}/api/data/jemaat?limit=${limit}&offset=${offset}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            }
        );
        
        return await response.json();
    }
}

// Usage
const client = new APIClient('https://enternal.my.id/flask');
await client.login('admin', 'admin123', '192.168.1.100', 9000);
const jemaatData = await client.getJemaat();
```

---

# Rate Limiting

API menggunakan rate limiting untuk mencegah abuse:

- **General endpoints**: 100 requests per hour per IP
- **Authentication endpoints**: 20 requests per hour per IP
- **Data modification endpoints**: 50 requests per hour per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642665600
```

---

# Changelog

## Version 1.0.0 (2024-01-20)
- Initial API release
- Authentication system
- Server management endpoints
- Data access endpoints
- Monitoring endpoints
- Rate limiting
- CORS support

---

# Support

Untuk pertanyaan atau masalah dengan API:

1. Check status API: `GET /api/health`
2. Review log files
3. Check authentication token validity
4. Verify server connectivity

**Base URL**: https://enternal.my.id/flask
**Documentation**: https://enternal.my.id/flask/docs (jika tersedia)
**Contact**: admin@enternal.my.id