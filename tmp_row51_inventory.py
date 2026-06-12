"""Row 51 inventory builder: walks all 1,236 root .md files and captures
filename, size, last-modified, and first 2 lines (title) into a CSV.
Used to build the per-file classification table per CLAUDE.md §16.3."""
import os
import csv
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents")
OUT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row51_inventory.csv")

files = sorted([p for p in ROOT.glob("*.md") if p.is_file()])
print(f"Found {len(files)} root .md files", flush=True)

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename", "size_bytes", "mtime", "first_line", "second_line"])
    for p in files:
        try:
            stat = p.stat()
            with p.open("r", encoding="utf-8", errors="replace") as fp:
                lines = fp.readlines()
            l1 = lines[0].rstrip() if len(lines) > 0 else ""
            l2 = lines[1].rstrip() if len(lines) > 1 else ""
            w.writerow([p.name, stat.st_size, stat.st_mtime, l1[:200], l2[:200]])
        except Exception as e:
            w.writerow([p.name, 0, 0, f"ERR: {e}", ""])

print(f"Wrote {OUT}", flush=True)
