from django.contrib import admin
from .models import CustomerDate, Refinery, RefineryDate, Simulation, SimulationComment, Supplier, Cargo, Customer, Plant, PlantInventory, APIConfiguration, SupplierDate, MasterVersion, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'user', 'department', 'designation', 'is_active_employee']
    list_filter = ['department', 'designation', 'is_active_employee']
    search_fields = ['employee_id', 'full_name', 'user__username', 'user__email']
    readonly_fields = ['user']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('user', 'employee_id', 'full_name')
        }),
        ('Additional Details', {
            'fields': ('department', 'designation', 'is_active_employee')
        })
    )


@admin.register(MasterVersion)
class MasterVersionAdmin(admin.ModelAdmin):
    list_display = ['version_number', 'name', 'source_type', 'created_by', 'created_at', 'is_active']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['version_number', 'name', 'description']
    readonly_fields = ['version_number', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']


class PlantInventoryInline(admin.TabularInline):
    model = PlantInventory
    extra = 1
    fields = ['plant', 'opening_inventory']


class SupplierInline(admin.TabularInline):
    model = Supplier
    extra = 1
    fields = ['name', 'plant', 'preference']


class CargoInline(admin.TabularInline):
    model = Cargo
    extra = 1
    fields = ['cargo_name', 'plant', 'delivery_date', 'amount']


class CustomerInline(admin.TabularInline):
    model = Customer
    extra = 1
    fields = ['name', 'plant', 'preference']

class RefineryInline(admin.TabularInline):
    model = Refinery
    extra = 1
    fields = ['name', 'plant', 'preference']

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'start_date', 'end_date', 'is_master', 'is_active', 'master_version', 'last_sap_sync', 'updated_at']
    list_filter = ['is_active', 'is_master', 'created_at', 'user', 'master_version']
    search_fields = ['name', 'user__username']
    date_hierarchy = 'created_at'
    inlines = [PlantInventoryInline, SupplierInline, CargoInline, CustomerInline, RefineryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'is_active', 'is_master')
        }),
        ('Master Version Tracking', {
            'fields': ('master_version',),
            'description': 'Master version this simulation was created from'
        }),
        ('Planning Parameters', {
            'fields': ('start_date', 'end_date')
        }),
        ('SAP Integration (Master Only)', {
            'fields': ('sap_api_url', 'last_sap_sync'),
            'classes': ('collapse',),
            'description': 'These fields are only used for master simulations'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_sap_sync']
    
    def get_readonly_fields(self, request, obj=None):
        """Make last_sap_sync always readonly"""
        readonly = list(self.readonly_fields)
        if obj and obj.is_master:
            # When editing master, show last_sap_sync as readonly
            pass
        return readonly

@admin.register(SimulationComment)
class SimulationCommentAdmin(admin.ModelAdmin):
    list_display = [
        'simulation',
        'created_by',
        'created_at'
    ]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plant',
        'simulation',
        'preference',
        'created_at'
    ]

    list_filter = ['plant', 'simulation']
    search_fields = ['name']

@admin.register(SupplierDate)
class SupplierDateAdmin(admin.ModelAdmin):
    list_display = [
        'supplier',
        'from_date',
        'to_date',
        'daily_supply'
    ]

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['cargo_name', 'plant', 'simulation', 'delivery_date', 'amount']
    list_filter = ['simulation', 'plant', 'delivery_date']
    search_fields = ['cargo_name', 'simulation__name', 'plant__name']
    date_hierarchy = 'delivery_date'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plant',
        'simulation',
        'preference',
        'created_at'
    ]

    list_filter = ['plant', 'simulation']
    search_fields = ['name']

@admin.register(CustomerDate)
class CustomerDateAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'from_date',
        'to_date',
        'daily_demand'
    ]

@admin.register(Refinery)
class RefineryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plant',
        'simulation',
        'preference',
        'created_at'
    ]

@admin.register(RefineryDate)
class RefineryDateAdmin(admin.ModelAdmin):
    list_display = [
        'refinery',
        'from_date',
        'to_date',
        'daily_refinery_demand'
    ]

@admin.register(APIConfiguration)
class APIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'api_url', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'api_url', 'user__username']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'api_url')
        }),
        ('Supplier Mapping', {
            'fields': (
                'supplier_table',
                'supplier_name_col',
                'supplier_daily_supply_col',
                'supplier_from_date_col',
                'supplier_to_date_col'
            )
        }),
        ('Cargo Mapping', {
            'fields': (
                'cargo_table',
                'cargo_name_col',
                'cargo_date_col',
                'cargo_amount_col'
            )
        }),
        ('Customer Mapping', {
            'fields': (
                'customer_table',
                'customer_name_col',
                'customer_daily_demand_col',
                'customer_from_date_col',
                'customer_to_date_col'
            )
        }),
    )