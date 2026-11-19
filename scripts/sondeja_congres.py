#!/usr/bin/env python3
"""Sondeig de la paginació del Congrés: comparam les dues primeres pàgines reals."""
import json
import ssl
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE="https://www.congreso.es/es/busqueda-de-iniciativas"
COMMON={
"p_p_id":"iniciativas","p_p_lifecycle":"2","p_p_state":"normal",
"p_p_mode":"view","p_p_resource_id":"filtrarListado",
"p_p_cacheability":"cacheLevelPage",
"_iniciativas_legislatura":"15","_iniciativas_mode":"verListadoIndice",
}
report=[]
for serie in ["161","162","122","120"]:
 for page in [1,2]:
  params={**COMMON,"_iniciativas_tipo":serie,"_iniciativas_paginaActual":str(page)}
  url=BASE+"?"+urllib.parse.urlencode(params)
  forms=[("GET",None)]
  if page == 2: forms.append(("POST",urllib.parse.urlencode(params).encode("utf-8")))
  for method,data in forms:
   row={"serie":serie,"pagina":page,"metode":method}
   try:
    request=urllib.request.Request(url, data=data,headers={
     "User-Agent":"Mozilla/5.0 (compatible; QueProposenResearch/0.2)",
     "Accept":"application/json, text/plain, */*",
    })
    with urllib.request.urlopen(request,timeout=23) as res:
     raw=res.read(4_000_000)
     row["http"]=res.status;row["bytes"]=len(raw)
    obj=json.loads(raw)
    d=obj.get("lista_iniciativas") or {}
    vals=list(d.values())
    row["total"]=obj.get("iniciativas_encontradas")
    row["comptats"]=len(vals)
    row["primer"]=vals[0].get("id_iniciativa") if vals else None
    row["darrer"]=vals[-1].get("id_iniciativa") if vals else None
    row["paginacion"]=obj.get("paginacion")
    row["format_ok"]=True
   except Exception as ex:
    row["error"]=f"{type(ex).__name__}: {str(ex)[:160]}"
   report.append(row)
   print(json.dumps(row,ensure_ascii=False),flush=True)
   time.sleep(1)
Path("sondeig_congres.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
