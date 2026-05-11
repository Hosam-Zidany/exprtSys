"""
Generate an Arabic (RTL) technical report for the Battery Fuzzy System.

The report covers the three sections requested by the project owner:

    1.  مخطط هندسة المعرفة      (knowledge engineering diagram + membership functions)
    2.  هيكلية القواعد          (the 46 Mamdani rules grouped by consequent)
    3.  عينة من حالات الاختبار   (sample test scenarios with inputs and outputs)

Page numbering starts at 2 because the project owner maintains a separate
template for page 1 and concatenates it ahead of this PDF.

Usage:
    python3 report_ar.py                  # writes report_ar.pdf in cwd
    python3 report_ar.py --out report.pdf # custom path
"""

from __future__ import annotations

import argparse
import html
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from weasyprint import CSS, HTML

import vis2
from battery_fuzzy_system import BatteryFuzzySystem


# ---------------------------------------------------------------------------
# Arabic glossary
# ---------------------------------------------------------------------------
#
# Mapping from code-level term names to their Arabic equivalents used in body
# text. Identifier strings (e.g. table headers tied to keys returned by
# get_recommendations) are kept in English/Latin so they match the API.

VAR_AR = {
    'battery_level':   'مستوى البطارية',
    'temperature':     'درجة الحرارة',
    'health':          'صحة البطارية',
    'load':            'الحمل',
    'charging_speed':  'سرعة الشحن',
    'cooling_level':   'مستوى التبريد',
    'warning_status':  'حالة التحذير',
    'discharge_limit': 'حد التفريغ',
}

TERM_AR = {
    # battery_level
    'very_low': 'منخفض جدًا', 'low': 'منخفض', 'medium': 'متوسط',
    'high': 'مرتفع', 'full': 'ممتلئ',
    # temperature
    'cold': 'بارد', 'normal': 'عادي', 'hot': 'حار', 'very_hot': 'حار جدًا',
    # health
    'poor': 'سيئة', 'average': 'متوسطة', 'good': 'جيدة',
    # charging_speed
    'stop': 'إيقاف', 'slow': 'بطيء', 'fast': 'سريع',
    # cooling_level
    'off': 'إيقاف',
    # warning_status
    'safe': 'آمن', 'warning': 'تحذير', 'critical': 'حرج',
    # discharge_limit
    'conservative': 'متحفظ', 'balanced': 'متوازن', 'aggressive': 'مكثف',
}


# ---------------------------------------------------------------------------
# Helper: build the knowledge-engineering architecture diagram
# ---------------------------------------------------------------------------

