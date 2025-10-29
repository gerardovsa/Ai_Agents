# 📋 Google Forms Module - Quick Reference

**80 Functions | 9 Categories | AI-Powered | Production Ready**

---

## 🚀 Quick Start

```python
from google_workspace.google_forms import *

# Create a form
form = google_forms_create_form("My Survey")

# Add questions
google_forms_add_text_question(form['form_id'], "Your name?", index=0)
google_forms_add_multiple_choice(form['form_id'], "Favorite color?", 
    ["Red", "Blue", "Green"], index=1)

# Get responses
responses = google_forms_get_responses(form['form_id'])
print(f"Total responses: {responses['count']}")
```

---

## 📊 Function Categories

### **1. FORM MANAGEMENT** (6 functions)

```python
# Create
form = google_forms_create_form("Title")
form_id = form['form_id']

# Read
form = google_forms_get_form(form_id)

# Update
google_forms_update_info(form_id, title="New Title", description="Updated")

# Clone
cloned = google_forms_clone_form(form_id, "Copy of Form")

# Configure
google_forms_set_settings(form_id, {'collect_email': True})

# Delete
google_forms_delete_form(form_id)
```

---

### **2. ADD QUESTIONS** (9 types)

```python
# Text (short answer)
google_forms_add_text_question(form_id, "Name?", paragraph=False, required=True, index=0)

# Paragraph (long answer)
google_forms_add_text_question(form_id, "Comments?", paragraph=True, index=1)

# Multiple Choice
google_forms_add_multiple_choice(form_id, "Pick one:", ["A", "B", "C"], index=2)

# Checkbox (multiple selection)
google_forms_add_checkbox(form_id, "Select all:", ["X", "Y", "Z"], index=3)

# Dropdown
google_forms_add_dropdown(form_id, "Choose:", ["Option 1", "Option 2"], index=4)

# Linear Scale
google_forms_add_linear_scale(form_id, "Rate 1-5:", "Low", "High", 1, 5, index=5)

# Date
google_forms_add_date_question(form_id, "Event date?", include_time=True, index=6)

# Time
google_forms_add_time_question(form_id, "What time?", duration=False, index=7)

# Grid (matrix)
google_forms_add_grid(form_id, "Rate these:", 
    rows=["Item 1", "Item 2"], 
    columns=["Poor", "Good", "Excellent"], 
    index=8)

# File Upload
google_forms_add_file_upload(form_id, "Upload resume:", 
    file_types=['application/pdf'], max_files=1, index=9)
```

---

### **3. MANAGE QUESTIONS** (4 functions)

```python
# Update
google_forms_update_question(form_id, item_id, updates={'title': 'New text', 'required': True})

# Delete
google_forms_delete_question(form_id, item_id)

# Move
google_forms_move_question(form_id, item_id, new_index=3)

# Add section break
google_forms_add_section(form_id, "Page 2", "Section description", index=5)
```

---

### **4. ADD CONTENT** (3 types)

```python
# Description text
google_forms_add_description(form_id, "Please read carefully...", index=0)

# Image
google_forms_add_image(form_id, "https://example.com/image.jpg", alt_text="Logo", index=1)

# Video
google_forms_add_video(form_id, "https://youtube.com/watch?v=...", caption="Tutorial", index=2)
```

---

### **5. RESPONSES** (4 operations)

```python
# Get all
responses = google_forms_get_responses(form_id)
print(f"{responses['count']} responses")

# Get one
response = google_forms_get_response(form_id, response_id)

# Delete one
google_forms_delete_response(form_id, response_id)

# Delete all
google_forms_delete_all_responses(form_id)
```

---

### **6. QUIZ MODE** (4 functions)

```python
# Create quiz
quiz = google_forms_create_quiz("Python Quiz")

# Add graded question
google_forms_add_quiz_question(
    quiz['form_id'],
    "What is 2+2?",
    ["3", "4", "5"],
    correct_answer="4",
    points=1,
    feedback="Correct!",
    index=0
)

# Configure grading
google_forms_set_quiz_settings(quiz['form_id'], release_score='IMMEDIATELY')

# Grade response
grade = google_forms_grade_response(quiz['form_id'], response_id)
print(f"Score: {grade['total_score']}/{grade['max_score']}")
```

