#!/usr/bin/env python3
"""Priorització de falsos negatius potencials per TÍTOLS, mai classificació temàtica.

Revisa tot el marc dels 4.264 expedients inicialment fora de cua i detecta
pistes noves que l'extracció original no contemplava. No substitueix la
mostra probabilística estratificada ni acredita el contingut del dispositiu.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

from scripts.integra_auditoria_ambient_xv import (
    DATA, load_decisions, normalize, read_csv, write_csv,
)

# Cada grup de termes es cerca dins el títol normalitzat. Els punts descriuen
# PRIORITAT DE LECTURA, no probabilitat que una proposta sigui ambiental.
STRONG = {
    "contaminacio_acustica": r"\bacustic|\bsoroll|\bruido|\bsonor",
    "energia_i_electrificacio": (
        r"\balta tension|\btension alta|\belectricidad|\belectrico|"
        r"\belectrica|\belectrific|\bhidrogeno|\bfotovoltaic|\beolic|"
        r"\benergia renovable|\bnuclear|\bdescarboniz|\bdescarbonitz"
    ),
    "gestio_del_litoral": r"\bcosta(s)?\b|\blitoral|\bplaya|\bmaritim|\bmarino|\bcostero",
    "aigua_i_inundacions": (
        r"\bembalse|\btrasvas|\bdepurad|\bdesalador|\bhidrolog|\binundaci|"
        r"\briada|\bsequia|\bdesbordamiento|\bagua regenerad|\bacuifer|\bgot(a|es) fri(a|es)"
    ),
    "riscos_i_emergencia": r"\bdana\b|\btemporal|\bincendio forestal|\bincendi forestal|\bcatastrofe natural",
    "proteccio_ecologica": (
        r"\bfauna|\bflora|\bespecie(s)? (invasor|amenazad|proteg)|"
        r"\bbiodivers|\becosistem|\becocid|\bmedio ambiente|\bmedio natural|"
        r"\bnaturaleza|\bparque nacional|\bparque natural|\bproteccion ambiental|"
        r"\brenaturaliz|\brestauracion ambiental|\brecicl|\bvertido|\bresiduo|"
        r"\bemision|\bcontamina"
    ),
    "mobilitat_sostenible": (
        r"\btransporte publico|\bmovilidad sostenible|\bmovilidad electrica|"
        r"\bvehiculo electrico|\bbicicleta|\bvia verde|\bcarril bici|\bciclist"
    ),
    "economia_i_industria_verda": (
        r"\beconomia circular|\btransicion energetica|\btransicion ecologica|"
        r"\becodiseno|\bbiocombustible|\beficiencia energetica|\benergias limpias"
    ),
}
# Senyals indirectes, amb molts falsos positius. No inferim protecció ambiental
# a partir d'un aeroport, un ferrocarril o un sector productiu.
WEAK = {
    "agricultura_i_alimentacio": (
        r"\bagrari|\bagricultur|\bagroalimentar|\bganader|\bregadi|\bpatata|"
        r"\bpesca|\bpescador|\bforestal|\bmonte(s)?\b"
    ),
    "transport_i_infraestructura": (
        r"\btransporte|\bautopista|\bcarreter|\bferrocarril|\brodalies|"
        r"\brenfe|\badif|\bmetro\b|\baeropuerto|\baeroport|\baeronaut"
    ),
    "industria_i_energia_sectorial": (
        r"\bindustrial|\bindustria|\baluminio|\benergetic|\benergia\b|"
        r"\bmineria|\bpacto del agua|\bdesarrollo sostenible|\bsostenib"
    ),
    "ordenacio_territorial_i_turisme": (
        r"\burbanism|\bterritorio|\bterritorial|\bturismo|\bhidraulica|"
        r"\bdominio publico|\bpaisaje|\bpaisatg"
    ),
}
COLS = [
    "id", "serie", "titol_oficial", "autor_oficial",
    "prioritat_lectura", "categories_pista", "pistes_fortes",
    "pistes_indirectes", "revisio_actual", "url_expedient",
    "advertiment",
]


def title_signals(title: str) -> dict:
    t = normalize(title)
    strong = [name for name, pattern in STRONG.items() if re.search(pattern, t)]
    weak = [name for name, pattern in WEAK.items() if re.search(pattern, t)]
    priority = len(strong) * 10 + len(weak) * 2
    return {
        "prioritat_lectura": priority,
        "categories_pista": strong + weak,
        "pistes_fortes": strong,
        "pistes_indirectes": weak,
    }


def calculate(outside: list[dict], decisions: dict,
              max_queue: int = 250) -> tuple[list[dict], list[dict], dict]:
    ids = [r["id"] for r in outside]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicats al marc de revisio")
    all_signals = []
    without_signal = 0
    audited_outside = 0
    for row in outside:
        code = row["id"]
        audit = decisions.get(code)
        if audit:
            audited_outside += 1
            continue
        hints = title_signals(row["titol_oficial"])
        if not hints["prioritat_lectura"]:
            without_signal += 1
            continue
        all_signals.append({
            "id": code, "serie": row["serie"],
            "titol_oficial": row["titol_oficial"],
            "autor_oficial": row["autor_oficial"],
            "prioritat_lectura": hints["prioritat_lectura"],
            "categories_pista": " | ".join(hints["categories_pista"]),
            "pistes_fortes": " | ".join(hints["pistes_fortes"]),
            "pistes_indirectes": " | ".join(hints["pistes_indirectes"]),
            "revisio_actual": "PENDENT: text original i dispositiu no verificats",
            "url_expedient": row["url_expedient"],
            "advertiment": (
                "Pista lexica de TITOL: no es una inclusio ni una decisio"
            )
        })
    all_signals.sort(key=lambda r: (
        -r["prioritat_lectura"], -bool(r["pistes_fortes"]),
        int(r["serie"]), r["id"],
    ))
    queue = all_signals[:max_queue]
    cnt = Counter()
    for row in all_signals:
        for c in row["categories_pista"].split(" | "):
            cnt[c] += 1
    summary = {
        "univers_fora_cua_original": len(outside),
        "ja_revisats_fora_cua": audited_outside,
        "sense_pistes_noves_i_sense_revisar": without_signal,
        "amb_pistes_i_sense_revisar": len(all_signals),
        "cua_prioritaria": len(queue),
        "suma_verificada": audited_outside + without_signal + len(all_signals),
        "categories": dict(cnt.most_common()),
        "tipus": "CRIBRATGE_LEXIC_DE_TITOLS_SENSE_CLASSIFICACIO",
        "mostra_aleatoria_independent": "NO ALTERADA",
        "limitacions": [
            "Algunes iniciatives ambientals no tenen cap pista ambiental al titol.",
            "La coincidencia lexical no significa que les mesures siguin ambientals.",
            "La cua de lectura no es una mostra estadistica representativa.",
            "L'ambientalitat directa i secundaria exigeix dispositius llegits.",
            "Els expedients revisats queden fora de la nova cua per evitar duplicats.",
        ],
    }
    if summary["suma_verificada"] != len(outside):
        raise ValueError("Particio fora de cua incompleta")
    return all_signals, queue, summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dades", type=Path, default=DATA)
    parser.add_argument("--max-cua", type=int, default=250)
    args = parser.parse_args()
    if args.max_cua < 1:
        raise ValueError("La cua ha de tenir almenys un registre")
    data = args.dades
    outside = read_csv(data / "fora_cua_xv_4264.csv")
    decisions = load_decisions(data)
    all_signals, queue, result = calculate(outside, decisions, args.max_cua)
    write_csv(data / "pistes_ampliades_fora_cua_xv.csv", all_signals, COLS)
    write_csv(data / "cua_ampliada_fora_cua_xv_250.csv", queue, COLS)
    (data / "resum_pistes_ampliades_xv.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
