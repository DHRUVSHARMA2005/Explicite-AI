"""
Explicite AI — Group 6 Presentation Generator
Generates an 18-slide PowerPoint using python-pptx.
Run from any directory: python presentation/build_presentation.py
"""
import math
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn
from lxml import etree
import copy

# ── Output paths ──────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent
PPTX_PATH = OUT_DIR / "Explicite_AI_Group_6_Presentation.pptx"

# ── Design tokens — Explicite Midnight ───────────────────────────────────────
BG        = RGBColor(0x09, 0x0B, 0x10)   # #090B10 app background
SURFACE   = RGBColor(0x11, 0x15, 0x1D)   # #11151D card surface
ELEVATED  = RGBColor(0x1B, 0x23, 0x30)   # #1B2330 elevated surface
ACCENT    = RGBColor(0x4F, 0x8E, 0xF7)   # #4F8EF7 indigo accent
CYAN      = RGBColor(0x56, 0xD3, 0xF7)   # #56D3F7 cyan
GREEN     = RGBColor(0x3F, 0xB9, 0x50)   # #3FB950 success
AMBER     = RGBColor(0xE3, 0xB3, 0x41)   # #E3B341 warning
RED       = RGBColor(0xE5, 0x53, 0x4B)   # #E5534B critical
TEXT      = RGBColor(0xE6, 0xED, 0xF3)   # #E6EDF3 primary text
TEXT2     = RGBColor(0x7D, 0x8B, 0x9A)   # muted secondary
BORDER    = RGBColor(0x30, 0x3D, 0x4F)   # subtle border

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

# ── python-pptx helpers ───────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs

def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)

