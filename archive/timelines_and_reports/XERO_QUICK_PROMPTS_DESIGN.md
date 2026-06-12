# Xero Quick Prompts Design Document
**Created:** December 17, 2024  
**Purpose:** Enhance "Export for AI" feature with pre-written analysis prompts  
**Inspired by:** Communication Hub agent dropdown pattern

---

## Overview

Add a **Quick Prompts dropdown** next to the "Export for AI" button on all Xero dashboards. When clicked, users see dashboard-specific analysis questions they can select. Upon selection, the dashboard data + selected prompt are copied to clipboard in a conversation-ready format.

---

## UI Design (Inspired by Communication Hub)

### Button Placement
```
┌─────────────────────────────────────────┐
│  XERO DASHBOARD HEADER                   │
│                                          │
│  [🎯 Quick Prompts ▼]  [📋 Export]     │ ← Top-right corner
└─────────────────────────────────────────┘
```

### Dropdown Structure
```
┌───────────────────────────────────────────────────────┐
│ 💬 Quick Analysis Prompts                             │
│ Business Comparison Dashboard                         │
├───────────────────────────────────────────────────────┤
│ 🎯 STRATEGIC ANALYSIS (Generic - All Dashboards)     │
│ ├─ 🔬 Deep Insights Analysis                          │
│ │   → Multi-domain analysis with structured...        │
│ │   [Click to see full framework]                     │
│ ├─ 🚀 Actionable Strategy                             │
│ │   → WSJF prioritization with phased plan...         │
│ │   [Click to see full framework]                     │
│ ├─ 📊 Historical Comparison                           │
│ │   → YoY, MoM, QoQ, STLY with projections...         │
│ │   [Click to see full framework]                     │
│ ├─ 💡 Key Insights & Executive Summary                │
│ │   → Distilled insights ranked by impact...          │
│ │   [Click to see full framework]                     │
│ ├─ ⚡ Next Action Steps (Tactical)                    │
│ │   → 7-30 day action plan with priorities...         │
│ │   [Click to see full framework]                     │
│ └─ 🎯 Data Explanation & Context                      │
│     → Plain-language explanation for all...           │
│     [Click to see full framework]                     │
│                                                       │
├───────────────────────────────────────────────────────┤
│ 📊 GROWTH & TRENDS (Dashboard-Specific)              │
│ ├─ Compare YoY growth across businesses               │
│ ├─ Identify declining market share trends             │
│ └─ Which business is growing fastest?                 │
│                                                       │
│ 💰 FINANCIAL HEALTH                                   │
│ ├─ Which business has best collection days?           │
│ ├─ Analyze average order value trends                 │
│ └─ Identify businesses with cash flow issues          │
│                                                       │
│ 🎯 RECOMMENDATIONS                                    │
│ ├─ Which business needs immediate attention?          │
│ ├─ Suggest resource allocation strategy               │
│ └─ Recommend marketing budget distribution            │
│                                                       │
├───────────────────────────────────────────────────────┤
│ ✨ CUSTOM PROMPT                                      │
│ └─ Write your own analysis question...                │
└───────────────────────────────────────────────────────┘
```

**Note:** Strategic prompts show truncated preview text. Clicking reveals the full multi-step framework before copying to clipboard.

---

## Prompt Categories by Dashboard

### **🎯 STRATEGIC ANALYSIS (Generic - All Dashboards)**

These powerful multi-step prompts work across all dashboards and provide deep analytical frameworks:

#### 🔬 Deep Insights Analysis
**Prompt:**
```
You are provided Xero financial data below including:
- Date range and time period
- SQL queries used to extract this data
- Raw JSON data from multiple sources

OBJECTIVE: Extract maximum insights from this information using a structured multi-domain analysis approach.

ANALYSIS FRAMEWORK:

STEP 1 - Multi-Perspective Analysis
→ Analyze data from multiple business perspectives:
  • Financial health (cash flow, profitability, collection efficiency)
  • Operational performance (transaction volumes, processing times)
  • Strategic positioning (market trends, competitive dynamics)
  • Risk assessment (volatility, exposure, concentration)
  • Growth trajectory (momentum, acceleration, sustainability)

STEP 2 - Domain Identification & Deep Dive
→ Identify 3-5 major domains where significant patterns emerge
→ For each domain, perform additional statistical analyses:
  • Calculate trend lines, growth rates, volatility metrics
  • Identify outliers, anomalies, and inflection points
  • Compare to industry benchmarks if applicable
→ Cross-reference patterns across domains to find correlations

STEP 3 - Insight Explanation & Reasoning
→ For each insight discovered:
  • State the insight clearly and concisely
  • Explain the underlying data patterns that support it
  • Describe the business implications and potential impact
  • Rate confidence level (High/Medium/Low) with justification
  • Identify any caveats or limitations in the analysis

STEP 4 - Follow-Up Actions & Tool Recommendations
→ Suggest specific follow-up analyses I can perform:
  • Additional SQL queries to drill deeper
  • Comparative analyses to validate findings
  • Predictive models to forecast trends
  • Risk scenarios to test resilience
→ Recommend specific tools I have access to that would help

DELIVERABLE: Comprehensive insight report with executive summary, detailed findings, and actionable next steps.
```

