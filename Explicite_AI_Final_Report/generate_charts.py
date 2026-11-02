"""
Generate verified charts for the Explicite AI Final Report.
All data derived from actual project inspection (2026-11-02).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "Report_Assets"
OUT.mkdir(exist_ok=True)

DARK_BG   = "#0D1117"
ACCENT    = "#4F8EF7"
GREEN     = "#3FB950"
AMBER     = "#D29922"
RED       = "#F85149"
PURPLE    = "#BC8CFF"
CYAN      = "#39D2C0"
TEXT      = "#E6EDF3"
GRID      = "#21262D"
MUTED     = "#8B949E"

def _style(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


# ── Chart 1: Module Distribution ────────────────────────────────────────────
def chart_module_distribution():
    categories = [
        "Test Files", "Services", "Frontend Screens",
        "API Routes", "DB Models", "Alembic Migrations",
        "Schemas", "Frontend Components"
    ]
    # Verified counts from actual project inspection
    counts = [20, 13, 11, 8, 6, 9, 7, 3]
    colors = [ACCENT, GREEN, PURPLE, AMBER, CYAN, RED, "#F0883E", MUTED]

    fig, ax = plt.subplots(figsize=(9, 5))
    _style(fig, ax)
    bars = ax.barh(categories, counts, color=colors, height=0.6, edgecolor="none")
    for bar, val in zip(bars, counts):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', color=TEXT, fontsize=10, fontweight='bold')
    ax.set_xlabel("Count", color=TEXT, fontsize=10)
    ax.set_title("Project Module Distribution (Verified from Codebase)", color=TEXT,
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(0, 26)
    ax.grid(axis='x', color=GRID, linestyle='--', alpha=0.5)
    ax.invert_yaxis()
    ax.text(0, -0.9, "Source: Direct codebase inspection, 2026-11-02",
            transform=ax.get_xaxis_transform(), color=MUTED, fontsize=8, ha='left')
    fig.tight_layout()
    fig.savefig(str(OUT / "chart01_module_distribution.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart01_module_distribution.png")


# ── Chart 2: Test Results ────────────────────────────────────────────────────
def chart_test_results():
    labels = ['Passed (426)', 'Skipped (1)']
    sizes = [426, 1]
    colors = [GREEN, AMBER]
    explode = (0.03, 0.08)

    fig, ax = plt.subplots(figsize=(7, 5))
    _style(fig, ax)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=90,
        textprops={'color': TEXT, 'fontsize': 11},
        wedgeprops={'edgecolor': DARK_BG, 'linewidth': 2}
    )
    for at in autotexts:
        at.set_color(DARK_BG)
        at.set_fontweight('bold')
    ax.set_title("Backend Test Suite Results\n427 Tests Collected (0 Failures)",
                 color=TEXT, fontsize=12, fontweight='bold', pad=14)
    ax.text(0, -1.35, "Source: pytest run, 2026-11-02 (venv/Scripts/python -m pytest tests/)",
            ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "chart02_test_results.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart02_test_results.png")


# ── Chart 3: Feature Implementation Status ──────────────────────────────────
def chart_feature_status():
    # Verified feature checklist from code inspection
    labels = ['Fully Implemented\n(21)', 'Partially Implemented\n(4)', 'Planned\n(5)']
    sizes = [21, 4, 5]
    colors = [GREEN, AMBER, RED]
    explode = (0.03, 0.06, 0.06)

    fig, ax = plt.subplots(figsize=(7, 5))
    _style(fig, ax)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=140,
        textprops={'color': TEXT, 'fontsize': 10},
        wedgeprops={'edgecolor': DARK_BG, 'linewidth': 2}
    )
    for at in autotexts:
        at.set_color(DARK_BG)
        at.set_fontweight('bold')
    ax.set_title("Feature Implementation Status\n30 Features Assessed",
                 color=TEXT, fontsize=12, fontweight='bold', pad=14)
    ax.text(0, -1.38, "Partial: missing language support warning, CVSS 4.0 scoring,\n"
            "formal accessibility audit, SSRF network-level isolation",
            ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "chart03_feature_status.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart03_feature_status.png")


# ── Chart 4: Vulnerability Severity Distribution ─────────────────────────────
def chart_severity_distribution():
    # Actual findings from Student Management System project (verified via API)
    severities = ['High', 'Medium', 'Low', 'Critical']
    counts = [3, 2, 1, 0]
    colors = [AMBER, CYAN, GREEN, RED]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    _style(fig, ax)
    bars = ax.bar(severities, counts, color=colors, width=0.5, edgecolor="none")
    for bar, val in zip(bars, counts):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.05,
                    str(val), ha='center', va='bottom', color=TEXT, fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Findings", color=TEXT, fontsize=10)
    ax.set_xlabel("Severity Level", color=TEXT, fontsize=10)
    ax.set_title("Vulnerability Severity Distribution\n(Student Management System — 6 Findings)",
                 color=TEXT, fontsize=12, fontweight='bold', pad=12)
    ax.set_ylim(0, 4.5)
    ax.grid(axis='y', color=GRID, linestyle='--', alpha=0.5)
    ax.text(0.5, -0.18, "Source: Live application data — POST /api/v1/projects/{id}/issues, 2026-11-02",
            transform=ax.transAxes, ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "chart04_severity_distribution.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart04_severity_distribution.png")


# ── Chart 5: Competitor Feature Comparison ──────────────────────────────────
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
    # 2=Full, 1=Partial, 0=None
    # Based on official documentation verified 2025-2026
    data = np.array([
        [2, 2, 2, 2, 2],  # Static Analysis
        [2, 2, 2, 2, 2],  # Vulnerability Detection
        [2, 2, 1, 1, 0],  # CVSS Scoring
        [2, 0, 1, 0, 0],  # AI Explanations
        [2, 0, 2, 0, 0],  # Fix Suggestions
        [2, 0, 0, 0, 0],  # Learning Pathway
        [0, 2, 2, 2, 2],  # CI/CD Integration
    ])

    cmap = matplotlib.colors.ListedColormap([RED, AMBER, GREEN])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    _style(fig, ax)
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=2, aspect='auto')

    ax.set_xticks(range(len(tools)))
    ax.set_xticklabels(tools, color=TEXT, fontsize=10, fontweight='bold')
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features, color=TEXT, fontsize=10)

    labels_map = {0: '✗', 1: '~', 2: '✓'}
    for i in range(len(features)):
        for j in range(len(tools)):
            ax.text(j, i, labels_map[data[i, j]], ha='center', va='center',
                    color='white', fontsize=14, fontweight='bold')

    ax.set_title("Competitor Feature Comparison Matrix",
                 color=TEXT, fontsize=12, fontweight='bold', pad=14)

    legend_patches = [
        mpatches.Patch(color=GREEN, label='✓ Full support'),
        mpatches.Patch(color=AMBER, label='~ Partial / paid tier'),
        mpatches.Patch(color=RED, label='✗ Not supported'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', facecolor=DARK_BG,
              labelcolor=TEXT, fontsize=9, framealpha=0.8)
    ax.text(0.5, -0.12, "Source: Official product documentation, 2025–2026",
            transform=ax.transAxes, ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "chart05_competitor_matrix.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart05_competitor_matrix.png")


# ── Chart 6: Technology Stack ────────────────────────────────────────────────
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
    # Actual file/component counts per layer (verified)
    counts = [13, 9, 14, 2, 3, 20, 6]
    colors = [ACCENT, GREEN, PURPLE, RED, AMBER, CYAN, "#F0883E"]

    fig, ax = plt.subplots(figsize=(9.5, 5))
    _style(fig, ax)
    bars = ax.barh(categories, counts, color=colors, height=0.6, edgecolor='none')
    for bar, val in zip(bars, counts):
        ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', color=TEXT, fontsize=10, fontweight='bold')
    ax.set_xlabel("Number of Files / Components", color=TEXT, fontsize=10)
    ax.set_title("Technology Stack — Files per Layer (Verified from Repository)",
                 color=TEXT, fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(0, 26)
    ax.grid(axis='x', color=GRID, linestyle='--', alpha=0.5)
    ax.invert_yaxis()
    ax.text(0, -0.9, "Source: Direct repository file count, 2026-11-02",
            transform=ax.get_xaxis_transform(), color=MUTED, fontsize=8, ha='left')
    fig.tight_layout()
    fig.savefig(str(OUT / "chart06_tech_stack.png"), dpi=150, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close()
    print("  chart06_tech_stack.png")


# ── Chart 7: SDG Contribution ───────────────────────────────────────────────
def chart_sdg():
    sdgs = ['SDG 4\nQuality Education', 'SDG 9\nIndustry & Innovation', 'SDG 16\nPeace & Institutions']
    feature_counts = [5, 6, 3]
    colors = [PURPLE, ACCENT, GREEN]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    _style(fig, ax)
    bars = ax.bar(sdgs, feature_counts, color=colors, width=0.45, edgecolor='none')
    for bar, val in zip(bars, feature_counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.08,
                str(val), ha='center', va='bottom', color=TEXT, fontsize=12, fontweight='bold')

    ax.set_ylabel("Number of Features Contributing", color=TEXT, fontsize=10)
    ax.set_title("SDG Contribution — Implemented Feature Count per SDG",
                 color=TEXT, fontsize=12, fontweight='bold', pad=12)
    ax.set_ylim(0, 8)
    ax.grid(axis='y', color=GRID, linestyle='--', alpha=0.5)
    ax.text(0.5, -0.2,
            "Note: Represents potential contribution based on implemented features,\n"
            "not measured social impact. Source: Feature-SDG mapping, 2026.",
            transform=ax.transAxes, ha='center', color=MUTED, fontsize=8)
    fig.tight_layout()
    fig.savefig(str(OUT / "chart07_sdg.png"), dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print("  chart07_sdg.png")


if __name__ == "__main__":
    print("Generating charts...")
    chart_module_distribution()
    chart_test_results()
    chart_feature_status()
    chart_severity_distribution()
    chart_competitor_matrix()
    chart_tech_stack()
    chart_sdg()
    print(f"All 7 charts saved to {OUT}")
