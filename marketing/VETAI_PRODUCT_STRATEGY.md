# VetAI Product Strategy & Technical Infrastructure
**Date:** November 25, 2025  
**Purpose:** Define realistic pricing model and required technical modules for veterinary AI platform

---

## CRITICAL REALITY CHECK

### What We ACTUALLY Have Today:
✅ **594 AI tool integrations** (Google Workspace, Microsoft 365, Slack, etc.)  
✅ **26 specialized AI agents** (can coordinate across tools)  
✅ **Thread-based conversations** (persistent context)  
✅ **Multi-agent orchestration** (Command Centre coordination)  
✅ **Automation workflows** (visual no-code builder)  

### What We DON'T Have Yet (Veterinary-Specific):
❌ **PIMS integrations** (Cornerstone, ezyVet, Avimark)  
❌ **Telephony system** (Twilio/Vonage for AI phone answering)  
❌ **SMS gateway** (for automated text reminders)  
❌ **Voice synthesis** (text-to-speech for voice reminders)  
❌ **Lab portal connectors** (IDEXX, Antech APIs)  
❌ **Veterinary-trained AI models** (SOAP note formatting, treatment protocols)  

**Marketing vs. Reality Gap:** The website promises specific veterinary features we haven't built yet.

---

## HONEST PRICING STRATEGY (Value-Based, Not Agent-Count)

### Why NOT to Price by Agent Count:
- ❌ Users could use 26 agents just for Google Docs (gaming the system)
- ❌ "Agent" is a technical concept, not a business benefit
- ❌ Doesn't align with customer value perception
- ❌ Hard to upsell/cross-sell

### RECOMMENDED: Usage-Based Tiers