#### 🚀 Actionable Strategy Development
**Prompt:**
```
You are provided Xero financial data below including date range, SQL queries, and raw data.

OBJECTIVE: Develop a prioritized action plan that maximizes business performance using data-driven insights.

STRATEGIC FRAMEWORK:

STEP 1 - Opportunity & Challenge Identification
→ Scan the data to identify:
  • High-impact opportunities (quick wins, strategic moves)
  • Critical challenges (risks, bottlenecks, inefficiencies)
  • Hidden patterns (emerging trends, subtle signals)
→ Quantify potential impact for each item (Revenue, Cost, Risk, Time)

STEP 2 - Prioritization Using Weighted Shortest Job First (WSJF)
→ For each opportunity/challenge, calculate:
  • Business Value (1-10): Revenue impact, cost savings, risk reduction
  • Time Criticality (1-10): Urgency, seasonal factors, competitive pressure
  • Risk Reduction (1-10): Mitigates major risks, improves stability
  • Implementation Effort (1-10): Time, resources, complexity required
  • WSJF Score = (Business Value + Time Criticality + Risk Reduction) / Implementation Effort
→ Rank all items by WSJF score (highest priority first)

STEP 3 - Analysis & Reasoning
→ For top 5 prioritized items:
  • Explain why this action matters (strategic rationale)
  • Describe expected outcomes (quantified when possible)
  • Identify dependencies and prerequisites
  • Highlight potential risks and mitigation strategies
  • Estimate timeline and resource requirements

STEP 4 - Step-by-Step Implementation Plan
→ Create detailed action plan with:
  • Phase 1 (0-30 days): Immediate actions, quick wins
  • Phase 2 (30-90 days): Strategic initiatives, capacity building
  • Phase 3 (90+ days): Long-term improvements, optimization
→ For each phase, specify:
  • Specific tasks and deliverables
  • Responsible parties (even if just "business owner")
  • Success metrics and KPIs
  • Review checkpoints and decision gates

STEP 5 - Follow-Up Tool Recommendations
→ Suggest specific analyses I can run to:
  • Monitor progress on action items
  • Validate assumptions and projections
  • Detect early warning signs of issues
  • Measure ROI and effectiveness

DELIVERABLE: Prioritized action plan with WSJF scores, implementation roadmap, and monitoring framework.
```

#### 📊 Historical Comparison Analysis
**Prompt:**
```
You are provided Xero financial data with historical time series information.

OBJECTIVE: Perform comprehensive temporal analysis to identify trends, patterns, and strategic implications.

COMPARISON FRAMEWORK:

STEP 1 - Temporal Analysis Dimensions
→ Analyze data across multiple time comparisons:
  • Year-over-Year (YoY): Compare to same period last year
  • Month-over-Month (MoM): Sequential period progression
  • Quarter-over-Quarter (QoQ): Quarterly trend analysis
  • Same Time Last Year (STLY): Direct period matching
  • Multi-Year Trends: 3-5 year historical patterns if available
  • Seasonal Adjustments: Remove seasonal effects to see true trends

STEP 2 - Trend Identification & Classification
→ For each metric, identify:
  • Direction: Growing, declining, stable, volatile
  • Magnitude: Percentage change, absolute change, rate of change
  • Acceleration: Is trend speeding up or slowing down?
  • Cyclicality: Repeating patterns, seasonal cycles
  • Anomalies: Unusual spikes, dips, or disruptions
→ Classify trends as:
  • Structural (long-term, fundamental changes)
  • Cyclical (repeating patterns tied to business cycles)
  • Seasonal (predictable time-based variations)
  • Random (noise, one-time events)

STEP 3 - Causal Analysis & Context
→ For significant trends, investigate:
  • What business events might explain this pattern?
  • Are there external factors (economy, seasonality, competition)?
  • Do multiple metrics confirm the same story?
  • Are there leading indicators that predicted this?
→ Build narrative explaining the "why" behind the numbers

STEP 4 - Projection & Scenario Planning
→ Based on historical patterns:
  • Project forward 3-6 months using trend analysis
  • Develop 3 scenarios: Optimistic, Base Case, Pessimistic
  • Identify trigger points that would shift scenarios
  • Recommend monitoring metrics for early detection

STEP 5 - Strategic Implications
→ Answer key questions:
  • What do these trends mean for business strategy?
  • Should we accelerate, maintain, or pivot current approach?
  • What resources should we allocate based on trends?
  • What risks do these trends expose?

DELIVERABLE: Historical trend report with YoY/MoM/QoQ analysis, projections, and strategic recommendations.
```

#### 💡 Key Insights & Executive Summary
**Prompt:**
```
You are provided Xero financial data below.

OBJECTIVE: Distill complex data into clear, actionable insights for executive decision-making.

SYNTHESIS FRAMEWORK:

STEP 1 - Data Comprehension
→ Quickly scan all provided data to understand:
  • What metrics are included and their meanings
  • Time periods covered and data granularity
  • Data quality and completeness
→ Identify the 5-7 most important metrics in this dataset

STEP 2 - Pattern Recognition
→ Look for:
  • Standout numbers (exceptional performance or concerns)
  • Surprising findings (unexpected patterns)
  • Hidden relationships (correlations between metrics)
  • Missing context (what's not shown but matters)

STEP 3 - Key Insights Extraction (Top 5)
→ For each insight:
  • ONE-SENTENCE SUMMARY: The core finding in plain language
  • SUPPORTING DATA: Specific numbers that prove this insight
  • SO WHAT?: Why this matters to the business
  • CONFIDENCE LEVEL: How certain are we? (High/Medium/Low)
→ Rank insights by business impact (most important first)

STEP 4 - Executive Explanation
→ Explain the data story in 3 parts:
  • WHERE WE ARE: Current state summary (2-3 sentences)
  • HOW WE GOT HERE: Key drivers and trends (2-3 sentences)
  • WHERE WE'RE HEADING: Trajectory and implications (2-3 sentences)
→ Use business language, not technical jargon
→ Include specific numbers for credibility

STEP 5 - Recommendations Summary
→ Provide 3-5 concrete recommendations:
  • Each recommendation in one clear sentence
  • Expected impact if implemented
  • Approximate effort/timeline required
  • Why this should be prioritized

DELIVERABLE: Executive summary with top 5 insights, data story narrative, and prioritized recommendations.
```

