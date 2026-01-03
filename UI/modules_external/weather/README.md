# Weather Module

**Backend weather integration using Open-Meteo API with database caching**

## Features

- ✅ **IP-based auto-location** - Automatically detects user location
- ✅ **Database caching** - 1-hour cache in Supabase (minimizes API calls)
- ✅ **Free unlimited API** - No API key required (Open-Meteo)
- ✅ **Multiple endpoints** - Current, forecast, hourly, location search
- ✅ **Registry V3 integration** - Auto-discovered by tool registry

## Tools Available

### 1. `get_current_weather`
Get current weather conditions for any location.

**Parameters:**
- `latitude` (optional): Auto-detected from IP if not provided
- `longitude` (optional): Auto-detected from IP if not provided
- `location_name` (optional): Display name

**Returns:**
```json
{
  "success": true,
  "cached": false,
  "location": {
    "name": "Brisbane, Queensland, Australia",
    "latitude": -27.4786,
    "longitude": 153.0244
  },
  "current_weather": {
    "temperature_c": 28.5,
    "temperature_f": 83.3,
    "feels_like_c": 30.2,
    "humidity": 65,
    "precipitation_mm": 0,
    "wind_speed_kmh": 15,
    "wind_direction": 120,
    "pressure_hpa": 1013,
    "weather_code": 2,
    "weather_description": "Partly cloudy",
    "timestamp": "2025-12-29T14:00"
  }
}
```

### 2. `get_weather_forecast`
Get multi-day weather forecast (up to 16 days).

**Parameters:**
- `days` (optional): Number of days (default: 7, max: 16)
- `latitude`, `longitude`, `location_name` (optional)

**Returns:**
```json
{
  "success": true,
  "location": {...},
  "forecast": [
    {
      "date": "2025-12-29",
      "temperature_max_c": 32,
      "temperature_min_c": 24,
      "precipitation_mm": 0,
      "precipitation_probability": 10,
      "wind_speed_max_kmh": 20,
      "weather_description": "Partly cloudy",
      "sunrise": "2025-12-29T05:15:00",
      "sunset": "2025-12-29T18:45:00"
    }
  ]
}
```

### 3. `get_hourly_forecast`
Get hourly forecast (up to 168 hours / 7 days).

**Parameters:**
- `hours` (optional): Number of hours (default: 48, max: 168)

### 4. `search_location_weather`
Search weather by city name.

**Parameters:**
- `query` (required): City name or address (e.g., "New York, USA")

## Usage in Flask Routes

```python
from tools.registry_v3 import get_registry

registry = get_registry()

# Get current weather (auto-detected location)
weather = registry.execute_tool(tool_name='get_current_weather')

# Get weather for specific location
weather = registry.execute_tool(
    tool_name='get_current_weather',
    latitude=-27.4786,
    longitude=153.0244,
    location_name='Brisbane, Australia'
)

# Get 7-day forecast
forecast = registry.execute_tool(
    tool_name='get_weather_forecast',
    days=7
)
```

## Usage in Frontend

### Option 1: Direct Flask API Call
```javascript
// Get current weather
const response = await fetch('/api/weather/current');
const data = await response.json();
console.log(data.current_weather.temperature_c);

// Get forecast
const forecast = await fetch('/api/weather/forecast?days=5');
const forecastData = await forecast.json();
```

### Option 2: Use Weather Widget Fragment
```html
<!-- Include weather widget -->
<div id="weatherWidget" data-auto-init="true"></div>
<script src="/fragments/weather-widget.html"></script>

<script>
// Or manually initialize
WeatherWidget.init('weatherWidget', {
    autoRefresh: true,
    lat: -27.4786,  // optional
    lon: 153.0244   // optional
});
</script>
```

## Database Schema

The module auto-creates this table on first use:

```sql
CREATE TABLE IF NOT EXISTS weather_cache (
    location_key TEXT PRIMARY KEY,
    weather_data JSONB NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

**Cache Strategy:**
- Key: `{lat}_{lon}` rounded to 2 decimals (~1km resolution)
- TTL: 1 hour
- Automatic cleanup on read (expired entries ignored)

## Integration Points

### Where Weather Data Can Be Used

1. **Main Dashboard** (`UI/business-ai-platform-v2.html`)
   - Display weather widget in sidebar or header
   - AI agent sees weather in system prompt
   - Weather-aware recommendations

2. **Van Thermal Manager** (`MCP_Server/van-thermal-manager/renderer/unified-dashboard.html`)
   - Climate control optimization based on outside temperature
   - Solar power predictions based on cloud cover
   - Heating/cooling recommendations

3. **Quote Calculator** (AI_agents/UI/modules_external/quote-calculator/)
   - Weather-dependent delivery estimates
   - Seasonal pricing adjustments

4. **Custom Tools**
   - Any tool can access weather via Registry V3
   - Example: HVAC quotes adjusted for climate

## API Information

**Open-Meteo API:**
- Free tier: Unlimited requests
- No API key required
- Global coverage
- Response time: ~200-500ms
- Data sources: National weather services worldwide

**Rate Limiting:**
- No official rate limit
- Caching minimizes requests (1 call per location per hour)
- Frontend widget auto-refreshes every 10 minutes

## Error Handling

All tools return consistent error format:

```json
{
  "success": false,
  "error": "Connection timeout",
  "message": "Failed to fetch current weather"
}
```

Graceful fallbacks:
- IP geolocation fails → Uses Brisbane default
- Weather API fails → Returns cached data if available
- Cache query fails → Proceeds without cache (logs warning)

## Testing

```python
# Test weather tools
python -c "
from tools.registry_v3 import get_registry
registry = get_registry()

# Test current weather
weather = registry.execute_tool(tool_name='get_current_weather')
print(f'Temperature: {weather[\"current_weather\"][\"temperature_c\"]}°C')

# Test forecast
forecast = registry.execute_tool(tool_name='get_weather_forecast', days=5)
print(f'Forecast days: {len(forecast[\"forecast\"])}')
"
```

## Future Enhancements

- [ ] Add weather alerts/warnings
- [ ] Historical weather data
- [ ] UV index and air quality
- [ ] Weather radar images
- [ ] Weather-based notifications
- [ ] Dashboard widget customization
