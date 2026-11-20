#!/usr/bin/env python3
"""Comprovació local del catàleg. No substitueix la verificació de fonts primàries."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ID = re.compile(r"^(?:161|162|122)/\d{6}$")
ALLOWED_TYPES = {"PNL": {"161", "162"}, "PL": {"122"}}


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    try:
        items = load(DATA / "iniciatives.json")
        catalog = load(DATA / "catalog.json")
    except (OSError, ValueError) as exc:
        print(f"ERROR: no es poden llegir les dades: {exc}", file=sys.stderr)
        return 1
    errors: list[str] = []
    if not isinstance(items, list):
        print("ERROR: iniciatives.json ha de contenir una llista.", file=sys.stderr)
        return 1
    group_ids = {x["id"] for x in catalog["grups"]}
    topics = set(catalog["temes"])
    env_topics = set(catalog["subtemesAmbientals"])
    seen: set[str] = set()

    for n, record in enumerate(items, start=1):
        if not isinstance(record, dict):
            errors.append(f"Registre {n}: no és un objecte.")
            continue
        code = record.get("id", "")
        prefix = str(code).split("/", 1)[0]
        kind = record.get("tipus")
        context = f"Registre {n} ({code!s})"
        if not ID.fullmatch(str(code)):
            errors.append(f"{context}: format d'expedient desconegut.")
        if code in seen:
            errors.append(f"{context}: expedient duplicat.")
        seen.add(code)
        if kind not in ALLOWED_TYPES or prefix not in ALLOWED_TYPES.get(kind, set()):
            errors.append(f"{context}: tipus {kind!r} incompatible amb el codi.")
        for field in ("titol", "resum", "estat", "qualitat"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                errors.append(f"{context}: falta {field}.")
        grps = record.get("grups")
        if not isinstance(grps, list) or not grps:
            errors.append(f"{context}: grups ha de ser una llista no buida.")
        elif any(g not in group_ids for g in grps):
            errors.append(f"{context}: grup parlamentari no declarat: {grps}.")
        if record.get("tema") not in topics:
            errors.append(f"{context}: tema principal fora de taxonomia.")
        tags = record.get("etiquetesAmbientals", [])
        if not isinstance(tags, list) or any(t not in env_topics for t in tags):
            errors.append(f"{context}: etiquetes ambientals no vàlides.")
        if len(tags) != len(set(tags)):
            errors.append(f"{context}: etiquetes ambientals duplicades.")
        if tags and record.get("subtemaAmbiental") not in tags:
            errors.append(f"{context}: el subtema principal no consta entre les etiquetes.")

        rev = record.get("revisio")
        if rev is not None:
            if not isinstance(rev, dict):
                errors.append(f"{context}: revisio ha de ser un objecte.")
            else:
                if rev.get("nivell") not in {"autoria", "contingut", "tramitacio", "resultat"}:
                    errors.append(f"{context}: nivell de revisio desconegut.")
                if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", str(rev.get("data", ""))):
                    errors.append(f"{context}: manca data ISO de revisio.")
                if not isinstance(rev.get("nota"), str) or len(rev.get("nota", "")) < 30:
                    errors.append(f"{context}: cal documentar el límit de la revisió.")
                fs = rev.get("fonts")
                if not isinstance(fs, list) or not fs:
                    errors.append(f"{context}: la revisió no té fonts.")
                else:
                    for fuente in fs:
                        parsed_source = urlparse(str(fuente))
                        if parsed_source.scheme != "https" or parsed_source.hostname not in {
                            "www.congreso.es", "congreso.es", "app.congreso.es",
                            "www.boe.es", "boe.es"
                        }:
                            errors.append(f"{context}: font de revisió no oficial: {fuente}")
                if rev.get("nivell") == "resultat" and record.get("estat") == "Resultat no incorporat":
                    errors.append(f"{context}: resultat suposadament verificat, però no incorporat.")

        url = record.get("url", "")
        parsed = urlparse(str(url))
        if parsed.scheme != "https" or parsed.hostname not in {"www.congreso.es", "congreso.es"}:
            errors.append(f"{context}: falta un URL oficial del Congrés.")

    if errors:
        print("\n".join("ERROR: " + e for e in errors), file=sys.stderr)
        print(f"\n{len(errors)} error(s) de dades.", file=sys.stderr)
        return 1
    counts = Counter(p["tipus"] for p in items)
    env = [p for p in items if p.get("etiquetesAmbientals")]
    print(f"Dades vàlides: {len(items)} expedients ({counts['PNL']} PNL, {counts['PL']} PL).")
    print(f"Medi ambient: {len(env)} expedients de mostra; {len(env_topics)} subtemes possibles.")
    print("ATENCIÓ: la validació és estructural; NO acredita exhaustivitat ni exactitud jurídica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
