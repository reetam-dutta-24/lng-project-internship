import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lng_project.settings')
django.setup()

from lng_planner.models import Simulation

# Get current active master
master = Simulation.objects.filter(is_master=True, is_active=True).first()

if not master:
    # Try to get any master
    master = Simulation.objects.filter(is_master=True).first()

if master:
    print("=" * 70)
    print("CURRENT MASTER SIMULATION")
    print("=" * 70)
    print(f"Name:           {master.name}")
    print(f"SAP API URL:    {master.sap_api_url or 'NOT SET'}")
    print(f"Is Active:      {master.is_active}")
    print(f"Last Sync:      {master.last_sap_sync or 'Never'}")
    print()
    
    # Update to mock endpoint
    new_url = "http://localhost:8000/api/mock-sap/"
    
    if master.sap_api_url != new_url:
        print("Updating SAP API URL...")
        master.sap_api_url = new_url
        master.save()
        print(f"✓ Updated to: {new_url}")
    else:
        print(f"✓ Already set to: {new_url}")
    
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Make sure your Django server is running (python manage.py runserver)")
    print("2. Go to your dashboard in the browser")
    print("3. Click 'Refresh From SAP' button")
    print("4. You should see a success message with new Master Version created!")
    print()
    print("The mock API will return:")
    print("  - 2 Plants (Dahej, Ennore)")
    print("  - 10 Suppliers with date ranges")
    print("  - 10 Customers with supplier mappings")
    print("  - 3 Refineries with date ranges")
    print("  - 10 Cargos")
    print("=" * 70)
else:
    print("❌ ERROR: No master simulation found in database!")
    print("   Please create a master simulation first via 'Manage Master Simulation'")
