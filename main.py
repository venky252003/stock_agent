import gradio as gr
from dotenv import load_dotenv
from pathlib import Path

from agent.stock_manager_agent import SupervisorManager


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

load_dotenv(override=True)


async def run(query: str):
    manager = SupervisorManager()
    last_chunk = ""
    async for chunk in manager.run(query):
        last_chunk = chunk
        yield chunk, None

    pdf_bytes = markdown_to_pdf_bytes(last_chunk)
    pdf_path = Path("/tmp/report.pdf")
    pdf_path.write_bytes(pdf_bytes)
    yield last_chunk, str(pdf_path)


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# AI Agent Stock Analysist ")
    query_textbox = gr.Textbox(label="Analysis Apple stock")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    download = gr.File(label="Download PDF", visible=False)

    run_button.click(fn=run, inputs=query_textbox, outputs=[report, download])
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=[report, download])

#ui.launch(inbrowser=True)
ui.launch(
    inbrowser=True,
    auth=[("venky", "Venky25")],  # or auth=[("user1", "pass1"), ("user2", "pass2")]
    auth_message="Please log in to use the stock analysis tool"
)
