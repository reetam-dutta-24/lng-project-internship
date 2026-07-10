"""
Quick fix: Update master simulation SAP API URL to use mock endpoint
Run this command: python manage.py shell < update_sap_url.py
"""

from lng_planner.models import Simulation, MasterVersion

# Get current active master
master = Simulation.objects.filter(is_master=True).first()

if not master:
    print("ERROR: No master simulation found!")
else:
    # Update SAP API URL to mock endpoint
    old_url = master.sap_api_url
    new_url = "http://localhost:8000/api/mock-sap/"
    
    master.sap_api_url = new_url
    master.save()
    
    print("✓ Successfully updated SAP API URL!")
    print(f"  Old URL: {old_url}")
    print(f"  New URL: {new_url}")
    print()
    print("You can now click 'Refresh From SAP' button.")
    print("It will create a new Master Version (e.g., V2, V3) with the mock data.")
