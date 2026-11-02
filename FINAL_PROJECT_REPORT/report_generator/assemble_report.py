"""Assemble the complete Explicite AI Final Project Report."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from styles import new_document, add_header_footer, page_break
from front_matter import build_front_matter
from chapters_01_05 import build_chapters_01_05
from chapters_06_09 import build_chapters_06_09
from chapters_10_14 import build_chapters_10_14
from references import build_references

OUT_DIR = Path(__file__).parent.parent
DOCX_PATH = OUT_DIR / 'Explicite_AI_Final_Project_Report.docx'


def assemble():
    print("Assembling Explicite AI Final Project Report...")
    doc = new_document()

    print("  [1/6] Front matter...")
    build_front_matter(doc)

    print("  [2/6] Chapters 1–5...")
    build_chapters_01_05(doc)

    print("  [3/6] Chapters 6–9...")
    build_chapters_06_09(doc)

    print("  [4/6] Chapters 10–14...")
    build_chapters_10_14(doc)

    print("  [5/6] References and Appendices...")
    build_references(doc)

    print("  [6/6] Header/footer...")
    add_header_footer(doc)

    print(f"\nSaving to {DOCX_PATH}...")
    doc.save(str(DOCX_PATH))
    print(f"Done. File size: {DOCX_PATH.stat().st_size / 1024:.1f} KB")
    return DOCX_PATH


def try_pdf_export(docx_path: Path):
    """Attempt to convert DOCX to PDF using LibreOffice."""
    import subprocess, shutil
    out_dir = docx_path.parent

    # Try LibreOffice
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    if soffice:
        try:
            result = subprocess.run(
                [soffice, '--headless', '--convert-to', 'pdf',
                 '--outdir', str(out_dir), str(docx_path)],
                capture_output=True, text=True, timeout=120
            )
            pdf_path = out_dir / (docx_path.stem + '.pdf')
            if pdf_path.exists():
                print(f"PDF exported: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
                return pdf_path
        except Exception as e:
            print(f"LibreOffice export failed: {e}")

    # Try docx2pdf
    try:
        from docx2pdf import convert
        pdf_path = out_dir / (docx_path.stem + '.pdf')
        convert(str(docx_path), str(pdf_path))
        if pdf_path.exists():
            print(f"PDF exported via docx2pdf: {pdf_path}")
            return pdf_path
    except ImportError:
        pass
    except Exception as e:
        print(f"docx2pdf failed: {e}")

    print("PDF export unavailable — open DOCX in Microsoft Word and use File > Save As > PDF.")
    return None


if __name__ == '__main__':
    docx = assemble()
    try_pdf_export(docx)
    print("\nReport generation complete.")
    print(f"  DOCX: {docx}")
