"""
Per-variable plots for the Battery Fuzzy System.

Where `vis.py` packs every membership function into one 3x3 grid figure, this
module emits one PNG per fuzzy variable, plus a per-scenario rule-firing
bar chart, so each can be embedded individually in the Arabic technical
report (see `report_ar.py`).

Outputs are written to `figs/` next to this file, named with a 2-digit prefix
so they sort the same order they appear in the report:

    figs/mf_01_battery_level.png      ...      figs/mf_08_discharge_limit.png
    figs/rule_firings.png             (firing strengths for one scenario)

Usage:
    python3 vis2.py                 # generate all PNGs into ./figs/
    python3 vis2.py --out my_dir/   # custom output directory
"""

from __future__ import annotations

import argparse
import os

import matplotlib.pyplot as plt

from battery_fuzzy_system import BatteryFuzzySystem


# Plot specification per variable: which Antecedent/Consequent attribute on the
# system to read, which membership-function term names to plot in which order,
# matching color palette, x-range, axis labels (kept in English/Latin so they
# stay legible alongside the Arabic body text), and the PNG filename.
VARIABLE_PLOTS = [
    {
        'attr': 'battery_level',
        'terms': ['very_low', 'low', 'medium', 'high', 'full'],
        'colors': ['#FF6B6B', '#FF8E72', '#FFD93D', '#6BCB77', '#4D96FF'],
        'xlim': (0, 100),
        'title': 'Battery Level (0-100%)',
        'xlabel': 'Battery Level (%)',
        'filename': 'mf_01_battery_level.png',
    },
    {
        'attr': 'temperature',
        'terms': ['cold', 'normal', 'hot', 'very_hot'],
        'colors': ['#1E88E5', '#90CAF9', '#FFA726', '#E53935'],
        'xlim': (-20, 80),
        'title': 'Temperature (-20 to 80 C)',
        'xlabel': 'Temperature (C)',
        'filename': 'mf_02_temperature.png',
    },
    {
        'attr': 'health',
        'terms': ['poor', 'average', 'good'],
        'colors': ['#E53935', '#FFB74D', '#81C784'],
        'xlim': (0, 100),
        'title': 'Battery Health (0-100)',
        'xlabel': 'Health',
        'filename': 'mf_03_health.png',
    },
    {
        'attr': 'load',
        'terms': ['low', 'medium', 'high'],
        'colors': ['#1976D2', '#81D4FA', '#D32F2F'],
        'xlim': (0, 100),
        'title': 'Load (0-100)',
        'xlabel': 'Load',
        'filename': 'mf_04_load.png',
    },
    {
        'attr': 'charging_speed',
        'terms': ['stop', 'slow', 'normal', 'fast'],
        'colors': ['#B71C1C', '#F57C00', '#FBC02D', '#388E3C'],
        'xlim': (0, 100),
        'title': 'Charging Speed (0-100)',
        'xlabel': 'Charging Speed',
        'filename': 'mf_05_charging_speed.png',
    },
    {
        'attr': 'cooling_level',
        'terms': ['off', 'medium', 'high'],
        'colors': ['#2196F3', '#81D4FA', '#EF5350'],
        'xlim': (0, 100),
        'title': 'Cooling Level (0-100)',
        'xlabel': 'Cooling Level',
        'filename': 'mf_06_cooling_level.png',
    },
    {
        'attr': 'warning_status',
        'terms': ['safe', 'warning', 'critical'],
        'colors': ['#4CAF50', '#FFC107', '#D32F2F'],
        'xlim': (0, 100),
        'title': 'Warning Status (0-100)',
        'xlabel': 'Warning Status',
        'filename': 'mf_07_warning_status.png',
    },
    {
        'attr': 'discharge_limit',
        'terms': ['conservative', 'balanced', 'aggressive'],
        'colors': ['#E53935', '#FFB74D', '#1976D2'],
        'xlim': (0, 100),
        'title': 'Discharge Limit (0-100)',
        'xlabel': 'Discharge Limit',
        'filename': 'mf_08_discharge_limit.png',
    },
]


