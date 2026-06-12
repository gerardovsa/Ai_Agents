# User Feedback & Reinforcement Learning System

**Date:** November 27, 2025  
**Purpose:** User-specific and organization-level learning with sentiment-based reinforcement

---

## 🎯 Overview - Three Levels of Learning

### **1. Individual User Learning (Default)**
- **Scope:** Personal preferences, workflows, patterns
- **Privacy:** `sharing_level = 'user'` (only visible to that user)
- **Example:** "John prefers to export emails to Google Docs, not Sheets"

### **2. Organization Learning (Opt-in)**
- **Scope:** Team best practices, approved workflows
- **Privacy:** `sharing_level = 'organization'` (visible to all org members)
- **Example:** "Marketing team's standard campaign workflow"

### **3. Global Patterns (Aggregate Analytics)**
- **Scope:** Platform-wide optimization (anonymized)
- **Privacy:** `sharing_level = 'global'` (no PII)
- **Example:** "Users with 100+ contacts prefer batch operations"

---

## 📊 Updated Database Schema

### **Key Changes:**

**NEW COLUMNS (Ownership):**
```sql
organization_id INTEGER,  -- User's organization (NULL = individual)
sharing_level VARCHAR(20) DEFAULT 'user',  -- 'user', 'organization', 'global'
created_by_user_id INTEGER NOT NULL,  -- Who created this learning
is_shared BOOLEAN DEFAULT FALSE,  -- Shared with team?
is_approved_pattern BOOLEAN DEFAULT FALSE,  -- Organization approved?
approved_by VARCHAR(100),  -- Who approved it
approved_at TIMESTAMP  -- When approved
```

**NEW COLUMNS (User Feedback):**
```sql
user_feedback_sentiment VARCHAR(20),  -- 'positive', 'negative', 'neutral', 'frustrated', 'satisfied'
user_feedback_explicit TEXT,  -- User's actual words: "That's perfect!"
user_feedback_timestamp TIMESTAMP,  -- When feedback given
feedback_detected_from VARCHAR(50),  -- 'explicit_command', 'sentiment_analysis', 'follow_up_question'
```

**NEW COLUMNS (Reinforcement Learning):**
```sql
reinforcement_score INTEGER,  -- -10 to +10 (avoid → repeat)
times_user_repeated_workflow INTEGER DEFAULT 0,  -- Positive reinforcement
times_user_avoided_workflow INTEGER DEFAULT 0,  -- Negative reinforcement
was_offered_to_remember BOOLEAN DEFAULT FALSE,  -- AI asked permission
user_accepted_offer BOOLEAN  -- User said yes/no
```

**NEW INDEXES:**
```sql
INDEX idx_organization_sharing (organization_id, sharing_level, is_approved_pattern)
INDEX idx_user_feedback (user_feedback_sentiment, reinforcement_score)
INDEX idx_approved_patterns (is_approved_pattern, sharing_level) WHERE is_approved_pattern = TRUE
```

---

## 🎤 Sentiment Detection System

### **Positive Sentiment Indicators:**

**Explicit Praise:**
- "Perfect!", "Exactly what I needed!", "Great!", "Thanks!"
- "This is helpful", "Love it", "That works perfectly"
- "Yes, that's it!", "Brilliant!", "Much better"

**Behavioral Signals:**
- User continues same workflow without modifications
- User repeats same request pattern 3+ times
- No follow-up questions or corrections
- User moves to next task immediately

**Reinforcement Score:** +5 to +10

---

### **Negative Sentiment Indicators:**

**Explicit Criticism:**
- "That's not what I wanted", "No, stop", "This is wrong"
- "Why did you do it that way?", "That's too slow", "Too complicated"
- "Not like that", "Redo this", "Change approach"

**Frustration Keywords:**
- "Ugh", "Seriously?", "Not again", "Come on"
- "For God's sake", "This is ridiculous", "Why is this so hard?"

**Behavioral Signals:**
- Immediate request to redo/change approach
- Multiple modifications to same task
- Follow-up questions showing confusion
- User abandons task mid-way
- User switches to different approach

