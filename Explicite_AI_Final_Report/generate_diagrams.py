"""
Generate architecture diagrams as PNG for the Final Report.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "Report_Assets"
OUT.mkdir(exist_ok=True)

DARK_BG = "#0D1117"
SURFACE = "#11151D"
ACCENT  = "#4F8EF7"
GREEN   = "#3FB950"
AMBER   = "#D29922"
RED     = "#F85149"
PURPLE  = "#BC8CFF"
CYAN    = "#39D2C0"
TEXT    = "#E6EDF3"
MUTED   = "#8B949E"
GRID    = "#21262D"
BORDER  = "#30363D"


def box(ax, x, y, w, h, text, color, text_color=TEXT, fontsize=9.5, bold=False):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           facecolor=color, edgecolor=BORDER, linewidth=1.2, zorder=3)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            color=text_color, fontsize=fontsize,
            fontweight='bold' if bold else 'normal',
            wrap=True, zorder=4, multialignment='center')


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=1.5, style='->'):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle="arc3,rad=0"))


# ── Diagram 1: System Architecture ──────────────────────────────────────────
def diagram_system_arch():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title("Explicite AI — System Architecture", color=TEXT, fontsize=13,
                 fontweight='bold', pad=12)

    # Layer labels
    for y, label in [(5.6, "FRONTEND LAYER"), (3.6, "BACKEND LAYER"), (1.3, "DATA / INTEGRATION LAYER")]:
        ax.text(0.15, y, label, color=MUTED, fontsize=8, fontweight='bold')
        ax.axhline(y - 0.05, color=GRID, linestyle='--', alpha=0.4, xmin=0.01, xmax=0.99)

    # Frontend screens
    screens = ["Login", "Dashboard", "Findings", "AI Assistant", "Learning", "Settings"]
    for i, s in enumerate(screens):
        x = 0.3 + i * 1.9
        box(ax, x, 5.7, 1.6, 0.55, s, SURFACE, fontsize=8)
    box(ax, 0.1, 5.25, 11.8, 0.6, "React 19 + TypeScript + Vite 8  (Single Page Application, port 8443)",
        "#1B2330", ACCENT, fontsize=9, bold=True)

    # API
    box(ax, 0.3, 3.7, 3.8, 0.7, "FastAPI\n(Python 3.14.3, /api/v1)", "#1B2330", ACCENT, fontsize=9, bold=True)
    box(ax, 4.3, 3.7, 3.4, 0.7, "Auth + RBAC\n(JWT HS256, bcrypt)", SURFACE, AMBER, fontsize=9)
    box(ax, 7.9, 3.7, 3.8, 0.7, "Background Jobs\n(FastAPI BackgroundTasks)", SURFACE, GREEN, fontsize=9)

    # Services row
    services = [
        ("Analysis\nEngine\n(Semgrep 1.181)", SURFACE, RED, 0.2),
        ("CVSS 3.1\nScoring", SURFACE, AMBER, 2.1),
        ("AI Service\n(Ollama/Anthropic)", SURFACE, PURPLE, 4.0),
        ("Git Service\n(SSRF Guard)", SURFACE, GREEN, 5.9),
        ("Archive\nService", SURFACE, CYAN, 7.8),
        ("Fix Service\n(SHA-256 check)", SURFACE, ACCENT, 9.7),
    ]
    for text, bg, tc, x in services:
        box(ax, x + 0.1, 2.4, 1.7, 0.85, text, bg, tc, fontsize=8)

    # Data layer
    box(ax, 0.2, 0.6, 3.2, 0.75, "PostgreSQL 16\n(port 5434, 9 migrations)", "#1A2B1A", GREEN, fontsize=9, bold=True)
    box(ax, 3.7, 0.6, 3.5, 0.75, "Ollama\n(llama3, localhost:11434)", "#1B1525", PURPLE, fontsize=9, bold=True)
    box(ax, 7.5, 0.6, 2.3, 0.75, "Anthropic API\n(claude-haiku-4-5)", "#1B1525", AMBER, fontsize=9, bold=True)
    box(ax, 10.1, 0.6, 1.7, 0.75, "File System\n(uploads/, tmp/)", SURFACE, MUTED, fontsize=8)

    # Arrows: frontend → API
    arrow(ax, 6.0, 5.25, 6.0, 4.4, ACCENT, lw=1.8)
    # API → services
    for x in [1.05, 2.95, 4.75, 6.65, 8.55, 10.4]:
        arrow(ax, x, 3.7, x, 3.25, GRID, lw=1.2)
    # Services → data
    for (sx, dy) in [(1.05, 1.35), (5.05, 1.35), (6.95, 1.35)]:
        arrow(ax, sx, 2.4, sx, 1.35, GRID, lw=1.0)

    ax.text(6.0, 0.15, "Source: Explicite AI implementation — verified 2026-11-02",
            ha='center', color=MUTED, fontsize=8)

    fig.tight_layout()
    fig.savefig(str(OUT / "diag01_system_arch.png"), dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print("  diag01_system_arch.png")


# ── Diagram 2: ER Diagram ────────────────────────────────────────────────────
def diagram_er():
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Explicite AI — Database Entity-Relationship Overview", color=TEXT, fontsize=13,
                 fontweight='bold', pad=12)

    entities = {
        "users": (0.3, 5.5, 2.2, 2.0, [
            "PK id (UUID)", "email (unique)", "password_hash", "full_name",
            "system_role", "experience_level", "preferences (JSONB)"
        ], ACCENT),
        "projects": (3.2, 5.5, 2.2, 1.6, [
            "PK id (UUID)", "name", "description",
            "owner_id (FK→users)", "created_at"
        ], GREEN),
        "project_memberships": (6.1, 5.9, 2.3, 1.2, [
            "project_id (FK)", "user_id (FK)",
            "role (viewer/developer/owner)"
        ], AMBER),
        "analysis_jobs": (3.2, 2.8, 2.4, 2.3, [
            "PK id (UUID)", "project_id (FK)",
            "status (queued→completed)", "engine_name/version",
            "bugs/vulns/smells count", "technical_debt_minutes",
            "repo_url, source_path"
        ], PURPLE),
        "findings": (0.3, 0.6, 2.4, 2.3, [
            "PK id (UUID)", "analysis_job_id (FK)",
            "engine_severity, risk_level", "issue_type, title",
            "cvss_score, cvss_vector", "status (Open/In Review/Resolved)",
            "ai_explanation (Text)"
        ], RED),
        "suggested_fixes": (6.1, 0.6, 2.3, 2.0, [
            "PK id (UUID)", "finding_id (FK)",
            "proposed_lines (JSONB)", "rationale, caveats",
            "original_hash (SHA-256)", "status (pending/approved/rejected)"
        ], CYAN),
        "learning_resources": (9.2, 5.3, 2.5, 1.7, [
            "PK id (UUID)", "title, url",
            "resource_type", "tags (JSONB)",
            "cwe_ids, rule_keys"
        ], "#F0883E"),
        "tutor_sessions": (9.2, 2.7, 2.5, 1.5, [
            "PK id (UUID)", "user_id (FK)",
            "resource_id (FK)", "created_at"
        ], MUTED),
        "tutor_messages": (9.2, 0.6, 2.5, 1.5, [
            "PK id (UUID)", "session_id (FK)",
            "role (user/assistant)", "content (Text)"
        ], "#8B949E"),
    }

    for name, (x, y, w, h, fields, color) in entities.items():
        # Header
        hdr = FancyBboxPatch((x, y + h - 0.38), w, 0.38, boxstyle="round,pad=0.03",
                              facecolor=color, edgecolor=BORDER, linewidth=1.2, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.19, name, ha='center', va='center',
                color=DARK_BG, fontsize=9, fontweight='bold', zorder=4)
        # Body
        body = FancyBboxPatch((x, y), w, h - 0.38, boxstyle="round,pad=0.03",
                               facecolor=SURFACE, edgecolor=BORDER, linewidth=1.2, zorder=2)
        ax.add_patch(body)
        for fi, field in enumerate(fields):
            ax.text(x + 0.1, y + h - 0.5 - fi * 0.26, field,
                    va='top', color=TEXT if not field.startswith("PK") else GREEN,
                    fontsize=7, zorder=4)

    # Relationships
    rels = [
        # users → projects (owner)
        (1.4, 5.5, 4.3, 7.1),
        # users → project_memberships
        (2.5, 6.5, 6.1, 6.5),
        # projects → project_memberships
        (5.4, 6.8, 6.1, 6.5),
        # projects → analysis_jobs
        (4.3, 5.5, 4.3, 5.1),
        # analysis_jobs → findings
        (3.2, 3.9, 2.7, 2.9),
        # findings → suggested_fixes
        (2.7, 1.7, 6.1, 1.7),
        # users → tutor_sessions
        (2.5, 5.5, 10.4, 4.2),
        # learning_resources → tutor_sessions
        (10.4, 5.3, 10.4, 4.2),
        # tutor_sessions → tutor_messages
        (10.4, 2.7, 10.4, 2.1),
    ]
    for x1, y1, x2, y2 in rels:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0,
                                   connectionstyle="arc3,rad=0"))

    ax.text(6.0, 0.12, "Source: SQLAlchemy model files — verified 2026-11-02",
            ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "diag02_er_diagram.png"), dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print("  diag02_er_diagram.png")


# ── Diagram 3: Analysis Workflow ─────────────────────────────────────────────
def diagram_workflow():
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title("Code Analysis Workflow Pipeline", color=TEXT, fontsize=13,
                 fontweight='bold', pad=12)

    steps = [
        ("1. Source\nSubmission", "ZIP upload\nor Git URL", ACCENT),
        ("2. Input\nValidation", "Size, ratio,\nSSRF checks", AMBER),
        ("3. Extraction\n/ Clone", "Temp dir,\n.git/ removed", GREEN),
        ("4. Job\nCreation", "HTTP 202,\n'queued'", PURPLE),
        ("5. Semgrep\nAnalysis", "subprocess,\nshell=False", RED),
        ("6. Metric\nComputation", "Debt, dup%,\nrisk score", CYAN),
        ("7. CVSS\nScoring", "v3.1 formula,\nFIRST spec", AMBER),
        ("8. Result\nPersistence", "Findings →\nPostgreSQL", GREEN),
    ]

    bw, bh = 1.0, 0.95
    gap = 0.25
    total_w = len(steps) * (bw + gap) - gap
    start_x = (10 - total_w) / 2

    for i, (title, subtitle, color) in enumerate(steps):
        x = start_x + i * (bw + gap)
        y = 3.0
        rect = FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.05",
                               facecolor=SURFACE, edgecolor=color, linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + bw/2, y + bh * 0.65, title, ha='center', va='center',
                color=color, fontsize=8, fontweight='bold', zorder=4)
        ax.text(x + bw/2, y + bh * 0.25, subtitle, ha='center', va='center',
                color=MUTED, fontsize=7, zorder=4)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + bw + gap, y + bh/2), xytext=(x + bw, y + bh/2),
                        arrowprops=dict(arrowstyle="->", color=TEXT, lw=1.5))

    # Branching explanation below
    ax.text(5.0, 2.5, "Both ZIP (archive.py) and Git URL (git_service.py) paths converge at Step 4",
            ha='center', color=MUTED, fontsize=8)
    ax.text(5.0, 2.2, "Steps 5–8 execute in an async background task (FastAPI BackgroundTasks)",
            ha='center', color=MUTED, fontsize=8)

    # Post-analysis AI steps
    ai_steps = [
        ("AI\nExplanation", PURPLE),
        ("Suggested\nFix", CYAN),
        ("Learning\nRec.", "#F0883E"),
        ("Tutor\nSession", AMBER),
    ]
    ax_x = 1.2
    ax_y = 1.0
    ax.text(5.0, 1.7, "Post-analysis AI features (on-demand, triggered by developer action):",
            ha='center', color=MUTED, fontsize=8)
    for j, (title, color) in enumerate(ai_steps):
        x = ax_x + j * 2.2
        rect2 = FancyBboxPatch((x, ax_y), 1.6, 0.6, boxstyle="round,pad=0.05",
                                facecolor=SURFACE, edgecolor=color, linewidth=1.5, zorder=3)
        ax.add_patch(rect2)
        ax.text(x + 0.8, ax_y + 0.3, title, ha='center', va='center',
                color=color, fontsize=8, fontweight='bold', zorder=4)

    ax.text(5.0, 0.3, "Source: FastAPI route handlers and job_runner.py — verified 2026-11-02",
            ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "diag03_workflow.png"), dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print("  diag03_workflow.png")


if __name__ == "__main__":
    print("Generating diagrams...")
    diagram_system_arch()
    diagram_er()
    diagram_workflow()
    print(f"All diagrams saved to {OUT}")
