# Control de falsos negatius · XV legislatura · 20/11/2026

**Document de treball, no publicable com a resultat concloent.** La mostra aleatòria estratificada de 100 expedients fora de la cua ambiental inicial és reproduïble (llavor 20261120), però les decisions classificatòries i els estrats petits imposen limitacions importants. El web públic i l'univers de 5.094 expedients no s'han alterat.

## Estat observat

- **100 expedients** seleccionats entre els **4.264** que havien quedat fora de la cua inicial de 830.
- **96** amb decisió individual registrada: **8 INCLOURE**, **82 EXCLOURE** i **6 FRONTERER**.
- **4 pendents** perquè no s'ha recuperat o comprovat prou text dispositiu o articulat.
- **135 decisions individuals** en tots els lots acumulats, incloses **41 inclusions**, **85 exclusions** i **9 casos fronterers**. No confondre amb 135 fitxes íntegrament auditades fins a votacions.
- **857 registres** a l'inventari ambiental ampliat de treball: 830 originals més 27 decisions d'inclusió o frontera recuperades de fora de cua. Els 857 no són 857 inclusions ambientals comprovades.

La taula de la mostra és a [mostra_aleatoria_fora_cua_xv_100.csv](../data/treball/mostra_aleatoria_fora_cua_xv_100.csv). Els càlculs, reproduïbles mitjançant `python scripts/estima_omissions_mostra_xv.py`, es desen a [diagnostic_provisional_omissions_mostra_xv.json](../data/treball/diagnostic_provisional_omissions_mostra_xv.json).

## Desglossament i sensibilitat de classificació

| Sèrie | Fora cua original (N) | Mostra (n) | Inclusió | Exclusió | Fronterer | Pendent | Expansió només inclosos |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 42 | 2 | 0 | 0 | 0 | 2 | 0,00 |
| 122 | 274 | 7 | 0 | 7 | 0 | 0 | 0,00 |
| 123 | 2 | 1 | 0 | 0 | 1 | 0 | 0,00 |
| 124 | 42 | 2 | 0 | 2 | 0 | 0 | 0,00 |
| 125 | 15 | 1 | 0 | 1 | 0 | 0 | 0,00 |
| 161 | 3.184 | 71 | 7 | 58 | 4 | 2 | 313,92 |
| 162 | 705 | 16 | 1 | 14 | 1 | 0 | 44,06 |
| **Total** | **4.264** | **100** | **8** | **82** | **6** | **4** | **357,98** |

### Interpretació matemàtica precisa

Per cada sèrie (h), el valor d'expansió de les inclusions observades és (N_h\cdot k_h/n_h), on (N_h) és el nombre d'expedients fora de cua, (n_h) la mostra seleccionada i (k_h) les inclusions. La suma de les expansions de les **8 inclusions** és **357,98**.

Si les **6 decisions frontereres i els 4 pendents** fossin classificats tots com a inclusions, l'expansió de l'escenari seria **715,11**.

**ATENCIÓ: ni 358 ni 715 són el nombre real d'omissions, i aquest interval NO és un interval de confiança ni tan sols una cota garantida del total poblacional.** Són dues expansions condicionals de les categories observades en aquesta mostra. La mostra és aleatòria, però la variabilitat mostral pot fer que el nombre real quedi per sota o per damunt d'aquestes xifres.

No hem estimat un marge d'error defensable. En particular, les sèries **123 i 125 tenen un sol cas seleccionat**, de manera que ni tan sols es pot estimar la variància interna d'aquests estrats a partir de la mostra. A més, la classificació ambiental secundària i les decisions frontera requereixen consens metodològic; l'error de classificació no s'ha quantificat. **No publicar encara cap xifra global inferida ni comparació partidista.**

## Quatre expedients encara no resolts

| ID | Font oficial disponible | Què impedeix la classificació |
| --- | --- | --- |
| **120/000034** | [BOCG D-407](https://www.congreso.es/public_oficiales/L15/CONG/BOCG/D/BOCG-15-D-407.PDF), tràmit inicial de la ILP per reformar la llei d'educació | La publicació de l'acord no inclou l'articulat de la comissió promotora; cal comprovar si la reforma conté obligacions d'educació ambiental. |
| **120/000043** | [Fitxa del Congrés](https://www.congreso.es/es/proposiciones-de-ley?_iniciativas_id=120%2F000043&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle&p_p_id=iniciativas&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal) i [BOCG D-493](https://www.congreso.es/en/busqueda-de-publicaciones?_publicaciones_id_texto=%28BOCG-15-D-493.CODI.%29&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal), només tràmit inicial | No s'ha recuperat l'articulat sobre transparència i denunciants. La fitxa indica termini de signatures fins al **31/12/2026**, no aprovació de llei. |
| **161/003710** | [Fitxa de la PNL](https://www.congreso.es/es/busqueda-de-iniciativas?_iniciativas_id=161%2F003710&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle&p_p_id=iniciativas&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal) | La descripció tracta de la llei de famílies; falta el dispositiu per descartar continguts ambientals incidentals. |
| **161/003820** | [Fitxa de la PNL](https://www.congreso.es/es/busqueda-de-iniciativas?_iniciativas_id=161%2F003820&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle&p_p_id=iniciativas&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal) | Cooperació industrial i euroregions; el títol no permet saber si demana reduccions d'emissions, economia circular o solament mesures institucionals. |

Les fitxes de les dues PNL no varen oferir un text dispositiu recuperable mitjançant les consultes actuals. Això **no demostra que no existeixi**, només que encara no se n'ha verificat una còpia llegible. No es traslladen automàticament a EXCLOURE.

## Revisió documental de la mostra

Els lots 08–14 registren 96 decisions de la mostra, amb graus de revisió desiguals. L'etiqueta `AUDITAT` del programa d'integració significa que existeix **una decisió individual amb font oficial declarada i mesures resumides**, però el control informàtic comprova principalment identificadors, camps i el domini institucional dels enllaços: **no demostra que el fragment citat sigui correcte o que l'autor hagi verificat esmenes i votacions**.

Per tant, abans d'usar aquesta mostra per a inferència estadística o publicació cal:

1. Resoldre els quatre textos mancants o assignar-los explícitament l'estat **NO VERIFICABLE AMB LA FONT PUBLICADA**, sense suplantar aquesta manca amb exclusió.
2. Reavaluar amb criteri fix les sis categories **FRONTERER** (energia, transport, urbanisme, benestar animal, indústria, etc.).
3. Verificar que una segona revisió independent dels 96 casos coincideix amb el text dispositiu real; registrar discrepàncies, correccions i data.
4. Augmentar el nombre de controls de les sèries 123 i 125 i considerar una ampliació de la mostra 161, abans de calcular intervals de confiança.
5. Mantenir separades la **completesa del cens de set sèries**, l'**exhaustivitat de classificació temàtica** i la **verificació de textos finals/votacions**. Són tres coses diferents.

## Decisió de publicació

No publicar ara la mostra com a evidència d'«inventari exhaustiu de Medi Ambient» ni generar rànquings dels grups. La magnitud de les expansions condicionals és un senyal que l'actual filtre per títols podria haver omès una quantitat important de propostes; l'actuació prioritària és **millorar la recuperació íntegra dels textos dels 4.264 fora de cua i sotmetre'ls a un segon classificació supervisada**, no maquillar els quatre registres difícils.

**Integració i documents:** tot es conserva a `feat/prototip-atles-pnl` sense alterar `main` ni el catàleg visible del web.
