#!/usr/bin/env python3
"""Exporta el catàleg curat a CSV per facilitar-ne la revisió humana."""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "data/iniciatives.json"
dest = ROOT / "data/revisio_iniciatives.csv"
records = json.loads(src.read_text(encoding="utf-8"))
fields = ["id", "tipus", "grups", "impulsor", "tema", "etiquetesAmbientals",
          "titol", "accio", "resum", "estat", "qualitat", "url", "fontEspecifica", "notes"]
with dest.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    for item in records:
        row = {}
        for key in fields:
            value = item.get(key, "")
            row[key] = " | ".join(value) if isinstance(value, list) else value
        writer.writerow(row)
print(f"CSV per revisar: {dest} ({len(records)} files).")
