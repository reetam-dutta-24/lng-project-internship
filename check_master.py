import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lng_project.settings')
django.setup()

from lng_planner.models import Simulation, MasterVersion

# Check current master
master = Simulation.objects.filter(is_master=True).first()

if master:
    print("=" * 60)
    print("CURRENT MASTER SIMULATION")
    print("=" * 60)
    print(f"Name: {master.name}")
    print(f"SAP API URL: {master.sap_api_url or 'NOT SET'}")
    print(f"Is Active: {master.is_active}")
    print(f"Last SAP Sync: {master.last_sap_sync}")
    print()
    
    # Check master versions
    versions = MasterVersion.objects.all().order_by('-created_at')
    print("=" * 60)
    print("MASTER VERSIONS")
    print("=" * 60)
    for v in versions:
        active_marker = " ← ACTIVE" if v.is_active else ""
        print(f"{v.version_number} - {v.name} ({v.source_type}){active_marker}")
    
    print()
    print("=" * 60)
    print("RECOMMENDED SAP API URL FOR TESTING")
    print("=" * 60)
    print("http://localhost:8000/api/mock-sap/")
    print()
    print("To update, run this command in Django shell:")
    print(f'master.sap_api_url = "http://localhost:8000/api/mock-sap/"')
    print('master.save()')
    print("=" * 60)
else:
    print("No master simulation found!")
