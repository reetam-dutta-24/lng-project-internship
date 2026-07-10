# Authentication & Role Management System - Simplified Setup Guide

## Overview

This document describes the simplified authentication system using Django's built-in superuser functionality with two business roles: **Planner** and **Planning Admin**.

---

## Role Structure

### 1. Django Superuser (System Administrator)
- Created using Django's `createsuperuser` command
- NOT stored as a Group - uses Django's built-in `is_superuser` flag
- Full system access including Django admin interface
- Can manage all users and roles
- Can perform all Planning Admin actions

### 2. Planning Admin (Business Administrator)
- Stored in Django Group: "Planning Admin"
- Permissions:
  - ✅ Refresh From SAP
  - ✅ Publish Simulation To Master
  - ✅ View All Simulations
  - ✅ View Master Version History
  - ✅ Create/Edit Simulations
  - ✅ Export Data
- Cannot:
  - ❌ Manage user roles (Superuser only)
  - ❌ Access Django admin user management

### 3. Planner (Regular User)
- Stored in Django Group: "Planner"
- Permissions:
  - ✅ Create Simulations
  - ✅ Edit Own Simulations Only
  - ✅ Run Planning
  - ✅ Add Comments
  - ✅ Export Data
- Cannot:
  - ❌ Refresh SAP
  - ❌ Publish To Master
  - ❌ View other users' simulations
  - ❌ Manage users

---

## Setup Instructions

### Step 1: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Django Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: `admin` (or your preferred username)
- Email: (optional)
- Password: (choose a secure password)
- Password (again): (confirm)

**This superuser will have full system access.**

### Step 3: Setup Business Roles and Mock Data

```bash
python manage.py setup_auth_system
```

This command will:
1. Create "Planner" and "Planning Admin" groups
2. Create sample employees with default Planner role
3. Provide login credentials for testing

---

## Default Test Accounts

### Django Superuser
- Username: (whatever you created in Step 2)
- Password: (your chosen password)
- Access: Full system + Django admin

### Sample Planners (password: `planner123`)
- mahesh.prajapati / EMP002
- rohit.sharma / EMP003
- amit.kumar / EMP004
- priya.singh / EMP005
- sneha.reddy / EMP006

### Sample Planning Admins (password: `admin123`)
- rajesh.verma / EMP009
- pooja.nair / EMP010

---

## User Management

### For Django Superusers Only

Superusers manage roles through Django's built-in admin interface:

1. Go to `/admin/`
2. Navigate to **Authentication and Authorization** > **Users**
3. Select a user to edit
4. In the **Groups** section, add/remove:
   - `Planner` group → User becomes Planner
   - `Planning Admin` group → User becomes Planning Admin
5. Save changes

**Note:** Do NOT create a "Super User" group. Django superusers are identified by `is_superuser=True`, not group membership.

---

## Login Flow

1. User goes to login page (`/login/`)
2. Enters **Username OR Employee ID** + Password
3. System authenticates using Django's authentication
4. User is redirected to dashboard with role-based permissions

---

## Registration Flow

New employees register at `/register/`:

1. Enter: Employee ID, First Name, Last Name, Email, Password
2. System creates user account
3. **Automatically assigns "Planner" group** (cannot be changed during registration)
4. User is logged in and redirected to dashboard

---

## Permission Checks in Code

### Check for Django Superuser
```python
if request.user.is_superuser:
    # Full access
```

### Check for Planning Admin or Superuser
```python
if request.user.is_superuser or request.user.groups.filter(name='Planning Admin').exists():
    # Admin-level access
```

### Using Decorators
```python
from .decorators import admin_or_super_user_required

@admin_or_super_user_required
def my_view(request):
    # Only Planning Admins and Superusers can access
```

### Filter Simulations by Role
```python
# For Planners - only their own simulations
simulations = Simulation.objects.filter(user=request.user)

# For Planning Admins/Superusers - all simulations
if request.user.is_superuser or request.user.groups.filter(name='Planning Admin').exists():
    simulations = Simulation.objects.all()
else:
    simulations = Simulation.objects.filter(user=request.user)
```

---

## Template Variables

Available in all templates via context processor:

```django
{% if is_super_user %}
    <!-- Show superuser-only content -->
{% endif %}

{% if is_planning_admin %}
    <!-- Show admin-level content (includes superusers) -->
{% endif %}

{% if user_role == 'Planner' %}
    <!-- Show planner-specific content -->
{% endif %}
```

---

## Security Notes

1. **Never create a "Super User" group** - Use Django's built-in `is_superuser` flag
2. **Only Django superusers can manage roles** - Planning Admins cannot change user roles
3. **Planners see only their own simulations** - Enforced in view logic
4. **Change default passwords** before production use
5. **Use HTTPS** in production for authentication

---

## Troubleshooting

### "User has no permission" error
- Check if user is in correct group (Planner or Planning Admin)
- Verify the view has proper decorator (`@admin_or_super_user_required`)

### Cannot access `/admin/`
- Only Django superusers can access Django admin
- Create superuser using `python manage.py createsuperuser`

### Role changes not working
- Only Django superusers can change roles via `/admin/`
- Do NOT try to create "Super User" group

---

## Summary

✅ **Django Superuser** - System administration (created with `createsuperuser`)  
✅ **Planning Admin** - Business operations (stored in Group)  
✅ **Planner** - Regular users (stored in Group, default for new registrations)  

🚫 **NO "Super User" group** - Use Django's built-in superuser functionality

---

For questions or issues, refer to the code comments or Django documentation.
