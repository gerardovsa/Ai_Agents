# Markdown Rendering Fix - Code Block Hash Symbol Issue

## Problem Description

When displaying AI responses containing Markdown syntax (especially `#` headers and triple backticks) within code blocks, the renderer prematurely terminates the code block, causing formatting corruption.

## Root Cause

```markdown
# This hash is interpreted as a header even inside code blocks
```

The parser sees `#` and triple backticks (` ``` `) as Markdown syntax, not literal text.

## Solutions

### Solution 1: Use Indented Code Blocks (4 spaces)

Instead of triple backticks, indent all code with 4 spaces:

    # QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING
    
    You are a QA Testing AI tasked with testing quote calculators.
    
    ## YOUR MISSION
    
    Test ALL available quote calculators.

**Pros:** Simpler, no backtick conflicts  
**Cons:** Less readable in raw Markdown

### Solution 2: Use HTML Entities for Special Characters

Replace problematic characters with HTML entities:

```markdown
&num; QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with testing quote calculators.

&num;&num; YOUR MISSION
```

**Pros:** Renders correctly  
**Cons:** Less readable in source

### Solution 3: Use HTML `<pre><code>` Tags

Wrap content in HTML tags instead of Markdown:

<pre><code># QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with testing quote calculators.

## YOUR MISSION

Test ALL available quote calculators.
</code></pre>

**Pros:** Most reliable, handles all special characters  
**Cons:** Verbose

### Solution 4: Escape with Backslashes

Use backslashes to escape Markdown syntax:

```markdown
\# QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with testing quote calculators.

\## YOUR MISSION

Test ALL available quote calculators.
```

**Pros:** Clean source, widely supported  
**Cons:** Requires escaping every special character

### Solution 5: Use Different Fence Characters

Use tildes (`~~~`) instead of backticks for code fences:

~~~markdown
# QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with testing quote calculators.

## YOUR MISSION

```python
# This code block inside works fine
print("Hello")
```
~~~

**Pros:** Allows nested backtick code blocks  
**Cons:** Not all renderers support tildes

## Recommended Solution for AI Chat Bubbles

For your AI_AGENT project chat bubbles, use **Solution 3 (HTML tags)** or **Solution 5 (tildes)**:

### Using HTML (Most Reliable):

```html
<div class="ai-response">
  <pre><code># QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with comprehensively testing InHouse Print's quote calculator system.

## YOUR MISSION

Test ALL available quote calculators to verify functionality, accuracy, and robustness.

## TESTING WORKFLOW

### Phase 1: Discovery (10 minutes)
1. Find all available quote calculators in the system
2. For each calculator:
   - Get its name and description
   - Retrieve the complete parameter schema
   - Document required vs optional parameters
   - Note any special requirements (e.g., "pages must be divisible by 4")

### Phase 2: Standard Testing (20 minutes)
For each calculator found:
1. Create a realistic test quote with standard parameters:
   - Use common quantities (250, 500, 1000)
   - Use standard sizes (A4, A5, 90x55mm for cards)
   - Use typical materials (300gsm, Satin finish, etc.)
2. Execute the calculator
3. Record the result:
   - If successful: Document price, breakdown, specifications
   - If failed: Document exact error message and parameters used

### Phase 3: Edge Case Testing (15 minutes)
For calculators that passed Phase 2, test:
1. **Minimum Values:**
   - Smallest quantity
   - Minimum size/pages
   - Lightest materials

2. **Maximum Values:**
   - Largest quantity
   - Maximum size/pages
   - Heaviest materials

3. **Unusual Combinations:**
   - Single-sided with premium finishes
   - Custom sizes
   - Mixed specifications

### Phase 4: Error Recovery (10 minutes)
For any calculator that failed:
1. Try alternative parameter values
2. Test if parameters need to be strings vs integers
3. Try simpler configurations
4. Document if the calculator can be made to work

## DELIVERABLES

Create a comprehensive report with:

### 1. Executive Summary
- Total calculators found
- Success rate (X/Y working)
- Critical issues discovered
- Overall system health assessment

### 2. Calculator Details (one section per calculator)

```
Calculator Name: [name]
Status: ✅ PASS / ❌ FAIL
Product Type: [e.g., Business Cards, Flyers]

Standard Test:
- Parameters: [list all parameters used]
- Result: [price inc GST or error message]
- Breakdown: [cost breakdown if available]

Edge Cases Tested:
- Minimum: [result]
- Maximum: [result]
- Unusual: [result]

Notes: [any observations]
```

### 3. Issues Log
- List all errors encountered
- Categorize by severity (Critical/High/Medium/Low)
- Suggest fixes where possible

### 4. Recommendations
- Which calculators are production-ready
- Which need urgent fixes
- Suggested improvements
</code></pre>
</div>
```

### Using Tildes (Cleaner Source):

~~~markdown
# QUOTE CALCULATOR SYSTEM - QUALITY ASSURANCE TESTING

You are a QA Testing AI tasked with comprehensively testing InHouse Print's quote calculator system.

## YOUR MISSION

Test ALL available quote calculators to verify functionality, accuracy, and robustness.

```python
# Code blocks inside work fine with this approach
def test_calculator(name, params):
    print(f"Testing {name}")
```

## TESTING WORKFLOW

### Phase 1: Discovery (10 minutes)
1. Find all available quote calculators in the system
~~~

## Implementation for AI_AGENT Project

### Check Both Message Bubble Components:

1. **AI Agent Prime Message Bubble** (`components/AIAgentBubble.jsx` or similar)
2. **AI Chat Prime Message Bubble** (`components/AIChatBubble.jsx` or similar)

### Update the Markdown Renderer:

```javascript
// Example fix for React component
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

function MessageBubble({ content }) {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
```

### Or Use Plain HTML Rendering:

```javascript
function MessageBubble({ content }) {
  // Escape and wrap in pre/code tags
  const escaped = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  return (
    <pre className="ai-response">
      <code>{escaped}</code>
    </pre>
  );
}
```

## Quick Fix for Existing Content

Replace problematic sections in your AI responses:

**Before:**
~~~markdown
```markdown
# HEADING
## SUBHEADING
```
~~~

**After:**
~~~markdown
~~~markdown
# HEADING
## SUBHEADING
~~~
~~~

Or use HTML:

```html
<pre><code># HEADING
## SUBHEADING
</code></pre>
```

## Testing

Create test cases with:
- Hash symbols at various positions
- Nested code blocks
- Mixed Markdown syntax
- Special characters (`, *, _, #, etc.)

---

**Bottom Line:** For AI chat bubbles displaying Markdown-heavy content, use `<pre><code>` HTML tags or tilde fences (`~~~`) to prevent rendering issues.
