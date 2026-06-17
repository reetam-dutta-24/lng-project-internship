"""
Quick check to see if you have customers/suppliers/refineries with date ranges
Run this from terminal: python manage.py shell < check_data.py
"""

from lng_planner.models import Customer, Supplier, Refinery

print("=" * 60)
print("CHECKING CUSTOMERS")
print("=" * 60)
customers = Customer.objects.all()
for c in customers:
    ranges = list(c.date_ranges.all())
    print(f"\nCustomer: {c.name}")
    print(f"Plant: {c.plant.name}")
    print(f"Number of date ranges: {len(ranges)}")
    for r in ranges:
        print(f"  - From: {r.from_date} To: {r.to_date}, Daily Demand: {r.daily_demand} MT/day")

print("\n" + "=" * 60)
print("CHECKING SUPPLIERS")
print("=" * 60)
suppliers = Supplier.objects.all()
for s in suppliers:
    ranges = list(s.date_ranges.all())
    print(f"\nSupplier: {s.name}")
    print(f"Plant (Serves To): {s.plant.name}")
    print(f"Number of date ranges: {len(ranges)}")
    for r in ranges:
        print(f"  - From: {r.from_date} To: {r.to_date}, Daily Supply: {r.daily_supply} MT/day")

print("\n" + "=" * 60)
print("CHECKING REFINERIES")
print("=" * 60)
refineries = Refinery.objects.all()
for r in refineries:
    ranges = list(r.date_ranges.all())
    print(f"\nRefinery: {r.name}")
    print(f"Plant: {r.plant.name}")
    print(f"Number of date ranges: {len(ranges)}")
    for rd in ranges:
        print(f"  - From: {rd.from_date} To: {rd.to_date}, Daily Demand: {rd.daily_refinery_demand} MT/day")

print("\n" + "=" * 60)
