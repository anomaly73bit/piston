#!/usr/bin/env python3
"""Traduzioni di Piston (EN, FR, CS) scritte e revisionate a mano.

L'italiano in _data/motori.yml resta il testo di riferimento. Le traduzioni stanno in
_data/traduzioni/manuali/<slug>.json con questa forma:

    {"_source_hash": "...", "en": {...}, "fr": {...}, "cs": {...}}

Ogni lingua contiene gli stessi campi di `source_data()` (testi tradotti, numeri e codici invariati).
Se l'italiano cambia, l'hash non coincide più e la traduzione viene ignorata finché non è aggiornata.

Uso:
  python3 tools/traduci.py                 ricostruisce _data/traduzioni/{en,fr,cs}.json dai file manuali
  python3 tools/traduci.py --mancanti 20   elenca i prossimi 20 motori senza traduzione valida
  python3 tools/traduci.py --modello SLUG  stampa il modello JSON (testi italiani + hash) da tradurre
"""
import hashlib
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "_data" / "traduzioni"
LANGUAGES = ("en", "fr", "cs")
MANUALI = CACHE / "manuali"
FIELDS = (
    "storia", "limiti", "paese", "alimentazione", "aspirazione",
    "distribuzione", "blocco", "testa", "iniezione", "compressione",
)
LISTS = ("punti_deboli", "curiosita", "manutenzione")
OBJECTS = {
    "versioni": ("nota",),
    "in_breve": ("testo", "valore"),
    "fonti": ("nota",),
}
SINGLE_OBJECTS = {
    "affidabilita": ("motivo",),
    "foto": ("descrizione",),
}
def source_data(engine):
    """Fields which must be translated; a changed source invalidates old copies."""
    result = {k: engine[k] for k in FIELDS if isinstance(engine.get(k), str) and engine[k].strip()}
    for key in LISTS:
        if engine.get(key):
            result[key] = engine[key]
    for key, fields in OBJECTS.items():
        if isinstance(engine.get(key), list):
            result[key] = [
                {f: entry[f] for f in fields if isinstance(entry.get(f), str) and entry[f].strip()}
                for entry in engine[key]
            ]
    for key, fields in SINGLE_OBJECTS.items():
        if isinstance(engine.get(key), dict):
            result[key] = {
                f: engine[key][f] for f in fields
                if isinstance(engine[key].get(f), str) and engine[key][f].strip()
            }
    return result


def fingerprint(data):
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()



def numeri_ok(source, translated):
    """Numeri e codici devono restare identici tra italiano e traduzione."""
    def cifre(x):
        if isinstance(x, str):
            return re.findall(r"\d+", x)
        if isinstance(x, list):
            return [c for v in x for c in cifre(v)]
        if isinstance(x, dict):
            return [c for k in sorted(x) for c in cifre(x[k])]
        return []
    from collections import Counter
    # ogni numero dell'italiano deve comparire anche nella traduzione (l'ordine può cambiare)
    return all(not (Counter(cifre(source[k])) - Counter(cifre(translated.get(k)))) for k in source)


def is_complete(source, translated):
    for key, value in source.items():
        out = translated.get(key)
        if isinstance(value, str):
            if not isinstance(out, str) or not out.strip():
                return False
        elif isinstance(value, list):
            if not isinstance(out, list) or len(out) != len(value):
                return False
            for item, translated_item in zip(value, out):
                if isinstance(item, str):
                    if not isinstance(translated_item, str) or not translated_item.strip():
                        return False
                elif isinstance(item, dict):
                    if not isinstance(translated_item, dict):
                        return False
                    if any(not isinstance(translated_item.get(k), str) or not translated_item[k].strip() for k in item):
                        return False
        elif isinstance(value, dict):
            if not isinstance(out, dict) or any(not isinstance(out.get(k), str) or not out[k].strip() for k in value):
                return False
    return True



def stato():
    engines = yaml.safe_load((ROOT / "_data" / "motori.yml").read_text(encoding="utf-8"))
    risultato = []
    for e in engines:
        src = source_data(e)
        h = fingerprint(src)
        f = MANUALI / (e["slug"] + ".json")
        man = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        valide = {l: man[l] for l in LANGUAGES
                  if man.get("_source_hash") == h and is_complete(src, man.get(l, {}))}
        risultato.append((e, src, h, valide))
    return risultato


def main():
    args = sys.argv[1:]
    if args[:1] == ["--modello"]:
        for e, src, h, _ in stato():
            if e["slug"] == args[1]:
                print(json.dumps({"_source_hash": h, "it": src}, ensure_ascii=False, indent=2))
                return 0
        print("slug non trovato", file=sys.stderr)
        return 1
    if args[:1] == ["--mancanti"]:
        n = int(args[1]) if len(args) > 1 else 20
        mancanti = [e["slug"] for e, _, _, v in stato() if len(v) < len(LANGUAGES)]
        print("\n".join(mancanti[:n]))
        print(f"# {len(mancanti)} motori da tradurre", file=sys.stderr)
        return 0
    out = {l: {} for l in LANGUAGES}
    errori = 0
    for e, src, h, valide in stato():
        for l, tr in valide.items():
            if not numeri_ok(src, tr):
                print(f"Avviso {e['slug']} [{l}]: un numero dell'italiano non compare nella traduzione, controllare", file=sys.stderr)
            out[l][e["slug"]] = dict(tr, _source_hash=h, _complete=True)
    for l in LANGUAGES:
        (CACHE / (l + ".json")).write_text(json.dumps(out[l], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{l}: {len(out[l])} motori tradotti")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
