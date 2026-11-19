#!/usr/bin/env python3
"""Recupera i audita índexs d'iniciatives del Congrés (XV legislatura).

La sortida és una CUA DE REVISIÓ, mai un conjunt de fitxes verificades.
Cap candidat no es publica automàticament a data/iniciatives.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCE = "https://www.congreso.es/es/busqueda-de-iniciativas"
SERIES = ("161", "162", "122", "120")
ID = re.compile(r"(?<!\d)((?:161|162|122|120)/\d{6})(?:/\d{4})?(?!\d)")
WORDS = (
    "clim", "emision", "emiss", "carbon", "descarbon", "ambient",
    "ecolog", "transicion energet", "energias renovables", "renovables",
    "biodivers", "ecosistem", "especie", "fauna", "flora", "forest",
    "incendio", "bosque", "sequia", "agua", "hidric", "acuifer",
    "humedal", "litoral", "costa", "marino", "marina", "plastico", "residuo",
    "recicl", "vertido", "contamina", "microplastic", "glifosat",
    "agricultura ecologic", "suelo", "desertific", "movilidad sosten",
    "transporte sosten", "emergencia climatic", "inundaci", "pesca sosten",
    "consumo sostenible", "economia circular", "empaquetado",
)


def normalize(s: object) -> str:
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFKD", str(s or "").lower())
                   if not unicodedata.combining(ch))


def official_url(series: str, pagina: int = 1) -> str:
    if series not in SERIES:
        raise ValueError("Sèrie no admesa: " + series)
    params = {
        "p_p_id": "iniciativas", "p_p_lifecycle": "2",
        "p_p_state": "normal", "p_p_mode": "view",
        "p_p_resource_id": "filtrarListado",
        "p_p_cacheability": "cacheLevelPage",
        "_iniciativas_mode": "verListadoIndice",
        "_iniciativas_legislatura": "15", "_iniciativas_tipo": series,
    }
    if pagina < 1:
        raise ValueError("Número de pàgina no vàlid")
    if pagina > 1:
        params["_iniciativas_paginaActual"] = str(pagina)
    return SOURCE + "?" + urlencode(params)


def get_json(url: str, timeout: int = 25) -> object:
    if not url.startswith(SOURCE + "?"):
        raise ValueError("Només es permet el cercador oficial del Congrés")
    req = Request(url, headers={
        "User-Agent": "QueProposen-Research/0.1 (auditoria educativa; consulta puntual)",
        "Accept": "application/json,text/plain,*/*",
    })
    with urlopen(req, timeout=timeout) as res:
        raw = res.read(25 * 1024 * 1024 + 1)
    if len(raw) > 25 * 1024 * 1024:
        raise ValueError("Resposta de més de 25 MB: no s'importa")
    body = raw.decode("utf-8-sig").strip()
    if not body or body[0] not in "[{":
        raise ValueError("La resposta no és JSON; podria haver-hi un error o una pàgina de bloqueig")
    return json.loads(body)


def extract(obj: object) -> list[dict]:
    """Index oficial: claus 'iniciativaN' o variants d'exportació JSON.

    Conservam id, títol, autoria, resultat i data; no inferim el partit
    d'una cadena de text ni si la cerca ha retornat totes les pàgines.
    """
    found: dict[str, dict] = {}
    def walk(val: object, depth: int = 0) -> None:
        if depth > 12:
            return
        if isinstance(val, list):
            for x in val:
                walk(x, depth + 1)
        elif isinstance(val, dict):
            rid = str(val.get("id_iniciativa") or val.get("numeroExpediente")
                      or val.get("numero_expediente") or val.get("expediente")
                      or val.get("num_expediente") or "").strip()
            match = ID.search(rid)
            if match:
                code = match.group(1)
                row = {
                    "id": code,
                    "titol_oficial": str(val.get("titulo") or val.get("titulo_iniciativa")
                                         or val.get("tituloIniciativa") or val.get("title") or ""),
                    "autor_oficial": str(val.get("autor") or val.get("autores") or ""),
                    "resultat_oficial": str(val.get("resultado_tram") or val.get("resultado")
                                            or val.get("situacion") or ""),
                    "data_presentacio": str(val.get("fecha_presentado")
                                            or val.get("fecha_presentacion") or ""),
                }
                previous = found.get(code)
                if not previous or sum(bool(x) for x in row.values()) > sum(bool(x) for x in previous.values()):
                    found[code] = row
            for key, child in val.items():
                if isinstance(child, (dict, list)):
                    walk(child, depth + 1)
    walk(obj)
    return sorted(found.values(), key=lambda r: r["id"])


def candidate(row: dict) -> bool:
    title = normalize(row["titol_oficial"])
    return any(word in title for word in WORDS) or bool(re.search(r"\brio(?:s)?\b", title))


def record_url(id: str) -> str:
    return ("https://www.congreso.es/es/busqueda-de-iniciativas?"
            + urlencode({
                "_iniciativas_id": id,
                "_iniciativas_legislatura": "XV",
                "_iniciativas_mode": "mostrarDetalle",
                "p_p_id": "iniciativas", "p_p_lifecycle": "0",
                "p_p_mode": "view", "p_p_state": "normal",
            }))


def prepare(source_files: list[tuple[str, Path]], out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    allrows: dict[str, dict] = {}
    series_info = {}
    for serie, path in source_files:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = extract(payload)
        rows = [r for r in rows if r["id"].startswith(serie + "/")]
        for row in rows:
            if row["id"] not in allrows:
                allrows[row["id"]] = {**row, "serie": serie,
                                      "possible_ambiental": candidate(row),
                                      "font": record_url(row["id"]),
                                      "verificacio": "PENDENT: revisar text íntegre, autoria i estat"}
        total_declared = int(payload.get("iniciativas_encontradas", 0)) if isinstance(payload, dict) else 0
        if serie not in series_info:
            series_info[serie] = {
                "registres_visibles": 0,
                "registres_declarats_pel_Congres": total_declared,
                "pagines_pendents": True,
                "font": official_url(serie),
                "completitud_no_acreditada": True,
                "fitxers_bruts": [],
            }
        series_info[serie]["registres_visibles"] += len(rows)
        series_info[serie]["fitxers_bruts"].append(path.name)
        series_info[serie]["pagines_pendents"] = (
            series_info[serie]["registres_visibles"] < series_info[serie]["registres_declarats_pel_Congres"]
        )
    ordered = sorted(allrows.values(), key=lambda r: r["id"])
    if not ordered:
        raise ValueError("Cap expedient admissible. Comprova l'estructura de les fonts.")
    campos = ["id","serie","titol_oficial","autor_oficial","resultat_oficial",
              "data_presentacio","possible_ambiental","font","verificacio"]
    with (out / "inventari_index.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ordered)
    queue = [r for r in ordered if r["possible_ambiental"]]
    (out / "candidats_ambientals.json").write_text(
        json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # El resultat no acredita res sobre expedients que NO contenen paraules clau.
    audit = {
        "moment_utc": datetime.now(timezone.utc).isoformat(),
        "legislatura": "XV", "font": "Congrés dels Diputats",
        "series": series_info, "expedients_indexats": len(ordered),
        "candidats_per_titol": len(queue),
        "univers_exhaustiu_verificat": False,
        "limitacions": [
            "L'índex oficial retorna 25 registres per pàgina; cal recuperar les restants abans d'acreditar cobertura.",
            "El filtre de títols pot donar falsos positius i falsos negatius.",
            "Per a qualsevol candidat cal llegir el text dispositiu o articulat.",
            "No es publiquen fitxes automàticament a la web.",
            "Les PNL 161 i 162 i les proposicions de llei 120 i 122 són universos diferents.",
        ],
    }
    (out / "informe_cobertura.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return audit


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--descarrega", action="store_true", help="Obté l'índex oficial del Congrés")
    p.add_argument("--entrada", action="append", nargs=2, metavar=("SERIE", "JSON"),
                   default=[], help="JSON descarregat anteriorment (repetible)")
    p.add_argument("--sortida", type=Path, default=Path("revisio-ambiental"))
    p.add_argument("--pausa", type=float, default=2.0)
    p.add_argument("--totes-les-pagines", action="store_true",
                   help="Recorre l'índex oficial fins al total declarat, si el servidor ho permet")
    p.add_argument("--max-pagines", type=int, default=0,
                   help="Límit de pàgines per sèrie per a proves (0 = totes)")
    args = p.parse_args()
    sources = [(series, Path(path)) for series, path in args.entrada]
    if args.descarrega:
        args.sortida.mkdir(parents=True, exist_ok=True)
        import math
        for series in SERIES:
            seen_this_series = set()
            try:
                first = get_json(official_url(series))
                declared = int(first.get("iniciativas_encontradas", 0))
                if declared < 1:
                    raise ValueError("No hi ha un total declarat al cercador")
                number_pages = math.ceil(declared / 25) if args.totes_les_pagines else 1
                if args.max_pagines > 0:
                    number_pages = min(number_pages, args.max_pagines)
                print(f"Sèrie {series}: total oficial {declared}, pàgines previstes {number_pages}", file=sys.stderr)
                for page in range(1, number_pages + 1):
                    payload = first if page == 1 else get_json(official_url(series, pagina=page))
                    entries = extract(payload)
                    current_ids = {x["id"] for x in entries}
                    if not current_ids:
                        raise ValueError(f"Pàgina {page}: cap expedient reconegut")
                    if seen_this_series.intersection(current_ids):
                        raise ValueError(
                            f"Pàgina {page}: el servidor repeteix expedients d'una pàgina anterior; "
                            "la paginació no és correcta"
                        )
                    seen_this_series.update(current_ids)
                    dest = args.sortida / f"index_{series}_pagina_{page:03d}.json"
                    dest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                    sources.append((series, dest))
                    print(f"Sèrie {series}, pàgina {page}/{number_pages}: {len(entries)} registres", file=sys.stderr)
                    if page < number_pages:
                        time.sleep(max(args.pausa, 0))
                if args.totes_les_pagines and len(seen_this_series) != declared:
                    print(
                        f"ATENCIÓ sèrie {series}: esperats {declared}, recuperats {len(seen_this_series)}",
                        file=sys.stderr
                    )
            except (ValueError, HTTPError, URLError, TimeoutError, OSError) as exc:
                print(f"ADVERTIMENT: la sèrie {series} ha quedat incompleta: {exc}", file=sys.stderr)
            time.sleep(max(args.pausa, 0))
    if not sources:
        p.error("Indica --descarrega o, per a una prova local, --entrada SERIE FITXER.json")
    try:
        audit = prepare(sources, args.sortida)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("ERROR d'importació:", exc, file=sys.stderr)
        return 1
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
