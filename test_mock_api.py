# Quick test of mock SAP API endpoint
import requests

try:
    response = requests.get("http://localhost:8000/api/mock-sap/", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✓ Valid JSON received!")
        print(f"  - Plants: {len(data.get('plant_inventories', []))}")
        print(f"  - Suppliers: {len(data.get('suppliers', []))}")
        print(f"  - Customers: {len(data.get('customers', []))}")
        print(f"  - Refineries: {len(data.get('refineries', []))}")
        print(f"  - Cargos: {len(data.get('cargos', []))}")
    else:
        print(f"\n✗ Error: Status {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("✗ Connection Error: Server not running at http://localhost:8000")
    print("  Please start the server with: python manage.py runserver")
except requests.exceptions.Timeout:
    print("✗ Timeout: Server took too long to respond")
except Exception as e:
    print(f"✗ Error: {e}")
