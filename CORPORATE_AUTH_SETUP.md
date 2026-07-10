# LNG Planning System - Corporate Authentication Setup

## Overview
This is an internal corporate LNG Planning System with role-based access control. **No self-registration** - all employee accounts are pre-created by the organization.

---

## Role Structure

### Employee Roles (Business Roles)
1. **Planner** - Can create and manage their own simulations
2. **Planning Admin** - Can view all simulations, refresh SAP data, publish to master

### Django Superuser (Technical Admin Only)
- Separate from employee roles
- Created manually via `createsuperuser` command
- Full access to Django admin interface
- ONLY role that can assign/change employee roles
- Should NOT be used for daily planning operations

---

## Mock Employee Credentials

| Employee ID | Username | Password | Role | Name |
|-------------|----------|----------|------|------|
| EMP001 | planningadmin | admin123 | Planning Admin | Planning Head |
| EMP002 | mahesh | admin123 | Planner | Mahesh |
| EMP003 | rohit | admin123 | Planner | Rohit |
| EMP004 | amit | admin123 | Planner | Amit |
| EMP005 | neha | admin123 | Planner | Neha |
| EMP006 | priya | admin123 | Planner | Priya |
| EMP007 | arjun | admin123 | Planner | Arjun |
| EMP008 | vikas | admin123 | Planner | Vikas |
| EMP009 | ankit | admin123 | Planner | Ankit |
| EMP010 | pooja | admin123 | Planner | Pooja |

**Note:** These are mock credentials for development/testing only. In production, use real employee IDs and secure passwords.

---

## Setup Instructions

### Step 1: Run Database Migrations
```powershell
cd c:\Users\PrajapatiMK_intern\Downloads\first\LNG
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Django Superuser (Manual - Required)
```powershell
python manage.py createsuperuser
```

**Interactive prompts:**
- Username: e.g., `sysadmin` or your employee ID
- Email: Your email address  
- Password: Enter a **secure password** (minimum 8 characters, mix of letters/numbers/symbols)
- Password (again): Confirm password

**IMPORTANT:** 
- This creates the ONLY account that can manage employee roles
- Do NOT use mock credentials for superuser
- Remember these credentials - you'll need them to assign roles to employees

### Step 3: Setup Mock Employees and Groups
```powershell
python manage.py setup_auth_system
```

**Expected Output:**
```
🔐 Setting up Authentication System...

✅ Created group: Planner
✅ Created group: Planning Admin

✅ Found 1 Django superuser(s)

Creating employees...
✅ EMP001 - planningadmin (Planning Head) → Planning Admin
✅ EMP002 - mahesh (Mahesh) → Planner
✅ EMP003 - rohit (Rohit) → Planner
... (continues for all 9 planners)

