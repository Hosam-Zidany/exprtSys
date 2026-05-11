"""
Per-variable membership-function plots for the Battery Fuzzy System.

Where `vis.py` packs every membership function into one 3x3 grid figure, this
module emits one PNG per fuzzy variable so each one can be embedded
individually in the Arabic technical report (see `report_ar.py`).

Outputs are written to `figs/` next to this file, named with a 2-digit prefix
so they sort the same order they appear in the report:

    figs/mf_01_battery_level.png
    figs/mf_02_temperature.png
    figs/mf_03_health.png
    figs/mf_04_load.png
    figs/mf_05_charging_speed.png
    figs/mf_06_cooling_level.png
    figs/mf_07_warning_status.png
    figs/mf_08_discharge_limit.png

Usage:
    python3 vis2.py                 # generate all 8 PNGs into ./figs/
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


def generate_all(out_dir: str = 'figs', system: BatteryFuzzySystem | None = None) -> list[str]:
    """
    Generate one PNG per fuzzy variable.

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
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--out', default='figs',
        help='Output directory for the PNGs (default: ./figs)',
    )
    args = parser.parse_args()
    generate_all(args.out)


if __name__ == '__main__':
    main()
