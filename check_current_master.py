"""Check current master simulation and version info"""

from lng_planner.models import Simulation, MasterVersion

print("=" * 60)
print("📊 MASTER SIMULATION STATUS")
print("=" * 60)

# Get active master
master = Simulation.objects.filter(is_master=True).first()

if not master:
    print("❌ No master simulation found!")
else:
    print(f"\n✅ Active Master Simulation:")
    print(f"   ID: {master.id}")
    print(f"   Name: {master.name}")
    print(f"   Is Active: {master.is_active}")
    print(f"   SAP URL: {master.sap_api_url}")
    
    if hasattr(master, 'master_version') and master.master_version:
        print(f"\n📦 Master Version:")
        print(f"   Version Number: {master.master_version.version_number}")
        print(f"   Source Type: {master.master_version.source_type}")
        print(f"   Created At: {master.master_version.created_at}")
    else:
        print("\n⚠️  No master version linked!")

print("\n📋 All Master Versions:")
for mv in MasterVersion.objects.all().order_by('-created_at'):
    active_marker = "← ACTIVE" if mv.is_active else ""
    print(f"   {mv.version_number} ({mv.source_type}) - {mv.created_at.strftime('%Y-%m-%d %H:%M')} {active_marker}")

print("\n📋 All Simulations:")
for sim in Simulation.objects.all().order_by('-id'):
    active_marker = "← ACTIVE" if sim.is_active else ""
    master_marker = " [MASTER]" if sim.is_master else ""
    print(f"   ID {sim.id}: {sim.name} - Active: {sim.is_active}{master_marker} {active_marker}")

print("\n💡 TIP: If your browser shows an old simulation ID, just refresh the page!")
print("=" * 60)
