# Què proposen? · Atles d'iniciatives parlamentàries

Prototip interactiu en català per explorar proposicions no de llei (PNL) i proposicions de llei (PL) de la XV legislatura del Congrés. HTML, CSS i JavaScript estàtics, sense dependències.

## Publicació

Quan la sol·licitud de fusió s'hagi aprovat: **Settings → Pages → Deploy from a branch → main → /(root)**. URL prevista: https://tonisalom-commits.github.io/queproposen/ . Aquesta branca no està publicada automàticament.

## Secció pedagògica

- `com-funciona/index.html`: guia interactiva i accessible sobre projecte de llei, proposició de llei, PNL, reial decret llei, reial decret legislatiu i reial decret, amb recorreguts simplificats i un exercici de comprovació.
- Fonts primàries: Constitució espanyola, Reglament del Congrés, Llei del Govern i portals institucionals.
- La guia explica el procediment estatal general i no substitueix una consulta al text normatiu ni recull totes les excepcions.

## Fitxers

- `index.html`: estructura accessible.
- `estils.css`: disseny adaptable.
- `dades.js`: estadístiques i fitxes d'exemple.
- `app.js`: filtres, cerca i gràfic.

## Primera secció temàtica

- `medi-ambient/index.html`: secció ambiental amb portada pròpia, filtres, expedients, **comparador de dos grups**, classificació multietiqueta i enllaços contextuals a la guia pedagògica. Comparteix la **mateixa** `dades.js` del portal. No és un repositori independent.
- `docs/metodologia-medi-ambient.md`: criteris d'inclusió i full de ruta per fer un inventari exhaustiu.
- La secció ambiental conté, en aquesta revisió, **22 expedients parlamentaris** seleccionats i dos documents governamentals oficials d'exemple (projecte de llei 121/000025 i RDL 20/2026). No s'han de sumar els dos universos ni utilitzar-ne les xifres per classificar grups.
- La guia permet anar directament a l'explicació de PNL o proposició de llei des de cada expedient.
- No són justificables rànquings ni comparacions quantitatives de prioritats mentre no s'hagi recuperat i revisat l'inventari complet.

## Limitacions imprescindibles

- Les 52 fitxes parlamentàries (42 PNL i 10 PL) són **exemples seleccionats, no mostra representativa** ni inventari exhaustiu. No permeten estimar prioritats temàtiques globals.
- Els totals i el gràfic general corresponen només a les PNL i es basen en Àgora: https://agora.vedratic.com/es/learn/pnl/ .
- La classificació té 20 àmbits accessibles en un selector, sense una capçalera d'etiquetes. Un filtre sense resultats només indica que encara no hi ha fitxes dins aquesta mostra, no que el grup no hagi presentat propostes.
- Les barres per grup només compten iniciatives d'autoria exclusiva: exclouen les de coautoria i les procedents del Senat.
- Els resums i interpretacions són editorials, no cites literals. Verificació de fitxes desigual i identificada expressament.
- Les formacions del Grup Mixt no es poden equiparar al grup en conjunt.
- «Resultat no incorporat» no implica que el Congrés no hagi resolt l'expedient.
- Les PNL no són lleis. Les PL tampoc no són lleis vigents fins que concloguin tots els tràmits parlamentaris. Presentar, prendre en consideració i aprovar definitivament són estadis diferents. Una proposta caducada no equival a una rebutjada; la proposta no prova què faria el partit governant.

## Criteris per al catàleg complet

Conservar número d'expedient, grup, partit impulsor, coautors, data, text dispositiu, tema, subtemes, acció, estat, votacions, esmenes, URL oficial i data de verificació. Separar **fets documentats** d'**interpretacions**; validar manualment classificacions automàtiques. No interpretar absències com a oposició o suport.

## Fonts

- Congrés: https://www.congreso.es/es/busqueda-de-iniciativas
- Àgora: https://agora.vedratic.com/es/learn/pnl/

Llicència pendent de definir.
