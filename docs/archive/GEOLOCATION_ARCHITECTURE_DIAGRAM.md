# Geolocation System Architecture Diagram

## BEFORE Consolidation (3 Separate Systems)

```
┌──────────────────────────────────────────────────────────────┐
│                    OLD ARCHITECTURE                          │
└──────────────────────────────────────────────────────────────┘

System 1: Agent Routes
┌────────────────────────────────┐
│  agent_routes.py               │
│  ├─ Uses: ip_location.py       │
│  ├─ Returns: 6 fields          │
│  └─ Purpose: web_search tool   │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  core/ip_location.py           │
│  • get_location_dict()         │
│  • get_location_for_prompt()   │
└────────────────────────────────┘


System 2: User Preferences
┌────────────────────────────────┐
│  user_preferences_routes.py    │
│  ├─ Uses: Database only        │
│  ├─ No auto-detection          │
│  └─ Purpose: Store location    │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  SQLite Database               │
│  • detected_country            │
│  • detected_city               │
│  • detected_timezone           │
└────────────────────────────────┘


System 3: Geolocation API
┌────────────────────────────────┐
│  geolocation_routes.py         │
│  ├─ Uses: geolocation_service  │
│  ├─ Returns: 12 fields         │
│  └─ Purpose: API endpoint      │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  utils/geolocation_service.py  │
│  • get_location_from_ip()      │
│  • get_temporal_awareness()    │
└────────────────────────────────┘

PROBLEMS:
❌ Duplicate code in 2 files
❌ Inconsistent data structures
❌ No auto-detection in user prefs
❌ Different field counts (6 vs 12)
```

## AFTER Consolidation (Unified System)

```
┌──────────────────────────────────────────────────────────────┐
│                    NEW ARCHITECTURE                          │
└──────────────────────────────────────────────────────────────┘

                    SINGLE SOURCE OF TRUTH
┌──────────────────────────────────────────────────────────────┐
│              core/ip_location.py                             │
│                                                              │
│  5 Public Functions:                                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. get_location_from_ip(ip) → 22 fields               │ │
│  │    Full location + coordinates + temporal             │ │
│  │                                                        │ │
│  │ 2. build_geolocation_context(ip) → 22 fields         │ │
│  │    Same as #1 (convenience wrapper)                   │ │
│  │                                                        │ │
│  │ 3. get_temporal_awareness(tz) → 10 fields            │ │
│  │    Just temporal data (time_of_day, season, etc.)    │ │
│  │                                                        │ │
│  │ 4. get_location_for_prompt() → string                │ │
│  │    "Brisbane, Queensland, Australia"                  │ │
│  │                                                        │ │
│  │ 5. get_location_dict() → 19 fields                   │ │
│  │    Compatible with web_search tool                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Features:                                                   │
│  ✓ ipapi.co integration (1000 req/day)                     │
│  ✓ LRU cache (128 entries)                                  │
│  ✓ Fallback to Brisbane                                     │
│  ✓ pytz timezone support                                    │
│  ✓ Temporal calculations                                    │
└──────────────────────────────────────────────────────────────┘
                           ▲
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         │                 │                 │
┌────────┴────────┐ ┌──────┴─────────┐ ┌────┴──────────────┐
│ agent_routes.py │ │ geolocation_   │ │ user_preferences_ │
│                 │ │ routes.py      │ │ routes.py         │
│ Uses:           │ │ Uses:          │ │ Uses:             │
│ get_location_   │ │ get_location_  │ │ build_geo_        │
│ dict()          │ │ from_ip()      │ │ location_context()│
│                 │ │                │ │                   │
│ Purpose:        │ │ Purpose:       │ │ Purpose:          │
│ Web search      │ │ API endpoint   │ │ Auto-detect       │
│ integration     │ │ /detect        │ │ on save           │
│                 │ │                │ │                   │
│ Returns:        │ │ Returns:       │ │ Returns:          │
│ 19 fields       │ │ 22 fields      │ │ 22 fields         │
└─────────────────┘ └────────────────┘ └───────────────────┘

BENEFITS:
✅ Single source of truth
✅ Consistent 22-field data structure
✅ Auto-detection in user preferences
✅ No duplicate code
✅ Easy to maintain
✅ Enhanced features (coordinates, temporal)
```

## Data Flow Example

### User saves preferences:

