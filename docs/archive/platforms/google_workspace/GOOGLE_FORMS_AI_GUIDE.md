# 🤖 Google Forms - AI Agent Usage Guide

## 🎯 Quick Decision Tree

**"What should I use?"**

```
User wants to create a form?
│
├─ User describes it in natural language ("Make a survey about...")
│  └─ ✅ USE: google_forms_ai_generate_form
│
├─ User provides specific questions/structure
│  └─ ✅ USE: google_forms_create_complete_form
│
└─ User wants multiple similar forms (events, locations)
   └─ ✅ USE: google_forms_bulk_create_multiple
```

---

## ⭐ Preferred Methods (Use These First)

### 1. **google_forms_create_complete_form** - Most Efficient

**When to use:**
- User provides form title and questions
- You know exactly what questions to ask
- Creating a single form with multiple questions

**Why it's best:**
- **ONE call** instead of 5+ calls
- Automatic shareability (no extra steps)
- Returns complete form with all details

**Example Usage:**
```json
{
  "tool": "google_forms_create_complete_form",
  "parameters": {
    "title": "Customer Feedback Survey",
    "description": "Help us improve our service",
    "questions": [
      {
        "type": "text",
        "text": "What is your name?",
        "required": true
      },
      {
        "type": "multiple_choice",
        "text": "How satisfied are you with our service?",
        "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
        "required": true
      },
      {
        "type": "linear_scale",
        "text": "How likely are you to recommend us?",
        "low_value": 1,
        "high_value": 10,
        "low_label": "Not Likely",
        "high_label": "Very Likely",
        "required": true
      },
      {
        "type": "paragraph",
        "text": "Any additional comments?",
        "required": false
      }
    ],
    "shareable": true,
    "collect_email": true
  }
}
```

**Returns:**
```json
{
  "form_id": "abc123...",
  "responder_uri": "https://docs.google.com/forms/d/e/abc123.../viewform",
  "edit_uri": "https://docs.google.com/forms/d/abc123.../edit",
  "questions_added": 4,
  "shareable": true,
  "title": "Customer Feedback Survey"
}
```

---

### 2. **google_forms_ai_generate_form** - AI-Powered Creation

**When to use:**
- User describes what they want in natural language
- You're not sure what specific questions to ask
- User wants you to "make something appropriate"

**Why it's best:**
- AI determines optimal questions automatically
- Handles complex requirements intelligently
- Less back-and-forth with user

**Example Usage:**
```json
{
  "tool": "google_forms_ai_generate_form",
  "parameters": {
    "prompt": "Create a restaurant feedback survey. Include questions about food quality, service speed, cleanliness, atmosphere, value for money, and likelihood to return. Use a mix of ratings, multiple choice, and open-ended questions.",
    "form_type": "feedback",
    "shareable": true,
    "ai_model": "gpt-4"
  }
}
```

**Returns:**
```json
{
  "form_id": "xyz789...",
  "responder_uri": "https://docs.google.com/forms/d/e/xyz789.../viewform",
  "title": "Restaurant Feedback Survey",
  "questions_count": 8,
  "ai_generated": true,
  "shareable": true
}
```

**⚠️ Requirements:**
- Needs `OPENAI_API_KEY` environment variable
- Uses OpenAI API (costs apply)

---

### 3. **google_forms_bulk_create_multiple** - Batch Creation

**When to use:**
- Creating 2+ forms at once
- Similar forms for different purposes (locations, events, departments)
- Scaling operations efficiently

**Why it's best:**
- Creates all forms in one operation
- Consistent structure across all forms
- Much faster than creating one-by-one

**Example Usage:**
```json
{
  "tool": "google_forms_bulk_create_multiple",
  "parameters": {
    "forms_configs": [
      {
        "title": "Event Registration - New York",
        "description": "Register for our NYC conference",
        "questions": [
          {"type": "text", "text": "Full Name", "required": true},
          {"type": "text", "text": "Email Address", "required": true},
          {"type": "multiple_choice", "text": "Attendance Type", "options": ["In-Person", "Virtual"], "required": true},
          {"type": "checkbox", "text": "Sessions of Interest", "options": ["Keynote", "Workshop A", "Workshop B", "Networking"], "required": false}
        ],
        "collect_email": true
      },
      {
        "title": "Event Registration - Los Angeles",
        "description": "Register for our LA summit",
        "questions": [
          {"type": "text", "text": "Full Name", "required": true},
          {"type": "text", "text": "Email Address", "required": true},
          {"type": "multiple_choice", "text": "Attendance Type", "options": ["In-Person", "Virtual"], "required": true}
        ],
        "collect_email": true
      },
      {
        "title": "Event Registration - Chicago",
        "description": "Register for our Chicago meetup",
        "questions": [
          {"type": "text", "text": "Full Name", "required": true},
          {"type": "text", "text": "Email Address", "required": true}
        ],
        "collect_email": true
      }
    ],
    "shareable": true
  }
}
```

