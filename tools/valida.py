#!/usr/bin/env python3
"""Controlla _data/motori.yml prima della pubblicazione. Esce con codice 1 se trova errori."""
import pathlib
import sys

import yaml

RADICE = pathlib.Path(__file__).resolve().parent.parent
OBBLIGATORI = ["slug", "codice", "nome", "costruttore", "paese", "inizio", "architettura", "cilindri",
               "alimentazione", "aspirazione", "cilindrata", "compressione", "distribuzione", "valvole",
               "blocco", "testa", "iniezione", "cv_min", "cv_max", "nm_max", "limitatore", "in_breve",
               "versioni", "modelli", "storia", "punti_deboli", "limiti", "curiosita"]
ARCHITETTURE = {a["id"] for a in yaml.safe_load((RADICE / "_data/architetture.yml").read_text(encoding="utf-8"))}


def main() -> int:
    motori = yaml.safe_load((RADICE / "_data/motori.yml").read_text(encoding="utf-8"))
    errori = []
    visti = set()
    for i, m in enumerate(motori):
        nome = m.get("slug", f"voce {i + 1}")
        for k in OBBLIGATORI:
            if k not in m or m[k] in (None, "", []):
                errori.append(f"{nome}: manca '{k}'")
        if nome in visti:
            errori.append(f"{nome}: slug duplicato")
        visti.add(nome)
        if m.get("architettura") not in ARCHITETTURE:
            errori.append(f"{nome}: architettura '{m.get('architettura')}' non presente in _data/architetture.yml")
        if str(m.get("architettura", "")).startswith(("V", "W")) and not m.get("angolo"):
            errori.append(f"{nome}: manca 'angolo' tra le bancate")
        if m.get("architettura") != "Rotativo" and not (m.get("alesaggio") and m.get("corsa")):
            errori.append(f"{nome}: mancano alesaggio o corsa")
        if m.get("fine") and m.get("inizio") and m["fine"] < m["inizio"]:
            errori.append(f"{nome}: anno di fine precedente all'inizio")
        if isinstance(m.get("cv_min"), int) and isinstance(m.get("cv_max"), int) and m["cv_min"] > m["cv_max"]:
            errori.append(f"{nome}: cv_min maggiore di cv_max")
        if len(m.get("in_breve") or []) != 3:
            errori.append(f"{nome}: 'in_breve' deve avere esattamente 3 voci")
        for r in m.get("in_breve") or []:
            if not isinstance(r, dict) or not r.get("valore") or not r.get("testo"):
                errori.append(f"{nome}: voce di 'in_breve' senza valore o testo")
        for v in m.get("versioni") or []:
            if not isinstance(v, dict) or not v.get("nome") or "cv" not in v:
                errori.append(f"{nome}: versione incompleta {v}")
        for k in ("punti_deboli", "curiosita"):
            for x in m.get(k) or []:
                if not isinstance(x, str):
                    errori.append(f"{nome}: voce di '{k}' letta come dizionario (mettere il testo tra virgolette): {x}")
        f = m.get("foto")
        if f is not None:
            if not isinstance(f, dict) or not all(f.get(k) for k in ("url", "pagina", "autore", "licenza")):
                errori.append(f"{nome}: 'foto' deve avere url, pagina, autore e licenza")
            elif not str(f["url"]).startswith("https://upload.wikimedia.org/"):
                errori.append(f"{nome}: la foto deve venire da upload.wikimedia.org")
            elif not str(f["pagina"]).startswith("https://commons.wikimedia.org/wiki/File:"):
                errori.append(f"{nome}: 'pagina' deve essere la pagina del file su Wikimedia Commons")
        for k in ("storia", "limiti"):
            if not isinstance(m.get(k), str):
                errori.append(f"{nome}: '{k}' deve essere testo")
    pagine = {p.stem for p in (RADICE / "_motori").glob("*.md")}
    for s in visti - pagine:
        errori.append(f"{s}: manca la pagina in _motori/ (lanciare tools/genera_pagine.py)")
    if errori:
        print("\n".join(errori))
        print(f"\n{len(errori)} errori")
        return 1
    print(f"OK: {len(motori)} motori validi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
