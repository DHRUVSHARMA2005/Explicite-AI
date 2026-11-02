# Formatting QA Report — Explicite AI Final Report (Repaired)

**Date:** 2026-11-02  
**Files:** `Explicite_AI_Final_Report_Repaired.docx` (1,450 KB), `Explicite_AI_Final_Report_Repaired.pdf` (1,554 KB)  
**Page count:** 48 pages (target: 45–50)  
**QA method:** PDF rendered to PNG using PyMuPDF at 1.5× scale; every section visually inspected.

---

## 1. Root Causes of Original Formatting Failures

### 1.1 Images Rendering as Thin Strips (CRITICAL — Fixed)

All matplotlib charts, diagrams, and screenshots were rendering as 0.25 inch (18pt) horizontal strips.

**Root cause:** The Normal paragraph style was set with `w:lineRule="exact"` and `w:line="360"` (exact 18pt line spacing). Word's "exact line spacing" mode clips content in a paragraph — including embedded images — to the specified line height, regardless of the image's actual dimensions. Although the DOCX XML correctly stored EMU dimensions for each image (e.g., diag01 at 5,669,280 × 3,287,268 EMU = 6.2 × 3.6 inches), Word rendered each image paragraph as a single 18pt line.

**Fix applied:** Added explicit `w:spacing w:line="240" w:lineRule="auto"` to every image paragraph's `<w:pPr>` element via python-docx XML manipulation, overriding the inherited exact line spacing.

### 1.2 Charts and Diagrams Saving as RGBA PNG (CRITICAL — Fixed)

Matplotlib saves figures with RGBA colour mode even when the background is opaque white. Word's COM-based PDF export (`ExportAsFixedFormat`) cannot render RGBA PNG images; they appear as empty or black regions in the exported PDF.

**Fix applied:** All 10 matplotlib assets (7 charts + 3 diagrams) were regenerated with:
- `facecolor='white'` on the figure
- Post-generation compositing: RGBA → RGB by pasting onto a white `Image.new('RGB', ...)` using the alpha channel as a mask
- Saved at 150 DPI with `dpi=(150, 150)`

### 1.3 Dark Backgrounds on Charts/Diagrams (Fixed)

Original charts used `facecolor='#0D1117'` (near-black) matching the Explicite Midnight UI. On printed white paper these appeared as black rectangles.

**Fix applied:** `regenerate_white_bg.py` regenerated all assets with white figure backgrounds (`BG = "white"`, `AX_BG = "#F8F9FA"`), dark text (`TEXT_C = "#1C2128"`), and light grid lines (`GRID_C = "#D0D7DE"`). Colour accents adjusted for readability on white (e.g., `BLUE="#0969DA"`, `GREEN="#2DA44E"`).

### 1.4 Code Blocks Using Justify Alignment (Fixed)

Code block paragraphs inherited `WD_ALIGN_PARAGRAPH.JUSTIFY` from the Normal style, causing monospace tokens to be spaced out across the full line width.

**Fix applied:** Added `p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT` explicitly in the `code()` function.

### 1.5 List of Figures/Tables Missing Dot-Leader Tab Stops (Fixed)

The LOF and LOT entries had their page numbers appearing inline after the title rather than right-aligned with dot leaders.

**Fix applied:** Each LOF/LOT paragraph received explicit XML tab stop elements:
```xml
<w:tab w:val="right" w:pos="7920" w:leader="dot"/>
```
(7920 twips = 5.5 inches from left margin)

### 1.6 Screenshots Missing DPI Metadata (Fixed)

Playwright screenshots had no `pHYs` chunk (DPI metadata). Without explicit height in `add_picture`, python-docx defaulted to 72 DPI for height calculation. Fix: explicit height computation from pixel dimensions and 96 DPI set via PIL.

---

## 2. Final QA Validation Results

All pages were rendered from the PDF at 1.5× scale and inspected visually.

### 2.1 Front Matter (Pages 1–9)

| Page | Content | Status |
|------|---------|--------|
| 1 | Cover page: title, authors, institution, academic year | ✅ Pass |
| 2 | Declaration with signature lines | ✅ Pass |
| 3 | Abstract | ✅ Pass |
| 4–5 | Table of Contents with dot-leader tab stops | ✅ Pass |
| 6 | List of Figures — 15 entries, correct dot leaders, page numbers updated | ✅ Pass |
| 7 | List of Tables — 8 entries, correct dot leaders, page numbers updated | ✅ Pass |
| 8 | List of Abbreviations | ✅ Pass |
| 9 | Chapter 1: Introduction | ✅ Pass |

### 2.2 Diagrams (Pages 17–23)

| Figure | Description | Status |
|--------|-------------|--------|
| System Architecture | All 4 layers visible: Frontend SPA, FastAPI, Services, Infrastructure | ✅ Pass |
| Analysis Workflow | 8-stage pipeline + post-analysis AI features clearly labelled | ✅ Pass |
| ER Diagram | All entities and relationships visible | ✅ Pass |

