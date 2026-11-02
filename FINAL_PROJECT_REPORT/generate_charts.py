"""Generate chart PNGs for the Explicite AI project report."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "Report_Assets"
OUT.mkdir(exist_ok=True)

NAVY  = "#1A237E"
BLUE  = "#1565C0"
LBLUE = "#42A5F5"
GREY  = "#546E7A"
LGREY = "#B0BEC5"
GREEN = "#2E7D32"
AMBER = "#F57F17"
RED   = "#C62828"
WHITE = "#FFFFFF"

def fig_save(name, dpi=150):
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved {name}")

# ── Fig 1: Module Distribution ─────────────────────────────────────────────
def chart_modules():
    labels = ['API Routes\n(10)', 'Services\n(14)', 'DB Models\n(7)',
              'Schemas\n(8)', 'Frontend\nScreens (11)', 'Test Files\n(18)',
              'Migrations\n(9)', 'Components\n(3)']
    values = [10, 14, 7, 8, 11, 18, 9, 3]
    colors = [NAVY, BLUE, LBLUE, GREY, GREEN, AMBER, RED, LGREY]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor='white')
    ax.bar_label(bars, padding=4, fontsize=11, color='#333')
    ax.set_xlabel('Count', fontsize=11)
    ax.set_title('Figure 1: Distribution of Implemented Project Modules', fontsize=13, pad=12)
    ax.set_xlim(0, 24)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig_save("fig01_module_distribution.png")

# ── Fig 2: Test Results ────────────────────────────────────────────────────
def chart_tests():
    cats = ['Passed', 'Skipped', 'Failed / Error']
    vals = [426, 1, 0]
    colors = [GREEN, AMBER, RED]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(cats, vals, color=colors, width=0.5, edgecolor='white')
    ax.bar_label(bars, padding=3, fontsize=14, fontweight='bold')
    ax.set_ylabel('Test Count', fontsize=11)
    ax.set_title('Figure 2: Backend Test Suite Results\n(pytest, non-slow suite, Phase O verification)', fontsize=12, pad=10)
    ax.set_ylim(0, 480)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig_save("fig02_test_results.png")

# ── Fig 3: Feature Implementation Status ──────────────────────────────────
def chart_features():
    categories = ['Implemented\n& Verified', 'Implemented\n(partial / limited)', 'Planned\nEnhancement']
    counts = [20, 3, 7]
    colors = [GREEN, AMBER, LGREY]
    fig, ax = plt.subplots(figsize=(7, 4))
    wedges, texts, autotexts = ax.pie(
        counts, labels=categories, autopct='%1.0f%%',
        colors=colors, startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for t in autotexts:
        t.set_fontsize(13)
        t.set_fontweight('bold')
    ax.set_title('Figure 3: Feature Implementation Status', fontsize=13, pad=12)
    fig_save("fig03_feature_status.png")

# ── Fig 4: Competitor Feature Matrix ──────────────────────────────────────
def chart_competitors():
    features = ['Static Analysis', 'Vuln Detection', 'AI Explanations',
                'Risk Scoring', 'Suggested Fixes', 'Dev Learning', 'CI/CD Integration']
    tools = ['SonarQube', 'Snyk Code', 'Semgrep', 'CodeQL', 'Explicite AI']
    # 1=full, 0.5=partial, 0=no
    data = np.array([
        [1,   1,   0.5, 1,   0,   0,   1  ],  # SonarQube
        [1,   1,   1,   1,   1,   0,   1  ],  # Snyk Code
        [1,   1,   0,   0.5, 0,   0,   1  ],  # Semgrep
        [1,   1,   0,   0.5, 0,   0,   1  ],  # CodeQL
        [1,   1,   1,   1,   1,   1,   0  ],  # Explicite AI
    ])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    im = ax.imshow(data, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(features, rotation=25, ha='right', fontsize=10)
    ax.set_yticks(range(len(tools)))
    ax.set_yticklabels(tools, fontsize=11)
    for i in range(len(tools)):
        for j in range(len(features)):
            v = data[i, j]
            label = '✓' if v == 1 else ('~' if v == 0.5 else '✗')
            ax.text(j, i, label, ha='center', va='center', fontsize=14,
                    color='white' if v == 0 else 'black', fontweight='bold')
    ax.set_title('Figure 4: Competitor Feature Comparison Matrix\n(✓ Full   ~ Partial   ✗ Not Available)', fontsize=12, pad=10)
    plt.colorbar(im, ax=ax, label='Support Level', fraction=0.025)
    fig_save("fig04_competitor_matrix.png")

# ── Fig 5: SDG Contribution ────────────────────────────────────────────────
def chart_sdg():
    sdgs = ['SDG 4\nQuality\nEducation', 'SDG 9\nIndustry &\nInnovation', 'SDG 16\nPeace &\nInstitutions']
    feature_counts = [5, 6, 3]
    colors = [BLUE, GREEN, NAVY]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(sdgs, feature_counts, color=colors, width=0.5, edgecolor='white')
    ax.bar_label(bars, labels=[f'{v} features' for v in feature_counts],
                 padding=4, fontsize=11)
    ax.set_ylabel('Number of Related Features', fontsize=11)
    ax.set_title('Figure 5: Explicite AI SDG Contribution Mapping', fontsize=13, pad=12)
    ax.set_ylim(0, 9)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig_save("fig05_sdg_mapping.png")

# ── Fig 6: Analysis Workflow ───────────────────────────────────────────────
def chart_workflow():
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis('off')
    steps = [
        (0.6,  'Upload\nSource', BLUE),
        (2.1,  'Validate\nArchive', BLUE),
        (3.6,  'Extract\nFiles', LBLUE),
        (5.1,  'Semgrep\nAnalysis', NAVY),
        (6.6,  'Risk\nScoring', AMBER),
        (8.1,  'AI\nExplanation', GREEN),
        (9.6,  'Suggested\nFix', RED),
    ]
    for i, (x, label, color) in enumerate(steps):
        circle = plt.Circle((x, 1.5), 0.42, color=color, zorder=3)
        ax.add_patch(circle)
        ax.text(x, 1.5, str(i+1), ha='center', va='center',
                color='white', fontsize=13, fontweight='bold', zorder=4)
        ax.text(x, 0.7, label, ha='center', va='top', fontsize=9.5,
                color='#333', multialignment='center')
        if i < len(steps) - 1:
            ax.annotate('', xy=(x+0.68, 1.5), xytext=(x+0.42, 1.5),
                        arrowprops=dict(arrowstyle='->', color=GREY, lw=2))
    ax.set_title('Figure 6: Explicite AI Code Analysis Workflow', fontsize=13, pad=8)
    fig_save("fig06_analysis_workflow.png")

# ── Fig 7: Technology Distribution ────────────────────────────────────────
def chart_tech():
    categories = ['Frontend\n(React+TS+Tailwind)', 'Backend\n(Python+FastAPI)',
                  'Database\n(PostgreSQL+Alembic)', 'Analysis\n(Semgrep+CVSS)',
                  'AI Layer\n(Ollama+Anthropic)', 'Testing\n(pytest+httpx)']
    scores = [9, 10, 8, 9, 8, 9]
    colors = [LBLUE, NAVY, BLUE, AMBER, GREEN, GREY]
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    scores_r = scores + scores[:1]
    angles_r = angles + angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles_r, scores_r, color=BLUE, alpha=0.25)
    ax.plot(angles_r, scores_r, color=NAVY, linewidth=2)
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=8)
    ax.set_title('Figure 7: Technology Stack Maturity / Integration Depth', fontsize=12, pad=20)
    fig_save("fig07_tech_distribution.png")

if __name__ == '__main__':
    print("Generating report charts...")
    chart_modules()
    chart_tests()
    chart_features()
    chart_competitors()
    chart_sdg()
    chart_workflow()
    chart_tech()
    print(f"Done. All charts saved to {OUT}")
