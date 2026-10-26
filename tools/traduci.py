#!/usr/bin/env python3
"""Incremental offline translation of Piston's Italian engine catalogue.

Uses open Argos Translate language models, avoiding anonymous web-translation
rate limits. Italian YAML remains authoritative. Each run translates a bounded
number of new strings per language and saves a resumable JSON catalogue.
Never marks an untranslated field as translated.
"""
import hashlib
import json
import os
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "_data" / "traduzioni"
LANGUAGES = ("en", "fr", "cs")
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
MAX_NEW_PER_LANGUAGE = int(os.environ.get("PISTON_TRANSLATION_BATCH", "200"))



# Fixed automotive terminology takes precedence over generic machine translation.
# This prevents mistranslations such as "Benzina" -> "Petroleum" and "Ghisa" -> "Ghisa".
GLOSSARY = {
    "en": {
        "Benzina": "Petrol", "Gasolio": "Diesel fuel", "Diesel": "Diesel",
        "Ghisa": "Cast iron", "Alluminio": "Aluminium", "Aspirato": "Naturally aspirated",
        "Atmosferico": "Naturally aspirated", "Biturbo": "Twin-turbo",
        "Turbo": "Turbocharged", "Indiretta multipoint": "Multipoint port fuel injection",
        "Diretta": "Direct injection", "DOHC a catena": "Chain-driven DOHC",
        "DOHC a cinghia": "Belt-driven DOHC", "SOHC a catena": "Chain-driven SOHC",
        "SOHC a cinghia": "Belt-driven SOHC",
    },
    "fr": {
        "Benzina": "Essence", "Gasolio": "Gazole", "Diesel": "Diesel",
        "Ghisa": "Fonte", "Alluminio": "Aluminium", "Aspirato": "Atmosphérique",
        "Atmosferico": "Atmosphérique", "Biturbo": "Biturbo",
        "Turbo": "Turbocompressé", "Indiretta multipoint": "Injection indirecte multipoint",
        "Diretta": "Injection directe", "DOHC a catena": "Double arbre à cames entraîné par chaîne",
        "DOHC a cinghia": "Double arbre à cames entraîné par courroie",
        "SOHC a catena": "Simple arbre à cames entraîné par chaîne",
        "SOHC a cinghia": "Simple arbre à cames entraîné par courroie",
    },
    "cs": {
        "Benzina": "Benzín", "Gasolio": "Motorová nafta", "Diesel": "Nafta",
        "Ghisa": "Litina", "Alluminio": "Hliník", "Aspirato": "Atmosférický",
        "Atmosferico": "Atmosférický", "Biturbo": "Dvě turbodmychadla",
        "Turbo": "Přeplňovaný turbodmychadlem",
        "Indiretta multipoint": "Nepřímé vícebodové vstřikování",
        "Diretta": "Přímé vstřikování", "DOHC a catena": "DOHC s řetězovým rozvodem",
        "DOHC a cinghia": "DOHC s řemenovým rozvodem",
        "SOHC a catena": "SOHC s řetězovým rozvodem",
        "SOHC a cinghia": "SOHC s řemenovým rozvodem",
    },
}

def prepare_argos():
    import argostranslate.package as package
    import argostranslate.translate as translate

    package.update_package_index()
    available = package.get_available_packages()
    installed = {(p.from_code, p.to_code) for p in package.get_installed_packages()}

    # English is the bridge when a direct Italian -> French/Czech model
    # is unavailable. Argos automatically supports installed pivot routes.
    needed = [("it", "en"), ("en", "fr"), ("en", "cs")]
    for source, target in needed:
        if (source, target) in installed:
            continue
        candidate = next(
            (p for p in available if p.from_code == source and p.to_code == target),
            None,
        )
        if candidate is None:
            raise RuntimeError(f"No Argos model for {source}->{target}; not publishing incomplete translations")
        print(f"Installing Argos model {source}->{target}", flush=True)
        package.install_from_path(candidate.download())
    return translate


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


def validate_numbers(source, translated):
    """Reject translations that silently drop or change technical figures."""
    digits = lambda s: re.findall(r"\d+", s)
    units = ("CV", "Nm", "mm", "cc", "kW")
    return digits(source) == digits(translated) and all(unit not in source or unit in translated for unit in units)


def main():
    engines = yaml.safe_load((ROOT / "_data" / "motori.yml").read_text(encoding="utf-8"))
    CACHE.mkdir(parents=True, exist_ok=True)
    translator = prepare_argos()
    incomplete = 0
    for language in LANGUAGES:
        path = CACHE / (language + ".json")
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        memory = previous.get("_memory", {})
        memory.update(GLOSSARY[language])
        new_count = 0
        errors = 0

        def translate_one(value):
            nonlocal new_count, errors
            if not isinstance(value, str) or not value.strip():
                return value
            if re.fullmatch(r"[0-9.,:/ –-]+", value):
                return value
            if value in memory:
                if validate_numbers(value, memory[value]):
                    return memory[value]
                del memory[value]
            if new_count >= MAX_NEW_PER_LANGUAGE:
                return None
            try:
                result = translator.translate(value, "it", language)
                if not isinstance(result, str) or not result.strip():
                    raise ValueError("Empty translation")
                if not validate_numbers(value, result):
                    raise ValueError("Numbers or engine codes changed in translation")
                memory[value] = result
                new_count += 1
                return result
            except Exception as exc:
                errors += 1
                if errors <= 5:
                    print(f"{language}: translation requires review: {exc}", flush=True)
                return None

        output = {"_memory": memory}
        for engine in engines:
            slug = engine["slug"]
            source = source_data(engine)
            source_hash = fingerprint(source)
            old = previous.get(slug, {})
            # Never reuse a translation from a different Italian source.
            if old.get("_source_hash") != source_hash:
                old = {}
            item = {"_source_hash": source_hash}
            for key in FIELDS:
                if key in source:
                    item[key] = translate_one(source[key]) or old.get(key)
            for key in LISTS:
                if key in source:
                    old_list = old.get(key, [])
                    item[key] = [
                        translate_one(v) or (old_list[i] if i < len(old_list) else None)
                        for i, v in enumerate(source[key])
                    ]
            for key, fields in OBJECTS.items():
                if key in source:
                    old_list = old.get(key, [])
                    item[key] = []
                    for i, obj in enumerate(source[key]):
                        old_obj = old_list[i] if i < len(old_list) else {}
                        item[key].append({
                            f: translate_one(value) or old_obj.get(f)
                            for f, value in obj.items()
                        })
            for key, fields in SINGLE_OBJECTS.items():
                if key in source:
                    old_obj = old.get(key, {})
                    item[key] = {
                        f: translate_one(value) or old_obj.get(f)
                        for f, value in source[key].items()
                    }
            output[slug] = item
            if not is_complete(source, item):
                incomplete += 1

        path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{language}: {new_count} new translations, {errors} failed; progress saved", flush=True)
    print(f"Unfinished language/engine pairs: {incomplete} of {len(engines) * len(LANGUAGES)}", flush=True)


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


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Translation blocked: {exc}", file=sys.stderr)
        sys.exit(1)