**Layout:** All 3 diagrams at 5.0-inch width render at correct aspect ratios with white backgrounds. No black strips or clipped content.

### 2.3 Code Blocks (Pages 25–29)

All code blocks use:
- Courier New monospace font
- `LEFT` alignment (no justification spreading)
- Light grey background (`#F6F8FA`)
- 0.4-inch left indent

Inspected code samples: CVSS v3.1 scoring formula, technical debt weights, OllamaProvider class. All render correctly with preserved indentation. ✅ Pass

### 2.4 Application Screenshots (Pages 28–33)

All 8 screenshots captured from live application at 1440×900 resolution, stored as RGB PNG at 96 DPI, displayed at 4.2-inch width (2.625-inch height, 1.6:1 aspect ratio preserved).

| Figure | Screen | Status |
|--------|--------|--------|
| 1 | Login Screen | ✅ Pass — dark UI visible, form elements readable |
| 2 | Main Dashboard | ✅ Pass — project table with quality gates visible |
| 3 | Projects Screen | ✅ Pass — sidebar navigation visible |
| 4 | Code Analysis with History | ✅ Pass — analysis jobs table visible |
| 5 | Findings Screen | ✅ Pass — vulnerability list with severity badges |
| 6 | AI Assistant | ✅ Pass — chat interface with suggested questions |
| 7 | Learning Screen | ✅ Pass — course list with progress indicators |
| 8 | Settings Screen | ✅ Pass — profile form with theme controls |

### 2.5 Charts and Analytical Visualisations (Pages 36–40)

All 7 charts regenerated with white backgrounds, RGB mode, 150 DPI, readable labels.

| Figure | Chart Type | Status |
|--------|------------|--------|
| 9 | Project Module Distribution (horizontal bar) | ✅ Pass |
| 10 | Test Suite Results 426/427 (pie chart) | ✅ Pass |
| 11 | Feature Implementation Status 30 features (pie chart) | ✅ Pass |
| 12 | Vulnerability Severity Distribution (bar) | ✅ Pass |
| 13 | Competitor Feature Comparison Matrix (heatmap) | ✅ Pass |
| 14 | Technology Stack — Files per Layer (horizontal bar) | ✅ Pass |
| 15 | SDG Contribution Count (bar) | ✅ Pass |

### 2.6 Tables

All 8 tables inspected: dark navy header rows, alternating white/light-blue rows, correct column widths, no overflow. ✅ Pass

### 2.7 Headers and Footers

- Running header: *"Explicite AI — AI-Powered Code Review and Learning Platform"* (centred, small blue italic) — verified present on all content pages.
- Running footer: *"CBS3011 Usability Design of Software Applications — VIT Vellore, 2026–2027 | Page N"* — verified present on all content pages.
- First section page (cover) shows header/footer — acceptable for this document type. ✅ Pass

### 2.8 Typography and Layout

| Element | Specification | Observed |
|---------|--------------|---------|
| Body font | Times New Roman 12pt | ✅ Correct |
| Chapter headings | Times New Roman 16pt bold navy | ✅ Correct |
| Section headings | Times New Roman 13pt bold blue | ✅ Correct |
| Code font | Courier New 10pt | ✅ Correct |
| Line spacing | 18pt exact (body) | ✅ Correct |
| Margins | 0.9 inch all sides | ✅ Correct |
| Page size | A4 (21 × 29.7 cm) | ✅ Correct |

---

## 3. Known Limitations

- **TOC page numbers:** The Table of Contents contains static page numbers that were updated to match the current 48-page layout. Word's auto-updating TOC field is not used (python-docx does not support it); the user should right-click the TOC in Word and choose "Update Field → Update entire table" before final submission if any further edits are made.

- **Screenshot readability:** Screenshots are displayed at 4.2 × 2.625 inches. Fine UI text (table cell values, small labels) may be difficult to read at this scale in print. The images are correct and unaltered; this is a consequence of fitting all content into the 45–50 page target.

- **Pie chart label overlap:** The test suite pie chart (Figure 10) has minor label overlap between "Skipped (1)" and "0.2%" due to the very small segment. This is accurate data; the underlying numbers are verifiable from the pytest output.

---

## 4. Files Delivered

| File | Size | Description |
|------|------|-------------|
| `Explicite_AI_Final_Report_Repaired.docx` | 1,450 KB | Repaired Word document |
| `Explicite_AI_Final_Report_Repaired.pdf` | 1,554 KB | PDF exported via Word COM |
| `Formatting_QA_Report.md` | — | This QA report |
| `Report_Assets/*.png` | — | 10 regenerated assets (RGB, white bg, 150 DPI) |
| `regenerate_white_bg.py` | — | Script used to regenerate all chart/diagram assets |

---

*QA conducted by automated PDF-to-PNG rendering (PyMuPDF) and visual inspection. No fabricated data, benchmark numbers, or compliance claims were introduced during the repair process.*
