"""
Debug script to check Customer 1 data
Run: python manage.py shell < debug_customer1.py
"""

from lng_planner.models import Customer, CustomerDate

print("=" * 80)
print("DEBUGGING CUSTOMER 1")
print("=" * 80)

# Find Customer 1
try:
    customer = Customer.objects.get(name="Customer 1")
    print(f"\n✓ Found Customer: {customer.name}")
    print(f"  ID: {customer.id}")
    print(f"  Plant: {customer.plant.name}")
    print(f"  Preference: {customer.preference}")
    
    # Get all date ranges
    date_ranges = customer.date_ranges.all()
    print(f"\n✓ Number of date ranges found: {date_ranges.count()}")
    
    if date_ranges.exists():
        for dr in date_ranges:
            print(f"\n  Date Range ID: {dr.id}")
            print(f"    From: {dr.from_date}")
            print(f"    To: {dr.to_date}")
            print(f"    Daily Demand: {dr.daily_demand} MT/day")
    else:
        print("\n✗ NO DATE RANGES FOUND for Customer 1!")
        
except Customer.DoesNotExist:
    print("\n✗ Customer 'Customer 1' does not exist!")

print("\n" + "=" * 80)
print("ALL CUSTOMERS AND THEIR DATE RANGES")
print("=" * 80)

all_customers = Customer.objects.all()
for c in all_customers:
    ranges = list(c.date_ranges.all())
    print(f"\n{c.name} (ID: {c.id}) - Plant: {c.plant.name}")
    print(f"  Date Ranges Count: {len(ranges)}")
    for r in ranges:
        print(f"    - ID:{r.id} From:{r.from_date} To:{r.to_date} Demand:{r.daily_demand}")

print("\n" + "=" * 80)