def _draw_architecture_diagram(out_path: str) -> None:
    """
    Render a simple 3-stage block diagram:
        [4 inputs]  ->  [fuzzy inference engine]  ->  [4 outputs]
    Variable names stay in English/Latin because they mirror the code
    identifiers; the surrounding Arabic body text explains them.
    """
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')

    inputs = ['battery_level', 'temperature', 'health', 'load']
    outputs = ['charging_speed', 'cooling_level', 'warning_status', 'discharge_limit']

    # Left column: inputs.
    for i, name in enumerate(inputs):
        y = 4.6 - i * 1.05
        box = mpatches.FancyBboxPatch(
            (0.3, y), 2.6, 0.7,
            boxstyle='round,pad=0.05', linewidth=1.5,
            edgecolor='#1976D2', facecolor='#E3F2FD',
        )
        ax.add_patch(box)
        ax.text(1.6, y + 0.35, name, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#0D47A1')

    # Centre: inference engine.
    engine = mpatches.FancyBboxPatch(
        (4.2, 1.3), 2.6, 3.4,
        boxstyle='round,pad=0.1', linewidth=2.0,
        edgecolor='#6A1B9A', facecolor='#F3E5F5',
    )
    ax.add_patch(engine)
    ax.text(5.5, 3.6, 'Fuzzy Inference\n(Mamdani)', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#4A148C')
    ax.text(5.5, 2.5, '46 rules\nmin/max + centroid', ha='center', va='center',
            fontsize=9, color='#4A148C')

    # Right column: outputs.
    for i, name in enumerate(outputs):
        y = 4.6 - i * 1.05
        box = mpatches.FancyBboxPatch(
            (8.1, y), 2.6, 0.7,
            boxstyle='round,pad=0.05', linewidth=1.5,
            edgecolor='#2E7D32', facecolor='#E8F5E9',
        )
        ax.add_patch(box)
        ax.text(9.4, y + 0.35, name, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#1B5E20')

    # Arrows: inputs -> engine, engine -> outputs.
    for i in range(4):
        y_in = 4.6 - i * 1.05 + 0.35
        ax.annotate('', xy=(4.2, y_in), xytext=(2.9, y_in),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#1976D2'))
        y_out = 4.6 - i * 1.05 + 0.35
        ax.annotate('', xy=(8.1, y_out), xytext=(6.8, y_out),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#2E7D32'))

    # Layer captions.
    ax.text(1.6, 5.6, 'Inputs (Antecedents)', ha='center', fontsize=11,
            fontweight='bold', color='#0D47A1')
    ax.text(5.5, 5.6, 'Inference Engine', ha='center', fontsize=11,
            fontweight='bold', color='#4A148C')
    ax.text(9.4, 5.6, 'Outputs (Consequents)', ha='center', fontsize=11,
            fontweight='bold', color='#1B5E20')

    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# Helper: rule descriptions in Arabic
# ---------------------------------------------------------------------------

# Map of rule name -> Arabic description. The English descriptions in
# `system.rule_info` stay as the source of truth for engineers; this dict is
# the Arabic translation used in the report body only.
RULE_AR = {
    'R1':  'بطارية منخفضة جدًا + درجة حرارة عادية → شحن سريع',
    'R2':  'بطارية منخفضة جدًا + حرارة مرتفعة → شحن بطيء',
    'R3':  'بطارية منخفضة + درجة حرارة عادية → شحن سريع',
    'R4':  'بطارية منخفضة + حرارة مرتفعة → شحن بطيء',
    'R5':  'بطارية متوسطة + درجة حرارة عادية/حارة → شحن عادي',
    'R6':  'بطارية متوسطة + حرارة حارة جدًا → شحن بطيء',
    'R7':  'بطارية مرتفعة/ممتلئة + درجة حرارة عادية → شحن بطيء',
    'R8':  'بطارية مرتفعة/ممتلئة + حرارة مرتفعة → إيقاف الشحن',
    'R9':  'صحة سيئة + درجة حرارة عادية → شحن بطيء',
    'R10': 'صحة سيئة + حرارة مرتفعة → إيقاف الشحن',
    'R11': 'حرارة عادية + بطارية منخفضة/متوسطة → تبريد متوقف',
    'R12': 'حرارة عادية + بطارية مرتفعة/ممتلئة → تبريد متوقف',
    'R13': 'درجة حرارة حارة + بطارية منخفضة → تبريد عالٍ',
    'R14': 'درجة حرارة حارة + بطارية متوسطة → تبريد متوسط',
    'R15': 'درجة حرارة حارة + بطارية مرتفعة → تبريد متوسط',
    'R16': 'حرارة حارة جدًا + بطارية منخفضة → تبريد عالٍ',
    'R17': 'حرارة حارة جدًا + بطارية متوسطة/مرتفعة → تبريد عالٍ',
    'R18': 'صحة سيئة + حرارة مرتفعة → تبريد عالٍ',
    'R19': 'بطارية منخفضة + درجة حرارة عادية → تحذير',
    'R20': 'بطارية منخفضة + حرارة مرتفعة → حرج',
    'R21': 'حرارة حارة جدًا أو صحة سيئة → حرج',
    'R22': 'بطارية متوسطة + حرارة حارة + صحة متوسطة → تحذير',
    'R23': 'بطارية متوسطة + درجة حرارة عادية + صحة جيدة → آمن',
    'R24': 'بطارية مرتفعة/ممتلئة + صحة جيدة + درجة حرارة عادية → آمن',
    'R25': 'بطارية متوسطة + حرارة حارة + صحة جيدة → تحذير',
    'R26': 'بطارية مرتفعة/ممتلئة + درجة حرارة معتدلة → آمن',
    'R27': 'بطارية متوسطة + حرارة مرتفعة + صحة سيئة → تحذير',
    'R28': 'بطارية منخفضة جدًا + صحة سيئة + حمل مرتفع → حرج',
    'R29': 'بطارية منخفضة جدًا + صحة جيدة → تفريغ متحفظ',
    'R30': 'بطارية منخفضة + صحة سيئة/متوسطة → تفريغ متحفظ',
    'R31': 'بطارية متوسطة + حمل منخفض → تفريغ مكثف',
    'R32': 'بطارية متوسطة + حمل متوسط/مرتفع → تفريغ متوازن',
    'R33': 'بطارية مرتفعة + حمل منخفض → تفريغ متوازن',
    'R34': 'بطارية مرتفعة + حمل متوسط/مرتفع → تفريغ مكثف',
    'R35': 'بطارية ممتلئة + حمل منخفض → تفريغ مكثف',
    'R36': 'بطارية ممتلئة + حمل متوسط/مرتفع → تفريغ متوازن',
    'R37': 'صحة سيئة + حمل متوسط/مرتفع → تفريغ متحفظ',
    'R38': '(صحة سيئة أو حرارة حارة جدًا) + بطارية منخفضة → تفريغ متحفظ',
    'R39': 'حرارة حارة جدًا + بطارية منخفضة جدًا → تفريغ متحفظ',
    'R40': 'بطارية متوسطة + صحة سيئة → شحن بطيء',
    'R41': 'بطارية متوسطة + درجة حرارة عادية + صحة متوسطة → آمن',
    'R42': 'حرارة حارة جدًا → إيقاف الشحن',
    'R43': 'بطارية منخفضة جدًا → تفريغ متحفظ (قاعدة احتياطية)',
    'R44': 'بطارية منخفضة → تفريغ متحفظ (قاعدة احتياطية)',
    'R45': 'بطارية منخفضة جدًا + درجة حرارة باردة → شحن بطيء (أمان ليثيوم-أيون)',
    'R46': 'بطارية منخفضة + درجة حرارة باردة → شحن بطيء (أمان ليثيوم-أيون)',
}

# Test scenarios picked from `battery_test_runner.py` plus two extras that
# exercise the corner-cases the system was hardened against (cold-charging
# safety, very-hot/full-battery contradiction).
SCENARIO_LABELS_AR = [
    ('انخفاض شديد + شحن طبيعي',           (10, 25, 70, 50)),
    ('بطارية منخفضة + جو بارد',           (20, -10, 85, 30)),
    ('وضع طبيعي',                         (50, 25, 80, 50)),
    ('استخدام مكثف في الجو الحار',        (30, 65, 50, 80)),
    ('بطارية ممتلئة + حرارة عالية جدًا',  (95, 78, 80, 20)),
    ('صحة سيئة + شحن منخفض',              (40, 30, 25, 70)),
    ('بطارية مرتفعة + حمل منخفض',         (80, 22, 90, 15)),
]


# ---------------------------------------------------------------------------
# HTML / CSS rendering
# ---------------------------------------------------------------------------

# The PDF is in Arabic, so the document direction is RTL. Body counter starts
# at 1 so the first rendered page (after auto-increment) shows as "2".
_CSS = """
@page {
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
    @bottom-center {
        content: "صفحة " counter(page);
        font-family: 'Noto Naskh Arabic', 'Noto Kufi Arabic', serif;
        font-size: 10pt;
        color: #555;
    }
}
/* Project owner concatenates a separate page-1 template ahead of this
 * PDF, so our first rendered page must be numbered 2. WeasyPrint
 * auto-increments the page counter at the start of each page; on the
 * first page we override that increment to +2 instead of +1, so the
 * counter goes 0 -> 2 and subsequent pages keep adding +1 (3, 4, ...). */
@page :first {
    counter-increment: page 2;
}
html { font-family: 'Noto Naskh Arabic', 'Noto Kufi Arabic', serif; }
body {
    font-size: 11pt;
    line-height: 1.7;
    color: #222;
}
h1 {
    font-size: 20pt;
    color: #0D47A1;
    border-bottom: 2px solid #0D47A1;
    padding-bottom: 4mm;
    margin-top: 0;
    page-break-before: always;
}
h1.first { page-break-before: avoid; }
h2 {
    font-size: 14pt;
    color: #1B5E20;
    margin-top: 6mm;
    margin-bottom: 2mm;
}
h3 {
    font-size: 12pt;
    color: #4A148C;
    margin-top: 4mm;
    margin-bottom: 1mm;
}
p { margin: 2mm 0; text-align: justify; }
figure { text-align: center; margin: 4mm 0; page-break-inside: avoid; }
figure img { max-width: 100%; height: auto; }
figcaption {
    font-size: 9.5pt;
    color: #555;
    margin-top: 1mm;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 2mm 0 4mm 0;
    font-size: 9.5pt;
    page-break-inside: auto;
}
th, td {
    border: 1px solid #BBB;
    padding: 1.5mm 2mm;
    text-align: right;
    vertical-align: top;
}
th {
    background-color: #E3F2FD;
    color: #0D47A1;
    font-weight: bold;
}
tr:nth-child(even) td { background-color: #FAFAFA; }
.scenario-out { font-family: 'DejaVu Sans Mono', monospace; direction: ltr;
                text-align: left; font-size: 9pt; }
.note { background: #FFF8E1; border-right: 4px solid #F9A825;
        padding: 2mm 3mm; margin: 3mm 0; font-size: 10pt; }
"""


def _img_tag(path: str, caption_ar: str) -> str:
    """Embed an image as <figure> with an Arabic caption."""
    abs_path = os.path.abspath(path)
    return (
        '<figure>'
        f'<img src="file://{abs_path}" alt="{html.escape(caption_ar)}" />'
        f'<figcaption>{html.escape(caption_ar)}</figcaption>'
        '</figure>'
    )


def _rule_table_html(rule_info: list, output_var: str, header_ar: str) -> str:
    """Render the rules for one output variable as an Arabic table."""
    rows = []
    for name, _desc_en, var in rule_info:
        if var != output_var:
            continue
        ar = RULE_AR.get(name, '')
        rows.append(
            f'<tr><td style="width: 8%; font-weight: bold;">{name}</td>'
            f'<td>{html.escape(ar)}</td></tr>'
        )
    body = '\n'.join(rows)
    return (
        f'<h3>{html.escape(header_ar)} ({VAR_AR[output_var]})</h3>'
        '<table>'
        '<thead><tr><th style="width: 8%;">القاعدة</th>'
        '<th>الوصف</th></tr></thead>'
        f'<tbody>{body}</tbody>'
        '</table>'
    )


def _scenarios_table_html(system: BatteryFuzzySystem) -> str:
    """Run each scenario through the controller and render the result table."""
    rows = []
    for label, (b, t, h, l) in SCENARIO_LABELS_AR:
        r = system.get_recommendations(b, t, h, l)
        # Inputs and raw values are rendered LTR/monospace so the digits stay
        # visually grouped despite the surrounding RTL flow.
        rows.append(f"""
        <tr>
          <td>{html.escape(label)}</td>
          <td class="scenario-out">B={b}, T={t}, H={h}, L={l}</td>
          <td class="scenario-out">
            charging_speed = {r['charging_speed']} ({r['charging_speed_raw']})<br/>
            cooling_level  = {r['cooling_level']} ({r['cooling_level_raw']})<br/>
            warning_status = {r['warning_status']} ({r['warning_status_raw']})<br/>
            discharge_limit = {r['discharge_limit']} ({r['discharge_limit_raw']})
          </td>
        </tr>
        """)
    return (
        '<table>'
        '<thead><tr>'
        '<th style="width: 22%;">الحالة</th>'
        '<th style="width: 23%;">المدخلات</th>'
        '<th>المخرجات</th>'
        '</tr></thead>'
        '<tbody>' + '\n'.join(rows) + '</tbody>'
        '</table>'
    )


def _build_html(system: BatteryFuzzySystem, fig_dir: str) -> str:
    """Assemble the full Arabic HTML document."""
    arch_img = os.path.join(fig_dir, 'architecture.png')

    # Section 1 - knowledge engineering diagram + membership functions.
    section1 = f"""
    <h1 class="first">1. مخطط هندسة المعرفة</h1>

    <p>يستند النظام إلى محرّك استدلال ضبابي من نوع Mamdani يضمّ
    أربعة مدخلات (قدمات / Antecedents) وأربعة مخرجات (نتائج / Consequents)،
    تتصل ببعضها عبر قاعدة مكوّنة من <strong>46</strong> قاعدة استدلال.
    تتم عملية الاستدلال باستخدام عملياتَي <em>min</em> و<em>max</em>
    لدمج درجات الانتماء، وحساب القيمة المخرجة بطريقة <em>centroid</em>
    لفك التعميم (defuzzification).</p>

    {_img_tag(arch_img, 'الشكل 1: المخطط العام لمحرك الاستدلال الضبابي')}

    <h2>1.1 المتغيرات ودوال العضوية</h2>
    <p>كل متغيّر يُمَثَّل بمجموعة من دوال العضوية المثلثية والشبه منحرفية
    التي تربط القيمة الرقمية بدرجة انتمائها إلى الفئات الضبابية.</p>

    <h3>المدخلات</h3>
    {_img_tag(os.path.join(fig_dir, 'mf_01_battery_level.png'),
              f'الشكل 2: دوال عضوية {VAR_AR["battery_level"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_02_temperature.png'),
              f'الشكل 3: دوال عضوية {VAR_AR["temperature"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_03_health.png'),
              f'الشكل 4: دوال عضوية {VAR_AR["health"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_04_load.png'),
              f'الشكل 5: دوال عضوية {VAR_AR["load"]}')}

    <h3>المخرجات</h3>
    {_img_tag(os.path.join(fig_dir, 'mf_05_charging_speed.png'),
              f'الشكل 6: دوال عضوية {VAR_AR["charging_speed"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_06_cooling_level.png'),
              f'الشكل 7: دوال عضوية {VAR_AR["cooling_level"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_07_warning_status.png'),
              f'الشكل 8: دوال عضوية {VAR_AR["warning_status"]}')}
    {_img_tag(os.path.join(fig_dir, 'mf_08_discharge_limit.png'),
              f'الشكل 9: دوال عضوية {VAR_AR["discharge_limit"]}')}
    """

    # Section 2 - rule structure.
    rules_charging = _rule_table_html(system.rule_info, 'charging_speed',
                                      'قواعد سرعة الشحن')
    rules_cooling = _rule_table_html(system.rule_info, 'cooling_level',
                                     'قواعد التبريد')
    rules_warning = _rule_table_html(system.rule_info, 'warning_status',
                                     'قواعد التحذير')
    rules_discharge = _rule_table_html(system.rule_info, 'discharge_limit',
                                       'قواعد حد التفريغ')
    section2 = f"""
    <h1>2. هيكلية القواعد</h1>
    <p>تم تنظيم قواعد الاستدلال البالغ عددها {len(system.rule_info)} قاعدة
    وفقًا للمتغيّر المخرج الذي تؤثّر فيه كل قاعدة. يضم النظام أربع مجموعات
    رئيسية من القواعد، تُغطي على التوالي: سرعة الشحن، مستوى التبريد، حالة
    التحذير، وحد التفريغ. القواعد <strong>R45</strong> و<strong>R46</strong>
    أُضيفتا لاحقًا لضمان عدم الشحن السريع تحت الصفر المئوي حمايةً لخلايا
    الليثيوم-أيون من ظاهرة <em>lithium plating</em>.</p>

    {rules_charging}
    {rules_cooling}
    {rules_warning}
    {rules_discharge}
    """

    # Section 3 - sample test cases.
    section3 = f"""
    <h1>3. عيّنة من حالات الاختبار</h1>
    <p>تعرض الجدول التالي مجموعة من السيناريوهات الممثلة للأداء العملي
    للنظام. كل سيناريو يُمرَّر إلى الدالة
    <code>get_recommendations(battery_level, temperature, health, load)</code>
    وتُقدَّم نتائجها الأربع: سرعة الشحن، مستوى التبريد، حالة التحذير،
    وحد التفريغ، مع القيمة الرقمية (raw) قبل التصنيف.</p>

    {_scenarios_table_html(system)}

    <div class="note">
    <strong>ملاحظة:</strong> القيمة الرقمية raw تمثّل مركز الكتلة (centroid)
    على المحور 0-100 بعد فك التعميم، أما النص المرافق فهو التصنيف الناتج
    عن تطبيق العتبات الموثّقة في <code>API_INTEGRATION_GUIDE.md</code>.
    </div>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="utf-8"><title>التقرير التقني</title></head>
    <body>
    {section1}
    {section2}
    {section3}
    </body></html>
    """


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_pdf(out_pdf: str, fig_dir: str = 'figs') -> None:
    """Generate the supporting images and render the final PDF."""
    os.makedirs(fig_dir, exist_ok=True)

    system = BatteryFuzzySystem()

    # 1) Architecture diagram + 8 membership-function PNGs.
    _draw_architecture_diagram(os.path.join(fig_dir, 'architecture.png'))
    vis2.generate_all(out_dir=fig_dir, system=system)

    # 2) Render HTML -> PDF.
    html_doc = _build_html(system, fig_dir)
    HTML(string=html_doc, base_url=os.getcwd()).write_pdf(
        out_pdf, stylesheets=[CSS(string=_CSS)])
    print(f'wrote {out_pdf}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='report_ar.pdf',
                        help='Output PDF path (default: ./report_ar.pdf)')
    parser.add_argument('--figs', default='figs',
                        help='Directory for the intermediate PNGs '
                             '(default: ./figs)')
    args = parser.parse_args()
    build_pdf(args.out, args.figs)


if __name__ == '__main__':
    main()