---

### **7. EXPORT** (4 formats)

```python
# CSV
csv_data = google_forms_export_responses_csv(form_id)
print(csv_data['data'])

# JSON
json_data = google_forms_export_responses_json(form_id)

# Statistics
stats = google_forms_get_summary_statistics(form_id)
print(f"Total responses: {stats['total_responses']}")

# With metadata
export = google_forms_export_with_metadata(form_id, include_timestamps=True)
```

---

### **8. WEBHOOKS** (4 operations)

```python
# Create webhook
watch = google_forms_create_watch(form_id, "https://your-server.com/webhook", 'RESPONSES')

# List webhooks
watches = google_forms_list_watches(form_id)

# Renew webhook (7 days)
google_forms_renew_watch(form_id, watch_id)

# Delete webhook
google_forms_delete_watch(form_id, watch_id)
```

---

## 🚀 BULK OPERATIONS

### **Create Multiple Forms**

```python
forms_config = [
    {
        'title': 'Survey 1',
        'questions': [
            {'type': 'text', 'text': 'Name', 'required': True},
            {'type': 'multiple_choice', 'text': 'Rating', 'options': ['Good', 'Bad']}
        ]
    },
    {
        'title': 'Survey 2',
        'questions': [...]
    }
]

result = google_forms_bulk_create_forms(forms_config)
print(f"Created {result['count']} forms")
```

### **Clone from Template**

```python
variations = [
    {'title': 'Event Registration - NYC'},
    {'title': 'Event Registration - LA'},
    {'title': 'Event Registration - SF'}
]

forms = google_forms_create_from_template(template_id, variations)
```

### **Batch Add Questions**

```python
questions = [
    {'type': 'text', 'text': 'Question 1', 'required': True},
    {'type': 'multiple_choice', 'text': 'Question 2', 'options': ['A', 'B']},
    {'type': 'linear_scale', 'text': 'Question 3', 'low_value': 1, 'high_value': 5}
]

google_forms_batch_add_questions(form_id, questions)
```

### **Batch Operations**

```python
# Update multiple questions
updates = [
    {'item_id': 'item1', 'title': 'Updated text'},
    {'item_id': 'item2', 'required': True}
]
google_forms_batch_update_questions(form_id, updates)

# Delete multiple questions
google_forms_batch_delete_questions(form_id, ['item1', 'item2', 'item3'])

# Reorder all questions
new_order = ['item3', 'item1', 'item2', 'item4']
google_forms_reorder_questions(form_id, new_order)
```

### **Bulk Response Management**

```python
# Delete specific responses
google_forms_batch_delete_responses(form_id, ['resp1', 'resp2', 'resp3'])

# Export from multiple forms
form_ids = ['form1', 'form2', 'form3']
all_data = google_forms_export_all_responses(form_ids, format='json')

# Analyze multiple forms
analysis = google_forms_analyze_responses_bulk(form_ids)
print(f"Total responses: {analysis['total_responses']}")
```

### **Batch Settings**

```python
# Update settings for multiple forms
form_ids = ['form1', 'form2', 'form3']
settings = {'collect_email': True}
google_forms_batch_update_settings(form_ids, settings)

# Open/close multiple forms
google_forms_batch_open_close(form_ids, accepting=False)
```

---

## 🤖 AI-POWERED FEATURES

### **Generate Form from Description**

```python
form = google_forms_ai_generate_from_prompt(
    prompt="Create a customer satisfaction survey for a restaurant with 5 questions",
    form_type='survey',
    ai_model='gpt-4'
)
print(f"AI created: {form['form']['responder_uri']}")
```

### **Auto-Generate Survey**

```python
survey = google_forms_ai_generate_survey(
    topic="Employee Wellness",
    audience="Remote workers",
    question_count=10,
    ai_model='gpt-4'
)
```

### **Auto-Generate Quiz**

