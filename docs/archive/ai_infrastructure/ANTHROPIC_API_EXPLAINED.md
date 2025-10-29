# Anthropic API Explained: Messages vs Vision

**Date**: October 23, 2025  
**Topic**: Understanding API differences and their impact on AI capabilities

---

## 🎯 Quick Answer

**There is NO separate "Vision API"!** 

Anthropic has **ONE unified Messages API** that handles:
- ✅ Text-only conversations
- ✅ Images (Vision)
- ✅ PDFs (Document analysis)
- ✅ Tool use (Function calling)
- ✅ Extended thinking (reasoning)
- ✅ Interleaved thinking (streaming thoughts)

**The "Vision API" is just the Messages API with image/document content blocks.**

---

## 📚 The One Messages API

### Endpoint
```
POST https://api.anthropic.com/v1/messages
```

### What It Can Do
1. **Text conversations** (basic chat)
2. **Image analysis** (Vision - JPEG, PNG, GIF, WebP)
3. **PDF analysis** (Document understanding)
4. **Tool use** (Function calling, database queries)
5. **Extended thinking** (Deep reasoning mode)
6. **Interleaved thinking** (Stream thoughts while processing)

**All in ONE API!**

---

## 🔧 How Content Blocks Work

The Messages API uses **content blocks** to handle different types of input:

### 1. Text-Only (Basic Chat)
```python
messages = [
    {
        "role": "user",
        "content": "What's 2+2?"  # Simple string
    }
]
```

### 2. Vision (Images)
```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": "iVBORw0KGgoAAAANS..."  # Base64 encoded
                }
            },
            {
                "type": "text",
                "text": "What's in this image?"
            }
        ]
    }
]
```

### 3. PDF Documents
```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "document",  # PDF type
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": "JVBERi0xLjQKJeLjz9..."  # Base64 encoded PDF
                }
            },
            {
                "type": "text",
                "text": "Extract the invoice total"
            }
        ]
    }
]
```

### 4. Mixed Content (Text + Image + Tools)
```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Analyze this invoice and update the database"
            },
            {
                "type": "document",
                "source": {...}  # Invoice PDF
            }
        ]
    }
]

# With tool definitions
tools = [
    {
        "name": "update_stock_price",
        "description": "Update stock pricing in database",
        "input_schema": {...}
    }
]
```

---

## 🧠 Extended Thinking (Deep Reasoning)

### What It Is
Extended thinking lets Claude **think deeply** before responding, similar to OpenAI's o1 model.

### How to Enable
**Option 1: Model Parameter** (Recommended)
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",  # Sonnet 4 with thinking
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # Max tokens for thinking
    },
    messages=[...]
)
```

**Option 2: System Prompt** (Alternative)
```python
system_prompts = [
    {
        "type": "text",
        "text": "You are a helpful assistant."
    },
    {
        "type": "text",
        "text": "Before responding, think step-by-step about the problem.",
        "cache_control": {"type": "ephemeral"}
    }
]
```

### What You Get
```python
# Response includes thinking blocks
{
    "type": "thinking",
    "thinking": "Let me analyze this step by step:\n1. The invoice shows...\n2. Comparing to database...\n3. Price increased by 5%..."
}
{
    "type": "text", 
    "text": "I've analyzed the invoice. The price increased by 5%."
}
```

### Impact on Vision/PDFs
✅ **WORKS PERFECTLY** - Extended thinking works with images and PDFs!

Example:
```python
# Analyze invoice with deep thinking
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "document", "source": {...}},  # Invoice PDF
                {"type": "text", "text": "Compare prices to last month"}
            ]
        }
    ]
)

# Response:
# 1. Thinking block: "Extracting prices... Last month was $145, this is $152... 4.8% increase..."
# 2. Text block: "Prices increased 4.8%. Satin 350gsm: $145→$152"
```

---

## 🔄 Interleaved Thinking (Streaming Thoughts)

### What It Is
**Interleaved thinking** streams Claude's thoughts **as they happen**, mixed with the actual response.

### How It Works
```python
# Enable streaming
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[...]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("💭 Thinking:", event.content_block.thinking)
        elif event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print("💬 Response:", event.delta.text)
