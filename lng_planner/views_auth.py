"""Authentication and User Management Views"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Employee
from .forms_auth import LoginForm, EmployeeRegistrationForm, EmployeeRoleChangeForm
from .decorators import admin_or_super_user_required


def custom_login(request):
    """Login view - supports both username and employee ID"""
    if request.user.is_authenticated:
        return redirect('lng_planner:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id']  # Can be username or employee ID
            password = form.cleaned_data['password']
            
            user = None
            
            # Try to authenticate by username first
            try:
                user = authenticate(request, username=login_id, password=password)
            except:
                pass
            
            # If not found by username, try by employee ID
            if not user:
                try:
                    employee = Employee.objects.select_related('user').get(
                        employee_id=login_id, 
                        is_active_employee=True
                    )
                    user = authenticate(request, username=employee.user.username, password=password)
                except Employee.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect('lng_planner:dashboard')
            else:
                form.add_error(None, "Invalid username/Employee ID or password.")
    else:
        form = LoginForm()
    
    return render(request, 'lng_planner/login.html', {'form': form})


def custom_logout(request):
    """Logout view"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('lng_planner:login')


# Registration removed - corporate system with pre-created accounts only


@login_required
def profile_view(request):
    """View and edit user's own profile"""
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        # Add your profile update logic here
        messages.success(request, "Profile updated successfully.")
        return redirect('auth:profile')
    
    context = {
        'employee': employee,
    }
    return render(request, 'lng_planner/profile.html', context)


@require_http_methods(["POST"])
def user_management(request):
    """User management screen - Django Superuser only"""
    # Only Django superusers can access this
    if not request.user.is_superuser:
        messages.error(request, "Superuser access required.")
        return redirect('lng_planner:dashboard')
    
    employees = Employee.objects.select_related('user').filter(is_active_employee=True).order_by('employee_id')
    
    # Get statistics (excluding superusers from role counts)
    total_users = employees.count()
    planners = employees.filter(user__groups__name='Planner').exclude(user__is_superuser=True).count()
    admins = employees.filter(user__groups__name='Planning Admin').exclude(user__is_superuser=True).count()
    super_user_count = employees.filter(user__is_superuser=True).count()
    
    context = {
        'employees': employees,
        'total_users': total_users,
        'planners': planners,
        'admins': admins,
        'super_users': super_user_count,
    }
    return render(request, 'lng_planner/user_management.html', context)


@require_http_methods(["POST"])
def change_employee_role(request, employee_id):
    """Change employee role - Django Superuser only"""
    # Only Django superusers can manage roles
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False, 
            'error': "Superuser access required."
        })
    
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Prevent changing own superuser status
    if employee.user == request.user:
        return JsonResponse({
            'success': False, 
            'error': "Cannot change your own role. Use Django admin for superuser management."
        })
    
    form = EmployeeRoleChangeForm(request.POST, employee=employee)
    if form.is_valid():
        role = form.cleaned_data['role']
        employee.set_role(role)
        
        messages.success(
            request, 
            f"Updated {employee.full_name}'s role to {role}."
        )
        
        return JsonResponse({
            'success': True,
            'message': f"Role updated to {role}",
            'new_role': role
        })
    
    return JsonResponse({
        'success': False, 
        'error': form.errors.as_json()
    })


@login_required
def forgot_password(request):
    """Optional: Password reset view"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        
        try:
            employee = Employee.objects.select_related('user').get(employee_id=employee_id)
            
            # In production, send email with reset link
            # For now, show message to contact admin
            messages.info(
                request, 
                "Password reset instructions have been sent to your registered email. "
                "If you don't receive it, please contact the administrator."
            )
        except Employee.DoesNotExist:
            messages.error(request, "Employee ID not found.")
    
    return render(request, 'lng_planner/forgot_password.html')


def has_role(user, role_name):
    """Helper function to check if user has a specific role"""
    return user.groups.filter(name=role_name).exists()


def get_user_role(user):
    """Get primary role of user"""
    if has_role(user, 'Super User'):
        return 'Super User'
    elif has_role(user, 'Planning Admin'):
        return 'Planning Admin'
    else:
        return 'Planner'
