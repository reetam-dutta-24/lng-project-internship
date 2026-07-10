"""
Management command to setup authentication system with mock data.

Usage: python manage.py setup_auth_system

This will:
1. Create 'Planner' and 'Planning Admin' groups (NOT Super User group)
2. Create sample employees as specified
3. Provide instructions for creating Django superuser using createsuperuser command
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from lng_planner.models import Employee


class Command(BaseCommand):
    help = 'Setup authentication system with roles and mock employee data'

    def handle(self, *args, **options):
        self.stdout.write('🔐 Setting up Authentication System...\n')
        
        # Create only business role groups (NOT Super User)
        role_groups = ['Planner', 'Planning Admin']
        
        for role_name in role_groups:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created group: {role_name}'))
            else:
                self.stdout.write(f'  ℹ️  Group already exists: {role_name}')
        
        # Check if superuser exists
        superusers = User.objects.filter(is_superuser=True)
        if not superusers.exists():
            self.stdout.write(self.style.WARNING('\n⚠️  No Django superuser found!'))
            self.stdout.write('   Please create one manually using:')
            self.stdout.write('   python manage.py createsuperuser')
            self.stdout.write('   \n   Do NOT use the mock credentials below for superuser!\n')
        else:
            self.stdout.write(self.style.SUCCESS(f'\n  ✅ Found {superusers.count()} Django superuser(s)'))
        
        # Create mock employees - Planning Admin only
        planning_admins = [
            {
                'employee_id': 'EMP001',
                'username': 'planningadmin',
                'password': 'admin123',
                'first_name': 'Planning',
                'last_name': 'Head',
                'email': 'planning.admin@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planning Admin',
                'role': 'Planning Admin'
            },
        ]
        
        # Create mock employees - Planners only
        planners = [
            {
                'employee_id': 'EMP002',
                'username': 'mahesh',
                'password': 'admin123',
                'first_name': 'Mahesh',
                'last_name': '',
                'email': 'mahesh@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP003',
                'username': 'rohit',
                'password': 'admin123',
                'first_name': 'Rohit',
                'last_name': '',
                'email': 'rohit@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP004',
                'username': 'amit',
                'password': 'admin123',
                'first_name': 'Amit',
                'last_name': '',
                'email': 'amit@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP005',
                'username': 'neha',
                'password': 'admin123',
                'first_name': 'Neha',
                'last_name': '',
                'email': 'neha@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP006',
                'username': 'priya',
                'password': 'admin123',
                'first_name': 'Priya',
                'last_name': '',
                'email': 'priya@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP007',
                'username': 'arjun',
                'password': 'admin123',
                'first_name': 'Arjun',
                'last_name': '',
                'email': 'arjun@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP008',
                'username': 'vikas',
                'password': 'admin123',
                'first_name': 'Vikas',
                'last_name': '',
                'email': 'vikas@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP009',
                'username': 'ankit',
                'password': 'admin123',
                'first_name': 'Ankit',
                'last_name': '',
                'email': 'ankit@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
            {
                'employee_id': 'EMP010',
                'username': 'pooja',
                'password': 'admin123',
                'first_name': 'Pooja',
                'last_name': '',
                'email': 'pooja@lngplanner.com',
                'department': 'Planning',
                'designation': 'Planner',
                'role': 'Planner'
            },
        ]
        
        all_employees = planning_admins + planners
        created_count = 0
        
        for emp_data in all_employees:
            if not User.objects.filter(username=emp_data['username']).exists():
                # Create user
                user = User.objects.create_user(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    password=emp_data['password'],
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name']
                )
                
                # Create employee profile
                employee = Employee.objects.create(
                    user=user,
                    employee_id=emp_data['employee_id'],
                    full_name=f"{user.first_name} {user.last_name}".strip(),
                    department=emp_data['department'],
                    designation=emp_data['designation']
                )
                
                # Assign role (Planner or Planning Admin)
                role_group = Group.objects.get(name=emp_data['role'])
                user.groups.add(role_group)
                
                self.stdout.write(f'  ✅ Created: {emp_data["employee_id"]} - {emp_data["first_name"]} ({emp_data["role"]})')
                created_count += 1
            else:
                self.stdout.write(f'  ℹ️  User already exists: {emp_data["username"]}')
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Authentication System Setup Complete!'))
        self.stdout.write('='*60)
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  - Groups created: Planner, Planning Admin')
        self.stdout.write(f'  - Employees created: {created_count}')
        
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('\n⚠️  IMPORTANT: Create Django superuser manually!'))
            self.stdout.write('   Run: python manage.py createsuperuser')
            self.stdout.write('   Do NOT use mock credentials for superuser.')
        
        self.stdout.write(f'\n📋 Mock Employee Accounts (all passwords: admin123):')
        self.stdout.write(self.style.SUCCESS('\n   Planning Admin:'))
        self.stdout.write(f'     Username: planningadmin')
        self.stdout.write(f'     Employee ID: EMP001')
        self.stdout.write(f'     Name: Planning Head')
        
        self.stdout.write(self.style.SUCCESS('\n   Planners:'))
        self.stdout.write(f'     mahesh (EMP002)')
        self.stdout.write(f'     rohit (EMP003)')
        self.stdout.write(f'     amit (EMP004)')
        self.stdout.write(f'     neha (EMP005)')
        self.stdout.write(f'     priya (EMP006)')
        self.stdout.write(f'     arjun (EMP007)')
        self.stdout.write(f'     vikas (EMP008)')
        self.stdout.write(f'     ankit (EMP009)')
        self.stdout.write(f'     pooja (EMP010)')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Role Management:'))
        self.stdout.write('   Only Django superusers can manage user roles via /admin/')
        self.stdout.write('   Navigate to Authentication > Users > Select User > Groups')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANT: Change default passwords in production!'))
        self.stdout.write('='*60)
