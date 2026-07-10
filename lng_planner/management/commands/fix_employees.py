from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from lng_planner.models import Employee


class Command(BaseCommand):
    help = 'Fix employee roles - assign correct groups to existing employees'

    def handle(self, *args, **options):
        # Create groups if they don't exist
        planning_admin_group, _ = Group.objects.get_or_create(name='Planning Admin')
        planner_group, _ = Group.objects.get_or_create(name='Planner')
        
        self.stdout.write('=== Assigning Roles to Existing Employees ===\n')
        
        # Get all employees
        employees = Employee.objects.all().order_by('employee_id')
        
        # Define role assignments based on username
        planning_admin_usernames = ['planningadmin']
        planner_usernames = ['mahesh', 'rohit', 'amit', 'neha', 'priya', 'arjun', 'vikas', 'ankit', 'pooja']
        
        # Assign Planning Admin role
        self.stdout.write('Setting Planning Admin roles:')
        for username in planning_admin_usernames:
            try:
                user = User.objects.get(username=username)
                user.groups.clear()
                user.groups.add(planning_admin_group)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {username} → Planning Admin"))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️  {username} not found"))
        
        # Assign Planner role
        self.stdout.write('\nSetting Planner roles:')
        for username in planner_usernames:
            try:
                user = User.objects.get(username=username)
                user.groups.clear()
                user.groups.add(planner_group)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {username} → Planner"))
            except User.DoesNotExist:
                self.stdout.write(f"  ℹ️  {username} not found (will be created if needed)")
        
        # Print summary
        self.stdout.write('\n=== Final Employee List ===\n')
        for emp in employees:
            role = "Planning Admin" if emp.user.groups.filter(name='Planning Admin').exists() else "Planner"
            self.stdout.write(f"  {emp.employee_id}: {emp.full_name} ({emp.user.username}) - {role}")
        
        # Check for missing planners
        existing_usernames = [e.user.username for e in employees]
        missing_planners = [u for u in planner_usernames if u not in existing_usernames and u != 'planningadmin']
        
        if missing_planners:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Missing planners: {", ".join(missing_planners)}'))
            self.stdout.write('   These users need to be created manually or via setup_auth_system')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Role assignment complete! Total employees: {employees.count()}'))
