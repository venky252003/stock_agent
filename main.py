from pathlib import Path
import tempfile
import gradio as gr


def markdown_to_pdf_bytes(markdown_text: str) -> bytes:
    """Convert markdown text to a minimal PDF file."""
    width, height = 595, 842
    margin = 50
    leading = 14
    y = height - margin
    lines = markdown_text.splitlines()
    content_lines = ["BT", "/F1 12 Tf"]
    for line in lines:
        safe = (
            line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        )
        content_lines.append(f"1 0 0 1 {margin} {y} Tm ({safe}) Tj")
        y -= leading
    content_lines.append("ET")
    stream = "\n".join(content_lines)

    objects: list[str] = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append("<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    )
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")

    pdf_lines = ["%PDF-1.4"]
    offsets: list[int] = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len("\n".join(pdf_lines)) + 1)
        pdf_lines.append(f"{i} 0 obj\n{obj}\nendobj")

    xref_offset = len("\n".join(pdf_lines)) + 1
    pdf_lines.append("xref")
    pdf_lines.append(f"0 {len(objects)+1}")
    pdf_lines.append("0000000000 65535 f ")
    for off in offsets:
        pdf_lines.append(f"{off:010d} 00000 n ")
    pdf_lines.append(f"trailer << /Root 1 0 R /Size {len(objects)+1} >>")
    pdf_lines.append("startxref")
    pdf_lines.append(str(xref_offset))
    pdf_lines.append("%%EOF")
    return "\n".join(pdf_lines).encode("latin1", errors="replace")


def save_pdf(markdown_text: str) -> str:
    pdf_bytes = markdown_to_pdf_bytes(markdown_text)
    temp_dir = Path(tempfile.gettempdir())
    pdf_path = temp_dir / "report.pdf"
    pdf_path.write_bytes(pdf_bytes)
    return str(pdf_path)


if __name__ == "__main__":
    import app.main as app_main

    app_main.ui.launch()
