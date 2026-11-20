#!/usr/bin/env python3
"""Localitza extractes OFICIALS de la cua ampliada per accelerar lectura humana.

No classifica expedients. Un passatge recuperat no equival a lectura íntegra del
dispositiu, esmena o resultat. Escriu errors explícits i hash de font.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from scripts.integra_auditoria_ambient_xv import DATA, read_csv, write_csv

PATTERN = re.compile(r"(?<!\d)(?:120|122|123|124|125|161|162)/\d{6}(?!\d)")
URL_BOCG = re.compile(r"BOCG-15-(?:D|B|CG-A)-[0-9]+(?:-[0-9A-Za-z]+)?")
UA = "QueProposen-Corpus-Auditoria/1.1 (recerca parlamentar)"
MAX_HTML = 5_000_000
MAX_SNIPPET = 4800
MAX_CONTEXT = 30000
DISPOSITIVE_PATTERNS = (
    ("CONGRES_INSTA", re.compile(r"\b(?:El\s+)?Congreso\s+de\s+los\s+Diputados\s+insta\s+al\s+Gobierno\b", re.I)),
    ("CORTES_INSTAN", re.compile(r"\b(?:Las\s+)?Cortes\s+Generales\s+instan\s+al\s+Gobierno\b", re.I)),
    ("COMISSIO_INSTA", re.compile(r"\b(?:La\s+)?Comisi[oó]n\s+Mixta\s+insta\s+al\s+Gobierno\b", re.I)),
    ("ARTICLE_LLEI", re.compile(r"\bArt[ií]culo\s+[uú]nico\b|\bArt[ií]culo\s+1\b", re.I)),
)



def allowed(url):
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in ("www.congreso.es", "congreso.es")


class Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.anchors = []
        self.active = None
        self.ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.ignore += 1
        if tag == "a":
            self.active = [dict(attrs).get("href"), []]

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.ignore = max(0, self.ignore - 1)
        if tag == "a" and self.active:
            self.anchors.append((self.active[0], " ".join(self.active[1])))
            self.active = None

    def handle_data(self, data):
        if not self.ignore:
            self.parts.append(data)
            if self.active and self.active[0]:
                self.active[1].append(data)


def fetch_html(url):
    if not allowed(url):
        raise ValueError("Domini fora del Congres")
    request = Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"})
    with urlopen(request, timeout=25) as response:
        final = response.geturl()
        if not allowed(final):
            raise ValueError("Redireccio fora de domini")
        raw = response.read(MAX_HTML + 1)
        if len(raw) > MAX_HTML:
            raise ValueError("Font massa gran")
        kind = response.headers.get("Content-Type", "")
    if "html" not in kind and b"<html" not in raw[:600].lower():
        raise ValueError("La font no es HTML")
    dom = Extract()
    dom.feed(raw.decode("utf-8", errors="replace"))
    text = re.sub(r"\s+", " ", unescape(" ".join(dom.parts))).strip()
    return {
        "url": final, "hash": hashlib.sha256(raw).hexdigest(),
        "text": text, "links": dom.anchors,
    }


def find_bulletin(page):
    candidates = []
    for href, label in page["links"]:
        if not href:
            continue
        url = urljoin(page["url"], unescape(href))
        if not allowed(url) or not URL_BOCG.search(url):
            continue
        if "texto" in label.casefold() or "text" in label.casefold():
            candidates.append(url)
    return candidates[0] if candidates else None


def discover(row):
    data = {
        "id": row["id"], "serie": row["serie"],
        "titol_oficial": row["titol_oficial"],
        "categories_pista": row["categories_pista"],
        "url_expedient": row["url_expedient"],
        "url_bocg": "", "sha256_detall": "", "sha256_publicacio": "",
        "ocurrencies_id_publicacio": 0,
        "fragment_de_treball_no_validat": "",
        "finestra_dispositiu_possible": "",
        "tipus_senyal_dispositiu": "",
        "estat_recuperacio": "PENDENT",
        "error": "",
        "decisio_ambiental": "",
    }
    try:
        detail = fetch_html(row["url_expedient"])
        data["sha256_detall"] = detail["hash"]
        link = find_bulletin(detail)
        if not link:
            data["estat_recuperacio"] = "SENSE_BOCG_EN_DETALL"
            return data
        data["url_bocg"] = link
        data["estat_recuperacio"] = "BOCG_LOCALITZAT"
    except Exception as e:
        data["estat_recuperacio"] = "ERROR_DETALL"
        data["error"] = f"{type(e).__name__}: {str(e)}"[:300]
    return data


def snippet(text, code):
    matches = list(re.finditer(re.escape(code), text))
    if not matches:
        return "", 0
    # Primera menció sol ser índex. Guardam fragment més llarg de la darrera
    # aparició; NO pressuposa que inclogui tot el dispositiu.
    location = matches[-1].start()
    following = text[location:location + MAX_SNIPPET + 120]
    next_id = PATTERN.search(following[len(code) + 280:])
    if next_id:
        following = following[: len(code) + 280 + next_id.start()]
    return following[:MAX_SNIPPET], len(matches)


def possible_dispositive(text, code):
    """Tram de possible mandat; MAI lectura certificada per coincidencia regex."""
    matches = list(re.finditer(re.escape(code), text))
    if not matches:
        return "", ""
    start = matches[-1].start()
    remaining = text[start:start + MAX_CONTEXT]
    other = PATTERN.search(remaining[len(code) + 300:])
    if other:
        remaining = remaining[:len(code) + 300 + other.start()]
    found = []
    for name, pattern in DISPOSITIVE_PATTERNS:
        found.extend((m.start(), name) for m in pattern.finditer(remaining))
    if not found:
        return "", ""
    # La coincidencia mes tardana sol ser el mandat final, no un passatge
    # citat al preambul. Aixo es heuristica, no garantia documental.
    position, name = max(found, key=lambda item: item[0])
    return name, remaining[position:position + 3800]


def collect(rows, workers=3, pause=0.15):
    if workers not in (1, 2, 3):
        raise ValueError("Concurrencia limitada a 3")
    raw = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, val in enumerate(pool.map(discover, rows), start=1):
            raw[val["id"]] = val
            if pause:
                time.sleep(pause)
            if i % 10 == 0:
                print("FITXES", i, "/", len(rows), flush=True)
    bocg = sorted({r["url_bocg"] for r in raw.values() if r["url_bocg"]})
    documents = {}
    def download(url):
        try:
            page = fetch_html(url)
            return url, page, None
        except Exception as e:
            return url, None, f"{type(e).__name__}: {e}"[:300]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for fut in as_completed({pool.submit(download, url) for url in bocg}):
            url, page, error = fut.result()
            documents[url] = (page, error)
    for r in raw.values():
        url = r["url_bocg"]
        if not url:
            continue
        page, err = documents[url]
        if err:
            r["estat_recuperacio"] = "ERROR_BOCG"
            r["error"] = err
        else:
            r["sha256_publicacio"] = page["hash"]
            fragment, occurrences = snippet(page["text"], r["id"])
            r["ocurrencies_id_publicacio"] = occurrences
            r["fragment_de_treball_no_validat"] = fragment
            kind, text_candidate = possible_dispositive(page["text"], r["id"])
            r["tipus_senyal_dispositiu"] = kind
            r["finestra_dispositiu_possible"] = text_candidate
            r["estat_recuperacio"] = "FRAGMENT_CANDIDAT" if fragment else "NO_APAREIX_ID_AL_BOCG"
    return [raw[row["id"]] for row in rows], len(bocg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dades", type=Path, default=DATA)
    parser.add_argument("--max", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.max <= 50:
        raise ValueError("Pilot de 1-50 expedients")
    rows = read_csv(args.dades / "cua_ampliada_fora_cua_xv_250.csv")[:args.max]
    if not rows:
        raise ValueError("Cua ampliada buida o inexistent")
    result, unique_documents = collect(rows)
    out = args.dades / "fragments_pilot_fora_cua_xv_30.csv"
    fields = [
        "id", "serie", "titol_oficial", "categories_pista",
        "url_expedient", "url_bocg", "sha256_detall", "sha256_publicacio",
        "ocurrencies_id_publicacio", "fragment_de_treball_no_validat",
        "tipus_senyal_dispositiu", "finestra_dispositiu_possible",
        "estat_recuperacio", "error", "decisio_ambiental",
    ]
    write_csv(out, result, fields)
    counts = {kind: sum(x["estat_recuperacio"] == kind for x in result)
              for kind in sorted({x["estat_recuperacio"] for x in result})}
    info = {
        "data_execucio": datetime.now(timezone.utc).isoformat(),
        "expedients_pilot": len(result), "butlletins_diferents": unique_documents,
        "estats": counts, "fitxer": out.name,
        "amb_finestra_dispositiu_possible": sum(bool(r["finestra_dispositiu_possible"]) for r in result),
        "advertiment": (
            "FRAGMENT_CANDIDAT indica solament un passatge HTML del BOCG;"
            " NO que s'hagi llegit el dispositiu o el text definitiu. "
            "Sense decisions ni aprovacions imputades automaticament."
        ),
    }
    (args.dades / "resum_fragments_pilot_fora_cua_xv.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