```

### What You See (Real-time)
```
💭 Thinking: "Let me read the PDF... I see 5 line items..."
💭 Thinking: "Comparing to database: Satin 350gsm was $145..."
💭 Thinking: "Price changed from $145 to $152... that's +$7..."
💬 Response: "I've analyzed the invoice."
💬 Response: " The Satin 350gsm stock price increased"
💬 Response: " from $145 to $152 (+4.8%)."
```

### Impact on Vision/PDFs
✅ **WORKS PERFECTLY** - You can see Claude's thoughts while analyzing documents!

Example flow:
1. User uploads invoice PDF
2. Claude thinks: "Reading PDF... extracting line items..."
3. Claude thinks: "Found 5 products... checking database..."
4. Claude thinks: "Price comparison shows 2 increases..."
5. Claude responds: "Here's what changed: ..."

**This is AMAZING for debugging!** You see exactly how Claude interprets the document.

---

## 🛠️ Tool Use (Function Calling)

### What It Is
Tool use lets Claude **call functions** to interact with your systems (databases, APIs, etc.)

### How to Enable
```python
tools = [
    {
        "name": "query_database",
        "description": "Query the stock database",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "update_stock_price",
        "description": "Update stock pricing",
        "input_schema": {
            "type": "object",
            "properties": {
                "stock_id": {"type": "integer"},
                "new_price": {"type": "number"}
            },
            "required": ["stock_id", "new_price"]
        }
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=tools,  # Provide tool definitions
    messages=[...]
)
```

### Tool Use Flow
1. **User**: "Update Stock #44 to $152"
2. **Claude thinks**: "I need to call update_stock_price tool"
3. **Claude calls tool**:
   ```json
   {
       "type": "tool_use",
       "name": "update_stock_price",
       "input": {"stock_id": 44, "new_price": 152}
   }
   ```
4. **Your code executes**: Update database
5. **You respond with result**:
   ```json
   {
       "type": "tool_result",
       "tool_use_id": "...",
       "content": "Stock #44 updated: $145 → $152"
   }
   ```
6. **Claude continues**: "Done! Stock #44 price updated to $152."

### Impact on Vision/PDFs
✅ **WORKS PERFECTLY** - Combine document analysis with tool calls!

**Powerful workflow**:
```python
# 1. Upload invoice PDF
messages = [
    {
        "role": "user",
        "content": [
            {"type": "document", "source": {...}},  # Invoice
            {"type": "text", "text": "Extract prices and update database"}
        ]
    }
]

# 2. Claude analyzes PDF with extended thinking
# Thinking: "Reading invoice... found 5 items... extracting prices..."

# 3. Claude calls tools
# Tool call 1: query_database("SELECT * FROM stocks WHERE stock_id=44")
# Tool call 2: update_stock_price(44, 152)

# 4. Database updated automatically!
```

**This is what your Stock AI Chat does!** 🎉

---

## 🎨 Your Current Implementation

### In `unified_ai_client.py`:

```python
def _process_anthropic(self, session_id, prompt, files, sse_callback):
    """
    Handles ALL Anthropic API calls:
    - Text-only conversations
    - Image/PDF analysis (Vision)
    - Tool use (database queries)
    - Extended thinking
    - Interleaved thinking (streaming)
    """
    
    # Build content blocks
    content = []
    
    # Add files (images or PDFs)
    if files:
        for file_data in files:
            if file_data['media_type'] == 'application/pdf':
                content.append({
                    "type": "document",  # PDF
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": file_data['data']
                    }
                })
            else:
                content.append({
                    "type": "image",  # Image
                    "source": {
                        "type": "base64",
                        "media_type": file_data['media_type'],
                        "data": file_data['data']
                    }
                })
    
    # Add text prompt
    content.append({
        "type": "text",
        "text": prompt
    })
    
    # Create message with thinking + tools
    with self.anthropic_client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        thinking={
            "type": "enabled",
            "budget_tokens": 10000  # Extended thinking
        },
        tools=self.tool_agent.get_tools() if hasattr(self, 'tool_agent') else None,
        messages=[{
            "role": "user",
            "content": content  # Text + files + everything!
        }]
    ) as stream:
        for event in stream:
            # Handle thinking blocks (interleaved)
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    sse_callback("thinking", event.content_block.thinking)
            
            # Handle text responses
            elif event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    sse_callback("text", event.delta.text)
            
            # Handle tool calls
            elif event.type == "content_block_start":
                if event.content_block.type == "tool_use":
                    # Execute tool
                    result = self.tool_agent.execute_tool(...)
                    # Continue conversation with result
