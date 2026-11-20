#!/usr/bin/env python3
"""Auditoria documental: descarrega detalls i butlletins per a la selecció ambiental.

L'exportació és evidència recuperada amb enllaç i empremta criptogràfica;
les classificacions substantives i les esmenes exigeixen una revisió separada.
"""
from __future__ import annotations
import concurrent.futures as futures
import csv
import hashlib
import json
import random
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlencode, urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path("evidencia-ambiental")
SOURCE1=Path("fonts1")
SOURCE2=Path("fonts162")
ROOT.mkdir(exist_ok=True)
( ROOT / "butlletins" ).mkdir(exist_ok=True)
ENV_WORDS=("clim","emision","emiss","carbon","descarbon","ambient","ecolog",
    "transicion energet","energias renovables","renovables","biodivers",
    "ecosistem","especie","fauna","flora","forest","incendio","bosque","sequia",
    "agua","hidric","acuifer","humedal","litoral","costa","marino","marina",
    "plastico","residuo","recicl","vertido","contamina","microplastic",
    "glifosat","agricultura ecologic","suelo","desertific","movilidad sosten",
    "transporte sosten","emergencia climatic","inundaci","pesca sosten",
    "consumo sostenible","economia circular","empaquetado")
EXTRA=re.compile(r"\b(?:trasvase\w*|eolic\w*|fotovoltaic\w*|nuclear|"
    r"verteder\w*|presa\w*|embalse\w*|desalaci\w*|depuradora\w*|"
    r"agroecolog\w*|regadio\w*|riada\w*|refineria\w*|"
    r"fitosanitari\w*|pesticida\w*|acuifer\w*|megaparque\w*|"
    r"mineria|arbolado|electrificacion|hidroelectri\w*|"
    r"gestion del agua|gestion de las aguas|recarga de acuiferos|"
    r"contenedores de residuos)\b")
RE_ID=re.compile(r"(?<!\d)(?:120|122|123|124|125|161|162)/\d{6}(?!\d)")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; queproposen-auditoria-publica/1.0)",
         "Accept":"text/html,application/xhtml+xml,*/*"}
T0=datetime.now(timezone.utc).isoformat()

def normalize(s):
 return "".join(x for x in unicodedata.normalize("NFKD",str(s or "").casefold())
                if not unicodedata.combining(x))

def sources():
 data={}
 for folder in (SOURCE1,SOURCE2):
  for path in folder.rglob("index_*_pagina_*.json"):
   try:
    obj=json.loads(path.read_text(encoding="utf-8-sig"))
    for x in (obj.get("lista_iniciativas") or {}).values():
     rid=x.get("id_iniciativa","")
     if RE_ID.fullmatch(rid):
      if rid in data and data[rid]!=x:
       print("AVÍS: expedient duplicat diferent",rid,file=sys.stderr)
      data[rid]=x
   except Exception as e:
    print("ERROR font",path,e,file=sys.stderr)
 if len(data)!=5094:raise ValueError("Univers incomplet: "+str(len(data))+" registres")
 return data

def select(rows):
 allrows=[dict(id=id,titol=unescape(o.get("titulo","")),
               autor=unescape(o.get("autor","")),
               resultat=o.get("resultado_tram",""),
               data=o.get("fecha_presentado",""))
          for id,o in sorted(rows.items())]
 primary=[];excluded=[];added=[]
 for row in allrows:
  t=normalize(row["titol"])
  core=any(word in t for word in ENV_WORDS) or bool(re.search(r"\brio\b",t))
  extra=bool(EXTRA.search(t))
  if core:primary.append(row)
  else:
   excluded.append(row)
   if extra:added.append(row)
 sampled=random.Random(20261119).sample(excluded,160)
 final={}
 for kind,series in [("paraula_clau",primary),("terme_recuperat",added),("control_exclusions",sampled)]:
  for obj in series:
   final.setdefault(obj["id"],{**obj,"criteris":[]})["criteris"].append(kind)
 print("UNIVERS:",len(allrows),"primaris:",len(primary),
       "nous candidats:",len(added),"mostra exclusions:",len(sampled),
       "per recuperar:",len(final),flush=True)
 return final,{"univers":len(allrows),"candidats_primaris":len(primary),
               "candidats_addicionals":len(added),"mostra_exclusions":len(sampled),
               "seleccio_unica":len(final)}

def fetch(url,tries=3,limit=3000000):
 if urlparse(url).hostname not in ("www.congreso.es","congreso.es"):
  raise ValueError("Domini de font no autoritzat")
 last=None
 for j in range(tries):
  try:
   time.sleep(0.55 + random.random()*0.6)
   r=requests.get(url,timeout=25,headers=HEADERS)
   r.raise_for_status()
   data=r.content[:limit+1]
   if len(data)>limit:raise ValueError("Mida de font excedida")
   if b"<html" not in data[:500].lower() and b"<!doctype" not in data[:500].lower():
    raise ValueError("Resposta no HTML: "+repr(data[:80]))
   return data
  except (requests.RequestException,ValueError) as e:
   last=e
   time.sleep(1+2*j)
 raise RuntimeError(str(last))

def detail_url(id):
 return ("https://www.congreso.es/es/busqueda-de-iniciativas?"+
         urlencode({"_iniciativas_id":id,"_iniciativas_legislatura":"XV",
                    "_iniciativas_mode":"mostrarDetalle","p_p_id":"iniciativas",
                    "p_p_lifecycle":"0","p_p_state":"normal","p_p_mode":"view"}))

