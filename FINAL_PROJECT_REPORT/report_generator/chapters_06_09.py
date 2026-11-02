"""Chapters 6–9: Technology Stack, Functional Features, UI/Usability, SDGs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from styles import *
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_chapters_06_09(doc):
    _ch6_stack(doc)
    page_break(doc)
    _ch7_features(doc)
    page_break(doc)
    _ch8_ui(doc)
    page_break(doc)
    _ch9_sdg(doc)


# ── Chapter 6 ─────────────────────────────────────────────────────────────
def _ch6_stack(doc):
    heading(doc, 'CHAPTER 6: Technology Stack', level=1)

    heading(doc, '6.1 Overview', level=2)
    para(doc, 'Explicite AI employs a deliberately curated technology stack selected for '
         'developer productivity, async performance, and ecosystem maturity. Each technology '
         'choice reflects specific requirements of the platform: long-running analysis jobs '
         'demanded an async backend; real-time job status polling required a reactive frontend; '
         'security analysis required a programmable, subprocess-safe analysis engine.')

    heading(doc, '6.2 Frontend Technologies', level=2)
    fe = [
        ('React 19', 'Component-based UI framework. Selected for its hooks-based state management, concurrent rendering capabilities, and wide developer adoption. The application uses React 19\'s latest stable API including React Context for global navigation state (NavCtx).'),
        ('TypeScript', 'Statically typed superset of JavaScript. Provides compile-time type checking across all frontend components, API response types, and navigation state. Eliminates a class of runtime type errors in API communication.'),
        ('Vite 8', 'Build tool and development server. Provides hot module replacement (HMR) for rapid development feedback and produces optimised production bundles. Frontend development server runs on port 8443.'),
        ('Tailwind CSS v4', 'Utility-first CSS framework. Combined with --xm-* CSS custom properties to implement the Explicite Midnight design system. Theme switching uses the data-theme HTML attribute to override the full CSS variable set.'),
        ('Inter + JetBrains Mono', 'Typography: Inter (Google Fonts) for UI text; JetBrains Mono for code display, terminal output, and technical values throughout the interface.'),
    ]
    for tech, desc in fe:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(tech + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '6.3 Backend Technologies', level=2)
    be = [
        ('Python 3.14', 'Primary backend language. Selected for its extensive library ecosystem (FastAPI, SQLAlchemy, Pydantic, Semgrep) and native async/await support enabling non-blocking I/O throughout the API layer.'),
        ('FastAPI', 'Async web framework built on Starlette and Pydantic. Provides automatic OpenAPI documentation, native async route handlers, dependency injection, and tight integration with Pydantic for request validation. All API routes use async def.'),
        ('Pydantic v2', 'Data validation library. Defines all request and response schemas, enforcing type validation at system boundaries. Used for settings management (pydantic-settings) and Alembic configuration.'),
        ('SQLAlchemy 2.x (async)', 'ORM with full async support via AsyncSession and asyncpg. All database operations are non-blocking. Declarative models define the schema; queries use the 2.x Select API.'),
        ('asyncpg', 'High-performance async PostgreSQL driver. Used as the DBAPI backend for SQLAlchemy async sessions.'),
        ('Alembic', 'Database migration framework. Manages the nine-migration chain from initial schema to current head (c1d2e3f4a5b6). Migrations are authored as Python scripts with async support.'),
    ]
    for tech, desc in be:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(tech + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '6.4 Database', level=2)
    para(doc, 'PostgreSQL 16 is deployed via Docker, listening on host port 5434. PostgreSQL '
         'was selected for its robustness, JSONB support, and excellent compatibility with '
         'SQLAlchemy async. A separate test database (test_explicite_ai) is used for the '
         'automated test suite, ensuring that tests never touch production data. The Alembic '
         'migration chain provides reproducible schema management and tracks all structural '
         'changes to the database.')

    heading(doc, '6.5 Security Analysis Engine', level=2)
    para(doc, 'Semgrep 1.181.0 is the static analysis engine. It supports Python, Java, '
         'JavaScript, and TypeScript rule sets from the Semgrep Registry (r/ prefix). Semgrep '
         'is invoked as a subprocess within the backend virtual environment with a fixed '
         'argument list (shell=False). The source directory path is passed as an argument, '
         'not interpolated into a shell string, preventing injection. Semgrep outputs JSON '
         'which is parsed by the analysis_engine.py adapter into structured Finding records. '
         'CVSS vector strings extracted from Semgrep rule metadata are scored using a '
         'standards-compliant CVSS 3.1 implementation in cvss_scoring.py.')

    heading(doc, '6.6 Artificial Intelligence Layer', level=2)
    para(doc, 'The AI service supports two active providers and one null provider:')
    ai_items = [
        ('Ollama (llama3:latest)', 'Locally hosted inference server at localhost:11434. llama3:latest (8B Q4_0 quantised) is the default active model. No API key required. LLM_MAX_TOKENS=512 for explanations and chat; LLM_FIX_MAX_TOKENS=2048 for fix generation. Timeout: LLM_TIMEOUT_SECONDS=30.'),
        ('Anthropic API', 'Optional cloud provider using claude-haiku-4-5. Requires ANTHROPIC_API_KEY. Switchable via LLM_PROVIDER=anthropic without any code changes.'),
        ('None Provider (default)', 'When LLM_PROVIDER=none (the default in .env.example), all AI endpoints return HTTP 503 with an honest "AI provider not configured" message. No silent fallback or fabricated response is returned.'),
    ]
    for item, desc in ai_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(item + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '6.7 Technology Stack Summary', level=2)
    add_table(doc,
        headers=['Layer', 'Technology', 'Version', 'Purpose'],
        rows=[
            ['Frontend',   'React + TypeScript',  '19 / 5.x', 'Component UI, state management'],
            ['Frontend',   'Vite',                '8',        'Build tool, dev server (8443)'],
            ['Frontend',   'Tailwind CSS',        'v4',       'Utility styling + design system'],
            ['Backend',    'Python',              '3.14',     'Primary backend language'],
            ['Backend',    'FastAPI',             'Latest',   'Async REST API framework'],
            ['Backend',    'Pydantic',            'v2',       'Validation, settings, schemas'],
            ['Database',   'PostgreSQL',          '16',       'Relational data store (5434)'],
            ['Database',   'SQLAlchemy async',    '2.x',      'ORM for async DB access'],
            ['Database',   'Alembic',             'Latest',   'Schema migrations (9 total)'],
            ['Analysis',   'Semgrep',             '1.181.0',  'Static analysis engine'],
            ['Analysis',   'CVSS scoring',        '3.1',      'Vulnerability severity scoring'],
            ['AI',         'Ollama',              'Latest',   'Local LLM inference server'],
            ['AI',         'llama3:latest',       '8B Q4_0',  'Active language model'],
            ['AI',         'Anthropic API',       'Optional', 'Cloud AI provider'],
            ['Testing',    'pytest + asyncio',    'Latest',   'Backend test suite (426 tests)'],
            ['Testing',    'httpx',               'Latest',   'Async HTTP test client'],
        ],
        col_widths=[1.0, 1.7, 1.1, 2.8])

    figure(doc, ASSETS / 'fig07_tech_distribution.png',
           'Figure 7: Technology Stack Integration Depth (Source: Project implementation)', 5.0)


# ── Chapter 7 ─────────────────────────────────────────────────────────────
def _ch7_features(doc):
    heading(doc, 'CHAPTER 7: Functional Features and Application Modules', level=1)

    heading(doc, '7.1 User Authentication', level=2)
    para(doc, 'Authentication is implemented using JWT HS256 bearer tokens. Users '
         'register with an email and password; passwords are hashed using bcrypt before '
         'storage. The POST /api/v1/auth/login endpoint validates credentials and issues '
         'a signed JWT with a configurable expiry (JWT_ACCESS_TOKEN_EXPIRE_MINUTES). '
         'The token is stored in sessionStorage under the key "explicite_token" and '
         'included as a Bearer header in all subsequent API requests. The GET /api/v1/auth/me '
         'endpoint returns the current user\'s profile without exposing password hashes. '
         'PATCH /api/v1/auth/me allows users to update preferences and AI explanation level.')

    heading(doc, '7.2 Project Management', level=2)
    para(doc, 'Projects serve as the top-level container for analysis jobs and findings. '
         'A user creates a project via POST /api/v1/projects and becomes its owner. '
         'Other users can be added as members with viewer, developer, or owner roles. '
         'Every project-scoped API endpoint validates the current user\'s membership '
         'before proceeding. System administrators bypass membership checks. The project '
         'dashboard (GET /projects/{id}/dashboard) aggregates metrics including total '
         'findings, technical debt, duplications percentage, and risk score across the '
         'project\'s analysis history.')

    heading(doc, '7.3 Source Code Analysis', level=2)
    heading(doc, '7.3.1 ZIP Archive Analysis', level=3)
    para(doc, 'Developers upload source code as a ZIP archive (max 10 MB) to POST '
         '/api/v1/projects/{id}/analyse. The archive.py module validates the submission: '
         'it checks for the ZIP magic bytes (PK\\x03\\x04), verifies that no individual '
         'entry exceeds a 100:1 compression ratio (decompression bomb detection), enforces '
         'a 1,000-entry count limit, prevents path traversal by resolving all paths within '
         'the extraction directory, and enforces a 50 MB uncompressed size limit. Valid '
         'archives are extracted to a temporary directory for Semgrep analysis.')

    heading(doc, '7.3.2 Git Repository Analysis', level=3)
    para(doc, 'Developers submit a public HTTPS Git repository URL and branch name to '
         'POST /api/v1/projects/{id}/analyse/git. The git_service.py module performs '
         'multi-stage validation: the URL must use HTTPS (not HTTP, SSH, file://, or git://); '
         'embedded credentials in the URL are rejected; the branch name is validated against '
         'an alphanumeric allowlist regex; DNS resolution is performed on the hostname; '
         'all resolved IP addresses are checked against private ranges (RFC 1918, loopback '
         '127.0.0.0/8, and link-local 169.254.0.0/16). The clone uses git clone --depth 1 '
         'with GIT_TERMINAL_PROMPT=0 and enforces size and file-count limits. The .git/ '
         'directory is removed after cloning to prevent accidental exposure of repository '
         'metadata. The commit SHA is recorded with the analysis job.')

    heading(doc, '7.3.3 Asynchronous Job Lifecycle', level=3)
    para(doc, 'Both analysis paths return HTTP 202 immediately upon job creation, with '
         'the job in "queued" status. The background task transitions the job through '
         '"running" to "completed" or "failed". Failure reasons are sanitised before '
         'storage to remove temporary source paths. The frontend polls '
         'GET /api/v1/projects/{id}/analyse/{job_id} until the job reaches a terminal '
         'state. Job metrics recorded on completion include: findings count, technical '
         'debt in minutes (configurable per finding type), duplication percentage '
         '(hash-based block detection), and a project-level risk score (severity-weighted).')

    heading(doc, '7.4 Vulnerability Findings', level=2)
    para(doc, 'Each finding stores: severity (Critical/High/Medium/Low), issue_type '
         '(Vulnerability/Maintainability/CodeSmell/other), file path, start/end line and '
         'column, rule key, description, CVSS vector (if available), CVSS base score, '
         'CVSS version, and status (open/acknowledged/resolved). The issues list endpoint '
         'supports filtering by severity, issue type, status, and a keyword search query. '
         'CVSS 3.1 scores are computed from vector strings using a standards-compliant '
         'implementation; CVSS 4.0 vectors are stored but not scored with the v3.1 formula. '
         'Findings without CVSS data (general code quality findings) display no score '
         'rather than a fabricated zero.')

    heading(doc, '7.5 AI Vulnerability Explanations', level=2)
    para(doc, 'The POST /api/v1/projects/{id}/issues/{iid}/explain endpoint accepts an '
         'explanation level parameter (beginner/intermediate/advanced) and returns a '
         'structured five-field explanation: what (the finding in plain terms), why '
         '(the security or reliability risk), how_it_arises (how this pattern appears '
         'in code), remediation (concrete steps to address it), and caveats (limitations, '
         'false-positive risk, missing context). Each field is truncated at 600 characters. '
         'The explanation level adjusts the vocabulary and assumed knowledge in the '
         'system prompt. AI responses are validated for all five required fields before '
         'storage; a malformed response triggers AiInvalidResponseError (HTTP 502).')

    heading(doc, '7.6 AI Assistant', level=2)
    para(doc, 'The POST /api/v1/projects/{id}/assistant endpoint provides a general-purpose '
         'AI chat scoped to the selected project. The system prompt includes the project '
         'name as context. Developers can ask questions about findings, analysis results, '
         'or security concepts without needing to navigate to a specific issue. The '
         'assistant uses LLM_MAX_TOKENS=512 for responses.')

    heading(doc, '7.7 Suggested Fix Generation and Workflow', level=2)
    para(doc, 'The fix workflow consists of five stages:')
    fix_stages = [
        ('Generate', 'POST .../issues/{iid}/fix sends finding context to the AI, requesting replacement lines, rationale, and caveats. Uses LLM_FIX_MAX_TOKENS=2048 to accommodate longer code output.'),
        ('Review', 'The proposed fix is stored with the original source hash (SHA-256 of the full file content). The developer reviews the unified diff, rationale, and caveats in the frontend.'),
        ('Stale check', 'At approval time, the current source file\'s hash is recomputed and compared against the stored original_hash. A mismatch (409) prevents approving a fix generated against an outdated source version.'),
        ('Approve', 'POST .../fixes/{fid}/approve requires developer role. A developer-approved fix is not automatically applied to any file.'),
        ('Download', 'GET .../fixes/{fid}/download returns an in-memory ZIP containing the patched source file. The patch is constructed in memory; original source files are never modified.'),
    ]
    for stage, desc in fix_stages:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(stage + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(4)

    heading(doc, '7.8 Learning and Tutor System', level=2)
    para(doc, 'The learning module provides three interconnected capabilities:')
    learn_items = [
        ('Learning resources', 'Curated articles and guides accessible via GET /api/v1/learning/resources. Resources are tagged by vulnerability category, CWE, and OWASP mapping.'),
        ('Learning paths', 'Structured sequences of resources with progress tracking. Developers can mark resources as completed via POST /learning/resources/{id}/complete. Progress is tracked per-user.'),
        ('Personalised recommendations', 'A deterministic matching algorithm scores resources against the user\'s open findings: rule_key match scores 3 points, issue_type match scores 2, tag match scores 1. Completed resources are excluded. Results are weighted by the finding\'s risk score.'),
        ('Interactive AI tutor', 'POST /learning/tutor/start creates a per-user session linked to a specific learning resource. Subsequent POST /learning/tutor/{session_id}/chat messages maintain conversation history, with the resource topic injected into the AI system prompt. Sessions persist across browser sessions.'),
    ]
    for label, desc in learn_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(label + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '7.9 User Settings', level=2)
    para(doc, 'The settings screen allows users to update their profile, change their '
         'preferred AI explanation level (beginner/intermediate/advanced), and toggle '
         'the application theme between Explicite Midnight (dark) and Light mode. Settings '
         'are persisted in the users table via PATCH /api/v1/auth/me. The 422 validation '
         'error handler in Settings.tsx uses the structured ApiError.detail payload to '
         'display field-level error messages directly alongside the relevant form field.')

    heading(doc, '7.10 Functional Module Summary', level=2)
    add_table(doc,
        headers=['Module', 'Backend Endpoint(s)', 'Frontend Screen', 'Status'],
        rows=[
            ['Authentication',      'POST /auth/login, GET/PATCH /auth/me', 'Login, Settings', 'Implemented'],
            ['Project Management',  'POST/GET /projects, GET /dashboard', 'Projects, Dashboard', 'Implemented'],
            ['ZIP Analysis',        'POST /analyse', 'Code Analysis', 'Implemented'],
            ['Git Analysis',        'POST /analyse/git', 'Code Analysis', 'Implemented'],
            ['Job Status',          'GET /analyse/{id}', 'Code Analysis', 'Implemented'],
            ['Findings List',       'GET /issues', 'Issues', 'Implemented'],
            ['Finding Detail',      'GET /issues/{id}', 'Issue Detail', 'Implemented'],
            ['CVSS Scoring',        'Computed server-side', 'Issue Detail', 'Implemented'],
            ['AI Explanation',      'POST /issues/{id}/explain', 'Issue Detail', 'Implemented'],
            ['AI Assistant',        'POST /assistant', 'AI Assistant', 'Implemented'],
            ['Suggested Fix',       'POST /issues/{id}/fix', 'Suggested Fix', 'Implemented'],
            ['Fix Approve/Reject',  'POST /fixes/{id}/approve|reject', 'Suggested Fix', 'Implemented'],
            ['Fix Download',        'GET /fixes/{id}/download', 'Suggested Fix', 'Implemented'],
            ['Learning Resources',  'GET /learning/resources', 'Learning', 'Implemented'],
            ['Learning Paths',      'GET /learning/paths', 'Learning', 'Implemented'],
            ['Recommendations',     'GET /learning/recommendations', 'Learning', 'Implemented'],
            ['Tutor Session',       'POST /tutor/start, /chat', 'Tutor Session', 'Implemented'],
            ['Settings',            'PATCH /auth/me', 'Settings', 'Implemented'],
        ],
        col_widths=[1.7, 2.4, 1.5, 1.0])

    figure(doc, ASSETS / 'fig01_module_distribution.png',
           'Figure 1: Distribution of Implemented Project Modules (Source: Project implementation)', 6.0)


# ── Chapter 8 ─────────────────────────────────────────────────────────────
def _ch8_ui(doc):
    heading(doc, 'CHAPTER 8: User Interface and Usability Design', level=1)

    heading(doc, '8.1 User-Centred Design Principles', level=2)
    para(doc, 'Explicite AI\'s user interface was designed in accordance with ISO 9241-110 '
         'usability principles and Nielsen\'s ten usability heuristics. The target user '
         'base—developers and computer science students—was kept in mind throughout every '
         'design decision. The primary usability goals were: clarity (finding what matters '
         'quickly), discoverability (knowing where to go next), consistency (feeling at '
         'home on every screen), and feedback (always knowing what the system is doing).')

    heading(doc, '8.2 Explicite Midnight Design System', level=2)
    para(doc, 'All visual design is governed by the "Explicite Midnight" design system, '
         'a dark-first theme implemented through CSS custom properties with the prefix --xm-. '
         'This approach ensures that every screen shares identical colour semantics, '
         'eliminating visual inconsistency and reducing cognitive load during extended use. '
         'The full token set is overridden for light mode through the html[data-theme="light"] '
         'selector, providing a complete alternative theme without duplicating component styles.')

    heading(doc, '8.3 Design Tokens', level=2)
    add_table(doc,
        headers=['Token', 'Dark Value', 'Light Value', 'Usage'],
        rows=[
            ['--xm-bg-app',      '#090B10', '#F6F8FA', 'Page background'],
            ['--xm-bg-sidebar',  '#0D1117', '#FFFFFF', 'Navigation sidebar'],
            ['--xm-bg-surface',  '#11151D', '#FFFFFF', 'Cards and panels'],
            ['--xm-bg-elevated', '#1B2330', '#F0F3F6', 'Elevated / modal surfaces'],
            ['--xm-accent',      '#4F8EF7', '#0969DA', 'Primary interactive elements'],
            ['--xm-text',        '#E6EDF3', '#1C2128', 'Primary text'],
            ['--xm-severity-critical', 'Red', 'Red', 'Critical severity badges'],
            ['--xm-severity-high',     'Amber', 'Amber', 'High severity badges'],
            ['--xm-severity-medium',   'Cyan', 'Cyan', 'Medium severity badges'],
            ['--xm-severity-low',      'Green', 'Green', 'Low severity badges'],
        ],
        col_widths=[1.9, 1.1, 1.1, 2.5])

    heading(doc, '8.4 Typography', level=2)
    para(doc, 'Body and interface text uses Inter (Google Fonts, variable weight 300–700, '
         'optical size 14–32px), selected for its legibility at small sizes and its clean, '
         'professional appearance in developer tooling. All code snippets, file paths, '
         'terminal output, and technical values are displayed in JetBrains Mono (400/500 '
         'weight), a monospace typeface optimised for code readability. Font loading uses '
         'Google Fonts with display=swap for performance.')

    heading(doc, '8.5 Screen Inventory and Navigation', level=2)
    para(doc, 'The application comprises 11 screens navigated through a persistent left '
         'sidebar. Navigation is managed by the NavCtx React context using a '
         'useState<Screen> hook, eliminating the need for a router library and simplifying '
         'the global navigation model. Screen transitions are immediate with no loading '
         'state between screens.')

    screens = [
        ('Login',         'Entry point. Email/password authentication. JWT stored in sessionStorage on success.'),
        ('Dashboard',     'Aggregated metrics for the selected project: findings by severity, technical debt, duplication %, risk score.'),
        ('Projects',      'Project list and creation. Displays member count, finding count, last analysis date.'),
        ('Code Analysis', 'Source submission (ZIP or Git URL), job status display, and analysis history.'),
        ('Issues',        'Paginated, filterable findings list with severity badges, issue type, and file path.'),
        ('Issue Detail',  'Full finding detail including CVSS score, AI explanation accordion, and fix generation controls.'),
        ('AI Assistant',  'Project-scoped AI chat for developer questions.'),
        ('Suggested Fix', 'Diff viewer, rationale panel, caveats, and approval/rejection controls.'),
        ('Learning',      'Resource library, learning paths, progress tracking, and personalised recommendations.'),
        ('Tutor Session', 'Multi-turn AI chat anchored to a specific learning resource.'),
        ('Settings',      'Profile, AI level preference, theme toggle (light/dark).'),
    ]
    add_table(doc,
        headers=['Screen', 'Primary Purpose'],
        rows=screens,
        col_widths=[1.5, 5.1])

    heading(doc, '8.6 Visual Hierarchy and Information Architecture', level=2)
    para(doc, 'The interface follows a three-level hierarchy: Project (Dashboard, Issues '
         'list) → Finding (Issue Detail with CVSS and explanation) → Action (AI Assistant, '
         'Suggested Fix, Tutor). This progressive disclosure model reduces cognitive load '
         'by surfacing summary information first and deferring detail to demand. Severity '
         'is encoded visually at every level: Critical findings use red badges, High use '
         'amber, Medium use cyan, and Low use green—consistent across all screens.')

    heading(doc, '8.7 Feedback, Loading States, and Error Handling', level=2)
    para(doc, 'Every asynchronous operation provides visible feedback. Analysis job '
         'submission displays the job status (queued → running → completed/failed) with '
         'a polling interval. AI explanation generation shows a loading indicator while '
         'the model responds. Error states display actionable messages (e.g., "AI provider '
         'not configured" for 503 responses) rather than raw HTTP status codes. Form '
         'validation errors from the backend (422 responses) are displayed as field-level '
         'messages using the structured ApiError.detail payload.')

    heading(doc, '8.8 Usability Heuristics Application', level=2)
    heuristics = [
        ('Visibility of system status', 'Job status polling keeps developers informed about long-running analysis operations. Loading spinners appear during AI generation. Error states are always visible.'),
        ('User control and freedom', 'Fix approval is always explicit. Fixes can be rejected without consequences. Navigation always allows return to any screen.'),
        ('Consistency and standards', 'All --xm-* tokens are applied consistently. Severity badges use the same colours throughout all 11 screens. Button styles and icon usage are standardised.'),
        ('Error prevention', 'ZIP validation prevents malformed or dangerous archives. Git URL validation prevents SSRF attacks. Form validation provides real-time feedback.'),
        ('Recognition over recall', 'Sidebar labels are always visible. Severity classifications use colour plus text labels. Issue types are displayed in plain English.'),
        ('Flexibility and efficiency', 'API explanation level (beginner/intermediate/advanced) adapts to user expertise. Findings list supports text search and multi-filter.'),
        ('Help and documentation', 'The interactive AI tutor and AI assistant provide contextual help without leaving the application.'),
    ]
    for heur, desc in heuristics:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(heur + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '8.9 Accessibility and Responsive Design', level=2)
    para(doc, 'The application targets a minimum viewport width of 1280px for the full '
         'sidebar layout. Mobile responsive breakpoints are implemented but formal browser '
         'QA at 1440/1280/768/390px viewport widths has not yet been formally documented. '
         'Colour contrast ratios for the Explicite Midnight palette were selected to meet '
         'WCAG 2.1 AA standards for large text; a formal accessibility audit has not been '
         'conducted. Keyboard navigation support is provided through standard HTML semantics '
         'but has not been independently verified.')

    heading(doc, '8.10 Application Screenshots', level=2)
    para(doc, 'Note: Application screenshots require the full development environment to '
         'be running (PostgreSQL, FastAPI backend, Ollama, and the Vite frontend server). '
         'Screenshots could not be captured automatically during report generation. The '
         'following figure descriptions correspond to the implemented screens:')

    screenshot_notes = [
        ('Figure 8 – Login Screen', 'Displays the email/password login form against the dark app background. The Explicite AI logo and tagline are centred. Form validation errors appear below each field.'),
        ('Figure 9 – Dashboard', 'Shows aggregated project metrics: findings by severity (Critical/High/Medium/Low) as a breakdown, technical debt in hours/minutes, duplication percentage, and project risk score.'),
        ('Figure 10 – Issues Screen', 'Lists all findings with severity badges, issue type tags, file paths, and line numbers. Filter controls at the top support severity, type, status, and text search.'),
        ('Figure 11 – Issue Detail', 'Shows complete finding information: rule key, CWE mapping, CVSS vector and score, source location. An AI explanation accordion expands to reveal the five-field structured explanation.'),
        ('Figure 12 – Settings Screen', 'Contains profile edit fields, AI explanation level selector (Beginner/Intermediate/Advanced), and a theme toggle (Explicite Midnight / Light).'),
    ]
    for fig_name, description in screenshot_notes:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(fig_name + ': ')
        r1.font.bold = True
        r1.font.size = Pt(11)
        p.add_run(description).font.size = Pt(11)
        p.paragraph_format.space_after = Pt(5)

    para(doc, 'Screenshots are to be captured and inserted by the team before final '
         'submission, using the instructions in SETUP.md to start the full development '
         'environment.',
         align=WD_ALIGN_PARAGRAPH.LEFT)


# ── Chapter 9 ─────────────────────────────────────────────────────────────
def _ch9_sdg(doc):
    heading(doc, 'CHAPTER 9: Sustainable Development Goals', level=1)

    heading(doc, '9.1 Overview', level=2)
    para(doc, 'Explicite AI contributes to the United Nations 2030 Agenda for Sustainable '
         'Development by addressing three Sustainable Development Goals (SDGs). These '
         'contributions are grounded in the platform\'s implemented features and intended '
         'use cases rather than claimed measured social impact. The SDG relevance is '
         'assessed at the level of feature alignment and potential contribution.')

    heading(doc, '9.2 SDG 4 – Quality Education', level=2)
    para(doc, 'SDG 4 aims to ensure inclusive and equitable quality education and promote '
         'lifelong learning opportunities for all. Target 4.4 specifically addresses '
         'increasing the number of people with relevant skills, including technical and '
         'vocational skills, for employment and entrepreneurship.')

    para(doc, 'Explicite AI contributes to SDG 4 through:')
    sdg4_features = [
        ('Interactive AI Tutor', 'The multi-turn tutor session provides contextual, conversational learning support anchored to specific security topics. Developers can ask follow-up questions, request clarifications, and explore vulnerability concepts interactively without leaving the analysis workflow.'),
        ('Structured Learning Resources', 'Curated articles and guides linked to specific CWE and OWASP categories ensure that learning material is directly relevant to the findings a developer has encountered.'),
        ('Personalised Recommendations', 'The deterministic recommendation algorithm surfaces the most relevant learning resources based on the developer\'s own open findings, creating a personalised learning pathway grounded in their actual code.'),
        ('Adjustable Explanation Levels', 'The beginner/intermediate/advanced explanation setting adapts AI-generated content to the developer\'s expertise level, making security knowledge accessible to learners at all stages.'),
        ('Secure Coding Education', 'By explaining not just what a vulnerability is but why it matters and how it arises, Explicite AI supports the development of lasting secure coding knowledge rather than one-off fixes.'),
    ]
    for feature, desc in sdg4_features:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(feature + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '9.3 SDG 9 – Industry, Innovation and Infrastructure', level=2)
    para(doc, 'SDG 9 aims to build resilient infrastructure, promote inclusive and '
         'sustainable industrialisation, and foster innovation. Target 9.5 specifically '
         'addresses enhancing scientific research and upgrading the technological '
         'capabilities of industrial sectors.')

    para(doc, 'Explicite AI contributes to SDG 9 through:')
    sdg9_features = [
        ('Automated Security Analysis', 'Reducing the manual effort required for vulnerability detection in software development, enabling smaller teams to maintain higher security standards.'),
        ('AI-Assisted Development', 'Integrating AI-powered analysis assistance into the development workflow, demonstrating how AI can augment developer capability in security-sensitive domains.'),
        ('Improved Software Quality', 'Through technical debt measurement, duplication detection, and CVSS-based prioritisation, the platform supports systematic improvement of software quality.'),
        ('Open and Configurable AI', 'Supporting both locally hosted (Ollama) and cloud (Anthropic) AI providers enables the platform to function in resource-constrained environments without mandatory cloud dependency.'),
        ('Resilient Digital Infrastructure', 'By improving the security quality of software that developers produce, the platform contributes indirectly to the resilience of digital infrastructure.'),
        ('Replicable Architecture', 'The open implementation demonstrates how AI-augmented SAST tools can be built with accessible open-source components, supporting knowledge transfer.'),
    ]
    for feature, desc in sdg9_features:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(feature + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(5)

    heading(doc, '9.4 SDG 16 – Peace, Justice and Strong Institutions', level=2)
    para(doc, 'SDG 16 aims to promote peaceful and inclusive societies for sustainable '
         'development, provide access to justice for all, and build effective, accountable, '
         'and inclusive institutions. Target 16.6 addresses effective, accountable, and '
         'transparent institutions; Target 16.10 relates to public access to information.')

    para(doc, 'Explicite AI contributes indirectly to SDG 16 through its support for '
         'secure and trustworthy digital systems. Software vulnerabilities in critical '
         'infrastructure, public services, and institutional applications can undermine '
         'public trust, compromise personal data, and enable malicious actors to disrupt '
         'essential services. By helping developers identify and understand vulnerabilities '
         'in the software they build, the platform contributes to the broader ecosystem '
         'of secure, trustworthy digital institutions.')

    para(doc, 'The platform\'s design also reflects SDG 16 values through its human '
         'oversight principles: AI-generated fixes cannot be applied without explicit '
         'developer approval; AI responses are clearly labelled as advisory and potentially '
         'imprecise; and the system is designed to inform rather than automate decisions '
         'with security implications.')

    heading(doc, '9.5 SDG Contribution Summary', level=2)
    add_table(doc,
        headers=['SDG', 'Goal', 'Relevant Features', 'Contribution Type'],
        rows=[
            ['SDG 4', 'Quality Education',
             'AI tutor, learning resources, personalised recommendations, explanation levels',
             'Direct: educational tool for secure coding skills'],
            ['SDG 9', 'Industry & Innovation',
             'Automated SAST, AI-assisted development, open configurable architecture',
             'Direct: technology innovation in development tooling'],
            ['SDG 16', 'Peace & Institutions',
             'Security vulnerability detection, human oversight in AI decisions',
             'Indirect: contributes to secure digital systems'],
        ],
        col_widths=[0.6, 1.4, 2.8, 1.8])

    figure(doc, ASSETS / 'fig05_sdg_mapping.png',
           'Figure 5: Explicite AI SDG Feature Contribution Mapping (Source: Project analysis)', 5.5)

    para(doc, 'Important note: Explicite AI does not claim certification under any SDG '
         'programme, measured improvement in educational outcomes, or quantified impact '
         'on software security at a population level. The SDG contributions described '
         'above represent intended alignment with SDG principles based on the platform\'s '
         'implemented features and design philosophy.',
         align=WD_ALIGN_PARAGRAPH.LEFT)


if __name__ == '__main__':
    doc = new_document()
    build_chapters_06_09(doc)
    out = Path(__file__).parent.parent / 'test_ch6_9.docx'
    doc.save(str(out))
    print(f'Chapters 6–9 saved: {out}')
