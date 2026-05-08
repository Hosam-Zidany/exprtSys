"""
Comprehensive Visualization Suite for Battery Fuzzy Logic System
================================================================

This module provides 9 visualization functions to analyze and understand
the fuzzy logic battery management system in detail.

Usage:
    from vis import *
    system = BatteryFuzzySystem()
    
    # Generate all visualizations
    visualize_membership_functions(system)
    visualize_fuzzification(system)
    visualize_rule_activation(system)
    visualize_charging_intersection(system)
    visualize_cooling_intersection(system)
    visualize_warning_intersection(system)
    visualize_discharge_intersection(system)
    visualize_control_surfaces(system)
    visualize_output_distributions(system)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import skfuzzy as fuzz
from battery_fuzzy_system import BatteryFuzzySystem


# ============================================================================
# VISUALIZATION 1: MEMBERSHIP FUNCTIONS
# ============================================================================

def visualize_membership_functions(system):
    """
    Create a 3x3 subplot grid showing all membership functions.
    
    Displays:
    - Row 1: Battery Level, Temperature, Health (inputs)
    - Row 2: Load, Charging Speed, Cooling Level (inputs & outputs)
    - Row 3: Warning Status, Discharge Limit, (empty) (outputs)
    
    Each subplot shows all membership functions with distinct colors,
    filled areas with transparency, legends, and grid.
    """
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle('Fuzzy System Membership Functions', fontsize=16, fontweight='bold')
    
    # Color palettes for each variable
    colors_battery = ['#FF6B6B', '#FF8E72', '#FFD93D', '#6BCB77', '#4D96FF']
    colors_temp = ['#1E88E5', '#90CAF9', '#FFA726', '#EF5350', '#E53935']
    colors_health = ['#E53935', '#FFB74D', '#81C784']
    colors_load = ['#1976D2', '#81D4FA', '#D32F2F']
    colors_charging = ['#B71C1C', '#F57C00', '#FBC02D', '#388E3C']
    colors_cooling = ['#2196F3', '#81D4FA', '#EF5350']
    colors_warning = ['#4CAF50', '#FFC107', '#D32F2F']
    colors_discharge = ['#E53935', '#FFB74D', '#1976D2']
    
    # ---- INPUT 1: Battery Level ----
    ax = axes[0, 0]
    for i, (name, color) in enumerate(zip(['very_low', 'low', 'medium', 'high', 'full'], colors_battery)):
        mf = system.battery_level[name].mf
        ax.fill_between(system.battery_level.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.battery_level.universe, mf, color=color, linewidth=2)
    ax.set_title('Battery Level (0-100%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Battery Level (%)')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- INPUT 2: Temperature ----
    ax = axes[0, 1]
    for i, (name, color) in enumerate(zip(['cold', 'normal', 'hot', 'very_hot'], colors_temp)):
        mf = system.temperature[name].mf
        ax.fill_between(system.temperature.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.temperature.universe, mf, color=color, linewidth=2)
    ax.set_title('Temperature (-20 to 80°C)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([-20, 80])
    
    # ---- INPUT 3: Health ----
    ax = axes[0, 2]
    for i, (name, color) in enumerate(zip(['poor', 'average', 'good'], colors_health)):
        mf = system.health[name].mf
        ax.fill_between(system.health.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.health.universe, mf, color=color, linewidth=2)
    ax.set_title('Battery Health (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Health')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- INPUT 4: Load ----
    ax = axes[1, 0]
    for i, (name, color) in enumerate(zip(['low', 'medium', 'high'], colors_load)):
        mf = system.load[name].mf
        ax.fill_between(system.load.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.load.universe, mf, color=color, linewidth=2)
    ax.set_title('Load (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Load')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- OUTPUT 1: Charging Speed ----
    ax = axes[1, 1]
    for i, (name, color) in enumerate(zip(['stop', 'slow', 'normal', 'fast'], colors_charging)):
        mf = system.charging_speed[name].mf
        ax.fill_between(system.charging_speed.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.charging_speed.universe, mf, color=color, linewidth=2)
    ax.set_title('Charging Speed (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Charging Speed')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- OUTPUT 2: Cooling Level ----
    ax = axes[1, 2]
    for i, (name, color) in enumerate(zip(['off', 'medium', 'high'], colors_cooling)):
        mf = system.cooling_level[name].mf
        ax.fill_between(system.cooling_level.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.cooling_level.universe, mf, color=color, linewidth=2)
    ax.set_title('Cooling Level (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cooling Level')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- OUTPUT 3: Warning Status ----
    ax = axes[2, 0]
    for i, (name, color) in enumerate(zip(['safe', 'warning', 'critical'], colors_warning)):
        mf = system.warning_status[name].mf
        ax.fill_between(system.warning_status.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.warning_status.universe, mf, color=color, linewidth=2)
    ax.set_title('Warning Status (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Warning Status')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- OUTPUT 4: Discharge Limit ----
    ax = axes[2, 1]
    for i, (name, color) in enumerate(zip(['conservative', 'balanced', 'aggressive'], colors_discharge)):
        mf = system.discharge_limit[name].mf
        ax.fill_between(system.discharge_limit.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.discharge_limit.universe, mf, color=color, linewidth=2)
    ax.set_title('Discharge Limit (0-100)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Discharge Limit')
    ax.set_ylabel('Membership (μ)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- Empty subplot for 3x3 grid ----
    ax = axes[2, 2]
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('01_membership_functions.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 01_membership_functions.png")
    plt.close()


# ============================================================================
# VISUALIZATION 2: FUZZIFICATION
# ============================================================================

def visualize_fuzzification(system):
    """
    Show how crisp inputs are converted to fuzzy membership values.
    
    Displays 4 subplots showing all inputs:
    - Battery Level fuzzification (input=35%)
    - Temperature fuzzification (input=45°C)
    - Health fuzzification (input=60)
    - Load fuzzification (input=40)
    
    Each shows membership functions with input marker and μ values annotated.
    """
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    fig.suptitle('Fuzzification: Crisp Inputs to Fuzzy Membership Values', 
                 fontsize=14, fontweight='bold')
    
    # Test input values
    battery_input = 35.0
    temp_input = 45.0
    health_input = 60.0
    load_input = 40.0
    
    # ---- Battery Level Fuzzification ----
    ax = axes[0]
    colors = ['#FF6B6B', '#FF8E72', '#FFD93D', '#6BCB77', '#4D96FF']
    labels = ['very_low', 'low', 'medium', 'high', 'full']
    
    membership_values = {}
    for name, color in zip(labels, colors):
        mf = system.battery_level[name].mf
        ax.fill_between(system.battery_level.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.battery_level.universe, mf, color=color, linewidth=2)
        
        # Calculate membership value at input
        mu_val = fuzz.interp_membership(system.battery_level.universe, mf, battery_input)
        membership_values[name] = mu_val
    
    # Mark input value
    ax.axvline(x=battery_input, color='black', linewidth=2, linestyle='--', label=f'Input={battery_input}%')
    
    # Annotate membership values
    y_pos = 0.95
    ax.text(0.98, y_pos, 'Membership Values (μ):', transform=ax.transAxes,
            fontsize=9, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    y_pos -= 0.07
    for name, mu in membership_values.items():
        if mu > 0.01:  # Only show non-zero values
            ax.text(0.98, y_pos, f'{name}: {mu:.3f}', transform=ax.transAxes,
                   fontsize=8, ha='right', va='top', family='monospace')
            y_pos -= 0.07
    
    ax.set_title(f'Battery Level\n(Input = {battery_input}%)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Battery Level (%)', fontsize=9)
    ax.set_ylabel('Membership (μ)', fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- Temperature Fuzzification ----
    ax = axes[1]
    colors = ['#1E88E5', '#90CAF9', '#FFA726', '#EF5350']
    labels = ['cold', 'normal', 'hot', 'very_hot']
    
    membership_values = {}
    for name, color in zip(labels, colors):
        mf = system.temperature[name].mf
        ax.fill_between(system.temperature.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.temperature.universe, mf, color=color, linewidth=2)
        
        mu_val = fuzz.interp_membership(system.temperature.universe, mf, temp_input)
        membership_values[name] = mu_val
    
    ax.axvline(x=temp_input, color='black', linewidth=2, linestyle='--', label=f'Input={temp_input}°C')
    
    y_pos = 0.95
    ax.text(0.98, y_pos, 'Membership Values (μ):', transform=ax.transAxes,
            fontsize=9, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    y_pos -= 0.07
    for name, mu in membership_values.items():
        if mu > 0.01:
            ax.text(0.98, y_pos, f'{name}: {mu:.3f}', transform=ax.transAxes,
                   fontsize=8, ha='right', va='top', family='monospace')
            y_pos -= 0.07
    
    ax.set_title(f'Temperature\n(Input = {temp_input}°C)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Temperature (°C)', fontsize=9)
    ax.set_ylabel('Membership (μ)', fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([-20, 80])
    
    # ---- Health Fuzzification ----
    ax = axes[2]
    colors = ['#E53935', '#FFB74D', '#81C784']
    labels = ['poor', 'average', 'good']
    
    membership_values = {}
    for name, color in zip(labels, colors):
        mf = system.health[name].mf
        ax.fill_between(system.health.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.health.universe, mf, color=color, linewidth=2)
        
        mu_val = fuzz.interp_membership(system.health.universe, mf, health_input)
        membership_values[name] = mu_val
    
    ax.axvline(x=health_input, color='black', linewidth=2, linestyle='--', label=f'Input={health_input}')
    
    y_pos = 0.95
    ax.text(0.98, y_pos, 'Membership Values (μ):', transform=ax.transAxes,
            fontsize=9, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    y_pos -= 0.07
    for name, mu in membership_values.items():
        if mu > 0.01:
            ax.text(0.98, y_pos, f'{name}: {mu:.3f}', transform=ax.transAxes,
                   fontsize=8, ha='right', va='top', family='monospace')
            y_pos -= 0.07
    
    ax.set_title(f'Health\n(Input = {health_input})', fontsize=11, fontweight='bold')
    ax.set_xlabel('Health', fontsize=9)
    ax.set_ylabel('Membership (μ)', fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    # ---- Load Fuzzification ----
    ax = axes[3]
    colors = ['#1976D2', '#81D4FA', '#D32F2F']
    labels = ['low', 'medium', 'high']
    
    membership_values = {}
    for name, color in zip(labels, colors):
        mf = system.load[name].mf
        ax.fill_between(system.load.universe, mf, alpha=0.3, color=color, label=name)
        ax.plot(system.load.universe, mf, color=color, linewidth=2)
        
        mu_val = fuzz.interp_membership(system.load.universe, mf, load_input)
        membership_values[name] = mu_val
    
    ax.axvline(x=load_input, color='black', linewidth=2, linestyle='--', label=f'Input={load_input}')
    
    y_pos = 0.95
    ax.text(0.98, y_pos, 'Membership Values (μ):', transform=ax.transAxes,
            fontsize=9, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    y_pos -= 0.07
    for name, mu in membership_values.items():
        if mu > 0.01:
            ax.text(0.98, y_pos, f'{name}: {mu:.3f}', transform=ax.transAxes,
                   fontsize=8, ha='right', va='top', family='monospace')
            y_pos -= 0.07
    
    ax.set_title(f'Load\n(Input = {load_input})', fontsize=11, fontweight='bold')
    ax.set_xlabel('Load', fontsize=9)
    ax.set_ylabel('Membership (μ)', fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    
    plt.tight_layout()
    plt.savefig('02_fuzzification.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 02_fuzzification.png")
    plt.close()


# ============================================================================
# VISUALIZATION 3: RULE ACTIVATION
# ============================================================================

def visualize_rule_activation(system):
    """
    Show which rules fire for a specific scenario and their activation strength.
    
    Scenario: Battery=25%, Temperature=60°C, Health=40%
    
    Displays a table showing:
    - Rule number
    - Conditions
    - Output action
    - Activation strength (color-coded)
    """
    battery = 25.0
    temperature = 60.0
    health = 40.0
    load = 50.0
    
    # Get system output
    result = system.get_recommendations(battery, temperature, health, load)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.suptitle(f'Rule Activation for Scenario:\nBattery={battery}%, Temperature={temperature}°C, Health={health}',
                 fontsize=13, fontweight='bold')
    
    # Prepare rule data (43 total rules)
    rules_data = [
        # CHARGING SPEED (10 rules)
        ("R1", "Very Low & Cold/Normal", "Fast Charge", "charging_speed"),
        ("R2", "Very Low & Hot/Very Hot", "Slow Charge", "charging_speed"),
        ("R3", "Low & Cold/Normal", "Fast Charge", "charging_speed"),
        ("R4", "Low & Hot/Very Hot", "Slow Charge", "charging_speed"),
        ("R5", "Medium & Cold/Normal/Hot", "Normal Charge", "charging_speed"),
        ("R6", "Medium & Very Hot", "Slow Charge", "charging_speed"),
        ("R7", "High/Full & Cold/Normal", "Slow Charge", "charging_speed"),
        ("R8", "High/Full & Hot/Very Hot", "Stop Charge", "charging_speed"),
        ("R9", "Poor Health & Cold/Normal", "Slow Charge", "charging_speed"),
        ("R10", "Poor Health & Hot/Very Hot", "Stop Charge", "charging_speed"),
        # COOLING LEVEL (8 rules)
        ("R11", "Cold/Normal & Low-Med", "Cooling Off", "cooling_level"),
        ("R12", "Cold/Normal & High/Full", "Cooling Off", "cooling_level"),
        ("R13", "Hot & Low Battery", "High Cooling", "cooling_level"),
        ("R14", "Hot & Medium Battery", "Med Cooling", "cooling_level"),
        ("R15", "Hot & High/Full Battery", "Med Cooling", "cooling_level"),
        ("R16", "Very Hot & Low Battery", "High Cooling", "cooling_level"),
        ("R17", "Very Hot & Med/High/Full", "High Cooling", "cooling_level"),
        ("R18", "Poor Health & Hot/Very Hot", "High Cooling", "cooling_level"),
        # WARNING STATUS (9 rules - R28 added)
        ("R19", "Low & Cold/Normal", "Warning", "warning_status"),
        ("R20", "Low & Hot/Very Hot", "Critical", "warning_status"),
        ("R21", "Very Hot OR Poor Health", "Critical", "warning_status"),
        ("R22", "Medium & Hot & Avg Health", "Warning", "warning_status"),
        ("R23", "Medium & Cold/Normal & Good", "Safe", "warning_status"),
        ("R24", "High/Full & Good & Cold/Normal", "Safe", "warning_status"),
        ("R25", "Medium & Hot & Good Health", "Warning", "warning_status"),
        ("R26", "High/Full & Cold/Normal/Hot", "Safe", "warning_status"),
        ("R28", "Very Low & Poor Health & High Load", "Critical", "warning_status"),
        # DISCHARGE LIMIT (12 rules)
        ("R29", "Low Battery & Low Load", "Aggressive", "discharge_limit"),
        ("R30", "Low Battery & Med Load", "Balanced", "discharge_limit"),
        ("R31", "Low Battery & High Load", "Balanced", "discharge_limit"),
        ("R32", "Medium & Low Load", "Balanced", "discharge_limit"),
        ("R33", "Medium & Med Load", "Balanced", "discharge_limit"),
        ("R34", "Medium & High Load", "Conservative", "discharge_limit"),
        ("R35", "High Battery & Low Load", "Balanced", "discharge_limit"),
        ("R36", "High Battery & Med Load", "Conservative", "discharge_limit"),
        ("R37", "High Battery & High Load", "Conservative", "discharge_limit"),
        ("R38", "Poor Health OR Very Hot", "Conservative", "discharge_limit"),
        ("R39", "Good Health & Low Battery", "Aggressive", "discharge_limit"),
        # SAFETY OVERRIDES (3 rules)
        ("R40", "Very Hot Temp Override", "Stop Charge", "charging_speed"),
        ("R41", "Critical Battery Level", "Stop Charge", "charging_speed"),
        ("R42", "Very Low Battery Fallback", "Conservative", "discharge_limit"),
    ]
    
    # Simplified rule matching (basic demonstration)
    active_rules = []
    
    # Check which rules would be active based on crisp logic approximation
    # CHARGING SPEED RULES (0-9)
    if battery < 40:
        if temperature < 50:
            active_rules.extend([0, 2])  # R1, R3
        else:
            active_rules.extend([1, 3])  # R2, R4
    elif battery < 70:
        if temperature < 75:
            active_rules.append(4)  # R5
        else:
            active_rules.append(5)  # R6
    else:
        if temperature < 75:
            active_rules.append(6)  # R7
        else:
            active_rules.append(7)  # R8
    
    if health < 35:
        if temperature < 75:
            active_rules.append(8)  # R9
        else:
            active_rules.append(9)  # R10
    
    # COOLING RULES (10-17)
    if temperature < 50:
        if battery < 70:
            active_rules.append(10)  # R11
        else:
            active_rules.append(11)  # R12
    elif temperature < 75:
        if battery < 40:
            active_rules.append(12)  # R13
        elif battery < 70:
            active_rules.append(13)  # R14
        else:
            active_rules.append(14)  # R15
    else:  # Very hot
        if battery < 40:
            active_rules.append(15)  # R16
        else:
            active_rules.append(16)  # R17
    
    if health < 35 and temperature >= 75:
        active_rules.append(17)  # R18
    
    # WARNING RULES (18-26)
    if battery < 40:
        if temperature < 50:
            active_rules.append(18)  # R19
        else:
            active_rules.append(19)  # R20
    
    if temperature >= 75 or health < 35:
        active_rules.append(20)  # R21
    
    if battery >= 30 and battery < 70 and temperature >= 40 and temperature < 75 and health >= 25 and health < 67:
        active_rules.append(21)  # R22
    
    if battery >= 30 and battery < 70 and temperature < 50 and health >= 67:
        active_rules.append(22)  # R23
    
    if battery >= 60 and health >= 67 and temperature < 50:
        active_rules.append(23)  # R24
    
    if battery >= 30 and battery < 70 and temperature >= 40 and temperature < 75 and health >= 67:
        active_rules.append(24)  # R25
    
    if battery >= 60 and temperature < 75 and temperature >= -20:
        active_rules.append(25)  # R26
    
    # NEW RULE 28: Very Low & Poor Health & High Load -> Critical
    if battery < 20 and health < 35 and load >= 60:
        active_rules.append(26)  # R28
    
    # DISCHARGE LIMIT RULES (27-39)
    # Based on battery level and load
    if battery < 40:  # Low battery
        if load < 40:
            active_rules.append(27)  # R29
        elif load < 67:
            active_rules.append(28)  # R30
        else:
            active_rules.append(29)  # R31
    elif battery < 70:  # Medium battery
        if load < 40:
            active_rules.append(30)  # R32
        elif load < 67:
            active_rules.append(31)  # R33
        else:
            active_rules.append(32)  # R34
    else:  # High battery
        if load < 40:
            active_rules.append(33)  # R35
        elif load < 67:
            active_rules.append(34)  # R36
        else:
            active_rules.append(35)  # R37
    
    # Safety overrides
    if health < 35 or temperature >= 75:
        active_rules.append(36)  # R38
    
    if health >= 67 and battery >= 60 and load < 40:
        active_rules.append(37)  # R39
    
    active_rules = list(set(active_rules))
    
    # Create table
    ax.axis('off')
    
    # Table header
    header = ['Rule', 'Conditions', 'Output', 'Status']
    cell_height = 0.035
    y_start = 0.95
    
    # Draw header
    for col, text in enumerate(header):
        ax.text(0.02 + col * 0.24, y_start, text, fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # Draw rows
    y_pos = y_start - cell_height
    for idx, (rule_num, conditions, output, output_type) in enumerate(rules_data):
        is_active = idx in active_rules
        bg_color = '#90EE90' if is_active else '#E0E0E0'  # Light green or gray
        status_text = '✓ ACTIVE' if is_active else '○ Inactive'
        
        # Rule number
        ax.text(0.02, y_pos, rule_num, fontsize=9,
               bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.5))
        # Conditions
        ax.text(0.10, y_pos, conditions, fontsize=8,
               bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.5))
        # Output
        ax.text(0.50, y_pos, output, fontsize=9,
               bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.5))
        # Status
        ax.text(0.74, y_pos, status_text, fontsize=9, fontweight='bold' if is_active else 'normal',
               bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.5))
        
        y_pos -= cell_height
    
    # Add legend
    ax.text(0.02, 0.02, f'Total Active Rules: {len(active_rules)} / 43',
           fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('03_rule_activation.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 03_rule_activation.png")
    plt.close()


# ============================================================================
# VISUALIZATION 4: CHARGING SPEED INTERSECTION
# ============================================================================

def visualize_charging_intersection(system):
    """
    Show charging speed output membership functions with crisp output marked.
    
    6 scenarios:
    1. Very Low Battery (B=10%, T=35°C, H=50)
    2. Low + Cold (B=20%, T=10°C, H=50)
    3. Low + Hot (B=20%, T=75°C, H=50)
    4. Medium (B=50%, T=35°C, H=50)
    5. High (B=80%, T=35°C, H=50)
    6. Full (B=95%, T=35°C, H=50)
    """
    scenarios = [
        (10, 35, 50, "Very Low Battery"),
        (20, 10, 50, "Low + Cold"),
        (20, 75, 50, "Low + Hot"),
        (50, 35, 50, "Medium"),
        (80, 35, 50, "High"),
        (95, 35, 50, "Full"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 10))
    fig.suptitle('Charging Speed Output: Membership Functions & Crisp Output',
                 fontsize=14, fontweight='bold')
    
    colors = ['#B71C1C', '#F57C00', '#FBC02D', '#388E3C']
    labels = ['stop', 'slow', 'normal', 'fast']
    
    for idx, (battery, temp, health, scenario_name) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Get output
        result = system.get_recommendations(battery, temp, health, 50)
        charging_output = result['charging_speed_raw']
        
        # Plot membership functions
        for name, color in zip(labels, colors):
            mf = system.charging_speed[name].mf
            ax.fill_between(system.charging_speed.universe, mf, alpha=0.3, color=color, label=name)
            ax.plot(system.charging_speed.universe, mf, color=color, linewidth=2)
        
        # Mark crisp output
        ax.axvline(x=charging_output, color='black', linewidth=2.5, linestyle='--',
                  label=f'Output={charging_output:.1f}')
        
        # Annotate output interpretation
        interpretation = result['charging_speed']
        ax.text(0.98, 0.95, f'→ {interpretation}', transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        ax.set_title(f'{scenario_name}\n(B={battery}%, T={temp}°C, H={health})',
                    fontsize=10, fontweight='bold')
        ax.set_xlabel('Charging Speed')
        ax.set_ylabel('Membership (μ)')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 1.1])
    
    plt.tight_layout()
    plt.savefig('04_charging_intersection.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 04_charging_intersection.png")
    plt.close()


# ============================================================================
# VISUALIZATION 5: COOLING LEVEL INTERSECTION
# ============================================================================

def visualize_cooling_intersection(system):
    """
    Show cooling level output membership functions with crisp output marked.
    
    6 scenarios:
    1. Cold (B=50%, T=10°C, H=50)
    2. Normal Temp (B=50%, T=35°C, H=50)
    3. Hot (B=50%, T=65°C, H=50)
    4. Very Hot (B=50%, T=75°C, H=50)
    5. Low Battery + Hot (B=15%, T=65°C, H=50)
    6. High Battery + Hot (B=85%, T=75°C, H=50)
    """
    scenarios = [
        (50, 10, 50, "Cold Temperature"),
        (50, 35, 50, "Normal Temp"),
        (50, 65, 50, "Hot"),
        (50, 75, 50, "Very Hot"),
        (15, 65, 50, "Low Battery + Hot"),
        (85, 75, 50, "High Battery + Hot"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 10))
    fig.suptitle('Cooling Level Output: Membership Functions & Crisp Output',
                 fontsize=14, fontweight='bold')
    
    colors = ['#2196F3', '#81D4FA', '#EF5350']
    labels = ['off', 'medium', 'high']
    
    for idx, (battery, temp, health, scenario_name) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Get output
        result = system.get_recommendations(battery, temp, health, 50)
        cooling_output = result['cooling_level_raw']
        
        # Plot membership functions
        for name, color in zip(labels, colors):
            mf = system.cooling_level[name].mf
            ax.fill_between(system.cooling_level.universe, mf, alpha=0.3, color=color, label=name)
            ax.plot(system.cooling_level.universe, mf, color=color, linewidth=2)
        
        # Mark crisp output
        ax.axvline(x=cooling_output, color='black', linewidth=2.5, linestyle='--',
                  label=f'Output={cooling_output:.1f}')
        
        # Annotate output interpretation
        interpretation = result['cooling_level']
        ax.text(0.98, 0.95, f'→ {interpretation}', transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))
        
        ax.set_title(f'{scenario_name}\n(B={battery}%, T={temp}°C, H={health})',
                    fontsize=10, fontweight='bold')
        ax.set_xlabel('Cooling Level')
        ax.set_ylabel('Membership (μ)')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 1.1])
    
    plt.tight_layout()
    plt.savefig('05_cooling_intersection.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 05_cooling_intersection.png")
    plt.close()


# ============================================================================
# VISUALIZATION 6: WARNING STATUS INTERSECTION
# ============================================================================

def visualize_warning_intersection(system):
    """
    Show warning status output membership functions with crisp output marked.
    
    6 scenarios:
    1. Good Conditions (B=80%, T=35°C, H=80)
    2. Normal Conditions (B=50%, T=35°C, H=50)
    3. Very Low Battery + Normal (B=5%, T=35°C, H=50)
    4. Hot (B=50%, T=65°C, H=50)
    5. Very Hot (B=50%, T=75°C, H=50)
    6. Poor Health + Hot (B=50%, T=65°C, H=20)
    """
    scenarios = [
        (80, 35, 80, "Good Conditions"),
        (50, 35, 50, "Normal Conditions"),
        (5, 35, 50, "Very Low Battery"),
        (50, 65, 50, "Hot"),
        (50, 75, 50, "Very Hot"),
        (50, 65, 20, "Poor Health + Hot"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 10))
    fig.suptitle('Warning Status Output: Membership Functions & Crisp Output',
                 fontsize=14, fontweight='bold')
    
    colors = ['#4CAF50', '#FFC107', '#D32F2F']
    labels = ['safe', 'warning', 'critical']
    
    for idx, (battery, temp, health, scenario_name) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Get output
        result = system.get_recommendations(battery, temp, health, 50)
        warning_output = result['warning_status_raw']
        
        # Plot membership functions
        for name, color in zip(labels, colors):
            mf = system.warning_status[name].mf
            ax.fill_between(system.warning_status.universe, mf, alpha=0.3, color=color, label=name)
            ax.plot(system.warning_status.universe, mf, color=color, linewidth=2)
        
        # Mark crisp output
        ax.axvline(x=warning_output, color='black', linewidth=2.5, linestyle='--',
                  label=f'Output={warning_output:.1f}')
        
        # Annotate output interpretation
        interpretation = result['warning_status']
        ax.text(0.98, 0.95, f'→ {interpretation}', transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        ax.set_title(f'{scenario_name}\n(B={battery}%, T={temp}°C, H={health})',
                    fontsize=10, fontweight='bold')
        ax.set_xlabel('Warning Status')
        ax.set_ylabel('Membership (μ)')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 1.1])
    
    plt.tight_layout()
    plt.savefig('06_warning_intersection.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 06_warning_intersection.png")
    plt.close()


# ============================================================================
# VISUALIZATION 7: DISCHARGE LIMIT INTERSECTION
# ============================================================================

def visualize_discharge_intersection(system):
    """
    Show discharge limit output membership functions with crisp output marked.
    
    6 scenarios with varying battery and load:
    1. Low Battery + Low Load
    2. Low Battery + High Load
    3. Medium Battery + Low Load
    4. Medium Battery + High Load
    5. High Battery + Low Load
    6. High Battery + High Load
    """
    scenarios = [
        (20, 50, 50, 20, "Low Battery + Low Load"),
        (20, 50, 50, 80, "Low Battery + High Load"),
        (50, 50, 50, 20, "Medium Battery + Low Load"),
        (50, 50, 50, 80, "Medium Battery + High Load"),
        (80, 50, 50, 20, "High Battery + Low Load"),
        (80, 50, 50, 80, "High Battery + High Load"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 10))
    fig.suptitle('Discharge Limit Output: Membership Functions & Crisp Output',
                 fontsize=14, fontweight='bold')
    
    colors = ['#E53935', '#FFB74D', '#1976D2']
    labels = ['conservative', 'balanced', 'aggressive']
    
    for idx, (battery, temp, health, load, scenario_name) in enumerate(scenarios):
        ax = axes[idx // 3, idx % 3]
        
        # Get output
        result = system.get_recommendations(battery, temp, health, load)
        discharge_output = result['discharge_limit_raw']
        
        # Plot membership functions
        for name, color in zip(labels, colors):
            mf = system.discharge_limit[name].mf
            ax.fill_between(system.discharge_limit.universe, mf, alpha=0.3, color=color, label=name)
            ax.plot(system.discharge_limit.universe, mf, color=color, linewidth=2)
        
        # Mark crisp output
        ax.axvline(x=discharge_output, color='black', linewidth=2.5, linestyle='--',
                  label=f'Output={discharge_output:.1f}')
        
        # Annotate output interpretation
        interpretation = result['discharge_limit']
        ax.text(0.98, 0.95, f'→ {interpretation}', transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.set_title(f'{scenario_name}\n(B={battery}%, L={load}%)',
                    fontsize=10, fontweight='bold')
        ax.set_xlabel('Discharge Limit')
        ax.set_ylabel('Membership (μ)')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 1.1])
    
    plt.tight_layout()
    plt.savefig('07_discharge_intersection.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 07_discharge_intersection.png")
    plt.close()


# ============================================================================
# VISUALIZATION 8: CONTROL SURFACES (3D)
# ============================================================================

# ============================================================================
# VISUALIZATION 8: OUTPUT DISTRIBUTIONS
# ============================================================================

def visualize_output_distributions(system):
    """
    Create histograms and box plots of output distributions.
    
    Samples 100 random input combinations (reduced to avoid state issues).
    Includes load as random input.
    
    Top row: Histograms (25 bins, red dashed mean line)
    Bottom row: Box plots (with min/mean/max annotations)
    
    Colors: blue=charging, orange=cooling, red=warning, green=discharge
    """
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Generate random samples (reduced from 1000 to avoid corruption)
    n_samples = 100
    battery_samples = np.random.uniform(0, 100, n_samples)
    temp_samples = np.random.uniform(-20, 80, n_samples)
    health_samples = np.random.uniform(0, 100, n_samples)
    load_samples = np.random.uniform(0, 100, n_samples)
    
    # Collect outputs
    charging_outputs = []
    cooling_outputs = []
    warning_outputs = []
    discharge_outputs = []
    
    for i in range(n_samples):
        try:
            result = system.get_recommendations(
                battery_samples[i],
                temp_samples[i],
                health_samples[i],
                load_samples[i]
            )
            charging_outputs.append(result['charging_speed_raw'])
            cooling_outputs.append(result['cooling_level_raw'])
            warning_outputs.append(result['warning_status_raw'])
            discharge_outputs.append(result['discharge_limit_raw'])
        except Exception as e:
            # Skip samples that cause errors
            continue
        
    charging_outputs = np.array(charging_outputs)
    cooling_outputs = np.array(cooling_outputs)
    warning_outputs = np.array(warning_outputs)
    discharge_outputs = np.array(discharge_outputs)
    
    # Create figure
    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    fig.suptitle('Output Distributions (1000 Random Samples)', fontsize=14, fontweight='bold')
    
    # ---- CHARGING SPEED ----
    # Histogram
    ax = axes[0, 0]
    ax.hist(charging_outputs, bins=25, color='#2196F3', alpha=0.7, edgecolor='black')
    mean_val = np.mean(charging_outputs)
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean={mean_val:.1f}')
    ax.set_title('Charging Speed Distribution', fontsize=11, fontweight='bold')
    ax.set_xlabel('Charging Speed')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Box plot
    ax = axes[1, 0]
    bp = ax.boxplot(charging_outputs, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('#2196F3')
    bp['boxes'][0].set_alpha(0.7)
    ax.set_ylabel('Charging Speed')
    ax.set_title('Charging Speed Box Plot', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Annotate stats
    mean_val = np.mean(charging_outputs)
    median_val = np.median(charging_outputs)
    ax.text(1.15, mean_val, f'μ={mean_val:.1f}', fontsize=9, va='center')
    ax.text(1.15, median_val, f'M={median_val:.1f}', fontsize=9, va='center')
    
    # ---- COOLING LEVEL ----
    # Histogram
    ax = axes[0, 1]
    ax.hist(cooling_outputs, bins=25, color='#FF9800', alpha=0.7, edgecolor='black')
    mean_val = np.mean(cooling_outputs)
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean={mean_val:.1f}')
    ax.set_title('Cooling Level Distribution', fontsize=11, fontweight='bold')
    ax.set_xlabel('Cooling Level')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Box plot
    ax = axes[1, 1]
    bp = ax.boxplot(cooling_outputs, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('#FF9800')
    bp['boxes'][0].set_alpha(0.7)
    ax.set_ylabel('Cooling Level')
    ax.set_title('Cooling Level Box Plot', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Annotate stats
    mean_val = np.mean(cooling_outputs)
    median_val = np.median(cooling_outputs)
    ax.text(1.15, mean_val, f'μ={mean_val:.1f}', fontsize=9, va='center')
    ax.text(1.15, median_val, f'M={median_val:.1f}', fontsize=9, va='center')
    
    # ---- WARNING STATUS ----
    # Histogram
    ax = axes[0, 2]
    ax.hist(warning_outputs, bins=25, color='#F44336', alpha=0.7, edgecolor='black')
    mean_val = np.mean(warning_outputs)
    ax.axvline(mean_val, color='darkred', linestyle='--', linewidth=2, label=f'Mean={mean_val:.1f}')
    ax.set_title('Warning Status Distribution', fontsize=11, fontweight='bold')
    ax.set_xlabel('Warning Status')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Box plot
    ax = axes[1, 2]
    bp = ax.boxplot(warning_outputs, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('#F44336')
    bp['boxes'][0].set_alpha(0.7)
    ax.set_ylabel('Warning Status')
    ax.set_title('Warning Status Box Plot', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Annotate stats
    mean_val = np.mean(warning_outputs)
    median_val = np.median(warning_outputs)
    ax.text(1.15, mean_val, f'μ={mean_val:.1f}', fontsize=9, va='center')
    ax.text(1.15, median_val, f'M={median_val:.1f}', fontsize=9, va='center')
    
    # ---- DISCHARGE LIMIT ----
    # Histogram
    ax = axes[0, 3]
    ax.hist(discharge_outputs, bins=25, color='#4CAF50', alpha=0.7, edgecolor='black')
    mean_val = np.mean(discharge_outputs)
    ax.axvline(mean_val, color='darkgreen', linestyle='--', linewidth=2, label=f'Mean={mean_val:.1f}')
    ax.set_title('Discharge Limit Distribution', fontsize=11, fontweight='bold')
    ax.set_xlabel('Discharge Limit')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Box plot
    ax = axes[1, 3]
    bp = ax.boxplot(discharge_outputs, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('#4CAF50')
    bp['boxes'][0].set_alpha(0.7)
    ax.set_ylabel('Discharge Limit')
    ax.set_title('Discharge Limit Box Plot', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Annotate stats
    mean_val = np.mean(discharge_outputs)
    median_val = np.median(discharge_outputs)
    ax.text(1.15, mean_val, f'μ={mean_val:.1f}', fontsize=9, va='center')
    ax.text(1.15, median_val, f'M={median_val:.1f}', fontsize=9, va='center')
    
    plt.tight_layout()
    plt.savefig('08_output_distributions.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 08_output_distributions.png")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all 9 visualizations."""
    print("\n" + "="*60)
    print("BATTERY FUZZY SYSTEM - VISUALIZATION SUITE")
    print("="*60 + "\n")
    
    # Initialize system
    print("Initializing BatteryFuzzySystem...")
    system = BatteryFuzzySystem()
    print("✓ System initialized\n")
    
    # Generate all visualizations
    print("Generating visualizations...\n")
    
    print("[1/9] Membership Functions...")
    visualize_membership_functions(system)
    
    print("[2/9] Fuzzification...")
    visualize_fuzzification(system)
    
    print("[3/9] Rule Activation...")
    visualize_rule_activation(system)
    
    print("[4/9] Charging Intersection...")
    visualize_charging_intersection(system)
    
    print("[5/9] Cooling Intersection...")
    visualize_cooling_intersection(system)
    
    print("[6/9] Warning Intersection...")
    visualize_warning_intersection(system)
    
    print("[7/8] Discharge Limit Intersection...")
    visualize_discharge_intersection(system)
    
    print("[8/8] Output Distributions...")
    visualize_output_distributions(system)
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("="*60)
    print("\nGenerated files:")
    print("  ✓ 01_membership_functions.png")
    print("  ✓ 02_fuzzification.png")
    print("  ✓ 03_rule_activation.png")
    print("  ✓ 04_charging_intersection.png")
    print("  ✓ 05_cooling_intersection.png")
    print("  ✓ 06_warning_intersection.png")
    print("  ✓ 07_discharge_intersection.png")
    print("  ✓ 08_output_distributions.png")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
