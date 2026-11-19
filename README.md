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

- `medi-ambient/index.html`: secció ambiental amb portada pròpia, filtres, fitxes i connexió a la **mateixa** `dades.js` del portal. No és un repositori independent.
- `docs/metodologia-medi-ambient.md`: criteris d'inclusió i full de ruta per fer un inventari exhaustiu.
- La secció ambiental té només una **mostra preliminar** de propostes i no justifica encara rànquings ni comparacions quantitatives.

## Limitacions imprescindibles

- Les 37 fitxes (27 PNL i 10 PL) són **exemples seleccionats, no mostra representativa** ni inventari exhaustiu. No permeten estimar prioritats temàtiques globals.
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