```python
quiz = google_forms_ai_generate_quiz(
    topic="JavaScript Basics",
    difficulty="intermediate",
    question_count=15,
    ai_model='gpt-4'
)
```

### **Generate Event Registration**

```python
form = google_forms_ai_generate_registration(
    event_details="Tech Conference 2025, 500 attendees, catered lunch",
    ai_model='gpt-4'
)
```

### **Optimize Questions**

```python
suggestions = google_forms_ai_optimize_questions(form_id, ai_model='gpt-4')
print(f"Got {len(suggestions['suggestions'])} improvement suggestions")
```

### **Suggest Additional Questions**

```python
suggestions = google_forms_ai_suggest_questions(
    form_id,
    context="This is a product feedback form for a SaaS app",
    ai_model='gpt-4'
)
```

### **Translate Form**

```python
translated = google_forms_ai_translate_form(form_id, 'Spanish', ai_model='gpt-4')
```

### **Multi-Language Forms**

```python
forms = google_forms_ai_generate_multilingual(
    prompt="Customer satisfaction survey",
    languages=['English', 'Spanish', 'French', 'German'],
    ai_model='gpt-4'
)
```

### **Analyze Responses**

```python
# Summary
analysis = google_forms_ai_analyze_responses(form_id, 'summary', ai_model='gpt-4')

# Sentiment
sentiment = google_forms_ai_sentiment_analysis(form_id, ai_model='gpt-4')

# Insights
insights = google_forms_ai_extract_insights(form_id, ai_model='gpt-4')

# Generate report
report = google_forms_ai_generate_report(form_id, 'summary', ai_model='gpt-4')
```

### **Categorize Responses**

```python
categorized = google_forms_ai_categorize_responses(
    form_id,
    categories=['Positive', 'Negative', 'Neutral', 'Question'],
    ai_model='gpt-4'
)
```

### **Detect Spam**

```python
spam = google_forms_ai_detect_spam(form_id, ai_model='gpt-4')
print(f"Found {spam['count']} spam responses")
```

### **Flag Priority**

```python
priority = google_forms_ai_flag_priority(
    form_id,
    criteria="urgent, complaint, or mentions 'bug'",
    ai_model='gpt-4'
)
print(f"Flagged {priority['count']} priority responses")
```

---

## 🔧 WORKAROUNDS

### **Submit Response (HTTP POST)**

```python
# Step 1: Extract entry IDs (do once)
entry_data = google_forms_extract_entry_ids(form_id)
print(entry_data['entries'])
# Output: {'entry.123456': 'Name', 'entry.789012': 'Email', ...}

# Step 2: Submit response
response = google_forms_submit_response_http(
    form_id,
    responses_dict={
        'entry.123456': 'John Doe',
        'entry.789012': 'john@example.com',
        'entry.345678': 'Very Satisfied'
    }
)
print(f"Submitted: {response['submitted']}")
```

### **Bulk Submit**

```python
responses_list = [
    {'entry.123': 'Person 1', 'entry.456': 'email1@example.com'},
    {'entry.123': 'Person 2', 'entry.456': 'email2@example.com'},
    {'entry.123': 'Person 3', 'entry.456': 'email3@example.com'}
]

result = google_forms_bulk_submit_responses(form_id, responses_list)
print(f"Submitted {result['submitted']}/{result['total']}")
```

### **Auto-Generate Test Responses**

```python
# Generate 50 realistic test responses
result = google_forms_auto_test(
    form_id,
    count=50,
    realistic=True,  # Uses AI for realistic answers
    ai_model='gpt-4'
)
print(f"Generated {result['submitted']} test responses")
```

---

## 📊 Common Patterns

### **Pattern 1: Complete Form Workflow**

