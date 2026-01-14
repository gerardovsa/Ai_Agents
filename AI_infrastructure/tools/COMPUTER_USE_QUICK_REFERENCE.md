# Computer Use - Quick Reference Card

## 🎯 What Is It?

**Universal browser automation** using Anthropic Claude with Computer Use API.  
Claude controls a real browser to accomplish **ANY web-based task** you describe in natural language.

---

## 🚀 Quick Start

### 1. Setup (One-Time)

```bash
# Build Docker image
cd docker/computer-use/
docker build -t professional-verification-browser:latest .

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Use in Python

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to vistaprint.com, configure 1000 business cards, extract price',
    return_format='json',
    _user_id='user123'
)

print(result['result'])
# {'price': '$29.99', 'delivery': '3-5 days'}
```

### 3. Use in AI Agent (Natural Language)

```
User: "Research vistaprint.com pricing for business cards"

Agent: [Automatically calls computer_use_browse_and_extract]
       ✅ Found pricing: $29.99 for 1000 cards, 3-5 day delivery
```

---

## 📚 Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `computer_use_browse_and_extract` | Navigate websites, extract data | Competitor quote calculators, product scraping, OSINT |
| `computer_use_fill_form` | Auto-fill and submit forms | Contact forms, quote requests, account creation |
| `computer_use_compare_competitors` | Compare multiple sites | Side-by-side pricing, feature comparison |

---

## 💡 Use Cases

✅ **Competitor Research** - Quote calculators, pricing pages  
✅ **Web Scraping** - Product data, reviews, ratings  
✅ **Form Automation** - Contact forms, quote requests  
✅ **Testing** - UI/UX flows, checkout processes  
✅ **OSINT** - Social media, forums, databases  
✅ **Professional Verification** - LinkedIn, credential registries  
✅ **E-commerce** - Price comparisons, product research  
✅ **ANY web-based task**

---

## 📖 Common Examples

### Competitor Quote Calculator

```python
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to vistaprint.com business cards, configure 1000 qty 4-color both sides, extract price',
    return_format='json'
)
```

### Multi-Competitor Comparison

```python
result = registry.execute_tool(
    'computer_use_compare_competitors',
    competitors=['vistaprint.com', 'moo.com', 'printful.com'],
    comparison_task='Extract pricing for 1000 business cards'
)
```

### Product Scraping

```python
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Search amazon.com for "label printer", extract top 5 products with prices and ratings',
    return_format='json'
)
```

### Form Filling

```python
result = registry.execute_tool(
    'computer_use_fill_form',
    url='https://competitor.com/contact',
    form_data={'name': 'John Doe', 'email': 'john@example.com', 'message': 'Request quote'}
)
```

---

## 🛠️ Troubleshooting

| Error | Fix |
|-------|-----|
| "Failed to create browser container" | Start Docker: `docker ps` |
| "API key not configured" | Set: `export ANTHROPIC_API_KEY="sk-ant-..."` |
| "Max iterations reached" | Increase: `max_iterations=50` |
| "CAPTCHA detected" | Cannot automate - site has anti-bot protection |

---

## 💰 Pricing

| Task | Iterations | Cost | Time |
|------|-----------|------|------|
| Simple (1 page) | 5-10 | $0.05-$0.10 | 10-20s |
| Medium (multi-page) | 15-30 | $0.10-$0.30 | 30-60s |
| Complex (checkout) | 30-50 | $0.30-$0.50 | 1-2min |
| Comparison (3 sites) | 50-100 | $0.50-$2.00 | 2-5min |

**Monthly Budget:**
- Light (100 tasks): ~$20-30/month
- Medium (500 tasks): ~$100-150/month
- Heavy (2000 tasks): ~$400-600/month

---

## 📞 Documentation

| Resource | Location |
|----------|----------|
| Complete Guide | `AI_infrastructure/tools/COMPUTER_USE_GUIDE.md` |
| Architecture | `AI_infrastructure/COMPUTER_USE_ARCHITECTURE.md` |
| Example Script | `examples/competitor_printing_research.py` |
| Implementation | `AI_infrastructure/tools/computer_use_tools.py` |
| Docker Setup | `docker/computer-use/README.md` |

---

## 🔒 Best Practices

**✅ DO:**
- Be specific in task descriptions
- Use JSON format for structured data
- Check screenshots to debug failures
- Space out requests (respect rate limits)

**❌ DON'T:**
- Use vague task descriptions
- Hammer sites with rapid requests
- Bypass paywalls or authentication
- Extract personal data without consent

---

**Platform:** Valor AI - MustCare  
**Version:** 1.0.0  
**Last Updated:** December 16, 2025