#### ⚡ Next Action Steps (Tactical)
**Prompt:**
```
You are provided Xero financial data below.

OBJECTIVE: Identify immediate tactical actions that can be executed in the next 7-30 days.

TACTICAL FRAMEWORK:

STEP 1 - Quick Wins Identification
→ Scan data for opportunities that are:
  • HIGH IMPACT: Meaningful improvement to key metrics
  • LOW EFFORT: Can be done quickly with existing resources
  • LOW RISK: Minimal downside if it doesn't work
→ Look for:
  • Process inefficiencies that are obvious
  • Low-hanging fruit in collections or revenue
  • Immediate risks that need mitigation

STEP 2 - Action Categorization
→ Group actions into tactical categories:
  • COLLECTIONS: Actions to improve cash flow (chase invoices, review terms)
  • EFFICIENCY: Process improvements (automate, streamline, eliminate waste)
  • REVENUE: Quick revenue opportunities (upsell, cross-sell, price optimization)
  • COST: Immediate cost reductions (renegotiate, eliminate, optimize)
  • RISK: Urgent risk mitigation (address exposures, reduce volatility)
→ For each category, list 2-3 specific actions

STEP 3 - Action Specification
→ For each action, provide:
  • WHAT: Specific task to complete (be precise)
  • WHO: Role or person who should do it
  • WHEN: Deadline or timeframe (days/weeks)
  • HOW: Brief method or approach
  • WHY: Expected outcome or benefit (quantified if possible)
  • MEASURE: How to track success

STEP 4 - Priority Sequence
→ Organize actions into execution sequence:
  • THIS WEEK (Next 7 days): 2-3 urgent actions
  • NEXT TWO WEEKS (8-14 days): 3-5 important actions
  • THIS MONTH (15-30 days): 5-7 valuable actions
→ Ensure actions don't conflict or overload capacity

STEP 5 - Follow-Up Analysis
→ Suggest specific follow-up analyses to:
  • Monitor progress on tactical actions
  • Measure impact and ROI
  • Identify next wave of tactical opportunities
  • Escalate issues that need strategic attention

DELIVERABLE: Tactical action plan with prioritized sequence, clear ownership, and success metrics.
```

#### 🎯 Data Explanation & Context
**Prompt:**
```
You are provided Xero financial data below.

OBJECTIVE: Explain what this data shows in clear business language, providing context and meaning.

EXPLANATION FRAMEWORK:

STEP 1 - Data Overview
→ Describe what we're looking at:
  • What type of financial data is this? (revenue, expenses, cash flow, etc.)
  • What time period does it cover?
  • What businesses or entities are included?
  • How was this data collected? (mention SQL queries if relevant)

STEP 2 - Metric Definitions
→ For each key metric shown:
  • Define what it means in simple terms
  • Explain how it's calculated
  • Describe what "good" looks like for this metric
  • Note any industry benchmarks or standards
→ Use analogies or examples to make it relatable

STEP 3 - Current State Explanation
→ Describe what the numbers are telling us:
  • What are the headline figures? (state specific numbers)
  • Are these numbers good, bad, or neutral? (provide context)
  • How do they compare to typical expectations?
  • What patterns or trends are visible?
→ Explain in terms a non-financial person would understand

STEP 4 - Business Context
→ Put the data in business context:
  • What business activities do these numbers represent?
  • What external factors might be influencing these results?
  • What internal decisions or strategies are reflected here?
  • What does this tell us about business health and performance?

STEP 5 - Next Steps Guidance
→ Guide the user on what to do with this information:
  • What questions should they be asking based on this data?
  • What additional analysis would provide more clarity?
  • Who should see this data and why?
  • What decisions can be informed by these insights?

DELIVERABLE: Plain-language explanation of the data with context, definitions, and guidance for next steps.
```

---

### **1. Business Comparison Dashboard**

*(Dashboard-specific prompts remain the same)*

#### 📊 Growth & Trends
- "Compare year-over-year growth trends across all businesses"
- "Identify businesses with declining market share"
- "Which business is growing fastest and why?"
- "Analyze revenue acceleration or deceleration patterns"

#### 💰 Financial Health
- "Which business has the best collection days and why?"
- "Analyze average order value trends by business"
- "Identify businesses with concerning cash flow patterns"
- "Compare payment terms efficiency across businesses"

#### 🎯 Recommendations
- "Which business needs immediate attention or intervention?"
- "Suggest resource allocation strategy based on performance"
- "Recommend marketing budget distribution across businesses"
- "Identify cross-selling opportunities between businesses"

---

### **2. Consolidated Revenue Dashboard**

#### 💵 Cash Flow Analysis
- "Analyze cash flow health based on aging buckets"
- "Which aging bucket is most concerning and why?"
- "Project cash flow for next 30/60/90 days"
- "Identify collection risk factors in outstanding amounts"

#### 📈 Revenue Trends
- "Which business contributes most to total revenue?"
- "Analyze month-over-month consolidated revenue trends"
- "Identify seasonal patterns in consolidated data"
- "Compare actual vs. expected collection timelines"

#### ⚠️ Risk Assessment
- "Which outstanding invoices need immediate attention?"
- "Analyze bad debt risk in 90+ day bucket"
- "Recommend collection strategy priorities"
- "Identify businesses with improving/declining collection rates"

---

### **3. Seasonality Dashboard**

#### 📅 Seasonal Patterns
- "Which months are peak season for this business?"
- "What are the historically slow periods?"
- "Compare this year's performance to 3-year average"
- "Identify emerging seasonal trend changes"

#### 🎯 Marketing Strategy
- "When should we launch marketing campaigns?"
- "Recommend inventory planning based on seasonality"
- "Which months need promotional support?"
- "Suggest staffing adjustments for peak periods"

#### 🔮 Forecasting
- "Forecast Q1 performance based on seasonal patterns"
- "Project holiday season revenue using historical data"
- "Identify unusual deviations from seasonal norms"
- "Recommend budget allocation by season"

---

### **4. Forecast Dashboard**

#### 📊 Scenario Analysis
- "Should I budget based on optimistic or pessimistic scenario?"
- "What are the biggest risks to this forecast?"
- "How confident should I be in the 6-month projection?"
- "Analyze volatility factors affecting accuracy"

#### 🎯 Risk Factors
- "Which external factors pose greatest risk to forecast?"
- "Identify controllable vs. uncontrollable risk factors"
- "Recommend risk mitigation strategies"
- "What early warning indicators should I monitor?"

