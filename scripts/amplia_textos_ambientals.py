#!/usr/bin/env python3
"""Segon cribratge de sensibilitat: rescata títols ambientals sense paraules genèriques.

Els casos recuperats continuen essent candidats; no es publiquen al web.
"""
from __future__ import annotations
import concurrent.futures as futures
import json
import re
from collections import Counter
from pathlib import Path
from scripts import recull_textos_ambientals as m

m.ROOT=Path("evidencia-ampliada")
m.ROOT.mkdir(exist_ok=True)
(m.ROOT/"butlletins").mkdir(exist_ok=True)
VOCABULARI=re.compile(
    r"\b(?:cachalot\w*|cetace\w*|ballena\w*|lobo|lobos|lince\w*|"
    r"oso pardo|especies? en peligro|aves?\s+rapaces|aves? migratorias|posidonia|"
    r"parque nacional|parques nacionales|pesca|pesquer\w*|caza|cinegetic\w*|"
    r"vulcanolog\w*|dana|catastrof\w*|inundaci\w*|temporales?|"
    r"eolico|eolica|fotovoltaic\w*|nuclear|regadio|trasvase|embalse\w*|"
    r"presas?\b|desaladora\w*|escombrera\w*|agua\b|rio\b|rios\b|acuifer\w*|"
    r"sostenibil\w*|bioeconomia|subvenciones?\s+ambientales|calidad del aire|"
    r"proteccion del medio natural|recuperacion de\s+playas|montes\b|humedal\w*|"
    r"reduccion de\s+emisiones|invasor\w*|marisqueo|acuicultura|marina protegida|"
    r"biodiversidad|vertid\w*|productos? quimic\w*|industria extractiva|"
    r"plastico\w*|combustibles fosiles|gas\s+natural|ferrocarril|movilidad|"
    r"biciclet\w*|saneamiento|tratamiento de aguas|captura de carbono|"
    r"centro de volcanologia|proteccion civil\s+ante\s+riesgos|sequia|"
    r"mortalidad\s+de\s+fauna|campanas?\s+forestales|tramitacion\s+ambiental|"
    r"restauracion\s+ecologica|energias?\s+renovables|autoconsumo|diesel|"
    r"electrificacion|reduccion\s+de\s+la\s+huella)\b")

def main():
 rows=m.sources()
 first,_=m.select(rows)
 known=set(first)
 candidates=[]
 for code,raw in sorted(rows.items()):
  if code in known:
   continue
  t=m.normalize(raw.get("titulo",""))
  if not VOCABULARI.search(t):
   continue
  candidates.append({
   "id":code,"titol":raw.get("titulo",""),
   "autor":raw.get("autor",""),
   "resultat":raw.get("resultado_tram",""),
   "data":raw.get("fecha_presentado",""),
   "criteris":["ampliacio_semantica_fase_2"],
  })
 print("CANDIDATS ADDICIONALS: ",len(candidates),flush=True)
 with futures.ThreadPoolExecutor(max_workers=3) as pool:
  details=list(pool.map(m.get_detail,candidates))
 sources={m.document_urlkey(x["primera_publicacio"]):x["primera_publicacio"]
          for x in details if x.get("primera_publicacio")}
 with futures.ThreadPoolExecutor(max_workers=3) as pool:
  sources_info=dict(pool.map(m.get_bulletin,sources.items()))
 for row in details:
  url=row.get("primera_publicacio")
  key=m.document_urlkey(url) if url else None
  info=sources_info.get(key,{}) if key else {}
  row["font_primaria_text_obtingut"]=bool(info.get("correcte"))
  row["font_primaria_sha256"]=info.get("sha256_html")
  row["fragment_original"]=""
  row["document_text_id_ocurrencies"]=0
  if info.get("correcte"):
   text=(m.ROOT/"butlletins"/(key+".txt")).read_text(encoding="utf-8")
   row["fragment_original"],row["document_text_id_ocurrencies"]=m.section(text,row["id"])
  row["estat_revisio"]="TEXT_RECUPERAT_REVISIO_PENDENT" if row["fragment_original"] else "TEXT_NO_LOCALITZAT"
 (m.ROOT/"fitxes_amb_text_original.json").write_text(
  json.dumps(details,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (m.ROOT/"fonts_butlleti.json").write_text(
  json.dumps(sources_info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 summary={
  "candidats_titol_addicionals":len(candidates),
  "detalls_obtinguts":sum(bool(x["detall_obtingut"]) for x in details),
  "butlletins_distints":len(sources),
  "butlletins_obtinguts":sum(bool(x["correcte"]) for x in sources_info.values()),
  "fragments_localitzats":sum(bool(x["fragment_original"]) for x in details),
  "important":"No valida la pertinència ambiental ni les esmenes i votacions.",
 }
 (m.ROOT/"resum_segona_recuperacio.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=="__main__":
 main()