**Returns:**
```json
{
  "forms_created": 3,
  "forms": [
    {"form_id": "...", "title": "Event Registration - New York", "responder_uri": "..."},
    {"form_id": "...", "title": "Event Registration - Los Angeles", "responder_uri": "..."},
    {"form_id": "...", "title": "Event Registration - Chicago", "responder_uri": "..."}
  ]
}
```

---

## 🚫 Anti-Patterns (Don't Do This)

### ❌ BAD: Creating form then adding questions one-by-one

```json
// DON'T DO THIS (5 separate tool calls):
1. google_forms_create_form(title="Survey")
2. google_forms_add_text_question(form_id, "Name")
3. google_forms_add_multiple_choice(form_id, "Rating", options)
4. google_forms_add_paragraph(form_id, "Comments")
5. google_forms_update_settings(form_id, collect_email=true)
```

### ✅ GOOD: Create complete form in one call

```json
// DO THIS INSTEAD (1 tool call):
google_forms_create_complete_form(
  title="Survey",
  questions=[
    {"type": "text", "text": "Name"},
    {"type": "multiple_choice", "text": "Rating", "options": [...]},
    {"type": "paragraph", "text": "Comments"}
  ],
  collect_email=true
)
```

**Result:** 80% fewer tool calls, faster execution, simpler code

---

## 📊 Common Workflows

### Workflow 1: Simple Survey

**User Request:** "Create a customer satisfaction survey"

**Best Approach:**
```json
{
  "tool": "google_forms_ai_generate_form",
  "parameters": {
    "prompt": "Create a customer satisfaction survey with questions about product quality, customer service, delivery experience, and overall satisfaction. Include rating scales and one open-ended question for suggestions.",
    "form_type": "survey"
  }
}
```

**Why:** AI generates appropriate questions automatically

---

### Workflow 2: Event Registration (Multiple Locations)

**User Request:** "Create event registration forms for our conferences in 5 cities"

**Best Approach:**
```json
{
  "tool": "google_forms_bulk_create_multiple",
  "parameters": {
    "forms_configs": [
      {"title": "Conference - NYC", "questions": [...]},
      {"title": "Conference - LA", "questions": [...]},
      {"title": "Conference - Chicago", "questions": [...]},
      {"title": "Conference - Boston", "questions": [...]},
      {"title": "Conference - Seattle", "questions": [...]}
    ]
  }
}
```

**Why:** Creates all 5 forms in one operation

---

### Workflow 3: Analyze Existing Responses

**User Request:** "What do people think about our product based on the feedback form?"

**Best Approach:**
```json
// Step 1: Get form ID (if needed)
{
  "tool": "google_forms_search", // or user provides ID
}

// Step 2: Analyze with AI
{
  "tool": "google_forms_ai_analyze_responses",
  "parameters": {
    "form_id": "abc123...",
    "analysis_type": "sentiment"
  }
}
```

**Why:** AI provides intelligent analysis of responses

---

### Workflow 4: Export and Process Data

**User Request:** "Export responses from my survey as CSV"

**Best Approach:**
```json
{
  "tool": "google_forms_export_responses_csv",
  "parameters": {
    "form_id": "abc123..."
  }
}
```

**Returns:** CSV data ready for processing

---

## 🎓 Question Types Reference

### Text Question
```json
{
  "type": "text",
  "text": "What is your name?",
  "required": true
}
```

### Paragraph (Long Text)
```json
{
  "type": "paragraph",
  "text": "Please describe your experience",
  "required": false
}
```

### Multiple Choice (Single Selection)
```json
{
  "type": "multiple_choice",
  "text": "How did you hear about us?",
  "options": ["Google Search", "Social Media", "Friend", "Advertisement", "Other"],
  "required": true
}
```

### Checkbox (Multiple Selection)
```json
{
  "type": "checkbox",
  "text": "Which features do you use? (Select all that apply)",
  "options": ["Feature A", "Feature B", "Feature C", "Feature D"],
  "required": false
}
```

### Dropdown
```json
{
  "type": "dropdown",
  "text": "Select your country",
  "options": ["United States", "Canada", "United Kingdom", "Australia", "Other"],
  "required": true
}
```

### Linear Scale (Rating)
```json
{
  "type": "linear_scale",
  "text": "How likely are you to recommend us?",
  "low_value": 1,
  "high_value": 10,
  "low_label": "Not at all likely",
  "high_label": "Extremely likely",
  "required": true
}
```

### Date
```json
{
  "type": "date",
  "text": "What is your birth date?",
  "required": false
}
```

### Time
```json
{
  "type": "time",
  "text": "What time works best for you?",
  "required": false
}
```

---

## 🔧 Advanced Features

### Conditional Logic (Show/Hide Questions)
```json
// Not yet supported in API
// Use google_forms_workaround_add_section for manual grouping
```

