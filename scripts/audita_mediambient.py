#!/usr/bin/env python3
"""Diagnosi reproduïble de la cobertura ambiental (sense fingir exhaustivitat)."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(records: list[dict]) -> dict:
    ambient = [r for r in records if r.get("etiquetesAmbientals")]
    reviewed = [r for r in ambient if isinstance(r.get("revisio"), dict)]
    by_group = Counter(g for r in ambient for g in r.get("grups", []))
    by_status = Counter(r.get("estat", "Desconegut") for r in ambient)
    by_level = Counter(r["revisio"]["nivell"] for r in reviewed)
    return {
        "data": date.today().isoformat(),
        "abast": "XV legislatura, només les fitxes ambientals incorporades",
        "univers_recuperat_i_auditat": False,
        "nombre_fitxes_ambientals": len(ambient),
        "amb_revisio_documentada": len(reviewed),
        "amb_text_dispositiu_integre_revisat": None,
        "per_tipus": dict(Counter(r.get("tipus", "") for r in ambient)),
        "per_nivell_revisio": dict(sorted(by_level.items())),
        "per_estat_de_la_mostra": dict(sorted(by_status.items())),
        "per_grup_dins_la_mostra_NO_COMPARABLE": dict(sorted(by_group.items())),
        "advertiments": [
            "No hi ha denominador verificat: no es poden publicar percentatges d'exhaustivitat.",
            "La manca de fitxes d'un partit no indica que no presentàs propostes.",
            "Autoria, contingut, resultat i votacions són graus diferents de verificació.",
            "Una esmena pot alterar el text inicial, una retirada no és una votació de rebuig.",
            "Cal revisar també expedients descartats pels filtres de paraules clau.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortida", type=Path, help="Fitxer JSON opcional d'auditoria")
    args = ap.parse_args()
    data = json.loads((ROOT / "data" / "iniciatives.json").read_text(encoding="utf-8"))
    obj = audit(data)
    out = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if args.sortida:
        args.sortida.parent.mkdir(parents=True, exist_ok=True)
        args.sortida.write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
