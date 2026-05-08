# Battery Fuzzy System - API Integration Guide

Minimal reference for interacting with the `BatteryFuzzySystem` class.

## Quick Start

```python
from battery_fuzzy_system import BatteryFuzzySystem

system = BatteryFuzzySystem()
result = system.get_recommendations(battery_level=20, temperature=65, health=40, load=70)
print(result['charging_speed'])  # Output: "Slow"
print(result['charging_speed_raw'])  # Output: 31.4 (confidence 0-100)
print(result['discharge_limit'])  # Output: "Conservative"
print(result['discharge_limit_raw'])  # Output: 25.3 (confidence 0-100)
```

## API Reference

## Class: `BatteryFuzzySystem`

### `get_recommendations(battery_level, temperature, health, load)` → dict

Main method to get battery management decisions.

```python
result = system.get_recommendations(
    battery_level=20,
    temperature=65,
    health=40,
    load=70
)
```

**Parameters:**
- `battery_level` (float, 0-100): Current battery charge percentage
- `temperature` (float, -20 to 80): Battery temperature in °C
- `health` (float, 0-100): Battery health score
- `load` (float, 0-100): Current system load/power draw

**Returns:** Dictionary with 10 keys

```python
{
    'charging_speed': 'Slow',         # "Stop", "Slow", "Normal", "Fast"
    'charging_speed_raw': 31.4,       # Confidence 0-100
    'cooling_level': 'Medium',        # "Off", "Medium", "High"
    'cooling_level_raw': 48.2,        # Confidence 0-100
    'warning_status': 'Warning',      # "Safe", "Warning", "Critical"
    'warning_status_raw': 48.2,       # Confidence 0-100
    'discharge_limit': 'Conservative', # "Conservative", "Balanced", "Aggressive"
    'discharge_limit_raw': 25.3,      # Confidence 0-100
    'load': 70                        # Input echo
}
```

**Notes:**
- Deterministic: Same input always yields same output
- Processing time: <1ms
- Can be called repeatedly without issues

---

## Input Validation

```python
def validate_inputs(battery, temperature, health, load):
     if not isinstance(battery, (int, float)) or not 0 <= battery <= 100:
         raise ValueError("battery_level must be numeric 0-100")
     if not isinstance(temperature, (int, float)) or not -20 <= temperature <= 80:
         raise ValueError("temperature must be numeric -20 to 80")
     if not isinstance(health, (int, float)) or not 0 <= health <= 100:
         raise ValueError("health must be numeric 0-100")
     if not isinstance(load, (int, float)) or not 0 <= load <= 100:
         raise ValueError("load must be numeric 0-100")
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError` | scikit-fuzzy not installed | `pip install scikit-fuzzy numpy` |
| `ValueError` | Input not 0-100 range | Validate inputs before calling |
| `KeyError` | Accessing wrong key in result | Check dictionary keys match above |
