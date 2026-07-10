"""
Fix duplicate MasterVersion entries and ensure version numbers are unique
Run this with: python manage.py shell
Then paste this code or save as a management command
"""

from lng_planner.models import MasterVersion

print("🔍 Checking for duplicate MasterVersions...")

# Find all versions and check for duplicates
versions = list(MasterVersion.objects.all().order_by('version_number'))

if not versions:
    print("✅ No MasterVersions found - system is clean")
else:
    print(f"Found {len(versions)} MasterVersion(s):")
    for v in versions:
        print(f"  - {v.version_number} ({v.source_type}) - Active: {v.is_active}")

# Check for duplicates
seen = {}
duplicates = []
for v in versions:
    if v.version_number in seen:
        duplicates.append(v)
        print(f"\n⚠️  DUPLICATE FOUND: {v.version_number} (ID: {v.id})")
    else:
        seen[v.version_number] = v

if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate version(s)")
    print("\nTo fix this, you can:")
    print("1. Delete the duplicates manually in Django admin")
    print("2. Or run this command to delete older duplicates (keep newest):")
    print("\n   from lng_planner.models import MasterVersion")
    print("   for v in MasterVersion.objects.filter(version_number__in=['V1', 'V2']).order_by('-created_at')[1:]:")
    print("       print(f'Deleting {v.version_number} (ID: {v.id})')")
    print("       v.delete()")
else:
    print("\n✅ No duplicates found - system is clean!")

# Show next expected version number
if versions:
    max_num = 0
    for v in versions:
        try:
            num = int(v.version_number.replace('V', ''))
            if num > max_num:
                max_num = num
        except:
            pass
    
    print(f"\n📊 Next version should be: V{max_num + 1}")
