#!/usr/bin/env python3
"""Anteprima statica del sito senza Ruby/Jekyll.

Rende i template Liquid con python-liquid imitando i filtri Jekyll usati nel sito
e scrive il risultato in _anteprima/ con link relativi (apribile da qualsiasi cartella).
Serve solo per controllare i template: il sito vero lo costruisce Jekyll / GitHub Pages.

Uso:  pip install python-liquid pyyaml markdown
      python3 tools/anteprima.py
"""
import datetime
import json
import pathlib
import re
import shutil
import unicodedata

import markdown
import yaml
from liquid import DictLoader, Environment

RADICE = pathlib.Path(__file__).resolve().parent.parent
OUT = RADICE / "_anteprima"
FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
INCLUDE = re.compile(r"\{%-?\s*include\s+([\w.\-/]+)((?:\s+\w+=[^\s%]+)*)\s*-?%\}")


def separa(testo):
    m = FM.match(testo)
    if not m:
        return {}, testo
    return yaml.safe_load(m.group(1)) or {}, testo[m.end():]


def converti_include(src):
    """{% include x.html a=b %}  ->  {% include 'x.html', inc_a: b %}"""
    def sost(m):
        args = re.findall(r"(\w+)=([^\s%]+)", m.group(2) or "")
        extra = "".join(f", inc_{k}: {v}" for k, v in args)
        return "{% include '" + m.group(1) + "'" + extra + " %}"
    return INCLUDE.sub(sost, src)


def slugify(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    return re.sub(r"[^\w]+", "-", s).strip("-")


def group_by(items, chiave):
    gruppi = {}
    for it in items:
        gruppi.setdefault(it.get(chiave), []).append(it)
    return [{"name": k, "items": v, "size": len(v)} for k, v in gruppi.items()]


def costruisci():
    config = yaml.safe_load((RADICE / "_config.yml").read_text(encoding="utf-8"))
    site = dict(config)
    site["data"] = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (RADICE / "_data").glob("*.yml")}
    # Jekyll loads JSON files in nested _data directories as site.data.<dir>.<name>.
    translations_dir = RADICE / "_data" / "traduzioni"
    site["data"]["traduzioni"] = {
        p.stem: json.loads(p.read_text(encoding="utf-8"))
        for p in translations_dir.glob("*.json")
    } if translations_dir.exists() else {}
    site["time"] = datetime.datetime.now()

    includes = {str(p.relative_to(RADICE / "_includes")): converti_include(p.read_text(encoding="utf-8")).replace("include.", "inc_")
                for p in (RADICE / "_includes").rglob("*") if p.is_file()}
    env = Environment(loader=DictLoader(includes))
    stato = {"profondita": 0}

    def relative_url(percorso):
        p = str(percorso).lstrip("/")
        q = ""
        if "?" in p:
            p, q = p.split("?", 1)
            q = "?" + q
        if p == "" or p.endswith("/"):
            p += "index.html"
        return "../" * stato["profondita"] + p + q

    def absolute_url(percorso):
        base = str(site.get("url", "")).rstrip("/") + str(site.get("baseurl", "")).rstrip("/")
        return base + "/" + str(percorso).lstrip("/")

    env.filters["absolute_url"] = absolute_url
    env.filters["xml_escape"] = lambda v: (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("\u0027", "&apos;"))
    env.filters["relative_url"] = relative_url
    env.filters["slugify"] = slugify
    env.filters["jsonify"] = lambda v: json.dumps(v, ensure_ascii=False, default=str)
    env.filters["group_by"] = group_by

    layouts = {p.stem: separa(p.read_text(encoding="utf-8")) for p in (RADICE / "_layouts").glob("*.html")}

    def rendi(src, page, contenuto=None):
        ctx = {"site": site, "page": page}
        if contenuto is not None:
            ctx["content"] = contenuto
        return env.from_string(converti_include(src)).render(**ctx)

    def pubblica(fm, corpo, url, est=".html"):
        page = dict(fm, url=url)
        parti = [x for x in url.strip("/").split("/") if x]
        if url.endswith("/"):
            dest = OUT.joinpath(*parti, "index.html")
            stato["profondita"] = len(parti)
        else:
            dest = OUT.joinpath(*parti)
            stato["profondita"] = len(parti) - 1
        html = rendi(corpo, page)
        if est == ".md":
            html = markdown.markdown(html, extensions=["md_in_html", "tables"])
        nome_layout = fm.get("layout")
        while nome_layout and nome_layout != "null":
            lfm, lsrc = layouts[nome_layout]
            html = rendi(lsrc, page, html)
            nome_layout = lfm.get("layout")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        return dest

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # Pagine nella radice
    for p in sorted(RADICE.glob("*")):
        if p.suffix not in (".html", ".md") or p.name == "README.md":
            continue
        fm, corpo = separa(p.read_text(encoding="utf-8"))
        url = fm.get("permalink") or ("/" if p.stem == "index" else f"/{p.stem}/")
        pubblica(fm, corpo, url, p.suffix)

    # Schede dei motori
    for p in sorted((RADICE / "_motori").glob("*.md")):
        fm, corpo = separa(p.read_text(encoding="utf-8"))
        fm.setdefault("layout", "motore")
        pubblica(fm, corpo, f"/motori/{p.stem}/")

    # Render all generated localized engine pages too, not just Italian.
    for language in ("en", "fr", "cs"):
        for p in sorted((RADICE / language).glob("*")):
            if p.suffix in (".html", ".md"):
                fm, corpo = separa(p.read_text(encoding="utf-8"))
                pubblica(fm, corpo, fm.get("permalink") or f"/{language}/{p.stem}/", p.suffix)
        for p in sorted((RADICE / language / "motori").glob("*.md")):
            fm, corpo = separa(p.read_text(encoding="utf-8"))
            fm.setdefault("layout", "motore")
            pubblica(fm, corpo, f"/{language}/motori/{p.stem}/")

    # Asset
    for p in (RADICE / "assets").rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(RADICE)
        testo = p.read_bytes()
        if p.suffix in (".json", ".css", ".js") and testo.startswith(b"---"):
            fm, corpo = separa(testo.decode("utf-8"))
            pubblica(fm, corpo, "/" + str(rel))
        else:
            (OUT / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, OUT / rel)

    print("Anteprima in", OUT)


if __name__ == "__main__":
    costruisci()
