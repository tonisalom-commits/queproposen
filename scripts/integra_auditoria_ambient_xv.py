#!/usr/bin/env python3
"""Integra decisions individuals sense alterar el corpus original ni el web.

Entrades permanentment conservades al repositori:
- cua_ambient_xv_830_conciliada.csv (830 registres de treball)
- univers_congres_xv_5094.csv i fora_cua_xv_4264.csv
- auditoria_mediambient_lot*.csv (decisions amb fonts, mai inferides de títols)

Sortides de revisió, separades de data/iniciatives.json:
- inventari_ambient_xv_revisat.csv: cua + decisions individuals
- cua_lot02_40.csv: propostes prioritàries encara PENDENTS
- control_omissions_fora_cua_xv.csv: pistes no verificades del títol
- mostra_control_fora_cua_xv_100.csv: auditoria negativa sistemàtica
- resum_auditoria_ambient_xv.json: comptabilitat sense rànquings partidistes
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "treball"
ID = re.compile(r"^(?:120|122|123|124|125|161|162)/\d{6}$")
VALID = {"INCLOURE", "EXCLOURE", "FRONTERER"}
AUDIT_FIELDS = {
    "expedient", "decisio_ambiental", "grau_revision", "instrument",
    "subtemes", "mesures_identificades", "font_text_inicial",
    "font_resultat_o_tramit", "data_auditoria",
}
EXTRA = [
    "decisio_auditoria", "grau_auditoria", "lot_auditoria",
    "subtemes_auditoria", "mesures_auditoria", "observacions_auditoria",
    "font_text_auditoria", "font_resultat_auditoria", "data_auditoria",
]
SIGNALS = {
    "natura 2000": "xarxa Natura 2000",
    "espacios protegidos": "espais protegits",
    "parque nacional": "parcs nacionals",
    "reserva de la biosfera": "reserves de biosfera",
    "humedal": "zones humides",
    "acuifero": "aqüífers",
    "nitratos": "nitrats",
    "pesticida": "pesticides",
    "plaguicida": "plaguicides",
    "vertidos": "abocaments",
    "zona de bajas emisiones": "zones de baixes emissions",
    "zonas de bajas emisiones": "zones de baixes emissions",
    "movilidad sostenible": "mobilitat sostenible",
    "transporte publico": "transport públic",
    "corredor verde": "corredors verds",
    "inundacion": "inundacions",
    "erosion": "erosió",
    "emergencia climatica": "emergència climàtica",
    "residuos": "residus",
    "economia circular": "economia circular",
    "descarbonizacion": "descarbonització",
    "renaturalizacion": "renaturalització",
    "agua potable": "aigua potable",
    "medio ambiente": "medi ambient",
    "biodiversidad": "biodiversitat",
    "incendios forestales": "incendis forestals",
    "mar menor": "Mar Menor",
    "donana": "Doñana",
    "cambio climatico": "canvi climàtic",
    "playas": "platges",
}
HIGH_PRIORITY = (
    "clim", "ambient", "ecosistem", "biodivers", "emision", "residuo",
    "aguas", "forestal", "nitratos", "contamina", "litoral", "sostenib",
    "transicion energet", "energias renovables", "vertedero", "glifosat",
)


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", (s or "").casefold())
        if not unicodedata.combining(c)
    )


def official_source(s: str) -> bool:
    try:
        target = urlsplit(s)
        return target.scheme == "https" and target.hostname in {
            "www.congreso.es", "congreso.es", "www.boe.es", "boe.es",
        }
    except ValueError:
        return False


def stable_key(row: dict) -> str:
    return hashlib.sha256(("ambient-xv-v1:" + row.get("id", row.get("expedient", ""))).encode()).hexdigest()


def check_unique(rows: list[dict], field: str, count: int, name: str) -> dict[str, dict]:
    found = {}
    for row in rows:
        code = row.get(field, "")
        if not ID.fullmatch(code) or code in found:
            raise ValueError(f"{name}: identificador incorrecte o repetit: {code}")
        found[code] = row
    if len(found) != count:
        raise ValueError(f"{name}: {len(found)} expedients; esperats {count}")
    return found


def load_decisions(data: Path) -> dict[str, dict]:
    files = sorted(data.glob("auditoria_mediambient_lot*.csv"))
    if not files:
        raise ValueError("No existeix cap lot d'auditoria: no inferim decisions dels títols")
    decisions = {}
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter=";")
            if not AUDIT_FIELDS.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Lot amb columnes incompletes: {path.name}")
            for rec in reader:
                code = rec.get("expedient", "").strip()
                status = rec.get("decisio_ambiental", "").strip()
                if not ID.fullmatch(code) or status not in VALID or code in decisions:
                    raise ValueError(f"Lot duplicat o decisió invàlida: {path.name} / {code}")
                if not rec["grau_revision"].strip() or not rec["mesures_identificades"].strip():
                    raise ValueError(f"Manca lectura o grau: {code}")
                if not re.fullmatch(r"20\d\d-\d\d-\d\d", rec["data_auditoria"].strip()):
                    raise ValueError(f"Data de revisió invàlida: {code}")
                if not official_source(rec["font_text_inicial"]):
                    raise ValueError(f"Font inicial no oficial: {code}")
                if not official_source(rec["font_resultat_o_tramit"]):
                    raise ValueError(f"Font de resultat/tramitació no oficial: {code}")
                decisions[code] = dict(rec, lot_auditoria=path.name)
    return decisions


def priority_title(row: dict) -> int:
    title = normalize(row.get("titol_index", ""))
    return sum(3 for term in HIGH_PRIORITY if term in title) + (
        3 if row.get("text_BOCG_localitzat") == "SI" else 0
    )


def signal_title(title: str) -> list[str]:
    title = normalize(title)
    return sorted({label for term, label in SIGNALS.items() if term in title})


def process(data: Path = DATA) -> dict:
    base = read_csv(data / "cua_ambient_xv_830_conciliada.csv")
    universe = read_csv(data / "univers_congres_xv_5094.csv")
    outside = read_csv(data / "fora_cua_xv_4264.csv")
    based = check_unique(base, "expedient", 830, "Cua")
    universed = check_unique(universe, "id", 5094, "Univers")
    outside_ids = check_unique(outside, "id", 4264, "Fora de cua")
    if set(based) | set(outside_ids) != set(universed) or set(based) & set(outside_ids):
        raise ValueError("La cua i els descartats de cribratge no particionen l'univers")
    decisions = load_decisions(data)
    unlocated = set(decisions) - set(based)
    if unlocated:
        raise ValueError("Decisions sense fitxa en la cua: " + ", ".join(sorted(unlocated)))

    augmented = []
    for row in base:
        r = dict(row)
        audit = decisions.get(row["expedient"])
        r.update({field: "" for field in EXTRA})
        if audit:
            r["decisio_ambiental"] = audit["decisio_ambiental"]
            r["decisio_auditoria"] = audit["decisio_ambiental"]
            r["grau_auditoria"] = audit["grau_revision"]
            r["lot_auditoria"] = audit["lot_auditoria"]
            r["subtemes_auditoria"] = audit["subtemes"]
            r["mesures_auditoria"] = audit["mesures_identificades"]
            r["observacions_auditoria"] = audit.get("observacions", "")
            r["font_text_auditoria"] = audit["font_text_inicial"]
            r["font_resultat_auditoria"] = audit["font_resultat_o_tramit"]
            r["data_auditoria"] = audit["data_auditoria"]
        augmented.append(r)
    fields = list(base[0]) + [x for x in EXTRA if x not in base[0]]
    write_csv(data / "inventari_ambient_xv_revisat.csv", augmented, fields)

    # La priorització és una pista de cerca, mai una decisió ambiental.
    pending = [r for r in base if r["expedient"] not in decisions]
    pending.sort(key=lambda r: (-priority_title(r), stable_key(r)))
    lot2 = []
    for r in pending[:40]:
        lot2.append({
            "expedient": r["expedient"], "serie": r["serie"],
            "titol_index": r["titol_index"], "autor_index": r["autor_index"],
            "text_BOCG_localitzat": r["text_BOCG_localitzat"],
            "url_expedient": r["url_expedient"],
            "url_primera_publicacio": r["url_primera_publicacio"],
            "decisio_ambiental": "PENDENT: llegir dispositiu i tràmits",
            "criteri_prioritzacio": "Pistes del títol + disponibilitat de fragment; NO és validació",
        })
    write_csv(data / "cua_lot02_40.csv", lot2, list(lot2[0]))

    # Mostra d'errors de selecció: cap expedient d'aquí es considera exclòs.
    all_out = []
    for row in outside:
        hints = signal_title(row.get("titol_oficial", ""))
        all_out.append({
            "id": row["id"], "serie": row["serie"],
            "titol_oficial": row["titol_oficial"],
            "autor_oficial": row["autor_oficial"],
            "pistes_pel_titol": " | ".join(hints),
            "estat_revisio": "PENDENT: fora de cua no és exclusió ambiental",
            "url_expedient": row["url_expedient"],
            "prioritat": "ALERTA_TITOL" if hints else "CONTROL_ESTRATIFICAT",
        })
    alerts = sorted((r for r in all_out if r["pistes_pel_titol"]),
                    key=lambda r: (-len(r["pistes_pel_titol"].split(" | ")), stable_key(r)))
    controls = sorted((r for r in all_out if not r["pistes_pel_titol"]), key=stable_key)
    # Garantir cobertura de totes les set sèries presents a la mostra (quan sigui possible).
    chosen = []
    for serie in sorted({r["serie"] for r in all_out}):
        choices = [r for r in controls if r["serie"] == serie]
        if choices:
            chosen.append(choices[0])
    seen = {r["id"] for r in chosen}
    for row in alerts[:70] + controls:
        if len(chosen) >= 100:
            break
        if row["id"] not in seen:
            chosen.append(row)
            seen.add(row["id"])
    if len(chosen) != 100:
        raise ValueError("No s'ha pogut construir la mostra de 100 expedients")
    write_csv(data / "control_omissions_fora_cua_xv.csv", all_out, list(all_out[0]))
    write_csv(data / "mostra_control_fora_cua_xv_100.csv", chosen, list(chosen[0]))
    counts = Counter(a["decisio_ambiental"] for a in decisions.values())
    manifest = {
        "versio": 1, "legislatura": "XV", "data_tall": "2026-11-20",
        "univers": len(universe), "cua": len(base), "fora_cua": len(outside),
        "lot_01_i_successius_amb_decisio_individual": len(decisions),
        "inclusions_identificades": counts["INCLOURE"],
        "exclusions_identificades": counts["EXCLOURE"],
        "fronterers_identificats": counts["FRONTERER"],
        "cua_pendent_de_decisio": len(pending),
        "fora_cua_amb_pistes_de_titol": len(alerts),
        "mostra_fora_cua_per_llegir": len(chosen),
        "lots_conservats": sorted({r["lot_auditoria"] for r in decisions.values()}),
        "decisions_historic_19nov": {
            "total_agregat": 34, "inclusions": 19, "exclusions": 10,
            "ambigus": 5, "identificadors": "NO_RECUPERATS",
            "no_sumar_al_total_actual": True,
        },
        "limitacions": [
            "Les quatre decisions individuals actuals poden coincidir amb les 34 decisions anteriors no atribuïbles.",
            "La mostra fora de cua no prova ni completitud ni manca d'omissions.",
            "Pistes dels títols no són lectura documental ni classificació confirmada.",
            "No es publiquen fitxes ni percentatges partidistes automàticament.",
        ],
    }
    (data / "resum_auditoria_ambient_xv.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dades", type=Path, default=DATA)
    args = parser.parse_args()
    print(json.dumps(process(args.dades), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
