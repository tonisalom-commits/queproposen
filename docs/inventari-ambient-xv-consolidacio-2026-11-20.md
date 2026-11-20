# Consolidació documental de Medi Ambient · XV legislatura

**Data:** 20/11/2026. **Estat:** corpus de revisió consolidat, **NO inventari ambiental exhaustiu ni definitivament auditat**.

## Recompte reconciliat

| Sèrie | Univers oficial recuperat el 19/11 | Cua de revisió consolidada |
| --- | ---: | ---: |
| 161 — PNL en comissió | 3.824 | 640 |
| 162 — PNL al Ple | 850 | 145 |
| 122 — proposicions de llei de grups | 306 | 32 |
| 120 — iniciatives legislatives populars | 49 | 7 |
| 123 — proposicions de diputats | 2 | 0 |
| 124 — proposicions del Senat | 47 | 5 |
| 125 — proposicions autonòmiques | 16 | 1 |
| **Total** | **5.094** | **830** |

El recompte precedent de 5.029 només incloïa quatre sèries (161, 162, 122 i 120). Les sèries 123, 124 i 125 hi aporten 65 expedients, però no són propostes del mateix origen que les presentades per grups del Congrés.

El filtre inicial havia identificat 410 candidats. La primera fase documental suma **621 expedients únics** (410 per títol, 55 per termes complementaris i 160 de control d'exclusions; quatre coincidències entre els dos darrers subconjunts). El segon cribratge n'incorpora **205 sense duplicacions**: total **826 fitxes oficials recuperades**. En comparar-les amb les 25 fitxes de la mostra web, s'han identificat **quatre omissions**:

- 161/000070 — vols curts (Sumar)
- 161/003542 — futur sostenible del camp (PSOE)
- 162/000360 — ecocidi al Codi penal (Sumar)
- 162/000825 — qualitat de l'aire interior (Sumar)

Aquests quatre expedients no tenen còpia de la fitxa oficial als dos corpus descarregats; les seves referències s'han incorporat amb **procedència web explícita**. La cua passa de **826 a 830** registres únics; les 25 fitxes web ara hi estan referenciades.

## Qualitat de l'evidència

Dels 826 expedients descarregats, **795** disposen d'un fragment de primera publicació del BOCG que identifica l'expedient; **31** no. Les 4 fitxes web rescatades encara no tenen còpia documental en aquests corpus: **35 incidències totals**. En la primera fase, quatre fonts descarregades no contenien un fragment inequívoc de l'expedient; per això es compten 598 fragments localitzats, no 602. A la segona fase n'hi ha 197.

L'informe previ recull **34 primeres decisions temàtiques** (19 inclusions, 10 exclusions i 5 casos fronterers). **El fitxer que assignava les decisions a expedients no és als dos artefactes consultats**: aquest recompte agregat s'ha preservat però **no s'ha atribuït artificialment cap decisió a cap ID**. Els **4.264 expedients fora de la cua** no es poden etiquetar com a exclosos.

**Limitació crítica:** el control previ dels 5.094 expedients disposava de 206 pàgines originals d'índex, però els dos ZIP emprats en aquesta consolidació no les contenen. El total de 5.094 prové de [data/cobertura-ambiental.json](../data/cobertura-ambiental.json) i de l'auditoria del 19/11; no s'ha repetit independentment aquesta extracció. Cal preservar també les 206 pàgines d'índex si es vol una auditoria completament reproduïble de tot l'univers.

## Fitxers de treball incorporats

- [Inventari de la cua consolidada — 830 expedients](../data/treball/inventari_ambient_xv_830.csv)
- [Incidències documentals — 35 expedients](../data/treball/incidencies_ambient_xv_35.csv)
- [Manifest i procedència](../data/treball/manifest_ambient_xv.json)
- [Programa de consolidació](../scripts/consolida_ambient_xv.py)
- [Execució que ha consolidat i desat els fitxers](https://github.com/tonisalom-commits/queproposen/actions/runs/44694810933)
- [Corpus de la primera fase (621)](https://github.com/tonisalom-commits/queproposen/actions/runs/44630938748)
- [Segon cribratge (205)](https://github.com/tonisalom-commits/queproposen/actions/runs/44632672066)

Els CSV són **dades de treball**, no alimenten automàticament \`data/iniciatives.json\` ni la web publicada. Els artefactes d'Actions són temporals i s'han de guardar per preservar els fragments originals. La classificació ambiental individual, els dispositius, les esmenes, els partits del Grup Mixt, les votacions i els textos definitius continuen pendents d'auditoria. **No es poden publicar percentatges ni rànquings de partits a partir d'aquesta cua.**
