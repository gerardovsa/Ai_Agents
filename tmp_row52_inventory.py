"""Row 52 inventory: walks all 141 root files (non-.md) and captures
filename, size, mtime, and a classification hint based on extension + name."""
import os
import csv
from pathlib import Path

ROOT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents")
OUT = Path(r"C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\tmp_row52_inventory.csv")

KEEP_NAMES = {
    "Dockerfile", "docker-compose.yml",
    "package.json", "package-lock.json", "requirements.txt", "runtime.txt", ".env.example",
    "render.yaml",
    "startup.sh",
    "config.example.py", "get_supabase_credentials.py",
    "console_inspector.js", "ui-command-processor.js", "cad-chat-renderer.js",
    "BISTART.bat", "BISTOP.bat", "CHAT.bat", "CHATM.bat", "OPEN_APP.bat",
    "BISTART.ps1", "BISTOP.ps1", "CHATM.ps1",
    "chat.ps1",  # called by CHAT.bat
    "calculator_test_dashboard.html",  # opened by main SPA
    "synergy_requirements.txt",
    "tmp_row51_inventory.py", "tmp_row51_inventory.csv", "tmp_row51_classify.py",
    "tmp_row51_classification.csv", "tmp_row51_summary.txt", "tmp_row51_moves.csv",
    "tmp_row51_batches.sh",
}

AUDIT_EXTS = {".ps1", ".bat", ".sh", ".js", ".html", ".txt", ".css", ".svg", ".csv",
              ".yaml", ".yml"}

files = []
for p in sorted(ROOT.iterdir()):
    if not p.is_file():
        continue
    if p.name in KEEP_NAMES:
        continue
    ext = p.suffix.lower()
    if ext not in AUDIT_EXTS:
        continue
    stat = p.stat()
    files.append((p.name, stat.st_size, stat.st_mtime, ext))

print(f"Files to classify: {len(files)}")

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename", "ext", "size_bytes", "mtime"])
    for fn, sz, mt, ext in files:
        w.writerow([fn, ext, sz, mt])

print(f"Wrote {OUT}")
