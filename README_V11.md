# AI Agents V11 - InHouse Print Configuration

**Created:** 2026-01-15
**Branch:** v11
**Focus:** InHouse Print core functionality

---

##  What's New in V11

This is a **streamlined version** of the AI Agents platform, specifically configured for **InHouse Print** operations.

### Changes from V10:

**Removed (11 external modules):**
-  parametric-cad (Heavy CAD engine)
-  design_engineering (CAD/Engineering)
-  veterinary_alerts (Deprecated)
-  vsa-veterinary-alerts (Not InHouse Print)
-  voip-demo (Demo)
-  weather (Demo)
-  professional-verification (Not needed)
-  local-filesystem (Not needed)
-  salesforce (Not InHouse Print)
-  google-drive (Not needed)
-  microsoft-onedrive (Not needed)

**Removed (1 internal module):**
-  debug-module (Dev only)

**Kept (6 external modules):**
 **inhouse-kanban** - Production workflow Kanban board
 **inhouse-print** - Fred database connector (6 tools)
 **quote-calculator** - Quote engine (31 calculators, 80 tools)
 **stock-management** - Inventory management (6 tabs)
 **xero** - Xero accounting integration (25 tools)
 **shopify** - Shopify e-commerce (15 tools)

**Benefits:**
-  Faster deployments (~60% smaller codebase)
-  Reduced Render costs (fewer resources)
-  Focused on InHouse Print operations
-  Fewer dependencies = less maintenance

---

##  Module Summary

### Core Business Modules

1. **Quote Calculator** (quote-calculator/)
   - 31 calculators (4 GOD + 27 Shopify)
   - 80 registered tools
   - Database-driven pricing
   - Test suite: 97.5% pass rate

2. **Production Workflow** (inhouse-kanban/)
   - Drag & drop Kanban board
   - AI priority scoring
   - Real-time job tracking
   - Production logging

3. **Stock Management** (stock-management/)
   - Inventory tracking
   - Usage analytics
   - Reorder alerts
   - AI invoice processing

4. **InHouse Print Tools** (inhouse-print/)
   - Fred database access
   - 6 intelligent tools
   - SQL query execution
   - Stock level monitoring

5. **Xero Integration** (xero/)
   - Accounting automation
   - Invoice management
   - Financial reporting
   - 25 tools

6. **Shopify Integration** (shopify/)
   - E-commerce operations
   - Order management
   - Product sync
   - 15 tools

---

##  Deployment

### Render.com

This V11 configuration is ready to deploy to Render:

\\\yaml
Service Name: ai-agents-inhouse-v11
Branch: v11
Region: Singapore
Environment: Docker
\\\

### GitHub Repository

Clone this version:

\\\ash
git clone -b v11 <your-repo-url>
cd AI_agents
\\\

---

##  Configuration

### Environment Variables (Required)

**Database:**
- \SUPABASE_URL\
- \SUPABASE_KEY\
- \SUPABASE_DB_PASSWORD\

**AI Providers:**
- \ANTHROPIC_API_KEY\
- \OPENAI_API_KEY\

**InHouse Print (SQL Server):**
- Credentials stored in Supabase table: \i_infrastructure.user_platform_credentials\

**Xero (Optional):**
- \XERO_CLIENT_ID\
- \XERO_CLIENT_SECRET\

**Shopify (Optional):**
- \SHOPIFY_API_KEY\
- \SHOPIFY_API_SECRET\

---

##  Database Requirements

### Supabase Schemas:
1. **ai_infrastructure** - Core system (19 tables)
2. **sessions** - User sessions (9 tables)
3. **inhouse_kanban** - Production workflow
4. **public** - Shared data

### External Database:
- **Fred (SQL Server)** - InHouse Print database
  - Quote calculation tables
  - Stock inventory
  - Production data

---

##  Testing

\\\powershell
# Navigate to V11 folder
cd C:\Users\gpoli\GIT\AI_Agents_V11\AI_agents

# Start Flask server
cd AI_infrastructure
python flask_app.py

# Test in browser
# http://localhost:5001
\\\

### Verify Modules Load:
1. Check browser console for module loading
2. Verify 6 modules appear in sidebar
3. Test quote calculator
4. Test inhouse-kanban
5. Test stock-management

---

##  Migration from V10

If you have an existing V10 deployment:

1. Keep V10 running (no changes)
2. Deploy V11 as **separate service** on Render
3. Test V11 thoroughly
4. Switch DNS when ready
5. Keep V10 as fallback

---

##  Updating V11

\\\ash
# Pull latest V11 changes
git checkout v11
git pull origin v11

# Deploy to Render
git push render v11:main
\\\

---

##  Documentation

- **Architecture:** See ARCHITECTURE.md
- **Module Development:** See UI/module_development/
- **InHouse Print:** See UI/modules_external/quote-calculator/README.md

---

##  Support

For issues specific to V11:
- Check removed modules aren't referenced
- Verify environment variables are set
- Review Render deployment logs
- Compare with V10 if needed

---

**Version:** 11.0.0
**Last Updated:** 2026-01-15
**Maintained By:** InHouse Print Team
