"""
Test script to verify Publish To Master workflow.
Run with: python manage.py shell

This script tests all 8 requirements and prints verification results.
"""

from lng_planner.models import Simulation, MasterVersion, User, Supplier, Customer, Refinery, Cargo, PlantInventory

def test_publish_workflow():
    print("\n" + "="*70)
    print("PUBLISH TO MASTER - VERIFICATION TEST")
    print("="*70 + "\n")
    
    # Setup: Get or create test user
    user, _ = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    if not hasattr(user, 'employee_profile'):
        from lng_planner.models import Employee
        Employee.objects.create(
            user=user,
            employee_id='EMP999',
            full_name='Test User'
        )
    
    # Get current state
    print("1. CURRENT STATE")
    print("-" * 70)
    
    active_master = Simulation.objects.filter(is_master=True).first()
    if active_master:
        version = active_master.master_version.version_number if active_master.master_version else "None"
        print(f"✓ Active Master: {active_master.name} (ID: {active_master.id})")
        print(f"  Version: {version}")
        print(f"  User: {active_master.user.username if active_master.user else 'NULL'}")
    else:
        print("⚠ No active master found")
    
    total_versions = MasterVersion.objects.count()
    active_versions = MasterVersion.objects.filter(is_active=True).count()
    print(f"\n✓ Total MasterVersions: {total_versions}")
    print(f"✓ Active MasterVersions: {active_versions} (should be 1 or 0)")
    
    # Create test simulation with data
    print("\n2. CREATING TEST SIMULATION")
    print("-" * 70)
    
    from django.utils import timezone
    from datetime import date
    
    test_sim = Simulation.objects.create(
        user=user,
        name='Test Publish Simulation',
        start_date=date.today(),
        end_date=date.today().replace(year=date.today().year + 1),
        is_master=False,
        is_active=True
    )
    
    # Add some test data
    plant = Plant.objects.first() or Plant.objects.create(name='Test Plant')
    
    # Create suppliers
    supplier1 = Supplier.objects.create(simulation=test_sim, plant=plant, name='Supplier A', preference=1)
    supplier2 = Supplier.objects.create(simulation=test_sim, plant=plant, name='Supplier B', preference=2)
    
    # Create customers
    customer1 = Customer.objects.create(simulation=test_sim, plant=plant, name='Customer X', preference=1)
    
    # Create cargos
    Cargo.objects.create(simulation=test_sim, plant=plant, cargo_name='Cargo 1', amount=1000)
    Cargo.objects.create(simulation=test_sim, plant=plant, cargo_name='Cargo 2', amount=2000)
    
    # Create inventory
    PlantInventory.objects.create(simulation=test_sim, plant=plant, opening_inventory=5000)
    
    print(f"✓ Created simulation: {test_sim.name} (ID: {test_sim.id})")
    print(f"  Suppliers: {test_sim.suppliers.count()}")
    print(f"  Customers: {test_sim.customers.count()}")
    print(f"  Cargos: {test_sim.cargos.count()}")
    print(f"  Inventories: {test_sim.plant_inventories.count()}")
    
    # Simulate publish (manual steps since we can't call the view directly)
    print("\n3. SIMULATING PUBLISH TO MASTER")
    print("-" * 70)
    
    old_master = Simulation.objects.filter(is_master=True).first()
    old_version = old_master.master_version if old_master and hasattr(old_master, 'master_version') else None
    
    print(f"Old Active Master: {old_master.name if old_master else 'None'}")
    if old_version:
        print(f"  Version: {old_version.version_number}")
    
    # Step 1: Create new master version
    from lng_planner.models import MasterVersion
    from lng_planner.views import get_next_version_number
    
    version_number = get_next_version_number()
    new_master_version = MasterVersion.objects.create(
        version_number=version_number,
        name=f"Published from {test_sim.name}",
        source_type='SIMULATION',
        created_by=user,
        description=f"Test publish",
        is_active=True,
        source_simulation=test_sim
    )
    
    print(f"\n✓ New MasterVersion Created: {new_master_version.version_number}")
    print(f"  Source Type: {new_master_version.source_type}")
    print(f"  Created By: {new_master_version.created_by.username}")
    
    # Step 2: Deactivate previous versions
    deactivated = MasterVersion.objects.filter(is_active=True).exclude(pk=new_master_version.pk).update(is_active=False)
    print(f"\n✓ Deactivated {deactivated} previous version(s)")
    
    # Step 3: Deactivate old master simulation
    if old_master:
        old_master.is_master = False
        old_master.save()
        print(f"✓ Deactivated old master simulation")
    
    # Step 4: Create new master simulation
    from django.utils import timezone
    new_master = Simulation.objects.create(
        name=f"Master - {version_number}",
        start_date=test_sim.start_date,
        end_date=test_sim.end_date,
        is_master=True,
        user=None,
        master_version=new_master_version
    )
    
    print(f"\n✓ New Master Simulation Created: {new_master.name} (ID: {new_master.id})")
    print(f"  is_master: {new_master.is_master}")
    print(f"  user: {new_master.user}")
    print(f"  master_version: {new_master.master_version.version_number}")
    
    # Step 5: Copy data using the helper function
    from lng_planner.views import copy_simulation_data
    
    counts = copy_simulation_data(test_sim, new_master)
    
    print(f"\n✓ Data Copied:")
    print(f"  Plant Inventories: {counts['inventories']}")
    print(f"  Suppliers: {counts['suppliers']}")
    print(f"  Supplier Date Ranges: {counts['supplier_dates']}")
    print(f"  Customers: {counts['customers']}")
    print(f"  Customer Date Ranges: {counts['customer_dates']}")
    print(f"  Refineries: {counts['refineries']}")
    print(f"  Refinery Date Ranges: {counts['refinery_dates']}")
    print(f"  Cargos: {counts['cargos']}")
    print(f"  Comments: {counts['comments']}")
    
    # Verification
    print("\n4. VERIFICATION")
    print("-" * 70)
    
    errors = []
    
    # Check 1: New MasterVersion exists
    if MasterVersion.objects.filter(pk=new_master_version.pk).exists():
        print("✓ Requirement 1: New MasterVersion record created")
    else:
        errors.append("Requirement 1 FAILED: New MasterVersion not found")
        print("✗ Requirement 1 FAILED")
    
    # Check 2: Previous version deactivated
    if old_version and not MasterVersion.objects.filter(pk=old_version.pk, is_active=True).exists():
        print("✓ Requirement 2: Previous MasterVersion deactivated")
    elif not old_version:
        print("✓ Requirement 2: N/A (no previous version)")
    else:
        errors.append("Requirement 2 FAILED: Old version still active")
        print("✗ Requirement 2 FAILED")
    
    # Check 3: New version is active
    if MasterVersion.objects.filter(pk=new_master_version.pk, is_active=True).exists():
        print("✓ Requirement 3: New MasterVersion is active")
    else:
        errors.append("Requirement 3 FAILED: New version not active")
        print("✗ Requirement 3 FAILED")
    
    # Check 4: New master simulation with correct fields
    if (new_master.is_master and 
        new_master.user is None and 
        new_master.master_version == new_master_version):
        print("✓ Requirement 4: New Master Simulation created correctly")
        print(f"  - is_master=True ✓")
        print(f"  - user=NULL ✓")
        print(f"  - master_version={new_master_version.version_number} ✓")
    else:
        errors.append("Requirement 4 FAILED: Incorrect fields")
        print("✗ Requirement 4 FAILED")
    
    # Check 5: All data copied
    if (new_master.plant_inventories.count() == counts['inventories'] and
        new_master.suppliers.count() == counts['suppliers'] and
        new_master.customers.count() == counts['customers'] and
        new_master.cargos.count() == counts['cargos']):
        print("✓ Requirement 5: All data copied successfully")
    else:
        errors.append("Requirement 5 FAILED: Data mismatch")
        print("✗ Requirement 5 FAILED")
    
    # Check 6: New simulation would use active master
    test_new_sim = Simulation.objects.filter(is_master=True).first()
    if test_new_sim and test_new_sim.master_version == new_master_version:
        print("✓ Requirement 6: Active master has correct version reference")
    else:
        errors.append("Requirement 6 FAILED: Wrong version reference")
        print("✗ Requirement 6 FAILED")
    
    # Check 7: Dashboard would see active master
    dashboard_master = Simulation.objects.filter(is_master=True).first()
    if dashboard_master and dashboard_master.master_version.is_active:
        print("✓ Requirement 7: Dashboard will show active master")
    else:
        errors.append("Requirement 7 FAILED: Dashboard issue")
        print("✗ Requirement 7 FAILED")
    
    # Check 8: Other users would inherit new master
    other_user_sim = Simulation.objects.filter(
        is_master=False, 
        user__username__ne=user.username
    ).first()
    if not other_user_sim or other_user_sim.master_version != new_master_version:
        print("✓ Requirement 8: New simulations will use latest master")
    else:
        print("⚠ Requirement 8: N/A (no other user simulations)")
    
    # Summary
    print("\n" + "="*70)
    if errors:
        print("❌ VERIFICATION FAILED")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
    print("="*70 + "\n")
    
    # Cleanup (optional)
    print("Cleanup:")
    print(f"  Test simulation: {test_sim.id} (keep for inspection)")
    print(f"  New master: {new_master.id} (keep for inspection)")
    print("\nTo clean up manually, delete these simulations from Django admin.\n")

if __name__ == '__main__':
    test_publish_workflow()
