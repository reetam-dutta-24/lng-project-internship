# SAP Refresh Implementation Guide

## Overview
This document describes the SAP refresh functionality that integrates with the Master Versioning system to periodically update master simulation data from an external SAP API.

## Architecture

### Key Components

1. **MasterVersion Model** - Tracks versions of master data
   - `version_number`: Unique identifier (e.g., "V1", "V2")
   - `source_type`: Either 'SAP' or 'SIMULATION'
   - `is_active`: Boolean flag for currently active version
   - `created_by`: User who triggered the refresh/publish
   - `created_at`: Timestamp of creation

2. **Simulation Model** - Stores simulation data with master version linkage
   - `master_version`: ForeignKey to MasterVersion (nullable)
   - `is_master`: Boolean flag for master simulations
   - `is_active`: Active status for user simulations
   - `sap_api_url`: Configurable SAP API endpoint URL

3. **refresh_master_from_sap() View** - Main refresh logic
   - Location: `lng_planner/views.py` (lines ~2438-2730)
   - Access: Admin users only (`is_staff`)
   - Route: `/simulation/refresh-master-sap/`

## Refresh Process Flow

### Step-by-Step Execution

1. **Authentication & Validation**
   ```python
   # Check admin privileges
   if not request.user.is_staff:
       return redirect('lng_planner:dashboard')
   
   # Get current active master
   current_master = Simulation.objects.filter(is_master=True).first()
   
   # Validate SAP API URL is configured
   if not current_master.sap_api_url:
       messages.error(request, 'SAP API URL not configured')
       return redirect('lng_planner:manage_master')
   ```

2. **Fetch Data from SAP API**
   ```python
   response = requests.get(current_master.sap_api_url, timeout=30)
   response.raise_for_status()
   sap_data = response.json()
   ```

3. **Determine Next Version Number**
   ```python
   last_version = MasterVersion.objects.filter(
       source_type='SAP'
   ).order_by('-version_number').first()
   
   if last_version:
       next_num = int(last_version.version_number.replace('V', '')) + 1
   else:
       next_num = 1
   
   version_number = f"V{next_num}"
   ```

4. **Create New MasterVersion**
   ```python
   new_master_version = MasterVersion.objects.create(
       version_number=version_number,
       name=f"SAP Sync - {datetime.now().strftime('%Y-%m-%d')}",
       source_type='SAP',
       created_by=request.user,
       description=f'Master data refreshed from SAP API on {datetime.now()}',
       is_active=True  # This becomes the active version
   )
   
   # Deactivate previous versions
   MasterVersion.objects.filter(
       source_type='SAP', 
       is_active=True
   ).exclude(pk=new_master_version.pk).update(is_active=False)
   ```

5. **Create New Master Simulation**
   ```python
   new_master = Simulation.objects.create(
       user=None,  # No owner - it's a master
       name=f"Master - {version_number} ({datetime.now().strftime('%Y-%m-%d')})",
       start_date=current_master.start_date,
       end_date=current_master.end_date,
       is_master=True,
       is_active=True,
       sap_api_url=current_master.sap_api_url,
       master_version=new_master_version  # Link to version
   )
   
   # Mark old master as inactive (preserve for history)
   current_master.is_active = False
   current_master.save()
   ```

6. **Import Data from SAP**
   
   The function imports the following entities:
   
   - **Plant Inventories**: Opening inventory levels per plant
   - **Suppliers**: With date ranges (SupplierDate model)
   - **Customers**: With date ranges and supplier mappings (CustomerDate model)
   - **Refineries**: With date ranges (RefineryDate model)
   - **Cargos**: One-time deliveries

7. **Error Handling & Reporting**
   
   Success message format:
   ```
   ✅ SAP data imported successfully.

   📦 New Master Version: V2
   📊 Records Imported:
      - 2 Plants (Created: 0, Existing: 2)
      - 10 Suppliers
      - 10 Customers
      - 3 Refineries
      - 10 Cargos
      - 2 Plant Inventories
   ⏰ Sync Time: 2026-06-23 14:30:45
   ```

## SAP API Data Format

The mock SAP API endpoint (`/api/mock-sap/`) returns data in this structure:

```json
{
    "plant_inventories": [
        {
            "plant_name": "Dahej",
            "opening_inventory": 250,
            "location": ""
        }
    ],
    
    "suppliers": [
        {
            "name": "Shell",
            "plant_name": "Dahej",
            "preference": 1,
            "date_ranges": [
                {
                    "from_date": "2026-01-01",
                    "to_date": "2026-12-31",
                    "daily_supply": 10
                }
            ]
        }
    ],
    
    "customers": [
        {
            "name": "GAIL",
            "plant_name": "Dahej",
            "preference": 1,
            "date_ranges": [
                {
                    "supplier_name": "Shell",
                    "from_date": "2026-01-01",
                    "to_date": "2026-12-31",
                    "daily_demand": 4
                }
            ]
        }
    ],
    
    "refineries": [
        {
            "name": "IOCL Refinery",
            "plant_name": "Dahej",
            "preference": 1,
            "date_ranges": [
                {
                    "from_date": "2026-01-01",
                    "to_date": "2026-12-31",
                    "daily_refinery_demand": 20
                }
            ]
        }
    ],
    
    "cargos": [
        {
            "cargo_name": "CARGO-001",
            "plant_name": "Dahej",
            "delivery_date": "2026-02-15",
            "amount": 50
        }
    ]
}
```

