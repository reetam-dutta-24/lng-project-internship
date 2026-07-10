"""Context processors for adding user role information to all templates"""


def user_roles(request):
    """Add user role information to template context"""
    if request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        
        # Check roles using Django's built-in superuser and groups
        is_super_user = request.user.is_superuser
        is_planning_admin = is_super_user or request.user.groups.filter(name='Planning Admin').exists()
        is_planner = not is_super_user and not request.user.groups.filter(name='Planning Admin').exists()
        
        return {
            'employee': employee,
            'user_role': employee.role,
            'is_super_user': is_super_user,
            'is_planning_admin': is_planning_admin,  # Superusers have admin permissions too
            'is_planner': is_planner,
        }
    
    return {
        'employee': None,
        'user_role': None,
        'is_super_user': False,
        'is_planning_admin': False,
        'is_planner': False,
    }
