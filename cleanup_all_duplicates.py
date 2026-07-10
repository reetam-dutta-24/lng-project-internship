"""
Script to clean up duplicate suppliers and refineries
Run: Get-Content cleanup_all_duplicates.py | python manage.py shell
"""

from lng_planner.models import Supplier, Refinery

print("=" * 80)
print("CLEANING UP DUPLICATE SUPPLIERS AND REFINERIES")
print("=" * 80)

# Clean up Suppliers
print("\n" + "=" * 60)
print("PROCESSING SUPPLIERS")
print("=" * 60)

supplier_names = Supplier.objects.values_list('name', flat=True).distinct()

for name in supplier_names:
    duplicates = Supplier.objects.filter(name=name).order_by('id')
    
    if duplicates.count() > 1:
        print(f"\nProcessing: {name}")
        print(f"Found {duplicates.count()} duplicate entries")
        
        primary = None
        to_delete = []
        
        for s in duplicates:
            range_count = s.date_ranges.count()
            print(f"  ID:{s.id} - Plant: {s.plant.name} - Date Ranges: {range_count}")
            
            if range_count > 0 and primary is None:
                primary = s
                print(f"    → Keeping this one (has date ranges)")
            else:
                to_delete.append(s)
        
        if primary is None:
            primary = duplicates.first()
            to_delete = list(duplicates.exclude(id=primary.id))
            print(f"  → Keeping ID:{primary.id} (no date ranges on any)")
        
        if to_delete:
            print(f"\n  Deleting {len(to_delete)} duplicate(s)...")
            for s in to_delete:
                print(f"    - Deleting Supplier ID:{s.id}")
                s.delete()
            
            print(f"  ✓ Kept Supplier ID:{primary.id}")
        else:
            print(f"  ✓ No duplicates to delete")

# Clean up Refineries
print("\n" + "=" * 60)
print("PROCESSING REFINERIES")
print("=" * 60)

refinery_names = Refinery.objects.values_list('name', flat=True).distinct()

for name in refinery_names:
    duplicates = Refinery.objects.filter(name=name).order_by('id')
    
    if duplicates.count() > 1:
        print(f"\nProcessing: {name}")
        print(f"Found {duplicates.count()} duplicate entries")
        
        primary = None
        to_delete = []
        
        for r in duplicates:
            range_count = r.date_ranges.count()
            print(f"  ID:{r.id} - Plant: {r.plant.name} - Date Ranges: {range_count}")
            
            if range_count > 0 and primary is None:
                primary = r
                print(f"    → Keeping this one (has date ranges)")
            else:
                to_delete.append(r)
        
        if primary is None:
            primary = duplicates.first()
            to_delete = list(duplicates.exclude(id=primary.id))
            print(f"  → Keeping ID:{primary.id} (no date ranges on any)")
        
        if to_delete:
            print(f"\n  Deleting {len(to_delete)} duplicate(s)...")
            for r in to_delete:
                print(f"    - Deleting Refinery ID:{r.id}")
                r.delete()
            
            print(f"  ✓ Kept Refinery ID:{primary.id}")
        else:
            print(f"  ✓ No duplicates to delete")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE!")
print("=" * 80)

# Show final state
print("\nFinal Suppliers:")
all_suppliers = Supplier.objects.all().order_by('name', 'id')
for s in all_suppliers:
    range_count = s.date_ranges.count()
    print(f"  {s.name} (ID:{s.id}) - Plant: {s.plant.name} - Date Ranges: {range_count}")

print("\nFinal Refineries:")
all_refineries = Refinery.objects.all().order_by('name', 'id')
for r in all_refineries:
    range_count = r.date_ranges.count()
    print(f"  {r.name} (ID:{r.id}) - Plant: {r.plant.name} - Date Ranges: {range_count}")

print("\n" + "=" * 80)
