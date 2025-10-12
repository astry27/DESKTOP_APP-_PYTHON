"""
Test script untuk verify kegiatan endpoints berfungsi di production
"""
import requests
import json

API_BASE = "https://enternal.my.id/flask"

def test_endpoint(name, url, method='GET', data=None):
    """Test an endpoint and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")

    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                print(f"✓ SUCCESS - Returned {len(result)} records")
                if len(result) > 0:
                    print(f"Sample keys: {list(result[0].keys())[:5]}")
            elif isinstance(result, dict):
                if result.get('status') == 'success':
                    print(f"✓ SUCCESS")
                    if 'data' in result:
                        data = result['data']
                        if isinstance(data, list):
                            print(f"  Records: {len(data)}")
                else:
                    print(f"✗ ERROR: {result.get('message', 'Unknown error')}")
        else:
            print(f"✗ ERROR {response.status_code}")
            try:
                error = response.json()
                print(f"  Message: {error.get('message', error)}")
            except:
                print(f"  Response: {response.text[:200]}")

    except Exception as e:
        print(f"✗ EXCEPTION: {str(e)}")

# Test endpoints
print("="*60)
print("TESTING KEGIATAN ENDPOINTS")
print("="*60)

# 1. Test GET all kegiatan
test_endpoint(
    "GET /kegiatan - Get all kegiatan",
    f"{API_BASE}/kegiatan"
)

# 2. Test GET kegiatan/wr/all
test_endpoint(
    "GET /kegiatan/wr/all - Get WR kegiatan from kegiatan table",
    f"{API_BASE}/kegiatan/wr/all"
)

# 3. Test GET kegiatan-wr (from kegiatan_wr table)
test_endpoint(
    "GET /kegiatan-wr - Get kegiatan WR from kegiatan_wr table",
    f"{API_BASE}/kegiatan-wr"
)

# 4. Test POST kegiatan (simulate adding kegiatan paroki)
test_data = {
    "nama_kegiatan": "Test Kegiatan API",
    "deskripsi": "Testing API endpoint",
    "lokasi": "Gereja Test",
    "tanggal_mulai": "2025-10-15",
    "tanggal_selesai": "2025-10-15",
    "waktu_mulai": "10:00",
    "waktu_selesai": "12:00",
    "penanggungjawab": "Admin Test",
    "kategori": "Misa",
    "status": "Direncanakan"
}

test_endpoint(
    "POST /kegiatan - Add kegiatan paroki",
    f"{API_BASE}/kegiatan",
    method='POST',
    data=test_data
)

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