#### 💼 Business Planning
- "Create quarterly targets based on this forecast"
- "Recommend expense budget aligned with projections"
- "Identify growth investment opportunities"
- "Suggest contingency plans for downside scenarios"

---

## Technical Implementation

### Step 1: Add Quick Prompts Button
```javascript
createQuickPromptsButton(containerId, dashboardName) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Check if button already exists
    if (container.querySelector('.quick-prompts-btn')) return;

    // Create button (purple gradient, matches export button style)
    const button = document.createElement('button');
    button.className = 'quick-prompts-btn';
    button.innerHTML = `
        <i class="fas fa-lightbulb"></i>
        <span>Quick Prompts</span>
        <i class="fas fa-chevron-down" style="font-size: 10px; margin-left: 4px;"></i>
    `;
    
    button.style.cssText = `
        position: absolute;
        top: 16px;
        right: 160px; /* Left of Export button */
        background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%);
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(137, 87, 229, 0.3);
        transition: all 0.2s ease;
        z-index: 100;
    `;

    // Hover effects
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-1px)';
        button.style.boxShadow = '0 4px 12px rgba(137, 87, 229, 0.4)';
    });

    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 2px 8px rgba(137, 87, 229, 0.3)';
    });

    // Click handler - show dropdown
    button.addEventListener('click', (e) => {
        e.stopPropagation();
        this.showQuickPromptsDropdown(e, dashboardName, containerId);
    });

    container.appendChild(button);
}
```

### Step 2: Create Dropdown (Adapted from Communication Hub)
```javascript
showQuickPromptsDropdown(event, dashboardName, containerId) {
    // Remove any existing dropdown
    document.querySelectorAll('.quick-prompts-dropdown').forEach(d => d.remove());

    // Get button element for positioning
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();

    // Create dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'quick-prompts-dropdown';
    
    dropdown.style.cssText = `
        position: fixed;
        top: ${rect.bottom + 8}px;
        right: ${window.innerWidth - rect.right}px;
        background: #1a1a1a;
        border: 1px solid #30363d;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        z-index: 10000;
        width: 420px;
        max-height: 600px;
        overflow-y: auto;
        color: #f0f6fc;
        scrollbar-width: thin;
        scrollbar-color: #30363d #1a1a1a;
    `;

    // Get prompts for this dashboard
    const prompts = this.getQuickPromptsForDashboard(dashboardName);

    // Build HTML
    let html = `
        <div style="padding: 16px; border-bottom: 1px solid #30363d;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <i class="fas fa-lightbulb" style="color: #fbbf24; font-size: 18px;"></i>
                <div style="font-size: 14px; font-weight: 700; color: #f0f6fc;">Quick Analysis Prompts</div>
            </div>
            <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">
                ${dashboardName} Dashboard
            </div>
        </div>
        <div style="padding: 8px 12px;">
    `;

    // Render each category
    prompts.forEach((category, categoryIndex) => {
        // ✅ Check if this is a strategic prompt category (they're longer, need special rendering)
        const isStrategic = category.name.includes('Analysis') || 
                           category.name.includes('Strategy') || 
                           category.name.includes('Comparison') ||
                           category.name.includes('Summary') ||
                           category.name.includes('Steps') ||
                           category.name.includes('Explanation');

        html += `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 6px 8px; background: ${isStrategic ? 'rgba(251, 191, 36, 0.1)' : 'rgba(99, 102, 241, 0.1)'}; border-radius: 4px; ${isStrategic ? 'border-left: 3px solid #fbbf24;' : ''}">
                    <span style="font-size: 16px;">${category.icon}</span>
                    <div style="font-size: 12px; font-weight: 700; color: #f0f6fc; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${category.name}
                    </div>
                    ${isStrategic ? '<span style="margin-left: auto; font-size: 10px; color: #fbbf24; font-weight: 600; background: rgba(251, 191, 36, 0.2); padding: 2px 6px; border-radius: 3px;">STRATEGIC</span>' : ''}
                </div>
        `;

        // Render prompts in this category
        category.prompts.forEach((prompt, index) => {
            // For strategic prompts, show truncated preview
            const displayText = isStrategic ? 
                (prompt.split('\n')[0] + ' [Multi-step framework - click to use]') : 
                prompt;

            html += `
                <div class="prompt-option" 
                     data-prompt="${this.escapeHtml(prompt)}"
                     data-is-strategic="${isStrategic}"
                     style="padding: 10px 12px; margin: 4px 0; cursor: pointer; border-radius: 6px; display: flex; align-items: center; gap: 10px; transition: all 0.15s ease; ${isStrategic ? 'background: rgba(251, 191, 36, 0.05);' : ''}"
                     onmouseover="this.style.background='${isStrategic ? 'rgba(251, 191, 36, 0.15)' : 'rgba(99, 102, 241, 0.15)'}'; this.style.paddingLeft='16px'" 
                     onmouseout="this.style.background='${isStrategic ? 'rgba(251, 191, 36, 0.05)' : 'transparent'}'; this.style.paddingLeft='12px'">
                    <i class="fas ${isStrategic ? 'fa-brain' : 'fa-comment-dots'}" style="color: ${isStrategic ? '#fbbf24' : '#6366f1'}; font-size: 12px; width: 16px; text-align: center;"></i>
                    <div style="flex: 1; font-size: 13px; color: #e5e7eb; line-height: 1.4;">
                        ${this.escapeHtml(displayText)}
                    </div>
                    <i class="fas fa-arrow-right" style="color: #8b949e; font-size: 11px; opacity: 0.5;"></i>
                </div>
            `;
        });

        html += `</div>`;
    });

    // Custom prompt option
    html += `
        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #30363d;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 6px 8px;">
                <span style="font-size: 16px;">✨</span>
                <div style="font-size: 12px; font-weight: 700; color: #f0f6fc; text-transform: uppercase; letter-spacing: 0.5px;">
                    Custom Prompt
                </div>
            </div>
            <textarea id="custom-prompt-input" 
                      placeholder="Write your own analysis question..."
                      style="width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #f0f6fc; font-size: 13px; min-height: 80px; resize: vertical; font-family: inherit;"></textarea>
            <button class="custom-prompt-submit" 
                    style="margin-top: 8px; width: 100%; padding: 10px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;"
                    onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(99, 102, 241, 0.4)'"
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <i class="fas fa-paper-plane"></i> Export with Custom Prompt
            </button>
        </div>
    `;

    html += `</div>`;
    dropdown.innerHTML = html;
    document.body.appendChild(dropdown);

    // Add click handlers for prompt options
    dropdown.querySelectorAll('.prompt-option').forEach(option => {
        option.addEventListener('click', async (e) => {
            e.stopPropagation();
            const prompt = option.dataset.prompt;
            dropdown.remove();
            await this.exportWithPrompt(dashboardName, prompt, containerId);
        });
    });

    // Add click handler for custom prompt submit
    const customSubmit = dropdown.querySelector('.custom-prompt-submit');
    if (customSubmit) {
        customSubmit.addEventListener('click', async (e) => {
            e.stopPropagation();
            const textarea = dropdown.querySelector('#custom-prompt-input');
            const customPrompt = textarea.value.trim();
            
            if (!customPrompt) {
                textarea.style.borderColor = '#f85149';
                setTimeout(() => textarea.style.borderColor = '#30363d', 2000);
                return;
            }

            dropdown.remove();
            await this.exportWithPrompt(dashboardName, customPrompt, containerId);
        });
    }

    // Close on outside click
    setTimeout(() => {
        const closeHandler = (e) => {
            if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', closeHandler);
            }
        };
        document.addEventListener('click', closeHandler);
    }, 100);
}
```

