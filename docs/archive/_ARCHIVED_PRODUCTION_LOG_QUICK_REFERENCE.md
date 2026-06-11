# Production Log - Quick Reference Card

## What is it?
Comprehensive tracking system for job progress with automatic stage logging and manual entries.

## Entry Types

### 1. Stage Change (Automatic ⚡)
**When**: Job dragged between Kanban columns  
**Logs**: From stage → To stage, timestamp, user initials  
**Example**: `[2025-11-07] [14:30] [JD] Moved: Design → Press`

### 2. Manual Note 📝
**When**: Team member adds observation  
**Fields**: Initials, note text  
**Example**: `[14:35] [SM] Client approved proof via email`

### 3. Wastage ⚠️
**When**: Materials wasted during production  
**Fields**: Amount, unit, type, reason  
**Example**: `[15:20] [TK] Wastage: 50 sheets (paper) - Color calibration`

### 4. Delay ⏱️
**When**: Production stopped/delayed  
**Fields**: Hours, reason, resolved status  
**Example**: `[16:10] [SM] Delay: 2.5h - Press 2 maintenance`

### 5. Stock Change 📦
**When**: Stock added or used  
**Fields**: Item, quantity (+/-), reason  
**Example**: `[10:00] [JD] Stock: Card stock +500 sheets - New delivery`

### 6. Client Notification 📧
**When**: Contacting client  
**Fields**: Type (email/SMS/phone/WhatsApp), recipient, message  
**Example**: `[14:45] [JD] Email to client@example.com: "Order ready for pickup"`

## Display Format

```
[Date]       [Time]    [Init] [Type]                [Content]
2025-11-07   14:30:15  JD     stage_change          Design → Press
2025-11-07   14:35:22  SM     note                  Client approved proof
2025-11-07   15:20:10  TK     wastage               50 sheets - Color calibration
2025-11-07   16:10:05  SM     delay                 2.5h - Equipment failure
2025-11-07   16:45:00  JD     client_notification   Email sent: Order ready
```

## API Quick Reference

```bash
# Get all logs for job
GET /api/production-log/12345

# Add manual note
POST /api/production-log/12345
{
  "user_initials": "JD",
  "entry_type": "note",
  "note_text": "Client requested changes"
}

# Log wastage
POST /api/production-log/12345
{
  "user_initials": "SM",
  "entry_type": "wastage",
  "wastage_amount": 50,
  "wastage_unit": "sheets",
  "wastage_type": "paper",
  "wastage_reason": "Color calibration",
  "note_text": "Wastage: 50 sheets for tests"
}

# Log delay
POST /api/production-log/12345
{
  "user_initials": "TK",
  "entry_type": "delay",
  "delay_hours": 2.5,
  "delay_reason": "equipment_failure",
  "note_text": "Press 2 maintenance"
}

# Log client notification
POST /api/production-log/12345/notification
{
  "user_initials": "JD",
  "notification_type": "email",
  "notification_recipient": "client@example.com",
  "notification_subject": "Order ready",
  "notification_message": "Your business cards are ready for pickup",
  "notification_status": "sent"
}

# Get summary stats
GET /api/production-log/12345/summary
```

## Notification Types

| Type | Description | Use Case |
|------|-------------|----------|
| `email` | Email notification | Proof approval, order ready |
| `sms` | SMS/Text message | Urgent updates, pickup reminders |
| `phone` | Phone call | Complex issues, high-priority |
| `whatsapp` | WhatsApp message | Quick updates, photos |
| `client_portal` | Portal notification | Self-service updates |

## Wastage Reasons

- `color_calibration` - Test prints for color matching
- `equipment_issue` - Machine malfunction
- `material_defect` - Stock quality problems
- `operator_error` - Human mistakes
- `rework` - Client changes/corrections
- `setup` - Setup/calibration waste

## Delay Reasons

- `equipment_failure` - Machine breakdown
- `material_shortage` - Waiting for stock
- `rework` - Quality issues requiring redo
- `client_changes` - Client modifications
- `other` - Other reasons (specify in note)

## Color Coding

- 🔵 **Blue** = Stage change (automatic)
- 📝 **White** = Manual note
- ⚠️ **Yellow** = Wastage
- 🔴 **Red** = Delay
- 📦 **Gray** = Stock change
- 📧 **Green** = Client notification

## Benefits

1. **Complete Audit Trail** - Know exactly what happened and when
2. **Wastage Tracking** - Identify patterns, reduce costs
3. **Delay Analysis** - Find bottlenecks, improve workflows
4. **Client Communication** - Track all client interactions
5. **Team Accountability** - See who did what (via initials)

## Access

- **Web**: Job details modal → "Production Log" tab
- **API**: `http://localhost:5001/api/production-log/`
- **Database**: SQLite `data/kanban_analytics.db` → `production_log` table

## Support

**Questions?** Check `PRODUCTION_LOG_SYSTEM_COMPLETE.md` for full documentation.

---

**Version**: 1.0.0  
**Last Updated**: November 7, 2025
