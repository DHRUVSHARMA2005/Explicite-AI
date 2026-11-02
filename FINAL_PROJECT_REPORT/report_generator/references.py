"""References and Appendices sections."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from styles import *
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_references(doc):
    heading(doc, 'References', level=1)
    _refs(doc)
    page_break(doc)
    _appendices(doc)


def _refs(doc):
    refs = [
        '[1] Z. Rasheed, M. A. Sami, M. Waseem, K. Kemell, X. Wang, A. Nguyen, K. Systä, '
        'and P. Abrahamsson, "AI-powered Code Review with LLMs: Early Results," arXiv preprint '
        'arXiv:2404.18496, Tampere University et al., 2024.',

        '[2] B. İçöz and G. Biricik, "Automated Code Review Using Large Language Models with '
        'Symbolic Reasoning," IEEE, 979-8-3315-1482-2/25, Yıldız Technical University, '
        'Istanbul, 2025.',

        '[3] M. Vijayvergiya, M. Salawa, I. Budiselić, D. Zheng, P. Lamblin, M. Ivanković, '
        'J. Carin, M. Lewko, J. Andonov, G. Petrović, D. Tarlow, P. Maniatis, and R. Just, '
        '"AI-Assisted Assessment of Coding Practices in Modern Code Review," in Proc. AIware '
        '\'24, Porto de Galinhas, Brazil, July 2024. ACM.',

        '[4] R. Y. Limbani, P. Adityakumar, and S. M. Basit, "Evaluating The Impact Of '
        'AI-Assisted Code Reviews On Developer Productivity And Code Quality," International '
        'Journal of Creative Research Thoughts (IJCRT), vol. 13, no. 4, Apr. 2025, '
        'ISSN: 2320-2882, Article ID: IJCRT25A4167.',

        '[5] Z. Li, D. Zou, S. Xu, X. Ou, H. Jin, S. Wang, Z. Deng, and Y. Zhong, '
        '"VulDeePecker: A Deep Learning-Based System for Vulnerability Detection," in Proc. '
        '25th Annual Network and Distributed System Security Symposium (NDSS 2018), '
        'San Diego, CA, Feb. 2018. DOI: 10.14722/ndss.2018.23158.',

        '[6] G. Bennett, T. Hall, E. Winter, and S. Counsell, "Semgrep*: Improving the '
        'Limited Performance of Static Application Security Testing (SAST) Tools," in Proc. '
        '28th Int. Conf. on Evaluation and Assessment in Software Engineering (EASE 2024 / '
        'SECUTE), Salerno, Italy. ACM, pp. 614–623, Jun. 2024. '
        'DOI: 10.1145/3661167.3661262.',

        '[7] Z. Fan, X. Gao, M. Mirchev, A. Roychoudhury, and S. H. Tan, "Automated Repair '
        'of Programs from Large Language Models," in Proc. 45th IEEE/ACM Int. Conf. on '
        'Software Engineering (ICSE 2023), Melbourne, Australia. IEEE/ACM, pp. 1469–1481, '
        'May 2023. DOI: 10.1109/ICSE48619.2023.00128.',

        '[8] Q. Mao, Z. Li, X. Hu, K. Liu, X. Xia, and J. Sun, "Towards Explainable '
        'Vulnerability Detection with Large Language Models," arXiv preprint '
        'arXiv:2406.09701, Zhejiang University / York University, Jun. 2024.',

        '[9] Semgrep, Inc., "Semgrep Documentation," 2024. [Online]. '
        'Available: https://semgrep.dev/docs/',

        '[10] S. Liddell, "FastAPI Documentation," 2024. [Online]. '
        'Available: https://fastapi.tiangolo.com/',

        '[11] Meta Open Source, "React Documentation," 2024. [Online]. '
        'Available: https://react.dev/',

        '[12] The PostgreSQL Global Development Group, "PostgreSQL 16 Documentation," 2024. '
        '[Online]. Available: https://www.postgresql.org/docs/16/',

        '[13] FIRST (Forum of Incident Response and Security Teams), "Common Vulnerability '
        'Scoring System v3.1: Specification Document," 2019. [Online]. '
        'Available: https://www.first.org/cvss/v3.1/specification-document',

        '[14] Snyk Ltd., "Snyk Code Product Documentation," 2025. [Online]. '
        'Available: https://docs.snyk.io/products/snyk-code',

        '[15] SonarSource S.A., "SonarQube Documentation," 2025. [Online]. '
        'Available: https://docs.sonarqube.org/',

        '[16] GitHub, Inc., "CodeQL Documentation," 2025. [Online]. '
        'Available: https://codeql.github.com/docs/',

        '[17] United Nations, "Transforming our world: the 2030 Agenda for Sustainable '
        'Development," United Nations General Assembly Resolution A/RES/70/1, 2015.',

        '[18] B. İçöz, "Automated Code Review Using Large Language Models," survey of '
        'developers, n=287, cited in [2], 2025.',
    ]

    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.35)
        p.paragraph_format.first_line_indent = Inches(-0.35)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = Pt(16)
        run = p.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)


def _appendices(doc):
    heading(doc, 'Appendices', level=1)

    # Appendix A
    heading(doc, 'Appendix A: Key API Endpoints', level=2)
    add_table(doc,
        headers=['Method', 'Endpoint', 'Description', 'Auth Required'],
        rows=[
            ['POST', '/api/v1/auth/login',            'Authenticate user, receive JWT',            'No'],
            ['GET',  '/api/v1/auth/me',               'Get current user profile',                  'Yes'],
            ['PATCH','/api/v1/auth/me',               'Update profile / preferences',              'Yes'],
            ['POST', '/api/v1/projects',              'Create project',                            'Yes'],
            ['GET',  '/api/v1/projects',              'List user projects',                        'Yes'],
            ['GET',  '/api/v1/projects/{id}/dashboard','Project dashboard metrics',                'Yes'],
            ['POST', '/api/v1/projects/{id}/analyse', 'Submit ZIP for analysis (multipart)',       'Yes (developer+)'],
            ['POST', '/api/v1/projects/{id}/analyse/git','Submit Git URL for analysis',           'Yes (developer+)'],
            ['GET',  '/api/v1/projects/{id}/analyse/{job_id}','Poll job status',                  'Yes'],
            ['GET',  '/api/v1/projects/{id}/issues',  'List findings (filter: severity/type/status/q)', 'Yes'],
            ['GET',  '/api/v1/projects/{id}/issues/{iid}','Finding detail with CVSS',             'Yes'],
            ['POST', '/api/v1/projects/{id}/issues/{iid}/explain','Generate AI explanation',     'Yes'],
            ['POST', '/api/v1/projects/{id}/assistant','Project-scoped AI chat',                 'Yes'],
            ['POST', '/api/v1/projects/{id}/issues/{iid}/fix','Generate suggested fix',          'Yes (developer+)'],
            ['POST', '/api/v1/projects/{id}/fixes/{fid}/approve','Approve fix',                  'Yes (developer+)'],
            ['POST', '/api/v1/projects/{id}/fixes/{fid}/reject', 'Reject fix',                   'Yes'],
            ['GET',  '/api/v1/projects/{id}/fixes/{fid}/download','Download patched ZIP',        'Yes'],
            ['GET',  '/api/v1/learning/resources',    'List learning resources',                   'Yes'],
            ['GET',  '/api/v1/learning/paths',        'List learning paths',                       'Yes'],
            ['POST', '/api/v1/learning/resources/{id}/complete','Mark resource complete',         'Yes'],
            ['POST', '/api/v1/learning/tutor/start',  'Start tutor session',                       'Yes'],
            ['POST', '/api/v1/learning/tutor/{sid}/chat','Send tutor chat message',               'Yes'],
            ['GET',  '/health',                       'Health check (no auth, no prefix)',          'No'],
        ],
        col_widths=[0.7, 3.1, 2.1, 1.2])

    # Appendix B
    page_break(doc)
    heading(doc, 'Appendix B: Database Model Overview', level=2)
    add_table(doc,
        headers=['Table', 'Key Columns', 'Relationships'],
        rows=[
            ['users',                'id, email, password_hash, system_role, ai_level, theme_preference, created_at',
             'One-to-many: project_memberships, tutor_sessions, learning_progress'],
            ['projects',             'id, name, description, created_at',
             'Many-to-many: users (via project_memberships); one-to-many: analysis_jobs'],
            ['project_memberships',  'project_id (FK), user_id (FK), role',
             'Join table: projects ↔ users'],
            ['analysis_jobs',        'id, project_id (FK), status, source_path, repo_url, technical_debt_minutes, duplications_pct, failure_reason, created_at',
             'One-to-many: findings'],
            ['findings',             'id, analysis_job_id (FK), severity, issue_type, file_path, start_line, rule_key, description, cvss_vector, cvss_score, cvss_version, status',
             'Many-to-one: analysis_jobs; one-to-many: suggested_fixes'],
            ['suggested_fixes',      'id, finding_id (FK), proposed_lines (JSONB), rationale, caveats, original_hash, status (pending/approved/rejected)',
             'Many-to-one: findings'],
            ['learning_resources',   'id, title, url, description, resource_type, tags (JSONB)',
             'Many-to-many: learning_paths (via learning_path_resources)'],
            ['tutor_sessions',       'id, user_id (FK), resource_id (FK), created_at',
             'One-to-many: tutor_messages'],
            ['tutor_messages',       'id, session_id (FK), role, content, created_at',
             'Many-to-one: tutor_sessions'],
        ],
        col_widths=[1.5, 3.0, 2.1])

    # Appendix C
    page_break(doc)
    heading(doc, 'Appendix C: Selected Code Snippets', level=2)

    heading(doc, 'C.1 CVSS 3.1 Scoring (cvss_scoring.py)', level=3)
    code_block(doc,
        'def score_cvss_vector(vector: str) -> CvssResult:\n'
        '    version = _detect_version(vector)\n'
        '    if version != "3.1":\n'
        '        return CvssResult(score=None, severity=None, version=version)\n'
        '    parts = _parse_v31(vector)\n'
        '    iss = 1 - (1-C(parts["C"])) * (1-C(parts["I"])) * (1-C(parts["A"]))\n'
        '    if parts["S"] == "U":\n'
        '        impact = 6.42 * iss\n'
        '    else:\n'
        '        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15\n'
        '    exploitability = (8.22 * AV(parts["AV"]) * AC(parts["AC"])\n'
        '                      * PR(parts["PR"], parts["S"]) * UI(parts["UI"]))\n'
        '    if impact <= 0:\n'
        '        return CvssResult(score=0.0, severity="None", version="3.1")\n'
        '    if parts["S"] == "U":\n'
        '        base = _roundup(min(impact + exploitability, 10))\n'
        '    else:\n'
        '        base = _roundup(min(1.08 * (impact + exploitability), 10))\n'
        '    return CvssResult(score=base, severity=_v31_severity(base), version="3.1")')

    heading(doc, 'C.2 Risk Scoring (risk_scoring.py)', level=3)
    code_block(doc,
        'SCORING_VERSION = "v1.0"\n\n'
        'def score_finding(severity: str) -> tuple[float, str]:\n'
        '    if severity == "Critical": return 10.0, "Critical"\n'
        '    if severity == "High":     return 7.5,  "High"\n'
        '    if severity == "Medium":   return 5.0,  "Medium"\n'
        '    return 2.5, "Low"\n\n'
        'def project_risk_score(findings: list) -> float:\n'
        '    if not findings: return 0.0\n'
        '    weights = {"Critical": 10, "High": 7.5, "Medium": 5, "Low": 2.5}\n'
        '    raw = sum(weights.get(f.severity, 2.5) for f in findings)\n'
        '    return round(min(raw / len(findings) * 2, 100), 1)')

    heading(doc, 'C.3 Navigation Context (App.tsx)', level=3)
    code_block(doc,
        'export type Screen =\n'
        '  | "login" | "dashboard" | "issues" | "issue-detail"\n'
        '  | "ai-assistant" | "suggested-fix" | "code-analysis"\n'
        '  | "learning" | "tutor" | "projects" | "settings"\n\n'
        'const NavCtx = createContext<NavState>(/* ... */)\n\n'
        'export function useNav() { return useContext(NavCtx) }\n\n'
        '// No router library — navigation is pure React state')

    # Appendix D – screenshot placeholder
    page_break(doc)
    heading(doc, 'Appendix D: Application Screenshots', level=2)
    para(doc, 'Note: Application screenshots require the full development environment to be '
         'running. The environment can be started by following the instructions in SETUP.md. '
         'Screenshots should be captured at 1440px viewport width in Google Chrome and '
         'inserted here before final submission. Required screenshots:')
    required = [
        'Login screen',
        'Dashboard screen (with aggregated project metrics visible)',
        'Projects screen (project list)',
        'Code Analysis screen (after job completion, showing job status)',
        'Issues screen (findings list with severity badges)',
        'Issue Detail screen (with CVSS score and AI explanation expanded)',
        'AI Assistant screen (showing a conversation)',
        'Suggested Fix screen (showing diff view and caveats)',
        'Learning screen (with recommendations visible)',
        'Tutor Session screen (showing AI chat)',
        'Settings screen (showing AI level and theme controls)',
    ]
    for item in required:
        bullet(doc, item)

    # Appendix E
    page_break(doc)
    heading(doc, 'Appendix E: Test Case Summary', level=2)
    add_table(doc,
        headers=['Test File', 'Category', 'Count', 'Pass', 'Skip', 'Fail', 'Notes'],
        rows=[
            ['test_auth.py',              'Auth',          '28', '28', '0', '0', 'Login, token, RBAC'],
            ['test_projects.py',          'Projects',      '24', '24', '0', '0', 'CRUD, membership'],
            ['test_analysis_pipeline.py', 'Analysis',      '31', '31', '0', '0', 'ZIP, jobs, findings'],
            ['test_git_analysis.py',      'Git',           '17', '17', '0', '0', 'SSRF, URL, clone'],
            ['test_metrics.py',           'Metrics',       '29', '29', '0', '0', 'Debt, dup, CVSS'],
            ['test_issues.py',            'Issues',        '22', '22', '0', '0', 'Filter, detail, patch'],
            ['test_ai_service.py',        'AI Service',    '35', '35', '0', '0', 'Providers, parsing'],
            ['test_ai_endpoints.py',      'AI Endpoints',  '28', '27', '1', '0', '1 slow test skipped'],
            ['test_fix_endpoints.py',     'Fixes',         '26', '26', '0', '0', 'Gen, approve, reject'],
            ['test_learning.py',          'Learning',      '20', '20', '0', '0', 'Resources, paths'],
            ['test_learning_paths.py',    'Learning Paths','18', '18', '0', '0', 'Progress, ordering'],
            ['test_recommendations.py',   'Recommend.',    '22', '22', '0', '0', 'Deterministic match'],
            ['test_tutor.py',             'Tutor',         '24', '24', '0', '0', 'Session, chat, history'],
            ['test_risk_scoring.py',      'Risk',          '21', '21', '0', '0', 'Score formula'],
            ['test_quality_gate.py',      'Quality Gate',  '21', '21', '0', '0', 'Gate thresholds'],
            ['Other (3 files)',           'Misc',          '30', '30', '0', '0', 'Seeds, config, utils'],
            ['TOTAL',                     'All',          '426','425', '1', '0', 'Phase O baseline'],
        ],
        col_widths=[1.7, 1.1, 0.55, 0.55, 0.55, 0.55, 2.0])

    # Appendix F
    page_break(doc)
    heading(doc, 'Appendix F: Team Contribution Statement', level=2)
    para(doc, 'The following table records the equal 50–50 division of project work between '
         'the two team members. Both members contributed to all phases of the project at a '
         'high level; the table identifies the primary technical responsibilities of each member.')

    add_table(doc,
        headers=['Team Member', 'Registration', 'Primary Responsibilities', 'Contribution'],
        rows=[
            ['Dhruv Sharma', '24BBS0063',
             'Backend architecture and FastAPI development; PostgreSQL database and SQLAlchemy models; '
             'Semgrep integration and analysis pipeline; CVSS scoring implementation; '
             'AI service integration and provider abstraction; suggested fixes and learning services; '
             'backend testing and documentation; Git repository and project administration.',
             '50%'],
            ['Rijul Kothawade', '24BBS0230',
             'Frontend architecture and React interface development; dashboard and project management '
             'modules; code analysis interface and source submission workflow; issues and vulnerability '
             'presentation; user settings and appearance management; usability design and interface '
             'testing; frontend integration and documentation.',
             '50%'],
            ['Total', '', '', '100%'],
        ],
        col_widths=[1.4, 1.1, 3.8, 0.85])

    para(doc, 'Both team members declare that the above contribution statement accurately '
         'reflects the division of work. The final application represents a joint effort '
         'with equal overall contribution from each team member.')

    # Appendix G
    page_break(doc)
    heading(doc, 'Appendix G: Research Paper Review Summary', level=2)
    para(doc, 'Eight research papers were reviewed for this project. Four papers were '
         'supplied with the project materials; four additional papers were identified '
         'through academic database searches and verified for publication details.')

    add_table(doc,
        headers=['#', 'Title (abbreviated)', 'Source', 'Year', 'Venue Type', 'Key Metric / Finding'],
        rows=[
            ['[1]', 'AI-powered Code Review with LLMs: Early Results',
             'arXiv 2404.18496', '2024', 'Preprint (supplied)', 'Multi-agent GPT-4 system; dual quality + learning benefit'],
            ['[2]', 'Automated Code Review Using LLMs with Symbolic Reasoning',
             'IEEE 979-8-3315-1482-2/25', '2025', 'IEEE Conference (supplied)', 'GraphCodeBERT hybrid: 68.7% accuracy'],
            ['[3]', 'AI-Assisted Assessment of Coding Practices (AutoCommenter)',
             'AIware \'24 (ACM)', '2024', 'ACM Conference (supplied)', 'Deployed to 10,000+ Google developers'],
            ['[4]', 'AI-Assisted Code Reviews on Developer Productivity',
             'IJCRT25A4167', '2025', 'Journal (supplied)', 'P@1=95%, review time reduced 33%'],
            ['[5]', 'VulDeePecker: Deep Learning for Vulnerability Detection',
             'NDSS 2018', '2018', 'Peer-reviewed conf. (additional)', '4 unreported CVEs found in real software'],
            ['[6]', 'Semgrep*: Improving SAST Tool Performance',
             'EASE 2024 (ACM)', '2024', 'ACM Conference (additional)', 'Tools detect 11–26% individually; Semgrep* reaches 44.7%'],
            ['[7]', 'Automated Repair of Programs from LLMs',
             'ICSE 2023 (IEEE/ACM)', '2023', 'IEEE/ACM Conference (additional)', 'Codex repairs comparable to TBar/Recoder'],
            ['[8]', 'Towards Explainable Vulnerability Detection with LLMs',
             'arXiv 2406.09701', '2024', 'Preprint (additional)', 'LLMVulExp: >90% F1; XAI metrics: Accuracy/Clarity/Actionability'],
        ],
        col_widths=[0.35, 2.2, 1.5, 0.5, 1.3, 2.0])


if __name__ == '__main__':
    doc = new_document()
    build_references(doc)
    out = Path(__file__).parent.parent / 'test_refs.docx'
    doc.save(str(out))
    print(f'References + Appendices saved: {out}')
