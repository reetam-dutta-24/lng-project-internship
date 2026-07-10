# Simulation Visibility Fix

## Issue
Planning Admins were incorrectly seeing ALL simulations from all users instead of only their own simulations.

## Root Cause
The `dashboard` view in `views.py` had incorrect logic that gave Planning Admins visibility to all simulations:

```python
# ❌ INCORRECT (BEFORE)
if is_super_user or is_planning_admin:
    # Planning Admin and Superuser can see all simulations
    simulations = Simulation.objects.filter(is_master=False).order_by('-created_at')
else:
    # Planners can only see their own simulations
    simulations = Simulation.objects.filter(user=request.user, is_master=False).order_by('-created_at')
```

## Solution
Updated the logic to ensure ONLY Django superusers can see all simulations. Both Planners and Planning Admins now only see their own simulations:

```python
# ✅ CORRECT (AFTER)
is_super_user = request.user.is_superuser
is_planning_admin = is_super_user or request.user.groups.filter(name='Planning Admin').exists()

# ONLY superuser can see all simulations
# Both Planner and Planning Admin only see their own simulations
if is_super_user:
    simulations = Simulation.objects.filter(is_master=False).order_by('-created_at')
else:
    # Planners and Planning Admins can only see their own simulations
    simulations = Simulation.objects.filter(user=request.user, is_master=False).order_by('-created_at')
```

## Role Permissions Summary

### Planner
- ✅ Can create simulations
- ✅ Can view/edit/delete ONLY their own simulations
- ❌ Cannot access Refresh SAP
- ❌ Cannot publish to master
- ❌ Cannot see other users' simulations

### Planning Admin
- ✅ Can create simulations
- ✅ Can view/edit/delete ONLY their own simulations  
- ✅ Can access Refresh SAP (admin feature)
- ✅ Can publish simulations to master (admin feature)
- ❌ Cannot see other users' simulations

### Django Superuser
- ✅ Can view ALL simulations from all users
- ✅ Has full administrative control
- ✅ Created manually via `python manage.py createsuperuser`

## Testing Checklist

### Test 1: Planner Visibility
1. Login as `mahesh` (Planner)
2. Create a simulation called "Test Simulation"
3. Verify only "Test Simulation" appears in the dashboard
4. Logout

### Test 2: Planning Admin Visibility
1. Login as `planningadmin` (Planning Admin)
2. Create a simulation called "Admin Simulation"
3. Verify ONLY "Admin Simulation" appears in the dashboard
4. Verify you CANNOT see mahesh's "Test Simulation"
5. Verify Refresh SAP and Publish buttons are visible
6. Logout

### Test 3: Superuser Visibility (after creating superuser)
1. Create superuser: `python manage.py createsuperuser`
2. Login as superuser
3. Verify you can see BOTH mahesh's and planningadmin's simulations
4. Verify all administrative features are available

## Files Modified
- `lng_planner/views.py` - Updated `dashboard()` view simulation visibility logic

## Key Points
1. **Simulation ownership is always respected** - Users only see their own simulations unless they are superuser
2. **Planning Admin role grants admin FEATURES, not data access** - Refresh SAP, Publish to Master, etc.
3. **Only Django Superuser sees all data** - For administrative oversight
4. **Role promotion doesn't expose other users' data** - When a Planner becomes Planning Admin, they still only see their own simulations

## Dashboard Simulation Selector
The simulation dropdown will show:
- `Master (Read Only)` - Always visible
- User's own simulations only

Example for user `rohit`:
```
Master (Read Only)
Rohit Simulation 1
Rohit Simulation 2
```

Will NOT show:
```
❌ Mahesh Simulation
❌ Amit Simulation  
❌ Neha Simulation
```

Even if Rohit is a Planning Admin.
