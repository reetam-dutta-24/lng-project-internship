# Bulk Supply Adjustment Feature

## Overview
This feature allows planners to quickly adjust supplier capacity by a percentage and automatically update all linked customers and refineries. This is useful when a supplier informs the planner that their supply capacity has changed.

## Implementation Details

### Files Modified
1. **views.py** - Added `bulk_supply_adjustment()` function
2. **urls.py** - Added route for bulk adjustment endpoint
3. **dashboard.html** - Added button, modal dialog, and JavaScript functions

### Key Features

#### 1. Button Placement
- Located in the Suppliers tab next to "Add New Supplier"
- Styled with blue background to distinguish from CRUD buttons
- Only visible when there's an active simulation

#### 2. Modal Dialog Components
- **Supplier Selection**: Dropdown showing all suppliers in current simulation
- **Adjustment Type**: Radio buttons for Increase/Decrease
- **Percentage Input**: Numeric field (0-100%)
- **Apply To**: Always "Current Simulation Only" (disabled)
- **Preview Section**: Shows impact before applying changes

#### 3. Preview Functionality
Before applying changes, the system shows:
- Supplier name and plant
- Old supply value (example from first date range)
- New supply value after adjustment
- Number of affected customers
- Number of affected refineries
- Total records to be updated

#### 4. Update Logic
The percentage change is applied to:
1. **SupplierDate.daily_supply** - All date ranges for the selected supplier
2. **CustomerDate.daily_demand** - All customers linked to this supplier
3. **RefineryDate.daily_refinery_demand** - All refineries linked to this supplier

**Example:**
```
Initial State:
- Supplier (Shell): 10 MT/day
- Customer A: 4 MT/day
- Customer B: 6 MT/day
- Refinery X: 8 MT/day

Apply: Decrease by 20%

Result:
- Supplier (Shell): 8 MT/day (10 × 0.8)
- Customer A: 3.2 MT/day (4 × 0.8)
- Customer B: 4.8 MT/day (6 × 0.8)
- Refinery X: 6.4 MT/day (8 × 0.8)
```

#### 5. Transaction Safety
All updates are wrapped in a database transaction:
- If any update fails, ALL changes are rolled back
- No partial updates are saved
- Ensures data consistency

#### 6. Confirmation Dialog
Before finalizing, user must confirm:
- Shows which supplier will be affected
- Lists what will be updated (Supplier, Customer, Refinery)
- Warns that action cannot be automatically undone

### Technical Implementation

#### View Function (`bulk_supply_adjustment`)
```python
@login_required
def bulk_supply_adjustment(request):
    # POST: Apply changes
    if request.method == 'POST':
        with transaction.atomic():
            # Update SupplierDate records
            # Update CustomerDate records  
            # Update RefineryDate records
            # Return success response
    
    # GET: Show preview
    else:
        # Calculate multiplier based on percentage
        # Return preview data as JSON
```

#### JavaScript Functions
- `openBulkAdjustmentModal()` - Opens the modal
- `updatePreview()` - Fetches preview data via AJAX
- `showConfirmation()` - Shows confirmation dialog
- `applyBulkAdjustment()` - Submits changes via POST
- Event listeners for real-time preview updates

### URL Route
```python
path('bulk-supply-adjustment/', views.bulk_supply_adjustment, name='bulk_supply_adjustment')
```

### Usage Flow

1. **Navigate to Suppliers Tab**
   - User clicks on "Suppliers" tab in dashboard

2. **Click Bulk Adjustment Button**
   - Opens modal dialog

3. **Select Supplier**
   - Choose from dropdown (shows: "Supplier Name (Plant)")

4. **Choose Adjustment Type**
   - Increase Supply or Decrease Supply

5. **Enter Percentage**
   - Value between 0-100%

6. **Review Preview**
   - System shows old/new supply values
   - Shows count of affected entities
   - Total records to update

7. **Click "Apply Changes"**
   - Opens confirmation dialog

8. **Confirm Action**
   - User reviews what will be updated
   - Clicks "Confirm" to proceed

9. **System Updates Data**
   - All changes applied in single transaction
   - Page reloads to show updated values

10. **Verify Results**
    - Dashboard shows new supply/demand values
    - Daily inventory projection recalculates automatically

### Business Rules

#### What Gets Updated
✅ SupplierDate.daily_supply (all date ranges)
✅ CustomerDate.daily_demand (only for customers linked to selected supplier)
✅ RefineryDate.daily_refinery_demand (only for refineries linked to selected supplier)

#### What Does NOT Get Updated
❌ Master data
❌ Other simulations
❌ Customers/refineries linked to OTHER suppliers
❌ Cargo deliveries
❌ Plant inventory levels

#### Percentage Validation
- Must be between 0 and 100
- Decimal values allowed (e.g., 15.5%)
- Invalid values show error message

### Future Compatibility
- Works independently of SAP integration
- Only affects current simulation
- Does not modify master data
- Can be used before/after SAP sync

### Audit Trail
Console logs record:
- User who made adjustment
- Timestamp
- Supplier name
- Adjustment type and percentage
- Number of records updated

Example log:
```
BULK ADJUSTMENT - User: john.doe, Time: 2026-07-02 12:45:30, 
Supplier: Shell, Type: decrease, Percentage: 20.0%, 
Records Updated: 5
```

### Testing Checklist
- [ ] Select supplier with multiple date ranges
- [ ] Apply increase percentage (e.g., +15%)
- [ ] Verify all date ranges updated correctly
- [ ] Verify linked customers updated
- [ ] Verify linked refineries updated
- [ ] Check dashboard shows new values
- [ ] Verify daily inventory recalculates
- [ ] Test decrease percentage (e.g., -25%)
- [ ] Test with supplier having no linked customers
- [ ] Test with supplier having no linked refineries
- [ ] Test invalid percentage (>100 or <0)
- [ ] Test transaction rollback on error

### Known Limitations
- Only works for current active simulation
- Cannot be undone automatically (manual reversal needed)
- Preview shows only first date range as example
- No batch operations across multiple suppliers
