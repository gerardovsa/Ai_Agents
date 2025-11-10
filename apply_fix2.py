"""Apply Fix 2: Two-step form creation"""

# Read file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Applying Fix 2: Two-step form creation...")

# Find and replace lines 82-96 (the form creation logic)
# Line 82 should be "        service = _get_forms_service()"

# Find the start of the function body
start_idx = None
for i, line in enumerate(lines):
    if i >= 80 and 'service = _get_forms_service()' in line:
        start_idx = i
        break

if start_idx is None:
    print("❌ Could not find service = _get_forms_service() line")
    exit(1)

print(f"Found service line at index {start_idx} (line {start_idx+1})")

# Find the end (should be the "# Make it shareable" comment)
end_idx = None
for i in range(start_idx, min(start_idx + 30, len(lines))):
    if '# Make it shareable' in lines[i]:
        end_idx = i
        break

if end_idx is None:
    print("❌ Could not find '# Make it shareable' comment")
    exit(1)

print(f"Found end marker at index {end_idx} (line {end_idx+1})")

# New code to insert
new_code = """        service = _get_forms_service()

        # STEP 1: Create form with ONLY title (API restriction)
        # Google Forms API only accepts 'title' during creation
        # All other fields must be added via batchUpdate
        form_info = {
            'title': title
        }

        form = {'info': form_info}

        result = service.forms().create(body=form).execute()
        form_id = result['formId']

        # STEP 2: Add description and documentTitle via batchUpdate if provided
        if description or document_title:
            batch_requests = []

            if description:
                batch_requests.append({
                    'updateFormInfo': {
                        'info': {'description': description},
                        'updateMask': 'description'
                    }
                })

            if document_title and document_title != title:
                batch_requests.append({
                    'updateFormInfo': {
                        'info': {'documentTitle': document_title},
                        'updateMask': 'documentTitle'
                    }
                })

            if batch_requests:
                service.forms().batchUpdate(
                    formId=form_id,
                    body={'requests': batch_requests}
                ).execute()
                print(f"Added description/documentTitle to form: {form_id}")

        # Make it shareable (anyone with link can respond)
"""

# Replace the section
new_lines = lines[:start_idx] + [new_code] + lines[end_idx+1:]

# Write back
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Replaced lines {start_idx+1}-{end_idx+1}")
print("✅ Two-step form creation applied!")
