# 🗄️ InHouse Kanban - Database Field Reference

**Quick reference for developers working on the InHouse Kanban module**

---

## ✅ CORRECT Field Names (Use These!)

### **Job Identification:**
```javascript
job.TicketID     // int - Job ticket ID (PRIMARY)
job.OrderID      // int - Order ID (links to Orders table)
```

### **Client Information:**
```javascript
job.ClientName   // string - Customer name (from Orders table)
```

### **Job Description:**
```javascript
job.ProductionNotes  // string - Full specs (TicketNotes) ⭐ PRIMARY
job.ShortJobDesc     // string - Brief description (fallback)
```

### **Product Details:**
```javascript
job.QTY          // int - Quantity (note: uppercase QTY!)
job.JobType      // string - "Business Cards", "Stickers", etc.
job.PaperType    // string - "Satin", "Vinyl Sticker", etc.
job.GSM          // string - "350GSM", "Standard", etc.
job.PaperSize    // string - "A4", "Custom", etc.
job.BindType     // string - "Spiral Bound", null, etc.
```

### **Financial:**
```javascript
job.Cost         // decimal - Per-ticket cost (not order total!)
```

### **Dates & Timing:**
```javascript
job.OrderDate        // date - Order creation date (from Orders)
job.DateRequired     // date - Customer deadline (from Orders)
job.DaysInSystem     // int - Calculated: DATEDIFF(OrderDate, NOW)
job.DaysUntilDue     // int - Calculated: DATEDIFF(NOW, DateRequired)
```

### **Status & Urgency:**
```javascript
job.Urgent           // bool - Urgent flag (from Orders table)
job.Invoiced         // bool - Has been invoiced (from Orders)
job.StageDescription // string - "Digital - 9110", "ArtOnly", etc.
job.UrgencyLevel     // string - "OVERDUE", "CRITICAL", "HIGH", etc.
```

### **Priority & Colors:**
```javascript
job.AIPriorityScore   // int - AI-calculated priority (0-999)
job.PriorityColorHex  // string - "#ef4444", "#22c55e", etc.
job.PriorityLabel     // string - "CRITICAL", "HIGH", "NORMAL", etc.
```

### **Customer Metrics:**
```javascript
job.CustomerOrderCount    // int - Orders in last 12 months
job.CustomerLifetimeValue // decimal - Total spent in last 12 months
job.CustomerTier          // string - "VIP", "Premium", "Regular", "New"
```

---

## ❌ Fields That DON'T EXIST (Never Use These!)

```javascript
// ❌ These columns do NOT exist in the database:
job.Status         // WRONG - Use job.Invoiced instead
job.TotalCost      // WRONG - Use job.Cost (per-ticket)
job.PrintType      // WRONG - Check job.ProductionNotes instead
job.DateCreated    // WRONG - Use job.OrderDate instead
job.ProductType    // WRONG - Use job.JobType instead
job.Quality        // WRONG - Use job.GSM instead
job.Qty            // WRONG - Use job.QTY (uppercase!)
```

---

## 🎨 Frontend Display Patterns

### **Card Description (Correct Priority):**
```javascript
// ✅ CORRECT - Primary source is ProductionNotes
const description = job.ProductionNotes || job.ShortJobDesc || 'No description available';
```

### **Product Information:**
```javascript
// ✅ CORRECT - Combine JobType and GSM
const productType = job.JobType || job.PaperType || 'N/A';
const quality = job.GSM || job.PaperSize || '';
const productInfo = quality ? `${productType} - ${quality}` : productType;

// Display: "Business Cards - 350GSM"
// Display: "Stickers - Custom"
```

### **Job Identifiers:**
```javascript
// ✅ CORRECT - Show BOTH IDs
<span class="card-tag">
    <i class="fas fa-ticket-alt"></i> Job: ${job.TicketID}
</span>
<span class="card-tag">
    <i class="fas fa-file-invoice"></i> Order: ${job.OrderID}
</span>
```

### **Time Tracking:**
```javascript
// ✅ CORRECT - Display both metrics
<span class="time-info">
    <i class="fas fa-hourglass-half"></i> ${job.DaysInSystem}d in system
</span>
<span class="stage-time">
    <i class="fas fa-clock"></i> ${stageTimeInfo.display}
</span>
```

---

## 🔍 Common Mistakes & Fixes

### **Mistake 1: Using Wrong Field Names**
```javascript
// ❌ WRONG
const desc = job.ProductType;
const quality = job.Quality;

// ✅ CORRECT
const desc = job.JobType;
const quality = job.GSM;
```

### **Mistake 2: Wrong Description Priority**
```javascript
// ❌ WRONG - ShortJobDesc often empty
const description = job.ShortJobDesc || 'No description';

// ✅ CORRECT - ProductionNotes is primary
const description = job.ProductionNotes || job.ShortJobDesc || 'No description available';
```

### **Mistake 3: Case Sensitivity**
```javascript
// ❌ WRONG - Lowercase
job.qty

// ✅ CORRECT - Uppercase
job.QTY
```

### **Mistake 4: Missing IDs**
```javascript
// ❌ WRONG - Only showing one ID
<span>Job: ${job.TicketID}</span>

// ✅ CORRECT - Show both
<span>Job: ${job.TicketID}</span>
<span>Order: ${job.OrderID}</span>
```

---

## 📊 Example Data Structure

```javascript
{
  // Identifiers
  "TicketID": 72090,
  "OrderID": 56230,
  
  // Client
  "ClientName": "Gerardo Poli",
  
  // Description
  "ProductionNotes": "Jack gloss stickers\n500 Individual Stickers...",
  "ShortJobDesc": "EVG Cover Stickers",
  
  // Product Details
  "QTY": 500,
  "JobType": "Stickers - Digital Print",
  "PaperType": null,
  "GSM": null,
  "PaperSize": "Custom",
  "BindType": null,
  
  // Financial
  "Cost": 189.00,
  
  // Dates
  "OrderDate": "2025-08-28",
  "DateRequired": "2025-08-28",
  "DaysInSystem": 95,
  "DaysUntilDue": -95,
  
  // Status
  "Urgent": true,
  "Invoiced": true,
  "StageDescription": "JobComplete",
  "UrgencyLevel": "OVERDUE",
  
  // Priority
  "AIPriorityScore": 850,
  "PriorityColorHex": "#ef4444",
  "PriorityLabel": "CRITICAL",
  
  // Customer
  "CustomerOrderCount": 12,
  "CustomerLifetimeValue": 5420.50,
  "CustomerTier": "Premium"
}
```

---

## 🎯 Quick Checklist

When working with job data, verify:

- [ ] Using `ProductionNotes` (not just `ShortJobDesc`)
- [ ] Using `JobType` (not `ProductType`)
- [ ] Using `GSM` (not `Quality`)
- [ ] Using `QTY` uppercase (not `Qty`)
- [ ] Showing both `TicketID` and `OrderID`
- [ ] Using `Invoiced` (not `Status`)
- [ ] Using `Cost` per-ticket (not `TotalCost`)
- [ ] Getting dates from Orders table (`OrderDate`, `DateRequired`)

---

## 📚 Related Documentation

- **Full Database Schema:** `FRED_DATABASE_SCHEMA_ACTUAL.md`
- **API Reference:** `AI_infrastructure/routes/FRED_DATABASE_COMPLETE_REFERENCE.md`
- **V10 Fix Summary:** `V10_CARD_FIX_COMPLETE.md`

---

**Last Updated:** December 1, 2025  
**Version:** V10  
**Status:** ✅ PRODUCTION VERIFIED
