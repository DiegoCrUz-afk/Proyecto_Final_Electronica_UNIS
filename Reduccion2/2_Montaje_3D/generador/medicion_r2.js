// ---------- Reduccion 2: modo medicion con 6 campos por prueba (reemplaza medPts, showMeas y medShow de la v3) ----------
function epRef(spec, defBoard){
  if (spec && spec.txt) return {txt: spec.txt};
  if (spec && spec.rail){
    const gx = spec.rail === 'v5' ? -3 : -2, nm = spec.rail === 'v5' ? '+5 V' : 'GND';
    return {pt: V3(X(spec.board, gx), 0, Z(DATA.gnd[spec.board].y)), board: spec.board, text: spec.board + '-riel ' + nm + ' izq fila ' + (NR - 1 - DATA.gnd[spec.board].y), short: 'riel ' + nm + ' de la placa ' + spec.board};
  }
  const po = partObjs[spec[0]], q = po.data.pins.find(r => r.n === spec[1]);
  return {pt: pw(po.data, q), board: po.data.board, text: holeName(po.data, q) + ', red ' + netLabel(q.net), short: po.data.short + ' pata ' + q.n, ref: po.data.ref};
}
function medEnds(m){
  const r = epRef(m.red), bd = r.board || DATA.boards_list[0];
  const n = m.black ? epRef(m.black, bd) : epRef({rail: '0', board: bd});
  return {r, n};
}
function showMeas(id, fly, quiet){
  const m = measById[id]; if (!m) return; clearFx(); selected = null;
  const e = medEnds(m);
  if (e.r.pt) probeAt(e.r.pt, 0xff3b30, '#ff5a4d', 'ROJA (+) · ' + e.r.short, 0);
  if (e.n.pt) probeAt(e.n.pt, 0x222222, '#ffffff', 'NEGRA (−) · ' + e.n.short, 1);
  focus = null; applyFocus();
  const t0 = e.r.pt || e.n.pt;
  if (fly && t0){ const t = t0.clone(); flyTo(t, t.clone().add(V3(0, 90, 55)), 800); }
}
function medShow(){
  const box = $('medBox');
  if (medBi < 0){ box.innerHTML = ''; medMark(); return; }
  if (medBi >= MEDB.length) return medFinal();
  const b = MEDB[medBi], ids = DATA.med[b], B = DATA.blocks[b];
  const head = '<div class="hint">Bloque ' + (medBi + 1) + ' de ' + MEDB.length + '</div><div style="font-size:14px"><b>' + B.title + '</b></div>';
  if (medK >= ids.length) return medSummary(b, ids, head);
  const m = measById[ids[medK]], e = medEnds(m);
  showMeas(m.id, true, true);
  const redT = e.r.txt ? e.r.txt : '<b>' + e.r.short + '</b> (' + e.r.text + ')';
  const negT = e.n.txt ? e.n.txt : '<b>' + e.n.short + '</b> (' + e.n.text + ')';
  const tab = m.tabla ? '<table style="width:100%;border-collapse:collapse;margin:4px 0;font-size:12.5px">' + m.tabla.map(r => '<tr><td style="padding:2px 6px;border:1px solid #39424c">' + r[0] + '</td><td style="padding:2px 6px;border:1px solid #39424c"><b>' + r[1] + '</b></td></tr>').join('') + '</table>' : '';
  let h = head + '<div class="hint">Prueba ' + (medK + 1) + ' de ' + ids.length + (m.rieles ? ' · <span style="color:#ffb454">depende de los rieles de la BX-4135 (por confirmar)</span>' : '') + '</div>' +
    '<div style="margin:6px 0"><b>' + m.t + '</b></div>' +
    '<div style="margin:6px 0;padding:6px 8px;border-left:3px solid #ff5a4d;background:#1d2530"><b style="color:#ff5a4d">ROJA (+)</b>: ' + redT + '<br><b>NEGRA (−)</b>: ' + negT + '<br>Modo: <b>' + m.mode + '</b></div>' +
    '<div style="margin:4px 0"><b>Qué medimos:</b> ' + m.mide + '</div><div style="margin:4px 0"><b>Para qué sirve:</b> ' + m.sirve + '</div><div style="margin:4px 0"><b>Antes de medir:</b> ' + m.cond + '</div>' +
    '<div style="margin:6px 0"><b>Debe dar:</b> ' + m.exp + '</div>' + tab +
    '<div class="hint">Fuente del valor: ' + m.fuente + '</div>' + (m.nova ? '<div class="warn">NO validado todavía: depende del ' + m.nova + '.</div>' : '');
  if (medBad){
    h += '<div class="warn" style="margin-top:6px"><b>No salió igual.</b> Revisa en este orden:<ol style="margin:4px 0 4px 18px;padding:0">' + m.pasos.map(x => '<li>' + x + '</li>').join('') + '</ol></div>' +
      '<div class="row" style="margin-top:6px"><button data-a="again">Ya lo corregí: medir otra vez</button><button data-a="skip">Seguir de todos modos</button><button data-a="blk">Ver solo las piezas de este bloque</button></div>';
  } else {
    h += '<div class="row" style="margin-top:6px"><button data-a="ok">✔ Salió bien, siguiente</button><button data-a="bad">✖ No salió igual</button></div>' +
      '<div class="row" style="margin-top:4px"><button data-a="prev"' + (medK ? '' : ' disabled') + '>◀ Anterior</button><button data-a="blk">Ver solo las piezas de este bloque</button></div>';
  }
  box.innerHTML = h; medMark();
}
