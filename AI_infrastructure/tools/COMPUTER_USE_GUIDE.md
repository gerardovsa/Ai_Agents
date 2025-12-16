# Generic Computer Use Tools - Usage Guide

## 🎯 What Can These Tools Do?

Universal browser automation using Anthropic Claude with Computer Use API. Claude controls a real browser to accomplish **ANY web-based task** you describe in natural language.

### ✅ Use Cases

**Competitor Research:**
- Navigate quote calculators and extract pricing
- Compare product features across multiple sites
- Analyze competitor checkout flows
- Extract customer reviews and ratings

**Web Scraping:**
- Extract data from sites without public APIs
- Scrape product catalogs, price lists
- Collect contact information
- Download reports or documents

**Form Automation:**
- Fill contact/quote request forms
- Create accounts on competitor sites
- Submit surveys or applications
- Automate repetitive data entry

**OSINT & Research:**
- Search social media platforms
- Investigate public databases
- Cross-reference information sources
- Build timelines from multiple sources

**Testing & QA:**
- UI/UX testing across browsers
- Verify user flows (signup, checkout, etc.)
- Performance testing (load times)
- Accessibility checks

---

## 🚀 Quick Start

### 1. Setup (One-Time)

**Build Docker Image:**
```bash
cd docker/computer-use/
docker build -t professional-verification-browser:latest .
```

**Set Anthropic API Key:**
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Linux/Mac
export ANTHROPIC_API_KEY="sk-ant-..."
```

Get API key from: https://console.anthropic.com/

### 2. Basic Usage

**Python:**
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Research competitor quote calculator
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to vistaprint.com quote calculator, configure 1000 business cards 4-color both sides, extract final price and delivery time',
    return_format='json',
    _user_id='user123'
)

print(result['result'])
# {'price': '$29.99', 'delivery': '3-5 days', 'shipping': '$7.99'}
```

**AI Agent (Natural Language):**
```
User: "Research vistaprint.com business card pricing for 1000 quantity"

Agent: [Automatically calls computer_use_browse_and_extract tool]
       ✅ Found pricing: $29.99 for 1000 cards, 3-5 day delivery
```

---

## 📖 Tool Reference

### `computer_use_browse_and_extract`

**Purpose:** Universal browser automation - navigate, interact, extract data

**Parameters:**
- `task` (required): Natural language description of WHAT to do
- `return_format` (optional): `'json'`, `'text'`, or `'auto'` (default)
- `max_iterations` (optional): Max browser actions (default 30)

**Examples:**

```python
# Competitor quote calculator
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Go to printful.com, search for t-shirt printing, extract pricing tiers for 100, 500, 1000 units',
    return_format='json'
)
# Returns: {'100': '$8.50/unit', '500': '$7.25/unit', '1000': '$6.50/unit'}

# Product research
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Search amazon.com for "thermal label printer", extract top 3 product names, prices, and ratings',
    return_format='json'
)
# Returns: [
#   {'name': 'DYMO LabelWriter 450', 'price': '$99.99', 'rating': 4.5},
#   {'name': 'Brother QL-800', 'price': '$129.99', 'rating': 4.7},
#   ...
# ]

# Customer reviews
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Visit trustpilot.com, search for "vistaprint", extract overall rating and top 5 most common complaints',
    return_format='text'
)
# Returns: "Overall rating: 3.8/5. Common complaints: slow delivery (42%), quality issues (28%), customer service (18%), pricing not as advertised (8%), website bugs (4%)"
```

---

### `computer_use_fill_form`

**Purpose:** Automatically fill and submit web forms

**Parameters:**
- `url` (required): Form page URL
- `form_data` (required): Field → value mapping
- `submit` (optional): Click submit button (default `True`)
- `wait_for_result` (optional): Wait for confirmation (default `True`)

**Examples:**

```python
# Request quote from competitor
result = registry.execute_tool(
    'computer_use_fill_form',
    url='https://vistaprint.com/contact',
    form_data={
        'name': 'Research Team',
        'email': 'research@mycompany.com',
        'company': 'MustCare Printing',
        'quantity': '1000',
        'product': 'Business Cards',
        'message': 'Request quote for 1000 cards, 4-color both sides'
    }
)
# Returns: {'success': True, 'result': 'Thank you! We will send your quote within 24 hours.'}

# Create account for research
result = registry.execute_tool(
    'computer_use_fill_form',
    url='https://competitor.com/signup',
    form_data={
        'email': 'research@mycompany.com',
        'password': 'TempPassword123!',
        'company': 'MustCare Research',
        'industry': 'Printing'
    },
    submit=True
)
```

