"""Authentication and Employee Management Forms"""
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Employee


class LoginForm(forms.Form):
    """Login form supporting both username and employee ID"""
    login_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Employee ID',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )


class EmployeeRegistrationForm(UserCreationForm):
    """Registration form for new employees"""
    employee_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Employee ID'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    class Meta:
        model = User
        fields = ['employee_id', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("Employee ID already exists. Please contact administrator.")
        return employee_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create Employee profile and assign default Planner role
            employee = Employee.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                full_name=f"{user.first_name} {user.last_name}",
                department="",
                designation=""
            )
            
            # Assign to Planner group by default
            planner_group = Group.objects.filter(name='Planner').first()
            if planner_group:
                user.groups.add(planner_group)
        
        return user


class EmployeeRoleChangeForm(forms.Form):
    """Form for Super User to change employee roles (Planner or Planning Admin only)"""
    role = forms.ChoiceField(
        choices=[
            ('Planner', 'Planner'),
            ('Planning Admin', 'Planning Admin'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if self.employee and self.employee.user.is_superuser:
            # Prevent changing superuser's role through this form
            raise forms.ValidationError("Cannot change Super User role through this interface.")
        return role
    
    def save(self):
        if self.employee:
            self.employee.set_role(self.cleaned_data['role'])


class EmployeeUpdateForm(forms.ModelForm):
    """Form for updating employee details"""
    class Meta:
        model = Employee
        fields = ['full_name', 'department', 'designation']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
        }
