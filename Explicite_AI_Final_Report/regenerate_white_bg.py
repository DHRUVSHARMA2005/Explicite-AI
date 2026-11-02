"""
Regenerate all charts and diagrams with white backgrounds for print-quality output.
White backgrounds are required for printed academic reports.
Saves to Report_Assets/ with the same filenames, overwriting the dark-bg versions.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "Report_Assets"
OUT.mkdir(exist_ok=True)

# ── Print-friendly colour palette (dark text on white background) ─────────────
BG      = "white"
AX_BG   = "#F8F9FA"
TEXT_C  = "#1C2128"
MUTED_C = "#57606A"
GRID_C  = "#D0D7DE"
BORDER_C = "#D0D7DE"
SURFACE = "#F0F6FF"

# Vivid accent colours — adjusted for white-background legibility
BLUE   = "#0969DA"
GREEN  = "#2DA44E"
AMBER  = "#9A6700"
RED    = "#CF222E"
PURPLE = "#8250DF"
CYAN   = "#1B7C83"
ORANGE = "#BC4C00"
SLATE  = "#57606A"


def _style_light(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(AX_BG)
    ax.tick_params(colors=TEXT_C, labelsize=9)
    ax.title.set_color(TEXT_C)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
        spine.set_linewidth(0.8)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)


# ── Chart 1: Module Distribution ─────────────────────────────────────────────
def chart_module_distribution():
    categories = [
        "Test Files", "Services", "Frontend Screens",
        "API Routes", "DB Models", "Alembic Migrations",
        "Schemas", "Frontend Components"
    ]
    counts = [20, 13, 11, 8, 6, 9, 7, 3]
    colors = [BLUE, GREEN, PURPLE, AMBER, CYAN, RED, ORANGE, SLATE]

    fig, ax = plt.subplots(figsize=(9, 5))
    _style_light(fig, ax)
    bars = ax.barh(categories, counts, color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, counts):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', color=TEXT_C, fontsize=10, fontweight='bold')
    ax.set_xlabel("Count", color=TEXT_C, fontsize=10)
    ax.set_title("Project Module Distribution (Verified from Codebase)", color=TEXT_C,
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(0, 26)
    ax.grid(axis='x', color=GRID_C, linestyle='--', alpha=0.7)
    ax.invert_yaxis()
    fig.text(0.13, 0.01, "Source: Direct codebase inspection, 2026-11-02",
             color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(str(OUT / "chart01_module_distribution.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart01_module_distribution.png  [white bg]")


# ── Chart 2: Test Results ─────────────────────────────────────────────────────
def chart_test_results():
    labels = ['Passed (426)', 'Skipped (1)']
    sizes = [426, 1]
    colors = [GREEN, AMBER]
    explode = (0.03, 0.08)

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=90,
        textprops={'color': TEXT_C, 'fontsize': 11},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
    ax.set_title("Backend Test Suite Results\n427 Tests Collected (0 Failures)",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=14)
    fig.text(0.5, 0.01,
             "Source: pytest run, 2026-11-02 (venv/Scripts/python -m pytest tests/)",
             ha='center', color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.09)
    fig.savefig(str(OUT / "chart02_test_results.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart02_test_results.png  [white bg]")


# ── Chart 3: Feature Implementation Status ────────────────────────────────────
def chart_feature_status():
    labels = ['Fully Implemented\n(21)', 'Partially Implemented\n(4)', 'Planned\n(5)']
    sizes = [21, 4, 5]
    colors = [GREEN, AMBER, RED]
    explode = (0.03, 0.06, 0.06)

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=140,
        textprops={'color': TEXT_C, 'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
    ax.set_title("Feature Implementation Status\n30 Features Assessed",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=14)
    fig.text(0.5, 0.01,
             "Partial: missing language support warning, CVSS 4.0 scoring, "
             "formal accessibility audit, SSRF network-level isolation",
             ha='center', color=MUTED_C, fontsize=7.5, wrap=True)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(str(OUT / "chart03_feature_status.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart03_feature_status.png  [white bg]")


# ── Chart 4: Vulnerability Severity Distribution ──────────────────────────────
def chart_severity_distribution():
    severities = ['High', 'Medium', 'Low', 'Critical']
    counts = [3, 2, 1, 0]
    colors = [AMBER, CYAN, GREEN, RED]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    _style_light(fig, ax)
    bars = ax.bar(severities, counts, color=colors, width=0.5, edgecolor="none")
    for bar, val in zip(bars, counts):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.06,
                    str(val), ha='center', va='bottom', color=TEXT_C, fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Findings", color=TEXT_C, fontsize=10)
    ax.set_xlabel("Severity Level", color=TEXT_C, fontsize=10)
    ax.set_title("Vulnerability Severity Distribution\n(Student Management System — 6 Findings)",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=12)
    ax.set_ylim(0, 4.5)
    ax.grid(axis='y', color=GRID_C, linestyle='--', alpha=0.7)
    fig.text(0.5, 0.01,
             "Source: Live application data — GET /api/v1/projects/{id}/issues, 2026-11-02",
             ha='center', color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(str(OUT / "chart04_severity_distribution.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart04_severity_distribution.png  [white bg]")


# ── Chart 5: Competitor Feature Comparison Matrix ─────────────────────────────
def chart_competitor_matrix():
    tools = ['Explicite AI', 'SonarQube', 'Snyk Code', 'GitHub CodeQL', 'Semgrep CE']
    features = [
        'Static Analysis',
        'Vuln Detection',
        'CVSS Scoring',
        'AI Explanations',
        'Fix Suggestions',
        'Learning Pathway',
        'CI/CD Integration'
    ]
    data = np.array([
        [2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2],
        [2, 2, 1, 1, 0],
        [2, 0, 1, 0, 0],
        [2, 0, 2, 0, 0],
        [2, 0, 0, 0, 0],
        [0, 2, 2, 2, 2],
    ])

    cmap = matplotlib.colors.ListedColormap(['#CF222E', '#E6A817', '#2DA44E'])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.imshow(data, cmap=cmap, vmin=0, vmax=2, aspect='auto')

    ax.set_xticks(range(len(tools)))
    ax.set_xticklabels(tools, color=TEXT_C, fontsize=10, fontweight='bold')
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features, color=TEXT_C, fontsize=10)
    ax.tick_params(length=0)

    labels_map = {0: '✗', 1: '~', 2: '✓'}
    for i in range(len(features)):
        for j in range(len(tools)):
            ax.text(j, i, labels_map[data[i, j]], ha='center', va='center',
                    color='white', fontsize=14, fontweight='bold')

    ax.set_title("Competitor Feature Comparison Matrix",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=14)

    legend_patches = [
        mpatches.Patch(color='#2DA44E', label='✓ Full support'),
        mpatches.Patch(color='#E6A817', label='~ Partial / paid tier'),
        mpatches.Patch(color='#CF222E', label='✗ Not supported'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', facecolor=BG,
              labelcolor=TEXT_C, fontsize=9, framealpha=0.9, edgecolor=GRID_C)
    fig.text(0.5, 0.01, "Source: Official product documentation, 2025–2026",
             ha='center', color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.08)
    fig.savefig(str(OUT / "chart05_competitor_matrix.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart05_competitor_matrix.png  [white bg]")


# ── Chart 6: Technology Stack ──────────────────────────────────────────────────
def chart_tech_stack():
    categories = [
        'Backend (FastAPI/Python)',
        'Database (PostgreSQL/SQLAlchemy)',
        'Frontend (React/TypeScript)',
        'Analysis Engine (Semgrep)',
        'AI Layer (Ollama/Anthropic)',
        'Testing (pytest/httpx)',
        'Build & Tooling (Vite/Alembic)',
    ]
    counts = [13, 9, 14, 2, 3, 20, 6]
    colors = [BLUE, GREEN, PURPLE, RED, AMBER, CYAN, ORANGE]

    fig, ax = plt.subplots(figsize=(9.5, 5))
    _style_light(fig, ax)
    bars = ax.barh(categories, counts, color=colors, height=0.6, edgecolor='none')
    for bar, val in zip(bars, counts):
        ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', color=TEXT_C, fontsize=10, fontweight='bold')
    ax.set_xlabel("Number of Files / Components", color=TEXT_C, fontsize=10)
    ax.set_title("Technology Stack — Files per Layer (Verified from Repository)",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(0, 26)
    ax.grid(axis='x', color=GRID_C, linestyle='--', alpha=0.7)
    ax.invert_yaxis()
    fig.text(0.13, 0.01, "Source: Direct repository file count, 2026-11-02",
             color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(str(OUT / "chart06_tech_stack.png"), dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("  chart06_tech_stack.png  [white bg]")


# ── Chart 7: SDG Contribution ─────────────────────────────────────────────────
def chart_sdg():
    sdgs = ['SDG 4\nQuality Education', 'SDG 9\nIndustry & Innovation', 'SDG 16\nPeace & Institutions']
    feature_counts = [5, 6, 3]
    colors = [PURPLE, BLUE, GREEN]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    _style_light(fig, ax)
    bars = ax.bar(sdgs, feature_counts, color=colors, width=0.45, edgecolor='none')
    for bar, val in zip(bars, feature_counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.1,
                str(val), ha='center', va='bottom', color=TEXT_C, fontsize=12, fontweight='bold')

    ax.set_ylabel("Number of Features Contributing", color=TEXT_C, fontsize=10)
    ax.set_title("SDG Contribution — Implemented Feature Count per SDG",
                 color=TEXT_C, fontsize=12, fontweight='bold', pad=12)
    ax.set_ylim(0, 8)
    ax.grid(axis='y', color=GRID_C, linestyle='--', alpha=0.7)
    fig.text(0.5, 0.01,
             "Note: Represents potential contribution based on implemented features, "
             "not measured social impact. Source: Feature-SDG mapping, 2026.",
             ha='center', color=MUTED_C, fontsize=8)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(str(OUT / "chart07_sdg.png"), dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("  chart07_sdg.png  [white bg]")


# ── Diagram 1: System Architecture ────────────────────────────────────────────
def diagram_system_arch():
    BG2   = "white"
    SURF  = "#EFF2F5"
    ACC   = "#0969DA"
    GRN   = "#2DA44E"
    AMB   = "#9A6700"
    PUR   = "#8250DF"
    CYN   = "#1B7C83"
    R     = "#CF222E"
    TXT   = "#1C2128"
    MUT   = "#57606A"
    BDR   = "#D0D7DE"

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(BG2)
    ax.set_facecolor('#F6F8FA')
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title("Explicite AI — System Architecture", color=TXT, fontsize=13,
                 fontweight='bold', pad=12)

    def _box(x, y, w, h, text, fill, txt_c=TXT, fontsize=9.5, bold=False, edge=BDR):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                               facecolor=fill, edgecolor=edge, linewidth=1.2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                color=txt_c, fontsize=fontsize, fontweight='bold' if bold else 'normal',
                zorder=4, multialignment='center')

    def _arrow(x1, y1, x2, y2, color=MUT):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0"))

    # Layer separators
    for y, label in [(5.6, "FRONTEND LAYER"), (3.6, "BACKEND LAYER"), (1.3, "DATA / INTEGRATION LAYER")]:
        ax.text(0.15, y, label, color=MUT, fontsize=8, fontweight='bold')
        ax.axhline(y - 0.05, color=BDR, linestyle='--', alpha=0.7, xmin=0.01, xmax=0.99)

    # Frontend screens
    screens = ["Login", "Dashboard", "Findings", "AI Assistant", "Learning", "Settings"]
    for i, s in enumerate(screens):
        x = 0.3 + i * 1.9
        _box(x, 5.7, 1.6, 0.55, s, SURF, TXT, fontsize=8)
    _box(0.1, 5.25, 11.8, 0.6,
         "React 19 + TypeScript + Vite 8  (Single Page Application, port 8443)",
         "#DDEEFF", ACC, fontsize=9, bold=True, edge=ACC)

    # API boxes
    _box(0.3, 3.7, 3.8, 0.7, "FastAPI\n(Python 3.14.3, /api/v1)", "#DDEEFF", ACC, fontsize=9, bold=True, edge=ACC)
    _box(4.3, 3.7, 3.4, 0.7, "Auth + RBAC\n(JWT HS256, bcrypt)", SURF, AMB, fontsize=9, edge=AMB)
    _box(7.9, 3.7, 3.8, 0.7, "Background Jobs\n(FastAPI BackgroundTasks)", SURF, GRN, fontsize=9, edge=GRN)

    # Services
    services = [
        ("Analysis\nEngine\n(Semgrep 1.181)", R, 0.2),
        ("CVSS 3.1\nScoring", AMB, 2.1),
        ("AI Service\n(Ollama/Anthropic)", PUR, 4.0),
        ("Git Service\n(SSRF Guard)", GRN, 5.9),
        ("Archive\nService", CYN, 7.8),
        ("Fix Service\n(SHA-256 check)", ACC, 9.7),
    ]
    for text, tc, x in services:
        _box(x + 0.1, 2.4, 1.7, 0.85, text, SURF, tc, fontsize=8, edge=tc)

    # Data layer
    _box(0.2,  0.6, 3.2, 0.75, "PostgreSQL 16\n(port 5434, 9 migrations)", "#E6F4EA", GRN, fontsize=9, bold=True, edge=GRN)
    _box(3.7,  0.6, 3.5, 0.75, "Ollama\n(llama3, localhost:11434)", "#F3E8FF", PUR, fontsize=9, bold=True, edge=PUR)
    _box(7.5,  0.6, 2.3, 0.75, "Anthropic API\n(claude-haiku-4-5)", "#FFF8E1", AMB, fontsize=9, bold=True, edge=AMB)
    _box(10.1, 0.6, 1.7, 0.75, "File System\n(uploads/, tmp/)", SURF, MUT, fontsize=8, edge=BDR)

    # Arrows
    _arrow(6.0, 5.25, 6.0, 4.4, ACC)
    for x in [1.05, 2.95, 4.75, 6.65, 8.55, 10.4]:
        _arrow(x, 3.7, x, 3.25, BDR)
    for sx in [1.05, 5.05, 6.95]:
        _arrow(sx, 2.4, sx, 1.35, BDR)

    ax.text(6.0, 0.15, "Source: Explicite AI implementation — verified 2026-11-02",
            ha='center', color=MUT, fontsize=8)

    fig.tight_layout()
    fig.savefig(str(OUT / "diag01_system_arch.png"), dpi=150, bbox_inches='tight', facecolor=BG2)
    plt.close()
    print("  diag01_system_arch.png  [white bg]")


# ── Diagram 2: ER Diagram ─────────────────────────────────────────────────────
def diagram_er():
    BG2   = "white"
    SURF  = "#FAFBFC"
    ACC   = "#0969DA"
    GRN   = "#2DA44E"
    AMB   = "#9A6700"
    PUR   = "#8250DF"
    CYN   = "#1B7C83"
    R     = "#CF222E"
    ORG   = "#BC4C00"
    SLT   = "#57606A"
    TXT   = "#1C2128"
    MUT   = "#57606A"
    BDR   = "#D0D7DE"

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG2)
    ax.set_facecolor('#F6F8FA')
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Explicite AI — Database Entity-Relationship Overview", color=TXT, fontsize=13,
                 fontweight='bold', pad=12)

    entities = {
        "users":              (0.3, 5.5, 2.2, 2.0, ["PK id (UUID)", "email (unique)", "password_hash", "full_name",
                                                      "system_role", "experience_level", "preferences (JSONB)"], ACC),
        "projects":           (3.2, 5.5, 2.2, 1.6, ["PK id (UUID)", "name", "description",
                                                      "owner_id (FK→users)", "created_at"], GRN),
        "project_memberships":(6.1, 5.9, 2.3, 1.2, ["project_id (FK)", "user_id (FK)",
                                                      "role (viewer/developer/owner)"], AMB),
        "analysis_jobs":      (3.2, 2.8, 2.4, 2.3, ["PK id (UUID)", "project_id (FK)",
                                                      "status (queued→completed)", "engine_name/version",
                                                      "bugs/vulns/smells count", "technical_debt_minutes",
                                                      "repo_url, source_path"], PUR),
        "findings":           (0.3, 0.6, 2.4, 2.3, ["PK id (UUID)", "analysis_job_id (FK)",
                                                      "engine_severity, risk_level", "issue_type, title",
                                                      "cvss_score, cvss_vector", "status (Open/In Review/Resolved)",
                                                      "ai_explanation (Text)"], R),
        "suggested_fixes":    (6.1, 0.6, 2.3, 2.0, ["PK id (UUID)", "finding_id (FK)",
                                                      "proposed_lines (JSONB)", "rationale, caveats",
                                                      "original_hash (SHA-256)", "status (pending/approved/rejected)"], CYN),
        "learning_resources": (9.2, 5.3, 2.5, 1.7, ["PK id (UUID)", "title, url",
                                                      "resource_type", "tags (JSONB)",
                                                      "cwe_ids, rule_keys"], ORG),
        "tutor_sessions":     (9.2, 2.7, 2.5, 1.5, ["PK id (UUID)", "user_id (FK)",
                                                      "resource_id (FK)", "created_at"], SLT),
        "tutor_messages":     (9.2, 0.6, 2.5, 1.5, ["PK id (UUID)", "session_id (FK)",
                                                      "role (user/assistant)", "content (Text)"], "#57606A"),
    }

    for name, (x, y, w, h, fields, color) in entities.items():
        # Header bar (coloured)
        hdr = FancyBboxPatch((x, y + h - 0.38), w, 0.38, boxstyle="round,pad=0.03",
                              facecolor=color, edgecolor=BDR, linewidth=1.0, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.19, name, ha='center', va='center',
                color='white', fontsize=9, fontweight='bold', zorder=4)
        # Body (white)
        body = FancyBboxPatch((x, y), w, h - 0.38, boxstyle="round,pad=0.03",
                               facecolor=SURF, edgecolor=BDR, linewidth=1.0, zorder=2)
        ax.add_patch(body)
        for fi, field in enumerate(fields):
            col = GRN if field.startswith("PK") else TXT
            ax.text(x + 0.1, y + h - 0.5 - fi * 0.26, field,
                    va='top', color=col, fontsize=7, zorder=4)

    # Relationship lines
    rels = [
        (1.4, 5.5, 4.3, 7.1),
        (2.5, 6.5, 6.1, 6.5),
        (5.4, 6.8, 6.1, 6.5),
        (4.3, 5.5, 4.3, 5.1),
        (3.2, 3.9, 2.7, 2.9),
        (2.7, 1.7, 6.1, 1.7),
        (2.5, 5.5, 10.4, 4.2),
        (10.4, 5.3, 10.4, 4.2),
        (10.4, 2.7, 10.4, 2.1),
    ]
    for x1, y1, x2, y2 in rels:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-", color=MUT, lw=1.0,
                                   connectionstyle="arc3,rad=0"))

    ax.text(6.0, 0.12, "Source: SQLAlchemy model files — verified 2026-11-02",
            ha='center', color=MUT, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "diag02_er_diagram.png"), dpi=150, bbox_inches='tight', facecolor=BG2)
    plt.close()
    print("  diag02_er_diagram.png  [white bg]")


# ── Diagram 3: Analysis Workflow ──────────────────────────────────────────────
def diagram_workflow():
    BG2  = "white"
    SURF = "#FAFBFC"
    ACC  = "#0969DA"
    GRN  = "#2DA44E"
    AMB  = "#9A6700"
    PUR  = "#8250DF"
    CYN  = "#1B7C83"
    R    = "#CF222E"
    ORG  = "#BC4C00"
    TXT  = "#1C2128"
    MUT  = "#57606A"
    BDR  = "#D0D7DE"

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG2)
    ax.set_facecolor('#F6F8FA')
    ax.set_xlim(0, 10); ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title("Code Analysis Workflow Pipeline", color=TXT, fontsize=13,
                 fontweight='bold', pad=12)

    steps = [
        ("1. Source\nSubmission", "ZIP upload\nor Git URL", ACC),
        ("2. Input\nValidation", "Size, ratio,\nSSRF checks", AMB),
        ("3. Extraction\n/ Clone", "Temp dir,\n.git/ removed", GRN),
        ("4. Job\nCreation", "HTTP 202,\n'queued'", PUR),
        ("5. Semgrep\nAnalysis", "subprocess,\nshell=False", R),
        ("6. Metric\nComputation", "Debt, dup%,\nrisk score", CYN),
        ("7. CVSS\nScoring", "v3.1 formula,\nFIRST spec", AMB),
        ("8. Result\nPersistence", "Findings →\nPostgreSQL", GRN),
    ]

    bw, bh = 1.0, 0.95
    gap = 0.25
    total_w = len(steps) * (bw + gap) - gap
    start_x = (10 - total_w) / 2

    for i, (title, subtitle, color) in enumerate(steps):
        x = start_x + i * (bw + gap)
        y = 3.0
        rect = FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.05",
                               facecolor=SURF, edgecolor=color, linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + bw/2, y + bh * 0.65, title, ha='center', va='center',
                color=color, fontsize=8, fontweight='bold', zorder=4)
        ax.text(x + bw/2, y + bh * 0.25, subtitle, ha='center', va='center',
                color=MUT, fontsize=7, zorder=4)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + bw + gap, y + bh/2), xytext=(x + bw, y + bh/2),
                        arrowprops=dict(arrowstyle="->", color=TXT, lw=1.5))

    ax.text(5.0, 2.5, "Both ZIP (archive.py) and Git URL (git_service.py) paths converge at Step 4",
            ha='center', color=MUT, fontsize=8)
    ax.text(5.0, 2.2, "Steps 5–8 execute in an async background task (FastAPI BackgroundTasks)",
            ha='center', color=MUT, fontsize=8)

    ai_steps = [
        ("AI\nExplanation", PUR),
        ("Suggested\nFix", CYN),
        ("Learning\nRec.", ORG),
        ("Tutor\nSession", AMB),
    ]
    ax.text(5.0, 1.7, "Post-analysis AI features (on-demand, triggered by developer action):",
            ha='center', color=MUT, fontsize=8)
    ax_x = 1.2
    ax_y = 1.0
    for j, (title, color) in enumerate(ai_steps):
        x = ax_x + j * 2.2
        rect2 = FancyBboxPatch((x, ax_y), 1.6, 0.6, boxstyle="round,pad=0.05",
                                facecolor=SURF, edgecolor=color, linewidth=1.5, zorder=3)
        ax.add_patch(rect2)
        ax.text(x + 0.8, ax_y + 0.3, title, ha='center', va='center',
                color=color, fontsize=8, fontweight='bold', zorder=4)

    ax.text(5.0, 0.3, "Source: FastAPI route handlers and job_runner.py — verified 2026-11-02",
            ha='center', color=MUT, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "diag03_workflow.png"), dpi=150, bbox_inches='tight', facecolor=BG2)
    plt.close()
    print("  diag03_workflow.png  [white bg]")


if __name__ == "__main__":
    print("Regenerating all charts and diagrams with white backgrounds...")
    chart_module_distribution()
    chart_test_results()
    chart_feature_status()
    chart_severity_distribution()
    chart_competitor_matrix()
    chart_tech_stack()
    chart_sdg()
    diagram_system_arch()
    diagram_er()
    diagram_workflow()
    print(f"\nAll 10 assets saved to {OUT}")