**Reinforcement Score:** -5 to -10

---

### **Neutral/Unclear Signals:**

- Simple acknowledgment: "OK", "Sure", "Alright"
- Task continuation without feedback
- User moves on to unrelated task
- No emotional indicators

**Reinforcement Score:** 0

---

## 🧠 Feedback Detection Implementation

### **Method 1: Sentiment Analysis (Python)**

```python
import re
from typing import Dict, Optional

class SentimentAnalyzer:
    """Detect user sentiment from chat messages"""
    
    POSITIVE_KEYWORDS = {
        'perfect': 10, 'excellent': 10, 'brilliant': 10,
        'great': 8, 'good': 7, 'helpful': 7, 'love': 9,
        'thanks': 6, 'thank you': 7, 'exactly': 8,
        'yes that': 7, 'works': 6, 'nice': 6
    }
    
    NEGATIVE_KEYWORDS = {
        'wrong': -8, 'not what': -9, 'no stop': -10,
        'why did you': -7, 'too slow': -7, 'complicated': -6,
        'ugh': -8, 'seriously': -7, 'not again': -9,
        'ridiculous': -9, 'redo': -7, 'change': -5
    }
    
    FRUSTRATION_PATTERNS = [
        r'\bugh\b', r'\bseriously\??', r'\bnot again\b',
        r'\bwhy is this\b', r'\bcome on\b', r'\bfor .*sake\b'
    ]
    
    def analyze_sentiment(
        self, 
        user_message: str,
        previous_ai_action: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze sentiment from user's response to AI action
        
        Args:
            user_message: User's latest message
            previous_ai_action: What AI just did (tool execution summary)
        
        Returns:
            {
                'sentiment': 'positive'|'negative'|'neutral'|'frustrated',
                'reinforcement_score': -10 to +10,
                'confidence': 0.0 to 1.0,
                'detected_from': 'explicit_keywords'|'pattern_match'|'behavioral',
                'feedback_text': Original message (if explicit)
            }
        """
        message_lower = user_message.lower()
        
        # Check for frustration patterns first (strongest signal)
        for pattern in self.FRUSTRATION_PATTERNS:
            if re.search(pattern, message_lower):
                return {
                    'sentiment': 'frustrated',
                    'reinforcement_score': -10,
                    'confidence': 0.95,
                    'detected_from': 'pattern_match',
                    'feedback_text': user_message
                }
        
        # Score positive keywords
        positive_score = 0
        positive_matches = []
        for keyword, score in self.POSITIVE_KEYWORDS.items():
            if keyword in message_lower:
                positive_score += score
                positive_matches.append(keyword)
        
        # Score negative keywords
        negative_score = 0
        negative_matches = []
        for keyword, score in self.NEGATIVE_KEYWORDS.items():
            if keyword in message_lower:
                negative_score += score
                negative_matches.append(keyword)
        
        # Calculate net sentiment
        net_score = positive_score + negative_score  # negative_score is negative
        
        # Determine sentiment
        if net_score >= 10:
            sentiment = 'satisfied'
            reinforcement = 10
        elif net_score >= 5:
            sentiment = 'positive'
            reinforcement = 7
        elif net_score <= -10:
            sentiment = 'frustrated'
            reinforcement = -10
        elif net_score <= -5:
            sentiment = 'negative'
            reinforcement = -7
        else:
            sentiment = 'neutral'
            reinforcement = 0
        
        # Confidence based on number of matches
        total_matches = len(positive_matches) + len(negative_matches)
        confidence = min(0.3 + (total_matches * 0.2), 1.0)
        
        return {
            'sentiment': sentiment,
            'reinforcement_score': reinforcement,
            'confidence': confidence,
            'detected_from': 'explicit_keywords',
            'feedback_text': user_message if total_matches > 0 else None,
            'matched_keywords': {
                'positive': positive_matches,
                'negative': negative_matches
            }
        }
    
    def detect_behavioral_sentiment(
        self,
        workflow_context: Dict
    ) -> Dict[str, any]:
        """
        Detect sentiment from user behavior
        
        Behavioral signals:
        - Repeated same workflow → positive
        - Changed approach immediately → negative
        - Multiple corrections → frustrated
        """
        tool_sequence = workflow_context.get('tool_sequence', [])
        time_between_tools = workflow_context.get('time_between_tools', [])
        
        # User repeated same tool sequence
        if workflow_context.get('is_repeat', False):
            frequency = workflow_context.get('pattern_frequency', 0)
            if frequency >= 3:
                return {
                    'sentiment': 'satisfied',
                    'reinforcement_score': 8,
                    'confidence': 0.8,
                    'detected_from': 'behavioral_repeat'
                }
        
        # User changed approach quickly (< 30 seconds after completion)
        if len(tool_sequence) > 1 and time_between_tools:
            if time_between_tools[-1] < 30:  # seconds
                return {
                    'sentiment': 'negative',
                    'reinforcement_score': -6,
                    'confidence': 0.7,
                    'detected_from': 'behavioral_quick_change'
                }
        
        return {
            'sentiment': 'neutral',
            'reinforcement_score': 0,
            'confidence': 0.5,
            'detected_from': 'behavioral_unclear'
        }
```

