#!/usr/bin/env python3
"""Prova puntual d'accés a expedients i als documents primaris del Congrés."""
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re, json, time
BASE="https://www.congreso.es/es/busqueda-de-iniciativas"
IDS=["162/000470","162/000432","161/002045","122/000170","161/003360"]
for code in IDS:
 url=BASE+"?"+urlencode({"_iniciativas_id":code,"_iniciativas_legislatura":"XV","_iniciativas_mode":"mostrarDetalle","p_p_id":"iniciativas","p_p_lifecycle":"0","p_p_mode":"view","p_p_state":"normal"})
 d={"id":code}
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; QueProposenEducation/1.0)","Accept":"text/html,application/xhtml+xml"})
  with urlopen(req,timeout=22) as res:
   raw=res.read(2000000)
   d["code"]=res.status
   d["size"]=len(raw)
  soup=BeautifulSoup(raw,"html.parser")
  main=soup.get_text(" ",strip=True)
  at=main.find(code)
  d["near_exp"]=main[max(0,at-200):at+1500] if at>=0 else main[:500]
  d["text_links"]=[{"text":a.get_text(" ",strip=True)[:100],"url":urljoin(url,a.get("href",""))[:400]} for a in soup.find_all("a",href=True) if re.search("íntegro|integro|BOCG|Publicación|PDF|expediente",a.get_text(" ",strip=True),re.I)][:15]
  d["anchors"]=[{"txt":a.get_text(" ",strip=True)[:70],"href":a.get("href","")[:300]} for a in soup.find_all("a",href=True) if "texto" in a.get_text(" ",strip=True).lower()][:10]
 except Exception as e:d["error"]=repr(e)
 print(json.dumps(d,ensure_ascii=False),flush=True)
 time.sleep(1.0)

# Comprovam si el text íntegre del BOCG conté els paràgrafs de la iniciativa.
for code,publication in [
 ("162/000470","BOCG-15-D-317.CODI."),
 ("161/002045","BOCG-15-D-328.CODI."),
 ("122/000170","BOCG-15-B-193-1.CODI.")]:
 from urllib.parse import urlencode
 url="https://www.congreso.es/busqueda-de-publicaciones?"+urlencode({
  "p_p_id":"publicaciones","p_p_lifecycle":"0","p_p_state":"normal",
  "p_p_mode":"view","_publicaciones_mode":"mostrarTextoIntegro",
  "_publicaciones_legislatura":"XV","_publicaciones_id_texto":"("+publication+")"})
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; QueProposenEducation/1.0)"})
  with urlopen(req,timeout=24) as response:
   raw=response.read(2500000)
  soup=BeautifulSoup(raw,"html.parser")
  txt=soup.get_text(" ",strip=True)
  positions=[m.start() for m in re.finditer(re.escape(code),txt)]
  print(json.dumps({"doc":publication,"id":code,"bytes":len(raw),"textlength":len(txt),
   "occurrences":len(positions),"near":[txt[max(0,p-180):p+2400] for p in positions[:3]]},ensure_ascii=False),flush=True)
 except Exception as e:print(json.dumps({"doc":publication,"error":repr(e)}),flush=True)
