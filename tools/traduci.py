#!/usr/bin/env python3
"""Translate every current and future engine from canonical Italian into EN, FR and CZ JSON.
Run: pip install pyyaml deep-translator
     python tools/traduci.py
Uses an incremental cache, preserving all previously translated texts. Network access
is required; errors are explicit. Never rewrites the Italian source of truth.
"""
import json
import pathlib
import time
import os
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGUAGES = {"en": "en", "fr": "fr", "cs": "cs"}
FIELDS = ("storia", "limiti")
LISTS = ("punti_deboli", "curiosita", "manutenzione")
NESTED = {"versioni": ("nota",), "in_breve": ("testo",), "affidabilita": ("motivo",)}
CACHE = ROOT / "_data" / "traduzioni"
CACHE.mkdir(parents=True, exist_ok=True)

def main():
    from deep_translator import GoogleTranslator
    engines = yaml.safe_load((ROOT / "_data" / "motori.yml").read_text(encoding="utf-8"))
    for language, target in LANGUAGES.items():
        file = CACHE / (language + ".json")
        existing = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
        translator = GoogleTranslator(source="it", target=target)
        memory = existing.get("_memory", {})
        translated_count = 0
        batch_limit = int(os.environ.get("PISTON_TRANSLATION_BATCH", "30"))
        def translate(value):
            nonlocal translated_count
            if not isinstance(value, str) or not value.strip():
                return value
            if value in memory:
                return memory[value]
            if translated_count >= batch_limit:
                return None
            for attempt in range(3):
                try:
                    result = translator.translate(value)
                    if not result:
                        raise ValueError("empty translation")
                    memory[value] = result
                    translated_count += 1
                    time.sleep(3)
                    return result
                except Exception:
                    if attempt == 2:
                        print(f"{language}: translation provider unavailable; saving progress")
                        return None
                    time.sleep(45 * (attempt + 1))
        result = {"_memory": memory}
        for m in engines:
            item = {}
            for field in FIELDS:
                if m.get(field):
                    item[field] = translate(m[field]) or (existing.get(m["slug"], {}).get(field))
            for field in LISTS:
                if m.get(field):
                    old = existing.get(m["slug"], {}).get(field, [])
                    item[field] = [translate(v) or (old[i] if i < len(old) else None) for i, v in enumerate(m[field])]
            for field, keys in NESTED.items():
                obj = m.get(field)
                if isinstance(obj, dict):
                    old = existing.get(m["slug"], {}).get(field, {})
                    item[field] = {k: translate(obj[k]) or old.get(k) for k in keys if obj.get(k)}
                elif isinstance(obj, list):
                    old = existing.get(m["slug"], {}).get(field, [])
                    item[field] = [{k: translate(x[k]) or (old[i].get(k) if i < len(old) else None) for k in keys if x.get(k)} for i, x in enumerate(obj)]
            result[m["slug"]] = item
        file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(language, len(engines), "engine families processed;", translated_count, "new text translations")

if __name__ == "__main__":
    main()