---

### `computer_use_compare_competitors`

**Purpose:** Compare multiple websites side-by-side

**Parameters:**
- `competitors` (required): List of competitor URLs
- `comparison_task` (required): What to extract from each
- `return_format` (optional): `'json'` or `'text'` (default `'json'`)

**Examples:**

```python
# Compare printing prices
result = registry.execute_tool(
    'computer_use_compare_competitors',
    competitors=['vistaprint.com', 'moo.com', 'printful.com'],
    comparison_task='Extract pricing for 1000 business cards, 4-color both sides, standard delivery'
)

print(result['result'])
# {
#   'vistaprint.com': {'price': '$29.99', 'delivery': '3-5 days', 'shipping': '$7.99'},
#   'moo.com': {'price': '$39.99', 'delivery': '2-4 days', 'shipping': 'FREE'},
#   'printful.com': {'price': '$34.99', 'delivery': '4-7 days', 'shipping': '$5.99'}
# }

# Compare feature sets
result = registry.execute_tool(
    'computer_use_compare_competitors',
    competitors=['hubspot.com/pricing', 'salesforce.com/pricing'],
    comparison_task='Extract features included in Professional tier'
)
```

---

## 💡 Best Practices

### Writing Good Task Descriptions

**✅ DO:**
- Be specific about desired data points
- Include quantity/size/color specifications
- Specify return format (JSON for structured data)
- Mention exact element names if known

```python
# Good
task='Navigate to vistaprint.com business cards, select 1000 quantity, 3.5x2 size, 4-color both sides, extract FINAL price including shipping'

# Bad
task='Get vistaprint pricing'  # Too vague
```

**❌ DON'T:**
- Use vague language ("get info", "check site")
- Assume Claude knows your preferences
- Skip important details (size, color, quantity)

### Return Formats

**Use JSON when:**
- Extracting structured data (prices, lists, tables)
- Comparing multiple items
- Building datasets

**Use TEXT when:**
- Summarizing findings
- Qualitative analysis (reviews, complaints)
- Narrative reports

### Performance Tips

**Reduce Iterations:**
- Simple single-page extractions: `max_iterations=15`
- Multi-page flows (signup, checkout): `max_iterations=30`
- Complex comparisons: `max_iterations=50`

**Check Screenshots:**
```python
result = registry.execute_tool(...)

# View screenshots to debug
for screenshot in result['screenshots']:
    print(f"Iteration {screenshot['iteration']}: {screenshot['timestamp']}")
    # Decode base64 to view image
```

---

## 🛠️ Troubleshooting

### "Failed to create browser container"

**Cause:** Docker not running or image not built

**Fix:**
```bash
# Check Docker running
docker ps

# Build image
cd docker/computer-use/
docker build -t professional-verification-browser:latest .
```

---

### "Anthropic API key not configured"

**Cause:** ANTHROPIC_API_KEY environment variable not set

**Fix:**
```bash
# Set permanently (add to ~/.bashrc or system environment)
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify
echo $ANTHROPIC_API_KEY
```

---

### "Max iterations reached"

**Cause:** Task too complex or site slow to load

**Fix:**
```python
# Increase max_iterations
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='...',
    max_iterations=50  # Increase from default 30
)
```

---

### "CAPTCHA detected"

**Cause:** Site has anti-bot protection

**Fix:** Cannot automate sites with CAPTCHAs. Consider:
- Using site's public API instead
- Manual data collection
- Contacting site for data access

---

### Element not found / Task fails

**Cause:** Site layout changed or task description unclear

**Fix:**
1. Manually browse site to verify layout
2. Be more specific in task description
3. Check screenshots to see what Claude saw
4. Try simpler task first to verify tool works

---

## 💰 Pricing & Limits

**Anthropic API Costs:**
- Input tokens: ~$0.003 per 1K tokens
- Output tokens: ~$0.015 per 1K tokens
- Typical task: **$0.05 - $0.50** depending on complexity

