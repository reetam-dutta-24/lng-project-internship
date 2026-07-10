from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Employee(models.Model):
    """Employee profile linked to Django User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    is_active_employee = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Role constants for reference (only business roles)
    ROLE_PLANNER = 'Planner'
    ROLE_ADMIN = 'Planning Admin'
    
    class Meta:
        ordering = ['employee_id']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
    
    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
    
    @property
    def role(self):
        """Get employee's current role"""
        if self.user.is_superuser:
            return "Super User"
        elif self.user.groups.filter(name=self.ROLE_ADMIN).exists():
            return self.ROLE_ADMIN
        else:
            return self.ROLE_PLANNER
    
    def set_role(self, role_name):
        """Set employee's role by managing group membership (Planner or Planning Admin only)"""
        # Remove from both role groups
        Group.objects.filter(name__in=[self.ROLE_PLANNER, self.ROLE_ADMIN]).update(user=self.user)
        
        # Add to new role group if valid
        if role_name in [self.ROLE_PLANNER, self.ROLE_ADMIN]:
            group = Group.objects.filter(name=role_name).first()
            if group:
                self.user.groups.add(group)
    
    @classmethod
    def get_role_groups(cls):
        """Return list of role group names (business roles only)"""
        return [cls.ROLE_PLANNER, cls.ROLE_ADMIN]


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    """Automatically create Employee profile when User is created"""
    if created and not hasattr(instance, 'employee_profile'):
        # Only auto-create for non-staff users (regular employees)
        if not instance.is_staff:
            Employee.objects.create(
                user=instance,
                employee_id=f"EMP{str(Employee.objects.count() + 1).zfill(3)}",
                full_name=instance.get_full_name() or instance.username,
                department="",
                designation=""
            )


class MasterVersion(models.Model):
    """Master version tracking for SAP sync and simulation publishing"""
    SOURCE_CHOICES = [
        ('SAP', 'SAP Integration'),
        ('SIMULATION', 'Simulation Publish'),
    ]
    
    version_number = models.CharField(max_length=50, unique=True)  # e.g., "V1", "V2"
    name = models.CharField(max_length=200, help_text="Descriptive name for this version")
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, help_text="Optional description of changes")
    is_active = models.BooleanField(default=False, help_text="Currently active master version")
    
    # Reference to source simulation if published from simulation
    source_simulation = models.ForeignKey(
        'Simulation', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='master_versions'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Master Version"
        verbose_name_plural = "Master Versions"
    
    def __str__(self):
        status = " (Active)" if self.is_active else ""
        return f"{self.version_number} - {self.name}{status}"


class Plant(models.Model):
    """Plants/Terminals where LNG is stored"""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Simulation(models.Model):
    """Stores simulation configurations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='simulations', null=True, blank=True)
    name = models.CharField(max_length=200, default='Untitled Simulation')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_master = models.BooleanField(default=False, help_text="Master simulation loaded from SAP")
    sap_api_url = models.URLField(blank=True, help_text="SAP API URL for refreshing master data")
    last_sap_sync = models.DateTimeField(null=True, blank=True, help_text="Last time master data was synced from SAP")
    
    # Master version tracking
    master_version = models.ForeignKey(
        MasterVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulations',
        help_text="Master version this simulation was created from"
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{'[MASTER] ' if self.is_master else ''}{self.name} - {self.start_date} to {self.end_date}"

class SimulationComment(models.Model):
    simulation = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    comment = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

class PlantInventory(models.Model):
    """Opening inventory for each plant in a simulation"""
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='plant_inventories')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    opening_inventory = models.FloatField(validators=[MinValueValidator(0)], help_text="MT")

    class Meta:
        unique_together = ['simulation', 'plant']
        ordering = ['plant__name']

    def __str__(self):
        return f"{self.plant.name} - {self.opening_inventory} MT"


class Supplier(models.Model):
    """Suppliers with daily supply rates"""
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='suppliers')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=200)
    preference = models.IntegerField(
        default=1,
        help_text="Lower values are served first"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['plant__name', 'preference', 'name']

    def __str__(self):
        return f"{self.name} → {self.plant.name}"

class SupplierDate(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='date_ranges'
    )

    from_date = models.DateField()
    to_date = models.DateField()
    daily_supply = models.FloatField(validators=[MinValueValidator(0)], help_text="MT per day")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['from_date']

    def __str__(self):
        return f"{self.supplier.name}: {self.from_date} - {self.to_date}"

class Cargo(models.Model):
    """One-time cargo deliveries"""
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='cargos')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='cargos')
    cargo_name = models.CharField(max_length=200)
    delivery_date = models.DateField()
    amount = models.FloatField(validators=[MinValueValidator(0)], help_text="MT")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['delivery_date', 'plant__name', 'cargo_name']

    def __str__(self):
        return f"{self.cargo_name} → {self.plant.name} - {self.amount} MT on {self.delivery_date}"


class Customer(models.Model):
    """Customers with daily demand"""
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='customers')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    preference = models.IntegerField(
        default=1,
        help_text="Lower values are served first"
    )
    class Meta:
        ordering = ['plant__name', 'preference', 'name']

    def __str__(self):
        return f"{self.name} ← {self.plant.name}"

class CustomerDate(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='date_ranges'
    )

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_date_ranges',
        help_text="Supplier serving this customer during this date range"
    )

    from_date = models.DateField()
    to_date = models.DateField()

    daily_demand = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="MT per day"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['from_date']

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "No Supplier"
        return (
            f"{self.customer.name} "
            f"({supplier_name}) : "
            f"{self.from_date} - {self.to_date}"
        )




class Refinery(models.Model):
    simulation = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        related_name='refineries'
    )
    preference = models.IntegerField(
        default=1,
        help_text="Lower values are served first"
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='refineries'
    )

    name = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['plant__name', 'preference', 'name']

    def __str__(self):
        return f"{self.name} → {self.plant.name}"
    
class RefineryDate(models.Model):
    refinery = models.ForeignKey(
        Refinery,
        on_delete=models.CASCADE,
        related_name='date_ranges'
    )

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refinery_date_ranges',
        help_text="Supplier serving this refinery during this date range"
    )

    from_date = models.DateField()
    to_date = models.DateField()
    daily_refinery_demand = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="MT per day"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['from_date']

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "No Supplier"
        return (
            f"{self.refinery.name} "
            f"({supplier_name}) : "
            f"{self.from_date} - {self.to_date}"
        )


class APIConfiguration(models.Model):
    """Store API configurations for data import"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_configs')
    name = models.CharField(max_length=200)
    api_url = models.URLField()
    
    # Supplier mapping
    supplier_table = models.CharField(max_length=100, default='suppliers')
    supplier_name_col = models.CharField(max_length=100)
    supplier_daily_supply_col = models.CharField(max_length=100)
    supplier_from_date_col = models.CharField(max_length=100)
    supplier_to_date_col = models.CharField(max_length=100)
    
    # Cargo mapping
    cargo_table = models.CharField(max_length=100, default='cargos')
    cargo_name_col = models.CharField(max_length=100)
    cargo_date_col = models.CharField(max_length=100)
    cargo_amount_col = models.CharField(max_length=100)
    
    # Customer mapping
    customer_table = models.CharField(max_length=100, default='customers')
    customer_name_col = models.CharField(max_length=100)
    customer_daily_demand_col = models.CharField(max_length=100)
    customer_from_date_col = models.CharField(max_length=100)
    customer_to_date_col = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name