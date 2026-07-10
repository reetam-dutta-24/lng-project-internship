# Master Version Management Workflow

## Overview
The system maintains a **single active master version** at all times. All users (Planners and Planning Admins) create simulations from this same active master.

---

## Architecture

### Key Concepts

1. **MasterVersion**: Tracks versions of the master data
   - `version_number`: e.g., "V1", "V2", "V3"
   - `source_type`: 'SAP' or 'SIMULATION'
   - `is_active`: Only ONE version is active at a time
   - `created_by`: User who created this version

2. **Simulation (Master)**: The actual master simulation data
   - `is_master=True`
   - `user=None` (no owner, shared by all users)
   - Linked to exactly one MasterVersion via `master_version` field

3. **User Simulations**: Individual user simulations
   - `is_master=False`
   - `user=<owner>`
   - Created from the active master

---

## Business Flow

### Initial State
```
Active Master: V1 (from SAP)
├─ Master Simulation (is_master=True, user=None)
│  ├─ Suppliers: A, B, C
│  ├─ Customers: X, Y, Z
│  └─ Cargos: Cargo1, Cargo2
```

### User Creates Simulation
```
Priya clicks "New Simulation"
↓
System creates:
├─ Simulation (is_master=False, user=Priya)
│  ├─ Copies all data from Active Master V1
│  └─ Links to master_version=V1
```

### Planning Admin Publishes to Master

**Scenario**: Rohit (Planning Admin) modifies his simulation and publishes it.

#### Step-by-Step Process:

1. **Create New Master Version**
   ```python
   new_master_version = MasterVersion.objects.create(
       version_number="V2",
       name="Published from Rohit's Simulation",
       source_type='SIMULATION',
       created_by=Rohit,
       is_active=True
   )
   ```

2. **Deactivate Previous Master Version**
   ```python
   MasterVersion.objects.filter(is_active=True)
       .exclude(pk=new_master_version.pk)
       .update(is_active=False)
   
   # V1.is_active = False
   # V2.is_active = True
   ```

3. **Deactivate Old Master Simulation**
   ```python
   old_master.is_master = False
   old_master.save()
   ```

4. **Create NEW Master Simulation**
   ```python
   new_master_simulation = Simulation.objects.create(
       name="Master - V2",
       is_master=True,
       user=None,  # No owner
       master_version=new_master_version
   )
   ```

5. **Copy All Data from Published Simulation**
   ```python
   copy_simulation_data(
       source=Rohit's simulation,
       target=new_master_simulation
   )
   
   # Copies:
   # - Plant Inventories
   # - Suppliers + SupplierDates
   # - Customers + CustomerDates
   # - Refineries + RefineryDates
   # - Cargos
   # - Simulation Comments
   ```

#### Result:
```
Active Master: V2 (published from Rohit's simulation)
├─ New Master Simulation (is_master=True, user=None)
│  ├─ Suppliers: A', B', C' (from Rohit's changes)
│  ├─ Customers: X', Y', Z'
│  └─ Cargos: Cargo1', Cargo2'

Old State (preserved):
├─ V1 (is_active=False) - Historical record
└─ Old Master Simulation (is_master=False) - Historical data
```

### Next User Login

**Priya logs in after Rohit published V2:**

1. Dashboard shows: `Master (Read Only) - V2`
2. When Priya clicks "New Simulation":
   ```python
   # System clones from the ACTIVE master (V2)
   new_simulation = clone_from(master_simulation=V2)
   ```
3. Priya's new simulation includes Rohit's changes

---

## SAP Refresh Workflow

### Planning Admin Clicks "Refresh From SAP"

#### Step-by-Step Process:

1. **Call SAP API**
   ```python
   response = requests.get(sap_api_url)
   sap_data = response.json()
   ```

2. **Create New Master Version**
   ```python
   new_master_version = MasterVersion.objects.create(
       version_number="V3",
       name="SAP Sync - 2026-06-25 14:30",
       source_type='SAP',
       created_by=PlanningAdmin,
       is_active=True
   )
   ```

3. **Deactivate Previous Master Version**
   ```python
   # V2.is_active = False
   # V3.is_active = True
   ```

4. **Deactivate Old Master Simulation**
   ```python
   old_master.is_master = False
   old_master.save()
   ```

5. **Create NEW Master Simulation with SAP Data**
   ```python
   new_master_simulation = Simulation.objects.create(
       name="Master - V3",
       is_master=True,
       user=None,
       master_version=new_master_version,
       last_sap_sync=timezone.now()
   )
   ```

6. **Process SAP Data** (TODO: Implement actual parsing)
   ```python
   # Parse sap_data and create:
   # - Suppliers from SAP
   # - Customers from SAP
   # - Cargos from SAP
   ```

#### Result:
```
Active Master: V3 (from SAP)
├─ New Master Simulation (is_master=True, user=None)
│  ├─ Suppliers: From SAP API
│  ├─ Customers: From SAP API
│  └─ Cargos: From SAP API
```

---

## Permission Matrix

| Feature | Planner | Planning Admin | Django Superuser |
|---------|---------|----------------|------------------|
| View Active Master | ✅ | ✅ | ✅ |
| Create Simulation from Master | ✅ | ✅ | ✅ |
| **Publish To Master** | ❌ | ✅ | ✅ |
| **Refresh From SAP** | ❌ | ✅ | ✅ |
| View All User Simulations | ❌ | ❌ | ✅ |
| Manage Users/Roles | ❌ | ❌ | ✅ |

