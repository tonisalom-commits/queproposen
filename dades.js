/*
 * Què proposen? — DADES PROVISIONALS
 * Totals: Àgora, https://agora.vedratic.com/ca/learn/pnl/
 * Fitxes: selecció il·lustrativa d'iniciatives; NO mostra representativa.
 * Les interpretacions editorials NO són cites literals del Congrés.
 */
const punt = (id) => 'https://www.congreso.es/es/busqueda-de-iniciativas?_iniciativas_id=' + encodeURIComponent(id) + '&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle&p_p_id=iniciativas&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal';
const font = 'Fitxa resumida a partir del títol i l’expedient; cal revisar íntegrament els punts dispositius.';
window.DADES = {
  resum: {legislatura:'XV',inici:'17/08/2023',final:'06/10/2026',total:4673,ple:850,comissio:3823,aprovades:1231,caducades:2692,font:'https://agora.vedratic.com/ca/learn/pnl/'},
  grups: [
    {id:'PP',nom:'Partit Popular',ple:240,comissio:1370,aprovadesPle:37,aprovadesComissio:498},
    {id:'PSOE',nom:'Partit Socialista Obrer Espanyol',ple:123,comissio:569,aprovadesPle:36,aprovadesComissio:304},
    {id:'SUMAR',nom:'Sumar',ple:127,comissio:571,aprovadesPle:6,aprovadesComissio:99},
    {id:'VOX',nom:'Vox',ple:152,comissio:553,aprovadesPle:0,aprovadesComissio:60},
    {id:'MIXT',nom:'Grup Mixt (formacions diferents)',ple:157,comissio:425,aprovadesPle:2,aprovadesComissio:49},
    {id:'ERC',nom:'Grup Republicà (ERC)',ple:13,comissio:143,aprovadesPle:3,aprovadesComissio:56},
    {id:'JUNTS',nom:'Junts per Catalunya',ple:13,comissio:37,aprovadesPle:3,aprovadesComissio:17},
    {id:'BILDU',nom:'EH Bildu',ple:3,comissio:26,aprovadesPle:1,aprovadesComissio:6},
    {id:'PNB',nom:'Grup Basc (EAJ-PNB)',ple:5,comissio:9,aprovadesPle:3,aprovadesComissio:3}
  ],
  iniciatives: [
    {id:'161/002133',grups:['PP'],tema:'Habitatge',accio:'Derogar i substituir',titol:'Derogar la Llei pel dret a l’habitatge i elaborar una nova norma',resum:'Planteja derogar la llei vigent i impulsar una altra regulació orientada a augmentar l’oferta i reforçar la seguretat jurídica.',lectura:'Prioritza un marc normatiu diferent de l’actual, centrat en l’oferta.',ambit:'Comissió',estat:'Aprovada',qualitat:'Títol i expedient contrastats; síntesi introductòria, no anàlisi del text íntegre.'},
    {id:'161/002116',grups:['PSOE'],tema:'Habitatge',accio:'Mobilitzar recursos',titol:'Desplegar els recursos disponibles per garantir l’accés a l’habitatge',resum:'Reclama mobilitzar recursos públics en matèria d’accés a l’habitatge.',lectura:'Defensa l’actuació pública, sense que el títol permeti determinar totes les mesures concretes.',ambit:'Comissió',estat:'Rebutjada',qualitat:font},
    {id:'162/000498',grups:['SUMAR'],tema:'Habitatge',accio:'Limitar l’especulació',titol:'Frenar l’especulació immobiliària i garantir l’accés a un habitatge digne',resum:'Proposa mesures per limitar l’ús especulatiu de l’habitatge.',lectura:'Prioritza intervenir sobre l’especulació com a obstacle per accedir a un habitatge.',ambit:'Ple',estat:'Rebutjada',qualitat:'Expedient i resultat contrastats; manca desglossar les mesures.'},
    {id:'161/003360',grups:['VOX'],tema:'Medi ambient',accio:'Revocar i derogar',titol:'Revocar l’obligatorietat de les zones de baixes emissions',resum:'Demana revertir l’obligatorietat municipal d’aquestes zones i promoure la derogació de la Llei 7/2021 de canvi climàtic.',lectura:'S’oposa a instruments concrets de regulació climàtica i del trànsit urbà.',ambit:'Comissió mixta',estat:'Resultat no incorporat',qualitat:'Peticions verificades al BOCG; resultat parlamentari pendent de codificar.'},
    {id:'162/000580',grups:['ERC'],tema:'Habitatge',accio:'Regular i adquirir',titol:'Mesures fiscals, reguladores i d’adquisició pública per al dret a l’habitatge',resum:'Combina mesures fiscals, reguladores i d’adquisició pública.',lectura:'Defensa utilitzar diferents instruments públics per assegurar el dret a l’habitatge.',ambit:'Ple',estat:'Resultat no incorporat',qualitat:font},
    {id:'161/001358',grups:['JUNTS'],tema:'Habitatge',accio:'Transferir recursos',titol:'Cedir a Catalunya els habitatges i sòls de la SAREB',resum:'Demana transferir a Catalunya immobles i sòls de la SAREB situats al territori.',lectura:'Prioritza el traspàs territorial de recursos públics d’habitatge.',ambit:'Comissió',estat:'Rebutjada',qualitat:'Títol i autoria contrastats; resultat identificat al Congrés.'},
    {id:'161/003346',grups:['MIXT'],tema:'Habitatge',accio:'Limitar l’acumulació',titol:'Limitar l’acumulació especulativa d’habitatge',resum:'Reclama mesures contra la concentració especulativa d’habitatges.',lectura:'Planteja una regulació de l’acumulació especulativa.',ambit:'Comissió',estat:'Resultat no incorporat',qualitat:'Formació concreta del Grup Mixt pendent d’identificar. No atribuir al conjunt del grup.'},
    {id:'162/000167',grups:['BILDU'],tema:'Habitatge',accio:'Garantir l’accés',titol:'Mesures per assegurar el dret efectiu a l’habitatge',resum:'Planteja mesures per fer efectiu el dret a l’habitatge.',lectura:'Situa la garantia efectiva de l’accés a l’habitatge com a objectiu.',ambit:'Ple',estat:'Rebutjada',qualitat:'Títol, autoria i resultat contrastats; manca desglossar el text complet.'},
    {id:'162/000822',grups:['PNB'],tema:'Infraestructures',accio:'Impulsar infraestructures',titol:'Variant Sud Ferroviària i transport de mercaderies al País Basc',resum:'Proposa actuacions sobre la Variant Sud Ferroviària i la Y basca i mesures mitigadores locals.',lectura:'Prioritza una infraestructura ferroviària concreta i els efectes territorials.',ambit:'Ple',estat:'Aprovada',qualitat:'Títol, autoria i aprovació contrastats al Congrés.'},
    {id:'162/000728',grups:['PNB'],tema:'Indústria i energia',accio:'Reforçar la indústria',titol:'Competitivitat de la indústria siderúrgica i electrointensiva',resum:'Reclama reforçar la competitivitat i resiliència d’aquests sectors.',lectura:'Situa la indústria intensiva en energia entre les seves prioritats.',ambit:'Ple',estat:'Resultat no incorporat',qualitat:font},
    {id:'162/000797',grups:['BILDU','PNB','SUMAR','MIXT'],tema:'Defensa i territori',accio:'Cessar una activitat',titol:'Cessar l’activitat del polígon de tir de Bardenas',resum:'Iniciativa presentada conjuntament per diversos grups.',lectura:'Mostra una coincidència formal entre grups sobre una instal·lació militar.',ambit:'Ple',estat:'Resultat no incorporat',qualitat:'Coautoria contrastada; cal identificar els diputats del Grup Mixt i analitzar el text.'}
  ].map(p=>({...p,url:punt(p.id)}))
};