---

### **Method 2: Follow-up Question Detection**

```python
def detect_confusion_from_followup(
    user_message: str,
    previous_ai_response: str
) -> Dict[str, any]:
    """
    Detect if user is confused based on follow-up questions
    
    Confusion indicators:
    - "What?", "Huh?", "I don't understand"
    - "Can you explain?", "What do you mean?"
    - Asking same question differently
    """
    confusion_patterns = [
        r'\bwhat\??$', r'\bhuh\??', r'\bsorry\?',
        r'\bdon\'t understand\b', r'\bexplain\b',
        r'\bwhat do you mean\b', r'\bcan you clarify\b'
    ]
    
    message_lower = user_message.lower()
    
    for pattern in confusion_patterns:
        if re.search(pattern, message_lower):
            return {
                'sentiment': 'confused',
                'reinforcement_score': -4,  # Mild negative (not user's fault)
                'confidence': 0.8,
                'detected_from': 'follow_up_question',
                'feedback_text': user_message
            }
    
    return None  # No confusion detected
```

---

## 💬 AI Feedback Prompts (When to Ask)

### **Scenario 1: Pattern Detected (3+ repetitions)**

**Condition:**
- User has executed same workflow 3+ times
- All executions successful (no errors)
- No negative sentiment detected

**AI Prompt:**
```
AI: "I notice you often [describe workflow pattern]. 

For example:
- [Date 1]: [Brief description]
- [Date 2]: [Brief description]  
- [Date 3]: [Brief description]

Would you like me to remember this as your preferred approach for [task type]? 
I can make it faster next time by [optimization suggestion]."

User: "Yes" → reinforcement_score = +10, is_approved_pattern = TRUE
User: "No" → reinforcement_score = 0, no further prompts for this pattern
```

**Example:**
```
AI: "I notice you often save Gmail threads to Synergy projects.

For example:
- Nov 20: Saved 'Customer Questions' thread to Project Dashboard
- Nov 23: Saved 'Feature Requests' thread to Product Planning
- Nov 25: Saved 'Bug Reports' thread to Dev Tracker

Would you like me to remember this as your preferred approach for email organization?
I can add a quick action: 'Save this email thread to Synergy' to make it one-click."

User: "Yes, that would be great!"
→ Log: reinforcement_score = +10, user_accepted_offer = TRUE
```

---

### **Scenario 2: Organization Sharing Offer (5+ successful uses)**

**Condition:**
- User has workflow with 5+ successful uses
- User is in organization (organization_id present)
- reinforcement_score >= +40 (avg +8 per use)

**AI Prompt:**
```
AI: "Your workflow for [task] has been working great! I've tracked [N] successful uses.

Your team might benefit from this approach. Would you like me to:
1. Share this as a team best practice (visible to your organization)
2. Keep it personal (only you see this)

If shared, I'll mark it as '[Your Name]'s Recommended Workflow' and suggest it 
to teammates working on similar tasks."

User: "Yes, share" → sharing_level = 'organization', is_shared = TRUE
User: "No, keep private" → sharing_level = 'user'
```