**Pricing Dimensions:**
1. **Practice Size** (# of veterinarians)
2. **Transaction Volume** (appointments/month, calls handled, reminders sent)
3. **Feature Bundles** (which workflows are active)

---

## PROPOSED PRICING TIERS

### **Tier 1: Essentials** - $299/month
**Target:** Solo vet or small practice (1 vet, 1-2 staff)

**Included Workflows:**
- ✅ **Automated Appointment Reminders** (up to 500 reminders/month)
  - SMS + Email (no voice yet)
- ✅ **Basic Scheduling Assistant** (AI helps book via email/chat)
- ✅ **Simple Estimate Generator** (template-based quotes)

**What It Does:**
- Eliminates manual reminder calls
- Reduces no-shows
- Provides instant estimates

**What It Doesn't Include:**
- No phone answering
- No SOAP notes
- No lab monitoring
- No inventory tracking

**Transaction Limits:**
- 500 reminders/month
- 100 appointments booked via AI
- 50 estimates generated

---

### **Tier 2: Professional** - $599/month ⭐ MOST POPULAR
**Target:** Multi-doctor practice (2-3 vets, 3-6 staff)

**Everything in Essentials, PLUS:**
- ✅ **AI Phone Answering** (up to 1,000 calls/month)
  - Routes to humans when needed
  - Answers FAQs, books appointments
- ✅ **Voice-to-Text SOAP Notes** (up to 300 notes/month)
  - Dictate during exam, AI formats
- ✅ **Client Communication Hub**
  - Post-visit instructions auto-sent
  - Medication reminders
  - Vaccine due notifications
- ✅ **Basic Analytics Dashboard**
  - Revenue trends
  - No-show rates
  - Call volume metrics

**Transaction Limits:**
- Unlimited reminders
- 1,000 AI-handled calls/month
- 300 SOAP notes/month
- 500 client messages/month

**Why Upgrade:**
- Receptionist handles 70% fewer calls
- Vets finish notes during exams (no late nights)
- Better client engagement

---

### **Tier 3: Practice** - $999/month
**Target:** Large practice (4+ vets, 7+ staff, multi-location)

**Everything in Professional, PLUS:**
- ✅ **Real-Time Lab Monitoring** (IDEXX/Antech integration)
  - AI checks portals every 15 minutes
  - Alerts vet when results ready
- ✅ **Predictive Inventory Management**
  - Tracks usage patterns
  - Auto-generates purchase orders
  - Alerts on low stock
- ✅ **Advanced Analytics**
  - Client retention analysis
  - Service profitability
  - Staff efficiency metrics
- ✅ **Multi-Location Support**
  - Centralized dashboard
  - Cross-location scheduling
- ✅ **Custom Workflow Builder**
  - No-code automation designer
  - Practice-specific protocols

**Transaction Limits:**
- Unlimited everything
- Priority support (2-hour response SLA)
- Dedicated success manager
- Quarterly business reviews

**Why Upgrade:**
- Never miss lab results
- Never run out of supplies
- Data-driven decision making

---

### **Tier 4: Enterprise** - Custom Pricing
**Target:** Multi-location hospital groups, specialty chains

**Custom Configuration:**
- White-label option
- Custom integrations
- Dedicated infrastructure
- SLA guarantees
- On-site training

**Starts at:** $2,500/month

---

## TECHNICAL INFRASTRUCTURE REQUIRED

### Module 1: **Telephony Integration Layer**
**What:** Connect AI to phone system  
**How:** Twilio Programmable Voice API  
**Build Time:** 4-6 weeks  

**Components:**
- Twilio account + phone number provisioning
- WebSocket connection for real-time audio streaming
- Speech-to-Text (Deepgram or Google Speech API)
- Text-to-Speech (ElevenLabs or Google TTS)
- Call routing logic (AI vs. human escalation)
- Call recording + transcription storage

**Cost Structure:**
- Twilio: $0.0085/minute inbound
- Deepgram STT: $0.0043/minute
- ElevenLabs TTS: $0.30/1K characters
- **Example:** 1,000 calls/month @ 3 min avg = $38/month in API costs

**Pricing Impact:**
- Professional tier: 1,000 calls/month = ~$40 COGS
- Margin: $599 - $40 = $559 gross profit (93% margin)

---

### Module 2: **SMS/MMS Gateway**
**What:** Send automated text reminders  
**How:** Twilio Messaging API  
**Build Time:** 2-3 weeks  

**Components:**
- Twilio SMS number pool
- Message template system
- Scheduling queue (cron jobs)
- Delivery tracking + retry logic
- Opt-out management (TCPA compliance)

**Cost Structure:**
- Twilio SMS: $0.0079/message (US)
- **Example:** 500 reminders/month = $4/month

**Pricing Impact:**
- Essentials tier: 500 SMS/month = $4 COGS
- Margin: $299 - $4 = $295 gross profit (98% margin)

---

### Module 3: **Voice Reminder System**
**What:** Automated voice calls for reminders  
**How:** Twilio + Pre-recorded/TTS messages  
**Build Time:** 3-4 weeks  

**Components:**
- Voice call initiation API
- TTS message generation
- DTMF (keypress) detection for confirmations
- Voicemail detection + drop message
- Call outcome tracking

**Cost Structure:**
- Twilio voice: $0.013/minute outbound
- TTS: $0.30/1K characters
- **Example:** 500 voice reminders/month @ 1 min = $6.50/month

**Pricing Impact:**
- Can offer as add-on: +$99/month for voice reminders
- COGS: $6.50, Margin: $92.50 (93% margin)

---

### Module 4: **PIMS Integration Framework**
**What:** Connect to veterinary practice management systems  
**How:** REST APIs + screen scraping fallback  
**Build Time:** 8-12 weeks (per PIMS)  

**PIMS Priority List:**
1. **Cornerstone** (most common)
2. **ezyVet** (cloud-based, API-friendly)
3. **Avimark** (legacy, harder integration)

**Components:**
- OAuth authentication per PIMS
- Data sync engine (appointments, clients, medical records)
- Webhook listeners for real-time updates
- Data mapping layer (standardize schemas)
- Error handling + retry logic

**Cost Structure:**
- Development: $15K-$25K per PIMS integration
- Maintenance: $500/month per PIMS

**Pricing Impact:**
- Requires ALL paid tiers to have PIMS connection
- One-time setup fee: $500 (covers dev costs over 50 customers)

---

### Module 5: **Lab Portal Connectors**
**What:** Auto-check IDEXX/Antech for results  
**How:** Headless browser automation (Puppeteer)  
**Build Time:** 6-8 weeks  

**Components:**
- Credential vault (encrypted storage)
- Scheduled scrapers (every 15 minutes)
- Result parser (extract data from HTML)
- Alert system (push notifications to vets)
- Result storage (attach to patient record)

**Cost Structure:**
- Compute: $20/month (always-on EC2 instance)
- No per-transaction API costs (scraping, not API)

**Pricing Impact:**
- Only in Practice tier ($999/month)
- COGS: $20/month, Margin: $979 (98% margin)

---

### Module 6: **Voice-to-Text SOAP Engine**
**What:** Convert vet dictation to formatted SOAP notes  
**How:** Deepgram STT + GPT-4 formatting  
**Build Time:** 4-5 weeks  

**Components:**
- Real-time audio streaming from mobile app
- Deepgram for transcription
- GPT-4 prompt: "Format this dictation into SOAP structure"
- PIMS integration to save note
- Voice command detection ("save note", "discard")

**Cost Structure:**
- Deepgram: $0.0043/minute
- GPT-4: $0.03/1K tokens (avg 500 tokens/note = $0.015/note)
- **Example:** 300 notes/month = $15/month

**Pricing Impact:**
- Professional tier: 300 notes/month = $15 COGS
- Included in $599/month price

---

### Module 7: **Inventory Tracking System**
**What:** Monitor stock levels, predict usage, auto-order  
**How:** PIMS integration + ML forecasting  
**Build Time:** 10-12 weeks  

**Components:**
- Inventory sync from PIMS
- Usage pattern analysis (time series forecasting)
- Reorder threshold alerts
- Purchase order generation (email or EDI)
- Supplier integration (Henry Schein, Patterson API)

**Cost Structure:**
- Compute: $10/month
- No per-transaction costs

**Pricing Impact:**
- Only in Practice tier ($999/month)
- Massive value add (prevents $5K+ emergency orders)

---

### Module 8: **Analytics & Reporting Dashboard**
**What:** Business intelligence for practices  
**How:** PostgreSQL + Chart.js visualizations  
**Build Time:** 6-8 weeks  

**Components:**
- Data warehouse (aggregate PIMS data)
- Pre-built report templates
- Custom report builder
- Export to PDF/Excel
- Scheduled email delivery

**Cost Structure:**
- Compute: $15/month
- No per-transaction costs

**Pricing Impact:**
- Basic: Professional tier
- Advanced: Practice tier
- High perceived value (replaces $200/month BI tools)

---

## DEVELOPMENT ROADMAP (MVP to Full Platform)

### **Phase 1: MVP (3 months)** - Launch Essentials Tier
**Goal:** Prove value with simplest workflows

**Build:**
1. SMS reminders (Module 2) - 3 weeks
2. Email reminders - 1 week
3. Basic scheduling assistant (email-based) - 2 weeks
4. Simple estimate generator - 2 weeks
5. Cornerstone PIMS integration (read-only) - 8 weeks
6. Basic analytics dashboard - 4 weeks

**Launch Price:** $299/month  
**Target:** 10 pilot customers (solo vets)  
**Revenue:** $3K/month  

---

### **Phase 2: Professional Tier (6 months)** - Add Phone + SOAP
**Goal:** Unlock mid-market ($599 tier)

**Build:**
1. Telephony integration (Module 1) - 6 weeks
2. AI phone answering - 4 weeks
3. Voice-to-text SOAP (Module 6) - 5 weeks
4. Client communication hub - 3 weeks
5. ezyVet integration - 8 weeks

**Launch Price:** $599/month  
**Target:** 30 customers (20 new + 10 upgrades)  
**Revenue:** $15K/month  

---

### **Phase 3: Practice Tier (12 months)** - Enterprise Features
**Goal:** Serve large practices ($999 tier)

**Build:**
1. Lab portal connectors (Module 5) - 8 weeks
2. Inventory tracking (Module 7) - 12 weeks
3. Advanced analytics (Module 8) - 8 weeks
4. Multi-location support - 4 weeks
5. Avimark integration - 10 weeks

**Launch Price:** $999/month  
**Target:** 50 customers (35 Professional + 15 Practice)  
**Revenue:** $35K/month  

---

## REALISTIC GO-TO-MARKET STRATEGY

### **Year 1 Goals:**
- **Q1:** 10 Essentials customers ($3K MRR)
- **Q2:** 25 customers mix ($10K MRR)
- **Q3:** 40 customers, launch Professional ($20K MRR)
- **Q4:** 60 customers, 20% on Professional ($30K MRR)

**Annual Revenue:** ~$200K ARR

### **Year 2 Goals:**
- **Q1:** Launch Practice tier, 80 customers ($45K MRR)
- **Q2:** 120 customers, growth in Professional/Practice ($75K MRR)
- **Q3:** 180 customers ($120K MRR)
- **Q4:** 250 customers ($180K MRR)

**Annual Revenue:** ~$1.5M ARR

---

## COST STRUCTURE ANALYSIS

### **Per-Customer Unit Economics:**

**Essentials ($299/month):**
- SMS reminders: $4
- Compute/hosting: $5
- Support: $10
- **Total COGS:** $19/month
- **Gross Margin:** $280/month (94%)

**Professional ($599/month):**
- SMS reminders: $8
- Telephony (1,000 calls): $40
- SOAP notes (300): $15
- Compute/hosting: $15
- Support: $25
- **Total COGS:** $103/month
- **Gross Margin:** $496/month (83%)

**Practice ($999/month):**
- All Professional costs: $103
- Lab monitoring: $20
- Inventory: $10
- Advanced analytics: $15
- Dedicated support: $50
- **Total COGS:** $198/month
- **Gross Margin:** $801/month (80%)

**Blended Margin (60% Essentials, 30% Professional, 10% Practice):**
- **Average Revenue:** $449/customer
- **Average COGS:** $86/customer
- **Average Margin:** $363/customer (81%)

---

## INTEGRATION PARTNERS NEEDED

### **Critical Partnerships:**

1. **Twilio** (telephony + SMS)
   - Volume discount at 100K+ minutes/month
   - Potential co-marketing opportunity

2. **PIMS Vendors** (Cornerstone, ezyVet, Avimark)
   - Official API access (avoid screen scraping)
   - Integration marketplace listing

3. **Lab Companies** (IDEXX, Antech)
   - API partnerships (better than scraping)
   - Revenue share on increased orders?

4. **Veterinary Associations** (AVMA, state VMA)
   - Endorsement/certification
   - Member discounts for customer acquisition

5. **Distributors** (Henry Schein, Patterson)
   - EDI integration for automated ordering
   - Referral fees on supplies ordered

---

## COMPETITIVE POSITIONING

### **Direct Competitors:**
- **Weave** ($300-500/month) - Phone, SMS, reviews, scheduling
- **VetSuccess by Instinct** ($200-400/month) - Reminders, reviews, client engagement
- **Slice** ($99-299/month) - Client communication, online booking

### **Our Differentiators:**
✅ **AI-First** (not just automation)  
✅ **PIMS-Integrated** (not standalone)  
✅ **Workflow Automation** (beyond comms)  
✅ **Practice Intelligence** (analytics built-in)  

### **Positioning Statement:**
*"The only AI platform that connects your entire practice—from PIMS to phones to lab portals—eliminating admin work and giving you back 25+ hours per week."*

---

## HONEST FAQ FOR INTERNAL USE

**Q: Can we really build all this?**  
A: Not all at once. MVP (Essentials tier) is realistic in 3 months with 2-3 developers. Full platform = 12-18 months.

**Q: Do we need veterinary expertise?**  
A: Yes. Hire 1-2 vet techs or practice managers as product advisors. Pay $50/hour for 10 hours/week feedback.

**Q: What if PIMS vendors won't give API access?**  
A: Fallback to screen scraping (Puppeteer). Slower, more fragile, but works. Many practices will pressure PIMS vendors for official integration.

**Q: How do we handle HIPAA compliance?**  
A: Veterinary records aren't HIPAA-covered (pets aren't humans). But treat data with same security standards:
- Encrypted at rest (PostgreSQL with encryption)
- Encrypted in transit (TLS 1.3)
- SOC 2 Type II certification ($20K-$40K)
- Regular pen testing

