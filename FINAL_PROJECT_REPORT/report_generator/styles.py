"""Shared document styles and helpers for the Explicite AI report."""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "Report_Assets"

NAVY  = RGBColor(0x1A, 0x23, 0x7E)
BLUE  = RGBColor(0x15, 0x65, 0xC0)
LGREY = RGBColor(0xEC, 0xEF, 0xF1)
DGREY = RGBColor(0x37, 0x47, 0x4F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)


def new_document() -> Document:
    doc = Document()
    _set_page_margins(doc)
    _define_styles(doc)
    return doc


def _set_page_margins(doc):
    for section in doc.sections:
        section.page_width  = Inches(8.27)   # A4
        section.page_height = Inches(11.69)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)
        section.top_margin    = Inches(1.0)
        section.bottom_margin = Inches(1.0)


def _define_styles(doc):
    styles = doc.styles

    # Body text
    body = styles['Normal']
    body.font.name = 'Times New Roman'
    body.font.size = Pt(12)
    body.paragraph_format.space_after = Pt(6)
    body.paragraph_format.line_spacing = Pt(18)   # ~1.5 line spacing
    body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Heading 1 — Chapter
    h1 = styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = NAVY
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after  = Pt(12)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.page_break_before = True

    # Heading 2 — Section
    h2 = styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = BLUE
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after  = Pt(6)
    h2.paragraph_format.keep_with_next = True

    # Heading 3 — Subsection
    h3 = styles['Heading 3']
    h3.font.name = 'Times New Roman'
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = DGREY
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after  = Pt(4)

    # Caption style
    try:
        cap = styles['Caption']
    except KeyError:
        cap = styles.add_style('Caption', 1)
    cap.font.name = 'Times New Roman'
    cap.font.size = Pt(10)
    cap.font.italic = True
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)

    # Code style
    try:
        code_style = styles['Code']
    except KeyError:
        code_style = styles.add_style('Code', 1)
    code_style.font.name = 'Courier New'
    code_style.font.size = Pt(9)
    code_style.paragraph_format.left_indent = Inches(0.3)
    code_style.paragraph_format.space_after = Pt(4)


# ── Paragraph helpers ─────────────────────────────────────────────────────

def heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    return p


def para(doc, text, style='Normal', align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(text, style=style)
    p.alignment = align
    return p


def bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.3 + level * 0.25)
    p.add_run(text).font.size = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    return p


def numbered(doc, text, level=0):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.left_indent = Inches(0.3 + level * 0.25)
    p.add_run(text).font.size = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    return p


def code_block(doc, text):
    for line in text.split('\n'):
        p = doc.add_paragraph(style='Code')
        p.add_run(line)


def figure(doc, img_path, caption_text, width_inches=5.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    try:
        run.add_picture(str(img_path), width=Inches(width_inches))
    except Exception:
        p.add_run(f'[Figure: {img_path.name}]')
    cap = doc.add_paragraph(caption_text, style='Caption')
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def page_break(doc):
    doc.add_page_break()


# ── Table helpers ─────────────────────────────────────────────────────────

def add_table(doc, headers, rows, col_widths=None, shade_header=True):
    ncols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=ncols)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = table.rows[0]
    for i, htext in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = htext
        run = cell.paragraphs[0].runs[0]
        run.font.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = WHITE
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if shade_header:
            _shade_cell(cell, '1A237E')

    # Data rows
    for ri, row_data in enumerate(rows):
        row = table.rows[ri + 1]
        for ci, val in enumerate(row_data):
            cell = row.cells[ci]
            cell.text = str(val)
            cell.paragraphs[0].runs[0].font.size = Pt(11)
            if ri % 2 == 1:
                _shade_cell(cell, 'ECEFF1')

    # Column widths
    if col_widths:
        for ri2 in range(len(table.rows)):
            for ci2, w in enumerate(col_widths):
                table.rows[ri2].cells[ci2].width = Inches(w)

    doc.add_paragraph()  # spacing after table
    return table


def _shade_cell(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_toc(doc):
    """Insert a Word TOC field."""
    p = doc.add_paragraph()
    run = p.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)
    p2 = doc.add_paragraph()
    p2.add_run('(Update this field in Microsoft Word: right-click → Update Field)').font.italic = True
    return p


def add_header_footer(doc, title_short='Explicite AI – Final Project Report'):
    for section in doc.sections:
        # Header
        hdr = section.header
        hdr.paragraphs[0].text = title_short
        hdr.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hdr.paragraphs[0].runs[0].font.size = Pt(9)
        hdr.paragraphs[0].runs[0].font.color.rgb = DGREY
        # Footer with page number
        ftr = section.footer
        fp = ftr.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = fp.add_run()
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.text = 'PAGE'
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run.font.size = Pt(10)