---

### **Scenario 3: Negative Feedback Recovery**

**Condition:**
- reinforcement_score <= -7 (strong negative)
- AI wants to learn what to avoid

**AI Prompt:**
```
AI: "I sense that didn't work well for you. I'm learning your preferences.

Would you like me to:
1. Try a different approach for [task type]
2. Remember to avoid [specific method] in the future

What would work better for you?"

User explains → Log detailed feedback, adjust future behavior
```

**Example:**
```
AI: "I sense that spreadsheet export was too slow. I'm learning your preferences.

Would you like me to:
1. Use smaller batch sizes (faster but more steps)
2. Export directly to Google Sheets instead of downloading first

What would work better for you?"

User: "Just do it directly in Sheets, don't download"
→ Log: user_feedback_explicit = "Prefer direct Sheets export over download"
→ reinforcement_score = -8 for download method
→ Future workflows: Skip download step
```

---

## 🏢 Organization Learning System

### **How Organizations Benefit:**

**1. Shared Best Practices**
- Team member develops efficient workflow
- After 5+ successes, AI offers to share with team
- Organization approves (optional admin review)
- All team members benefit from optimization

**2. Onboarding Acceleration**
- New team member joins
- AI: "Your team has 12 approved workflows for common tasks"
- New member learns org standards faster
- Consistency across team

**3. Workflow Evolution**
- Multiple team members use similar workflows
- AI detects patterns: "5 team members do X this way"
- Suggests org-wide standard
- Continuous improvement

---

### **Privacy Controls:**

```sql
-- User 42 creates personal workflow
INSERT INTO ai_tool_intelligence_log (
    user_id = 42,
    organization_id = 10,  -- Works for Acme Corp
    sharing_level = 'user',  -- DEFAULT: Private
    created_by_user_id = 42,
    is_shared = FALSE,
    workflow_sequence = ['gmail_list', 'synergy_create'],
    reinforcement_score = 8
);

-- After 5 uses, user agrees to share
UPDATE ai_tool_intelligence_log SET
    sharing_level = 'organization',
    is_shared = TRUE,
    is_approved_pattern = TRUE,  -- User approved
    approved_by = 'user_42',
    approved_at = NOW();

-- Now visible to all Acme Corp members (organization_id = 10)
-- But NOT visible to users in other organizations
```

---

## 📊 Query Patterns

### **Query 1: Get User's Personal Patterns**

```sql
-- What has User 42 learned that works well?
SELECT 
    workflow_sequence,
    reinforcement_score,
    times_user_repeated_workflow,
    user_feedback_sentiment,
    ai_observation
FROM ai_tool_intelligence_log
WHERE user_id = 42
  AND sharing_level = 'user'
  AND reinforcement_score >= 5
ORDER BY reinforcement_score DESC, times_user_repeated_workflow DESC
LIMIT 10;
```

---

### **Query 2: Get Organization Best Practices**

```sql
-- What workflows are approved for Acme Corp (org 10)?
SELECT 
    created_by_user_id,
    workflow_sequence,
    AVG(reinforcement_score) as avg_score,
    COUNT(*) as times_used,
    ai_observation,
    approved_by,
    approved_at
FROM ai_tool_intelligence_log
WHERE organization_id = 10
  AND sharing_level = 'organization'
  AND is_approved_pattern = TRUE
GROUP BY created_by_user_id, workflow_sequence, ai_observation, approved_by, approved_at
ORDER BY avg_score DESC, times_used DESC;
```

---

### **Query 3: Detect Negative Patterns to Avoid**

```sql
-- What should User 42 avoid doing?
SELECT 
    workflow_sequence,
    reinforcement_score,
    times_user_avoided_workflow,
    user_feedback_sentiment,
    user_feedback_explicit
FROM ai_tool_intelligence_log
WHERE user_id = 42
  AND reinforcement_score <= -5
ORDER BY reinforcement_score ASC
LIMIT 10;
```

