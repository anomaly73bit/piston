#!/usr/bin/env python3
"""Crea una pagina in _motori/ per ogni voce di _data/motori.yml.

Jekyll (anche su GitHub Pages, senza plugin) non genera pagine dai file di dati:
questo script scrive per ogni motore un piccolo file con il solo front matter.
Il contenuto della scheda viene letto dal layout 'motore' direttamente dai dati.

Uso:  python3 tools/genera_pagine.py      (richiede PyYAML: pip install pyyaml)
"""
import pathlib
import sys

import yaml

RADICE = pathlib.Path(__file__).resolve().parent.parent
DATI = RADICE / "_data" / "motori.yml"
USCITA = RADICE / "_motori"


def main() -> int:
    motori = yaml.safe_load(DATI.read_text(encoding="utf-8"))
    slugs = [m["slug"] for m in motori]
    doppi = {s for s in slugs if slugs.count(s) > 1}
    if doppi:
        print("Slug duplicati:", ", ".join(sorted(doppi)))
        return 1

    USCITA.mkdir(exist_ok=True)
    attesi = set()
    for m in motori:
        f = USCITA / f"{m['slug']}.md"
        attesi.add(f.name)
        nome = m["nome"] if str(m["codice"]) in m["nome"] else f"{m['nome']} ({m['codice']})"
        descr = f"{nome}: scheda tecnica, versioni, auto, storia, punti deboli e limiti."
        f.write_text(
            "---\n"
            f"slug: {m['slug']}\n"
            f"title: {yaml.safe_dump(m['nome'], allow_unicode=True).strip().removesuffix('...').strip()}\n"
            f"description: {yaml.safe_dump(descr, allow_unicode=True, width=1000).strip().removesuffix('...').strip()}\n"
            "---\n",
            encoding="utf-8",
        )
    # Rimuove le pagine di motori tolti dal file di dati
    for vecchio in USCITA.glob("*.md"):
        if vecchio.name not in attesi:
            vecchio.unlink()
            print("Rimossa", vecchio.name)
    print(f"{len(motori)} pagine in {USCITA.relative_to(RADICE)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
