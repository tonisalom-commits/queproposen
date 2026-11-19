# Què proposen? — atles parlamentari en català

Web temàtica i divulgativa per conèixer què han proposat els grups al Congrés i distingir-ho de l'acció del Govern.

**Estat: prototip, NO exhaustiu ni representatiu.** Actualment hi ha 55 expedients parlamentaris de mostra (44 PNL i 11 proposicions de llei). Medi ambient té 25 fitxes (24 PNL i 1 PL) i 4 documents governamentals addicionals, que no s'afegeixen als recomptes parlamentaris.

## Tecnologia

- **Astro 7** genera HTML estàtic amb components compartits.
- **JSON** conté iniciatives, grups, temes, instruments i exemples de l'acció del Govern.
- **Python** valida l'estructura dels registres i permet exportar un CSV per a la revisió humana.
- **JavaScript** gestiona el cercador, els filtres, el comparador i la guia interactiva.
- **Markdown** conté articles pedagògics i el protocol ambiental.
- **GitHub Actions** executa la validació i compila el web, que es publica a **GitHub Pages** quan s'integra a main.

## Pàgines i fitxers importants

- **/** — portada i catàleg provisional.
- **/medi-ambient/** — primera secció completa estructuralment: 12 subtemes, etiquetes múltiples, filtres i comparador entre dos grups.
- **/medi-ambient/metodologia/** — protocol de verificació, compartit amb docs/metodologia-medi-ambient.md.
- **/com-funciona/** — explicacions dels instruments parlamentaris i del Govern.
- **/com-funciona/pnl/**, **/com-funciona/proposicio-llei/** i **/com-funciona/decret-llei/** — articles en Markdown.
- **data/iniciatives.json** — catàleg únic d'expedients.
- **data/catalog.json** — taxonomia i grups.
- **data/govern-ambient.json** — acció del Govern separada de PNL/PL.
- **data/instruments.json** — sis explicacions pedagògiques.
- **src/components/IniciativaCard.astro** — targetes reutilitzables.
- **src/layouts/**, **src/styles/** i **src/scripts/** — maquetació, disseny i interaccions.
- **scripts/valida_dades.py** i **scripts/exporta_csv.py** — eines Python.
- **.github/workflows/astro.yml** — compilació automàtica.

Els fitxers de l'antic prototip a l'arrel (index.html, estils.css, app.js, dades.js) són versions anteriors i **no intervenen en la compilació d'Astro**.

## Posada en marxa local

Cal Node.js 24 i Python 3.10 o posterior.

~~~bash
npm install
npm run dev
~~~

La ruta local usa el prefix /queproposen/. Per comprovar les dades i generar el web:

~~~bash
npm run check:data
npm run build
~~~

El resultat és el directori dist/. Per exportar un CSV de revisió:

~~~bash
python3 scripts/exporta_csv.py
~~~

L'exportació i la validació Python **no verifiquen jurídicament** les propostes, les esmenes o els resultats.

## Publicació

La sol·licitud de fusió es compila i es comprova automàticament, però **no es publica**. Quan la branca de treball s'integri a main:

1. GitHub: Settings → Pages → Build and deployment → Source: GitHub Actions.
2. El flux compila Astro i desplega el resultat a https://tonisalom-commits.github.io/queproposen/ .

Els paràmetres de la ruta són a astro.config.mjs.


## Recuperació i revisió sistemàtica del medi ambient

Hem afegit eines per passar de les fitxes seleccionades a una recerca amb traçabilitat:

- `scripts/recull_index_congres.py`: consulta els índexs oficials per sèries **161, 162, 120 i 122**, desa la resposta original i genera un CSV d'expedients i una cua de candidats ambientals. **No insereix candidats automàticament al portal**: els títols no basten per determinar pertinència o resultat. Accepta també fitxers JSON ja descarregats per revisar-los fora de línia.
- `scripts/audita_mediambient.py`: informa dels expedients introduïts i del grau de revisió, sense fabricar un percentatge de cobertura.
- `tests/test_recull_index_congres.py`: proves de deduplicació, validació dels codis, selecció provisional i segregació de les dades candidates.
- `.github/workflows/inventari-ambient.yml`: consulta de les dades com a **artefacte de revisió**, mai com a fitxes públiques de forma automàtica.

Execució amb Python (sense dependències):

~~~bash
python3 -m unittest discover -s tests -v
python3 scripts/recull_index_congres.py --descarrega --sortida revisio-ambiental
python3 scripts/audita_mediambient.py --sortida revisio-ambiental/estat_fitxes.json
~~~

**Important:** els índexs oficials estan paginats (25 registres per petició), i el catàleg d'opendata del Congrés no publica una descàrrega global equivalent per a totes les PNL. La recuperació automàtica inicial és una **cua de treball**. La cobertura completa requereix comprovar paginació, descarregar els texts, auditar els casos negatius i contrastar els tràmits, els partits concrets del Grup Mixt i les votacions. No publicarem cap xifra d'exhaustivitat fins haver fet aquestes comprovacions.


La primera execució del recuperador, el **19/11/2026**, ha aconseguit connexió amb el Congrés, però ha recuperat **només 25 expedients per sèrie** (100 en total). Els índexs oficials indiquen **3.824** expedients per a 161, **850** per a 162, **306** per a 122 i **49** per a 120. Això és una **fotografia dels resultats declarats pel cercador**, no l'univers ambiental classificat. La resta de pàgines no s'ha descarregat ni revisat encara; la comprovació de la paginació forma part de la feina pendent. S'ha desat l'artefacte de GitHub Actions per a auditoria.

**Revisió parcial documentada:** 14 de les 25 fitxes ambientals de mostra tenen a `data/iniciatives.json` una `revisio` amb grau (autoria, contingut, tràmit o resultat), data, observació i enllaç oficial. La resta es mostren com a pendents de comprovació detallada. L'aspecte de les fitxes s'actualitza a partir del **mateix component Astro**; no es reescriu cada pàgina HTML.

## Rigor i límits

- Una PNL no és una llei. Una retirada o caducada no és una rebutjada.
- No s'ha de confondre un projecte o decret del Govern amb una proposta presentada per un grup.
- Els resums són editorials i les fonts parlamentàries són la referència definitiva.
- Cal identificar les signatures, les coautories, els partits concrets dins el Grup Mixt, les esmenes i el text que acaba votant-se.
- L'absència de fitxes sobre un tema **no significa que un grup no hagi presentat iniciatives**.
- No publicarem percentatges o rànquings per grup fins disposar d'un univers d'expedients complet, recuperat i auditat, de totes les comissions i del Ple.

Fonts: [Congrés](https://www.congreso.es/es/busqueda-de-iniciativas), [Reglament](https://www.congreso.es/es/cem/tit10), [BOE](https://www.boe.es/).

**Llicència del projecte: pendent de decidir.**
