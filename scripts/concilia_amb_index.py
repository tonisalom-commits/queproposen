#!/usr/bin/env python3
"""Concilia la mostra publicada amb l'índex oficial recuperat.

No altera les fitxes. Genera incidències que necessiten revisió humana.
Si falten pàgines a l'índex, la verificació té cobertura limitada.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def text(s: object) -> str:
    return str(s or "").strip()

def comparison(official: str, local: str) -> str:
    """No tradueix estats amb regles aproximades que confonguin tràmits."""
    if not official:
        return "estat oficial buit"
    if local == "Resultat no incorporat":
        return "resultat oficial per revisar"
    chunks = {
        "Retirada": ("retirad",),
        "Rebutjada": ("rechazad", "rechaz", "desestimar"),
        "Aprovada": ("aprobad",),
        "Aprovada amb modificacions": ("modificaci", "aprobada con modific"),
    }
    if local not in chunks:
        return "estat editorial no mapejat"
    matches = any(x in official.lower() for x in chunks[local])
    if matches:
        return "coherent: pendent revisar el document de resultat"
    return "ATENCIÓ: estat local no coincideix amb la descripció oficial"

def produce(csv_path: Path, out: Path) -> dict:
    indexed: dict[str, dict] = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        for item in csv.DictReader(stream):
            indexed[item["id"]] = item
    data = json.loads((ROOT / "data" / "iniciatives.json").read_text(encoding="utf-8"))
    env = [x for x in data if x.get("etiquetesAmbientals")]
    rows = []
    for item in env:
        match = indexed.get(item["id"])
        state = comparison(text(match["resultat_oficial"]), text(item.get("estat"))) if match else "EXPEDIENT NO RECUPERAT"
        rows.append({
            "id": item["id"],
            "tipus": item["tipus"],
            "grup_editorial": "|".join(item["grups"]),
            "autor_index": text(match["autor_oficial"]) if match else "",
            "titol_editorial": text(item["titol"]),
            "titol_index": text(match["titol_oficial"]) if match else "",
            "estat_editorial": text(item.get("estat")),
            "resultat_index": text(match["resultat_oficial"]) if match else "",
            "comparacio_resultat": state,
            "revisio_humana": "PENDENT",
            "font": text(match["font"]) if match else item["url"],
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        fields = list(rows[0]) if rows else []
        writer = csv.DictWriter(fh, fields)
        writer.writeheader()
        writer.writerows(rows)
    overview = {
        "corpus_ambiental_publicat": len(env),
        "expedients_indexats_a_les_fonts_rebudes": len(indexed),
        "fitxes_localitzades_a_l_index": sum(r["comparacio_resultat"]!="EXPEDIENT NO RECUPERAT" for r in rows),
        "discrepancies_de_resultat": [r["id"] for r in rows if r["comparacio_resultat"].startswith("ATENCIÓ")],
        "expedients_no_recuperats": [r["id"] for r in rows if r["comparacio_resultat"]=="EXPEDIENT NO RECUPERAT"],
        "limitacio": "La conciliació d'estats utilitza pistes textuals: no acredita votacions ni les formulacions de cada text dispositiu.",
        "informe": str(out),
    }
    (out.parent / "conciliacio_resum.json").write_text(
        json.dumps(overview, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return overview

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--sortida", type=Path, default=Path("revisio-ambiental/conciliacio_amb_web.csv"))
    opts=parser.parse_args()
    print(json.dumps(produce(opts.index, opts.sortida),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
