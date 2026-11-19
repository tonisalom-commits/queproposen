#!/usr/bin/env python3
"""Diagnòstic *no publicador* de la paginació del cercador oficial.

No fa una descàrrega massiva. Prova un conjunt petit de convencions i
conserva únicament metadades per trobar la pàgina 26-50 de 161.
"""
from __future__ import annotations
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
from urllib.request import Request, urlopen
from recull_index_congres import official_url, extract


def fetch(url: str) -> tuple[str, str]:
    req = Request(url, headers={"User-Agent": "QueProposen-Research/0.1 (diagnostic paginacio)",
                                "Accept": "application/json,text/html,*/*"})
    try:
        with urlopen(req, timeout=14) as res:
            return res.read(180_000).decode("utf-8-sig", errors="replace"), res.headers.get("Content-Type","")
    except Exception as ex:
        return "ERROR "+str(ex)[:150], ""


def inspect_json(payload: str) -> dict:
    try:
        d=json.loads(payload)
        rows=extract(d)
        return {
            "json": True,
            "iniciativa_primera": rows[0]["id"] if rows else None,
            "iniciativa_darrera": rows[-1]["id"] if rows else None,
            "registres": len(rows),
            "docs_ini": d.get("paginacion",{}).get("docs_ini"),
            "docs_fin": d.get("paginacion",{}).get("docs_fin"),
        }
    except (ValueError, TypeError, AttributeError):
        return {"json": False, "resposta_inici": payload[:100]}


def main() -> None:
    base=official_url("161")
    original,typ=fetch(base)
    variants=[
        ("_iniciativas_docs_ini","26"),("_iniciativas_docs_fin","50"),
        ("_iniciativas_doc_ini","26"),("_iniciativas_start","26"),
        ("_iniciativas_pagina","2"),("_iniciativas_page","2"),
        ("_iniciativas_doc","26-50"),("_iniciativas_paginacion","26-50"),
        ("page","2"),("cur","2"),("delta","25")
    ]
    results=[{"prova":"original","tipus":typ,**inspect_json(original)}]
    for k,v in variants:
        u=base+"&"+urlencode({k:v})
        content,content_type=fetch(u)
        results.append({"prova":k+"="+v,"tipus":content_type,**inspect_json(content)})
        time.sleep(0.4)
    # Formulari CGI antic amb l'interval de documents del mateix índex
    query='("161").SINI.+Y+I.ACIN1.'
    cgi="https://www.congreso.es/wc/servidorCGI"
    for docs in ("26-50","26","26:50"):
        qs=urlencode({"CMD":"VERLST","FMT":"INITZLUS.fmt","FORM1":"INITZLUS.fmt",
                      "BASE":"IW15","QUERY":query,"DOCS":docs,"DOCORDER":"FIFO"})
        content,ctype=fetch(cgi+"?"+qs)
        results.append({"prova":"CGI DOCS="+docs,"tipus":ctype,
                        "resposta_inici":re.sub(r"\s+"," ",content[:120])})
        time.sleep(.4)
    # Font HTML del portal, per detectar el nom exacte de paràmetres.
    page,ctype=fetch("https://www.congreso.es/es/busqueda-de-iniciativas")
    patterns=re.findall(r".{0,140}(?:paginar|paginacion|filtrarListado|docs_ini|docs_fin|pagina).{0,170}",
                        page, flags=re.I)
    out={"resultats":results,"fragments_paginacio":patterns[:35]}
    dest=Path("revisio-ambiental/proves_paginacio.json")
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for entry in results:
        print(entry["prova"],entry.get("iniciativa_primera"),entry.get("docs_ini"),entry.get("resposta_inici","")[:90])


if __name__=="__main__":
    main()