### Step 3: Define Prompts by Dashboard
```javascript
getQuickPromptsForDashboard(dashboardName) {
    // ✅ STRATEGIC PROMPTS (Generic - work for all dashboards)
    const strategicPrompts = [
        {
            icon: '🔬',
            name: 'Deep Insights Analysis',
            prompts: [
                `You are provided Xero financial data below including date range, SQL queries, and raw JSON data.

OBJECTIVE: Extract maximum insights using structured multi-domain analysis.

ANALYSIS FRAMEWORK:

STEP 1 - Multi-Perspective Analysis
→ Analyze from multiple business perspectives:
  • Financial health (cash flow, profitability, collection efficiency)
  • Operational performance (transaction volumes, processing times)
  • Strategic positioning (market trends, competitive dynamics)
  • Risk assessment (volatility, exposure, concentration)
  • Growth trajectory (momentum, acceleration, sustainability)

STEP 2 - Domain Identification & Deep Dive
→ Identify 3-5 major domains where significant patterns emerge
→ For each domain, perform additional analyses:
  • Calculate trend lines, growth rates, volatility metrics
  • Identify outliers, anomalies, and inflection points
  • Cross-reference patterns across domains to find correlations

STEP 3 - Insight Explanation & Reasoning
→ For each insight:
  • State the insight clearly
  • Explain the underlying data patterns
  • Describe business implications and impact
  • Rate confidence level (High/Medium/Low)
  • Identify caveats or limitations

STEP 4 - Follow-Up Actions & Tool Recommendations
→ Suggest specific follow-up analyses I can perform:
  • Additional SQL queries to drill deeper
  • Comparative analyses to validate findings
  • Predictive models to forecast trends
  • Risk scenarios to test resilience

DELIVERABLE: Comprehensive insight report with executive summary, detailed findings, and actionable next steps.`
            ]
        },
        {
            icon: '🚀',
            name: 'Actionable Strategy',
            prompts: [
                `You are provided Xero financial data below including date range, SQL queries, and raw data.

OBJECTIVE: Develop prioritized action plan that maximizes business performance.

STRATEGIC FRAMEWORK:

STEP 1 - Opportunity & Challenge Identification
→ Identify:
  • High-impact opportunities (quick wins, strategic moves)
  • Critical challenges (risks, bottlenecks, inefficiencies)
  • Hidden patterns (emerging trends, subtle signals)
→ Quantify potential impact (Revenue, Cost, Risk, Time)

STEP 2 - Prioritization Using Weighted Shortest Job First (WSJF)
→ For each opportunity/challenge, calculate:
  • Business Value (1-10): Revenue impact, cost savings, risk reduction
  • Time Criticality (1-10): Urgency, seasonal factors, competitive pressure
  • Risk Reduction (1-10): Mitigates major risks, improves stability
  • Implementation Effort (1-10): Time, resources, complexity
  • WSJF Score = (Business Value + Time Criticality + Risk Reduction) / Implementation Effort
→ Rank by WSJF score (highest priority first)

STEP 3 - Analysis & Reasoning
→ For top 5 prioritized items, explain:
  • Why this action matters (strategic rationale)
  • Expected outcomes (quantified when possible)
  • Dependencies and prerequisites
  • Risks and mitigation strategies
  • Timeline and resource requirements

STEP 4 - Step-by-Step Implementation Plan
→ Create detailed action plan:
  • Phase 1 (0-30 days): Immediate actions, quick wins
  • Phase 2 (30-90 days): Strategic initiatives, capacity building
  • Phase 3 (90+ days): Long-term improvements, optimization
→ For each phase: tasks, deliverables, success metrics, review checkpoints

STEP 5 - Follow-Up Tool Recommendations
→ Suggest analyses to monitor progress and measure ROI

DELIVERABLE: Prioritized action plan with WSJF scores, implementation roadmap, and monitoring framework.`
            ]
        },
        {
            icon: '📊',
            name: 'Historical Comparison',
            prompts: [
                `You are provided Xero financial data with historical time series information.

OBJECTIVE: Perform comprehensive temporal analysis to identify trends, patterns, and strategic implications.

COMPARISON FRAMEWORK:

STEP 1 - Temporal Analysis Dimensions
→ Analyze across multiple time comparisons:
  • Year-over-Year (YoY): Compare to same period last year
  • Month-over-Month (MoM): Sequential period progression
  • Quarter-over-Quarter (QoQ): Quarterly trend analysis
  • Same Time Last Year (STLY): Direct period matching
  • Multi-Year Trends: 3-5 year historical patterns
  • Seasonal Adjustments: Remove seasonal effects

