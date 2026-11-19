#!/usr/bin/env python3
"""Completa la sèrie 162, amb reintents per als errors intermitents HTTP 200."""
from __future__ import annotations
import json
import math
import random
import sys
import time
from pathlib import Path
from scripts.recull_index_congres import official_url,get_json,extract,prepare

OUT=Path("revisio-162")
OUT.mkdir(parents=True, exist_ok=True)
SERIE="162"
MAX_RETRIES=7
first=None
try:
    for attempt in range(MAX_RETRIES):
        try:
            first=get_json(official_url(SERIE))
            if not extract(first):
                raise ValueError("L'índex no té iniciatives")
            break
        except Exception as exc:
            print(f"pàgina 1: intent {attempt+1}, {exc}", file=sys.stderr, flush=True)
            time.sleep(2 + attempt * 2)
    if first is None or not extract(first):
        raise ValueError("No s'ha recuperat la primera pàgina")
    total=int(first.get("iniciativas_encontradas",0))
    pages=math.ceil(total/25)
    print("Total declarat",total,"pàgines",pages,flush=True)
    seen=set()
    sources=[]
    failed=[]
    for page in range(1,pages+1):
        current=None
        for attempt in range(MAX_RETRIES):
            try:
                current=first if page==1 else get_json(official_url(SERIE,page))
                records=extract(current)
                if len(records)<(25 if page<pages else total-(pages-1)*25):
                    raise ValueError("Resposta sense registres suficients: "+
                                     str(current.get("error") if isinstance(current,dict) else ""))
                codes={r["id"] for r in records}
                if seen & codes:
                    raise ValueError("Pàgina duplicada; fitxer no acceptat")
                break
            except Exception as exc:
                current=None
                print(f"pàgina {page}: intent {attempt+1}/{MAX_RETRIES}, {exc}",file=sys.stderr,flush=True)
                if attempt<MAX_RETRIES-1:
                    time.sleep(min(2+2*attempt,16))
        if current is None:
            failed.append(page)
            continue
        seen |= codes
        dest=OUT/f"index_162_pagina_{page:03d}.json"
        dest.write_text(json.dumps(current,ensure_ascii=False),encoding="utf-8")
        sources.append((SERIE,dest))
        print(f"pàgina {page}/{pages}: +{len(codes)}; acumulat {len(seen)}",flush=True)
        time.sleep(0.6)
    report={"esperats":total,"recuperats":len(seen),"pagines_esperades":pages,
            "pagines_correctes":len(sources),"pagines_fallides":failed,
            "complet":len(seen)==total and not failed}
    (OUT/"estat_162.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False),flush=True)
    if sources:
        prepare(sources,OUT)
    if not report["complet"]:
        raise SystemExit(2)
except Exception as exc:
    print("ERROR DE RECUPERACIÓ:",repr(exc),file=sys.stderr)
    raise SystemExit(1)