def get_detail(row):
 result={"id":row["id"],"titol":row["titol"],"autor_index":row["autor"],
         "resultat_index":row["resultat"],"criteris":row["criteris"],
         "url":detail_url(row["id"]),"data_captura":T0}
 try:
  html=fetch(result["url"])
  soup=BeautifulSoup(html,"html.parser")
  text=soup.get_text(" ",strip=True)
  loc=text.find(row["id"])
  links=[]
  for a in soup.find_all("a",href=True):
   label=a.get_text(" ",strip=True).casefold()
   href=a.get("href","")
   if "texto íntegro" in label or ("pdf"==label and "/enmiendas/" in href):
    from urllib.parse import urljoin
    full=urljoin(result["url"],href)
    if urlparse(full).hostname=="www.congreso.es":
     links.append({"url":full,"tipus":"BOCG" if "BOCG-" in full else
                   "DIARI" if "DSCD-" in full or "DSCG-" in full else "ALTRE"})
  result.update({"detall_obtingut":True,"sha256_detall":hashlib.sha256(html).hexdigest(),
                 "text_detall":text[loc:loc+4200] if loc>=0 else text[:1500],
                 "primera_publicacio":next((k["url"] for k in links if k["tipus"]=="BOCG"),None),
                 "documents":links[:30]})
 except Exception as e:
  result.update({"detall_obtingut":False,"error_detall":str(e)[:350],
                 "documents":[],"primera_publicacio":None})
 return result

def document_urlkey(url):
 return hashlib.sha256(url.encode()).hexdigest()[:16]

def get_bulletin(arg):
 key,url=arg
 try:
  raw=fetch(url,tries=4,limit=6000000)
  soup=BeautifulSoup(raw,"html.parser")
  for node in soup(["script","style","noscript"]):node.decompose()
  tx=soup.get_text(" ",strip=True)
  # Preservam text públic i metadades a l'artefacte temporal, no al web.
  (ROOT/"butlletins"/(key+".txt")).write_text(tx,encoding="utf-8")
  return key,{"url":url,"sha256_html":hashlib.sha256(raw).hexdigest(),
              "bytes":len(raw),"text_len":len(tx),"correcte":True}
 except Exception as e:
  return key,{"url":url,"correcte":False,"error":str(e)[:320]}

def section(text,id):
 positions=[m.start() for m in re.finditer(re.escape(id),text)]
 if not positions:return "",0
 # Habitualment la primera aparició és a l'índex i la segona és l'articulat.
 if len(positions)>1:
  p=positions[1]
 else:p=positions[0]
 rest=text[p:]
 next_code=RE_ID.search(rest[len(id)+150:])
 # Si hi ha un altre número d'expedient al cap de poc, retallam abans.
 if next_code and next_code.start()+len(id)+150>250:
  rest=rest[:next_code.start()+len(id)+150]
 return rest[:13000],len(positions)

def main():
 universe=sources()
 rows,summary=select(universe)
 with futures.ThreadPoolExecutor(max_workers=3) as pool:
  details=list(pool.map(get_detail,rows.values()))
 (ROOT/"fitxes_detall.json").write_text(
  json.dumps(details,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 source_urls={document_urlkey(x["primera_publicacio"]):x["primera_publicacio"]
              for x in details if x.get("primera_publicacio")}
 print("Detalls recuperats",sum(x["detall_obtingut"] for x in details),
       "/ ",len(details),"butlletins diferents",len(source_urls),flush=True)
 with futures.ThreadPoolExecutor(max_workers=3) as pool:
  publications=dict(pool.map(get_bulletin,source_urls.items()))
 (ROOT/"fonts_butlleti.json").write_text(
  json.dumps(publications,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 for row in details:
  uri=row.get("primera_publicacio")
  key=document_urlkey(uri) if uri else None
  info=publications.get(key,{}) if key else {}
  row["font_primaria_text_obtingut"]=bool(info.get("correcte"))
  row["font_primaria_sha256"]=info.get("sha256_html")
  row["document_text_id_ocurrencies"]=0
  row["fragment_original"]=""
  if info.get("correcte"):
   text=(ROOT/"butlletins"/(key+".txt")).read_text(encoding="utf-8")
   row["fragment_original"],row["document_text_id_ocurrencies"]=section(text,row["id"])
  row["estat_revisio"]="TEXT_RECUPERAT_REVISIO_PENDENT" if row["fragment_original"] else "TEXT_NO_LOCALITZAT"
 (ROOT/"fitxes_amb_text_original.json").write_text(
  json.dumps(details,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with (ROOT/"revisio_expedients.csv").open("w",encoding="utf-8-sig",newline="") as f:
  cols=["id","titol","autor_index","resultat_index","criteris","detall_obtingut",
        "primera_publicacio","font_primaria_text_obtingut",
        "document_text_id_ocurrencies","estat_revisio","fragment_original","url"]
  w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
  w.writeheader()
  for row in details:
   rr={**row,"criteris":"; ".join(row["criteris"])}
   w.writerow(rr)
 summary.update({
  "detalls_obtinguts":sum(bool(x["detall_obtingut"]) for x in details),
  "fonts_primaries_distintes":len(source_urls),
  "butlletins_obtinguts":sum(bool(x["correcte"]) for x in publications.values()),
  "fragments_amb_expedient":sum(bool(x["fragment_original"]) for x in details),
  "estat":"Evidència documental recollida; auditoria semàntica i de votacions NO COMPLETADA",
  "iniciatives_certificades_ambientals":None,
  "errors_detall":[x["id"] for x in details if not x["detall_obtingut"]],
  "errors_text":[x["id"] for x in details if not x["fragment_original"]],
 })
 (ROOT/"resum_recuperacio.json").write_text(
  json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=="__main__":
 main()
