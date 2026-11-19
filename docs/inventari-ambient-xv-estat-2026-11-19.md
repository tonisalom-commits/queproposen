# Inventari ambiental de la XV legislatura — auditoria de cobertura (19/11/2026)

**Encara no és un inventari ambiental exhaustiu i auditat de continguts.**

## Univers documental del Congrés

La XV legislatura va del 17/08/2023 al 06/10/2026. Hem recuperat 206 pàgines de set índexs amb **5.094 expedients únics**; el nombre de cada sèrie coincideix amb els totals oficials.

| Sèrie | Procediment | Expedients | Pàgines |
| --- | --- | ---: | ---: |
| 161 | PNL en comissió | 3.824 | 153 |
| 162 | PNL al Ple | 850 | 34 |
| 122 | Proposicions de llei de grups | 306 | 13 |
| 120 | Iniciatives legislatives populars | 49 | 2 |
| 123 | Proposicions de llei de diputats | 2 | 1 |
| 124 | Proposicions de llei del Senat | 47 | 2 |
| 125 | Proposicions de llei autonòmiques | 16 | 1 |
| **Total** | | **5.094** | **206** |

Font: https://www.congreso.es/es/indice-de-iniciativas (consulta del 19/11/2026). Cada font original es conserva amb una empremta SHA-256, rang de pàgines, total declarat i prova que no hi ha expedients duplicats.

El servidor pot retornar errors dins respostes HTTP 200. La sèrie 162 es recuperà amb reintents; les 34 pàgines i els 850 identificadors són complets.

## Candidats ambientals: encara no validats

El cribratge per paraules clau del **títol** ha identificat **410 candidats**: 320 de la sèrie 161, 74 de la 162, 12 de la 122, dos de la 120 i dos de la 124. **No són 410 iniciatives ambientals comprovades**. És possible que hi hagi títols no pertinents i iniciatives ambientals ocultes per títols genèrics.

Hem preparat una mostra reproduïble de 160 exclusions per revisar falsos negatius. El mostreig no ha estat validat manualment. Les etiquetes suggerides per heurístiques no es poden publicar com a categories confirmades.

## Contrast amb la web

Els identificadors, grups i resultats de les **25 fitxes ambientals del prototip** són compatibles amb les metadades de l'índex oficial en la comprovació automàtica: zero discrepàncies detectades. Això **no** certifica les síntesis del dispositiu, les esmenes, els textos finalment aprovats ni les votacions.

## Què falta per certificar l'inventari ambiental?

1. Llegir els punts dispositius o l'articulat de cadascun dels candidats i justificar les inclusions i exclusions.
2. Revisar les exclusions, sobretot iniciatives sobre transports, indústria, salut, agricultura i urbanisme; la mostra aleatòria de 160 exclusions encara està pendent.
3. Distingir partits del Grup Mixt, signants i coautories.
4. Contrastar textos originals, esmenes, versions aprovades i vots.
5. Fer una segona auditoria i publicar indicadors d'inclosos, exclosos i pendents.
6. Construir un inventari governamental separat (projectes de llei, decrets llei i reials decrets).

## Reproducció tècnica

- scripts/recull_index_congres.py: captura dels índexs per sèrie i pàgina.
- scripts/completa_162.py: captura robusta de la sèrie 162.
- scripts/audita_cobertura_ambiental.py: comparació amb les fitxes curades.
- data/cobertura-ambiental.json: indicadors separats de l'inventari de propostes.

El projecte continua sense dades suficients per publicar rànquings de propostes ambientals per partit.


## Auditoria de textos primaris: ampliació del 19/11/2026

S'ha incorporat una **segona fase documental**, sense promoció automàtica de candidats a la web:

| Control | Resultat |
| --- | ---: |
| Univers dels set índexs oficials | 5.094 expedients |
| Expedients inclosos a la cua de revisió, després de dos cribratges i un control d'exclusions | 826 |
| Fitxes oficials d'expedient recuperades | 826 |
| Expedients amb fragment localitzat al primer BOCG enllaçat | 795 |
| Incidències de localització del fragment | 31 |
| Primera lectura i decisió temàtica documentada | 34 |
| D'aquests, inclusions ambientals justificades | 19 |
| D'aquests, exclusions justificades | 10 |
| Decisions frontereres o pendents de comprovació especial | 5 |
| Expedients de la cua sense lectura temàtica completa | 792 |
| Expedients de l'univers encara fora de la cua de revisió | 4.268 |

Els fitxers de treball provenen de les execucions de GitHub Actions
[**Corpus inicial**](https://github.com/tonisalom-commits/queproposen/actions/runs/44630938748) i
[**Segon cribratge d'omissions**](https://github.com/tonisalom-commits/queproposen/actions/runs/44632672066).
S'hi conserven l'URL d'expedient, la primera publicació del BOCG, fragments textuals i empremtes SHA-256. Els artefactes temporals d'Actions caduquen i s'han de conservar en un arxiu documental estable abans de donar per reproduïble l'auditoria.

**No confondre:**
- 826 és la **cua documental de revisió**, no el nombre total d'iniciatives ambientals.
- 795 és la xifra de **fragments recuperats**, no de fitxes amb les mesures contrastades.
- 34 és la xifra de **primeres decisions editorials** a partir de fonts primàries, no de fitxes amb una segona auditoria independent ni de votacions verificades.
- El total dels set índexs no inclou els projectes governamentals de llei 121 ni els reials decrets llei 130; s'han de documentar separadament.

### Falsejaments detectats i interpretacions possibles

- El filtre de paraules clau produïa falsos positius: «Nicaragua» coincidia amb «agua», i «remisión» amb «emisión».
- També havia omès iniciatives relacionades amb el transvasament de l'Ebre, la posidònia, la protecció de cetacis o la regulació del llop.
- Tres expedients diferents sobre l'àrea de cria dels catxalots al nord de Menorca tenen propostes substancialment semblants: 161/001325 (caducat), 161/001727 (aprovat sense modificacions) i 162/000470 (caducat). Una PNL aprovada **no declara automàticament** una àrea marina protegida.

### Criteris per passar a una publicació quantitativa definitiva

Cal acabar la lectura dels dispositius i l'articulat dels expedients seleccionats, auditar les omissions de la resta de l'univers, identificar les formacions del Grup Mixt, verificar esmenes i text votat i comprovar les votacions i els resultats. **Sense aquests controls no es publicaran percentatges, rànquings ni conclusions sobre les prioritats globals dels partits.**
