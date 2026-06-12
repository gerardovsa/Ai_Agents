"""Row 52 classifier: for each root non-.md file, decide archive vs keep.
Heuristic: extension + filename pattern + reference count.
- .ps1/.bat: archive unless load-bearing launcher (BISTART/BISTOP/CHAT/CHATM/OPEN_APP)
- .js: archive unless load-bearing (console_inspector.js, etc.)
- .html: archive all (test pages)
- .txt: archive all one-shots (output files, demos, ref cards)
- .sh: archive unless load-bearing (startup.sh)
- .css: archive all (TEMP_OLD_ and temp_ prefixes)
- .svg: archive (one-shot diagram)
- .csv: archive (one-shot data export)
- .yaml/.yml: archive unless load-bearing (render.yaml, docker-compose.yml)
"""
import csv
import os
import re
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents")
INV = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row52_inventory.csv")
OUT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row52_classification.csv")
OUT_SUMMARY = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row52_summary.txt")

# Target dirs (per row 50/51 precedent)
TGT_TIMELINES = "archive/timelines_and_reports/"
TGT_SCRIPTS = "archive/root_scripts_row52/"  # new subdir for this row's scripts

# Load-bearing names that override the auto-classification
KEEP = {
    # .ps1 launchers
    "BISTART.ps1", "BISTOP.ps1", "CHATM.ps1",
    # .bat launchers
    "BISTART.bat", "BISTOP.bat", "CHAT.bat", "CHATM.bat", "OPEN_APP.bat",
    # .js package.json mains
    "console_inspector.js", "ui-command-processor.js", "cad-chat-renderer.js",
    # .sh
    "startup.sh",
    # .yaml/.yml
    "render.yaml", "docker-compose.yml",
    # side-project
    "synergy_requirements.txt",
}

# Archive (always, even if 0 refs)
ARCHIVE_ALWAYS = {
    # .css: TEMP_OLD_ and temp_ prefixes
    "TEMP_OLD_inhouse-kanban.css", "temp_synergy_styles.css",
    # .svg
    "architecture_diagram_content_blocks.svg",
    # .csv
    "thread_locations_export.csv",
    # .yaml dead
    "render-docker.yaml", "render-v10.yaml", "render_cleaned.yaml",
    # .txt dead
    "requirements_text_extraction.txt",
}

rows = []
with INV.open("r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        fn, ext = r["filename"], r["ext"]
        size = int(r["size_bytes"])

        if fn in KEEP:
            rows.append({"filename": fn, "ext": ext, "size": size, "bucket": "Keep", "action": "keep", "reason": "load-bearing"})
            continue

        if fn in ARCHIVE_ALWAYS:
            target = TGT_TIMELINES
            rows.append({"filename": fn, "ext": ext, "size": size, "bucket": "Archive", "action": f"git mv -> {target}", "reason": "always-archive (prefix: TEMP_OLD/temp_/dead variant)"})
            continue

        # Default: archive all one-shots
        # .ps1, .bat, .sh, .js, .html, .txt, .css, .svg, .csv, .yaml, .yml
        if ext in (".ps1", ".bat", ".sh", ".js", ".html", ".txt", ".css", ".svg", ".csv", ".yaml", ".yml"):
            target = TGT_TIMELINES
            reason = f"one-shot {ext} (0 live refs)"
            rows.append({"filename": fn, "ext": ext, "size": size, "bucket": "Archive", "action": f"git mv -> {target}", "reason": reason})
        else:
            rows.append({"filename": fn, "ext": ext, "size": size, "bucket": "Unknown", "action": "review", "reason": "unhandled ext"})

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["filename", "ext", "size", "bucket", "action", "reason"])
    w.writeheader()
    for r in rows:
        w.writerow(r)

counts = Counter((r["bucket"], r["ext"]) for r in rows)
sizes = {}
for r in rows:
    key = (r["bucket"], r["ext"])
    sizes[key] = sizes.get(key, 0) + r["size"]

with OUT_SUMMARY.open("w", encoding="utf-8") as f:
    f.write("Row 52 classification summary\n" + "=" * 60 + "\n\n")
    f.write(f"Total files: {len(rows)}\n\n")
    f.write("By bucket + ext:\n")
    for (b, e), c in sorted(counts.items()):
        f.write(f"  {b:10} {e:6} {c:5} files  ({sizes.get((b,e), 0):>12,} bytes)\n")
    f.write("\nFiles to KEEP at root:\n")
    for r in rows:
        if r["bucket"] == "Keep":
            f.write(f"  {r['filename']}\n")
    f.write("\nFiles to ARCHIVE:\n")
    for r in rows:
        if r["bucket"] == "Archive":
            f.write(f"  {r['ext']:6} {r['filename']}\n")

print(f"Total: {len(rows)} files")
for b in ("Keep", "Archive", "Unknown"):
    c = sum(1 for r in rows if r["bucket"] == b)
    print(f"  {b:10} {c:5} files")
print(f"Wrote {OUT}")
print(f"Wrote {OUT_SUMMARY}")
