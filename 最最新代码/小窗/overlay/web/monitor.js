'use strict';
// 监控小窗：跟「灵弈小窗」共用同一个智能体、同一个 WebSocket（127.0.0.1:8760/ws），
// 快照里多出来的 mon 字段就是被攻击监控（空 / 海 / 陆 三组，每个单元后面跟着指向它的
// 每一枚弹：弹型 / 弹速 / 距离→CPA / 到最近接近点的时间）。
//
// 版式：空 | 海 | 陆 三列并排，每列自己滚。
// 排序：默认**固定**（单元按编号、弹按弹型+距离），不再按 tgo 每帧重排 —— 之前
//       每帧顺序都在跳，看不住。想按威胁/弹速看，点掉「固定排序」再选。
const $ = id => document.getElementById(id);
const AGENT = new URLSearchParams(location.search).get('agent') || '127.0.0.1:8760';
const GRP = [['air', '空'], ['sea', '海'], ['land', '陆']];
const CN = {air: '空', sea: '海', land: '陆'};

let snap = null, snapAt = 0, ws = null, lastMsg = 0;
let onlyHit = localStorage.getItem('mvOnlyHit') !== '0';
let fixed = localStorage.getItem('mvFixed') !== '0';        // 默认固定排序
let q = '';
const fold = new Set(JSON.parse(localStorage.getItem('mvFold') || '[]'));

