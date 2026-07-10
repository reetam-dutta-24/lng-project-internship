# Read the file
with open(r'c:\Users\PrajapatiMK_intern\Downloads\first\LNG\lng_planner\templates\lng_planner\supplier_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add JavaScript for handling existing ranges
old_script = '''    <script>
        let dateRangeCount = 0;

        document.getElementById('addDateRangeBtn').addEventListener'''

new_script = '''    <script>
        let dateRangeCount = 0;
        const existingRangesToDelete = new Set();

        function removeExistingRange(rangeId) {
            if (confirm('Are you sure you want to remove this date range?')) {
                existingRangesToDelete.add(rangeId);
                const element = document.querySelector(`[data-range-id="${rangeId}"]`);
                if (element) {
                    element.style.opacity = '0.5';
                    element.style.pointerEvents = 'none';
                }
            }
        }

        document.getElementById('addDateRangeBtn').addEventListener'''

content = content.replace(old_script, new_script)

# Add form submission handler to include deleted range IDs
old_submit = '''    </script>
</body>
</html>'''

new_submit = '''        // Add hidden inputs for deleted ranges before form submission
        document.querySelector('form').addEventListener('submit', function(e) {
            existingRangesToDelete.forEach(rangeId => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'delete_date_range';
                input.value = rangeId;
                this.appendChild(input);
            });
        });
    </script>
</body>
</html>'''

content = content.replace(old_submit, new_submit)

# Write back
with open(r'c:\Users\PrajapatiMK_intern\Downloads\first\LNG\lng_planner\templates\lng_planner\supplier_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript updated successfully!")