```python
# 1. Create form
form = google_forms_create_form("Customer Survey 2025")
form_id = form['form_id']

# 2. Add questions
google_forms_add_text_question(form_id, "Name", required=True, index=0)
google_forms_add_multiple_choice(form_id, "Satisfaction?", 
    ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"], required=True, index=1)
google_forms_add_text_question(form_id, "Comments", paragraph=True, index=2)

# 3. Configure settings
google_forms_set_settings(form_id, {'collect_email': True})

# 4. Share link
print(f"Share this: {form['responder_uri']}")

# 5. Wait for responses...

# 6. Analyze responses
responses = google_forms_get_responses(form_id)
print(f"Got {responses['count']} responses")

# 7. AI analysis
analysis = google_forms_ai_analyze_responses(form_id, 'insights')
print(analysis['analysis'])
```

### **Pattern 2: Multi-Event Registration**

```python
events = ["NYC Conference", "LA Summit", "SF Meetup", "Austin Workshop"]

for event in events:
    form = google_forms_create_form(f"{event} - Registration")
    form_id = form['form_id']
    
    questions = [
        {'type': 'text', 'text': 'Full Name', 'required': True},
        {'type': 'text', 'text': 'Email', 'required': True},
        {'type': 'text', 'text': 'Company'},
        {'type': 'multiple_choice', 'text': 'Attendance', 
         'options': ['In-Person', 'Virtual'], 'required': True},
        {'type': 'checkbox', 'text': 'Dietary Restrictions', 
         'options': ['Vegetarian', 'Vegan', 'Gluten-Free', 'None']},
    ]
    
    google_forms_batch_add_questions(form_id, questions)
    print(f"✅ Created: {event}")
```

### **Pattern 3: Survey + Analysis Pipeline**

```python
# Generate survey
survey = google_forms_ai_generate_survey(
    topic="Product Feedback",
    audience="Beta testers",
    question_count=8
)

form_id = survey['form']['form_id']

# Wait for responses (or use webhook)
# ...

# Analyze
sentiment = google_forms_ai_sentiment_analysis(form_id)
spam = google_forms_ai_detect_spam(form_id)
priority = google_forms_ai_flag_priority(form_id, "urgent or bug")
report = google_forms_ai_generate_report(form_id, 'summary')

# Export
csv_data = google_forms_export_responses_csv(form_id)
with open('responses.csv', 'w') as f:
    f.write(csv_data['data'])
```

---

## ⚡ Performance Tips

### **Use Bulk Operations**
```python
# ❌ Slow - 10 API calls
for question in questions:
    google_forms_add_text_question(form_id, question['text'])

# ✅ Fast - 1 API call
google_forms_batch_add_questions(form_id, questions)
```

### **Cache Form Structure**
```python
# Get once, use many times
form = google_forms_get_form(form_id)
questions = form['items']  # Reuse this
```

### **Use Webhooks Instead of Polling**
```python
# ❌ Don't poll repeatedly
while True:
    responses = google_forms_get_responses(form_id)
    time.sleep(60)

# ✅ Use webhook
google_forms_create_watch(form_id, "https://your-server.com/webhook", 'RESPONSES')
```

---

## 🚨 Quota Limits

- **Read operations:** 600/minute
- **Write operations:** 100/minute
- **Watches:** Max 100 per form
- **Watch duration:** 7 days (must renew)

---

## 📚 All 80 Functions

### Form Management (6)
1. `google_forms_create_form`
2. `google_forms_get_form`
3. `google_forms_delete_form`
4. `google_forms_clone_form`
5. `google_forms_update_info`
6. `google_forms_set_settings`

### Questions (17)
7-23. Add/update/delete/move questions of all types

### Sections (4)
24-27. Add sections, descriptions, images, videos

### Responses (5)
28-32. Get/delete responses, statistics

### Quiz (4)
33-36. Create quiz, graded questions, grading

### Advanced (6)
37-42. Validation, shuffle, other options, etc.

### Export (4)
43-46. CSV, JSON, statistics, Sheets

### Webhooks (4)
47-50. Create/delete/list/renew watches

### Bulk (12)
51-62. Batch operations for forms/questions/responses

### AI (17)
63-79. AI generation, analysis, optimization

### Workarounds (9)
80-88. HTTP submission, testing, export

---

**Total: 80+ Functions | File: `google_workspace/google_forms.py`**