**Q: What if competitors copy us?**  
A: First-mover advantage + network effects. Deep PIMS integration = high switching cost. Focus on customer success (95% retention).

**Q: Can we bootstrap or need funding?**  
A: Realistic options:
- Bootstrap: 6-12 month runway, grow slowly (10 customers/quarter)
- Seed funding ($500K-$1M): 18-month runway, hire team, grow faster (30 customers/quarter)
- Series A ($3M-$5M): After $1M ARR, scale to $10M ARR

---

## RECOMMENDED NEXT STEPS

### **Immediate (Next 30 Days):**
1. ✅ **Validate with 10 vet practices** (Zoom calls, show mockups)
   - Would they pay $299/month for automated reminders?
   - What's their biggest pain point?
2. ✅ **Prototype SMS reminder workflow** (use existing tools)
   - Google Sheets → Zapier → Twilio
   - Prove concept in 1 week
3. ✅ **Research PIMS APIs** (read documentation)
   - Cornerstone: Does API exist?
   - ezyVet: API docs available?
   - Avimark: Screen scraping feasibility?

### **Short-Term (90 Days):**
1. ✅ **Build MVP** (Essentials tier features)
2. ✅ **Onboard 5 pilot customers** (free for 90 days)
3. ✅ **Get feedback** (weekly check-ins)
4. ✅ **Refine pricing** (based on actual usage data)