### File Upload Questions
```json
{
  "type": "file_upload",
  "text": "Please upload your resume",
  "required": true
}
```

### Section Headers
```json
{
  "type": "section",
  "text": "Contact Information",
  "description": "Please provide your contact details"
}
```

---

## 📈 Performance Tips

### 1. Always Use Smart Bundled Tools
- ✅ `google_forms_create_complete_form` instead of separate calls
- ✅ `google_forms_batch_add_questions` instead of individual additions
- ✅ `google_forms_bulk_create_multiple` for multiple forms

### 2. Forms Are Shareable by Default
- No need to call separate permission APIs
- `shareable=true` is the default parameter
- Returns both `responder_uri` (shareable link) and `edit_uri`

### 3. Use AI Generation for Complex Forms
- When user describes requirements in natural language
- When you're not sure what questions to ask
- AI determines optimal question types and options

### 4. Batch Operations for Multiple Items
- Add multiple questions at once
- Create multiple forms at once
- Export all responses at once

---

## ⚠️ Error Handling

### Common Errors and Solutions

**Error: "Parameter 'questions' must be a non-empty array"**
- **Cause:** Empty questions list passed
- **Solution:** Ensure at least one question in the array

**Error: "OPENAI_API_KEY not found"**
- **Cause:** AI-powered tools require OpenAI API key
- **Solution:** Set environment variable or use non-AI alternative

**Error: "Form not found"**
- **Cause:** Invalid form_id or user lacks permission
- **Solution:** Verify form_id and check permissions

**Error: "Question type not supported"**
- **Cause:** Invalid question type in questions array
- **Solution:** Use valid types: text, paragraph, multiple_choice, checkbox, dropdown, linear_scale, date, time, file_upload

---

## 🎯 Success Criteria

**You've used the tools correctly if:**
- ✅ You create complete forms in 1-2 tool calls (not 5+)
- ✅ Forms are automatically shareable
- ✅ You use AI generation when user describes needs naturally
- ✅ You use bulk operations for multiple items
- ✅ Users receive shareable links immediately

**You should reconsider if:**
- ❌ Making 5+ tool calls to create one form
- ❌ Manually setting permissions after creation
- ❌ Creating forms one-by-one when bulk is possible
- ❌ Not using AI generation for complex requirements

---

## 📝 Complete Example: Restaurant Feedback System

**User Request:** "Create a feedback system for my restaurant chain with 3 locations. I want to know about food quality, service, cleanliness, and get suggestions."

**Optimal Solution:**

```json
{
  "tool": "google_forms_bulk_create_multiple",
  "parameters": {
    "forms_configs": [
      {
        "title": "Customer Feedback - Downtown Location",
        "description": "Help us improve your dining experience at our Downtown restaurant",
        "questions": [
          {
            "type": "text",
            "text": "Your Name (Optional)",
            "required": false
          },
          {
            "type": "linear_scale",
            "text": "How would you rate the quality of your food?",
            "low_value": 1,
            "high_value": 5,
            "low_label": "Poor",
            "high_label": "Excellent",
            "required": true
          },
          {
            "type": "linear_scale",
            "text": "How would you rate our service?",
            "low_value": 1,
            "high_value": 5,
            "low_label": "Poor",
            "high_label": "Excellent",
            "required": true
          },
          {
            "type": "linear_scale",
            "text": "How would you rate the cleanliness?",
            "low_value": 1,
            "high_value": 5,
            "low_label": "Poor",
            "high_label": "Excellent",
            "required": true
          },
          {
            "type": "multiple_choice",
            "text": "How likely are you to recommend us to a friend?",
            "options": ["Very Likely", "Likely", "Neutral", "Unlikely", "Very Unlikely"],
            "required": true
          },
          {
            "type": "paragraph",
            "text": "Do you have any suggestions for improvement?",
            "required": false
          }
        ],
        "collect_email": false
      },
      {
        "title": "Customer Feedback - Westside Location",
        "description": "Help us improve your dining experience at our Westside restaurant",
        "questions": [
          // Same questions as above
        ]
      },
      {
        "title": "Customer Feedback - Eastside Location",
        "description": "Help us improve your dining experience at our Eastside restaurant",
        "questions": [
          // Same questions as above
        ]
      }
    ],
    "shareable": true
  }
}
```

**Result:**
- ✅ 3 forms created in ONE operation
- ✅ All forms shareable by default
- ✅ Consistent question structure
- ✅ User gets 3 shareable links immediately
- ✅ Total execution time: < 5 seconds

---

## 🚀 Next Steps

1. **Review this guide** before using Google Forms tools
2. **Always prefer smart bundled tools** over individual operations
3. **Use AI generation** when requirements are described naturally
4. **Test with simple forms first** before complex workflows
5. **Check response count** before analyzing responses

---

**Questions?** Check GOOGLE_FORMS_IMPLEMENTATION_COMPLETE.md for technical details.

**Last Updated:** 2025-01-XX  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
