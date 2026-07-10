"""
Script to clean up duplicate customers
Run: Get-Content cleanup_duplicates.py | python manage.py shell
"""

from lng_planner.models import Customer, CustomerDate

print("=" * 80)
print("CLEANING UP DUPLICATE CUSTOMERS")
print("=" * 80)

# Find all customer names
customer_names = Customer.objects.values_list('name', flat=True).distinct()

for name in customer_names:
    # Get all customers with this name
    duplicates = Customer.objects.filter(name=name).order_by('id')
    
    if duplicates.count() > 1:
        print(f"\n{'='*60}")
        print(f"Processing: {name}")
        print(f"Found {duplicates.count()} duplicate entries")
        
        # Find the one with date ranges (if any)
        primary = None
        to_delete = []
        
        for c in duplicates:
            range_count = c.date_ranges.count()
            print(f"  ID:{c.id} - Date Ranges: {range_count}")
            
            if range_count > 0 and primary is None:
                primary = c
                print(f"    → Keeping this one (has date ranges)")
            else:
                to_delete.append(c)
        
        # If none have date ranges, keep the first one
        if primary is None:
            primary = duplicates.first()
            to_delete = list(duplicates.exclude(id=primary.id))
            print(f"  → Keeping ID:{primary.id} (no date ranges on any)")
        
        # Delete duplicates
        if to_delete:
            print(f"\n  Deleting {len(to_delete)} duplicate(s)...")
            for c in to_delete:
                print(f"    - Deleting Customer ID:{c.id}")
                c.delete()
            
            print(f"  ✓ Kept Customer ID:{primary.id}")
        else:
            print(f"  ✓ No duplicates to delete")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE!")
print("=" * 80)

# Show final state
print("\nFinal customer list:")
all_customers = Customer.objects.all().order_by('name', 'id')
for c in all_customers:
    range_count = c.date_ranges.count()
    print(f"  {c.name} (ID:{c.id}) - Plant: {c.plant.name} - Date Ranges: {range_count}")

print("\n" + "=" * 80)