const esc = t => String(t).replace(/[&<>"]/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[ch]));
const fmtT = t => { t = Math.max(0, Math.round(t)); return `${Math.floor(t / 3600)}:${String(Math.floor(t % 3600 / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`; };
const live = () => Date.now() - snapAt < 8000;
const kmh = v => (v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(Math.round(v)));
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

function onSnap(msg) {
  // 同一个 ws 上还有 overlay 自己的字段：只认 type=snap，并且只取 mon 这一栏
  if (msg.type && msg.type !== 'snap') return;
  snapAt = Date.now();
  const d = msg.mon;
  if (!d) { snap = null; con('● 等待智能体', 'bad'); render(); return; }
  snap = d;
  $('clock').textContent = fmtT(d.t || 0);
  const g = d.groups || {};
  const all = g.all || [0, 0];
  $('stat').innerHTML = `被攻击 <b>${all[0]}</b> <i>/ ${all[1]}</i>`;
  $('mstat').textContent = `敌方弹药 ${d.ms || 0}`;
  con(d.started ? '● 监控中' : '● 战前', 'ok');
  const side = d.side || '';
  $('brand').textContent = '◎ 监控 ' + (side || '');
  $('brand').style.color = side === '蓝方' ? '#3fd0e6' : '#ff6070';
  render();
}

// ---------------------------------------------------------------- 排序
// 固定排序：单元按名字里的编号（苏35 #12 < #100），弹按「弹型 + 距离」。
// 都取“不会因为每帧数值抖动就改变”的键，所以顺序稳。
const numOf = n => { const m = /#(\d+)\s*$/.exec(n || ''); return m ? +m[1] : 1e9; };
const nameKey = r => [numOf(r.n), String(r.n || '')];
const msKeyFixed = h => [wname(h.n), -(h.d || 0)];
const msKeyThreat = h => [h.tgo == null ? 1 : 0, h.tgo == null ? 1e9 : h.tgo, -(h.cpa || 0)];
const msKeySpeed = h => [-Math.round((h.spd || 0) / 50)];      // 50km/h 一档，减少来回跳

function sortUnits(list) {
  if (fixed) return list.slice().sort((a, b) => {
    const ka = nameKey(a), kb = nameKey(b);
    return ka[0] - kb[0] || (ka[1] < kb[1] ? -1 : ka[1] > kb[1] ? 1 : 0);
  });
  // 非固定：被攻击的在前，越紧急越前
  return list.slice().sort((a, b) => (b.hit - a.hit) || (a.ms?.[0]?.tgo ?? 1e9) - (b.ms?.[0]?.tgo ?? 1e9));
}
function sortMs(list) {
  const k = fixed ? msKeyFixed : msKeyThreat;
  return (list || []).slice().sort((a, b) => {
    const ka = k(a), kb = k(b);
    for (let i = 0; i < ka.length; i++) {
      if (ka[i] < kb[i]) return -1;
      if (ka[i] > kb[i]) return 1;
    }
    return 0;
  });
}

// ---------------------------------------------------------------- 渲染
const matcher = () => {
  const toks = q.trim().split(/\s+/).filter(Boolean).map(t => t.replace(/^#/, ''));
  if (!toks.length) return null;
  return n => { const nn = String(n).toLowerCase().replace(/[\s\-_·.“”"]/g, ''); const num = String(numOf(n) === 1e9 ? '' : numOf(n));
                return toks.every(t => /^\d+$/.test(t) ? num === t : nn.includes(t.toLowerCase())); };
};

function cls(h) {
  if (h.tgo == null) return 't0';
  if (h.tgo <= 30) return 't1';
  if (h.tgo <= 90) return 't2';
  return 't3';
}
function msRow(h) {
  // 一行一枚弹：弹型 | 弹速 | 距离→CPA | 到 CPA 的时间
  // ⚠ tgo 是“到**最近接近点**的时间”，不是“命中时间”；擦边掠过的把时间压暗（graze）。
  const spd = h.spd || 0, d = h.d || 0, cpa = h.cpa || 0;
  const graze = d > 1 && cpa > d * 0.5;
  const cl = cls(h) + (graze ? ' graze' : '');
  const tg = h.tgo == null ? '—' : Math.round(h.tgo) + 's';
  return `<div class="mc ${cl}" title="弹型 ${esc(h.n) || '未识别'}`
    + `\n弹速 ${kmh(spd)} km/h（${(spd / 1.852).toFixed(0)} 节）`
    + `\n当前距离 ${d.toFixed(1)} km　最近接近点 CPA ${h.tgo == null ? '未知' : cpa.toFixed(1) + ' km'}`
    + `\n到最近接近点 ${h.tgo == null ? '未知（刚出现/数据不全）' : Math.round(h.tgo) + ' s'}`
    + (graze ? `\n⚠ 擦边掠过（CPA ${cpa.toFixed(0)} km），不是冲这个单元来的` : '') + `">`
    + `<span class="mn">${esc(wname(h.n))}</span>`
    + `<span class="sp">${kmh(spd)}</span>`
    + `<span class="dd">${d.toFixed(0)}→${h.tgo == null ? '?' : cpa.toFixed(0)}</span>`
    + `<span class="tg">${tg}</span></div>`;
}
function unitRow(r) {
  const ms = sortMs(r.ms);
  const alt = r.g === 'air' ? `<u>${Math.round((r.alt || 0) / 100) / 10}km</u>` : '';
  const dmg = (r.dmg || 0) >= 1 ? `<u class="dmg" title="已受损 ${Math.round(r.dmg)}%">损${Math.round(r.dmg)}%</u>` : '';
  return `<div class="row ${r.hit ? 'hit' : 'safe'}">`
    + `<div class="un"><b title="${esc(r.n)}">${esc(r.n)}</b>${alt}${dmg}</div>`
    + `<div class="ms">${ms.length ? ms.map(msRow).join('') : ''}</div></div>`;
}

const lastHtml = {air: null, sea: null, land: null};
function render() {
  // 三列结构是固定的（index.html 里就写好了），这里只更新每列的 .bd
  for (const [k] of GRP) {
    const sec = document.querySelector(`.sec[data-g="${k}"]`);
    if (!sec) continue;
    const bd = sec.querySelector('.bd');
    const gv = (snap && snap.groups && snap.groups[k]) || [0, 0];
    const isFold = fold.has(k);
    sec.classList.toggle('fold', isFold);
    sec.querySelector('.hd .ct').innerHTML = `被攻击 <b>${gv[0]}</b> / ${gv[1]}`;
    sec.querySelector('.hd .car').textContent = isFold ? '▸' : '▾';

    let html;
    if (!snap) {
      html = '<div class="empty">等待智能体…</div>';
    } else {
      const qm = matcher();
      const list = (snap.rows || []).filter(r => r.g === k && (!onlyHit || r.hit) && (!qm || qm(r.n)));
      html = sortUnits(list).map(unitRow).join('') || '<div class="empty">无</div>';
    }
    if (html !== lastHtml[k]) {           // 内容没变就不碰 DOM，避免滚动/闪烁
      const top = bd.scrollTop;
      bd.innerHTML = html;
      bd.scrollTop = top;
      lastHtml[k] = html;
    }
  }
  // 标题**必须**以「监控小窗」开头：launcher.py 靠它找自己的窗口并按 z 序置顶。
  // （老 bug：标题一变成「监控 1/0/0」就找不到窗口，launcher 4 秒后自杀 -> 灰屏）
  const g = (snap && snap.groups) || {};
  const nHit = (g.air?.[0] || 0) + (g.sea?.[0] || 0) + (g.land?.[0] || 0);
  document.title = `监控小窗 ${nHit}/${(snap && snap.own) || 0}` + ((snap && snap.ms) ? ` 弹${snap.ms}` : '');
}

// ---------------------------------------------------------------- 交互
$('list').addEventListener('click', e => {
  const h = e.target.closest('.hd');
  if (!h) return;
  const k = h.parentElement.dataset.g;
  fold.has(k) ? fold.delete(k) : fold.add(k);
  localStorage.setItem('mvFold', JSON.stringify([...fold]));
  render();
});
$('onlyHit').onclick = () => {
  onlyHit = !onlyHit; localStorage.setItem('mvOnlyHit', onlyHit ? '1' : '0');
  $('onlyHit').classList.toggle('on', onlyHit); render();
};
$('fixed').onclick = () => {
  fixed = !fixed; localStorage.setItem('mvFixed', fixed ? '1' : '0');
  $('fixed').classList.toggle('on', fixed); render();
};
$('q').addEventListener('input', e => { q = e.target.value; render(); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { if (e.target.id === 'q') { e.target.value = ''; q = ''; render(); } else $('q').focus(); }
  else if (e.key === 'f' || e.key === '/') { e.preventDefault(); $('q').focus(); }
});

$('onlyHit').classList.toggle('on', onlyHit);
$('fixed').classList.toggle('on', fixed);
connect();
render();
