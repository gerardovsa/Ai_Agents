# IP Location Functions - Quick Reference

**Last Updated:** November 5, 2025  
**Status:** ✅ Production Ready

## Single Source of Truth

**File:** `AI_infrastructure/core/ip_location.py`

All location detection uses this file. Import from here.

## 5 Available Functions

### 1. `get_location_from_ip(ip_address: str) -> Dict`
**Returns:** 22 fields (coordinates + temporal data)

```python
from AI_infrastructure.core.ip_location import get_location_from_ip

location = get_location_from_ip('8.8.8.8')
# city, region, country, timezone, latitude, longitude, 
# time_of_day, season, is_work_hours, etc.
```

### 2. `build_geolocation_context(ip_address: str) -> Dict`
**Returns:** Same 22 fields (convenience wrapper)

```python
from AI_infrastructure.core.ip_location import build_geolocation_context

context = build_geolocation_context(request.remote_addr)
if context['success']:
    city = context['city']
```

### 3. `get_temporal_awareness(timezone: str) -> Dict`
**Returns:** 10 temporal fields (no location)

```python
from AI_infrastructure.core.ip_location import get_temporal_awareness

temporal = get_temporal_awareness('Australia/Brisbane')
# current_time, time_of_day, day_of_week, season, etc.
```

### 4. `get_location_for_prompt() -> str`
**Returns:** String for AI prompts

```python
from AI_infrastructure.core.ip_location import get_location_for_prompt

location_str = get_location_for_prompt()
# "Brisbane, Queensland, Australia"
```

### 5. `get_location_dict() -> Dict`
**Returns:** 19 fields for web_search tool

```python
from AI_infrastructure.core.ip_location import get_location_dict

location = get_location_dict()
# Compatible with web_search tool
```

## Data Structure (26 Fields)

```python
{
    # Basic (6 fields)
    'city': 'Brisbane',
    'region': 'Queensland', 
    'country': 'AU',
    'country_name': 'Australia',
    'timezone': 'Australia/Brisbane',
    'location_string': 'Brisbane, Queensland, Australia',
    
    # Coordinates (2 fields)
    'latitude': -27.4786,
    'longitude': 153.0244,
    
    # Metadata (2 fields)
    'ip': '2405:6e00:640:23b3:...',
    'success': True,
    
    # Temporal (12 fields)
    'current_time': '2025-11-06 23:45:00',
    'time_of_day': 'night',
    'day_of_week': 'Wednesday',
    'day_of_week_num': 2,
    'is_weekend': False,
    'is_work_hours': False,
    'season': 'Fall',
    'hour': 23,
    'date': '2025-11-06',
    
    # Weather (4 fields - NEW!)
    'temperature_c': 18.7,
    'temperature_f': 65.7,
    'weather_condition': 'Mainly clear',
    'weather_code': 1
}
```

## Usage by Route

| Route | Function Used | Purpose |
|-------|---------------|---------|
| agent_routes.py | `get_location_dict()` | Web search integration |
| geolocation_routes.py | `get_location_from_ip()` | API endpoint |
| user_preferences_routes.py | `build_geolocation_context()` | Auto-detect on save |

## Common Patterns

### Auto-detect location
```python
ip = request.remote_addr
geo = build_geolocation_context(ip)
if geo['success']:
    city = geo['city']
```

### Check work hours
```python
location = get_location_from_ip(ip)
if location['is_work_hours']:
    send_notification()
```

### Time-aware greeting
```python
location = get_location_from_ip(ip)
if location['time_of_day'] == 'morning':
    greeting = "Good morning"
```

### Weather-aware suggestions (NEW!)
```python
location = get_location_from_ip(ip)
temp = location.get('temperature_c')
if temp and temp > 30:
    advice = "It's hot! Stay hydrated"
elif temp and temp < 10:
    advice = "It's cold! Dress warmly"
```

## Quick Comparison

| Need | Use Function |
|------|--------------|
| Full details + weather | `get_location_from_ip()` or `build_geolocation_context()` |
| Just temporal | `get_temporal_awareness()` |
| AI prompts | `get_location_for_prompt()` |
| Web search | `get_location_dict()` |

## Testing

```powershell
# Test imports
python -c "from AI_infrastructure.core.ip_location import build_geolocation_context; print('OK')"

# Full test
python test_consolidated_geolocation.py

# Test temperature integration
python test_temperature_integration.py
```

## Migration

**Old (deprecated):**
```python
from AI_infrastructure.utils.geolocation_service import get_location_from_ip
```

**New (use this):**
```python
from AI_infrastructure.core.ip_location import get_location_from_ip
```

---

**TL;DR:** Import from `ip_location.py`, use `build_geolocation_context(ip)`, get 26 fields including temperature.

See full docs: `GEOLOCATION_CONSOLIDATION_COMPLETE.md`, `TEMPERATURE_INTEGRATION_COMPLETE.md`
