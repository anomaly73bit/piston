#!/usr/bin/env python3
"""Audit non bloccante della tracciabilita delle fonti nel catalogo Piston.

Uso: python tools/audit_fonti.py
Non certifica la veridicita dei dati: elenca le schede da verificare.
"""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "_data" / "motori.yml"
raw = path.read_text(encoding="utf-8")
items = yaml.safe_load(raw)
blocks = re.split(r"(?m)^- slug:\s*", raw)[1:]
missing_sources = []
missing_photos = []
incomplete_sources = []
for block in blocks:
    slug = block.splitlines()[0].strip().strip('"').strip("'")
    if not re.search(r"(?m)^# Fonti?:\s*https?://", block):
        missing_sources.append(slug)
    if not re.search(r"(?m)^  foto:\s*$", block):
        missing_photos.append(slug)
    if re.search(r"(?m)^# Fonti?:", block) and not re.search(r"https?://", block):
        incomplete_sources.append(slug)
print(f"Motori: {len(items)}")
print(f"Schede senza fonti URL esplicite nel YAML: {len(missing_sources)}")
print(f"Schede senza fotografia dichiarata: {len(missing_photos)}")
print(f"Commenti fonti senza URL: {len(incomplete_sources)}")
for label, values in [("DA DOCUMENTARE", missing_sources), ("FOTO ASSENTE", missing_photos)]:
    if values:
        print(f"\n{label}:")
        for slug in values:
            print(f" - {slug}")
print("\nNOTA: una URL non prova che i dati siano corretti. Serve verifica umana delle fonti, versioni e licenze.")
