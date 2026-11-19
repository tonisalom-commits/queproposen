'use strict';
const {resum,grups,iniciatives}=window.DADES;
const fmt=new Intl.NumberFormat('ca-ES');
const el=id=>document.getElementById(id);
const clean=x=>String(x??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names=Object.fromEntries(grups.map(g=>[g.id,g.nom]));
el('totalPnls').textContent=fmt.format(resum.total);
el('plePnls').textContent=fmt.format(resum.ple);
el('comPnls').textContent=fmt.format(resum.comissio);
el('cadPnls').textContent=fmt.format(resum.caducades);
const topics=window.DADES.temes;
el('topic').insertAdjacentHTML('beforeend',topics.map(t=>'<option value="'+esc(t)+'">'+esc(t)+'</option>').join(''));
el('party').insertAdjacentHTML('beforeend',grups.map(g=>'<option value="'+esc(g.id)+'">'+esc(g.id)+' · '+esc(g.nom)+'</option>').join(''));
let selectedKind='';
function card(p){
 const tags=p.grups.map(g=>'<span class="chip '+(g==='MIXT'?'emphasis':'')+'" title="'+esc(names[g]||g)+'">'+esc(g==='MIXT'?(p.impulsor?'MIXT · '+p.impulsor:'GRUP MIXT'):g)+'</span>').join('');
 return '<article class="proposal"><div class="proposal-top"><span class="kind-chip '+(p.tipus==='PL'?'kind-law':'')+'">'+esc(p.tipus==='PL'?'Proposició de llei':'PNL')+'</span>'+tags+'<span class="topic-chip">'+esc(p.tema)+'</span></div>'+
 '<span class="action-line">'+esc(p.accio)+'</span><h3>'+esc(p.titol)+'</h3>'+
 '<p class="summary">'+esc(p.resum)+'</p><p class="reading"><b>Què ens indica?</b> '+esc(p.lectura)+'</p>'+
 '<footer><div class="meta"><span>EXP. '+esc(p.id)+'</span><span>'+esc(p.ambit)+' · '+esc(p.estat)+'</span></div>'+
 '<a class="source-link" href="'+esc(p.url)+'" target="_blank" rel="noopener noreferrer">Consulta l’expedient oficial ↗</a>'+
 '<details class="details"><summary>Grau de revisió de la fitxa</summary><p>'+esc(p.qualitat)+'</p></details></footer></article>';
}
function draw(){
 const q=clean(el('search').value.trim()),topic=el('topic').value,party=el('party').value;
 const found=iniciatives.filter(p=>(!q||clean([p.id,p.titol,p.resum,p.lectura,p.accio,p.tema,...p.grups].join(' ')).includes(q))&&(!topic||p.tema===topic)&&(!party||p.grups.includes(party))&&(!selectedKind||p.tipus===selectedKind));
 el('cards').innerHTML=found.length?found.map(card).join(''):'<div class="empty">No hi ha fitxes d’aquesta selecció que coincideixin amb els filtres. Això no significa que el grup no hagi presentat iniciatives sobre el tema.</div>';
 el('count').textContent=found.length+' de '+iniciatives.length+' fitxes de la selecció preliminar';
 for(const b of document.querySelectorAll('.type-button'))b.setAttribute('aria-pressed',String(b.dataset.kind===selectedKind));
}
for(const id of ['search','topic','party'])el(id).addEventListener(id==='search'?'input':'change',draw);
el('reset').addEventListener('click',()=>{for(const id of ['search','topic','party','ambit'])el(id).value='';draw();});
document.querySelectorAll('.type-button').forEach(b=>b.addEventListener('click',()=>{selectedKind=b.dataset.kind;draw();}));
const ordered=[...grups].sort((a,b)=>(b.ple+b.comissio)-(a.ple+a.comissio));
const max=ordered[0].ple+ordered[0].comissio;
el('bars').innerHTML=ordered.map(g=>{const n=g.ple+g.comissio;return '<div class="bar-row" role="listitem" aria-label="'+esc(g.nom)+': '+fmt.format(n)+' PNL"><span class="bar-name" title="'+esc(g.nom)+'">'+esc(g.id)+'</span><div class="track" aria-hidden="true"><div class="fill" style="width:'+((n/max)*100).toFixed(2)+'%"></div></div><strong class="bar-value">'+fmt.format(n)+'</strong></div>';}).join('');
draw();