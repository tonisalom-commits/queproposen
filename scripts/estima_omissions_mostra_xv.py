#!/usr/bin/env python3
"""Diagnòstic descriptiu, auditable, de la mostra probabilística de fora de cua.

Les expansions són estimadors *condicionals* a escenaris de classificació dels
observats; NO són límits del nombre real d'omissions ni intervals de confiança.
No modifica el web ni pren decisions sobre expedients.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "treball"
KEYS = {"INCLOURE", "EXCLOURE", "FRONTERER", "PENDENT"}


def assess(sample: list[dict], manifest: dict) -> dict:
    strata = manifest["estrats"]
    if len(sample) != manifest["mida"] or len({r["id"] for r in sample}) != len(sample):
        raise ValueError("Mostra absent, parcial o amb identificadors repetits")
    if {r["serie"] for r in sample} != set(strata):
        raise ValueError("Estrats discordants entre mostra i manifest")
    bins: dict[str, Counter] = defaultdict(Counter)
    ids_per_serie = defaultdict(set)
    for row in sample:
        serie = row["serie"]
        st = row["estat_revision"]
        if st.startswith("AUDITAT: "):
            value = st.removeprefix("AUDITAT: ").strip()
        elif st.startswith("PENDENT: "):
            value = "PENDENT"
        else:
            raise ValueError(f"Estat de revisió no reconegut: {row['id']} ({st})")
        if value not in KEYS:
            raise ValueError(f"Decisió desconeguda: {row['id']} ({value})")
        if serie not in strata:
            raise ValueError(f"Sèrie no prevista: {serie}")
        bins[serie][value] += 1
        ids_per_serie[serie].add(row["id"])
    stratum_stats = {}
    totals = Counter()
    est_min = 0.
    est_max = 0.
    one = []
    for serie, obj in sorted(strata.items()):
        pop = obj["poblacio"]
        n = obj["seleccionats"]
        if not (0 < n <= pop) or n != len(ids_per_serie[serie]):
            raise ValueError(f"Mida de mostra per sèrie incorrecta: {serie}")
        c = bins[serie]
        if sum(c.values()) != n:
            raise ValueError(f"Recompte incorrecte: {serie}")
        weight = pop / n  # Pes exacte, no la representació decimal truncada del CSV.
        lo = c["INCLOURE"] * weight
        hi = (c["INCLOURE"] + c["FRONTERER"] + c["PENDENT"]) * weight
        est_min += lo
        est_max += hi
        totals.update(c)
        stratum_stats[serie] = {
            "poblacio_fora_cua": pop, "mostra": n,
            "incloses": c["INCLOURE"], "excloses": c["EXCLOURE"],
            "frontereres": c["FRONTERER"], "pendents": c["PENDENT"],
            "pes_disseny": round(weight, 6),
            "expansio_inclusions_confirmades": round(lo, 2),
            "expansio_si_ambigues_i_pendents_fossin_incloses": round(hi, 2),
            "variancia_dins_estrat_estimable": n >= 2,
        }
        if n < 2:
            one.append(serie)
    if sum(totals.values()) != len(sample):
        raise ValueError("Recompte global discordant")
    result = {
        "marc": manifest["marc_mostral"],
        "llavor": manifest["llavor"],
        "mostra_total": len(sample),
        "mostra_revisada": len(sample) - totals["PENDENT"],
        "repartiment": {
            "incloses": totals["INCLOURE"], "excloses": totals["EXCLOURE"],
            "frontereres": totals["FRONTERER"], "pendents": totals["PENDENT"],
        },
        "escenaris_d_expansio_condicional": {
            "si_totes_les_ambigues_i_pendents_fossin_excloses": round(est_min, 2),
            "si_totes_les_ambigues_i_pendents_fossin_incloses": round(est_max, 2),
            "unitat": "expedients fora de la cua inicial",
            "interpretacio": (
                "Dues expansions de les freqüències observades ponderades per sèrie,"
                " sota escenaris alternatius de classificació de la mostra. "
                "NO són cotes poblacionals, ni estimacions amb interval de confiança."
            ),
        },
        "estrats": stratum_stats,
        "advertiments": [
            f"No es pot estimar la variància de disseny dins dels estrats amb un sol cas: {', '.join(one)}.",
            "Els casos frontera i els pendents no tenen classificació resolta.",
            "L'atzar del mostreig no demostra que les decisions temàtiques siguin correctes.",
            "La precisió i l'error de classificació no han estat estimats.",
            "La selecció inicial de 830 pot contenir falsos positius i encara té molts casos sense classificar.",
            "No usar els escenaris com a nombre verificat d'omissions ni publicar comparacions de partits.",
        ],
        "grau": "DIAGNOSTIC_PROVISIONAL_SENSE_INTERVAL_DE_CONFIANCA",
    }
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dades", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.dades
    with (root / "mostra_aleatoria_fora_cua_xv_100.csv").open(
        encoding="utf-8-sig", newline=""
    ) as fh:
        sample = list(csv.DictReader(fh))
    manifest = json.loads((root / "manifest_mostra_aleatoria_fora_cua_xv.json").read_text())
    output = assess(sample, manifest)
    target = root / "diagnostic_provisional_omissions_mostra_xv.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
