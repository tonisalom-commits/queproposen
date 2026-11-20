#!/usr/bin/env python3
"""Consolida l'auditoria documental ambiental XV sense publicar fitxes al web.

Entrades: dos directoris amb fitxes_amb_text_original.json provinents dels
artefactes GitHub Actions 14582681187 i 14581873661.
Diferencia metadades oficials, mostra web i validacio tematica pendent.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "treball"
HEADERS = [
    "expedient", "serie", "tipus", "titol_index", "autor_index",
    "resultat_index", "titol_web", "grup_web", "estat_web",
    "criteris_cua", "procedencia", "text_BOCG_localitzat",
    "incidencia", "decisio_ambiental", "url_expedient",
    "url_primera_publicacio", "sha256_fitxa", "sha256_BOCG",
    "data_captura",
]
TIPUS = {
    "161": "PNL en comissio", "162": "PNL al Ple",
    "122": "Proposicio de llei de grups", "120": "ILP",
    "123": "Proposicio de diputats", "124": "Proposicio del Senat",
    "125": "Proposicio autonomica",
}
EXPECTED = {"161": 3824, "162": 850, "122": 306, "120": 49,
            "123": 2, "124": 47, "125": 16}
RUNS = {
    "fase_1": {"run": 44630938748, "artifact": 14582681187},
    "fase_2": {"run": 44632672066, "artifact": 14581873661},
}

def load(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise ValueError("Fitxer d'entrada no es una llista: " + str(path))
    return rows, hashlib.sha256(raw).hexdigest()

def make(phase1: Path, phase2: Path) -> dict:
    catalog = json.loads((ROOT / "data" / "iniciatives.json").read_text(encoding="utf-8"))
    existing = {r["id"]: r for r in catalog if r.get("etiquetesAmbientals")}
    coverage = json.loads((ROOT / "data" / "cobertura-ambiental.json").read_text(encoding="utf-8"))
    if coverage["expedients_indexats"] != 5094:
        raise ValueError("El recompte de l'univers no es l'esperat")
    allrows = {}
    provenance = {}
    for phase,path in (("fase_1",phase1),("fase_2",phase2)):
        rows, digest = load(path)
        provenance[phase] = dict(RUNS[phase], sha256_json=digest, n=len(rows))
        for rec in rows:
            id = str(rec.get("id", ""))
            if not re.fullmatch(r"(?:120|122|123|124|125|161|162)/[0-9]{6}", id):
                raise ValueError("Codi invalid: " + id)
            if id in allrows:
                raise ValueError("Expedient duplicat: " + id)
            if not rec.get("detall_obtingut") or not rec.get("sha256_detall"):
                raise ValueError("Fitxa oficial o empremta absent: " + id)
            serie = id.split("/")[0]
            fragment = str(rec.get("fragment_original") or "")
            found = bool(fragment.strip()) and bool(rec.get("document_text_id_ocurrencies", 0))
            cat = existing.get(id, {})
            allrows[id] = {
                "expedient": id,
                "serie": serie,
                "tipus": TIPUS[serie],
                "titol_index": rec.get("titol",""),
                "autor_index": rec.get("autor_index",""),
                "resultat_index": rec.get("resultat_index",""),
                "titol_web": cat.get("titol",""),
                "grup_web": " | ".join(cat.get("grups") or []),
                "estat_web": cat.get("estat",""),
                "criteris_cua": " | ".join(rec.get("criteris",[])),
                "procedencia": phase,
                "text_BOCG_localitzat": "SI" if found else "NO",
                "incidencia": "" if found else "Falta fragment de l'expedient al BOCG",
                "decisio_ambiental": "PENDENT: lectura i decisio individual",
                "url_expedient": rec.get("url",""),
                "url_primera_publicacio": rec.get("primera_publicacio",""),
                "sha256_fitxa": rec.get("sha256_detall",""),
                "sha256_BOCG": rec.get("font_primaria_sha256",""),
                "data_captura": rec.get("data_captura",""),
            }
    if len(allrows) != 826:
        raise ValueError("Dos corpus: s'esperaven 826 fitxes uniques")
    missing = sorted(set(existing)-set(allrows))
    if len(missing) != 4:
        raise ValueError("Fitxes del web fora dels dos corpus: s'esperaven 4, hem obtingut " + repr(missing))
    for id in missing:
        cat=existing[id]
        serie=id.split("/")[0]
        allrows[id] = {
            "expedient": id, "serie": serie, "tipus": TIPUS[serie],
            "titol_index": "", "autor_index": "", "resultat_index": "",
            "titol_web": cat.get("titol",""),
            "grup_web": " | ".join(cat.get("grups") or []),
            "estat_web": cat.get("estat",""),
            "criteris_cua": "fitxa_web_omesa",
            "procedencia": "rescat_web_sense_copia_documental",
            "text_BOCG_localitzat": "NO",
            "incidencia": "Manca copia de la fitxa oficial i del text als dos corpus",
            "decisio_ambiental": "PENDENT: recuperar documentacio i revisar",
            "url_expedient": cat.get("url",""),
            "url_primera_publicacio": cat.get("fontEspecifica",""),
            "sha256_fitxa": "", "sha256_BOCG": "",
            "data_captura": cat.get("revisio",{}).get("data",""),
        }
    rows=[allrows[id] for id in sorted(allrows, key=lambda s:(int(s.split("/")[0]), int(s.split("/")[1])))]
    issues=[r for r in rows if r["incidencia"]]
    nfragments=sum(r["text_BOCG_localitzat"]=="SI" for r in rows)
    if (len(rows),len(issues),nfragments)!=(830,35,795):
        raise ValueError("Recomptes inesperats: " + repr((len(rows),len(issues),nfragments)))
    OUT.mkdir(parents=True,exist_ok=True)
    for file,data in (("inventari_ambient_xv_830.csv",rows),
                      ("incidencies_ambient_xv_35.csv",issues)):
        with (OUT/file).open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=HEADERS)
            writer.writeheader(); writer.writerows(data)
    counts=Counter(r["serie"] for r in rows)
    manifest={
        "versio":1, "data_consolidacio":"2026-11-20", "legislatura":"XV",
        "univers_total":sum(EXPECTED.values()), "expedients_consolidats":len(rows),
        "amb_fitxa_recuperada":826, "rescatats_del_web":len(missing),
        "expedients_rescatats":missing, "fragments_BOCG_localitzats":nfragments,
        "incidencies_total":len(issues), "incidencies_corpus":len(issues)-len(missing),
        "sense_registre_individual_en_corpus_ni_web":sum(EXPECTED.values())-len(rows),
        "sense_duplicats":True, "fitxes_mostra_web_localitzades":len(existing),
        "per_serie":{x:{"univers":EXPECTED[x],"cua":counts[x]} for x in EXPECTED},
        "fonts":provenance,
        "decisions_informe_previ":{"total":34,"incloses":19,"excloses":10,"especials":5,
            "nota":"Les decisions per ID no consten als dos corpus; no s'han assignat sense font."},
        "advertiments":[
            "La cua de 830 no equival a 830 propostes ambientals confirmades.",
            "Els 206 indexs originals no s'inclouen en aquests dos artefactes; el total global prové del control de cobertura previ.",
            "L'extraccio de fragments no acredita contingut, esmenes, text aprovat ni votacions.",
            "Les fitxes web rescatades tenen menor nivell d'evidencia que les 826 fitxes recuperades.",
            "No publicar estadistiques per partit ni percentatges ambientals d'aquesta cua.",
        ],
    }
    (OUT/"manifest_ambient_xv.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--fase-1",type=Path,required=True)
    parser.add_argument("--fase-2",type=Path,required=True)
    opts=parser.parse_args()
    print(json.dumps(make(opts.fase_1,opts.fase_2),ensure_ascii=False,indent=2))
