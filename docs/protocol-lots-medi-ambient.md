# Auditoria ambiental per lots · XV legislatura

**Versió:** 20 de novembre de 2026. **Abast:** dades internes de treball; la web pública no es modifica.

## Principi de funcionament

Partim de l'**univers de 5.094 expedients** (7 sèries), una **cua de 830 candidats** i **4.264 expedients fora de la cua**. Ni la cua equival a inclusions confirmades ni «fora de cua» equival a «no ambiental».

El programa `scripts/gestiona_auditoria_ambiental.py` combina, sempre per identificador oficial únic:

1. Les metadades de l'índex complet, sense modificar-les.
2. La cua de 830 i les seves incidències documentals.
3. Les **decisions individuals documentades** en fitxers `auditoria_mediambient_lot*.csv` (separador `;`), que aporten fonts i grau de revisió.

Les 34 decisions històriques només conservades com a agregat **no es fusionen** amb les noves, perquè no en coneixem els identificadors. Una inclusió amb revisió parcial continua tenint pendents; no es converteix en fitxa definitivament auditada.

## Resultats reproduïbles

- `data/treball/registre_auditoria_ambient_xv.csv`: els 830 candidats, amb estat **INCLOURE, EXCLOURE, FRONTERER o PENDENT**, fonts i grau de revisió.
- `data/treball/pla_lots_ambient_xv.csv`: les iniciatives que continuen pendents, repartides en lots de 40 i amb una puntuació *només per ordenar lectures*.
- `data/treball/control_omissions_ambient_xv.csv`: selecció de registres **fora de cua**, per cercar falsos negatius; combina alertes terminològiques i controls sistemàtics per sèrie.
- `data/treball/estat_auditoria_ambient_xv.json`: recompte auditable, sense rànquings de grups ni percentatges d'exhaustivitat.

La selecció de controls **no és estadísticament aleatòria**: serveix per detectar omissions, no per estimar amb garanties una taxa de falsos negatius.

## Com avançar

Després d'obrir una fitxa oficial i el seu BOCG, cal llegir l'objecte, el dispositiu, els possibles canvis, el resultat i les signatures. Es crea el següent fitxer `data/treball/auditoria_mediambient_lot02_YYYY-MM-DD.csv` amb la mateixa capçalera que el lot 01, identificadors únics, notes i fonts. **El programa no decideix automàticament la pertinència ambiental.** Les etiquetes proposades a partir dels títols no equivalen a una lectura.

El pla es pot regenerar amb:

```bash
python -m unittest discover -s tests -v
python scripts/gestiona_auditoria_ambiental.py
```

Les tasques de GitHub Actions executen aquestes comprovacions i desen els quatre fitxers de sortida a la branca de treball. No toquen `data/iniciatives.json`, ni `main`, ni el web.

**Publicació futura:** caldrà auditar decisions i errors d'omissió, estudiar les esmenes, votacions i autoria concreta del Grup Mixt, i revisar per separat les iniciatives del Govern abans de derivar conclusions comparatives.
