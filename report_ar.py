"""
Generate an Arabic (RTL) technical report for the Battery Fuzzy System.

Document layout:

    Page 1   - Title page (Arabic + English title, teammates names placeholder)
    Page 2   - Introduction
    Page 3+  - Section 1: Knowledge engineering schema + membership functions
    Page N   - Section 2: Rule structure (46 rules grouped by consequent)
    Page N+1 - Section 3: Sample test cases + a per-scenario rule-firing chart
    Page N+2 - Section 4: Frontend + Backend

Page numbering starts at 1 (no offset, default WeasyPrint behaviour).

Usage:
    python3 report_ar.py                  # writes report_ar.pdf in cwd
    python3 report_ar.py --out report.pdf # custom path
"""

from __future__ import annotations

import argparse
import datetime
import html
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from weasyprint import CSS, HTML

import vis2
from battery_fuzzy_system import BatteryFuzzySystem


# ---------------------------------------------------------------------------
# Project metadata (title page)
# ---------------------------------------------------------------------------

PROJECT_TITLE_AR = 'نظام إدارة البطارية الذكي'
PROJECT_SUBTITLE_AR = 'مبني على المنطق الضبابي'
PROJECT_TITLE_EN = 'Smart Battery Management System'
PROJECT_SUBTITLE_EN = 'Built on Fuzzy Logic'

# Number of blank lines reserved on the title page for team-member names.
TEAM_NAME_SLOTS = 5


# ---------------------------------------------------------------------------
# Arabic glossary
# ---------------------------------------------------------------------------

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
    'very_low': 'منخفض جدًا', 'low': 'منخفض', 'medium': 'متوسط',
    'high': 'مرتفع', 'full': 'ممتلئ',
    'cold': 'بارد', 'normal': 'عادي', 'hot': 'حار', 'very_hot': 'حار جدًا',
    'poor': 'سيئة', 'average': 'متوسطة', 'good': 'جيدة',
    'stop': 'إيقاف', 'slow': 'بطيء', 'fast': 'سريع',
    'off': 'إيقاف',
    'safe': 'آمن', 'warning': 'تحذير', 'critical': 'حرج',
    'conservative': 'متحفظ', 'balanced': 'متوازن', 'aggressive': 'مكثف',
}


# ---------------------------------------------------------------------------
# Architecture diagram (RTL: inputs on RIGHT, engine MIDDLE, outputs LEFT;
# arrows point left to match Arabic reading flow)
# ---------------------------------------------------------------------------