**Platform Rate Limits:**
- 100 calls per hour
- 500 calls per day
- Limited by Docker container resources

**Best Practices:**
- Cache results (don't re-scrape same data)
- Batch comparisons (use `computer_use_compare_competitors` instead of multiple single calls)
- Space out requests (avoid rapid-fire calls to same site)

---

## 🔒 Ethical Guidelines

**✅ DO:**
- Respect robots.txt files
- Use for legitimate research purposes
- Identify yourself in forms (use real company email)
- Space out requests to avoid overwhelming sites

**❌ DON'T:**
- Scrape sites that prohibit automation
- Overwhelm sites with rapid requests
- Bypass paywalls or authentication
- Use for spam or malicious purposes
- Extract personal data without consent

---

## 📚 Integration Examples

### AI Agent Integration

Tools are automatically available to AI agents via Tool Registry V3:

```python
# Agent system prompt
"""
You have access to browser automation tools:
- computer_use_browse_and_extract: Navigate websites and extract data
- computer_use_fill_form: Fill web forms automatically
- computer_use_compare_competitors: Compare multiple sites

When user asks for competitor research or web data, use these tools.
"""

# User query
"Research vistaprint.com pricing for business cards"

# Agent response
[Calls computer_use_browse_and_extract automatically]
✅ Vistaprint pricing: 500 cards = $20.99, 1000 cards = $29.99, 2000 cards = $49.99
Delivery: 3-5 business days standard, 1-2 days rush (+$15)
```

---

### Workflow Integration

Combine with other platform tools:

```python
# Step 1: Research competitor pricing
competitor_pricing = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Extract vistaprint.com business card pricing for 500, 1000, 2000 quantities',
    return_format='json'
)

# Step 2: Update database
registry.execute_tool(
    'postgres_execute',
    statement=f"INSERT INTO competitor_pricing (competitor, product, qty_500, qty_1000) VALUES ('Vistaprint', 'Business Cards', {competitor_pricing['500']}, {competitor_pricing['1000']})",
    connection_id='...'
)

# Step 3: Generate report
registry.execute_tool(
    'generate_pdf_report',
    title='Competitor Pricing Analysis',
    data=competitor_pricing
)
```

---

## 🎓 Advanced Examples

### Multi-Step Research Flow

```python
# Research competitor's entire product catalog
task = """
1. Navigate to printful.com product catalog
2. For each product category (Apparel, Home & Living, Accessories):
   - Extract product name, base price, and available sizes
   - Click into 3 example products
   - Extract detailed pricing tiers (1-10, 11-50, 51-100, 101+ units)
3. Return as JSON with structure:
   {
     "category": {
       "product_name": {
         "base_price": "$X",
         "tiers": {"1-10": "$X/unit", "11-50": "$Y/unit", ...}
       }
     }
   }
"""

result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task=task,
    return_format='json',
    max_iterations=100  # Complex multi-page task
)
```

---

### Checkout Flow Testing

```python
# Test competitor checkout flow (don't actually purchase!)
task = """
1. Go to vistaprint.com
2. Configure product: 1000 business cards, 3.5x2, 4-color both sides
3. Add to cart
4. Proceed to checkout
5. Stop at payment page (DO NOT ENTER PAYMENT)
6. Extract:
   - Subtotal
   - Shipping options (standard/express/rush with prices)
   - Taxes
   - Discount code field (yes/no)
   - Total
7. Count number of clicks required from homepage to checkout
8. Return as JSON
"""

result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task=task,
    return_format='json',
    max_iterations=40
)

# Result includes UX metrics
print(f"Clicks to checkout: {result['result']['clicks_required']}")
print(f"Total price: {result['result']['total']}")
```

---

## 📞 Support

**Issues?**
- Check Docker running: `docker ps`
- Verify API key set: `echo $ANTHROPIC_API_KEY`
- Review screenshots in result to see what Claude saw
- Increase `max_iterations` for complex tasks

**Questions?**
See `AI_infrastructure/tools/computer_use_tools.py` source code for implementation details.

---

**Last Updated:** December 16, 2025  
**Version:** 1.0.0  
**Platform:** Valor AI - MustCare