STEP 2 - Trend Identification & Classification
→ For each metric, identify:
  • Direction: Growing, declining, stable, volatile
  • Magnitude: Percentage change, absolute change, rate of change
  • Acceleration: Is trend speeding up or slowing down?
  • Cyclicality: Repeating patterns, seasonal cycles
  • Anomalies: Unusual spikes, dips, disruptions
→ Classify as: Structural, Cyclical, Seasonal, or Random

STEP 3 - Causal Analysis & Context
→ Investigate:
  • What business events explain this pattern?
  • External factors (economy, seasonality, competition)?
  • Do multiple metrics confirm the same story?
  • Are there leading indicators?

STEP 4 - Projection & Scenario Planning
→ Based on historical patterns:
  • Project forward 3-6 months
  • Develop 3 scenarios: Optimistic, Base Case, Pessimistic
  • Identify trigger points that would shift scenarios
  • Recommend monitoring metrics

STEP 5 - Strategic Implications
→ Answer:
  • What do trends mean for business strategy?
  • Should we accelerate, maintain, or pivot?
  • What resources should we allocate?
  • What risks do trends expose?

DELIVERABLE: Historical trend report with YoY/MoM/QoQ analysis, projections, and strategic recommendations.`
            ]
        },
        {
            icon: '💡',
            name: 'Key Insights & Executive Summary',
            prompts: [
                `You are provided Xero financial data below.

OBJECTIVE: Distill complex data into clear, actionable insights for executive decision-making.

SYNTHESIS FRAMEWORK:

STEP 1 - Data Comprehension
→ Understand:
  • What metrics are included and their meanings
  • Time periods covered and data granularity
  • Data quality and completeness
→ Identify the 5-7 most important metrics