def _draw_architecture_diagram(out_path: str) -> None:
    """
    Render a perfectly-symmetric 3-stage block diagram in RTL orientation:
        [inputs RIGHT]  <-  [inference engine MIDDLE]  <-  [outputs LEFT]
    The figure x-range is 12 units; the three column boxes are each 3 units
    wide separated by 1-unit gutters, which keeps the engine column visually
    centered between the two flanking columns.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    inputs = ['battery_level', 'temperature', 'health', 'load']
    outputs = ['charging_speed', 'cooling_level', 'warning_status', 'discharge_limit']

    # x-extents of the three columns -- chosen so the engine column's
    # midpoint equals the figure midpoint (6.0) exactly.
    output_col = (0.5, 3.5)
    engine_col = (4.5, 7.5)
    input_col = (8.5, 11.5)

    box_h = 0.7
    base_y = 4.6
    row_gap = 1.05

    def add_box(xspan, y, h, label, edge, face, text_color):
        box = mpatches.FancyBboxPatch(
            (xspan[0], y), xspan[1] - xspan[0], h,
            boxstyle='round,pad=0.05', linewidth=1.5,
            edgecolor=edge, facecolor=face,
        )
        ax.add_patch(box)
        ax.text((xspan[0] + xspan[1]) / 2, y + h / 2, label,
                ha='center', va='center',
                fontsize=10, fontweight='bold', color=text_color)

    # Outputs on the LEFT.
    for i, name in enumerate(outputs):
        add_box(output_col, base_y - i * row_gap, box_h, name,
                '#2E7D32', '#E8F5E9', '#1B5E20')

    # Inputs on the RIGHT.
    for i, name in enumerate(inputs):
        add_box(input_col, base_y - i * row_gap, box_h, name,
                '#1976D2', '#E3F2FD', '#0D47A1')

    # Engine in the MIDDLE -- spans the full vertical extent of the columns.
    engine_top = base_y + box_h
    engine_bot = base_y - 3 * row_gap
    engine_height = engine_top - engine_bot
    engine = mpatches.FancyBboxPatch(
        (engine_col[0], engine_bot),
        engine_col[1] - engine_col[0], engine_height,
        boxstyle='round,pad=0.1', linewidth=2.0,
        edgecolor='#6A1B9A', facecolor='#F3E5F5',
    )
    ax.add_patch(engine)
    engine_cx = (engine_col[0] + engine_col[1]) / 2
    engine_cy = (engine_top + engine_bot) / 2
    ax.text(engine_cx, engine_cy + 0.55, 'Fuzzy Inference', ha='center',
            va='center', fontsize=13, fontweight='bold', color='#4A148C')
    ax.text(engine_cx, engine_cy - 0.05, 'Engine', ha='center',
            va='center', fontsize=13, fontweight='bold', color='#4A148C')
    ax.text(engine_cx, engine_cy - 0.85, '46 rules', ha='center',
            va='center', fontsize=10, color='#4A148C')

    # Arrows pointing LEFT (RTL flow): input box -> engine -> output box.
    for i in range(4):
        y = base_y - i * row_gap + box_h / 2
        # input.left  -> engine.right  (arrow head sits on engine.right)
        ax.annotate(
            '', xy=(engine_col[1], y), xytext=(input_col[0], y),
            arrowprops=dict(arrowstyle='->', lw=1.6, color='#1976D2'),
        )
        # engine.left -> output.right (arrow head sits on output.right)
        ax.annotate(
            '', xy=(output_col[1], y), xytext=(engine_col[0], y),
            arrowprops=dict(arrowstyle='->', lw=1.6, color='#2E7D32'),
        )

    # Captions above each column.
    caption_y = base_y + box_h + 0.45
    ax.text((input_col[0] + input_col[1]) / 2, caption_y,
            'Inputs (Antecedents)', ha='center', fontsize=11,
            fontweight='bold', color='#0D47A1')
    ax.text(engine_cx, caption_y,
            'Inference Engine', ha='center', fontsize=11,
            fontweight='bold', color='#4A148C')
    ax.text((output_col[0] + output_col[1]) / 2, caption_y,
            'Outputs (Consequents)', ha='center', fontsize=11,
            fontweight='bold', color='#1B5E20')

    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# Rule descriptions in Arabic.
# The implication arrow is written as the Arabic left-pointing arrow so it
# visually flows right-to-left to match the surrounding script.
# ---------------------------------------------------------------------------

RULE_AR = {
    'R1':  'بطارية منخفضة جدًا + درجة حرارة عادية ← شحن سريع',
    'R2':  'بطارية منخفضة جدًا + حرارة مرتفعة ← شحن بطيء',
    'R3':  'بطارية منخفضة + درجة حرارة عادية ← شحن سريع',
    'R4':  'بطارية منخفضة + حرارة مرتفعة ← شحن بطيء',
    'R5':  'بطارية متوسطة + درجة حرارة عادية/حارة ← شحن عادي',
    'R6':  'بطارية متوسطة + حرارة حارة جدًا ← شحن بطيء',
    'R7':  'بطارية مرتفعة/ممتلئة + درجة حرارة عادية ← شحن بطيء',
    'R8':  'بطارية مرتفعة/ممتلئة + حرارة مرتفعة ← إيقاف الشحن',
    'R9':  'صحة سيئة + درجة حرارة عادية ← شحن بطيء',
    'R10': 'صحة سيئة + حرارة مرتفعة ← إيقاف الشحن',
    'R11': 'حرارة عادية + بطارية منخفضة/متوسطة ← تبريد متوقف',
    'R12': 'حرارة عادية + بطارية مرتفعة/ممتلئة ← تبريد متوقف',
    'R13': 'درجة حرارة حارة + بطارية منخفضة ← تبريد عالٍ',
    'R14': 'درجة حرارة حارة + بطارية متوسطة ← تبريد متوسط',
    'R15': 'درجة حرارة حارة + بطارية مرتفعة ← تبريد متوسط',
    'R16': 'حرارة حارة جدًا + بطارية منخفضة ← تبريد عالٍ',
    'R17': 'حرارة حارة جدًا + بطارية متوسطة/مرتفعة ← تبريد عالٍ',
    'R18': 'صحة سيئة + حرارة مرتفعة ← تبريد عالٍ',
    'R19': 'بطارية منخفضة + درجة حرارة عادية ← تحذير',
    'R20': 'بطارية منخفضة + حرارة مرتفعة ← حرج',
    'R21': 'حرارة حارة جدًا أو صحة سيئة ← حرج',
    'R22': 'بطارية متوسطة + حرارة حارة + صحة متوسطة ← تحذير',
    'R23': 'بطارية متوسطة + درجة حرارة عادية + صحة جيدة ← آمن',
    'R24': 'بطارية مرتفعة/ممتلئة + صحة جيدة + درجة حرارة عادية ← آمن',
    'R25': 'بطارية متوسطة + حرارة حارة + صحة جيدة ← تحذير',
    'R26': 'بطارية مرتفعة/ممتلئة + درجة حرارة معتدلة ← آمن',
    'R27': 'بطارية متوسطة + حرارة مرتفعة + صحة سيئة ← تحذير',
    'R28': 'بطارية منخفضة جدًا + صحة سيئة + حمل مرتفع ← حرج',
    'R29': 'بطارية منخفضة جدًا + صحة جيدة ← تفريغ متحفظ',
    'R30': 'بطارية منخفضة + صحة سيئة/متوسطة ← تفريغ متحفظ',
    'R31': 'بطارية متوسطة + حمل منخفض ← تفريغ مكثف',
    'R32': 'بطارية متوسطة + حمل متوسط/مرتفع ← تفريغ متوازن',
    'R33': 'بطارية مرتفعة + حمل منخفض ← تفريغ متوازن',
    'R34': 'بطارية مرتفعة + حمل متوسط/مرتفع ← تفريغ مكثف',
    'R35': 'بطارية ممتلئة + حمل منخفض ← تفريغ مكثف',
    'R36': 'بطارية ممتلئة + حمل متوسط/مرتفع ← تفريغ متوازن',
    'R37': 'صحة سيئة + حمل متوسط/مرتفع ← تفريغ متحفظ',
    'R38': '(صحة سيئة أو حرارة حارة جدًا) + بطارية منخفضة ← تفريغ متحفظ',
    'R39': 'حرارة حارة جدًا + بطارية منخفضة جدًا ← تفريغ متحفظ',
    'R40': 'بطارية متوسطة + صحة سيئة ← شحن بطيء',
    'R41': 'بطارية متوسطة + درجة حرارة عادية + صحة متوسطة ← آمن',
    'R42': 'حرارة حارة جدًا ← إيقاف الشحن',
    'R43': 'بطارية منخفضة جدًا ← تفريغ متحفظ',
    'R44': 'بطارية منخفضة ← تفريغ متحفظ',
    'R45': 'بطارية منخفضة جدًا + درجة حرارة باردة ← شحن بطيء',
    'R46': 'بطارية منخفضة + درجة حرارة باردة ← شحن بطيء',
}

# Test scenarios for Section 3.
SCENARIO_LABELS_AR = [
    ('انخفاض شديد + شحن طبيعي',           (10, 25, 70, 50)),
    ('بطارية منخفضة + جو بارد',           (20, -10, 85, 30)),
    ('وضع طبيعي',                         (50, 25, 80, 50)),
    ('استخدام مكثف في الجو الحار',        (30, 65, 50, 80)),
    ('بطارية ممتلئة + حرارة عالية جدًا',  (95, 78, 80, 20)),
    ('صحة سيئة + شحن منخفض',              (40, 30, 25, 70)),
    ('بطارية مرتفعة + حمل منخفض',         (80, 22, 90, 15)),
]

# Scenario used for the rule-firings figure -- chosen so multiple rules
# across different output variables fire simultaneously.
RULE_FIRING_SCENARIO = (30.0, 65.0, 50.0, 80.0)
RULE_FIRING_LABEL_AR = 'استخدام مكثف في الجو الحار (B=30, T=65 C, H=50, L=80)'


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def _build_css(font_dir: str) -> str:
    """
    Compose the stylesheet, embedding the modern Arabic font (Tajawal) via
    @font-face so the report is reproducible without touching system fonts.
    """
    tajawal_reg = 'file://' + os.path.abspath(
        os.path.join(font_dir, 'Tajawal-Regular.ttf'))
    tajawal_bold = 'file://' + os.path.abspath(
        os.path.join(font_dir, 'Tajawal-Bold.ttf'))

    return f"""
    @font-face {{
        font-family: 'Tajawal';
        src: url('{tajawal_reg}') format('truetype');
        font-weight: normal;
    }}
    @font-face {{
        font-family: 'Tajawal';
        src: url('{tajawal_bold}') format('truetype');
        font-weight: bold;
    }}

    @page {{
        size: A4;
        margin: 22mm 18mm 22mm 18mm;
        @bottom-center {{
            content: "صفحة " counter(page);
            font-family: 'Tajawal', 'Noto Naskh Arabic', sans-serif;
            font-size: 10pt;
            color: #666;
        }}
    }}
    @page :first {{
        /* Title page: drop the page-number footer for visual cleanliness;
           every subsequent page still shows its number. */
        @bottom-center {{ content: ""; }}
    }}

    html, body {{
        font-family: 'Tajawal', 'Noto Naskh Arabic', sans-serif;
    }}
    body {{
        font-size: 11pt;
        line-height: 1.7;
        color: #1A1A1A;
    }}

    /* Title page (block layout to avoid flex+RTL quirks in WeasyPrint) */
    .title-page {{
        width: 100%;
        text-align: center;
        page-break-after: always;
        padding-top: 28mm;
    }}
    .title-page .top-bar {{
        width: 60%;
        height: 4px;
        background: linear-gradient(to left, #0D47A1, #6A1B9A, #2E7D32);
        margin: 0 auto 22mm auto;
        border-radius: 2px;
    }}
    .title-page .title-ar {{
        font-size: 30pt;
        font-weight: bold;
        color: #0D47A1;
        margin-top: 4mm;
        letter-spacing: 0.5pt;
    }}
    .title-page .subtitle-ar {{
        font-size: 17pt;
        color: #4A148C;
        margin-top: 4mm;
        font-weight: bold;
    }}
    .title-page .title-en {{
        font-size: 16pt;
        color: #444;
        margin-top: 14mm;
        direction: ltr;
        font-family: 'Tajawal', 'DejaVu Sans', sans-serif;
        letter-spacing: 0.5pt;
    }}
    .title-page .subtitle-en {{
        font-size: 12pt;
        color: #777;
        margin-top: 1mm;
        direction: ltr;
        font-style: italic;
    }}
    .title-page .team-label {{
        font-size: 13pt;
        font-weight: bold;
        color: #0D47A1;
        margin-top: 30mm;
        margin-bottom: 4mm;
    }}
    .title-page .team-slot {{
        width: 65%;
        height: 0;
        border-bottom: 1px solid #888;
        margin: 9mm auto 0 auto;
    }}
    .title-page .date-line {{
        font-size: 11pt;
        color: #555;
        margin-top: 26mm;
    }}

    /* Intro & sections */
    h1.section {{
        font-size: 20pt;
        color: #0D47A1;
        border-bottom: 2px solid #0D47A1;
        padding-bottom: 4mm;
        margin-top: 0;
        page-break-before: always;
    }}
    h1.intro {{
        font-size: 24pt;
        color: #0D47A1;
        border-bottom: 2px solid #0D47A1;
        padding-bottom: 4mm;
        margin-top: 0;
    }}
    h2 {{
        font-size: 14pt;
        color: #1B5E20;
        margin-top: 6mm;
        margin-bottom: 2mm;
    }}
    h3 {{
        font-size: 12pt;
        color: #4A148C;
        margin-top: 4mm;
        margin-bottom: 1mm;
    }}
    p {{ margin: 2mm 0; text-align: justify; }}

    figure {{
        text-align: center;
        margin: 4mm 0;
        page-break-inside: avoid;
    }}
    figure img {{ max-width: 100%; height: auto; }}
    figcaption {{
        font-size: 9.5pt;
        color: #555;
        margin-top: 1mm;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 2mm 0 4mm 0;
        font-size: 9.5pt;
        page-break-inside: auto;
    }}
    th, td {{
        border: 1px solid #BBB;
        padding: 1.5mm 2mm;
        text-align: right;
        vertical-align: top;
    }}
    th {{
        background-color: #E3F2FD;
        color: #0D47A1;
        font-weight: bold;
    }}
    tr:nth-child(even) td {{ background-color: #FAFAFA; }}

    .scenario-out {{
        font-family: 'DejaVu Sans Mono', monospace;
        direction: ltr;
        text-align: left;
        font-size: 9pt;
    }}
    .note {{
        background: #FFF8E1;
        border-right: 4px solid #F9A825;
        padding: 2mm 3mm;
        margin: 3mm 0;
        font-size: 10pt;
    }}
    """


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _img_tag(path: str, caption_ar: str) -> str:
    abs_path = os.path.abspath(path)
    return (
        '<figure>'
        f'<img src="file://{abs_path}" alt="{html.escape(caption_ar)}" />'
        f'<figcaption>{html.escape(caption_ar)}</figcaption>'
        '</figure>'
    )


def _rule_table_html(rule_info: list, output_var: str, header_ar: str) -> str:
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
    rows = []
    for label, (b, t, h, l) in SCENARIO_LABELS_AR:
        r = system.get_recommendations(b, t, h, l)
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


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def _title_page_html() -> str:
    slots = '\n'.join('<div class="team-slot"></div>'
                      for _ in range(TEAM_NAME_SLOTS))
    today = datetime.date.today().strftime('%Y / %m / %d')
    return f"""
    <section class="title-page">
        <div class="top-bar"></div>

        <div class="title-ar">{html.escape(PROJECT_TITLE_AR)}</div>
        <div class="subtitle-ar">{html.escape(PROJECT_SUBTITLE_AR)}</div>

        <div class="title-en">{html.escape(PROJECT_TITLE_EN)}</div>
        <div class="subtitle-en">{html.escape(PROJECT_SUBTITLE_EN)}</div>

        <div class="team-label">إعداد فريق العمل</div>
        {slots}

        <div class="date-line">{html.escape(today)}</div>
    </section>
    """


def _intro_page_html(system: BatteryFuzzySystem) -> str:
    n_rules = len(system.rule_info)
    return f"""
    <h1 class="intro">مقدمة</h1>

    <p>يستعرض هذا التقرير نظام إدارة بطارية يعتمد على المنطق الضبابي
    (Fuzzy Logic) لاتخاذ قرارات تشغيلية محسوبة بشأن سرعة الشحن، مستوى
    التبريد، حالة التحذير، وحد التفريغ، انطلاقًا من أربعة قياسات مدخلة
    تمثّل حالة البطارية لحظيًا: <strong>مستوى البطارية</strong>،
    <strong>درجة الحرارة</strong>، <strong>صحة البطارية</strong>،
    و<strong>الحمل</strong>.</p>

    <p>يقوم النظام بترجمة كل مدخل عددي إلى درجات انتماء لفئات لغوية واضحة
    (مثل: منخفض، عادي، مرتفع)، ثم يطبّق قاعدة معرفة مكوّنة من
    <strong>{n_rules}</strong> قاعدة استنتاجية لاستخلاص قيم المخرجات
    الأربع. تُحوَّل القيم الضبابية في النهاية إلى أرقام عملية باستخدام
    أسلوب <em>Area of Center</em> لفك التعميم (defuzzification)،
    لتُسلَّم إلى وحدة التحكم كنصائح قابلة للتنفيذ.</p>

    <p>يتناول التقرير ثلاثة محاور رئيسية: المخطط العام لهندسة المعرفة
    في النظام (المدخلات والمخرجات ودوال العضوية)، الهيكل الكامل لقاعدة
    القواعد مُصنَّفًا حسب المتغير المخرج، ثم عيّنة من حالات الاختبار
    العملية تُظهر استجابة النظام، يصاحبها رسم تفصيلي يوضّح أيّ القواعد
    اشتعلت ومدى مساهمتها في القرار النهائي. وفي الختام، نستعرض الواجهة
    الأمامية والخدمة الخلفية اللتين تتيحان تجربة النظام بشكل تفاعلي.</p>
    """


def _section1_html(system: BatteryFuzzySystem, fig_dir: str) -> str:
    n_rules = len(system.rule_info)
    arch_img = os.path.join(fig_dir, 'architecture.png')
    return f"""
    <h1 class="section">1. مخطط هندسة المعرفة</h1>

    <p>يستند النظام إلى محرّك استدلال ضبابي يضمّ أربعة مدخلات (قدمات /
    Antecedents) وأربعة مخرجات (نتائج / Consequents)، تتصل ببعضها عبر
    قاعدة مكوّنة من <strong>{n_rules}</strong> قاعدة استدلالية. تتم
    عملية الاستدلال باستخدام عمليّتَي <em>min</em> و<em>max</em> لدمج
    درجات الانتماء، ثم يُحسب الناتج بأسلوب <em>Area of Center</em>
    لفك التعميم (defuzzification).</p>

    {_img_tag(arch_img, 'الشكل 1: المخطط العام لمحرّك الاستدلال الضبابي')}

    <h2>1.1 المتغيرات ودوال العضوية</h2>
    <p>كل متغيّر يُمَثَّل بمجموعة من دوال العضوية المثلثية والشبه
    منحرفية التي تربط القيمة الرقمية بدرجة انتمائها إلى الفئات
    الضبابية.</p>

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


def _section2_html(system: BatteryFuzzySystem) -> str:
    rules_charging = _rule_table_html(system.rule_info, 'charging_speed',
                                      'قواعد سرعة الشحن')
    rules_cooling = _rule_table_html(system.rule_info, 'cooling_level',
                                     'قواعد التبريد')
    rules_warning = _rule_table_html(system.rule_info, 'warning_status',
                                     'قواعد التحذير')
    rules_discharge = _rule_table_html(system.rule_info, 'discharge_limit',
                                       'قواعد حد التفريغ')
    return f"""
    <h1 class="section">2. هيكلية القواعد</h1>
    <p>تم تنظيم قواعد الاستدلال البالغ عددها {len(system.rule_info)}
    قاعدة وفقًا للمتغيّر المخرج الذي تؤثّر فيه كل قاعدة. يضم النظام
    أربع مجموعات رئيسية من القواعد، تُغطي على التوالي: سرعة الشحن،
    مستوى التبريد، حالة التحذير، وحد التفريغ.</p>

    {rules_charging}
    {rules_cooling}
    {rules_warning}
    {rules_discharge}
    """


def _section3_html(system: BatteryFuzzySystem, fig_dir: str,
                   firing_info: dict) -> str:
    firings_img = os.path.join(fig_dir, 'rule_firings.png')
    outputs = firing_info['outputs']
    active = firing_info['active_rule_count']
    total = firing_info['total_rule_count']
    return f"""
    <h1 class="section">3. عيّنة من حالات الاختبار</h1>
    <p>يعرض الجدول التالي مجموعة من السيناريوهات الممثّلة للأداء العملي
    للنظام. كل سيناريو يُمرَّر إلى محرّك الاستدلال وتُقدَّم نتائجه الأربع:
    سرعة الشحن، مستوى التبريد، حالة التحذير، وحد التفريغ، مع القيمة
    الرقمية (raw) قبل التصنيف.</p>

    {_scenarios_table_html(system)}

    <div class="note">
    <strong>ملاحظة:</strong> القيمة الرقمية raw تمثّل المركز
    (Area of Center) على المحور 0-100 بعد فك التعميم، أما النص المرافق
    فهو التصنيف اللغوي الناتج عن تطبيق العتبات المعرّفة لكل متغيّر مخرج.
    </div>

    <h2>3.1 القواعد التي اشتعلت لسيناريو نموذجي</h2>
    <p>للسيناريو: <strong>{html.escape(RULE_FIRING_LABEL_AR)}</strong>،
    قام النظام بحساب درجة اشتعال (μ) لكل قاعدة من أصل
    <strong>{total}</strong> قاعدة، فاشتعلت منها
    <strong>{active}</strong> قاعدة (μ &gt; 0.01). الرسم البياني التالي
    يعرض هذه الدرجات مرتّبة حسب رقم القاعدة، مع تلوين كل عمود وفقًا
    لمتغيّر المخرج الذي تؤثر فيه القاعدة.</p>

    {_img_tag(firings_img, 'الشكل 10: درجات اشتعال القواعد للسيناريو')}

    <p>المخرجات المنبثقة عن هذا السيناريو:</p>
    <ul>
      <li>سرعة الشحن: <strong>{outputs['charging_speed']}</strong>
          ({outputs['charging_speed_raw']})</li>
      <li>مستوى التبريد: <strong>{outputs['cooling_level']}</strong>
          ({outputs['cooling_level_raw']})</li>
      <li>حالة التحذير: <strong>{outputs['warning_status']}</strong>
          ({outputs['warning_status_raw']})</li>
      <li>حد التفريغ: <strong>{outputs['discharge_limit']}</strong>
          ({outputs['discharge_limit_raw']})</li>
    </ul>
    """


def _section4_html() -> str:
    """
    Frontend / Backend section.

    Describes the runtime architecture exposed by the project's HTTP service
    and the HTML page that consumes it. Endpoint/route names are kept generic
    so the section remains accurate as the front/back code evolves.
    """
    return """
    <h1 class="section">4. الواجهة الأمامية والخدمة الخلفية</h1>

    <p>لتسهيل التفاعل مع النظام، تم تغليف محرّك الاستدلال الضبابي خلف
    خدمة ويب صغيرة مرفقة بصفحة HTML بسيطة. تتبع البنية نمط
    <em>client/server</em> الكلاسيكي: تقوم الصفحة الأمامية بجمع
    المدخلات الأربعة من المستخدم وإرسالها إلى نقطة وصول HTTP، ثم تستقبل
    استجابة JSON تحتوي على المخرجات الأربع وتعرضها بصورة قابلة للقراءة.</p>

    <h2>4.1 الخدمة الخلفية (Backend)</h2>
    <p>الخدمة الخلفية مكتوبة بلغة Python وتُحمِّل وحدة الاستدلال الضبابي
    عند الإقلاع، فتُعيد استخدام الكائن نفسه لكل طلب وتتجنّب تكلفة إعادة
    بناء النظام في كل مرة. تستقبل الخدمة طلب POST يحمل المدخلات الأربعة
    بصيغة JSON، ثم تستدعي محرّك الاستدلال وتُرجع قاموسًا يحوي:</p>

    <ul>
      <li>القيمة الرقمية الخام (raw) لكل مخرج من المخرجات الأربعة.</li>
      <li>التصنيف النصي المقابل (مثلًا: Slow, Normal, Fast لسرعة الشحن).</li>
      <li>صدى المدخلات للتحقق من صحتها على جانب المستخدم.</li>
    </ul>

    <p>كما تُغطّى الأخطاء الشائعة: <code>TypeError</code> عند إرسال قيمة
    غير رقمية، و<code>ValueError</code> عند خروج أي مُدخَل عن نطاقه
    المسموح به.</p>

    <h2>4.2 الواجهة الأمامية (Frontend)</h2>
    <p>صفحة HTML خفيفة تعرض أربعة حقول إدخال (مع تحقق رقمي على جانب
    المتصفّح)، وزرّ لإرسال البيانات إلى الخدمة الخلفية، ولوحة عرض النتائج.
    حالما تصل الاستجابة، تظهر القيم الرقمية الخام إلى جانب التصنيفات
    اللغوية، ممّا يتيح للمختبِر قياس استجابة النظام بصريًا لمختلف
    السيناريوهات قبل دمجه في أيّ منظومة تحكم أكبر.</p>

    <p>هذا الفصل بين الواجهة والمحرّك يضمن استقلال الجزأين: يمكن تطوير
    الواجهة (مكتبات الرسم البياني، التصميم المتجاوب) دون لمس قاعدة
    المعرفة، كما يمكن استبدال الواجهة بأخرى (مثلًا تطبيق جوّال) باستهلاك
    الخدمة الخلفية نفسها.</p>
    """


def _build_html(system: BatteryFuzzySystem, fig_dir: str,
                firing_info: dict) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="utf-8"><title>التقرير التقني</title></head>
    <body>
    {_title_page_html()}
    {_intro_page_html(system)}
    {_section1_html(system, fig_dir)}
    {_section2_html(system)}
    {_section3_html(system, fig_dir, firing_info)}
    {_section4_html()}
    </body></html>
    """


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_pdf(out_pdf: str, fig_dir: str = 'figs',
              font_dir: str = 'fonts') -> None:
    os.makedirs(fig_dir, exist_ok=True)

    system = BatteryFuzzySystem()

    # Architecture diagram + 8 MF PNGs + scenario rule-firings PNG.
    _draw_architecture_diagram(os.path.join(fig_dir, 'architecture.png'))
    vis2.generate_all(out_dir=fig_dir, system=system,
                      firing_scenario=RULE_FIRING_SCENARIO)

    # Re-run the firing scenario through the system so Section 3.1 can name
    # the active-rule count and exact outputs alongside the figure.
    firing_info = vis2.visualize_rule_firings(
        system, RULE_FIRING_SCENARIO,
        os.path.join(fig_dir, 'rule_firings.png'))

    html_doc = _build_html(system, fig_dir, firing_info)
    HTML(string=html_doc, base_url=os.getcwd()).write_pdf(
        out_pdf, stylesheets=[CSS(string=_build_css(font_dir))])
    print(f'wrote {out_pdf}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='report_ar.pdf',
                        help='Output PDF path (default: ./report_ar.pdf)')
    parser.add_argument('--figs', default='figs',
                        help='Directory for the intermediate PNGs '
                             '(default: ./figs)')
    parser.add_argument('--fonts', default='fonts',
                        help='Directory containing Tajawal-*.ttf font files '
                             '(default: ./fonts)')
    args = parser.parse_args()
    build_pdf(args.out, args.figs, args.fonts)


if __name__ == '__main__':
    main()
