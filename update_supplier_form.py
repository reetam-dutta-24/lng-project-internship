# Read the file
with open(r'c:\Users\PrajapatiMK_intern\Downloads\first\LNG\lng_planner\templates\lng_planner\supplier_form.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "Add one or more date ranges" and replace from there
new_lines = []
i = 0
while i < len(lines):
    if 'Add one or more date ranges with daily supply quantities.' in lines[i]:
        # Replace this line and the next few lines
        new_lines.append('                    <p class="text-sm text-gray-600 mb-4">Edit existing date ranges or add new ones.</p>\n')
        new_lines.append('\n')
        new_lines.append('                    <!-- Existing date ranges -->\n')
        new_lines.append('                    {% if date_ranges %}\n')
        new_lines.append('                    <div id="existingDateRanges" class="space-y-4 mb-4">\n')
        new_lines.append('                        {% for date_range in date_ranges %}\n')
        new_lines.append('                        <div class="bg-green-50 p-6 rounded-lg border-2 border-green-300" data-range-id="{{ date_range.id }}">\n')
        new_lines.append('                            <div class="flex justify-between items-center mb-4 pb-3 border-b border-green-200">\n')
        new_lines.append('                                <h4 class="font-bold text-gray-800 text-lg">Supply Period #{{ forloop.counter }}</h4>\n')
        new_lines.append('                                <button type="button" onclick="removeExistingRange({{ date_range.id }})" \n')
        new_lines.append('                                        class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition text-sm font-semibold">\n')
        new_lines.append('                                    ✕ Remove\n')
        new_lines.append('                                </button>\n')
        new_lines.append('                            </div>\n')
        new_lines.append('                            \n')
        new_lines.append('                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">\n')
        new_lines.append('                                <div>\n')
        new_lines.append('                                    <label class="block text-sm font-semibold text-gray-700 mb-2">\n')
        new_lines.append('                                        Daily Supply (MT/day) *\n')
        new_lines.append('                                    </label>\n')
        new_lines.append('                                    <input type="number" step="0.01" name="date_ranges_{{ forloop.counter }}_daily_supply" \n')
        new_lines.append('                                           value="{{ date_range.daily_supply }}"\n')
        new_lines.append('                                           class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200" required placeholder="e.g., 10">\n')
        new_lines.append('                                    <input type="hidden" name="date_ranges_{{ forloop.counter }}_date_range_id" value="{{ date_range.id }}">\n')
        new_lines.append('                                </div>\n')
        new_lines.append('                                \n')
        new_lines.append('                                <div>\n')
        new_lines.append('                                    <label class="block text-sm font-semibold text-gray-700 mb-2">\n')
        new_lines.append('                                        From Date *\n')
        new_lines.append('                                    </label>\n')
        new_lines.append('                                    <input type="date" name="date_ranges_{{ forloop.counter }}_from_date" \n')
        new_lines.append('                                           value="{{ date_range.from_date|date:\'Y-m-d\' }}"\n')
        new_lines.append('                                           class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200" required>\n')
        new_lines.append('                                </div>\n')
        new_lines.append('                                \n')
        new_lines.append('                                <div>\n')
        new_lines.append('                                    <label class="block text-sm font-semibold text-gray-700 mb-2">\n')
        new_lines.append('                                        To Date *\n')
        new_lines.append('                                    </label>\n')
        new_lines.append('                                    <input type="date" name="date_ranges_{{ forloop.counter }}_to_date" \n')
        new_lines.append('                                           value="{{ date_range.to_date|date:\'Y-m-d\' }}"\n')
        new_lines.append('                                           class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200" required>\n')
        new_lines.append('                                </div>\n')
        new_lines.append('                            </div>\n')
        new_lines.append('                        </div>\n')
        new_lines.append('                        {% endfor %}\n')
        new_lines.append('                    </div>\n')
        new_lines.append('                    {% endif %}\n')
        new_lines.append('                    \n')
        
        # Skip the old lines until we reach "Additional date ranges container"
        i += 1
        while i < len(lines) and '<!-- Additional date ranges container -->' not in lines[i]:
            i += 1
        # Now add the additional date ranges container line
        if i < len(lines):
            new_lines.append('                    <!-- Additional date ranges container -->\n')
            i += 1
    else:
        new_lines.append(lines[i])
        i += 1

# Write back
with open(r'c:\Users\PrajapatiMK_intern\Downloads\first\LNG\lng_planner\templates\lng_planner\supplier_form.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("File updated successfully!")