def _plot_one(system: BatteryFuzzySystem, spec: dict, out_path: str) -> None:
    """Render a single variable's membership functions to a PNG."""
    variable = getattr(system, spec['attr'])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for term, color in zip(spec['terms'], spec['colors']):
        mf = variable[term].mf
        ax.fill_between(variable.universe, mf, alpha=0.3, color=color, label=term)
        ax.plot(variable.universe, mf, color=color, linewidth=2)

    ax.set_title(spec['title'], fontsize=12, fontweight='bold')
    ax.set_xlabel(spec['xlabel'])
    ax.set_ylabel('Membership (mu)')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(spec['xlim'])
    ax.set_ylim([0, 1.1])

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def visualize_rule_firings(
    system: BatteryFuzzySystem,
    scenario: tuple[float, float, float, float],
    out_path: str,
) -> dict:
    """
    Render a horizontal bar chart of every rule's firing strength for one
    scenario.

    Bars are colored by which output variable the rule influences, so the
    reader can immediately see which sub-system each active rule belongs to
    (charging speed / cooling / warning / discharge). Inactive rules
    (strength <= 0.01) are drawn in light gray for visual completeness; the
    text annotation at the right of every active bar shows its exact mu.

    Returns a dict summarizing the run:
        {'inputs': (b, t, h, l), 'outputs': {...}, 'active_rule_count': N}
    so the caller can describe the scenario in the surrounding report copy.
    """
    battery, temperature, health, load = scenario
    outputs = system.get_recommendations(battery, temperature, health, load)

    # Read each rule's firing strength after compute(). For an unfired rule
    # the membership_value dict may not contain the simulation key at all.
    strengths = []
    for rule, info in zip(system.rules, system.rule_info):
        name, _desc_en, output_var = info
        try:
            mu = float(rule.antecedent.membership_value[system.simulation])
        except Exception:
            mu = 0.0
        strengths.append((name, output_var, mu))

    output_colors = {
        'charging_speed':  '#1976D2',
        'cooling_level':   '#0097A7',
        'warning_status':  '#D32F2F',
        'discharge_limit': '#388E3C',
    }
    inactive_color = '#E0E0E0'

    n = len(strengths)
    fig, ax = plt.subplots(figsize=(10, max(8, n * 0.22)))

    y_positions = list(range(n))
    # Plot top-to-bottom in rule order, so reverse y so R1 is on top.
    for i, (name, output_var, mu) in enumerate(strengths):
        y = n - 1 - i
        color = output_colors.get(output_var, '#999') if mu > 0.01 else inactive_color
        ax.barh(y, mu if mu > 0.01 else 0.005, color=color,
                edgecolor='#444' if mu > 0.01 else '#CCC', linewidth=0.5)
        if mu > 0.01:
            ax.text(min(mu + 0.01, 1.02), y, f' {mu:.2f}',
                    va='center', ha='left', fontsize=8, fontweight='bold',
                    color='#222')

    ax.set_yticks([n - 1 - i for i in range(n)])
    ax.set_yticklabels([name for name, _, _ in strengths], fontsize=8)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel('Firing strength (mu)', fontsize=10)
    ax.set_title(
        f'Rule firings for scenario: '
        f'battery={battery}, temperature={temperature}, '
        f'health={health}, load={load}',
        fontsize=11, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.25)

    # Legend for the output-variable color mapping.
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=output_colors[v])
        for v in ['charging_speed', 'cooling_level', 'warning_status', 'discharge_limit']
    ]
    handles.append(plt.Rectangle((0, 0), 1, 1, color=inactive_color))
    labels = ['charging_speed', 'cooling_level', 'warning_status', 'discharge_limit',
              'inactive (mu <= 0.01)']
    ax.legend(handles, labels, loc='lower right', fontsize=9,
              framealpha=0.95)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches='tight')
    plt.close(fig)

    active = sum(1 for _, _, mu in strengths if mu > 0.01)
    return {'inputs': scenario, 'outputs': outputs, 'active_rule_count': active,
            'total_rule_count': n}


def generate_all(out_dir: str = 'figs', system: BatteryFuzzySystem | None = None,
                 firing_scenario: tuple[float, float, float, float] | None = None,
                 ) -> list[str]:
    """
    Generate one PNG per fuzzy variable plus the rule-firings figure.

    Returns the list of written file paths in canonical order.
    """
    os.makedirs(out_dir, exist_ok=True)
    if system is None:
        system = BatteryFuzzySystem()

    written: list[str] = []
    for spec in VARIABLE_PLOTS:
        path = os.path.join(out_dir, spec['filename'])
        _plot_one(system, spec, path)
        written.append(path)
        print(f'wrote {path}')

    if firing_scenario is not None:
        path = os.path.join(out_dir, 'rule_firings.png')
        visualize_rule_firings(system, firing_scenario, path)
        written.append(path)
        print(f'wrote {path}')

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--out', default='figs',
        help='Output directory for the PNGs (default: ./figs)',
    )
    parser.add_argument(
        '--firing-scenario', nargs=4, type=float, metavar=('B', 'T', 'H', 'L'),
        help='Also write figs/rule_firings.png for this scenario '
             '(battery, temperature, health, load).',
    )
    args = parser.parse_args()
    scenario = tuple(args.firing_scenario) if args.firing_scenario else None
    generate_all(args.out, firing_scenario=scenario)


if __name__ == '__main__':
    main()
