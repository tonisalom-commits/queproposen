# Què proposen? — atles parlamentari en català

Web temàtica i divulgativa per conèixer què han proposat els grups al Congrés i distingir-ho de l'acció del Govern.

**Estat: prototip, NO exhaustiu ni representatiu.** Actualment hi ha 52 expedients parlamentaris de mostra (41 PNL i 11 proposicions de llei). Medi ambient té 22 fitxes (21 PNL i 1 PL) i 4 documents governamentals addicionals, que no s'afegeixen als recomptes parlamentaris.

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

## Rigor i límits

- Una PNL no és una llei. Una retirada o caducada no és una rebutjada.
- No s'ha de confondre un projecte o decret del Govern amb una proposta presentada per un grup.
- Els resums són editorials i les fonts parlamentàries són la referència definitiva.
- Cal identificar les signatures, les coautories, els partits concrets dins el Grup Mixt, les esmenes i el text que acaba votant-se.
- L'absència de fitxes sobre un tema **no significa que un grup no hagi presentat iniciatives**.
- No publicarem percentatges o rànquings per grup fins disposar d'un univers d'expedients complet, recuperat i auditat, de totes les comissions i del Ple.

Fonts: [Congrés](https://www.congreso.es/es/busqueda-de-iniciativas), [Reglament](https://www.congreso.es/es/cem/tit10), [BOE](https://www.boe.es/).

**Llicència del projecte: pendent de decidir.**