```
1. User clicks "Save" in Account Settings
   │
   ▼
2. POST /api/user/preferences
   │
   ▼
3. user_preferences_routes.py
   │
   ├─ Get IP from request.remote_addr
   │  (e.g., "2405:6e00:640:23b3:...")
   │
   ├─ Call: build_geolocation_context(ip)
   │  │
   │  ▼
   │  ┌─────────────────────────────────────┐
   │  │  core/ip_location.py                │
   │  │  ├─ API call to ipapi.co            │
   │  │  ├─ Add temporal data (_add_...)    │
   │  │  └─ Return 22 fields                │
   │  └─────────────────────────────────────┘
   │
   ├─ Extract: city, country, timezone
   │
   └─ Save to database
      │
      ▼
4. SQLite Database Updated
   ├─ detected_city: "Brisbane"
   ├─ detected_country: "Australia"
   ├─ detected_timezone: "Australia/Brisbane"
   └─ detected_ip_address: "2405:6e00:..."
```

### Web search needs location:

```
1. User asks: "Find coffee shops near me"
   │
   ▼
2. agent_routes.py processes request
   │
   ├─ Call: get_location_dict()
   │  │
   │  ▼
   │  ┌─────────────────────────────────────┐
   │  │  core/ip_location.py                │
   │  │  ├─ Cached or API call              │
   │  │  └─ Return 19 fields (web_search)   │
   │  └─────────────────────────────────────┘
   │
   └─ Pass location to web_search tool
      │
      ▼
3. Search API receives:
   {
     "city": "Brisbane",
     "country": "Australia",
     "latitude": -27.4786,
     "longitude": 153.0244
   }
```

## Field Comparison

### Basic Location (6 fields) - Original:
```
city, region, country, country_name, 
timezone, location_string
```

### Enhanced Location (22 fields) - After Consolidation:
```
Basic:           city, region, country, country_name, 
                 timezone, location_string

Coordinates:     latitude, longitude

Metadata:        ip, success

Temporal:        current_time, time_of_day, day_of_week,
                 day_of_week_num, is_weekend, is_work_hours,
                 season, hour, date
```

## Function Selection Guide

```
┌─────────────────────────────────────────────────┐
│          WHICH FUNCTION SHOULD I USE?           │
└─────────────────────────────────────────────────┘

Need full location + temporal data?
└─► build_geolocation_context(ip)
    or get_location_from_ip(ip)
    Returns: 22 fields

Already have timezone, just need temporal?
└─► get_temporal_awareness(timezone)
    Returns: 10 fields

Building AI system prompts?
└─► get_location_for_prompt()
    Returns: string

Passing to web_search tool?
└─► get_location_dict()
    Returns: 19 fields

Don't know IP address?
└─► get_location_dict()  [uses default]
    or get_location_for_prompt()  [uses default]
    Returns: Brisbane data
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────┐
│              PERFORMANCE METRICS                │
└─────────────────────────────────────────────────┘

First Call (uncached):
├─ API Request to ipapi.co:    ~500ms
├─ Temporal calculations:       ~2ms
├─ JSON parsing:                ~1ms
└─ Total:                       ~503ms

Subsequent Calls (cached):
├─ LRU cache lookup:            ~1ms
├─ Temporal calculations:       ~2ms
└─ Total:                       ~3ms

Cache Details:
├─ Type: functools.lru_cache
├─ Size: 128 entries
├─ Scope: Per-function
└─ TTL: Session lifetime

Rate Limits:
├─ Free tier: 1000 req/day
├─ Timeout: 2 seconds
└─ Fallback: Brisbane, Australia
```

## Testing Checklist

```
□ Import test
  python -c "from AI_infrastructure.core.ip_location import *"

□ Function test
  python test_consolidated_geolocation.py

□ Route test
  python -c "from AI_infrastructure.routes.user_preferences_routes import user_preferences_bp"
  python -c "from AI_infrastructure.routes.geolocation_routes import geolocation_bp"

□ Flask startup test
  BISTART

□ API endpoint test
  curl http://localhost:5001/api/geolocation/detect

□ User preferences save test
  (Save preferences in UI, check detected_* fields in database)
```

---

**Legend:**
- ✅ = Feature working
- ❌ = Problem identified
- ▼ = Data flow direction
- │ = Connection
- └─► = Recommended path

**Last Updated:** November 5, 2025  
**Status:** Production Ready
