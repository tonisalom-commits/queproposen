#!/usr/bin/env python3
"""Recupera els índexs originals de la XV legislatura i crea l'univers individual.
No classifica la temàtica ni modifica data/iniciatives.json.
"""
from __future__ import annotations
import csv, hashlib, json, math, re, sys, time, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from recull_index_congres import extract, official_url, record_url

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'treball'
ARCH=ROOT/'data'/'fonts'/'indexs_originals_congres_xv.zip'
EXPECTED={'161':3824,'162':850,'122':306,'120':49,'123':2,'124':47,'125':16}
FIELDS=['id','serie','titol_oficial','autor_oficial','resultat_oficial','data_presentacio','url_expedient','en_cua_ambiental','estat_auditoria_tematica']

def fetch(url):
    last=None
    for tries in range(7):
        try:
            req=Request(url,headers={'User-Agent':'QueProposen-IndexXV/1.0 (auditoria educativa)',
                                     'Accept':'application/json,text/plain,*/*'})
            with urlopen(req,timeout=35) as response:
                raw=response.read(10000001)
            if len(raw)>10000000:
                raise ValueError('Resposta massa gran')
            data=json.loads(raw.decode('utf-8-sig'))
            if not isinstance(data,dict) or data.get('error'):
                raise ValueError('Resposta JSON amb error: '+str(data)[:120])
            return raw,data
        except (ValueError,UnicodeError,HTTPError,URLError,TimeoutError,OSError) as ex:
            last=ex
            print('REINTENT',tries+1,url,str(ex)[:180],file=sys.stderr,flush=True)
            if tries<6:
                time.sleep(min(2+tries*2,12))
    raise RuntimeError('Descàrrega no disponible '+url+': '+str(last))

def save_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def main():
    with (OUT/'inventari_ambient_xv_830.csv').open(encoding='utf-8-sig',newline='') as file:
        queue_rows=list(csv.DictReader(file))
    queue={r['expedient'] for r in queue_rows}
    if len(queue)!=830 or len(queue_rows)!=830:
        raise ValueError('La cua no conté 830 codis únics')
    OUT.mkdir(parents=True,exist_ok=True)
    ARCH.parent.mkdir(parents=True,exist_ok=True)
    temp=ARCH.with_name('indexs_originals_congres_xv.partial.zip')
    allrows={}
    pages=[]
    try:
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
            for serie,total in EXPECTED.items():
                seen=set()
                total_pages=math.ceil(total/25)
                for page in range(1,total_pages+1):
                    url=official_url(serie,page)
                    for attempt in range(7):
                        raw,payload=fetch(url)
                        rows=extract(payload)
                        ids={r['id'] for r in rows}
                        expected_n=min(25,total-25*(page-1))
                        if (int(payload.get('iniciativas_encontradas',-1))==total
                                and len(rows)==expected_n and len(ids)==expected_n
                                and all(x.startswith(serie+'/') for x in ids)
                                and not seen.intersection(ids)):
                            break
                        print('REINTENT DE VALIDACIÓ',serie,page,'registres',len(rows),
                              'duplicats',len(seen&ids),file=sys.stderr,flush=True)
                        if attempt==6:
                            raise ValueError('Pàgina incompleta/repetida: '+serie+'/'+str(page))
                        time.sleep(2+attempt*2)
                    seen.update(ids)
                    for row in rows:
                        code=row['id']
                        if not re.fullmatch(r'(161|162|122|120|123|124|125)/[0-9]{6}',code) or code in allrows:
                            raise ValueError('Duplicat o codi invàlid: '+code)
                        allrows[code]={
                            'id':code,'serie':serie,'titol_oficial':row['titol_oficial'],
                            'autor_oficial':row['autor_oficial'],
                            'resultat_oficial':row['resultat_oficial'],
                            'data_presentacio':row['data_presentacio'],
                            'url_expedient':record_url(code),
                            'en_cua_ambiental':'SI' if code in queue else 'NO',
                            'estat_auditoria_tematica':'PENDENT: no equival a exclusió temàtica'
                        }
                    path='indexs/'+serie+'/pagina_'+str(page).zfill(3)+'.json'
                    archive.writestr(path,raw)
                    pages.append({'serie':serie,'pagina':page,'url':url,
                                  'registres':len(rows),'sha256':hashlib.sha256(raw).hexdigest(),
                                  'fitxer_zip':path})
                    if page%10==0 or page==total_pages:
                        print('SERIE',serie,'PÀGINA',page,'/',total_pages,
                              'ACUMULAT',len(allrows),flush=True)
                    time.sleep(0.45)
                if len(seen)!=total:
                    raise ValueError('Total de la sèrie '+serie+' incorrecte')
        if len(allrows)!=5094 or queue-set(allrows):
            raise ValueError('Univers global incoherent; manquen '+repr(sorted(queue-set(allrows))[:20]))
        rows=sorted(allrows.values(),key=lambda x:(int(x['serie']),int(x['id'].split('/')[1])))
        outside=[r for r in rows if r['en_cua_ambiental']=='NO']
        if len(pages)!=206 or len(outside)!=4264:
            raise ValueError('Recomptes inconsistents: '+repr((len(pages),len(outside))))
        # No substituïm les dades verificades fins superar tots els controls.
        temp.replace(ARCH)
        save_csv(OUT/'univers_congres_xv_5094.csv',rows)
        save_csv(OUT/'fora_cua_xv_4264.csv',outside)
        manifest={
            'legislatura':'XV','data_recuperacio':datetime.now(timezone.utc).isoformat(),
            'font':'https://www.congreso.es/es/indice-de-iniciativas',
            'expedients_indexats':5094,'pagines_originals':206,
            'expedients_a_cua':830,'expedients_fora_cua':4264,
            'per_serie':{s:{'total':n,'recuperats':sum(x['serie']==s for x in rows)} for s,n in EXPECTED.items()},
            'sha256_zip':hashlib.sha256(ARCH.read_bytes()).hexdigest(),
            'pagines':pages,'duplicats':0,'expedients_de_la_cua_no_localitzats':0,
            'advertiment':'No s’ha auditat individualment la pertinència ambiental de les 5094 iniciatives.',
            'decisions_34':{'estat':'NO_RECUPERADES_PER_ID','agregat':34,
                'inclosos':19,'exclosos':10,'ambigus':5,
                'nota':'La taula original per ID no consta als dos corpus recuperats. No inventar la correspondència.'}
        }
        (OUT/'manifest_univers_congres_xv.json').write_text(
            json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in manifest.items() if k!='pagines'},
                         ensure_ascii=False,indent=2),flush=True)
    finally:
        if temp.exists():
            temp.unlink()

if __name__=='__main__':
    main()