### **Mid-Term (6 Months):**
1. ✅ **Launch Professional tier**
2. ✅ **Hire 2 developers** (backend + mobile)
3. ✅ **Build telephony + SOAP modules**
4. ✅ **Scale to 30 paying customers**

### **Long-Term (12 Months):**
1. ✅ **Launch Practice tier**
2. ✅ **Raise seed funding** (show $30K+ MRR)
3. ✅ **Hire growth team** (sales + marketing)
4. ✅ **Target $100K MRR**

---

## CONCLUSION

**The Bottom Line:**

**✅ REALISTIC PRICING:**
- Essentials: $299/month (basic workflows)
- Professional: $599/month (phone + SOAP)
- Practice: $999/month (full platform)

**✅ REQUIRED MODULES:** 8 core systems (telephony, SMS, PIMS, labs, SOAP, inventory, analytics, voice)

**✅ BUILD TIME:** 3 months MVP → 12 months full platform

**✅ UNIT ECONOMICS:** 80%+ gross margins (profitable per customer)

**✅ COMPETITIVE EDGE:** AI + PIMS integration + workflow automation (not just comms)

**The website is aspirational, not dishonest—but we must build these features to deliver the promised value.**

---

**Key Decision:**  
Do we launch with **honest limitations** ("coming soon" badges) or wait until features are built? 

**Recommendation:** Launch MVP tier now, pre-sell Professional tier (90-day delivery), build in public, show progress weekly. Transparency builds trust with early adopters.
