import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class BatteryFuzzySystem:

    # Defuzzified-output thresholds for the categorical labels returned by
    # `get_recommendations`. Kept as class constants so the boundaries are a
    # single source of truth (and easy to tune without diving into the
    # interpretation methods).
    CHARGING_SPEED_THRESHOLDS = (20, 50, 75)   # Stop  | Slow    | Normal | Fast
    COOLING_LEVEL_THRESHOLDS = (25, 70)        # Off   | Medium  | High
    WARNING_STATUS_THRESHOLDS = (33, 65)       # Safe  | Warning | Critical
    DISCHARGE_LIMIT_THRESHOLDS = (33, 67)      # Cons. | Balanced| Aggressive

    def __init__(self):
        self._setup_antecedents()
        self._setup_consequents()
        self._create_membership_functions()
        self._setup_rules()
        self._create_control_system()
        self._call_count = 0  # Track number of compute() calls
    
    def _setup_antecedents(self):
        self.battery_level = ctrl.Antecedent(np.arange(0, 101, 1), 'battery_level')
        self.temperature = ctrl.Antecedent(np.arange(-20, 81, 1), 'temperature')
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
        self.load = ctrl.Antecedent(np.arange(0, 101, 1), 'load')
    
    def _setup_consequents(self):
        self.charging_speed = ctrl.Consequent(np.arange(0, 101, 1), 'charging_speed')
        self.cooling_level = ctrl.Consequent(np.arange(0, 101, 1), 'cooling_level')
        self.warning_status = ctrl.Consequent(np.arange(0, 101, 1), 'warning_status')
        self.discharge_limit = ctrl.Consequent(np.arange(0, 101, 1), 'discharge_limit')
    
    def _create_membership_functions(self):
        
        # Battery Level
        self.battery_level['very_low'] = fuzz.trimf(self.battery_level.universe, [0, 0, 20])
        self.battery_level['low'] = fuzz.trimf(self.battery_level.universe, [10, 25, 40])
        self.battery_level['medium'] = fuzz.trimf(self.battery_level.universe, [30, 50, 70])
        self.battery_level['high'] = fuzz.trimf(self.battery_level.universe, [60, 75, 90])
        self.battery_level['full'] = fuzz.trimf(self.battery_level.universe, [80, 100, 100])
        
        # Temperature (realistic range: -20°C to 80°C)
        self.temperature['cold'] = fuzz.trimf(self.temperature.universe, [-20, -20, 5])
        self.temperature['normal'] = fuzz.trimf(self.temperature.universe, [0, 25, 40])
        self.temperature['hot'] = fuzz.trimf(self.temperature.universe, [35, 55, 70])
        self.temperature['very_hot'] = fuzz.trapmf(self.temperature.universe, [65, 75, 80, 80])
        
        # Health
        self.health['poor'] = fuzz.trimf(self.health.universe, [0, 0, 33])
        self.health['average'] = fuzz.trimf(self.health.universe, [25, 50, 75])
        self.health['good'] = fuzz.trimf(self.health.universe, [67, 100, 100])
        
        # Charging Speed
        self.charging_speed['stop'] = fuzz.trimf(self.charging_speed.universe, [0, 0, 20])
        self.charging_speed['slow'] = fuzz.trimf(self.charging_speed.universe, [10, 35, 50])
        self.charging_speed['normal'] = fuzz.trimf(self.charging_speed.universe, [40, 65, 85])
        self.charging_speed['fast'] = fuzz.trimf(self.charging_speed.universe, [75, 100, 100])
        
        # Cooling Level
        self.cooling_level['off'] = fuzz.trimf(self.cooling_level.universe, [0, 0, 25])
        self.cooling_level['medium'] = fuzz.trimf(self.cooling_level.universe, [15, 50, 80])
        self.cooling_level['high'] = fuzz.trimf(self.cooling_level.universe, [70, 100, 100])
        
        # Warning Status
        self.warning_status['safe'] = fuzz.trimf(self.warning_status.universe, [0, 0, 33])
        self.warning_status['warning'] = fuzz.trimf(self.warning_status.universe, [20, 50, 75])
        self.warning_status['critical'] = fuzz.trimf(self.warning_status.universe, [65, 100, 100])
        
        # Load
        self.load['low'] = fuzz.trimf(self.load.universe, [0, 0, 33])
        self.load['medium'] = fuzz.trimf(self.load.universe, [25, 50, 75])
        self.load['high'] = fuzz.trimf(self.load.universe, [67, 100, 100])
        
        # Discharge Limit
        self.discharge_limit['conservative'] = fuzz.trimf(self.discharge_limit.universe, [0, 0, 33])
        self.discharge_limit['balanced'] = fuzz.trimf(self.discharge_limit.universe, [25, 50, 75])
        self.discharge_limit['aggressive'] = fuzz.trimf(self.discharge_limit.universe, [67, 100, 100])
     
    def _setup_rules(self):

        # CHARGING SPEED (10)
        # R1/R3 only fire on `normal` temperature: charging Li-ion below 0 C
        # causes lithium plating, so cold conditions are handled by R45/R46
        # (slow charge) instead of fast charging.
        self.rule1 = ctrl.Rule(self.battery_level['very_low'] & self.temperature['normal'], self.charging_speed['fast'])
        self.rule2 = ctrl.Rule(self.battery_level['very_low'] & (self.temperature['hot'] | self.temperature['very_hot']), self.charging_speed['slow'])
        self.rule3 = ctrl.Rule(self.battery_level['low'] & self.temperature['normal'], self.charging_speed['fast'])
        self.rule4 = ctrl.Rule(self.battery_level['low'] & (self.temperature['hot'] | self.temperature['very_hot']), self.charging_speed['slow'])
        self.rule5 = ctrl.Rule(self.battery_level['medium'] & (self.temperature['cold'] | self.temperature['normal'] | self.temperature['hot']), self.charging_speed['normal'])
        self.rule6 = ctrl.Rule(self.battery_level['medium'] & self.temperature['very_hot'], self.charging_speed['slow'])
        self.rule7 = ctrl.Rule((self.battery_level['high'] | self.battery_level['full']) & (self.temperature['cold'] | self.temperature['normal']), self.charging_speed['slow'])
        self.rule8 = ctrl.Rule((self.battery_level['high'] | self.battery_level['full']) & (self.temperature['hot'] | self.temperature['very_hot']), self.charging_speed['stop'])
        self.rule9 = ctrl.Rule(self.health['poor'] & (self.temperature['cold'] | self.temperature['normal']), self.charging_speed['slow'])
        self.rule10 = ctrl.Rule(self.health['poor'] & (self.temperature['hot'] | self.temperature['very_hot']), self.charging_speed['stop'])
        
        # COOLING LEVEL (8)
        self.rule11 = ctrl.Rule((self.temperature['cold'] | self.temperature['normal']) & (self.battery_level['very_low'] | self.battery_level['low'] | self.battery_level['medium']), self.cooling_level['off'])
        self.rule12 = ctrl.Rule((self.temperature['cold'] | self.temperature['normal']) & (self.battery_level['high'] | self.battery_level['full']), self.cooling_level['off'])
        self.rule13 = ctrl.Rule(self.temperature['hot'] & (self.battery_level['very_low'] | self.battery_level['low']), self.cooling_level['high'])
        self.rule14 = ctrl.Rule(self.temperature['hot'] & self.battery_level['medium'], self.cooling_level['medium'])
        self.rule15 = ctrl.Rule(self.temperature['hot'] & (self.battery_level['high'] | self.battery_level['full']), self.cooling_level['medium'])
        self.rule16 = ctrl.Rule(self.temperature['very_hot'] & (self.battery_level['very_low'] | self.battery_level['low']), self.cooling_level['high'])
        self.rule17 = ctrl.Rule(self.temperature['very_hot'] & (self.battery_level['medium'] | self.battery_level['high'] | self.battery_level['full']), self.cooling_level['high'])
        self.rule18 = ctrl.Rule(self.health['poor'] & (self.temperature['hot'] | self.temperature['very_hot']), self.cooling_level['high'])
        
        # WARNING STATUS (8)
        self.rule19 = ctrl.Rule((self.battery_level['very_low'] | self.battery_level['low']) & (self.temperature['cold'] | self.temperature['normal']), self.warning_status['warning'])
        self.rule20 = ctrl.Rule((self.battery_level['very_low'] | self.battery_level['low']) & (self.temperature['hot'] | self.temperature['very_hot']), self.warning_status['critical'])
        self.rule21 = ctrl.Rule(self.temperature['very_hot'] | self.health['poor'], self.warning_status['critical'])
        self.rule22 = ctrl.Rule(self.battery_level['medium'] & self.temperature['hot'] & self.health['average'], self.warning_status['warning'])
        self.rule23 = ctrl.Rule(self.battery_level['medium'] & (self.temperature['cold'] | self.temperature['normal']) & self.health['good'], self.warning_status['safe'])
        self.rule24 = ctrl.Rule((self.battery_level['high'] | self.battery_level['full']) & self.health['good'] & (self.temperature['cold'] | self.temperature['normal']), self.warning_status['safe'])
        self.rule25 = ctrl.Rule(self.battery_level['medium'] & self.temperature['hot'] & self.health['good'], self.warning_status['warning'])
        # R26 used to be `(high|full) -> safe` unconditionally, which contradicted
        # R21 (very_hot|poor -> critical) when the battery was full but the cell
        # was overheating. Excluding `very_hot` lets the safety-critical rule win.
        self.rule26 = ctrl.Rule((self.battery_level['high'] | self.battery_level['full']) & (self.temperature['cold'] | self.temperature['normal'] | self.temperature['hot']), self.warning_status['safe'])
        self.rule27 = ctrl.Rule(self.battery_level['medium'] & (self.temperature['hot'] | self.temperature['very_hot']) & self.health['poor'], self.warning_status['warning'])
        self.rule28 = ctrl.Rule(self.battery_level['very_low'] & self.health['poor'] & self.load['high'], self.warning_status['critical'])
        self.rule29 = ctrl.Rule(self.battery_level['very_low'] & self.health['good'], self.discharge_limit['conservative'])
        self.rule30 = ctrl.Rule(self.battery_level['low'] & (self.health['poor'] | self.health['average']), self.discharge_limit['conservative'])
        self.rule31 = ctrl.Rule(self.battery_level['medium'] & self.load['low'], self.discharge_limit['aggressive'])
        
        # Moderate battery levels
        self.rule32 = ctrl.Rule(self.battery_level['medium'] & (self.load['medium'] | self.load['high']), self.discharge_limit['balanced'])
        self.rule33 = ctrl.Rule(self.battery_level['high'] & self.load['low'], self.discharge_limit['balanced'])
        self.rule34 = ctrl.Rule(self.battery_level['high'] & (self.load['medium'] | self.load['high']), self.discharge_limit['aggressive'])
        
        # Full battery
        self.rule35 = ctrl.Rule(self.battery_level['full'] & self.load['low'], self.discharge_limit['aggressive'])
        self.rule36 = ctrl.Rule(self.battery_level['full'] & (self.load['medium'] | self.load['high']), self.discharge_limit['balanced'])
        self.rule37 = ctrl.Rule(self.health['poor'] & (self.load['medium'] | self.load['high']), self.discharge_limit['conservative'])
        
        # DISCHARGE LIMIT SAFETY
        self.rule38 = ctrl.Rule((self.health['poor'] | self.temperature['very_hot']) & self.battery_level['low'], self.discharge_limit['conservative'])
        self.rule39 = ctrl.Rule(self.temperature['very_hot'] & self.battery_level['very_low'], self.discharge_limit['conservative'])
        
        self.rule40 = ctrl.Rule(self.battery_level['medium'] & self.health['poor'], self.charging_speed['slow'])
        self.rule41 = ctrl.Rule(self.battery_level['medium'] & (self.temperature['cold'] | self.temperature['normal']) & self.health['average'], self.warning_status['safe'])
        self.rule42 = ctrl.Rule(self.temperature['very_hot'], self.charging_speed['stop'])
        self.rule43 = ctrl.Rule(self.battery_level['very_low'], self.discharge_limit['conservative'])

        # Catch-all for `low` battery so discharge_limit is always defined regardless of health/temp/load.
        # Without this, low battery + good health + cold/normal temp + low load fires no discharge rule.
        self.rule44 = ctrl.Rule(self.battery_level['low'], self.discharge_limit['conservative'])

        # Cold-charging Li-ion safety: never fast-charge below freezing.
        # Pairs with R1/R3 which now only cover `normal` temperatures.
        self.rule45 = ctrl.Rule(self.battery_level['very_low'] & self.temperature['cold'], self.charging_speed['slow'])
        self.rule46 = ctrl.Rule(self.battery_level['low'] & self.temperature['cold'], self.charging_speed['slow'])

        self.rules = [
             self.rule1, self.rule2, self.rule3, self.rule4, self.rule5,
             self.rule6, self.rule7, self.rule8, self.rule9, self.rule10,
             self.rule11, self.rule12, self.rule13, self.rule14, self.rule15,
             self.rule16, self.rule17, self.rule18, self.rule19, self.rule20,
             self.rule21, self.rule22, self.rule23, self.rule24, self.rule25,
             self.rule26, self.rule27, self.rule28, self.rule29, self.rule30,
             self.rule31, self.rule32, self.rule33, self.rule34, self.rule35,
             self.rule36, self.rule37, self.rule38, self.rule39, self.rule40,
             self.rule41, self.rule42, self.rule43, self.rule44,
             self.rule45, self.rule46,
        ]

        # Single source of truth for rule descriptions, used by vis.py for the
        # rule-activation table. Each tuple is (name, description, output_var)
        # in the same order as `self.rules`.
        self.rule_info = [
            ('R1',  'Very Low Battery + Normal Temp -> Fast Charge',                 'charging_speed'),
            ('R2',  'Very Low Battery + Hot/Very Hot Temp -> Slow Charge',           'charging_speed'),
            ('R3',  'Low Battery + Normal Temp -> Fast Charge',                      'charging_speed'),
            ('R4',  'Low Battery + Hot/Very Hot Temp -> Slow Charge',                'charging_speed'),
            ('R5',  'Medium Battery + Cold/Normal/Hot Temp -> Normal Charge',        'charging_speed'),
            ('R6',  'Medium Battery + Very Hot Temp -> Slow Charge',                 'charging_speed'),
            ('R7',  'High/Full Battery + Cold/Normal Temp -> Slow Charge',           'charging_speed'),
            ('R8',  'High/Full Battery + Hot/Very Hot Temp -> Stop Charge',          'charging_speed'),
            ('R9',  'Poor Health + Cold/Normal Temp -> Slow Charge',                 'charging_speed'),
            ('R10', 'Poor Health + Hot/Very Hot Temp -> Stop Charge',                'charging_speed'),
            ('R11', 'Cold/Normal Temp + Very Low/Low/Medium Battery -> Cooling Off', 'cooling_level'),
            ('R12', 'Cold/Normal Temp + High/Full Battery -> Cooling Off',           'cooling_level'),
            ('R13', 'Hot Temp + Very Low/Low Battery -> Cooling High',               'cooling_level'),
            ('R14', 'Hot Temp + Medium Battery -> Cooling Medium',                   'cooling_level'),
            ('R15', 'Hot Temp + High/Full Battery -> Cooling Medium',                'cooling_level'),
            ('R16', 'Very Hot Temp + Very Low/Low Battery -> Cooling High',          'cooling_level'),
            ('R17', 'Very Hot Temp + Medium/High/Full Battery -> Cooling High',      'cooling_level'),
            ('R18', 'Poor Health + Hot/Very Hot Temp -> Cooling High',               'cooling_level'),
            ('R19', 'Very Low/Low Battery + Cold/Normal Temp -> Warning',            'warning_status'),
            ('R20', 'Very Low/Low Battery + Hot/Very Hot Temp -> Critical',          'warning_status'),
            ('R21', 'Very Hot Temp OR Poor Health -> Critical',                      'warning_status'),
            ('R22', 'Medium Battery + Hot Temp + Average Health -> Warning',         'warning_status'),
            ('R23', 'Medium Battery + Cold/Normal Temp + Good Health -> Safe',       'warning_status'),
            ('R24', 'High/Full Battery + Good Health + Cold/Normal Temp -> Safe',    'warning_status'),
            ('R25', 'Medium Battery + Hot Temp + Good Health -> Warning',            'warning_status'),
            ('R26', 'High/Full Battery + Cold/Normal/Hot Temp -> Safe',              'warning_status'),
            ('R27', 'Medium Battery + Hot/Very Hot Temp + Poor Health -> Warning',   'warning_status'),
            ('R28', 'Very Low Battery + Poor Health + High Load -> Critical',        'warning_status'),
            ('R29', 'Very Low Battery + Good Health -> Conservative',                'discharge_limit'),
            ('R30', 'Low Battery + Poor/Average Health -> Conservative',             'discharge_limit'),
            ('R31', 'Medium Battery + Low Load -> Aggressive',                       'discharge_limit'),
            ('R32', 'Medium Battery + Medium/High Load -> Balanced',                 'discharge_limit'),
            ('R33', 'High Battery + Low Load -> Balanced',                           'discharge_limit'),
            ('R34', 'High Battery + Medium/High Load -> Aggressive',                 'discharge_limit'),
            ('R35', 'Full Battery + Low Load -> Aggressive',                         'discharge_limit'),
            ('R36', 'Full Battery + Medium/High Load -> Balanced',                   'discharge_limit'),
            ('R37', 'Poor Health + Medium/High Load -> Conservative',                'discharge_limit'),
            ('R38', '(Poor Health OR Very Hot) + Low Battery -> Conservative',       'discharge_limit'),
            ('R39', 'Very Hot Temp + Very Low Battery -> Conservative',              'discharge_limit'),
            ('R40', 'Medium Battery + Poor Health -> Slow Charge',                   'charging_speed'),
            ('R41', 'Medium Battery + Cold/Normal Temp + Average Health -> Safe',    'warning_status'),
            ('R42', 'Very Hot Temp -> Stop Charge',                                  'charging_speed'),
            ('R43', 'Very Low Battery -> Conservative (catch-all)',                  'discharge_limit'),
            ('R44', 'Low Battery -> Conservative (catch-all)',                       'discharge_limit'),
            ('R45', 'Very Low Battery + Cold Temp -> Slow Charge (Li-ion safety)',   'charging_speed'),
            ('R46', 'Low Battery + Cold Temp -> Slow Charge (Li-ion safety)',        'charging_speed'),
        ]
    
    def _create_control_system(self):
        self.system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.system)
    
    def get_recommendations(self, battery_level, temperature, health, load):
        # Validate inputs first
        try:
            battery_level = float(battery_level)
            temperature = float(temperature)
            health = float(health)
            load = float(load)
        except (ValueError, TypeError) as e:
            raise TypeError(f"All inputs must be numeric: {e}")
        
        if not (0 <= battery_level <= 100):
            raise ValueError("battery_level must be between 0-100")
        if not (-20 <= temperature <= 80):
            raise ValueError("temperature must be between -20 and 80°C")
        if not (0 <= health <= 100):
            raise ValueError("health must be between 0-100")
        if not (0 <= load <= 100):
            raise ValueError("load must be between 0-100")
        
        # Attempt to get recommendations with fallback to simulation recreation
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Set inputs
                self.simulation.input['battery_level'] = battery_level
                self.simulation.input['temperature'] = temperature
                self.simulation.input['health'] = health
                self.simulation.input['load'] = load
                
                # Compute
                self.simulation.compute()
                
                # Get outputs
                charging_speed = self.simulation.output['charging_speed']
                cooling_level = self.simulation.output['cooling_level']
                warning_status = self.simulation.output['warning_status']
                discharge_limit = self.simulation.output['discharge_limit']
                
                # Success, break out of loop
                break
            except (KeyError, ValueError, AttributeError) as e:
                if attempt == 0:
                    # First attempt failed, recreate simulation and try again
                    self._create_control_system()
                else:
                    # Second attempt failed, re-raise the exception
                    raise
        
        return {
            'battery_level': battery_level,
            'temperature': temperature,
            'health': health,
            'load': load,
            'charging_speed_raw': round(charging_speed, 1),
            'charging_speed': self._interpret_charging_speed(charging_speed),
            'cooling_level_raw': round(cooling_level, 1),
            'cooling_level': self._interpret_cooling_level(cooling_level),
            'warning_status_raw': round(warning_status, 1),
            'warning_status': self._interpret_warning_status(warning_status),
            'discharge_limit_raw': round(discharge_limit, 1),
            'discharge_limit': self._interpret_discharge_limit(discharge_limit)
        }
    
    def _interpret_charging_speed(self, value):
        stop, slow, normal = self.CHARGING_SPEED_THRESHOLDS
        if value < stop:
            return "Stop"
        if value < slow:
            return "Slow"
        if value < normal:
            return "Normal"
        return "Fast"

    def _interpret_cooling_level(self, value):
        off, medium = self.COOLING_LEVEL_THRESHOLDS
        if value < off:
            return "Off"
        if value < medium:
            return "Medium"
        return "High"

    def _interpret_warning_status(self, value):
        safe, warning = self.WARNING_STATUS_THRESHOLDS
        if value < safe:
            return "Safe"
        if value < warning:
            return "Warning"
        return "Critical"

    def _interpret_discharge_limit(self, value):
        conservative, balanced = self.DISCHARGE_LIMIT_THRESHOLDS
        if value < conservative:
            return "Conservative"
        if value < balanced:
            return "Balanced"
        return "Aggressive"