---

### **Query 4: Organization-Wide Sentiment Analysis**

```sql
-- How is Acme Corp team feeling about tool usage?
SELECT 
    tool_category,
    user_feedback_sentiment,
    COUNT(*) as count,
    AVG(reinforcement_score) as avg_score
FROM ai_tool_intelligence_log
WHERE organization_id = 10
  AND user_feedback_sentiment IS NOT NULL
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY tool_category, user_feedback_sentiment
ORDER BY tool_category, avg_score DESC;

-- Results might show:
-- email, satisfied, 45, +8.2  → Email tools working great
-- sheets, frustrated, 12, -6.5 → Sheets tools need improvement
```

---

## 🎯 Complete Use Case Example

### **Scenario: John's Email Organization Workflow**

**Week 1 - Discovery:**
```
Nov 20:
User (John): "Save this email thread to my project"
AI: Calls gmail_get_thread() → synergy_create_internal_doc()
User: "Perfect!"
→ Log: reinforcement_score = +8, sentiment = 'satisfied'

Nov 23:
User: "Save these emails to the project too"
AI: Same workflow
User: "Great, thanks"
→ Log: reinforcement_score = +7, pattern_frequency = 2

Nov 25:
User: "Add this email thread to Synergy"
AI: Same workflow (3rd time)
User: "Exactly what I needed"
→ Log: reinforcement_score = +9, pattern_frequency = 3
```

**Week 2 - AI Offers to Remember:**
```
Nov 27:
User: "Save this thread..."
AI: "I notice you often save email threads to Synergy projects. I've done this 
     successfully 3 times now. Would you like me to remember this as your 
     preferred email organization method?"
User: "Yes! Make it faster if you can"
→ Log: user_accepted_offer = TRUE, is_approved_pattern = TRUE
→ AI adds quick action: "Save to Synergy" button in email interface
```

**Week 3 - Organization Sharing:**
```
Dec 1 (5th successful use):
AI: "Your email-to-Synergy workflow has been working great (5 successful uses).
     
     Your teammates Sarah and Mike also work with email organization. Would you 
     like to share this workflow as a team best practice?"

John: "Yes, share with the team"
→ Log: sharing_level = 'organization', is_shared = TRUE
```

**Result:**
- John's personal workflow: 5 successful uses, reinforcement_score = +40
- Team benefit: Sarah and Mike get suggestion next time they organize emails
- Organization learning: Acme Corp now has documented best practice

---

## ✅ Implementation Checklist

### **Phase 1: Database Updates (Week 1)**
- [ ] Add organization_id, sharing_level columns
- [ ] Add user_feedback_* columns (sentiment, explicit, timestamp)
- [ ] Add reinforcement_score, times_repeated columns
- [ ] Add was_offered_to_remember, user_accepted_offer columns
- [ ] Create new indexes for feedback and sharing queries
- [ ] Migrate existing data (set sharing_level = 'user' by default)

### **Phase 2: Sentiment Analysis (Week 2)**
- [ ] Implement SentimentAnalyzer class
- [ ] Add keyword-based detection
- [ ] Add pattern-based frustration detection
- [ ] Add behavioral signal detection
- [ ] Test with sample messages (positive/negative/neutral)

### **Phase 3: AI Feedback System (Week 3)**
- [ ] Add feedback prompt generation logic
- [ ] Implement "Would you like me to remember?" prompt
- [ ] Implement organization sharing prompt
- [ ] Add negative feedback recovery prompts
- [ ] Update system prompt with feedback guidelines

### **Phase 4: Organization Features (Week 4)**
- [ ] Build organization best practices query
- [ ] Create admin approval workflow (optional)
- [ ] Add team member discovery of shared patterns
- [ ] Build analytics dashboard (org sentiment, top patterns)
- [ ] Privacy controls and opt-out options

---

**Last Updated:** November 27, 2025  
**Status:** Design Complete with User Feedback & Organization Learning  
**Next Step:** Database schema updates and sentiment analyzer implementation
