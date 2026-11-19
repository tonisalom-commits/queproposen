#!/usr/bin/env python3
"""Auditoria documental de la selecció ambiental contra els índexs oficials de la XV legislatura.

NO marca un tema ambiental com a verificat basant-se només en el títol; NO
substitueix la lectura del text, de les esmenes ni dels acords de cada expedient.

Ús: python3 scripts/audita_cobertura_ambiental.py \
  --index revisio-ambiental/inventari_index.csv \
  --sortida revisio-ambiental/auditoria
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "iniciatives.json"
SERIES = ["161", "162", "122", "120", "123", "124", "125"]
IDENTITY = re.compile(r"^(?:161|162|122|120|123|124|125)/[0-9]{6}$")


def normalized(text: object) -> str:
    text = unicodedata.normalize("NFKD", str(text or "").casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def inferred_groups(author: object) -> set[str]:
    """Suggereix grups per comparació, MAI substitueix el camp d'autoria."""
    text = normalized(author)
    lexicon = {
        "PSOE": ("grupo parlamentario socialista",),
        "PP": ("grupo parlamentario popular",),
        "SUMAR": ("grupo parlamentario plurinacional sumar", "grupo parlamentario sumar"),
        "VOX": ("grupo parlamentario vox",),
        "JUNTS": ("grupo parlamentario junts per catalunya",),
        "ERC": ("grupo parlamentario republicano",),
        "PNB": ("grupo parlamentario vasco",),
        "BILDU": ("grupo parlamentario euskal herria bildu", "grupo parlamentario eh bildu"),
        "MIXT": ("grupo parlamentario mixto",),
    }
    return {group for group, variants in lexicon.items()
            if any(variant in text for variant in variants)}


def status_family(text: object) -> str:
    raw = normalized(text)
    if not raw or "no incorporat" in raw or "pendiente" in raw:
        return "desconegut"
    if "modificaci" in raw or "modificacion" in raw:
        if "aproba" in raw:
            return "aprovada_amb_modificacions"
    if "aproba" in raw or "convalida" in raw:
        return "aprovada"
    if "rechaz" in raw or "rebutjad" in raw:
        return "rebutjada"
    if "retira" in raw:
        return "retirada"
    if "caduc" in raw:
        return "caducada"
    if "inadmit" in raw:
        return "inadmesa"
    return "altres"


def audit(index_csv: Path, dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    official = {}
    duplicates = []
    with index_csv.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            code = row.get("id", "").strip()
            if not IDENTITY.fullmatch(code):
                raise ValueError(f"ID mal format a l'índex: {code!r}")
            if code in official:
                duplicates.append(code)
            else:
                official[code] = row
    curated = json.loads(CATALOG.read_text(encoding="utf-8"))
    environmental = [record for record in curated if record.get("etiquetesAmbientals")]
    series_count = Counter(x["serie"] for x in official.values())
    candidates_count = Counter(x["serie"] for x in official.values()
                               if str(x.get("possible_ambiental", "")).lower() in {"true", "1", "sí", "si"})
    findings = []
    for record in environmental:
        code = record["id"]
        row = official.get(code)
        expected_groups = set(record.get("grups") or [])
        observed_groups = inferred_groups(row.get("autor_oficial", "")) if row else set()
        recorded_status = status_family(record.get("estat"))
        official_status = status_family(row.get("resultat_oficial")) if row else "desconegut"
        if not row:
            flag = "NO_LOCALITZAT_A_L_INDEX"
        elif observed_groups and not observed_groups.intersection(expected_groups):
            flag = "AUTORIA_DIFERENT: REVISAR"
        elif official_status != "desconegut" and recorded_status not in (
                official_status, "desconegut",
                # Una proposta aprovada amb modificacions és una aprovació.
                "aprovada" if official_status == "aprovada_amb_modificacions" else "INEXISTENT"):
            flag = "ESTAT_DIFERENT: REVISAR"
        else:
            flag = "METADADES_COMPATIBLES"
        findings.append({
            "id": code,
            "tipus": record.get("tipus", ""),
            "etiquetesAmbientals": " | ".join(record["etiquetesAmbientals"]),
            "titol_web": record.get("titol", ""),
            "titol_oficial": row.get("titol_oficial", "") if row else "",
            "autor_web": " | ".join(record.get("grups") or []),
            "autor_oficial": row.get("autor_oficial", "") if row else "",
            "estat_web": record.get("estat", ""),
            "resultat_oficial": row.get("resultat_oficial", "") if row else "",
            "font_oficial": row.get("font", "") if row else "",
            "present_al_index": bool(row),
            "marca": flag,
            "lectura_text_complet": "PENDENT O PARCIAL",
            "votacions_verificades": "NO",
        })
    no_title = [f["id"] for f in findings
                if f["present_al_index"] and str(official[f["id"]]["possible_ambiental"]).lower()
                not in {"true", "1", "sí", "si"}]
    columns = list(findings[0]) if findings else []
    with (dest / "auditoria_fitxes_ambientals.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(findings)
    summary = {
        "data_revisio": datetime.now(timezone.utc).isoformat(),
        "univers_consultat": "XV legislatura — índexs de les sèries 161,162,122,120,123,124,125",
        "index_registres_unics": len(official),
        "index_repetits": duplicates[:50],
        "per_serie": dict(sorted(series_count.items())),
        "candidats_per_titol_per_serie": dict(sorted(candidates_count.items())),
        "fitxes_ambientals_existents": len(environmental),
        "fitxes_trobades": sum(x["present_al_index"] for x in findings),
        "metadades_amb_incidencies": [
            {"id":x["id"],"marca":x["marca"]} for x in findings
            if x["marca"] != "METADADES_COMPATIBLES"
        ],
        "fitxes_ambientals_que_no_contindrien_paraules_clau_al_titol": no_title,
        "conclusio": (
            "S'ha contrastat només la coherència de les metadades de les fitxes "
            "ja publicades. La pertinença ambiental, els textos, les esmenes i "
            "els vots no estan auditats exhaustivament."
        ),
        "estat_auditoria_integral": "PENDENT",
    }
    (dest / "resum_auditoria.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--sortida", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.index, args.sortida), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
