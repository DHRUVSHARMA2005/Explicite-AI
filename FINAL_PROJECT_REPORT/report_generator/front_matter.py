"""Front matter: title page, abstract, TOC, abbreviations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from styles import *
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def build_front_matter(doc):
    _title_page(doc)
    page_break(doc)
    _abstract(doc)
    page_break(doc)
    _toc_page(doc)
    page_break(doc)
    _list_of_figures(doc)
    page_break(doc)
    _list_of_tables(doc)
    page_break(doc)
    _abbreviations(doc)
    page_break(doc)


def _title_page(doc):
    # Top university line
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('\n\n')
    run.font.size = Pt(12)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('VELLORE INSTITUTE OF TECHNOLOGY')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(16)
    r2.font.bold = True
    r2.font.color.rgb = NAVY

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run('Vellore, Tamil Nadu, India')
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(13)
    r3.font.color.rgb = DGREY

    doc.add_paragraph()
    _divider(doc)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run('\nFINAL PROJECT REPORT')
    r4.font.name = 'Times New Roman'
    r4.font.size = Pt(14)
    r4.font.bold = True
    r4.font.color.rgb = DGREY

    # Big title
    doc.add_paragraph()
    t1 = doc.add_paragraph()
    t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rt1 = t1.add_run('EXPLICITE AI')
    rt1.font.name = 'Times New Roman'
    rt1.font.size = Pt(28)
    rt1.font.bold = True
    rt1.font.color.rgb = NAVY

    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rt2 = t2.add_run('An AI-Powered Explainable Code Review and Security Analysis Platform')
    rt2.font.name = 'Times New Roman'
    rt2.font.size = Pt(14)
    rt2.font.italic = True
    rt2.font.color.rgb = BLUE

    doc.add_paragraph()
    _divider(doc)
    doc.add_paragraph()

    # Submitted by
    _centre_label(doc, 'Submitted by:', size=12, bold=True)
    _centre_label(doc, 'Dhruv Sharma (24BBS0063)', size=12)
    _centre_label(doc, 'Rijul Kothawade (24BBS0230)', size=12)
    doc.add_paragraph()

    _centre_label(doc, 'Submitted in partial fulfilment of the requirements for:', size=11, italic=True)
    _centre_label(doc, 'CBS3011 – Usability Design of Software Applications', size=12, bold=True, color=NAVY)
    doc.add_paragraph()

    _centre_label(doc, 'Submitted to:', size=11, italic=True)
    _centre_label(doc, 'Swarnalatha P.', size=12, bold=True)
    _centre_label(doc, 'Vellore Institute of Technology', size=11)
    doc.add_paragraph()
    doc.add_paragraph()

    _centre_label(doc, 'Academic Year: 2026–2027', size=12, bold=True)
    doc.add_paragraph()
    _divider(doc)


def _divider(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('─' * 60)
    r.font.color.rgb = LGREY
    r.font.size = Pt(10)


def _centre_label(doc, text, size=12, bold=False, italic=False, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return p


def _abstract(doc):
    heading(doc, 'Abstract', level=1)

    abstract_text = (
        "Modern software development faces a growing challenge: static analysis tools generate "
        "large volumes of vulnerability findings, yet developers—particularly those with limited "
        "security expertise—lack the contextual guidance necessary to understand, prioritise, and "
        "remediate these issues effectively. This disconnect between automated detection and "
        "actionable developer knowledge represents a critical gap in contemporary software "
        "engineering practice.\n\n"
        "Explicite AI addresses this gap by providing an integrated, AI-powered platform that "
        "combines static application security testing (SAST) with contextual AI-generated "
        "explanations, structured suggested fixes, and adaptive learning support. The platform "
        "enables developers to submit source code—either as a ZIP archive or via a public Git "
        "repository URL—and receive a comprehensive analysis covering security vulnerabilities, "
        "code quality issues, CVSS severity scores, and technical debt estimates.\n\n"
        "The technical implementation employs a modern three-tier architecture: a React 19 and "
        "TypeScript frontend presenting an 'Explicite Midnight' dark-first design system; a "
        "Python 3.14 and FastAPI backend providing a RESTful API; and a PostgreSQL 16 database "
        "for persistent storage of analysis results, findings, and learning progress. Static "
        "analysis is performed by Semgrep 1.181.0, supporting Python, Java, JavaScript, and "
        "TypeScript. AI-powered explanations and suggested fixes are generated through a "
        "configurable provider layer supporting both locally hosted Ollama models (llama3:latest) "
        "and the Anthropic API.\n\n"
        "Core implemented features include: asynchronous code analysis with job status polling; "
        "categorised vulnerability findings with CVSS 3.1 scoring; structured AI explanations "
        "covering what, why, how, remediation, and caveats; AI-generated code fixes with "
        "mandatory developer approval; an interactive multi-turn AI tutor session; personalised "
        "learning resource recommendations; and a configurable light/dark user interface.\n\n"
        "The usability design applies principles from ISO 9241 and Nielsen's heuristics, "
        "emphasising clarity, discoverability, consistent visual hierarchy, and human oversight "
        "preservation. The platform includes 426 passing automated backend tests verified through "
        "a comprehensive Phase O live smoke test across 62 API checks.\n\n"
        "Explicite AI contributes to three United Nations Sustainable Development Goals: SDG 4 "
        "(Quality Education) through its AI tutor and learning pathway; SDG 9 (Industry, "
        "Innovation and Infrastructure) through automated security analysis; and SDG 16 (Peace, "
        "Justice and Strong Institutions) through its contribution to secure and trustworthy "
        "digital systems. The platform is intended as an educational and development tool, "
        "empowering developers to move from passive vulnerability detection towards active "
        "understanding and effective remediation."
    )
    for para_text in abstract_text.split('\n\n'):
        p = doc.add_paragraph(para_text)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = Pt(18)
        p.paragraph_format.space_after = Pt(8)


def _toc_page(doc):
    heading(doc, 'Table of Contents', level=1)
    add_toc(doc)


def _list_of_figures(doc):
    heading(doc, 'List of Figures', level=1)
    figures = [
        ('Figure 1', 'Distribution of Implemented Project Modules'),
        ('Figure 2', 'Backend Test Suite Results'),
        ('Figure 3', 'Feature Implementation Status'),
        ('Figure 4', 'Competitor Feature Comparison Matrix'),
        ('Figure 5', 'Explicite AI SDG Contribution Mapping'),
        ('Figure 6', 'Explicite AI Code Analysis Workflow'),
        ('Figure 7', 'Technology Stack Maturity and Integration Depth'),
        ('Figure 8', 'Login Screen (screenshot unavailable – application must be running)'),
        ('Figure 9', 'Dashboard Screen (screenshot unavailable)'),
        ('Figure 10', 'Issues Screen with Severity Classification (screenshot unavailable)'),
    ]
    for fig_num, fig_title in figures:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(fig_num + ': ')
        r1.font.bold = True
        r1.font.size = Pt(11)
        p.add_run(fig_title).font.size = Pt(11)


def _list_of_tables(doc):
    heading(doc, 'List of Tables', level=1)
    tables = [
        ('Table 1',  'Technology Stack Summary'),
        ('Table 2',  'Literature Review Comparison'),
        ('Table 3',  'Competitor Feature Comparison'),
        ('Table 4',  'Implemented Functional Modules'),
        ('Table 5',  'Database Entity Summary'),
        ('Table 6',  'Backend Test Suite Results'),
        ('Table 7',  'CVSS 3.1 Severity Ratings'),
        ('Table 8',  'SDG Contribution Mapping'),
        ('Table 9',  'Development Challenges and Solutions'),
        ('Table 10', 'Team Contribution Statement'),
        ('Table 11', 'API Endpoint Summary (Appendix A)'),
        ('Table 12', 'Database Model Overview (Appendix B)'),
        ('Table 13', 'Test Case Summary (Appendix E)'),
    ]
    for tnum, ttitle in tables:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(tnum + ': ')
        r1.font.bold = True
        r1.font.size = Pt(11)
        p.add_run(ttitle).font.size = Pt(11)


def _abbreviations(doc):
    heading(doc, 'List of Abbreviations', level=1)
    abbrevs = [
        ('AI',   'Artificial Intelligence'),
        ('API',  'Application Programming Interface'),
        ('CVSS', 'Common Vulnerability Scoring System'),
        ('CWE',  'Common Weakness Enumeration'),
        ('DAST', 'Dynamic Application Security Testing'),
        ('DFD',  'Data Flow Diagram'),
        ('ERD',  'Entity Relationship Diagram'),
        ('HTTP', 'Hypertext Transfer Protocol'),
        ('IDE',  'Integrated Development Environment'),
        ('JSON', 'JavaScript Object Notation'),
        ('JWT',  'JSON Web Token'),
        ('LLM',  'Large Language Model'),
        ('ML',   'Machine Learning'),
        ('NVD',  'National Vulnerability Database'),
        ('ORM',  'Object-Relational Mapper'),
        ('OWASP','Open Web Application Security Project'),
        ('REST', 'Representational State Transfer'),
        ('SAST', 'Static Application Security Testing'),
        ('SDG',  'Sustainable Development Goal'),
        ('SQL',  'Structured Query Language'),
        ('SSRF', 'Server-Side Request Forgery'),
        ('UI',   'User Interface'),
        ('UX',   'User Experience'),
        ('VIT',  'Vellore Institute of Technology'),
        ('XAI',  'Explainable Artificial Intelligence'),
    ]
    add_table(doc,
              headers=['Abbreviation', 'Full Form'],
              rows=abbrevs,
              col_widths=[1.5, 4.5])


if __name__ == '__main__':
    doc = new_document()
    build_front_matter(doc)
    out = Path(__file__).parent.parent / 'Explicite_AI_Final_Project_Report.docx'
    doc.save(str(out))
    print(f'Front matter saved to {out}')
