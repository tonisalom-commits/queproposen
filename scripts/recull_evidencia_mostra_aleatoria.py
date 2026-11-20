#!/usr/bin/env python3
"""Recupera evidència textual OFICIAL per a la mostra aleatòria estratificada XV.

NO classifica ni verifica cap iniciativa. Captura fragments del document
del Congrés per facilitar lectura individual. Manté intacte l'univers.
"""
from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlencode

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / "data" / "treball"
EXP_RE = re.compile(r"(?:120|122|123|124|125|161|162)/\d{6}")
HEADERS = {
    "User-Agent": "queproposen-educational-audit/1.0 (documentary review, XV legislature)",
    "Accept": "text/html,application/xhtml+xml,*/*",
}
OUT_FIELDS = [
    "id", "serie", "titol_oficial", "url_expedient", "estat_actual",
    "detall_lectura", "text_original_lectura", "url_primera_publicacio",
    "ocurrencies_id", "sha256_detall", "sha256_bocg",
    "fragment_original", "incidencia",
]


def read(path, delimiter=","):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def get(url, tries=3):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in {
        "www.congreso.es", "congreso.es",
    }:
        raise ValueError("URL no oficial: " + url)
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(url, timeout=25, headers=HEADERS)
            r.raise_for_status()
            raw = r.content
            if len(raw) > 5_500_000:
                raise ValueError("Pàgina massa gran")
            if b"<html" not in raw[:1000].lower() and b"<!doctype" not in raw[:1000].lower():
                raise ValueError("La pàgina no és HTML")
            return raw
        except (requests.RequestException, ValueError) as exc:
            last = exc
            time.sleep(0.8 + attempt * 1.8)
    raise RuntimeError(str(last))


def source_url(code):
    return ("https://www.congreso.es/es/busqueda-de-iniciativas?" + urlencode({
        "_iniciativas_id": code, "_iniciativas_legislatura": "XV",
        "_iniciativas_mode": "mostrarDetalle", "p_p_id": "iniciativas",
        "p_p_lifecycle": "0", "p_p_state": "normal", "p_p_mode": "view",
    }))


def extract_section(text, code):
    indices = [m.start() for m in re.finditer(re.escape(code), text)]
    if not indices:
        return "", 0
    for pos in indices[1:] + indices[:1]:
        snippet = text[pos: pos + 16000]
        # La capçalera o índex no és el dispositiu. Es prefereix el passatge
        # que segueix l'expedient amb un encapçalament de proposta.
        head = snippet[:2600].casefold()
        if any(token in head for token in (
            "proposición no de ley", "proposición de ley", "proposicion no de ley",
            "proposicion de ley", "artículo único", "articulo unico",
        )):
            next_code = EXP_RE.search(snippet, len(code) + 200)
            if next_code and next_code.start() > 1100:
                snippet = snippet[:next_code.start()]
            return snippet[:11000], len(indices)
    return text[indices[-1]: indices[-1] + 11000], len(indices)


def capture(row):
    code = row["id"]
    result = dict.fromkeys(OUT_FIELDS, "")
    result.update({
        "id": code, "serie": row["serie"], "titol_oficial": row["titol_oficial"],
        "url_expedient": row.get("url_expedient") or source_url(code),
        "estat_actual": row.get("estat_revision", ""),
        "detall_lectura": "NO", "text_original_lectura": "NO",
        "ocurrencies_id": 0,
    })
    try:
        raw = get(result["url_expedient"])
        result["sha256_detall"] = hashlib.sha256(raw).hexdigest()
        soup = BeautifulSoup(raw, "html.parser")
        first = []
        for link in soup.select("a[href]"):
            label = link.get_text(" ", strip=True).casefold()
            href = urljoin(result["url_expedient"], link.get("href", ""))
            if urlsplit(href).hostname not in ("www.congreso.es", "congreso.es"):
                continue
            if "texto íntegro" in label or "texto integro" in label or "texto íntegro" in href:
                if "BOCG" in href and href not in first:
                    first.append(href)
        result["detall_lectura"] = "SI"
        if not first:
            result["incidencia"] = "Cap enllaç de BOCG dins la fitxa original"
            return result
        url = first[0]
        result["url_primera_publicacio"] = url
        bulletin = get(url)
        result["sha256_bocg"] = hashlib.sha256(bulletin).hexdigest()
        bulletin_soup = BeautifulSoup(bulletin, "html.parser")
        for node in bulletin_soup(["script", "style", "noscript"]):
            node.decompose()
        txt = bulletin_soup.get_text(" ", strip=True)
        excerpt, count = extract_section(txt, code)
        result["ocurrencies_id"] = count
        result["fragment_original"] = excerpt
        result["text_original_lectura"] = "SI" if len(excerpt) > 100 else "NO"
        if len(excerpt) < 100:
            result["incidencia"] = "Text oficial obtingut però fragment no atribuïble"
    except Exception as exc:
        result["incidencia"] = type(exc).__name__ + ": " + str(exc)[:240]
    return result


def main():
    sample = read(ROOT / "mostra_aleatoria_fora_cua_xv_100.csv")
    already = set()
    for p in ROOT.glob("auditoria_mediambient_lot*.csv"):
        for r in read(p, ";"):
            already.add(r["expedient"])
    remaining = [r for r in sample if r["id"] not in already]
    if len(sample) != 100 or len(remaining) > 100 or len({x["id"] for x in sample}) != 100:
        raise ValueError("Mostra aleatòria invàlida")
    print("Expedients pendents de recuperar:", len(remaining), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        evidence = list(executor.map(capture, remaining))
    evidence.sort(key=lambda x: (int(x["serie"]), x["id"]))
    path = ROOT / "evidencia_mostra_aleatoria_fora_cua_xv.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=OUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(evidence)
    manifest = {
        "data": datetime.now(timezone.utc).isoformat(),
        "poblacio_fora_cua": 4264, "mostra": 100,
        "ja_auditats": len(already.intersection({r["id"] for r in sample})),
        "pendents_al_comencament": len(remaining),
        "fitxes_recuperades": sum(r["detall_lectura"] == "SI" for r in evidence),
        "fragments_obtinguts": sum(r["text_original_lectura"] == "SI" for r in evidence),
        "incidencies": [
            {"id": r["id"], "error": r["incidencia"]} for r in evidence if r["incidencia"]
        ],
        "advertiment": (
            "Evidència automàtica de fonts oficials, no revisió humana. "
            "Cap fila sense lectura i decisió individual no es considera auditada."
        ),
    }
    (ROOT / "resum_evidencia_mostra_aleatoria_xv.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
