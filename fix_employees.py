"""
Quick script to fix employee roles and create missing employees
Run with: python manage.py shell -c "exec(open('fix_employees.py').read())"
"""
from django.contrib.auth.models import User, Group
from lng_planner.models import Employee

# Create groups if they don't exist
planning_admin_group, _ = Group.objects.get_or_create(name='Planning Admin')
planner_group, _ = Group.objects.get_or_create(name='Planner')

print("=== Creating Missing Employees ===\n")

# List of employees to create
employees_to_create = [
    {'employee_id': 'EMP004', 'username': 'amit', 'password': 'admin123', 'first_name': 'Amit', 'last_name': '', 'email': 'amit@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP005', 'username': 'neha', 'password': 'admin123', 'first_name': 'Neha', 'last_name': '', 'email': 'neha@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP006', 'username': 'priya', 'password': 'admin123', 'first_name': 'Priya', 'last_name': '', 'email': 'priya@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP007', 'username': 'arjun', 'password': 'admin123', 'first_name': 'Arjun', 'last_name': '', 'email': 'arjun@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP008', 'username': 'vikas', 'password': 'admin123', 'first_name': 'Vikas', 'last_name': '', 'email': 'vikas@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP009', 'username': 'ankit', 'password': 'admin123', 'first_name': 'Ankit', 'last_name': '', 'email': 'ankit@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
    {'employee_id': 'EMP010', 'username': 'pooja', 'password': 'admin123', 'first_name': 'Pooja', 'last_name': '', 'email': 'pooja@lngplanner.com', 'department': 'Planning', 'designation': 'Planner'},
]

# Create missing users and employees
for emp_data in employees_to_create:
    if not User.objects.filter(username=emp_data['username']).exists():
        user = User.objects.create_user(
            username=emp_data['username'],
            email=emp_data['email'],
            password=emp_data['password'],
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name']
        )
        
        employee = Employee.objects.create(
            user=user,
            employee_id=emp_data['employee_id'],
            full_name=f"{emp_data['first_name']} {emp_data['last_name']}".strip() or emp_data['first_name'],
            department=emp_data['department'],
            designation=emp_data['designation']
        )
        
        # Assign to Planner group
        user.groups.add(planner_group)
        
        print(f"✅ Created: {emp_data['employee_id']} - {emp_data['username']} ({emp_data['first_name']}) → Planner")
    else:
        print(f"ℹ️  Already exists: {emp_data['username']}")

# Fix existing users' roles
print("\n=== Assigning Roles to Existing Users ===\n")

# planningadmin should be Planning Admin
planning_admin_user = User.objects.get(username='planningadmin')
if not planning_admin_user.groups.filter(name='Planning Admin').exists():
    planning_admin_user.groups.clear()
    planning_admin_user.groups.add(planning_admin_group)
    print(f"✅ Assigned Planning Admin role to: {planning_admin_user.username}")

# mahesh and rohit should be Planners
for username in ['mahesh', 'rohit']:
    user = User.objects.get(username=username)
    if not user.groups.filter(name='Planner').exists():
        user.groups.clear()
        user.groups.add(planner_group)
        print(f"✅ Assigned Planner role to: {user.username}")

# Print summary
print("\n=== Final Employee List ===\n")
employees = Employee.objects.all().order_by('employee_id')
for emp in employees:
    role = "Planning Admin" if emp.user.groups.filter(name='Planning Admin').exists() else "Planner"
    print(f"{emp.employee_id}: {emp.full_name} ({emp.user.username}) - {role}")

print(f"\n✅ Setup complete! Total employees: {employees.count()}")