---

## Database Schema

### MasterVersion Table
```
id | version_number | name              | source_type | created_by | is_active | created_at
---|----------------|-------------------|-------------|------------|-----------|------------
1  | V1             | Initial Master    | SAP         | admin      | FALSE     | 2026-06-20
2  | V2             | Published from X  | SIMULATION  | Rohit      | FALSE     | 2026-06-24
3  | V3             | SAP Sync 14:30    | SAP         | Rohit      | TRUE      | 2026-06-25 ← ACTIVE
```

### Simulation Table (Master Simulations)
```
id | name           | is_master | user_id | master_version_id | last_sap_sync
---|----------------|-----------|---------|-------------------|---------------
1  | Master - V1    | FALSE     | NULL    | 1                 | 2026-06-20
2  | Master - V2    | FALSE     | NULL    | 2                 | 2026-06-24
3  | Master - V3    | TRUE      | NULL    | 3                 | 2026-06-25 ← ACTIVE
```

### Simulation Table (User Simulations)
```
id | name              | is_master | user_id | master_version_id
---|-------------------|-----------|---------|-------------------
10 | Priya's Simulation| FALSE     | Priya   | 3 (V3 - latest)
11 | Rohit's Simulation| FALSE     | Rohit   | 2 (V2 - older)
```

---

## Key Guarantees

### ✅ Always True:
1. **Only ONE active MasterVersion** (`is_active=True`)
2. **Only ONE master Simulation** (`is_master=True`)
3. **Master simulations have no owner** (`user=None`)
4. **All users see the same active master**
5. **New simulations always clone from active master**
6. **Existing simulations are NEVER modified when master updates**

### ❌ Never Happens:
1. Multiple active masters simultaneously
2. Master simulation owned by a user
3. Planning Admins seeing other users' simulations
4. Automatic updates to existing user simulations

---

## Code Implementation

### Helper Function: `copy_simulation_data()`
```python
def copy_simulation_data(source_simulation, target_simulation):
    """Copy all data from source to target simulation"""
    # Deletes existing data in target
    # Copies: Suppliers, Customers, Refineries, Cargos, Plant Inventories, Comments
```

### View: `publish_simulation_to_master()`
```python
@login_required
@user_passes_test(is_planning_admin)
def publish_simulation_to_master(request, simulation_id):
    # 1. Create new MasterVersion (is_active=True)
    # 2. Deactivate old MasterVersions
    # 3. Deactivate old master Simulation (is_master=False)
    # 4. Create NEW master Simulation (is_master=True, user=None)
    # 5. Copy data from published simulation to new master
```

### View: `refresh_master_from_sap()`
```python
@login_required
@user_passes_test(is_planning_admin)
def refresh_master_from_sap(request):
    # 1. Call SAP API
    # 2. Create new MasterVersion (is_active=True, source_type='SAP')
    # 3. Deactivate old MasterVersions
    # 4. Deactivate old master Simulation
    # 5. Create NEW master Simulation with SAP data
```

---

## Testing Checklist

### Test 1: Publish to Master
- [ ] Login as Planning Admin (Rohit)
- [ ] Create and modify a simulation
- [ ] Click "Publish To Master"
- [ ] Verify new MasterVersion created (V_next)
- [ ] Verify old master simulation deactivated
- [ ] Verify NEW master simulation created with correct data
- [ ] Logout

### Test 2: User Sees New Master
- [ ] Login as Planner (Priya)
- [ ] Dashboard shows new active master (V_next)
- [ ] Click "New Simulation"
- [ ] New simulation contains data from V_next
- [ ] NOT from previous version

### Test 3: SAP Refresh
- [ ] Login as Planning Admin
- [ ] Configure SAP API URL
- [ ] Click "Refresh From SAP"
- [ ] Verify new MasterVersion created (source_type='SAP')
- [ ] Verify NEW master simulation created
- [ ] All users now see this as active master

### Test 4: Historical Versions Preserved
- [ ] Check MasterVersion table
- [ ] Old versions still exist with `is_active=False`
- [ ] Old master simulations preserved with `is_master=False`
- [ ] User simulations unchanged

---

## Migration Notes

If you have existing data:

1. **Check for multiple active masters:**
   ```python
   Simulation.objects.filter(is_master=True)
   # Should return exactly 1
   ```

2. **Check for multiple active versions:**
   ```python
   MasterVersion.objects.filter(is_active=True)
   # Should return exactly 1
   ```

3. **If inconsistencies found, fix manually:**
   ```python
   # Keep only the latest version as active
   MasterVersion.objects.update(is_active=False)
   latest_version = MasterVersion.objects.order_by('-created_at').first()
   latest_version.is_active = True
   latest_version.save()
   
   # Keep only one master simulation
   Simulation.objects.filter(is_master=True).update(is_master=False)
   latest_simulation = Simulation.objects.filter(master_version=latest_version).first()
   if latest_simulation:
       latest_simulation.is_master = True
       latest_simulation.save()
   ```

---

## Summary

The system now maintains a **single global active master** that:
- Is updated when Planning Admins publish simulations or refresh from SAP
- Is visible to ALL users (Planners and Planning Admins)
- Is used as the source for all NEW simulations
- Preserves historical versions for audit trail
- Never modifies existing user simulations

This ensures data consistency across the entire organization while allowing Planning Admins to evolve the master data through controlled workflows.
