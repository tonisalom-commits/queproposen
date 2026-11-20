#!/usr/bin/env python3
"""Sondeig traçable dels quatre expedients pendents, sense classificació automàtica.

Guarda diagnòstics HTTP, enllaços i indicis que un text es pugui llegir.
El fet que un número aparegui a un BOCG no demostra que l'articulat hi sigui.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "treball" / "recuperacio_4_pendents_xv_2026-11-20.json"
CODES = ["120/000034", "120/000043", "161/003710", "161/003820"]
DOCS = {"120/000034": "BOCG-15-D-407", "120/000043": "BOCG-15-D-493"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.href = None
        self.anchor_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.anchor_text = []

    def handle_data(self, data):
        if data.strip():
            self.text.append(data)
            if self.href is not None:
                self.anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            if self.href:
                self.links.append((html.unescape(" ".join(self.anchor_text)), self.href))
            self.href = None
            self.anchor_text = []


def permitted(url):
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in {"www.congreso.es", "congreso.es"}


def detail_url(code):
    return (
        "https://www.congreso.es/es/busqueda-de-iniciativas"
        "?_iniciativas_id=" + quote(code, safe="") +
        "&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle"
        "&p_p_id=iniciativas&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view"
    )


def request_page(url):
    if not permitted(url):
        raise ValueError("URL no autoritzada")
    req = Request(url, headers={"User-Agent": "QueProposen-AuditoriaDocumental/1.0",
                                "Accept": "text/html,application/xhtml+xml"})
    try:
        with urlopen(req, timeout=20) as response:
            original = response.read(2_000_001)
            code = response.status
            mime = response.headers.get("Content-Type", "")
            final_url = response.geturl()
        if len(original) > 2_000_000:
            raise ValueError("Resposta HTML massa gran")
        if not permitted(final_url):
            raise ValueError("Redireccio fora del domini oficial")
        text = original.decode("utf-8", "replace")
        parsed = Page()
        parsed.feed(text)
        plain = re.sub(r"\s+", " ", html.unescape(" ".join(parsed.text)))
        anchors = [(name, urljoin(final_url, href)) for name, href in parsed.links]
        anchors = [dict(titol=name[:140], url=link) for name, link in anchors
                   if permitted(link) and
                   ("texto" in name.lower() or "pdf" in name.lower()
                    or "bocg" in name.lower() or "pdf" in link.lower())]
        return {
            "obtingut": True, "http": code, "mime": mime,
            "url": final_url, "sha256_html": hashlib.sha256(original).hexdigest(),
            "llargada_text": len(plain), "enllacos_publicacio": anchors[:30],
            "text_normalitzat": plain
        }
    except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
        return {"obtingut": False, "url": url,
                "error": (type(exc).__name__ + ": " + str(exc))[:250]}


def record(code, url, kind):
    result = request_page(url)
    plain = result.pop("text_normalitzat", "")
    pos = plain.find(code)
    if pos >= 0:
        result["ocurrencies_id"] = len(list(re.finditer(re.escape(code), plain)))
        # L'extracte és una pista contextual, NO una prova d'articulat.
        result["fragment_curt"] = plain[max(0, pos - 120):pos + 1800]
    else:
        result["ocurrencies_id"] = 0
        result["fragment_curt"] = ""
    result["tipus_consulta"] = kind
    result["codi"] = code
    result["lectura_dispositiu_certificada"] = False
    return result


def main():
    allrows = []
    for code in CODES:
        allrows.append(record(code, detail_url(code), "fitxa_expedient"))
        time.sleep(0.8)
        if code in DOCS:
            source = DOCS[code]
            url = ("https://www.congreso.es/en/busqueda-de-publicaciones"
                   "?_publicaciones_id_texto=%28" + source + ".CODI.%29"
                   "&_publicaciones_legislatura=XV"
                   "&_publicaciones_mode=mostrarTextoIntegro"
                   "&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view"
                   "&p_p_state=normal")
            allrows.append(record(code, url, "bocg_tramit_inicial"))
            time.sleep(0.8)
    out = {
        "generat": datetime.now(timezone.utc).isoformat(),
        "finalitat": "Localitzar fonts primaries que permetin lectura futura",
        "advertiment": (
            "No hi ha classificacio automatica. La lectura de cada dispositiu"
            " exigeix verificar-ne exactament els punts o l'articulat. "
            "Un text HTTP obtingut no equival a document verificat."
        ),
        "expedients": CODES,
        "consultes": allrows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "destinacio": str(OUT), "consultes": len(allrows),
        "respostes_obtingudes": sum(r["obtingut"] for r in allrows),
        "amb_tractament_automatic_complet": 0
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
