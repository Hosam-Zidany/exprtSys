# Battery Fuzzy System - API Integration Guide

Reference for the `BatteryFuzzySystem` class exposed by `battery_fuzzy_system.py`.

## Quick Start

```python
from battery_fuzzy_system import BatteryFuzzySystem

system = BatteryFuzzySystem()
result = system.get_recommendations(battery_level=20, temperature=65, health=40, load=70)

print(result['charging_speed'])       # "Slow"
print(result['charging_speed_raw'])   # 30.8 (defuzzified score on 0-100 scale)
print(result['discharge_limit'])      # "Conservative"
print(result['discharge_limit_raw'])  # 11.9
```

## API Reference

### `BatteryFuzzySystem()`

Constructs the controller. Building the rule graph takes ~30 ms on a typical machine; instantiate the class once at startup and reuse it across calls.

### `get_recommendations(battery_level, temperature, health, load) -> dict`

Run one inference pass and return categorical + raw outputs.

```python
result = system.get_recommendations(
    battery_level=20,
    temperature=65,
    health=40,
    load=70,
)
```

**Parameters**

| Name | Type | Range | Description |
|---|---|---|---|
| `battery_level` | float | 0-100 | State of charge (%) |
| `temperature`   | float | **-20 to 80** | Battery temperature (°C) |
| `health`        | float | 0-100 | State of health |
| `load`          | float | 0-100 | Current power draw / load |

Inputs may be any value `float()` accepts (numeric strings such as `"50"` are coerced). Out-of-range values raise `ValueError`; non-numeric values raise `TypeError`.

**Returns** — a `dict` with **12 keys**: 4 echoed inputs (cast to `float`) + 4 categorical outputs + 4 raw defuzzified outputs.

```python
{
    # echoed inputs (floats)
    'battery_level': 20.0,
    'temperature':   65.0,
    'health':        40.0,
    'load':          70.0,

    # categorical outputs
    'charging_speed':   'Slow',          # Stop | Slow | Normal | Fast
    'cooling_level':    'High',          # Off  | Medium | High
    'warning_status':   'Critical',      # Safe | Warning | Critical
    'discharge_limit':  'Conservative',  # Conservative | Balanced | Aggressive

    # raw defuzzified outputs (centroid on 0-100 universe)
    'charging_speed_raw':  30.8,
    'cooling_level_raw':   87.3,
    'warning_status_raw':  85.2,
    'discharge_limit_raw': 11.9,
}
```

**Output thresholds** (raw → category mapping)

| Output | < threshold₁ | < threshold₂ | otherwise |
|---|---|---|---|
| `charging_speed`  | `Stop` (<20)         | `Slow` (<50)     | `Normal` (<75) → else `Fast` |
| `cooling_level`   | `Off` (<25)          | `Medium` (<70)   | `High` |
| `warning_status`  | `Safe` (<33)         | `Warning` (<65)  | `Critical` |
| `discharge_limit` | `Conservative` (<33) | `Balanced` (<67) | `Aggressive` |

**Behaviour notes**

- **Deterministic.** Same inputs always yield the same outputs.
- **Latency.** First call ~30-50 ms (graph build + simulation warmup). Subsequent calls ~1-5 ms each on commodity hardware.
- **State.** scikit-fuzzy's `ControlSystemSimulation` caches state between calls. The implementation includes a one-shot retry that re-creates the simulation on `KeyError` / `ValueError` / `AttributeError` to recover from internal state corruption — callers don't need to handle this themselves, but be aware that a single `get_recommendations` call may rebuild the system once.
- **Thread-safety.** A single `BatteryFuzzySystem` instance is **not** thread-safe (mutable simulation state). Use one instance per worker, or guard calls with a lock.

## Input Validation

Inline validation is already performed inside `get_recommendations`; you only need a separate validator if you want to fail earlier. The helper below mirrors the actual implementation:

```python
def validate_inputs(battery_level, temperature, health, load):
    try:
        battery_level = float(battery_level)
        temperature   = float(temperature)
        health        = float(health)
        load          = float(load)
    except (TypeError, ValueError) as e:
        raise TypeError(f"All inputs must be numeric: {e}")

    if not (0 <= battery_level <= 100):
        raise ValueError("battery_level must be between 0-100")
    if not (-20 <= temperature <= 80):
        raise ValueError("temperature must be between -20 and 80°C")
    if not (0 <= health <= 100):
        raise ValueError("health must be between 0-100")
    if not (0 <= load <= 100):
        raise ValueError("load must be between 0-100")
```

## Errors

| Exception | When it is raised | How to handle |
|---|---|---|
| `TypeError`   | An input cannot be coerced via `float()` (e.g. `'abc'`, `None`, list). Message: `"All inputs must be numeric: …"`. | Validate / coerce on the caller side. |
| `ValueError`  | A numeric input is outside its documented range. The message names the offending input (`"temperature must be between -20 and 80°C"`, etc.). | Clamp or reject upstream. |
| `ImportError` | `scikit-fuzzy` (and its transitive deps `scipy`, `packaging`, `networkx`) not installed. | `pip install scikit-fuzzy numpy scipy packaging networkx`. |
| `KeyError`    | Caller accesses a key that does not exist in the result dict. | Use the documented key list above. |

## Minimal End-to-End Example

```python
from battery_fuzzy_system import BatteryFuzzySystem

system = BatteryFuzzySystem()

scenarios = [
    ("Hot, low battery, heavy load",  dict(battery_level=20, temperature=65, health=40, load=70)),
    ("Cool, mid battery, light load", dict(battery_level=50, temperature=25, health=80, load=30)),
]

for name, inputs in scenarios:
    r = system.get_recommendations(**inputs)
    print(f"{name}: charging={r['charging_speed']:<6}  "
          f"cooling={r['cooling_level']:<6}  "
          f"warning={r['warning_status']:<8}  "
          f"discharge={r['discharge_limit']}")
```

Expected output:

```
Hot, low battery, heavy load: charging=Slow    cooling=High    warning=Critical  discharge=Conservative
Cool, mid battery, light load: charging=Normal  cooling=Off     warning=Safe      discharge=Balanced
```