STEP 2 - Pattern Recognition
→ Look for:
  • Standout numbers (exceptional performance or concerns)
  • Surprising findings (unexpected patterns)
  • Hidden relationships (correlations between metrics)
  • Missing context (what's not shown but matters)

STEP 3 - Key Insights Extraction (Top 5)
→ For each insight:
  • ONE-SENTENCE SUMMARY: Core finding in plain language
  • SUPPORTING DATA: Specific numbers proving this insight
  • SO WHAT?: Why this matters to the business
  • CONFIDENCE LEVEL: High/Medium/Low with justification
→ Rank by business impact

STEP 4 - Executive Explanation
→ Explain the data story in 3 parts:
  • WHERE WE ARE: Current state summary (2-3 sentences)
  • HOW WE GOT HERE: Key drivers and trends (2-3 sentences)
  • WHERE WE'RE HEADING: Trajectory and implications (2-3 sentences)
→ Use business language, not technical jargon

STEP 5 - Recommendations Summary
→ Provide 3-5 concrete recommendations with expected impact, effort, and priority

DELIVERABLE: Executive summary with top 5 insights, data story narrative, and prioritized recommendations.`
            ]
        },
        {
            icon: '⚡',
            name: 'Next Action Steps (Tactical)',
            prompts: [
                `You are provided Xero financial data below.

OBJECTIVE: Identify immediate tactical actions executable in the next 7-30 days.

TACTICAL FRAMEWORK:

STEP 1 - Quick Wins Identification
→ Find opportunities that are:
  • HIGH IMPACT: Meaningful improvement to key metrics
  • LOW EFFORT: Can be done quickly with existing resources
  • LOW RISK: Minimal downside
→ Look for process inefficiencies, low-hanging fruit, immediate risks

STEP 2 - Action Categorization
→ Group into:
  • COLLECTIONS: Improve cash flow (chase invoices, review terms)
  • EFFICIENCY: Process improvements (automate, streamline)
  • REVENUE: Quick revenue opportunities (upsell, cross-sell, pricing)
  • COST: Immediate cost reductions (renegotiate, eliminate)
  • RISK: Urgent risk mitigation (address exposures)
→ List 2-3 specific actions per category

STEP 3 - Action Specification
→ For each action:
  • WHAT: Specific task (be precise)
  • WHO: Role or person to do it
  • WHEN: Deadline or timeframe
  • HOW: Brief method or approach
  • WHY: Expected outcome (quantified if possible)
  • MEASURE: How to track success

STEP 4 - Priority Sequence
→ Organize:
  • THIS WEEK (Next 7 days): 2-3 urgent actions
  • NEXT TWO WEEKS (8-14 days): 3-5 important actions
  • THIS MONTH (15-30 days): 5-7 valuable actions

STEP 5 - Follow-Up Analysis
→ Suggest analyses to monitor progress and measure impact

DELIVERABLE: Tactical action plan with prioritized sequence, clear ownership, and success metrics.`
            ]
        },
        {
            icon: '🎯',
            name: 'Data Explanation & Context',
            prompts: [
                `You are provided Xero financial data below.

OBJECTIVE: Explain what this data shows in clear business language, providing context and meaning.

EXPLANATION FRAMEWORK:

STEP 1 - Data Overview
→ Describe:
  • What type of financial data is this?
  • What time period does it cover?
  • What businesses or entities are included?
  • How was this data collected?

STEP 2 - Metric Definitions
→ For each key metric:
  • Define in simple terms
  • Explain how it's calculated
  • Describe what "good" looks like
  • Note industry benchmarks
→ Use analogies or examples

STEP 3 - Current State Explanation
→ Describe what numbers tell us:
  • Headline figures (specific numbers)
  • Are these good, bad, or neutral?
  • How do they compare to expectations?
  • What patterns or trends are visible?
→ Explain for non-financial audience

STEP 4 - Business Context
→ Put in business context:
  • What business activities do these numbers represent?
  • What external factors might be influencing results?
  • What internal decisions are reflected here?
  • What does this tell us about business health?

STEP 5 - Next Steps Guidance
→ Guide user:
  • What questions should they ask?
  • What additional analysis would help?
  • Who should see this data and why?
  • What decisions can be informed?

DELIVERABLE: Plain-language explanation with context, definitions, and guidance for next steps.`
            ]
        }
    ];

    const promptsMap = {
        'Business Comparison': [
            ...strategicPrompts, // ✅ Include strategic prompts first
            {
                icon: '📊',
                name: 'Growth & Trends',
                prompts: [
                    'Compare year-over-year growth trends across all businesses',
                    'Identify businesses with declining market share',
                    'Which business is growing fastest and why?',
                    'Analyze revenue acceleration or deceleration patterns'
                ]
            },
            {
                icon: '💰',
                name: 'Financial Health',
                prompts: [
                    'Which business has the best collection days and why?',
                    'Analyze average order value trends by business',
                    'Identify businesses with concerning cash flow patterns',
                    'Compare payment terms efficiency across businesses'
                ]
            },
            {
                icon: '🎯',
                name: 'Recommendations',
                prompts: [
                    'Which business needs immediate attention or intervention?',
                    'Suggest resource allocation strategy based on performance',
                    'Recommend marketing budget distribution across businesses',
                    'Identify cross-selling opportunities between businesses'
                ]
            }
        ],
        'Consolidated Revenue': [
            ...strategicPrompts, // ✅ Include strategic prompts first
            {
                icon: '💵',
                name: 'Cash Flow Analysis',
                prompts: [
                    'Analyze cash flow health based on aging buckets',
                    'Which aging bucket is most concerning and why?',
                    'Project cash flow for next 30/60/90 days',
                    'Identify collection risk factors in outstanding amounts'
                ]
            },
            {
                icon: '📈',
                name: 'Revenue Trends',
                prompts: [
                    'Which business contributes most to total revenue?',
                    'Analyze month-over-month consolidated revenue trends',
                    'Identify seasonal patterns in consolidated data',
                    'Compare actual vs. expected collection timelines'
                ]
            },
            {
                icon: '⚠️',
                name: 'Risk Assessment',
                prompts: [
                    'Which outstanding invoices need immediate attention?',
                    'Analyze bad debt risk in 90+ day bucket',
                    'Recommend collection strategy priorities',
                    'Identify businesses with improving/declining collection rates'
                ]
            }
        ],
        'Seasonality': [
            ...strategicPrompts, // ✅ Include strategic prompts first
            {
                icon: '📅',
                name: 'Seasonal Patterns',
                prompts: [
                    'Which months are peak season for this business?',
                    'What are the historically slow periods?',
                    'Compare this year\'s performance to 3-year average',
                    'Identify emerging seasonal trend changes'
                ]
            },
            {
                icon: '🎯',
                name: 'Marketing Strategy',
                prompts: [
                    'When should we launch marketing campaigns?',
                    'Recommend inventory planning based on seasonality',
                    'Which months need promotional support?',
                    'Suggest staffing adjustments for peak periods'
                ]
            },
            {
                icon: '🔮',
                name: 'Forecasting',
                prompts: [
                    'Forecast Q1 performance based on seasonal patterns',
                    'Project holiday season revenue using historical data',
                    'Identify unusual deviations from seasonal norms',
                    'Recommend budget allocation by season'
                ]
            }
        ],
        'Forecast': [
            ...strategicPrompts, // ✅ Include strategic prompts first
            {
                icon: '📊',
                name: 'Scenario Analysis',
                prompts: [
                    'Should I budget based on optimistic or pessimistic scenario?',
                    'What are the biggest risks to this forecast?',
                    'How confident should I be in the 6-month projection?',
                    'Analyze volatility factors affecting accuracy'
                ]
            },
            {
                icon: '🎯',
                name: 'Risk Factors',
                prompts: [
                    'Which external factors pose greatest risk to forecast?',
                    'Identify controllable vs. uncontrollable risk factors',
                    'Recommend risk mitigation strategies',
                    'What early warning indicators should I monitor?'
                ]
            },
            {
                icon: '💼',
                name: 'Business Planning',
                prompts: [
                    'Create quarterly targets based on this forecast',
                    'Recommend expense budget aligned with projections',
                    'Identify growth investment opportunities',
                    'Suggest contingency plans for downside scenarios'
                ]
            }
        ]
    };

    return promptsMap[dashboardName] || [];
}
```

### Step 4: Export with Selected Prompt
```javascript
async exportWithPrompt(dashboardName, selectedPrompt, containerId) {
    // Get the dashboard's data export function
    let data = null;
    let endpoint = '';

    switch(dashboardName) {
        case 'Business Comparison':
            data = this.lastBusinessComparisonData;
            endpoint = '/api/xero/business-comparison';
            break;
        case 'Consolidated Revenue':
            data = this.lastConsolidatedRevenueData;
            endpoint = '/api/xero/consolidated-revenue';
            break;
        case 'Seasonality':
            data = this.lastSeasonalityData;
            endpoint = '/api/xero/seasonality';
            break;
        case 'Forecast':
            data = this.lastForecastData;
            endpoint = '/api/xero/forecast';
            break;
    }

    if (!data) {
        alert('No data available. Please wait for dashboard to load.');
        return;
    }

    // Format data for AI (reuse existing method)
    const formattedData = this.formatDataForAI(data, dashboardName, endpoint);

    // Add selected prompt at the beginning
    const exportContent = `# 🎯 AI Analysis Request

## User Question
${selectedPrompt}

---

${formattedData}`;

    // Copy to clipboard
    try {
        await navigator.clipboard.writeText(exportContent);
        
        // Show success notification
        this.showExportSuccessNotification(containerId, selectedPrompt);
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        alert('Failed to copy to clipboard. Please try again.');
    }
}

showExportSuccessNotification(containerId, prompt) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: absolute;
        top: 60px;
        right: 16px;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
        z-index: 1000;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;

    notification.innerHTML = `
        <div style="display: flex; align-items: start; gap: 10px;">
            <i class="fas fa-check-circle" style="font-size: 20px; flex-shrink: 0;"></i>
            <div>
                <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px;">
                    Copied to Clipboard!
                </div>
                <div style="font-size: 11px; opacity: 0.9; line-height: 1.3;">
                    Dashboard data + prompt ready to paste into AI chat
                </div>
                <div style="font-size: 10px; opacity: 0.7; margin-top: 4px; font-style: italic;">
                    "${prompt.substring(0, 60)}${prompt.length > 60 ? '...' : ''}"
                </div>
            </div>
        </div>
    `;

    container.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
```

---

## Integration Points

### Initialize in Each Dashboard Method
```javascript
// In showBusinessComparison()
this.createQuickPromptsButton('businessComparisonContent', 'Business Comparison');

// In showConsolidatedRevenue()
this.createQuickPromptsButton('consolidatedRevenueContent', 'Consolidated Revenue');

// In showSeasonality()
this.createQuickPromptsButton('seasonalityContent', 'Seasonality');

// In showForecast()
this.createQuickPromptsButton('forecastContent', 'Forecast');
```

---

## CSS Animations (Add to xero.js or global styles)
```css
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}
```

---

## Benefits Over Basic Export

### **Before (Basic Export):**
1. User clicks "Export for AI"
2. Dashboard data copied to clipboard
3. User pastes into AI chat
4. User types their question manually (often too vague or narrow)
5. AI analyzes with limited guidance

### **After (Quick Prompts with Strategic Frameworks):**
1. User clicks "Quick Prompts"
2. Sees two types of prompts:
   - **🎯 STRATEGIC PROMPTS** (6 powerful frameworks that work for any dashboard)
     - Deep Insights Analysis (multi-domain, step-by-step)
     - Actionable Strategy (WSJF prioritization, implementation plan)
     - Historical Comparison (YoY, MoM, QoQ, STLY with projections)
     - Key Insights & Executive Summary (distilled, decision-ready)
     - Next Action Steps (tactical, 7-30 day actions)
     - Data Explanation & Context (plain-language, non-technical)
   - **📊 DASHBOARD-SPECIFIC PROMPTS** (3-4 categories per dashboard)
3. Clicks a strategic prompt (e.g., "Deep Insights Analysis")
4. Data + **structured multi-step framework** copied to clipboard
5. User pastes into AI chat → **Question already asked with complete methodology!**
6. AI follows the framework step-by-step, providing comprehensive analysis

**Time saved:** 2-5 minutes per analysis (thinking + typing)  
**Quality improvement:** Expert-designed frameworks with proven methodologies  
**Consistency:** Every analysis follows structured approach (WSJF, multi-domain, etc.)  
**Discovery:** Users see advanced analytical techniques they didn't know existed  
**Depth:** Strategic prompts go far deeper than basic questions  

### **Power of Strategic Prompts:**

**Deep Insights Analysis** gives you:
- Multi-perspective analysis (financial, operational, strategic, risk, growth)
- Domain identification with statistical deep dives
- Confidence-rated insights with reasoning
- Follow-up action recommendations

**Actionable Strategy** gives you:
- WSJF prioritization (Business Value, Time Criticality, Risk Reduction / Effort)
- Phased implementation plan (0-30, 30-90, 90+ days)
- Quantified impact estimates
- Resource requirements and success metrics

**Historical Comparison** gives you:
- YoY, MoM, QoQ, STLY analysis automatically
- Trend classification (Structural, Cyclical, Seasonal, Random)
- 3-scenario projections (Optimistic, Base, Pessimistic)
- Trigger points and monitoring metrics

**Key Insights & Executive Summary** gives you:
- Top 5 insights ranked by business impact
- "WHERE WE ARE / HOW WE GOT HERE / WHERE WE'RE HEADING" narrative
- Confidence levels for each insight
- Executive recommendations with effort estimates

**Next Action Steps** gives you:
- Categorized tactical actions (Collections, Efficiency, Revenue, Cost, Risk)
- Time-sequenced plan (This Week, Next Two Weeks, This Month)
- Clear ownership and deadlines
- Success measurement criteria

**Data Explanation & Context** gives you:
- Plain-language definitions of every metric
- Business context for the numbers
- Guidance on what questions to ask
- Non-technical explanation for stakeholders

---

## User Experience Flow

```
XERO DASHBOARD
     ↓
[🎯 Quick Prompts ▼] ← Click
     ↓
DROPDOWN OPENS
 📊 Growth & Trends
   → "Compare YoY growth trends..."
   → "Identify declining businesses..."
 💰 Financial Health
   → "Best collection days..."
 🎯 Recommendations
   → "Which business needs attention..."
 ✨ Custom Prompt
   → [Textarea for custom question]
     ↓
USER CLICKS PROMPT
     ↓
CLIPBOARD CONTAINS:
 🎯 User Question: "Compare YoY growth trends..."
 📊 Dashboard Data: {...}
 📝 SQL Queries: {...}
 🤖 AI Instructions: {...}
     ↓
USER PASTES INTO AI CHAT
     ↓
AI IMMEDIATELY ANALYZES
(No need to type question!)
```

---

## Next Steps

1. ✅ **Review this design document**
2. ⏳ **Implement Quick Prompts button** (createQuickPromptsButton)
3. ⏳ **Implement dropdown UI** (showQuickPromptsDropdown)
4. ⏳ **Add prompt definitions** (getQuickPromptsForDashboard)
5. ⏳ **Implement export with prompt** (exportWithPrompt)
6. ⏳ **Add to all 4 dashboards**
7. ⏳ **Test end-to-end flow**
8. ⏳ **Create user documentation**

---

## Notes

- **Positioning:** Quick Prompts button appears **left** of Export button (right: 160px)
- **Styling:** Matches existing purple gradient theme (#8957e5 → #9b6df7)
- **Dropdown:** Max height 600px with scroll, dark theme (#1a1a1a background)
- **Prompt Count:** 9-12 prompts per dashboard across 3 categories
- **Custom Option:** Always available for user-written questions
- **Notification:** Green success message shows for 3 seconds after copy
- **Clipboard Format:** User question at top, then full dashboard export

---

**End of Design Document**
