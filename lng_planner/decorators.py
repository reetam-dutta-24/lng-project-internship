"""Role-based access control decorators and mixins"""
from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def employee_required(view_func=None):
    """Decorator to require user to have an Employee profile"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            # Redirect to profile setup if no employee profile
            return redirect('auth:profile_setup')
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def role_required(*role_names):
    """
    Decorator to require specific role(s).
    Usage: @role_required('Planning Admin', 'Super User')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has any of the required roles
            user_roles = [group.name for group in request.user.groups.all()]
            
            if not any(role in user_roles for role in role_names):
                return HttpResponseForbidden(
                    "You do not have permission to access this resource."
                )
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def admin_or_super_user_required(view_func=None):
    """Decorator to require Planning Admin or Django Superuser"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is superuser OR has Planning Admin group
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.groups.filter(name='Planning Admin').exists():
            return view_func(request, *args, **kwargs)
        
        return HttpResponseForbidden(
            "Planning Admin or Superuser access required."
        )
    
    return _wrapped_view


class RoleRequiredMixin:
    """Mixin for class-based views to require specific role(s)"""
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        
        if not hasattr(request.user, 'employee_profile'):
            return redirect('auth:profile_setup')
        
        # Superusers always have access
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        user_roles = [group.name for group in request.user.groups.all()]
        
        if not any(role in user_roles for role in self.required_roles):
            return HttpResponseForbidden(
                "You do not have permission to access this resource."
            )
        
        return super().dispatch(request, *args, **kwargs)


class AdminOrSuperUserRequiredMixin(RoleRequiredMixin):
    """Mixin requiring Planning Admin or Django Superuser"""
    required_roles = ['Planning Admin']
    required_roles = ['Planning Admin', 'Super User']
