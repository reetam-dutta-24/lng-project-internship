"""
Test script to verify forms save multiple date ranges correctly
Run: Get-Content test_form_save.py | python manage.py shell
"""

from lng_planner.models import Supplier, Customer, Refinery, SupplierDate, CustomerDate, RefineryDate

print("=" * 80)
print("TESTING FORM SAVE FUNCTIONALITY")
print("=" * 80)

# Check Suppliers
print("\n" + "=" * 60)
print("SUPPLIERS - Checking for date ranges")
print("=" * 60)

suppliers = Supplier.objects.all().order_by('name')
for s in suppliers:
    date_ranges = list(s.date_ranges.all())
    print(f"\n{s.name} (ID:{s.id}) - Plant: {s.plant.name}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"  ✓ ID:{dr.id} | From:{dr.from_date} To:{dr.to_date} | Supply:{dr.daily_supply} MT/day")
    else:
        print(f"  ⚠ No date ranges found")

# Check Customers  
print("\n" + "=" * 60)
print("CUSTOMERS - Checking for date ranges")
print("=" * 60)

customers = Customer.objects.all().order_by('name')
for c in customers:
    date_ranges = list(c.date_ranges.all())
    print(f"\n{c.name} (ID:{c.id}) - Plant: {c.plant.name}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"  ✓ ID:{dr.id} | From:{dr.from_date} To:{dr.to_date} | Demand:{dr.daily_demand} MT/day")
    else:
        print(f"  ⚠ No date ranges found")

# Check Refineries
print("\n" + "=" * 60)
print("REFINERIES - Checking for date ranges")
print("=" * 60)

refineries = Refinery.objects.all().order_by('name')
for r in refineries:
    date_ranges = list(r.date_ranges.all())
    print(f"\n{r.name} (ID:{r.id}) - Plant: {r.plant.name}")
    
    if date_ranges:
        for dr in date_ranges:
            print(f"  ✓ ID:{dr.id} | From:{dr.from_date} To:{dr.to_date} | Demand:{dr.daily_refinery_demand} MT/day")
    else:
        print(f"  ⚠ No date ranges found")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Suppliers: {Supplier.objects.count()} | SupplierDate records: {SupplierDate.objects.count()}")
print(f"Total Customers: {Customer.objects.count()} | CustomerDate records: {CustomerDate.objects.count()}")
print(f"Total Refineries: {Refinery.objects.count()} | RefineryDate records: {RefineryDate.objects.count()}")

# Instructions
print("\n" + "=" * 80)
print("HOW THE FORMS NOW WORK:")
print("=" * 80)
print("""
1. ADD NEW ENTITY (Supplier/Customer/Refinery):
   - Fill in base fields (Name, Plant, Preference)
   - Click "+ Add Date Range" button to add range boxes
   - Each box has: Daily Quantity, From Date, To Date
   - Click button again to add more ranges
   - Click "Save" → Creates 1 entity + ALL date ranges in DB

2. EDIT EXISTING ENTITY:
   - Dashboard shows entity with all its date ranges listed below
   - Click ✏️ (edit icon) next to any date range
   - Edit that specific range and save
   
3. DASHBOARD DISPLAY:
   - Each entity appears ONCE
   - All its date ranges shown below as separate entries
   - Each range has edit/delete buttons

FORM FIELD NAMES (for JavaScript):
- Supplier: date_ranges_1_daily_supply, date_ranges_1_from_date, date_ranges_1_to_date
- Customer: date_ranges_1_daily_demand, date_ranges_1_from_date, date_ranges_1_to_date  
- Refinery: date_ranges_1_daily_refinery_demand, date_ranges_1_from_date, date_ranges_1_to_date

The view loops through POST data looking for keys starting with "date_ranges_" 
and ending with the appropriate field name, then creates Date records for each.
""")

print("=" * 80)