def bg(slide, color=BG):
    """Fill slide background."""
    bg_ = slide.background
    fill = bg_.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, fill=SURFACE, border=BORDER, border_pt=0.75, radius=None):
    """Add a filled rectangle (optionally with rounded corners)."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if border_pt:
        shape.line.color.rgb = border
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    if radius:
        # pptx rounded rect
        sp = shape.element
        spPr = sp.find(qn('p:spPr'))
        if spPr is not None:
            prstGeom = spPr.find(qn('a:prstGeom'))
            if prstGeom is not None:
                prstGeom.set('prst', 'roundRect')
                avLst = prstGeom.find(qn('a:avLst'))
                if avLst is None:
                    avLst = etree.SubElement(prstGeom, qn('a:avLst'))
                gd = etree.SubElement(avLst, qn('a:gd'))
                gd.set('name', 'adj')
                gd.set('fmla', f'val {radius}')
    return shape

def txt(slide, text, x, y, w, h, size=18, bold=False, color=TEXT,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    """Add a text box."""
    tf_box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tf_box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return tf_box

def txt_multi(slide, lines, x, y, w, h, size=16, bold=False, color=TEXT,
              align=PP_ALIGN.LEFT, line_spacing=1.2):
    """Add multi-line text box with multiple paragraphs."""
    from pptx.util import Pt as _Pt
    from pptx.oxml.ns import qn as _qn
    from lxml import etree as _et
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (line_text, line_size, line_bold, line_color) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line_text
        run.font.size = _Pt(line_size)
        run.font.bold = line_bold
        run.font.color.rgb = line_color
    return tb

def hline(slide, x, y, w, color=BORDER, pt=0.75):
    """Horizontal rule."""
    line = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Pt(pt))
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()
    return line

def accent_bar(slide, x, y, h=0.05, color=ACCENT):
    """Thin vertical accent bar."""
    bar = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(0.05), Inches(h))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

def dot(slide, x, y, r=0.08, color=ACCENT):
    """Small circle bullet."""
    shape = slide.shapes.add_shape(9, Inches(x-r/2), Inches(y-r/2), Inches(r), Inches(r))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()

def slide_num(slide, n, total=18):
    txt(slide, f"{n} / {total}", 12.3, 7.1, 0.8, 0.25, size=9, color=TEXT2, align=PP_ALIGN.RIGHT)

def section_tag(slide, label, x=0.35, y=0.22):
    """Small section label above the slide title."""
    txt(slide, label.upper(), x, y, 4, 0.22, size=8, color=ACCENT, bold=True)

def slide_title(slide, title, x=0.35, y=0.48, w=12.6, size=32, color=TEXT):
    txt(slide, title, x, y, w, 0.55, size=size, bold=True, color=color)

def subtitle_line(slide, sub, x=0.35, y=1.1, w=12.0, size=15):
    txt(slide, sub, x, y, w, 0.3, size=size, color=TEXT2)

def content_header(prs, slide, section_lbl, title, subtitle=None, slide_n=None):
    """Standard content slide header with section tag, title, divider."""
    bg(slide)
    if section_lbl:
        section_tag(slide, section_lbl)
    slide_title(slide, title)
    hline(slide, 0.35, 1.08, 12.6, color=BORDER)
    if subtitle:
        subtitle_line(slide, subtitle)
    if slide_n:
        slide_num(slide, slide_n)

def bullet_card(slide, title, bullets, x, y, w, h, title_color=ACCENT, bullet_size=13):
    """A card with title and bullet list."""
    box(slide, x, y, w, h, fill=SURFACE, border=BORDER, border_pt=0.5, radius=20000)
    ty = y + 0.12
    txt(slide, title, x+0.2, ty, w-0.4, 0.3, size=13, bold=True, color=title_color)
    by = ty + 0.35
    for b in bullets:
        dot(slide, x+0.32, by+0.06, r=0.06, color=ACCENT)
        txt(slide, b, x+0.48, by, w-0.65, 0.28, size=bullet_size, color=TEXT)
        by += 0.28

def flow_arrow(slide, x1, y, x2, color=TEXT2):
    """Simple horizontal arrow between two x positions at height y."""
    from pptx.util import Emu as _Emu
    connector = slide.shapes.add_connector(
        1,  # MSO_CONNECTOR_TYPE.STRAIGHT
        Inches(x1), Inches(y), Inches(x2), Inches(y)
    )
    connector.line.color.rgb = color
    connector.line.width = Pt(1.5)

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def slide_01_cover(prs):
    slide = blank_slide(prs)
    bg(slide)

    # Deep background gradient-like overlay panel
    box(slide, 0, 0, 13.33, 7.5, fill=RGBColor(0x06, 0x08, 0x0D), border_pt=0)

    # Decorative side accent strip
    strip = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.18), Inches(7.5))
    strip.fill.solid(); strip.fill.fore_color.rgb = ACCENT
    strip.line.fill.background()

    # Decorative code-line motif (subtle text)
    for i, snippet in enumerate([
        "analysing src/auth.py ... 3 findings",
        "severity: HIGH  CWE-89: SQL Injection",
        "AI explanation generated  ✓",
        "suggested fix proposed  ✓",
    ]):
        txt(slide, snippet, 0.5, 5.8 + i*0.22, 9, 0.22,
            size=8, color=RGBColor(0x22, 0x2D, 0x40), italic=True)

    # Project badge
    box(slide, 0.5, 0.55, 2.8, 0.42, fill=ELEVATED, border=ACCENT, border_pt=0.75, radius=20000)
    txt(slide, "USABILITY DESIGN & SOFTWARE APPLICATIONS", 0.65, 0.62, 2.5, 0.3,
        size=7.5, bold=True, color=ACCENT)

    # Main title
    txt(slide, "Explicite AI", 0.5, 1.35, 10, 1.1,
        size=68, bold=True, color=TEXT)

    # Accent underline
    bar = slide.shapes.add_shape(1, Inches(0.5), Inches(2.52), Inches(4.2), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

    # Subtitle
    txt(slide, "AI-Powered Code Analysis, Explainable Findings & Developer Assistance",
        0.5, 2.72, 10, 0.55, size=18, color=TEXT2)

    # Divider
    hline(slide, 0.5, 3.52, 9, color=BORDER)

    # Team info
    txt(slide, "Group 6", 0.5, 3.72, 3, 0.3, size=14, bold=True, color=TEXT)
    txt(slide, "Dhruv Sharma   —   24BBS0063", 0.5, 4.1, 6, 0.28, size=13, color=TEXT2)
    txt(slide, "Rijul Kothawade   —   24BBS0230", 0.5, 4.42, 6, 0.28, size=13, color=TEXT2)

    # GitHub badge
    box(slide, 0.5, 5.0, 6.5, 0.38, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "⬡  github.com/DHRUVSHARMA2005/Explicite-AI",
        0.72, 5.07, 6.0, 0.26, size=10, color=TEXT2)

    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Opening talking points:\n"
        "1. Introduce the project: Explicite AI is a full-stack web application for AI-assisted code analysis.\n"
        "2. Developed for the Usability Design and Software Applications subject — Group 6.\n"
        "3. Team: Dhruv Sharma (24BBS0063) and Rijul Kothawade (24BBS0230).\n"
        "4. The codebase is live at the GitHub repository shown — fully implemented and tested.\n"
        "5. This presentation walks through the problem, solution, architecture, features, design decisions, "
        "testing, and limitations in 18 slides.\n"
        "Transition: Let's start with the problem we set out to solve.")
    return slide


def slide_02_problem(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Context", "The Developer Challenge", slide_n=2)

    intro = ("Modern software development generates a large volume of static-analysis findings. "
             "Without context, developers struggle to understand, prioritise, and resolve them effectively.")
    txt(slide, intro, 0.35, 1.22, 12.6, 0.5, size=13, color=TEXT2)

    problems = [
        ("🔍  Opaque findings",       "Static-analysis output is technical and often lacks explanation of risk or impact."),
        ("📚  Scattered remediation",  "Developers must switch between tools, docs, and issue trackers to understand and fix issues."),
        ("🔒  Security blind spots",   "Code-quality and security findings look similar; severity and exploitability are rarely explained."),
        ("🎓  Learning gap",           "Junior developers lack contextual guidance to understand why a finding matters."),
        ("⚙️   Workflow friction",      "Moving from 'finding' to 'fix' requires multiple disconnected manual steps."),
    ]

    col_w = 5.8
    row_h = 0.88
    for i, (title, desc) in enumerate(problems):
        row = i // 2
        col = i % 2
        px = 0.35 + col * 6.3
        py = 1.85 + row * row_h
        if i == 4:   # centre last card
            px = 3.45
        box(slide, px, py, col_w, row_h - 0.06, fill=SURFACE, border=BORDER, border_pt=0.5, radius=18000)
        txt(slide, title, px+0.2, py+0.1, col_w-0.3, 0.28, size=12, bold=True, color=ACCENT)
        txt(slide, desc,  px+0.2, py+0.42, col_w-0.3, 0.4, size=11, color=TEXT)

    slide_num(slide, 2)

    # Notes embedded as a comment in the XML (pptx notes)
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = ("Talking points:\n"
               "1. Analysts flag hundreds of issues per codebase — most get ignored because context is missing.\n"
               "2. Teams waste time tool-switching: scanner → StackOverflow → OWASP docs → PR comment.\n"
               "3. Severity labels like 'HIGH' don't explain what an attacker can actually do.\n"
               "4. Students and junior devs need guided explanation, not just a rule ID.\n"
               "Transition: Explicite AI was built to address each of these gaps in a single integrated tool.")
    return slide


def slide_03_objectives(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Problem", "Problem Statement & Objectives", slide_n=3)

    # Problem statement box
    box(slide, 0.35, 1.22, 12.6, 0.88, fill=ELEVATED, border=ACCENT, border_pt=0.75, radius=15000)
    txt(slide, "Problem Statement", 0.65, 1.28, 5, 0.28, size=10, bold=True, color=ACCENT)
    stmt = ("Developers lack an integrated tool that combines static-analysis reporting with "
            "contextual AI-generated explanations, suggested remediations, and adaptive learning "
            "support — creating friction between discovering a code issue and resolving it effectively.")
    txt(slide, stmt, 0.65, 1.56, 12.1, 0.5, size=12, color=TEXT)

    txt(slide, "Project Objectives", 0.35, 2.25, 8, 0.28, size=13, bold=True, color=TEXT)

    objectives = [
        ("O1", "Source analysis",   "Enable ZIP upload and Git repository analysis through a consistent pipeline."),
        ("O2", "Findings interface","Present categorised security and quality findings with severity and file context."),
        ("O3", "AI explanations",   "Provide AI-generated, level-adjusted explanations of each finding."),
        ("O4", "Suggested fixes",   "Generate and present proposed code fixes with explicit developer approval required."),
        ("O5", "Developer learning","Offer a tutor chat and learning-resource pathway for findings."),
        ("O6", "Usability design",  "Apply a consistent dark-first design system prioritising clarity and discoverability."),
    ]

    col_w = 4.0
    row_h = 0.72
    for i, (code, label, desc) in enumerate(objectives):
        row = i // 3
        col = i % 3
        px = 0.35 + col * 4.28
        py = 2.6 + row * row_h
        box(slide, px, py, col_w, row_h - 0.05, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
        # Badge
        badge = slide.shapes.add_shape(1, Inches(px+0.18), Inches(py+0.17), Inches(0.38), Inches(0.28))
        badge.fill.solid(); badge.fill.fore_color.rgb = ACCENT
        badge.line.fill.background()
        txt(slide, code, px+0.18, py+0.17, 0.38, 0.28, size=8, bold=True,
            color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        txt(slide, label, px+0.65, py+0.13, col_w-0.8, 0.22, size=11, bold=True, color=TEXT)
        txt(slide, desc,  px+0.20, py+0.4,  col_w-0.35, 0.28, size=10, color=TEXT2)

    slide_num(slide, 3)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. This problem statement is grounded in the actual product — no user study data was fabricated.\n"
        "2. Each objective maps directly to an implemented feature verified in the codebase.\n"
        "3. O6 ties the project to the Usability Design subject — discuss the design system choices.\n"
        "Transition: Let's see how the solution addresses each objective.")
    return slide


def slide_04_solution(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Solution", "Our Proposed Solution", slide_n=4)

    subtitle_line(slide, "An integrated platform connecting code analysis → AI understanding → guided remediation")

    steps = [
        ("📁 Upload",       "ZIP or\nGit URL",      ACCENT),
        ("⚙️  Analyse",      "Semgrep\nstatic scan",  ACCENT),
        ("📋 Findings",     "Severity,\nCVSS, debt",  CYAN),
        ("🤖 Explain",      "AI-generated\nexplanation", CYAN),
        ("🔧 Fix",          "Proposed fix\n+ approval",  GREEN),
        ("🎓 Learn",        "Tutor &\nresources",    AMBER),
    ]

    step_w = 1.68
    step_h = 1.38
    gap = 0.38
    start_x = 0.35
    y = 1.85

    for i, (icon, label, color) in enumerate(steps):
        sx = start_x + i * (step_w + gap)

        # Arrow before step (except first)
        if i > 0:
            ax = sx - gap + 0.05
            arr = slide.shapes.add_connector(1, Inches(ax), Inches(y + step_h/2),
                                              Inches(sx - 0.05), Inches(y + step_h/2))
            arr.line.color.rgb = TEXT2
            arr.line.width = Pt(1.5)

        # Box
        box(slide, sx, y, step_w, step_h, fill=SURFACE, border=color, border_pt=1.0, radius=20000)
        txt(slide, icon, sx, y+0.15, step_w, 0.4, size=22, align=PP_ALIGN.CENTER)
        txt(slide, label, sx, y+0.6, step_w, 0.65, size=11, color=TEXT,
            align=PP_ALIGN.CENTER)

    # Key principle note
    box(slide, 0.35, 3.52, 12.6, 0.72, fill=ELEVATED, border=BORDER, border_pt=0.5, radius=12000)
    txt(slide, "⚠  Design Principle: AI assistance is advisory, not automatic. "
               "Every suggested fix requires explicit developer approval before it can be applied. "
               "AI explanations may be incorrect; developer judgment is always required.",
        0.6, 3.62, 12.1, 0.52, size=11, color=AMBER)

    # User benefit bar
    benefits = ["Single integrated workflow", "No tool-switching", "Contextual learning", "Human oversight preserved"]
    bx = 0.35
    for b in benefits:
        box(slide, bx, 4.42, 3.0, 0.38, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
        txt(slide, "✓  " + b, bx+0.15, 4.5, 2.7, 0.25, size=11, color=GREEN)
        bx += 3.25

    slide_num(slide, 4)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The workflow is end-to-end in one application — login → submit → findings → explain → fix → learn.\n"
        "2. Both ZIP upload and Git repository clone are supported analysis paths.\n"
        "3. Emphasise the advisory principle: AI fix proposals require the developer to explicitly click Approve.\n"
        "4. The learning path connects findings to educational content and a tutor chat.\n"
        "Transition: Who are the users, and what usability goals guided the design?")
    return slide


def slide_05_users(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Design", "Target Users, Use Cases & Usability Goals", slide_n=5)

    # Users
    txt(slide, "Target Users", 0.35, 1.22, 5, 0.28, size=13, bold=True, color=TEXT)
    users = [
        ("👨‍💻  Developer", "Analyses their own code and inspects security and quality findings."),
        ("🎓  CS Student", "Learns about finding types, severity, and remediation through AI guidance."),
        ("👥  Project Member", "Reviews analysis results and tracks issue status across a shared project."),
    ]
    for i, (u, d) in enumerate(users):
        ux = 0.35 + i * 4.28
        box(slide, ux, 1.55, 3.9, 0.82, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
        txt(slide, u, ux+0.18, 1.62, 3.55, 0.28, size=12, bold=True, color=ACCENT)
        txt(slide, d, ux+0.18, 1.92, 3.55, 0.4, size=11, color=TEXT)

    hline(slide, 0.35, 2.58, 12.6, color=BORDER)

    # Use cases
    txt(slide, "Core Use Cases", 0.35, 2.68, 5, 0.28, size=13, bold=True, color=TEXT)
    cases = ["Upload ZIP source code", "Analyse a Git repository", "Review findings list",
             "Read issue detail & CVSS", "Request AI explanation", "Generate & review proposed fix",
             "Use tutor / learning path"]
    cx = 0.35
    for i, c in enumerate(cases):
        if i == 4: cx = 0.35
        dot(slide, cx+0.12, 3.08 + (i % 4) * 0.3 + 0.06, r=0.07, color=CYAN)
        txt(slide, c, cx+0.28, 3.08 + (i % 4) * 0.3, 2.8, 0.28, size=11, color=TEXT)
        if i == 3: cx = 6.75

    hline(slide, 0.35, 4.32, 12.6, color=BORDER)

    # Usability goals
    txt(slide, "Usability Goals  (ISO 9241 / Nielsen Heuristics)", 0.35, 4.42, 8, 0.28,
        size=13, bold=True, color=TEXT)
    goals = [
        ("Clarity",        "Clear visual hierarchy: severity → finding → action"),
        ("Discoverability","Sidebar navigation with labelled screens"),
        ("Consistency",    "Unified design tokens (--xm-*) across all 11 screens"),
        ("Feedback",       "Real-time job status polling; loading & error states"),
        ("User Control",   "Explicit approve/reject for AI-generated fixes"),
        ("Readability",    "Inter + JetBrains Mono; dark-first for extended use"),
    ]
    gx = 0.35
    for i, (g, d) in enumerate(goals):
        col = i % 2
        row = i // 2
        gx = 0.35 + col * 6.5
        gy = 4.82 + row * 0.58
        box(slide, gx, gy, 6.2, 0.52, fill=SURFACE, border=BORDER, border_pt=0.5, radius=12000)
        txt(slide, g + ": ", gx+0.18, gy+0.12, 1.8, 0.3, size=11, bold=True, color=ACCENT)
        txt(slide, d,        gx+1.95, gy+0.12, 4.1, 0.3, size=11, color=TEXT)

    slide_num(slide, 5)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. Users were identified from the product's implemented functionality — no formal user study was conducted.\n"
        "2. Use cases correspond directly to implemented and tested API endpoints.\n"
        "3. The usability goals informed the Explicite Midnight design system — discuss specific design decisions.\n"
        "Transition: Now the technical architecture that implements all this.")
    return slide


def slide_06_architecture(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Architecture", "System Architecture", slide_n=6)

    subtitle_line(slide, "Three-tier web application — React frontend · FastAPI backend · PostgreSQL database")

    # LAYER BOXES
    # Browser / Frontend
    box(slide, 0.2, 1.38, 3.85, 5.78, fill=RGBColor(0x0D, 0x14, 0x22), border=ACCENT, border_pt=0.75, radius=15000)
    txt(slide, "BROWSER / FRONTEND", 0.35, 1.48, 3.5, 0.28, size=9, bold=True, color=ACCENT)
    fe_items = ["React 19 + TypeScript", "Vite 8 (build + dev server)", "11 Screens", "Sidebar Navigation",
                "api.ts HTTP client", "JWT sessionStorage", "Tailwind CSS v4", "Explicite Midnight theme"]
    for i, item in enumerate(fe_items):
        dot(slide, 0.55, 1.92 + i*0.35 + 0.06, r=0.06, color=ACCENT)
        txt(slide, item, 0.68, 1.92 + i*0.35, 3.2, 0.3, size=11, color=TEXT)

    # HTTP arrow
    arr1 = slide.shapes.add_connector(1, Inches(4.05), Inches(4.27), Inches(4.6), Inches(4.27))
    arr1.line.color.rgb = CYAN; arr1.line.width = Pt(1.75)
    txt(slide, "HTTPS / JSON\n(port 8000)", 4.08, 4.35, 0.8, 0.4, size=8, color=TEXT2, align=PP_ALIGN.CENTER)

    # Backend / FastAPI
    box(slide, 4.62, 1.38, 4.28, 5.78, fill=RGBColor(0x0D, 0x16, 0x1A), border=CYAN, border_pt=0.75, radius=15000)
    txt(slide, "BACKEND / FastAPI", 4.78, 1.48, 4.0, 0.28, size=9, bold=True, color=CYAN)
    be_sections = [
        ("Auth",      ["JWT HS256", "Role-based access"]),
        ("APIs",      ["Projects · Issues · Analysis", "AI · Fixes · Learning · Tutor"]),
        ("Services",  ["Archive · Semgrep 1.181.0", "git_service (SSRF-safe)", "ai_service (Ollama / Anthropic)", "risk_scoring · duplication · cvss"]),
        ("Jobs",      ["Background async analysis", "ZIP + Git pipelines"]),
    ]
    by = 1.85
    for sec, items in be_sections:
        txt(slide, sec, 4.80, by, 0.8, 0.22, size=9, bold=True, color=CYAN)
        by += 0.22
        for it in items:
            dot(slide, 5.0, by+0.06, r=0.06, color=CYAN)
            txt(slide, it, 5.15, by, 3.55, 0.26, size=10.5, color=TEXT)
            by += 0.26
        by += 0.1

    # DB arrow
    arr2 = slide.shapes.add_connector(1, Inches(8.9), Inches(4.27), Inches(9.32), Inches(4.27))
    arr2.line.color.rgb = GREEN; arr2.line.width = Pt(1.75)
    txt(slide, "asyncpg\nORM", 8.93, 4.35, 0.6, 0.4, size=8, color=TEXT2, align=PP_ALIGN.CENTER)

    # Database
    box(slide, 9.35, 1.38, 3.62, 5.78, fill=RGBColor(0x0D, 0x17, 0x13), border=GREEN, border_pt=0.75, radius=15000)
    txt(slide, "PERSISTENCE", 9.5, 1.48, 3.4, 0.28, size=9, bold=True, color=GREEN)
    db_items = ["PostgreSQL 16", "SQLAlchemy 2.x async", "Alembic migrations", "",
                "users", "projects + memberships", "analysis_jobs + findings", "suggested_fixes",
                "learning resources + paths", "tutor_sessions + messages"]
    dy = 1.85
    for item in db_items:
        if item == "":
            dy += 0.1; continue
        dot(slide, 9.55, dy+0.06, r=0.06, color=GREEN)
        txt(slide, item, 9.68, dy, 3.1, 0.26, size=10.5, color=TEXT)
        dy += 0.26

    # Optional AI annotation
    box(slide, 4.62, 6.78, 4.28, 0.28, fill=RGBColor(0x0D, 0x14, 0x22), border=BORDER, border_pt=0.5, radius=10000)
    txt(slide, "External: Ollama (llama3, local)  ·  Anthropic API (optional)",
        4.75, 6.83, 4.0, 0.2, size=8.5, color=TEXT2, align=PP_ALIGN.CENTER)

    slide_num(slide, 6)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. Standard three-tier architecture: browser never talks directly to the database.\n"
        "2. Frontend at port 8443 (Vite dev server); backend at port 8000; PostgreSQL at 5434 (Docker).\n"
        "3. All AI calls go through ai_service.py — the provider is swappable without changing APIs.\n"
        "4. Analysis jobs are asynchronous — the frontend polls for status updates.\n"
        "Transition: Let's walk through the data flow when code is actually submitted.")
    return slide


def slide_07_dataflow(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Architecture", "Analysis Data Flow", slide_n=7)

    subtitle_line(slide, "Asynchronous pipeline: authentication → submission → job execution → results")

    steps = [
        ("1", "Authenticate",     "POST /auth/login\nJWT token issued",             ACCENT),
        ("2", "Select project",   "GET /projects\nMembership verified (role)",       ACCENT),
        ("3", "Submit code",      "POST .../analyse\n(ZIP) or .../analyse/git (Git)",CYAN),
        ("4", "Job created",      "AnalysisJob → queued\n202 returned immediately",  CYAN),
        ("5", "Background scan",  "Semgrep runs on\nextracted source",               AMBER),
        ("6", "Store results",    "Findings + metrics\n→ PostgreSQL",               GREEN),
        ("7", "Poll status",      "GET .../analyse/{id}\nFrontend polls until done", GREEN),
        ("8", "Inspect & act",    "View findings, AI explain,\ngenerate fix, learn", ACCENT),
    ]

    col_n = 4
    bw = 2.88
    bh = 0.95
    gap_x = 0.4
    gap_y = 0.45
    start_x = 0.35
    start_y = 1.42

    for i, (num, title, detail, color) in enumerate(steps):
        row = i // col_n
        col = i % col_n
        bx = start_x + col * (bw + gap_x)
        by_pos = start_y + row * (bh + gap_y)

        # Arrow within row (not after last in row or row-end)
        if col < col_n - 1:
            ax = bx + bw + 0.04
            arr = slide.shapes.add_connector(1, Inches(ax), Inches(by_pos + bh/2),
                                             Inches(ax + gap_x - 0.06), Inches(by_pos + bh/2))
            arr.line.color.rgb = TEXT2; arr.line.width = Pt(1.2)

        # Down arrow between rows for first column
        if row == 0 and col == col_n - 1:
            pass  # handled by visual flow

        box(slide, bx, by_pos, bw, bh, fill=SURFACE, border=color, border_pt=0.75, radius=15000)
        # Step number badge
        nb = slide.shapes.add_shape(1, Inches(bx+0.15), Inches(by_pos+0.17),
                                    Inches(0.35), Inches(0.35))
        nb.fill.solid(); nb.fill.fore_color.rgb = color; nb.line.fill.background()
        txt(slide, num, bx+0.15, by_pos+0.17, 0.35, 0.35, size=11, bold=True,
            color=BG, align=PP_ALIGN.CENTER)
        txt(slide, title, bx+0.62, by_pos+0.12, bw-0.75, 0.28, size=12, bold=True, color=TEXT)
        txt(slide, detail, bx+0.18, by_pos+0.48, bw-0.3, 0.42, size=10, color=TEXT2)

    # Validation / error note
    box(slide, 0.35, 4.85, 12.6, 0.42, fill=ELEVATED, border=BORDER, border_pt=0.5, radius=10000)
    txt(slide, "Validation gates: Git SSRF protection · URL scheme check · branch regex · ZIP bomb detection · "
               "10 MB upload limit · project membership enforced at every endpoint",
        0.55, 4.93, 12.1, 0.28, size=10.5, color=TEXT2)

    slide_num(slide, 7)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The 202 response in step 4 is critical — the API returns immediately and analysis runs in a background task.\n"
        "2. The frontend polls GET .../analyse/{job_id} until status is 'completed' or 'failed'.\n"
        "3. Git analysis includes SSRF protection: DNS resolution validates that resolved IPs are not private ranges.\n"
        "4. The source_path of the extracted archive is never exposed in any API response — security by design.\n"
        "Transition: What technology underpins each part of this pipeline?")
    return slide


def slide_08_stack(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Stack", "Technology Stack", slide_n=8)

    categories = [
        ("Frontend",   ACCENT,  ["React 19 + TypeScript", "Vite 8 (build + HMR)", "Tailwind CSS v4", "No router — custom NavCtx"]),
        ("Backend",    CYAN,    ["Python 3.14 + FastAPI", "Pydantic v2 (validation)", "Async SQLAlchemy 2.x", "asyncpg driver"]),
        ("Data",       GREEN,   ["PostgreSQL 16 (Docker)", "Alembic migrations", "9 DB migrations", "8 data models"]),
        ("Analysis",   AMBER,   ["Semgrep 1.181.0", "Python · Java · JS · TS rules", "Git clone (depth=1)", "SSRF-protected URL validation"]),
        ("AI",         RGBColor(0xC8, 0x7C, 0xF7), ["Ollama (llama3:latest, local)", "Anthropic API (configurable)", "Provider abstraction layer", "LLM_PROVIDER env switch"]),
        ("Testing",    RED,     ["pytest + pytest-asyncio", "18 test files", "426 tests passing", "httpx async test client"]),
    ]

    col_w = 3.9
    row_h = 2.0
    gap_x = 0.45
    gap_y = 0.35
    sx = 0.35
    sy = 1.35

    for i, (cat, color, items) in enumerate(categories):
        row = i // 3
        col = i % 3
        bx = sx + col * (col_w + gap_x)
        by = sy + row * (row_h + gap_y)

        box(slide, bx, by, col_w, row_h, fill=SURFACE, border=color, border_pt=0.75, radius=18000)
        # Color tag
        tag = slide.shapes.add_shape(1, Inches(bx+0.18), Inches(by+0.18), Inches(0.22), Inches(0.22))
        tag.fill.solid(); tag.fill.fore_color.rgb = color; tag.line.fill.background()
        txt(slide, cat, bx+0.5, by+0.16, col_w-0.65, 0.28, size=12, bold=True, color=color)
        for j, item in enumerate(items):
            dot(slide, bx+0.32, by+0.58 + j*0.32 + 0.06, r=0.06, color=color)
            txt(slide, item, bx+0.48, by+0.58 + j*0.32, col_w-0.62, 0.28, size=11, color=TEXT)

    slide_num(slide, 8)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. React 19 with no router library — navigation is managed by a custom NavCtx context.\n"
        "2. Python 3.14 and FastAPI with full async — all DB calls are non-blocking.\n"
        "3. Semgrep 1.181.0 is the active static analysis engine; it runs as a subprocess (shell=False).\n"
        "4. AI is modular — Ollama (local llama3) is the active provider; Anthropic is optional via .env.\n"
        "5. 426 automated tests across 18 test files verified the backend.\n"
        "Transition: Let's go deeper into each core feature, starting with code analysis.")
    return slide


def slide_09_analysis(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Feature 1", "Code Analysis & Repository Integration", slide_n=9)

    # Two path columns
    for col_i, (title, color, steps) in enumerate([
        ("ZIP Upload", ACCENT, [
            "User selects .zip archive (≤10 MB)",
            "Magic-byte validation + ZIP bomb check",
            "Safe extraction (path traversal blocked)",
            "Semgrep runs on extracted source tree",
            "Findings + metrics → stored",
            "HTTP 202 returned; frontend polls",
        ]),
        ("Git Repository", CYAN, [
            "User submits HTTPS URL + branch",
            "URL scheme + domain validation",
            "DNS resolution → private IP rejected (SSRF)",
            "git clone --depth 1 with timeout",
            ".git/ directory removed after clone",
            "Semgrep runs; commit SHA recorded",
        ]),
    ]):
        cx = 0.35 + col_i * 6.5
        box(slide, cx, 1.22, 6.2, 4.05, fill=SURFACE, border=color, border_pt=0.75, radius=15000)
        txt(slide, title, cx+0.25, 1.32, 5.7, 0.3, size=14, bold=True, color=color)
        for j, step in enumerate(steps):
            sy = 1.75 + j * 0.53
            nb = slide.shapes.add_shape(1, Inches(cx+0.22), Inches(sy+0.02),
                                        Inches(0.28), Inches(0.28))
            nb.fill.solid(); nb.fill.fore_color.rgb = color; nb.line.fill.background()
            txt(slide, str(j+1), cx+0.22, sy+0.02, 0.28, 0.28, size=9, bold=True,
                color=BG, align=PP_ALIGN.CENTER)
            txt(slide, step, cx+0.62, sy, 5.4, 0.3, size=11.5, color=TEXT)

    # VS divider
    txt(slide, "vs", 6.44, 3.05, 0.45, 0.45, size=18, bold=True, color=TEXT2, align=PP_ALIGN.CENTER)

    # Job lifecycle
    box(slide, 0.35, 5.42, 12.6, 0.52, fill=ELEVATED, border=BORDER, border_pt=0.5, radius=12000)
    txt(slide, "Job lifecycle:  queued  →  running  →  completed  (or failed with sanitised reason)",
        0.6, 5.54, 12.1, 0.3, size=11, color=TEXT2)
    for i, (st, col) in enumerate([("queued", TEXT2), ("running", AMBER), ("completed", GREEN), ("failed", RED)]):
        bx = 2.5 + i * 2.3
        box(slide, bx, 5.3, 1.85, 0.3, fill=SURFACE, border=col, border_pt=0.75, radius=15000)
        txt(slide, st, bx, 5.33, 1.85, 0.26, size=10, bold=True, color=col, align=PP_ALIGN.CENTER)

    slide_num(slide, 9)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. ZIP pipeline: archive.py validates magic bytes, checks for decompression bombs (100:1 ratio), "
        "blocks path traversal with secure chroot-like resolution.\n"
        "2. Git pipeline: git_service.py blocks HTTP, file://, ssh:// URLs; resolves DNS and checks all IPs "
        "against private ranges (RFC 1918, loopback, link-local).\n"
        "3. Source_path is never exposed in any API response — only the job ID and results are returned.\n"
        "4. Commit SHA is recorded so findings can always be traced to the exact revision analysed.\n"
        "Transition: What do the resulting findings look like?")
    return slide


def slide_10_findings(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Feature 2", "Findings, Metrics & Security Context", slide_n=10)

    # Finding card mock
    box(slide, 0.35, 1.22, 7.0, 3.25, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "Illustrative Finding Card", 0.5, 1.28, 6.8, 0.22, size=9, italic=True, color=TEXT2)

    sev_colors = {"Critical": RED, "High": AMBER, "Medium": CYAN, "Low": GREEN}
    sev_col = AMBER
    sev_box = slide.shapes.add_shape(1, Inches(0.5), Inches(1.6), Inches(0.9), Inches(0.28))
    sev_box.fill.solid(); sev_box.fill.fore_color.rgb = sev_col; sev_box.line.fill.background()
    txt(slide, "HIGH", 0.5, 1.6, 0.9, 0.28, size=9, bold=True, color=BG, align=PP_ALIGN.CENTER)

    type_box = slide.shapes.add_shape(1, Inches(1.5), Inches(1.6), Inches(1.5), Inches(0.28))
    type_box.fill.solid(); type_box.fill.fore_color.rgb = ELEVATED; type_box.line.fill.background()
    txt(slide, "Vulnerability", 1.5, 1.6, 1.5, 0.28, size=9, color=TEXT2, align=PP_ALIGN.CENTER)

    txt(slide, "SQL Injection via string formatting", 0.5, 2.0, 6.6, 0.3, size=14, bold=True, color=TEXT)
    txt(slide, "src/api/users.py  ·  line 42", 0.5, 2.35, 6.6, 0.22, size=10, color=TEXT2)

    finding_details = [
        ("Rule", "python.lang.security.audit.sqli"),
        ("CWE",  "CWE-89: Improper Neutralisation of SQL Commands"),
        ("OWASP","A03:2021 Injection"),
        ("CVSS", "7.5 HIGH  (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)"),
    ]
    for j, (k, v) in enumerate(finding_details):
        txt(slide, k + ":", 0.5, 2.62 + j*0.28, 1.0, 0.26, size=10, bold=True, color=TEXT2)
        txt(slide, v,       1.55, 2.62 + j*0.28, 5.5, 0.26, size=10, color=TEXT)

    txt(slide, "* Illustrative mock — not from real project data",
        0.35, 4.52, 7, 0.22, size=8, italic=True, color=TEXT2)

    # Metrics panel
    txt(slide, "Supporting Metrics (from live smoke test)", 7.6, 1.22, 5.7, 0.28, size=12, bold=True, color=TEXT)
    metrics = [
        ("Technical Debt",    "6h 15m",  AMBER, "(estimated from finding weights)"),
        ("Code Duplication",  "8.1%",    CYAN,  "(hash-based block detection)"),
        ("Coverage",          "N/A",     TEXT2, "(no coverage report provided)"),
        ("Risk Score",        "21 / 100",RED,   "(severity-weighted, open findings)"),
        ("Findings",          "29",      TEXT,  "(from pallets/flask git analysis)"),
    ]
    for j, (label, val, col, note) in enumerate(metrics):
        my = 1.62 + j * 0.62
        box(slide, 7.6, my, 5.6, 0.52, fill=SURFACE, border=BORDER, border_pt=0.5, radius=12000)
        txt(slide, label, 7.78, my+0.12, 2.5, 0.3, size=11, color=TEXT2)
        txt(slide, val,   10.35, my+0.08, 1.5, 0.36, size=16, bold=True, color=col, align=PP_ALIGN.RIGHT)
        txt(slide, note,  7.78, my+0.34, 4.8, 0.18, size=8.5, italic=True, color=TEXT2)

    txt(slide, "* Metric values from Phase O live API smoke test (pallets/flask, 2026-10-25)",
        7.6, 4.82, 5.7, 0.22, size=8, italic=True, color=TEXT2)

    slide_num(slide, 10)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. Each finding includes severity (Critical/High/Medium/Low), issue type, file path, line, rule key.\n"
        "2. CVSS v3.1 scores are computed from the vector string; v4.0 vectors are stored but not scored "
        "(v3.1 formula does not apply); generic code findings have no CVSS score.\n"
        "3. Technical debt is an estimate: each finding type has a configured minute cost — not actual dev hours.\n"
        "4. Duplication uses hash-based block detection across the source tree.\n"
        "5. Coverage is honestly reported as unavailable when no coverage report is present — never faked as 0.\n"
        "Transition: How does AI help developers understand these findings?")
    return slide


def slide_11_ai_explain(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Feature 3", "AI Explanations & Assistant", slide_n=11)

    # Provider architecture
    txt(slide, "AI Provider Architecture", 0.35, 1.22, 6, 0.28, size=13, bold=True, color=TEXT)

    prov_items = [
        ("Ollama  (active)", "llama3:latest · local · no API key", ACCENT),
        ("Anthropic (optional)", "claude-haiku-4-5 · API key required", RGBColor(0xC8, 0x7C, 0xF7)),
        ("None Provider (default)", "Returns 503 honestly when not configured", TEXT2),
    ]
    for j, (p, d, c) in enumerate(prov_items):
        box(slide, 0.35, 1.62 + j*0.58, 6.1, 0.52, fill=SURFACE, border=c, border_pt=0.75, radius=12000)
        txt(slide, p, 0.55, 1.72 + j*0.58, 3.5, 0.28, size=12, bold=True, color=c)
        txt(slide, d, 0.55, 1.98 + j*0.58, 5.6, 0.22, size=10, color=TEXT2)

    txt(slide, "Switched via LLM_PROVIDER env var — no API or UI changes needed.",
        0.35, 3.48, 6.1, 0.22, size=10, italic=True, color=TEXT2)

    # Explanation response schema
    hline(slide, 0.35, 3.78, 6.1, color=BORDER)
    txt(slide, "Explanation Response Fields", 0.35, 3.88, 6, 0.28, size=12, bold=True, color=TEXT)
    exp_fields = [
        ("what",         "What the finding means in context"),
        ("why",          "Why this may be a security / reliability risk"),
        ("how_it_arises","How this pattern typically appears in code"),
        ("remediation",  "Concrete steps to address the finding"),
        ("caveats",      "Limitations, false-positive risk, missing context"),
    ]
    for j, (f, d) in enumerate(exp_fields):
        txt(slide, f,  0.55, 4.22 + j*0.28, 1.7, 0.26, size=10.5, bold=True, color=ACCENT)
        txt(slide, d,  2.25, 4.22 + j*0.28, 4.1, 0.26, size=10.5, color=TEXT)

    # Right — sample output panel
    box(slide, 6.7, 1.22, 6.45, 5.2, fill=ELEVATED, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "Sample AI Explanation  (illustrative — captured from live Ollama run)",
        6.85, 1.28, 6.15, 0.22, size=8, italic=True, color=TEXT2)

    sample_lines = [
        ("What:", 10, True,  ACCENT),
        ("The analyser detected a 'return' statement inside a class __init__ method. "
         "This is syntactically unusual in Python and likely indicates a logic error.", 10, False, TEXT),
        ("", 6, False, TEXT),
        ("Why:", 10, True, ACCENT),
        ("Returning early from __init__ can leave the object in an inconsistent or partially "
         "initialised state, leading to unexpected AttributeError exceptions at runtime.", 10, False, TEXT),
        ("", 6, False, TEXT),
        ("Remediation:", 10, True, ACCENT),
        ("Remove the return statement. If early exit logic is needed, raise an exception "
         "or refactor into a factory method instead.", 10, False, TEXT),
        ("", 6, False, TEXT),
        ("Caveats:", 10, True, AMBER),
        ("AI output may be imprecise. Always review in context. Developer judgment required.", 9.5, True, AMBER),
    ]
    sy = 1.58
    for line_text, sz, bld, col in sample_lines:
        if line_text == "":
            sy += 0.12; continue
        txt(slide, line_text, 6.88, sy, 6.08, 0.35, size=sz, bold=bld, color=col)
        sy += 0.34 if len(line_text) > 50 else 0.28

    # Levels
    txt(slide, "Explanation levels: Beginner · Intermediate · Advanced", 6.7, 6.52, 6.45, 0.22,
        size=10, italic=True, color=TEXT2)

    slide_num(slide, 11)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The provider abstraction means the team can switch from Ollama to Anthropic by changing one .env variable.\n"
        "2. Prompts explicitly label finding data as DATA not instructions — prompt injection mitigation.\n"
        "3. The model output is validated: all 5 JSON fields must be present; truncated at 600 chars each.\n"
        "4. Explanation levels (beginner/intermediate/advanced) adjust the system prompt vocabulary.\n"
        "5. Emphasise: AI responses may be wrong — this is teaching assistance, not authoritative guidance.\n"
        "Transition: Beyond explaining, the system can propose a fix.")
    return slide


def slide_12_fix_learn(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Feature 4", "Suggested Fixes & Developer Learning", slide_n=12)

    # Left — Fixes
    box(slide, 0.35, 1.22, 6.2, 5.55, fill=SURFACE, border=ACCENT, border_pt=0.75, radius=15000)
    txt(slide, "🔧  Suggested Fix Workflow", 0.55, 1.32, 5.9, 0.3, size=13, bold=True, color=ACCENT)

    fix_steps = [
        ("Generate",   "POST .../issues/{id}/fix → AI proposes\nreplacement lines + rationale + caveats", ACCENT),
        ("Review",     "Developer inspects unified diff,\nrationale, and caveats panel", TEXT),
        ("Freshness",  "SHA-256 hash of original file\nchecked before approval (stale detection)", AMBER),
        ("Approve",    "Explicit POST .../approve — never automatic.\nDeveloper role required.", GREEN),
        ("Reject",     "POST .../reject — fix marked rejected;\noriginal source unchanged.", RED),
        ("Download",   "Approved fix → patched ZIP in memory\n(source_path never written to)", CYAN),
    ]
    for j, (step, desc, col) in enumerate(fix_steps):
        fy = 1.75 + j * 0.74
        nb = slide.shapes.add_shape(1, Inches(0.52), Inches(fy+0.05),
                                    Inches(0.28), Inches(0.28))
        nb.fill.solid(); nb.fill.fore_color.rgb = col; nb.line.fill.background()
        txt(slide, str(j+1), 0.52, fy+0.05, 0.28, 0.28, size=9, bold=True, color=BG, align=PP_ALIGN.CENTER)
        txt(slide, step, 0.92, fy+0.03, 1.5, 0.26, size=11, bold=True, color=col)
        txt(slide, desc, 0.92, fy+0.3, 5.5, 0.38, size=10.5, color=TEXT)

    # Right — Learning
    box(slide, 6.8, 1.22, 6.2, 5.55, fill=SURFACE, border=AMBER, border_pt=0.75, radius=15000)
    txt(slide, "🎓  Developer Learning & Tutor", 7.0, 1.32, 5.9, 0.3, size=13, bold=True, color=AMBER)

    learn_items = [
        ("Learning resources", "Curated articles and guides linked to CWE/OWASP categories."),
        ("Learning paths",     "Structured sequences with progress tracking per user."),
        ("Personalised recs",  "Deterministic matching: rule key → issue type → tag; "
                               "weighted by risk score; excludes already-completed resources."),
        ("Tutor session",      "POST /learning/tutor/start → per-user session.\nMulti-turn AI chat with conversation history."),
        ("Context-aware",      "Session tied to a specific learning resource;\ntopic context injected into system prompt."),
        ("Progress",           "Mark complete; progress tracked per user.\nCompleted resources excluded from recommendations."),
    ]
    ly = 1.75
    for label, desc in learn_items:
        dot(slide, 7.0, ly+0.06, r=0.07, color=AMBER)
        txt(slide, label + ":", 7.18, ly, 1.9, 0.26, size=11, bold=True, color=AMBER)
        txt(slide, desc, 7.18, ly+0.27, 5.65, 0.38, size=10.5, color=TEXT)
        ly += 0.75

    slide_num(slide, 12)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The LLM_FIX_MAX_TOKENS=2048 override was specifically needed because fix output can be many lines.\n"
        "2. Stale detection: if a source file changes between generation and approval, the fix is rejected with 409.\n"
        "3. The fix ZIP is created entirely in memory — no write to the original source_path.\n"
        "4. Recommendations are deterministic (no AI): rule_key match scores 3, issue type 2, tag 1.\n"
        "5. Tutor session messages are persisted — a user can leave and return to the same conversation.\n"
        "Transition: Let's talk about the UI/UX design decisions that make all of this usable.")
    return slide


def slide_13_ui(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Usability Design", "UI Design & Usability Decisions", slide_n=13)

    subtitle_line(slide, "Explicite Midnight — dark-first design system applied consistently across 11 screens")

    # Design token showcase
    txt(slide, "Design System Tokens", 0.35, 1.32, 5, 0.26, size=12, bold=True, color=TEXT)

    token_colors = [
        ("#090B10", BG,      "App background"),
        ("#11151D", SURFACE, "Card surface"),
        ("#1B2330", ELEVATED,"Elevated surface"),
        ("#4F8EF7", ACCENT,  "Primary accent"),
        ("#56D3F7", CYAN,    "Technical flow"),
        ("#3FB950", GREEN,   "Success / pass"),
        ("#E3B341", AMBER,   "Warning / debt"),
        ("#E5534B", RED,     "Critical severity"),
    ]
    for j, (hex_val, col, label) in enumerate(token_colors):
        cx_ = 0.35 + (j % 4) * 1.6
        cy_ = 1.68 + (j // 4) * 0.55
        swatch = slide.shapes.add_shape(1, Inches(cx_), Inches(cy_), Inches(0.35), Inches(0.32))
        swatch.fill.solid(); swatch.fill.fore_color.rgb = col
        swatch.line.color.rgb = BORDER; swatch.line.width = Pt(0.5)
        txt(slide, hex_val, cx_+0.42, cy_+0.04, 0.85, 0.16, size=8, color=TEXT)
        txt(slide, label,   cx_+0.42, cy_+0.19, 0.85, 0.15, size=8.5, color=TEXT2)

    # Annotation callouts
    hline(slide, 0.35, 2.88, 5.8, color=BORDER)
    txt(slide, "Key Usability Decisions", 0.35, 2.98, 5.8, 0.26, size=12, bold=True, color=TEXT)
    decisions = [
        (ACCENT, "Consistent design tokens",
         "All --xm-* CSS vars from a single source; light/dark themes via data-theme attribute."),
        (CYAN,   "Severity badge system",
         "Critical/High/Medium/Low shown as coloured badges — colour-coded consistently everywhere."),
        (GREEN,  "Progressive disclosure",
         "Dashboard → Issues → Issue Detail hierarchy; AI explanation and fix on demand."),
        (AMBER,  "System status feedback",
         "Job polling with status indicators; loading skeletons; error states with actionable messages."),
        (RED,    "Human oversight preserved",
         "Fix approval requires explicit action; AI unavailability shown honestly (503), not hidden."),
    ]
    for j, (col, label, desc) in enumerate(decisions):
        dy = 3.35 + j * 0.66
        accent_bar(slide, 0.35, dy, h=0.52, color=col)
        txt(slide, label, 0.55, dy+0.04, 2.2, 0.24, size=11, bold=True, color=col)
        txt(slide, desc,  0.55, dy+0.28, 5.5, 0.3, size=10.5, color=TEXT)

    # Screens list
    box(slide, 6.5, 1.22, 6.65, 5.55, fill=ELEVATED, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "11 Implemented Screens", 6.68, 1.32, 6.3, 0.26, size=12, bold=True, color=TEXT)
    screens = ["Login", "Dashboard", "Projects", "Code Analysis", "Issues",
               "Issue Detail", "AI Assistant", "Suggested Fix", "Learning", "Tutor Session", "Settings"]
    for j, s in enumerate(screens):
        sy2 = 1.72 + j * 0.45
        dot(slide, 6.72, sy2+0.1, r=0.07, color=ACCENT)
        txt(slide, s, 6.88, sy2, 6.15, 0.32, size=12, color=TEXT)

    txt(slide, "Typography: Inter (UI) + JetBrains Mono (code)\nTheme toggle: Settings → Appearance → Light/Dark",
        6.5, 6.35, 6.65, 0.38, size=10, italic=True, color=TEXT2)

    txt(slide, "Note: Visual QA at 1440/1280/768/390px widths is a planned manual step.",
        0.35, 6.92, 12.6, 0.22, size=8, italic=True, color=TEXT2)

    slide_num(slide, 13)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The --xm-* CSS custom properties mean every screen uses the same colour definitions.\n"
        "2. Light theme is implemented: html[data-theme='light'] overrides all tokens — not an afterthought.\n"
        "3. Severity badges use consistent colour coding: red=Critical, amber=High, cyan=Medium, green=Low.\n"
        "4. The sidebar provides persistent navigation — developers always know where they are.\n"
        "5. No formal usability study was conducted; the design is grounded in established heuristics.\n"
        "6. Manual browser QA at multiple viewport widths is still outstanding as of the Phase O report.\n"
        "Transition: Security and reliability controls in the implementation.")
    return slide


def slide_14_security(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Security", "Security, Validation & Reliability Controls", slide_n=14)

    controls = [
        ("Authentication & Authorisation", ACCENT, [
            "JWT HS256 bearer token; configurable expiry",
            "Three roles: viewer · developer · owner",
            "project_membership checked on every endpoint",
            "password_hash never exposed in API responses",
        ]),
        ("Input Validation", CYAN, [
            "Pydantic v2 models on all request bodies",
            "ZIP: magic bytes + bomb ratio + entry count",
            "Git URL: HTTPS-only; credentials in URL rejected",
            "Branch name: regex allowlist (alphanumeric + - / .)",
        ]),
        ("SSRF Protection", AMBER, [
            "DNS resolution of all Git hostnames",
            "All resolved IPs checked vs private ranges",
            "RFC 1918, loopback (127.x), link-local (169.254.x) blocked",
            "Note: app-level check; full network isolation not guaranteed",
        ]),
        ("Safe Process Execution", GREEN, [
            "Semgrep invoked with fixed args; shell=False",
            "Source directory passed as argument, not shell string",
            "Analysis runs in isolated temp directory",
            ".git/ removed after clone; source_path never in API",
        ]),
        ("AI & Fix Safeguards", RGBColor(0xC8, 0x7C, 0xF7), [
            "Finding data labelled as DATA in prompts",
            "Model output validated (required fields, length limits)",
            "Fix approval explicit; original source never written to",
            "Stale detection: SHA-256 hash check before approve",
        ]),
        ("Error Handling", TEXT2, [
            "AiUnavailableError → 503 (not a crash)",
            "Sanitised failure_reason (source_path stripped)",
            "Job marked failed; other jobs unaffected",
            "Standard HTTP status codes; no stack traces to client",
        ]),
    ]

    col_w = 4.0
    row_h = 1.72
    gap_x = 0.35
    gap_y = 0.22

    for i, (cat, col, items) in enumerate(controls):
        row = i // 3
        c = i % 3
        bx = 0.35 + c * (col_w + gap_x)
        by = 1.38 + row * (row_h + gap_y)
        box(slide, bx, by, col_w, row_h, fill=SURFACE, border=col, border_pt=0.75, radius=15000)
        txt(slide, cat, bx+0.18, by+0.14, col_w-0.3, 0.26, size=11, bold=True, color=col)
        for j, item in enumerate(items):
            dot(slide, bx+0.3, by+0.52 + j*0.3 + 0.06, r=0.06, color=col)
            txt(slide, item, bx+0.46, by+0.52 + j*0.3, col_w-0.6, 0.28, size=10.5, color=TEXT)

    slide_num(slide, 14)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. Role-based access: viewers can read; developers can submit and generate fixes; owners can approve.\n"
        "2. SSRF is mitigated at application level but a fully isolated network sandbox provides stronger guarantees.\n"
        "3. Semgrep runs with shell=False — no shell injection via user-provided file paths.\n"
        "4. The stale-source protection prevents approving a fix that was generated against an old version of a file.\n"
        "5. All AI errors are handled gracefully — the user sees a 503 message, not a stack trace.\n"
        "Transition: Testing and evaluation — what was actually verified?")
    return slide


def slide_15_testing(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Evaluation", "Testing & Evaluation", slide_n=15)

    subtitle_line(slide, "Evidence-led verification — automated tests, live API smoke tests, and reported build results")

    # Score cards
    score_cards = [
        ("426", "Backend Tests Passed", "(pytest, non-slow suite)", GREEN),
        ("1",   "Skipped", "(1 slow integration test)", TEXT2),
        ("0",   "Errors", "(clean run)", GREEN),
        ("62",  "Live API Checks", "(Phase O smoke test)", ACCENT),
        ("32",  "Frontend Modules", "(production build)", CYAN),
        ("0",   "TypeScript Errors", "(npm run build)", GREEN),
    ]

    card_w = 1.9
    card_h = 1.28
    gap = 0.35
    sx = 0.35
    sy = 1.52

    for i, (val, label, note, col) in enumerate(score_cards):
        cx = sx + (i % 3) * (card_w + gap * 1.5)
        cy = sy + (i // 3) * (card_h + 0.3)
        box(slide, cx, cy, card_w, card_h, fill=SURFACE, border=col, border_pt=0.75, radius=18000)
        txt(slide, val, cx, cy+0.12, card_w, 0.55, size=34, bold=True, color=col, align=PP_ALIGN.CENTER)
        txt(slide, label, cx, cy+0.7, card_w, 0.3, size=11, bold=True, color=TEXT, align=PP_ALIGN.CENTER)
        txt(slide, note, cx, cy+0.98, card_w, 0.22, size=8.5, italic=True, color=TEXT2, align=PP_ALIGN.CENTER)

    # Test file breakdown
    txt(slide, "Test Coverage Areas (18 test files)", 7.1, 1.52, 6.0, 0.28, size=12, bold=True, color=TEXT)
    test_files = [
        ("test_auth.py",            "JWT login, token validation"),
        ("test_analysis_pipeline.py","ZIP upload, job lifecycle"),
        ("test_git_analysis.py",    "Git clone, SSRF, URL validation"),
        ("test_metrics.py",         "Debt, duplication, CVSS scoring"),
        ("test_ai_service.py",      "Provider abstraction, prompt parsing"),
        ("test_ai_endpoints.py",    "Explain, assistant, caching"),
        ("test_fix_endpoints.py",   "Generate, approve, reject, stale"),
        ("test_tutor.py",           "Session, chat, history, isolation"),
        ("test_recommendations.py", "Deterministic matching logic"),
        ("+ 9 more files",          "Projects, issues, learning, scoring…"),
    ]
    for j, (fname, desc) in enumerate(test_files):
        ry = 1.92 + j * 0.43
        txt(slide, fname, 7.1, ry, 2.9, 0.28, size=10.5, bold=(j < 9), color=ACCENT if j < 9 else TEXT2)
        txt(slide, desc,  10.0, ry, 3.15, 0.28, size=10.5, color=TEXT)

    # Disclaimer box
    box(slide, 0.35, 5.72, 12.6, 0.62, fill=ELEVATED, border=AMBER, border_pt=0.75, radius=12000)
    txt(slide, "⚠  Clarifications: Automated backend tests ≠ formal usability evaluation  ·  "
               "Manual browser/responsive QA (1440→390px) is outstanding  ·  "
               "test_slow_integration.py excluded from baseline  ·  No user satisfaction study was conducted.",
        0.55, 5.82, 12.1, 0.45, size=10.5, color=AMBER)

    slide_num(slide, 15)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. All 426 passing tests and 62/62 smoke test checks were verified during Phase O (2026-10-25).\n"
        "2. The live smoke test used the actual running application with Ollama — not mocks.\n"
        "3. AI workflows (explain, assistant, fix generation, tutor chat) all passed with llama3:latest.\n"
        "4. Be clear: 426 unit/integration tests verify functionality, not usability.\n"
        "5. Manual visual QA at multiple viewport widths has not yet been formally documented.\n"
        "Transition: Every project has constraints — let's be honest about ours.")
    return slide


def slide_16_limitations(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Limitations", "Current Limitations & Constraints", slide_n=16)

    limitations = [
        ("AI Model Dependence", AMBER,
         "Response quality depends on the deployed model. llama3:latest (8B) may produce inaccurate "
         "or incomplete explanations and fixes. Provider outages affect all AI features."),
        ("Token Output Limit", AMBER,
         "LLM_MAX_TOKENS=512 is set for explain/chat; LLM_FIX_MAX_TOKENS=2048 for fixes. "
         "Very long source snippets may still truncate outputs in edge cases."),
        ("Analysis Engine Scope", CYAN,
         "Semgrep analyses Python, Java, JavaScript, and TypeScript. Other languages "
         "pass through without findings — no error is shown, which may be misleading."),
        ("Coverage Unavailable", CYAN,
         "Test coverage percentage cannot be inferred without an actual coverage report. "
         "Reported correctly as unavailable — not as 0%."),
        ("Estimates, Not Measurements", TEXT2,
         "Technical debt (in minutes) and duplication percentage are estimates "
         "derived from heuristic weights, not measured engineering hours."),
        ("SSRF Mitigation (Partial)", RED,
         "Git URL validation blocks private IPs at application level. A fully isolated "
         "network sandbox or egress firewall provides stronger protection."),
        ("Manual Browser QA Outstanding", TEXT2,
         "Responsive visual QA (1440/1280/768/390px) and theme-toggle verification "
         "across all 11 screens has not yet been formally documented."),
        ("No Formal Usability Study", TEXT2,
         "No user research, A/B testing, or SUS/NPS measurement was conducted. "
         "Usability goals are grounded in design principles, not empirical evidence."),
    ]

    for i, (label, col, desc) in enumerate(limitations):
        row = i // 2
        c = i % 2
        bx = 0.35 + c * 6.5
        by = 1.38 + row * 1.42
        box(slide, bx, by, 6.2, 1.35, fill=SURFACE, border=col, border_pt=0.75, radius=15000)
        # Icon strip
        strip = slide.shapes.add_shape(1, Inches(bx), Inches(by), Inches(0.12), Inches(1.35))
        strip.fill.solid(); strip.fill.fore_color.rgb = col
        strip.line.fill.background()
        txt(slide, label, bx+0.25, by+0.1, 5.8, 0.28, size=12, bold=True, color=col)
        txt(slide, desc,  bx+0.25, by+0.45, 5.8, 0.82, size=10.5, color=TEXT)

    slide_num(slide, 16)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. The AI limitations are inherent to the current model size — llama3:latest (8B) is capable but not infallible.\n"
        "2. The SSRF partial-mitigation note is important: we protect at the app layer, but a real deployment "
        "should add network-level egress controls.\n"
        "3. Metrics honesty: we never show 0% coverage when we simply don't have the data.\n"
        "4. No user study is an honest limitation for a Usability Design subject — "
        "the design was guided by principles, not measurement.\n"
        "Transition: What's next, and who built what?")
    return slide


def slide_17_future_contributions(prs):
    slide = blank_slide(prs)
    content_header(prs, slide, "Future & Team", "Future Scope & Team Contributions", slide_n=17)

    # Future scope — left half
    box(slide, 0.35, 1.22, 6.2, 5.55, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "🚀  Future Scope", 0.55, 1.32, 5.9, 0.3, size=13, bold=True, color=ACCENT)
    futures = [
        ("Formal usability testing",     "Conduct user studies; measure task completion and SUS score."),
        ("Accessibility evaluation",     "WCAG 2.1 audit; keyboard navigation; screen-reader support."),
        ("Browser-based regression tests","Playwright/Cypress E2E tests for all 11 screens."),
        ("CI/CD pipeline",               "Automated build, test, and deploy on push (GitHub Actions)."),
        ("Expanded analysis rules",      "Add more Semgrep rule packs; support additional languages."),
        ("AI output validation",         "Structured post-processing to improve fix proposal quality."),
        ("Collaborative features",       "Multi-user comments, notifications, and issue assignment."),
    ]
    fy = 1.78
    for label, desc in futures:
        dot(slide, 0.55, fy+0.08, r=0.07, color=ACCENT)
        txt(slide, label + ":", 0.73, fy, 2.2, 0.26, size=11, bold=True, color=TEXT)
        txt(slide, desc, 0.73, fy+0.28, 5.7, 0.3, size=10.5, color=TEXT2)
        fy += 0.68

    # Team contributions — right half
    box(slide, 6.8, 1.22, 6.2, 5.55, fill=SURFACE, border=BORDER, border_pt=0.5, radius=15000)
    txt(slide, "👥  Team Contributions", 7.0, 1.32, 5.9, 0.3, size=13, bold=True, color=CYAN)

    txt(slide, "Group 6", 7.0, 1.78, 5.9, 0.28, size=14, bold=True, color=TEXT)

    # Member 1
    box(slide, 7.0, 2.18, 5.8, 2.12, fill=ELEVATED, border=CYAN, border_pt=0.5, radius=12000)
    txt(slide, "Dhruv Sharma", 7.18, 2.28, 5.5, 0.3, size=13, bold=True, color=CYAN)
    txt(slide, "24BBS0063", 7.18, 2.6, 5.5, 0.22, size=10, color=TEXT2)
    txt(slide, "Git commit author  ·  project repository on GitHub\n"
               "[Confirm: specific feature responsibilities\n"
               " e.g. backend phases, frontend design, testing]",
        7.18, 2.85, 5.5, 0.98, size=10.5, color=TEXT)

    # Member 2
    box(slide, 7.0, 4.45, 5.8, 2.12, fill=ELEVATED, border=ACCENT, border_pt=0.5, radius=12000)
    txt(slide, "Rijul Kothawade", 7.18, 4.55, 5.5, 0.3, size=13, bold=True, color=ACCENT)
    txt(slide, "24BBS0230", 7.18, 4.87, 5.5, 0.22, size=10, color=TEXT2)
    txt(slide, "[Confirm: specific feature responsibilities\n"
               " e.g. frontend screens, documentation,\n"
               " presentation, testing coordination]",
        7.18, 5.12, 5.5, 0.98, size=10.5, color=TEXT)

    txt(slide, "⚠  Contribution placeholders — team should fill in before presenting.",
        6.8, 6.82, 6.2, 0.22, size=9, italic=True, color=AMBER)

    slide_num(slide, 17)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Key talking points:\n"
        "1. Future items are labelled as planned — none are implemented yet.\n"
        "2. Formal usability testing is the highest-priority next step for this subject.\n"
        "3. IMPORTANT: The contribution fields for both team members contain placeholders. "
        "Both Dhruv Sharma and Rijul Kothawade must confirm and fill in their actual responsibilities "
        "before the presentation. The Git commit author field shows Dhruv Sharma, but this alone "
        "does not capture the full division of work.\n"
        "4. Consider the exact distribution: who designed which screens, who implemented which APIs, "
        "who wrote which tests, who prepared the documentation, etc.\n"
        "Transition: A brief summary to close.")
    return slide


def slide_18_conclusion(prs):
    slide = blank_slide(prs)
    bg(slide, RGBColor(0x06, 0x08, 0x0D))

    # Accent strip (same as cover)
    strip = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.18), Inches(7.5))
    strip.fill.solid(); strip.fill.fore_color.rgb = ACCENT
    strip.line.fill.background()

    txt(slide, "USABILITY DESIGN AND SOFTWARE APPLICATIONS  ·  GROUP 6",
        0.5, 0.45, 10, 0.28, size=8.5, bold=True, color=ACCENT)

    txt(slide, "Explicite AI", 0.5, 1.05, 9, 0.85, size=52, bold=True, color=TEXT)

    bar2 = slide.shapes.add_shape(1, Inches(0.5), Inches(2.02), Inches(3.5), Inches(0.055))
    bar2.fill.solid(); bar2.fill.fore_color.rgb = ACCENT; bar2.line.fill.background()

    # Three key takeaways
    txt(slide, "Key Contributions", 0.5, 2.22, 9, 0.3, size=14, bold=True, color=TEXT)

    takeaways = [
        (ACCENT, "Integrated analysis workflow",
         "ZIP and Git repository analysis → categorised, severity-ranked findings with supporting metrics."),
        (CYAN,   "AI-assisted understanding",
         "Structured, level-adjusted explanations; suggested fixes with explicit approval; multi-turn tutor chat."),
        (GREEN,  "Usability-oriented design",
         "Explicite Midnight design system: consistent tokens, clear hierarchy, feedback states, human oversight."),
    ]
    for j, (col, label, desc) in enumerate(takeaways):
        ty = 2.68 + j * 0.98
        nb = slide.shapes.add_shape(1, Inches(0.5), Inches(ty+0.12), Inches(0.18), Inches(0.58))
        nb.fill.solid(); nb.fill.fore_color.rgb = col; nb.line.fill.background()
        txt(slide, label, 0.82, ty+0.1, 7.5, 0.28, size=13, bold=True, color=col)
        txt(slide, desc,  0.82, ty+0.42, 8.5, 0.48, size=12, color=TEXT)

    hline(slide, 0.5, 5.68, 9, color=BORDER)

    # Team sign-off
    txt(slide, "Dhruv Sharma — 24BBS0063     ·     Rijul Kothawade — 24BBS0230",
        0.5, 5.82, 10, 0.28, size=12, color=TEXT2)

    txt(slide, "github.com/DHRUVSHARMA2005/Explicite-AI",
        0.5, 6.15, 9, 0.26, size=11, color=TEXT2)

    # Final tag line
    txt(slide, "Thank you", 0.5, 6.55, 5, 0.55, size=28, bold=True, color=TEXT)

    slide_num(slide, 18)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        "Closing talking points:\n"
        "1. Explicite AI solves a real pain point: going from a static-analysis finding to understanding and "
        "action is now a single integrated workflow.\n"
        "2. The AI is advisory — the system preserves developer agency through explicit approval steps.\n"
        "3. Designed with usability principles in mind: consistent, discoverable, with clear feedback.\n"
        "4. The codebase is fully verified: 426 automated tests, 62 live API checks, production build clean.\n"
        "Leave time for questions. Be ready to discuss any of the 18 slides in detail.")
    return slide


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN BUILD
# ═══════════════════════════════════════════════════════════════════════════════

def build():
    prs = new_prs()

    builders = [
        slide_01_cover,
        slide_02_problem,
        slide_03_objectives,
        slide_04_solution,
        slide_05_users,
        slide_06_architecture,
        slide_07_dataflow,
        slide_08_stack,
        slide_09_analysis,
        slide_10_findings,
        slide_11_ai_explain,
        slide_12_fix_learn,
        slide_13_ui,
        slide_14_security,
        slide_15_testing,
        slide_16_limitations,
        slide_17_future_contributions,
        slide_18_conclusion,
    ]

    for i, builder in enumerate(builders, 1):
        print(f"  Building slide {i:02d}: {builder.__name__} ...", end=" ", flush=True)
        try:
            builder(prs)
            print("OK")
        except Exception as e:
            print(f"ERROR: {e}")
            raise

    prs.save(str(PPTX_PATH))
    print(f"\nSaved: {PPTX_PATH}")
    print(f"Slides: {len(prs.slides)}")
    return prs

if __name__ == "__main__":
    print("Building Explicite AI Presentation...")
    build()
    print("Done.")
