#!/usr/bin/env python3
"""Audit EN/FR/CS coverage against the canonical Italian catalogue."""
import json
import pathlib
import sys
import subprocess
import yaml

from traduci import source_data, fingerprint, is_complete

ROOT = pathlib.Path(__file__).resolve().parent.parent
motori = yaml.safe_load((ROOT / "_data/motori.yml").read_text(encoding="utf-8"))
if "--new-only" in sys.argv:
    try:
        previous = yaml.safe_load(subprocess.check_output(
            ["git", "show", "HEAD^:_data/motori.yml"], cwd=ROOT, text=True
        ))
    except Exception as exc:
        print(f"Cannot verify newly added engines against parent commit: {exc}", file=sys.stderr)
        sys.exit(1)
    previous_slugs = {m["slug"] for m in previous}
    motori = [m for m in motori if m["slug"] not in previous_slugs]
    print(f"New engine families in this commit: {len(motori)}")
total = len(motori)
all_complete = True
for language in ("en", "fr", "cs"):
    path = ROOT / "_data" / "traduzioni" / (language + ".json")
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    complete = 0
    missing = []
    for m in motori:
        src = source_data(m)
        tr = data.get(m["slug"], {})
        if tr.get("_source_hash") == fingerprint(src) and is_complete(src, tr):
            complete += 1
        else:
            missing.append(m["slug"])
    print(f"{language}: {complete}/{total} engine articles fully translated")
    if missing:
        print("  First missing:", ", ".join(missing[:8]))
        all_complete = False
if ("--strict" in sys.argv or "--new-only" in sys.argv) and not all_complete:
    sys.exit(1)