Setup complete!
```

### Step 4: Assign Roles to Employees via Django Admin

1. **Start the server:**
   ```powershell
   python manage.py runserver
   ```

2. **Login as Django Superuser:**
   - Navigate to: http://127.0.0.1:8000/login/
   - Username: [your superuser username]
   - Password: [your superuser password]

3. **Access Django Admin:**
   - Navigate to: http://127.0.0.1:8000/admin/
   - Login with your superuser credentials

4. **Assign Planning Admin Role:**
   - Go to "Groups" → "Planning Admin"
   - Click "Add users" or select from available
   - Add `planningadmin` (EMP001) to the group
   - Save changes

5. **Assign Planner Roles:**
   - Go to "Groups" → "Planner"  
   - Select all employees EMP002-EMP010
   - Add them to the group
   - Save changes

**Alternative: Use the management command which auto-assigns roles automatically.**

---

## Application Flow

### Root URL Behavior
```
/  → Automatically redirects to /login/
```

### Login Process
1. Navigate to http://127.0.0.1:8000/
2. Redirected to login page
3. Enter Employee ID or Username + Password
4. On success → Redirected to dashboard with role-appropriate access

### Logout Process
1. Click "Logout" button in navbar
2. Session cleared
3. Redirected back to login page

---

## Permission Matrix

| Feature | Planner | Planning Admin | Django Superuser |
|---------|---------|----------------|------------------|
| Create Simulation | ✅ Own only | ✅ All | ✅ All |
| View Simulations | ✅ Own only | ✅ All | ✅ All |
| Edit Simulations | ✅ Own only | ✅ All | ✅ All |
| Delete Simulations | ✅ Own only | ✅ All | ✅ All |
| Refresh SAP Data | ❌ | ✅ | ✅ |
| Publish to Master | ❌ | ✅ | ✅ |
| View Master History | ❌ | ✅ | ✅ |
| Export Reports | ✅ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| Assign Roles | ❌ | ❌ | ✅ |
| Access Django Admin | ❌ | ❌ | ✅ |

---

## Simulation Visibility Rules

### Planner View
```python
Simulation.objects.filter(user=request.user, is_master=False)
```
- Can ONLY see simulations they created
- Cannot see other planners' work
- Cannot see Planning Admin's simulations

### Planning Admin View  
```python
Simulation.objects.filter(is_master=False)
```
- Can see ALL user simulations
- Used for reviewing planning scenarios
- Can compare different planner submissions

### Django Superuser View
```python
Simulation.objects.all()
```
- Full access including master simulation
- Can manage all aspects of the system

---

## Security Features

### 1. No Self-Registration
- Registration page removed
- Registration routes disabled  
- All accounts pre-created by organization

### 2. Role-Based Access Control
- Decorators: `@admin_or_super_user_required`
- Class-based mixins: `AdminOrSuperUserRequiredMixin`
- Template-level checks: `{% if is_planning_admin %}`

### 3. Simulation Ownership Enforcement
- Views filter by role, not just templates
- Database queries enforce visibility rules
- API endpoints validate permissions

### 4. Django Superuser Separation
- Employee roles ≠ Django superuser
- Role management ONLY via Django admin
- Planning Admins cannot promote/demote users

---

## Testing Checklist

### Test 1: Login as Planning Admin
```
Username: planningadmin (or EMP001)
Password: admin123
Expected: 
✅ Blue "Planning Admin" badge in navbar
✅ Can see ALL simulations in dropdown
✅ SAP Refresh button visible
✅ Publish to Master button visible
✅ Cannot access /admin/ URL
```

### Test 2: Login as Planner
```
Username: mahesh (or EMP002)
Password: admin123
Expected:
✅ Green "Planner" badge in navbar
✅ Can see ONLY mahesh's simulations
✅ SAP Refresh button NOT visible
✅ Publish to Master button NOT visible
✅ Cannot access /admin/ URL
```

### Test 3: Login as Django Superuser
```
Username: [your superuser username]
Password: [your superuser password]
Expected:
✅ Purple "Django Superuser" badge in navbar
✅ Can see ALL simulations
✅ All admin features available
✅ CAN access /admin/ URL
✅ CAN manage user roles
```

### Test 4: Unauthenticated Access
```
Navigate to: http://127.0.0.1:8000/dashboard/
Expected:
✅ Redirected to /login/
✅ Cannot bypass authentication
```

### Test 5: Root URL Redirect
```
Navigate to: http://127.0.0.1:8000/
Expected:
✅ Automatically redirects to /login/
✅ No landing page shown
```

---

## Troubleshooting

### Issue: "Group 'Planner' does not exist"
**Solution:** Run `python manage.py setup_auth_system`

### Issue: Login redirect loop
**Solution:** Check `LOGIN_URL = 'lng_planner:login'` in settings.py

### Issue: User can't see simulations they created
**Solution:** Verify user is logged in and simulation has correct `user` field

### Issue: Planning Admin can't see SAP Refresh button
**Solution:** 
1. Verify user is in "Planning Admin" group
2. Check context processor registered in settings.py
3. Clear browser cache

### Issue: Cannot access Django admin
**Solution:** Only accounts created via `createsuperuser` can access /admin/

---

## File Structure Changes

### Removed Files:
- ❌ `landing.html` - No public landing page
- ❌ `register.html` - No self-registration
- ❌ Registration forms and views

### Modified Files:
- ✅ `urls.py` - Root redirects to login, registration routes removed
- ✅ `login.html` - Clean corporate login form only
- ✅ `navbar.html` - Removed register links, shows user info
- ✅ `views_auth.py` - Registration view removed
- ✅ `settings.py` - LOGIN_URL updated

### Unchanged Files:
- ⏸️ `models.py` - Employee model unchanged
- ⏸️ `decorators.py` - Permission decorators unchanged
- ⏸️ `context_processors.py` - Role context unchanged

---

## Production Deployment Notes

1. **Change All Mock Passwords:**
   ```python
   # In Django admin or via shell
   user = User.objects.get(username='planningadmin')
   user.set_password('NEW_SECURE_PASSWORD')
   user.save()
   ```

2. **Enable HTTPS:**
   - Force HTTPS redirects in production
   - Set `SECURE_SSL_REDIRECT = True`

3. **Update Password Policies:**
   - Enforce minimum 12 characters
   - Require special characters
   - Implement password rotation

4. **Audit Logging:**
   - Enable Django audit logs
   - Monitor role changes
   - Track simulation publishes

5. **Backup Strategy:**
   - Regular database backups
   - Export user data periodically
   - Version control for master simulations

---

## Support & Contact

For issues or questions:
1. Check this setup guide first
2. Review Django authentication docs: https://docs.djangoproject.com/en/stable/topics/auth/
3. Verify all setup steps completed in order
4. Contact system administrator for role management requests

---

**Status:** ✅ Ready for corporate deployment  
**Last Updated:** 2025-06-25  
**Version:** 2.0 (Corporate Edition)