```

**This ONE method handles EVERYTHING!** 🚀

---

## 📊 Comparison Table

| Feature | Text-Only | + Vision (Images) | + PDFs | + Tools | + Thinking |
|---------|-----------|-------------------|--------|---------|------------|
| **API Endpoint** | Messages API | Messages API | Messages API | Messages API | Messages API |
| **Content Type** | String | Array of blocks | Array of blocks | Array of blocks | Array of blocks |
| **Model** | Any Claude | Sonnet 3.5+ | Sonnet 3.5+ | Any Claude | Sonnet 4+ |
| **Tool Use** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Extended Thinking** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Interleaved Thinking** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Max File Size** | N/A | 5MB per image | 32MB total | N/A | N/A |
| **Cost (Input)** | $3/1M tokens | $3/1M + image tokens | $3/1M + 1500-3000 tokens/page | $3/1M tokens | $3/1M tokens |
| **Cost (Output)** | $15/1M tokens | $15/1M tokens | $15/1M tokens | $15/1M tokens | $15/1M tokens |

---

## 🎯 Impact on Your System

### Current Stock AI Chat Flow

**Without Document:**
```
1. User: "What's the price of Satin 350gsm?"
2. Claude thinks: "Need to query database..."
3. Claude calls: query_database("SELECT * FROM stocks WHERE...")
4. Tool returns: {"stock_id": 44, "price": 145}
5. Claude responds: "Satin 350gsm costs $145/1000 sheets"
```

**With Document (Invoice PDF):**
```
1. User uploads invoice.pdf + "Extract pricing"
2. Claude thinks: "Reading PDF... found 5 line items..."
3. Claude thinks: "Extracting: Satin 350gsm = $152, Gloss 250gsm = $160..."
4. Claude calls: query_database("SELECT * FROM stocks WHERE stock_type='Satin'")
5. Tool returns: {"stock_id": 44, "price": 145}
6. Claude thinks: "Old: $145, New: $152, Increase: +4.8%"
7. Claude responds: "Invoice shows Satin 350gsm at $152 (was $145, +4.8% increase)"
8. Claude asks: "Should I update the database?"
9. User: "Yes"
10. Claude calls: update_stock_price(44, 152)
11. Tool executes: UPDATE stocks SET price=152 WHERE stock_id=44
12. Claude responds: "✅ Updated! Stock #44 now $152/1000"
```

**ALL using the SAME Messages API!** 🎉

---

## 💡 Key Takeaways

### 1. One API to Rule Them All
- ✅ Messages API handles text, images, PDFs, tools, thinking
- ❌ No separate "Vision API"
- ✅ Just different content block types

### 2. Extended Thinking Works with Everything
- ✅ Text conversations
- ✅ Image analysis
- ✅ PDF document understanding
- ✅ Tool use / function calling
- ✅ Multi-modal (text + image + tools)

### 3. Interleaved Thinking = Transparency
- ✅ See Claude's reasoning in real-time
- ✅ Understand how it interprets documents
- ✅ Debug tool calls
- ✅ Better user experience (shows AI is "working")

### 4. Tool Use + Vision = Powerful Automation
- ✅ Upload invoice → Extract data → Update database
- ✅ Upload catalog → Find products → Add to inventory
- ✅ Upload quote → Compare prices → Recommend action
- **All automatic!**

---

## 🚀 What This Means for Your System

### Your New Flask App Already Has This!

✅ **Extended Thinking**: Enabled in `unified_ai_client.py`
```python
thinking={"type": "enabled", "budget_tokens": 10000}
```

✅ **Interleaved Thinking**: Streaming enabled
```python
with client.messages.stream(...) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                # Stream thoughts to UI
```

✅ **Tool Use**: ToolUseAgent integrated
```python
tools=self.tool_agent.get_tools()
```

✅ **Vision/PDFs**: Content block handling
```python
if file_data['media_type'] == 'application/pdf':
    content.append({"type": "document", ...})
else:
    content.append({"type": "image", ...})
```

### All Features Work Together!

**Example: Invoice Processing with Thinking**
1. User uploads invoice.pdf
2. **Thinking stream**: "Reading PDF structure... found 5 pages... extracting line items..."
3. **Thinking stream**: "Identified 12 products... checking database for matches..."
4. **Tool call**: query_database(...)
5. **Thinking stream**: "Found 10 matches, 2 new products... price comparison shows 3 increases..."
6. **Tool call**: update_stock_price(...) × 3
7. **Response**: "✅ Processed invoice. Updated 3 prices, found 2 new products."

**All automatic, all visible, all in ONE API!** 🎊

---

## 📚 Further Reading

**Anthropic Documentation**:
- Messages API: https://docs.anthropic.com/en/api/messages
- Vision (Images): https://docs.anthropic.com/en/docs/build-with-claude/vision
- PDF Support: https://docs.anthropic.com/en/docs/build-with-claude/pdf-support
- Tool Use: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- Extended Thinking: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking

**Your Documentation**:
- `DOCUMENT_PROCESSING_WITH_CLAUDE.md` - Vision/PDF guide
- `BUILD_COMPLETE_SUMMARY.md` - What was built
- `NEW_FLASK_APP_DEPLOYMENT_GUIDE.md` - How it all works

---

**Summary**: There's NO separate Vision API. It's all the **Messages API** with different content blocks. Extended thinking, interleaved thinking, and tool use work perfectly with images and PDFs. Your new Flask app already has all of this integrated! 🚀
