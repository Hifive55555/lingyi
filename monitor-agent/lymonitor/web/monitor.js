'use strict';
// 监控小窗：连监控智能体的 WebSocket（默认 127.0.0.1:8762/ws），按 空 / 海 / 陆 三组
// 展示“我方哪些单元正被指着”，每个单元后面跟着指向它的每一枚弹（弹型 / 弹速 / 距离 / 剩余秒）。
const $ = id => document.getElementById(id);
const AGENT = new URLSearchParams(location.search).get('agent') || '127.0.0.1:8762';
const GRP = [['air', '空'], ['sea', '海'], ['land', '陆']];
const SIDE_CN = {red: '红方', blue: '蓝方'};

let snap = null, snapAt = 0, ws = null, lastMsg = 0;
let onlyHit = localStorage.getItem('mvOnlyHit') !== '0';
let bySpeed = localStorage.getItem('mvBySpeed') === '1';
let q = '', fold = new Set(JSON.parse(localStorage.getItem('mvFold') || '[]'));

const esc = t => String(t).replace(/[&<>"]/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[ch]));
const fmtT = t => { t = Math.max(0, Math.round(t)); return `${Math.floor(t / 3600)}:${String(Math.floor(t % 3600 / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`; };
const live = () => Date.now() - snapAt < 8000;
const kmh = v => (v >= 1000 ? `${(v / 1000).toFixed(2)}k` : Math.round(v));

// 弹型名缩短：去掉括号里的参数，留主型号
const wname = n => (n || '').split(/[\[\(（,，]/)[0].trim() || '未识别弹';

function connect() {
  ws = new WebSocket(`ws://${AGENT}/ws`);
  ws.onopen = () => { lastMsg = Date.now(); };
  ws.onclose = () => { con('● 无对局', 'bad'); setTimeout(connect, 1500); };
  ws.onerror = () => { try { ws.close(); } catch (e) {} };
  ws.onmessage = e => {
    lastMsg = Date.now();
    let d; try { d = JSON.parse(e.data); } catch (err) { return; }
    if (d.type === 'snap') onSnap(d);
  };
}
function con(text, cls) { $('conn').textContent = text; $('conn').className = cls; }
setInterval(() => {
  if (ws && ws.readyState === 1 && Date.now() - lastMsg > 8000) { ws.close(); return; }
  if (!live()) con('● 无对局', 'bad');
}, 1000);

function onSnap(d) {
  snapAt = Date.now(); snap = d;
  $('clock').textContent = fmtT(d.t || 0);
  const g = d.groups || {};
  const all = g.all || [0, 0];
  $('stat').innerHTML = `被攻击 <b>${all[0]}</b> <i>/ ${all[1]}</i>`;
  $('mstat').textContent = `敌方弹药 ${d.ms || 0}`;
  con(d.started ? '● 监控中' : '● 战前', 'ok');
  const side = d.side || '';
  $('brand').textContent = '◎ 监控 ' + (side || '');
  $('brand').style.color = side === '蓝方' ? '#3fd0e6' : '#ff6070';
  if (d.cfg) $('msg').textContent =
    '本智能体只做监控，不下发任何指令。判定：弹在朝我飞就算（不设距离/时间门限）；'
    + `决策间隔 ${d.cfg.sec} s 仿真时间`;
  render();
}

// ---------------------------------------------------------------- 渲染
const numOf = n => { const m = /#(\d+)\s*$/.exec(n || ''); return m ? m[1] : ''; };
const matcher = () => {
  const toks = q.trim().split(/\s+/).filter(Boolean).map(t => t.replace(/^#/, ''));
  if (!toks.length) return null;
  return n => { const nn = String(n).toLowerCase().replace(/[\s\-_·.“”"]/g, ''); const num = numOf(n);
                return toks.every(t => /^\d+$/.test(t) ? num === t : nn.includes(t.toLowerCase())); };
};

function cls(h) {
  if (h.tgo == null) return 't0';
  if (h.tgo <= 30) return 't1';
  if (h.tgo <= 90) return 't2';
  return 't3';
}
function msChip(h) {
  // 只显示当前弹速（km/h）；距离 / 最近接近 / 预计命中放悬停里
  const spd = h.spd || 0;
  return `<span class="mc ${cls(h)}" title="当前弹速 ${kmh(spd)} km/h（${(spd / 1.852).toFixed(0)} 节）`
    + `\n当前距离 ${(h.d || 0).toFixed(1)} km　最近接近 ${(h.cpa || 0).toFixed(1)} km`
    + `\n预计到最近接近点 ${h.tgo == null ? '未知' : Math.round(h.tgo) + ' s'}">`
    + `<span class="mn">${esc(wname(h.n) || ('弹' + (h.db || '')))}</span>`
    + `<span class="sp">${kmh(spd)} km/h</span>`
    + `<span class="dd">${(h.d || 0).toFixed(0)}km</span>`
    + `<span class="tg">${h.tgo == null ? '--' : Math.round(h.tgo) + 's'}</span></span>`;
}
function unitRow(r) {
  const ms = (r.ms || []).slice();
  if (bySpeed) ms.sort((a, b) => (b.spd || 0) - (a.spd || 0));
  const alt = r.g === 'air' ? `<u>${Math.round(r.alt / 100) / 10}km</u>` : '';
  const dmg = (r.dmg || 0) >= 1 ? `<u class="dmg" title="已受损 ${Math.round(r.dmg)}%">损${Math.round(r.dmg)}%</u>` : '';
  return `<div class="row ${r.hit ? 'hit' : 'safe'}">`
    + `<span class="u" title="${esc(r.n)}">${esc(r.n)}${alt}${dmg}</span>`
    + `<span class="ms">${ms.length ? ms.map(msChip).join('') : '<span class="sub">—</span>'}</span></div>`;
}
function render() {
  if (!snap) { $('list').innerHTML = '<div class="empty" style="padding:8px">等待智能体…（客户端里导入 monitor_ai.py 并启动）</div>'; return; }
  const qm = matcher();
  const rows = (snap.rows || []).filter(r => (!onlyHit || r.hit) && (!qm || qm(r.n)));
  const groups = snap.groups || {};
  let html = '';
  for (const [k, cn] of GRP) {
    const gv = groups[k] || [0, 0];
    const list = rows.filter(r => r.g === k);
    const isFold = fold.has(k);
    html += `<div class="sec"><div class="hd ${isFold ? 'fold' : ''}" data-g="${k}">`
      + `<span class="nm">${cn}</span>`
      + `<span class="ct">被攻击 <b>${gv[0]}</b> / ${gv[1]}</span>`
      + `<span class="grow"></span><span class="sub">${isFold ? '▸' : '▾'}</span></div><div class="bd">`;
    html += list.length ? list.map(unitRow).join('') : '<div class="empty">无</div>';
    html += '</div></div>';
  }
  const top = $('list').scrollTop;
  $('list').innerHTML = html;
  $('list').scrollTop = top;
  const air = groups.air || [0, 0], sea = groups.sea || [0, 0], land = groups.land || [0, 0];
  document.title = (air[0] + sea[0] + land[0]) ? `监控 ${air[0]}/${sea[0]}/${land[0]}` : '监控小窗';
}

// ---------------------------------------------------------------- 交互
$('list').addEventListener('click', e => {
  const h = e.target.closest('.hd');
  if (!h) return;
  const k = h.dataset.g;
  fold.has(k) ? fold.delete(k) : fold.add(k);
  localStorage.setItem('mvFold', JSON.stringify([...fold]));
  render();
});
$('onlyHit').onclick = () => {
  onlyHit = !onlyHit; localStorage.setItem('mvOnlyHit', onlyHit ? '1' : '0');
  $('onlyHit').classList.toggle('on', onlyHit); render();
};
$('bySpeed').onclick = () => {
  bySpeed = !bySpeed; localStorage.setItem('mvBySpeed', bySpeed ? '1' : '0');
  $('bySpeed').classList.toggle('on', bySpeed); render();
};
$('q').addEventListener('input', e => { q = e.target.value; render(); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { if (e.target.id === 'q') { e.target.value = ''; q = ''; render(); } else $('q').focus(); }
  else if (e.key === 'f' || e.key === '/') { e.preventDefault(); $('q').focus(); }
});

$('onlyHit').classList.toggle('on', onlyHit);
$('bySpeed').classList.toggle('on', bySpeed);
connect();
render();
