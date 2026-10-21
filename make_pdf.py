"""Print the executed notebook HTML to PDF with headless Chrome.

    python make_pdf.py ZIKV_DockingScoring.html
"""
import subprocess
import sys
from pathlib import Path

PRINT_CSS = """<style>
@page { size: A4 landscape; margin: 10mm; }
@media print {
  pre, .jp-RenderedText pre, .highlight pre { white-space: pre-wrap !important; word-break: break-word; }
  .jp-Cell, .jp-OutputArea-child, img, [id^="3dmolviewer"] { break-inside: avoid; }
  .jp-OutputArea-output { overflow: visible !important; }
  .jp-RenderedHTMLCommon table { font-size: 8px !important; table-layout: auto; }
  .jp-RenderedHTMLCommon th, .jp-RenderedHTMLCommon td { padding: 2px 4px !important; }
  .jp-RenderedHTMLCommon thead th { white-space: normal; word-break: break-word; }
  .jp-RenderedMarkdown img { max-width: 100%; height: auto; }
}
</style>
</head>"""
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

src = Path(sys.argv[1] if len(sys.argv) > 1 else "ZIKV_DockingScoring.html").resolve()
out = src.with_suffix(".pdf")
tmp = src.with_name(f".print_{src.name}")
body = src.read_text()
assert "</head>" in body, "no </head> in the HTML"
tmp.write_text(body.replace("</head>", PRINT_CSS, 1))
try:
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=60000", f"--print-to-pdf={out}", tmp.as_uri()],
                   check=True, capture_output=True)
finally:
    tmp.unlink(missing_ok=True)
print("PDF written", out, out.stat().st_size // 1024, "KB")
