from django.urls import path
from . import views

app_name = 'lng_planner'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Plant management
    path('plants/', views.manage_plants, name='manage_plants'),
    path('plants/<int:plant_id>/delete/', views.delete_plant, name='delete_plant'),
    
    # Simulation management
    path('simulation/create/', views.create_simulation, name='create_simulation'),
    path('simulation/<int:simulation_id>/setup-plants/', views.setup_plants, name='setup_plants'),
    path('simulation/<int:simulation_id>/switch/', views.switch_simulation, name='switch_simulation'),
    path('simulation/<int:simulation_id>/delete/', views.delete_simulation, name='delete_simulation'),
    path('simulation/master/manage/', views.manage_master_simulation, name='manage_master'),
    path('simulation/copy-from-master/', views.copy_from_master, name='copy_from_master'),
    path('simulation/refresh-master-sap/', views.refresh_master_from_sap, name='refresh_master_sap'),
    
    # Supplier management
    path('simulation/<int:simulation_id>/supplier/add/', views.add_supplier, name='add_supplier'),
    path('supplier/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('supplier/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
    
    # Cargo management
    path('simulation/<int:simulation_id>/cargo/add/', views.add_cargo, name='add_cargo'),
    path('cargo/<int:cargo_id>/edit/', views.edit_cargo, name='edit_cargo'),
    path('cargo/<int:cargo_id>/delete/', views.delete_cargo, name='delete_cargo'),
    
    # Customer management
    path('simulation/<int:simulation_id>/customer/add/', views.add_customer, name='add_customer'),
    path('customer/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customer/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('customer-date/<int:date_range_id>/edit/', views.edit_customer_date_range, name='edit_customer_date_range'),
    path('customer-date/<int:date_range_id>/delete/', views.delete_customer_date_range, name='delete_customer_date_range'),
    
    # Refinery management
    path('simulation/<int:simulation_id>/refinery/add/', views.add_refinery, name='add_refinery'),
    path('refinery/<int:refinery_id>/edit/', views.edit_refinery, name='edit_refinery'),
    path('refinery/<int:refinery_id>/delete/', views.delete_refinery, name='delete_refinery'),
    path('refinery-date/<int:date_range_id>/edit/', views.edit_refinery_date_range, name='edit_refinery_date_range'),
    path('refinery-date/<int:date_range_id>/delete/', views.delete_refinery_date_range, name='delete_refinery_date_range'),
    
    # Supplier date range management
    path('supplier-date/<int:date_range_id>/edit/', views.edit_supplier_date_range, name='edit_supplier_date_range'),
    path('supplier-date/<int:date_range_id>/delete/', views.delete_supplier_date_range, name='delete_supplier_date_range'),
    
    # Simulation comments
    path('simulation/<int:simulation_id>/comment/add/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Export/Import
    path('simulation/<int:simulation_id>/export/excel/', views.export_excel, name='export_excel'),
    path('simulation/<int:simulation_id>/export/json/', views.export_json, name='export_json'),
    path('simulation/<int:simulation_id>/import/json/', views.import_json, name='import_json'),

    # mock sap data api
    path('api/mock-sap/', views.mock_sap_api, name='mock_sap_api'),
]