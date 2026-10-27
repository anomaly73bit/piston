#!/usr/bin/env python3
"""Cerca su Wikimedia Commons una foto con licenza libera per ogni motore senza foto.

Gira su GitHub Actions (non consuma la quota di Claude). Scrive _data/foto.yml:

    toyota-2jz-gte:
      url: https://upload.wikimedia.org/.../800px-....jpg
      pagina: https://commons.wikimedia.org/wiki/File:....jpg
      autore: Nome
      licenza: CC BY-SA 4.0
      titolo: File:....jpg

Regole prudenti, per evitare foto sbagliate:
- il titolo del file deve contenere il codice del motore (es. "2JZ", "EA888", "M156");
- solo licenze libere: CC0, pubblico dominio, CC BY, CC BY-SA (no NC, no ND);
- solo fotografie JPEG/PNG; preferite quelle con "engine", "motor", "moteur" nel titolo.
Un motore senza foto adatta resta senza: meglio nessuna foto che quella sbagliata.
I motori con un campo `foto` scritto a mano in _data/motori.yml non vengono toccati.

Uso: python3 tools/foto.py [--max N]
"""
import html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

import yaml

RADICE = pathlib.Path(__file__).resolve().parent.parent
USCITA = RADICE / "_data" / "foto.yml"
API = "https://commons.wikimedia.org/w/api.php"
UA = "PistonEngineEncyclopedia/1.0 (https://piston.pacificit.solutions; info@pacificit.solutions)"
PAROLE_MOTORE = ("engine", "motor", "moteur", "motore", "triebwerk")
ESCLUSE = ("diagram", "drawing", "logo", "badge", "emblem", "schema", "cutaway", "brochure")


def api(**params):
    params.update(format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 + tentativo * 3)
    return {}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def codici(m):
    """Codici motore distintivi: almeno 3 caratteri con lettere e cifre (2JZ-GTE, EA888, M156...)."""
    testo = f"{m.get('codice', '')} {m.get('nome', '')}"
    out = []
    for tok in re.split(r"[\s/,()+]+", testo):
        t = tok.strip(" .'\"")
        if re.fullmatch(r"\d+[vV]", t):          # numero di valvole (16V), non un codice motore
            continue
        if len(norm(t)) >= 3 and re.search(r"\d", t) and re.search(r"[A-Za-z]", t):
            varianti = [t, t.split("-")[0], re.sub(r"T$", "", t.split("-")[0])]
            for v in varianti:
                if len(norm(v)) >= 3 and re.search(r"\d", v) and re.search(r"[A-Za-z]", v) \
                        and norm(v) not in [norm(x) for x in out]:
                    out.append(v)
    return out


def licenza_ok(lic):
    l = lic.lower().replace("-", " ")
    if "nc" in l.split() or "nd" in l.split() or "noncommercial" in l or "no derivatives" in l:
        return False
    return l.startswith(("cc0", "public domain", "pd", "cc by", "cc by sa"))


def pulisci(s):
    s = re.sub(r"<[^>]+>", "", html.unescape(s or "")).strip()
    return re.sub(r"\s+", " ", s)[:120]


def cerca(m):
    for cod in codici(m):
        ris = api(action="query", list="search", srsearch=f'"{cod}" engine', srnamespace=6, srlimit=20)
        titoli = [x["title"] for x in ris.get("query", {}).get("search", [])]
        candidati = [t for t in titoli
                     if norm(cod) in norm(t)
                     and t.lower().endswith((".jpg", ".jpeg", ".png"))
                     and not any(e in t.lower() for e in ESCLUSE)]
        if not candidati:
            continue
        info = api(action="query", titles="|".join(candidati[:10]), prop="imageinfo",
                   iiprop="url|extmetadata|mime", iiurlwidth=800)
        pagine = info.get("query", {}).get("pages", [])
        migliori = []
        for p in pagine:
            ii = (p.get("imageinfo") or [{}])[0]
            meta = ii.get("extmetadata", {})
            lic = pulisci(meta.get("LicenseShortName", {}).get("value", ""))
            if not licenza_ok(lic) or not ii.get("thumburl"):
                continue
            if ii.get("width", 0) and ii.get("width") < 640:
                continue
            punteggio = 2 if any(w in p["title"].lower() for w in PAROLE_MOTORE) else 0
            punteggio += 1 if norm(m["costruttore"].split()[0]) in norm(p["title"]) else 0
            migliori.append((punteggio, p["title"], ii, lic, meta))
        if migliori:
            migliori.sort(key=lambda x: -x[0])
            _, titolo, ii, lic, meta = migliori[0]
            return {
                "url": ii["thumburl"],
                "pagina": ii.get("descriptionurl") or ("https://commons.wikimedia.org/wiki/" + urllib.parse.quote(titolo.replace(" ", "_"))),
                "autore": pulisci(meta.get("Artist", {}).get("value", "")) or "Autore indicato su Wikimedia Commons",
                "licenza": lic,
                "titolo": titolo,
            }
    return None


def main():
    massimo = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 400
    motori = yaml.safe_load((RADICE / "_data" / "motori.yml").read_text(encoding="utf-8"))
    foto = yaml.safe_load(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    foto = foto or {}
    provati = foto.pop("_provati", {}) or {}
    nuove = 0
    controllati = 0
    for m in motori:
        slug = m["slug"]
        if m.get("foto") or slug in foto:
            continue
        # i motori già cercati senza risultato si riprovano ogni 30 giorni
        if provati.get(slug, 0) > time.time() - 30 * 86400:
            continue
        if controllati >= massimo:
            break
        controllati += 1
        trovata = cerca(m)
        if trovata:
            foto[slug] = trovata
            nuove += 1
            print(f"+ {slug}: {trovata['titolo']} ({trovata['licenza']})")
        else:
            provati[slug] = int(time.time())
        time.sleep(0.5)
    foto["_provati"] = provati
    USCITA.write_text(
        "# Foto trovate automaticamente su Wikimedia Commons da tools/foto.py. Una voce si può correggere o cancellare a mano.\n"
        + yaml.safe_dump(foto, allow_unicode=True, sort_keys=True, width=1000),
        encoding="utf-8")
    con_foto = sum(1 for m in motori if m.get("foto") or m["slug"] in foto)
    print(f"{nuove} foto nuove su {controllati} motori controllati; {con_foto}/{len(motori)} schede con foto")


if __name__ == "__main__":
    main()
