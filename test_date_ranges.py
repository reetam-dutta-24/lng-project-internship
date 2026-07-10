"""
Test script to verify date range creation from forms
Run: Get-Content test_date_ranges.py | python manage.py shell
"""

from lng_planner.models import Supplier, Customer, Refinery, SupplierDate, CustomerDate, RefineryDate

print("=" * 80)
print("TESTING DATE RANGE CREATION")
print("=" * 80)

# Test Suppliers
print("\n" + "=" * 60)
print("SUPPLIERS AND THEIR DATE RANGES")
print("=" * 60)

suppliers = Supplier.objects.all().order_by('name')
for s in suppliers:
    date_ranges = list(s.date_ranges.all())
    print(f"\nSupplier: {s.name} (ID:{s.id})")
    print(f"  Plant: {s.plant.name}")
    print(f"  Number of date ranges: {len(date_ranges)}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"    ✓ ID:{dr.id} From:{dr.from_date} To:{dr.to_date} Supply:{dr.daily_supply} MT/day")
    else:
        print(f"    - No date ranges")

# Test Customers
print("\n" + "=" * 60)
print("CUSTOMERS AND THEIR DATE RANGES")
print("=" * 60)

customers = Customer.objects.all().order_by('name')
for c in customers:
    date_ranges = list(c.date_ranges.all())
    print(f"\nCustomer: {c.name} (ID:{c.id})")
    print(f"  Plant: {c.plant.name}")
    print(f"  Number of date ranges: {len(date_ranges)}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"    ✓ ID:{dr.id} From:{dr.from_date} To:{dr.to_date} Demand:{dr.daily_demand} MT/day")
    else:
        print(f"    - No date ranges")

# Test Refineries
print("\n" + "=" * 60)
print("REFINERIES AND THEIR DATE RANGES")
print("=" * 60)

refineries = Refinery.objects.all().order_by('name')
for r in refineries:
    date_ranges = list(r.date_ranges.all())
    print(f"\nRefinery: {r.name} (ID:{r.id})")
    print(f"  Plant: {r.plant.name}")
    print(f"  Number of date ranges: {len(date_ranges)}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"    ✓ ID:{dr.id} From:{dr.from_date} To:{dr.to_date} Demand:{dr.daily_refinery_demand} MT/day")
    else:
        print(f"    - No date ranges")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Suppliers: {Supplier.objects.count()}")
print(f"Total SupplierDate records: {SupplierDate.objects.count()}")
print(f"Total Customers: {Customer.objects.count()}")
print(f"Total CustomerDate records: {CustomerDate.objects.count()}")
print(f"Total Refineries: {Refinery.objects.count()}")
print(f"Total RefineryDate records: {RefineryDate.objects.count()}")

print("\n" + "=" * 80)
print("HOW IT WORKS:")
print("=" * 80)
print("""
When you use the Add Supplier/Customer/Refinery form:

1. Base Entity Fields (shown first):
   - Name
   - Plant
   - Preference/Priority

2. Click "+ Add Date Range" button to add date ranges dynamically:
   - Each click creates a new date range box with:
     * From Date
     * To Date  
     * Daily Supply/Demand
   
3. When you click "Save Supplier/Customer/Refinery":
   - The base entity is saved first (Supplier/Customer/Refinery table)
   - ALL date ranges are saved to their respective tables:
     * SupplierDate for suppliers
     * CustomerDate for customers
     * RefineryDate for refineries
   
4. Each date range becomes a separate row in the database!

5. Dashboard displays them grouped by entity name with all ranges visible.
""")

print("=" * 80)
