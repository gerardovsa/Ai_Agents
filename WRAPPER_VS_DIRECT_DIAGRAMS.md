```mermaid
flowchart TB
    subgraph "AI Agent Layer"
        AI[AI Agent Request]
    end
    
    subgraph "Two Approaches"
        direction LR
        WRAPPER[Wrapper Approach<br/>inhouse_calculate_quote]
        DIRECT[Direct Approach<br/>calculate_business_cards]
    end
    
    subgraph "Wrapper Flow - BROKEN for GOD"
        W1[inhouse_wrapper.py<br/>inhouse_calculate_quote]
        W2{Parameter<br/>Translation?}
        W3[calculator_wrapper.py<br/>calculate_flyers]
        W4[GOD Calculator]
        W5[❌ ERROR<br/>Missing Args]
        
        W1 --> W2
        W2 -->|"NO - passes as-is"| W3
        W3 -->|"Expects width/height/gsm"| W4
        W4 --> W5
    end
    
    subgraph "Wrapper Flow - WORKS for Shopify"
        S1[inhouse_wrapper.py<br/>inhouse_calculate_quote]
        S2[calculator_wrapper.py<br/>calculate_business_cards]
        S3{Parameter<br/>Translation}
        S4[Shopify Calculator]
        S5[✅ SUCCESS<br/>$125.45]
        S6[⚠️ Double GST<br/>21% tax]
        
        S1 --> S2
        S2 --> S3
        S3 -->|"YES - translates params"| S4
        S4 --> S5
        S5 -.-> S6
    end
    
    subgraph "Direct Flow - WORKS PERFECTLY"
        D1[Registry V3<br/>Direct Tool Call]
        D2[calculate_flyers]
        D3[GOD Calculator]
        D4[✅ SUCCESS<br/>$397.73]
        
        D1 --> D2
        D2 -->|"Raw parameters"| D3
        D3 --> D4
    end
    
    AI -->|"Wrapper"| WRAPPER
    AI -->|"Direct"| DIRECT
    
    WRAPPER -->|"GOD Calculators"| W1
    WRAPPER -->|"Shopify Calculators"| S1
    DIRECT --> D1
    
    style W5 fill:#ffcccc
    style S6 fill:#ffffcc
    style D4 fill:#ccffcc
    style S5 fill:#ccffcc
```

## Key Findings Visualization

### Business Cards Pricing Breakdown

```mermaid
graph TD
    subgraph "Wrapper Approach - WooCommerce"
        WA[Subtotal: $87.56]
        WB[Profit 120%: +$47.76]
        WC[GST 10%: +$8.76]
        WD[Total: $96.32]
        
        WA --> WB --> WC --> WD
    end
    
    subgraph "Direct Approach - Shopify"
        DA[Subtotal: $103.68]
        DB[Profit 60%: +$38.88]
        DC[First GST 10%: +$10.37]
        DD[Second GST 10%: +$11.40]
        DE[Total: $125.45]
        
        DA --> DB --> DC --> DD --> DE
    end
    
    WD -.->|"$29.13 difference"| DE
    
    style DE fill:#ffcccc
    style DD fill:#ffcccc
    style WD fill:#ccffcc
```

### Parameter Translation Issue

```mermaid
sequenceDiagram
    participant AI as AI Agent
    participant Wrapper as inhouse_calculate_quote
    participant Translator as Parameter Translator
    participant Calc as GOD Calculator
    
    AI->>Wrapper: size="A5", stock="150gsm"
    
    rect rgb(255, 200, 200)
        Note over Wrapper,Translator: Missing Translation Layer
        Wrapper->>Calc: size="A5", stock="150gsm"
        Calc-->>Wrapper: ❌ Missing width, height, gsm
    end
    
    Wrapper-->>AI: Error: Missing arguments
    
    Note over AI: Workaround: Call direct
    
    AI->>Calc: width=148, height=210, gsm=150
    Calc-->>AI: ✅ SUCCESS: $397.73
```

### Celloglaze Bug Flow

```mermaid
graph LR
    A[AI: celloglaze='none'] --> B{String Check}
    B -->|"None" in celloglaze| C[✅ cello_cost = $0]
    B -->|"none" in celloglaze| D[❌ Falls to else]
    D --> E[cello_cost = $8]
    
    style C fill:#ccffcc
    style E fill:#ffcccc
```

## Calculator System Architecture

```mermaid
graph TB
    subgraph "Calculator Types"
        direction LR
        GOD[GOD Calculators<br/>Database-Driven]
        SHOP[Shopify Calculators<br/>Hardcoded Formula]
        WOO[WooCommerce Calculators<br/>DPO Formula]
    end
    
    subgraph "GOD Features"
        G1[Flyers]
        G2[Perfect Bound Books]
        G3[Booklets]
        G4[Letterheads]
        
        G1 -.-> GRES[Results: $397.73]
        G2 -.-> GRES
        G3 -.-> GRES
        G4 -.-> GRES
    end
    
    subgraph "Shopify Features"
        S1[Business Cards Premium]
        S2[Business Cards Economy]
        S3[Corflute Signs]
        S4[Wire Bound]
        
        S1 -.-> SRES[Results: $125.45<br/>⚠️ Double GST]
        S2 -.-> SRES
        S3 -.-> SRES
        S4 -.-> SRES
    end
    
    GOD --> G1
    GOD --> G2
    GOD --> G3
    GOD --> G4
    
    SHOP --> S1
    SHOP --> S2
    SHOP --> S3
    SHOP --> S4
    
    style GRES fill:#ccffcc
    style SRES fill:#ffffcc
```

## Issues Priority Matrix

```mermaid
quadrantChart
    title Calculator Issues by Impact and Effort
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    
    quadrant-1 Fix Immediately
    quadrant-2 Plan Carefully
    quadrant-3 Nice to Have
    quadrant-4 Quick Wins
    
    Celloglaze Bug: [0.1, 0.6]
    Parameter Translation: [0.6, 0.8]
    Double GST Decision: [0.3, 0.9]
    Integration Tests: [0.5, 0.4]
    Documentation: [0.3, 0.3]
```

## Recommended Fix Sequence

```mermaid
gantt
    title Calculator Fix Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Critical Fixes
    Fix Celloglaze Case Bug           :crit, fix1, 2026-01-03, 1d
    Add Parameter Translation Layer    :crit, fix2, 2026-01-03, 2d
    
    section Business Decision
    Review Double GST Strategy         :active, review, 2026-01-03, 3d
    Implement GST Decision             : impl, after review, 1d
    
    section Quality Assurance
    Add Integration Tests              : test, after fix2, 1d
    Update Documentation               : docs, after test, 1d
    
    section Deployment
    Deploy to Staging                  : stage, after docs, 1d
    Production Deployment              : prod, after stage, 1d
```
