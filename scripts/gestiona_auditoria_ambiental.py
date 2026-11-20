#!/usr/bin/env python3
"""Registre auditable i pla de revisió de Medi Ambient (XV legislatura).

No converteix paraules clau en decisions editorials i NO modifica el portal.
Les decisions signades es llegeixen de data/treball/auditoria_mediambient_lot*.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data" / "treball"
PATTERN = re.compile(r"^(120|122|123|124|125|161|162)/[0-9]{6}$")
DECISIONS = {"INCLOURE", "EXCLOURE", "FRONTERER"}
REQUIRED_DECISION = {
    "expedient", "decisio_ambiental", "grau_revision", "instrument",
    "subtemes", "mesures_identificades", "observacions",
    "font_text_inicial", "font_resultat_o_tramit", "data_auditoria",
}

# NOMÉS prioritza lectures; no pressuposa que un títol sigui ambiental.
KEYWORDS = {
    "canvi climatic": 6, "cambio climatico": 6, "biodiversidad": 6,
    "biodiversitat": 6, "medio ambiente": 5, "medioambient": 5,
    "ambiental": 5, "glifosato": 6, "ecocidio": 6, "contaminacion": 5,
    "residuos": 5, "emisiones": 5, "vertidos": 5, "sequia": 5,
    "incendios forestales": 6, "zona de bajas emisiones": 6,
    "zonas de bajas emisiones": 6, "aguas residuales": 6,
    "plasticos": 4, "transicion energetica": 4, "inundaciones": 5,
    "costa": 2, "litoral": 3, "agua": 2, "energia": 2,
    "sostenible": 2, "agricultura": 1, "movilidad": 2, "pesca": 1,
}

def normalize(value: object) -> str:
    raw = unicodedata.normalize("NFKD", str(value or "").casefold())
    return "".join(ch for ch in raw if not unicodedata.combining(ch))

def keywords(text: str) -> tuple[int, list[str]]:
    raw = normalize(text)
    found = [word for word in KEYWORDS if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", raw)]
    return sum(KEYWORDS[word] for word in found), found

def read_csv(path: Path, delimiter: str = ",") -> list[dict]:
    if not path.is_file():
        raise ValueError("No es troba el fitxer: " + str(path))
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError("CSV sense capçalera: " + str(path))
        return list(reader)

def unique(rows: list[dict], column: str, name: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        code = str(row.get(column, "")).strip()
        if not PATTERN.fullmatch(code):
            raise ValueError(name + ": identificador invàlid: " + repr(code))
        if code in result:
            raise ValueError(name + ": duplicat: " + code)
        result[code] = row
    return result

def official_url(value: str) -> bool:
    url = urlparse(value.strip())
    hostname = (url.hostname or "").lower()
    return url.scheme == "https" and (
        hostname in {"congreso.es", "www.congreso.es", "app.congreso.es",
                     "boe.es", "www.boe.es"} or
        hostname.endswith(".congreso.es")
    )

def load_decisions(directory: Path) -> dict[str, dict]:
    decisions = {}
    for path in sorted(directory.glob("auditoria_mediambient_lot*.csv")):
        for row in read_csv(path, delimiter=";"):
            if not REQUIRED_DECISION.issubset(row):
                raise ValueError(path.name + ": falten camps obligatoris")
            code = row["expedient"].strip()
            if not PATTERN.fullmatch(code) or code in decisions:
                raise ValueError(path.name + ": ID invàlid o repetit: " + code)
            decision = row["decisio_ambiental"].strip()
            if decision not in DECISIONS:
                raise ValueError(path.name + ": decisió no admesa: " + decision)
            if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", row["data_auditoria"].strip()):
                raise ValueError(path.name + ": data no ISO: " + code)
            if decision == "INCLOURE" and not row["mesures_identificades"].strip():
                raise ValueError(path.name + ": inclusió sense mesures: " + code)
            if not row["observacions"].strip() or not official_url(row["font_text_inicial"]):
                raise ValueError(path.name + ": falta nota o font oficial: " + code)
            url_resultat = row["font_resultat_o_tramit"].strip()
            if url_resultat and not official_url(url_resultat):
                raise ValueError(path.name + ": font de tramitació no oficial: " + code)
            row["lot_origen"] = path.name
            decisions[code] = row
    return decisions

def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def make_plan(work: Path = WORK, lot_size: int = 40, control_per_serie: int = 8) -> dict:
    if lot_size < 1 or control_per_serie < 1:
        raise ValueError("La mida dels lots i els controls ha de ser positiva")
    universe = unique(read_csv(work / "univers_congres_xv_5094.csv"), "id", "univers")
    queue_path = work / "cua_ambient_xv_830_conciliada.csv"
    if not queue_path.is_file():
        queue_path = work / "inventari_ambient_xv_830.csv"
    queue = unique(read_csv(queue_path), "expedient", "cua")
    decisions = load_decisions(work)
    if (len(universe), len(queue)) != (5094, 830):
        raise ValueError("Univers/cua diferents de 5094/830: " + repr((len(universe), len(queue))))
    if set(queue) - set(universe):
        raise ValueError("Cua amb identificadors absents de l'univers")
    if set(decisions) - set(queue):
        raise ValueError("Decisió sense expedient a la cua: " + repr(sorted(set(decisions) - set(queue))))
    if len(universe) - len(queue) != 4264:
        raise ValueError("No quadren els expedients fora de cua")
    details = []
    for code, source in queue.items():
        official = universe[code]
        title = source.get("titol_index") or official.get("titol_oficial") or source.get("titol_web") or ""
        score, matches = keywords(title)
        reviewed = decisions.get(code)
        if reviewed:
            label = reviewed["decisio_ambiental"]
            grade = reviewed["grau_revision"]
        else:
            label = "PENDENT"
            grade = "NO_REVISAT_INDIVIDUALMENT"
        details.append({
            "expedient": code,
            "serie": code.split("/")[0],
            "titol_oficial": official.get("titol_oficial", ""),
            "autor_oficial": official.get("autor_oficial", ""),
            "resultat_index": official.get("resultat_oficial", ""),
            "font_index": official.get("url_expedient", ""),
            "decisio_ambiental": label,
            "grau_revision": grade,
            "lot_decisio": reviewed.get("lot_origen", "") if reviewed else "",
            "font_text_auditada": reviewed.get("font_text_inicial", "") if reviewed else "",
            "font_tramit_auditada": reviewed.get("font_resultat_o_tramit", "") if reviewed else "",
            "incidencia_documental": source.get("incidencia", ""),
            "fragment_BOCG_localitzat": source.get("text_BOCG_localitzat", ""),
            "prioritat_lectura": str(score),
            "pistes_al_titol": " | ".join(matches),
            "lot_pendent": "",
        })

    # Qualsevol criteri de prioritat és auxiliar: la decisió sempre és humana/documental.
    pending = sorted((r for r in details if r["decisio_ambiental"] == "PENDENT"),
                     key=lambda r: (-int(r["prioritat_lectura"]),
                                    r["incidencia_documental"] != "",
                                    r["expedient"]))
    for i, row in enumerate(pending):
        row["lot_pendent"] = f"L{1 + i // lot_size:03d}"
    details.sort(key=lambda r: (int(r["serie"]), int(r["expedient"].split("/")[1])))
    columns = list(details[0])
    write_csv(work / "registre_auditoria_ambient_xv.csv", details, columns)
    write_csv(work / "pla_lots_ambient_xv.csv", pending, columns)

    # Control de falsos negatius: no s'exclouen expedients automàticament.
    outside = [v for k, v in universe.items() if k not in queue]
    by_series = defaultdict(list)
    for source in outside:
        score, terms = keywords(source.get("titol_oficial", ""))
        by_series[source["serie"]].append((score, source, terms))
    controls = []
    for serie in sorted(by_series):
        group = sorted(by_series[serie], key=lambda x: (-x[0], x[1]["id"]))
        candidates = group[:min(15, len(group))]
        # Mostra determinista en cada sèrie; no es presenta com a mostra aleatòria.
        remainder = [g for g in group if g not in candidates]
        if remainder:
            step = max(1, len(remainder) // control_per_serie)
            controls_serie = remainder[::step][:control_per_serie]
        else:
            controls_serie = []
        for reason, entries in (("ALERTA_TERMINOLOGICA", candidates),
                                ("CONTROL_SISTEMATIC", controls_serie)):
            for score, source, terms in entries:
                controls.append({
                    "expedient": source["id"],
                    "serie": serie,
                    "titol_oficial": source.get("titol_oficial", ""),
                    "autor_oficial": source.get("autor_oficial", ""),
                    "resultat_index": source.get("resultat_oficial", ""),
                    "motiu_control": reason,
                    "prioritat_lectura": str(score),
                    "pistes_al_titol": " | ".join(terms),
                    "estat": "PENDENT: verificar possibles omissions",
                    "url_expedient": source.get("url_expedient", ""),
                })
    control_columns = list(controls[0]) if controls else []
    write_csv(work / "control_omissions_ambient_xv.csv", controls, control_columns)

    count = Counter(r["decisio_ambiental"] for r in details)
    grades = Counter(r["grau_revision"] for r in details if r["decisio_ambiental"] != "PENDENT")
    summary = {
        "legislatura": "XV",
        "data_execucio_logica": "2026-11-20",
        "univers": len(universe),
        "cua": len(queue),
        "fora_cua_no_exclosos": len(outside),
        "decisions_amb_id": len(decisions),
        "inclusions_documentades": count["INCLOURE"],
        "exclusions_documentades": count["EXCLOURE"],
        "casos_fronterers": count["FRONTERER"],
        "pendents_cua": count["PENDENT"],
        "per_grau_revision": dict(grades),
        "lots_pendents": max((int(x["lot_pendent"][1:]) for x in pending), default=0),
        "mida_maxima_lot": lot_size,
        "controls_omissions_seleccionats": len(controls),
        "controls_omissions_revisats": 0,
        "decisions_historic_34": "NO RECUPERADES PER ID. NO sumades a les decisions documentades.",
        "cobertura_ambiental_exhaustiva": False,
        "comparacions_partidistes_permeses": False,
        "portal_public_alterat": False,
        "advertiment": "La prioritat lèxica no és una classificació. Les 4.264 entrades fora de cua no són exclusions.",
    }
    (work / "estat_auditoria_ambient_xv.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treball", type=Path, default=WORK)
    parser.add_argument("--mida-lot", type=int, default=40)
    parser.add_argument("--controls-per-serie", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(make_plan(args.treball, args.mida_lot, args.controls_per_serie),
                     indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
