"""Execute the notebook and write a static HTML copy of the run.

    python build_report.py [suffix]

nbconvert --execute stalls on the ipywidgets Output cells, so this drives a
kernel cell by cell instead. Set DOCKING_FLEXIBLE=<distance> for a flexible run.
"""
import os
import sys
from pathlib import Path

import jupyter_client
import nbformat
from nbconvert import HTMLExporter

HERE = Path(__file__).resolve().parent
NB = HERE / "ZIKV_DockingScoring.ipynb"
suffix = sys.argv[1] if len(sys.argv) > 1 else ""

nb = nbformat.read(NB, as_version=4)
km = jupyter_client.KernelManager(kernel_name="docking_scoring")
km.start_kernel(cwd=str(HERE), env={**os.environ, "DOCKING_AUTORUN": "1"})
kc = km.client()
kc.start_channels()
kc.wait_for_ready(timeout=120)

WIDGET = "application/vnd.jupyter.widget-view+json"
try:
    for n, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        msg_id = kc.execute(cell.source)
        outputs = []
        while True:
            msg = kc.get_iopub_msg(timeout=7200)
            if msg["parent_header"].get("msg_id") != msg_id:
                continue
            t, c = msg["msg_type"], msg["content"]
            if t == "status" and c["execution_state"] == "idle":
                break
            if t == "execute_input":
                cell.execution_count = c["execution_count"]
            elif t in ("display_data", "execute_result"):
                if WIDGET in c["data"]:
                    continue
                outputs.append(nbformat.v4.output_from_msg(msg))
            elif t in ("stream", "error"):
                outputs.append(nbformat.v4.output_from_msg(msg))
                if t == "error":
                    print(f"cell {n}: {c['ename']}: {c['evalue']}", file=sys.stderr)
        cell.outputs = outputs
        print(f"cell {n} done ({len(outputs)} outputs)", flush=True)
finally:
    kc.stop_channels()
    km.shutdown_kernel(now=True)

nb.metadata.pop("widgets", None)
body, _ = HTMLExporter().from_notebook_node(nb)
body = body.replace(str(HERE) + "/", "")
out = HERE / f"{NB.stem}{suffix}.html"
out.write_text(body)
print("HTML written", out, len(body) // 1024, "KB")