## Data Preservation Rules

The implementation follows these critical rules:

✅ **PRESERVED:**
- All previous Master Versions (for audit trail)
- All previous Master Simulations (historical data)
- All user simulations (unchanged)
- Plant records (shared across simulations)
- Error logs from failed imports

❌ **NOT PRESERVED:**
- Old master simulation's active status (deactivated)
- Previous active MasterVersion (deactivated)

## User Workflow

### For Administrators

1. **Configure SAP API URL**
   - Navigate to "Manage Master Simulation"
   - Set `sap_api_url` field to your SAP endpoint
   - Save the master simulation

2. **Refresh from SAP**
   - Click "Refresh From SAP" button on dashboard (when active master exists)
   - System fetches data, creates new version, and activates it
   - Success message shows import statistics

3. **View History**
   - Navigate to "Master Version History"
   - See all versions with timestamps and sources
   - Track which simulations were created from each version

### For Regular Users

1. **Create New Simulation**
   - Click "Copy from Master"
   - New simulation uses the **currently active** master version
   - Master version is automatically linked to the new simulation

2. **View Master Version**
   - Dashboard shows current master version info
   - See when it was last synced from SAP

## Error Handling

### Common Errors & Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Only administrators can refresh master data" | Non-staff user attempted refresh | Use admin account |
| "No master simulation found" | No master exists yet | Create master first via "Manage Master Simulation" |
| "SAP API URL not configured" | `sap_api_url` field is empty | Update master simulation with SAP endpoint |
| "Timeout: SAP API took too long" | Request exceeded 30 seconds | Check network/SAP server performance |
| "Connection Error" | Cannot reach SAP API URL | Verify URL and network connectivity |
| "HTTP Error 4xx/5xx" | SAP server returned error | Check SAP API status and credentials |
| "Invalid JSON" | Response not valid JSON | Verify SAP returns proper JSON format |

### Partial Import Handling

If some records fail to import:
- Successful records are committed to database
- Errors are logged in warning messages
- User sees count of successful imports + error details
- Refresh can be retried (creates new version)

## Testing with Mock API

The mock SAP endpoint provides realistic test data:

```python
# URL: /api/mock-sap/
# Returns: Sample data for 2 plants, 10 suppliers, 10 customers, 3 refineries, 10 cargos
```

**To test the refresh:**

1. Set master's `sap_api_url` to: `http://localhost:8000/api/mock-sap/`
2. Click "Refresh From SAP"
3. Verify success message shows correct counts
4. Check Master Version History for new version entry
5. Create a new simulation and verify it has the imported data

## Future Enhancements

### Potential Improvements

1. **Scheduled Refreshes**
   - Add cron job or Celery beat task for automatic daily/weekly SAP syncs
   
2. **Delta Updates**
   - Track changes between versions (what changed from V1 to V2?)
   
3. **Data Validation**
   - Validate SAP data before import (date ranges, negative values, etc.)
   
4. **Rollback Capability**
   - Ability to revert to previous master version if needed
   
5. **Diff View**
   - Show differences between current and incoming SAP data before committing
   
6. **Webhook Integration**
   - Allow SAP to push updates instead of polling

## Code References

### Key Functions

- `refresh_master_from_sap(request)` - Main refresh logic
  - File: `lng_planner/views.py`
  - Lines: ~2438-2730
  
- `mock_sap_api(request)` - Mock endpoint for testing
  - File: `lng_planner/views.py`
  - Lines: ~2734-3019

### Models Used

- `MasterVersion` - Version tracking
- `Simulation` - Master simulation storage
- `Plant` - Shared plant/terminal records
- `Supplier` + `SupplierDate` - Supply data
- `Customer` + `CustomerDate` - Demand data with supplier mapping
- `Refinery` + `RefineryDate` - Refinery demand data
- `Cargo` - One-time deliveries
- `PlantInventory` - Opening inventory levels

### URL Routes

```python
path('simulation/refresh-master-sap/', views.refresh_master_from_sap, name='refresh_master_sap'),
path('api/mock-sap/', views.mock_sap_api, name='mock_sap_api'),
```

## Security Considerations

1. **Admin-Only Access** - Only staff users can trigger SAP refresh
2. **No User Simulation Impact** - Refresh creates new master, doesn't modify existing user data
3. **API Timeout** - 30-second timeout prevents hanging requests
4. **Error Logging** - All errors are logged for audit trail

## Database Schema Changes

### MasterVersion Table
```sql
CREATE TABLE lng_planner_masterversion (
    id INTEGER PRIMARY KEY,
    version_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    source_type VARCHAR(20) CHECK (source_type IN ('SAP', 'SIMULATION')),
    created_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    source_simulation_id INTEGER REFERENCES lng_planner_simulation(id)
);
```

### Simulation Table (Updated)
```sql
ALTER TABLE lng_planner_simulation 
ADD COLUMN master_version_id INTEGER 
REFERENCES lng_planner_masterversion(id) 
NULL ON DELETE SET NULL;
```

## Conclusion

The SAP refresh functionality provides a robust, versioned approach to keeping master simulation data synchronized with external SAP systems. By creating new versions instead of overwriting existing data, the system maintains a complete audit trail while ensuring users always have access to the latest approved master data for creating their simulations.
