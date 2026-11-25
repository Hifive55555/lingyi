'use strict';
// 灵弈小窗（跟网页版指挥台是两个项目）：强制置顶叠在全屏的灵弈客户端上，补 Shift+F1 武器分配、F2 油门高度，
// 再加第三个面板「防空值班」（地空导弹 打击⇄机动、可机动雷达 骗弹⇄机动，一个单元一个按钮）。
// 两层：第一层大类按钮（我方 飞机/舰船/潜艇/地面，敌方 空中/水面/潜艇/陆上；飞机再按宿主分 西/中/东/其他，地面按拼音排），第二层所有单位的小方块，同型号挨在一起；
// 敌我各有搜索（"苏35"、"12" = #12、"苏35 3"）。点方块选单机，Shift/Ctrl+点 增减，点型号标签选整型。
// 选目标后光标自动进发数框，敲数字回车就打，Tab 换下一种武器；飞机够不着也能下，智能体退任务飞过去打（虚线方块 = 追打中）。
// 热键由 launcher.py 全局抢（同一个键再按一次收起），这里轮询 /key 切面板
const $ = id => document.getElementById(id);
let snap = null, units = new Map(), contacts = new Map(), CAT = {weapons: {}};
let sel = new Set(), tab = localStorage.getItem('ovTab') || 'weapon', tgt = null, qty = new Map();
let mCat = localStorage.getItem('ovMCat') || 'a', eCat = localStorage.getItem('ovECat') || 'sur', airOnly = localStorage.getItem('ovAirOnly') === '1';
let mReg = localStorage.getItem('ovMReg') || '', noteSeq = 0;
let mGroups = new Map(), eGroups = new Map();
const AGENT_HOST = new URLSearchParams(location.search).get('agent') || '127.0.0.1:8760';

const THR_ORDER = ['Loiter', 'Cruise', 'Full', 'Flank'];
const THR_CN = {Loiter: '低速', Cruise: '巡航', Full: '全速', Flank: '加力'};
const MCATS = [['a', '飞机'], ['s', '舰船'], ['u', '潜艇'], ['f', '地面']];
const ECATS = [['air', '空中'], ['sur', '水面'], ['sub', '潜艇'], ['land', '陆上']];
// 飞机按宿主（当前所在 / 归属基地）分片，没提到的都是“其他”
const REGIONS = {
  '蓝方': [['西', /福特|邦克山|阿利伯克/], ['中', /奥尔良|卡皮凯|阿斯图/], ['东', /CS机场|IZUMO|直升驱逐舰/]],
  '红方': [['西', /戴高乐|NK机场/], ['中', /BL机场|CT机场/], ['东', /BT机场|TF机场/]],
};
const REG_NAMES = ['西', '中', '东', '其他'];
const regOf = u => { for (const [k, re] of REGIONS[(snap && snap.side) || '蓝方'] || []) if (re.test(u.host || '')) return k; return '其他'; };
// 名字里第一个汉字的拼音首字母（没有汉字用第一个字母）：汉字按这组边界字查 26 字母表（i u v 没有汉字开头）
const PY = new Intl.Collator('zh-CN');
const PY_B = '阿八嚓哒妸发旮哈讥咔垃痳拏噢妑七呥仨它屲夕丫帀', PY_L = 'ABCDEFGHJKLMNOPQRSTWXYZ';
const hanzi = n => { const i = (n || '').search(/[\u4e00-\u9fff]/); return i < 0 ? (n || '') : n.slice(i); };
function pyLetter(n) {
  const h = hanzi(n)[0] || '';
  if (!/[\u4e00-\u9fff]/.test(h)) return (/[A-Za-z]/.exec(n || '') || ['#'])[0].toUpperCase();
  let i = PY_L.length - 1;
  while (i > 0 && PY.compare(h, PY_B[i]) < 0) i--;
  return PY_L[i];
}
const short = n => (n || '').replace(/型|“|”|"|\s+/g, '').replace(/战斗机|轰炸机|运输机|无人机|加油机|无人加油机|舰载预警机|电子战飞机|反潜直升机|级坦克登陆舰|级护卫舰|级驱逐舰|级巡洋舰|级航空母舰|号护卫舰/g, '');
const typeOf = n => short(n).replace(/#\d+$/, '') || '未识别';
const numOf = n => { const m = /#(\d+)\s*$/.exec(n || ''); return m ? m[1] : ''; };
const wname = d => { const w = CAT.weapons[d]; return w ? w.name : `武器${d}`; };
const wshort = d => wname(d).split(/[\[\(（,，]/)[0].slice(0, 18);
const esc = t => String(t).replace(/[&<>"]/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[ch]));
const km = (a, b) => { const dl = (a[0] - b[0]) * 111.32, dn = (a[1] - b[1]) * 111.32 * Math.cos((a[0] + b[0]) / 2 * Math.PI / 180); return Math.hypot(dl, dn); };
const fmtT = t => { t = Math.max(0, Math.round(t)); return `${Math.floor(t / 3600)}:${String(Math.floor(t % 3600 / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`; };
const isGun = r => r[6] === 2004;
const fuelPct = u => u.fmax ? Math.max(0, Math.min(1, u.fuel / u.fmax)) : 0;
const ammo = u => (u.w || []).filter(r => !isGun(r)).reduce((a, r) => a + r[1], 0);
const DOM_I = {air: 2, sur: 3, land: 4, sub: 5};
const DOM_CN = {air: '对空', sur: '对海', land: '对陆', sub: '对潜'};
const domOf = c => (c.ty === 0 || c.ty === 1) ? 'air' : (c.ty === 2 || c.ty === 4) ? 'sur' : c.ty === 3 ? 'sub' : 'land';
const selUnits = () => [...sel].map(id => units.get(id)).filter(Boolean);
const api = p => fetch(p).catch(() => {});

function say(text, cls = '') {
  const el = $('msg'), d = document.createElement('div');
  d.className = cls; d.textContent = `${snap ? fmtT(snap.t) : ''} ${text}`;
  el.prepend(d); while (el.children.length > 3) el.lastChild.remove();
}

// ---------------------------------------------------------------- 搜索：空格分词都要中；纯数字 = 编号（12 只中 #12），别的按名字包含（忽略 - 空格 型）
const norm = s => (s || '').toLowerCase().replace(/[\s\-_·.型“”"]/g, '');
function matcher(q) {
  const toks = q.trim().split(/\s+/).filter(Boolean).map(t => t.replace(/^#/, ''));
  if (!toks.length) return null;
  return n => { const nn = norm(n), num = numOf(n); return toks.every(t => /^\d+$/.test(t) ? num === t : nn.includes(norm(t))); };
}
// 行首已经写了型号，方块里只写编号（没编号才写名字）
const numTile = n => numOf(n) ? '#' + numOf(n) : tileName(n);
function tileName(n) {
  const s = short(n), m = /^(.*?)(#\d+)$/.exec(s);
  let p = m ? m[1] : s;
  if (p.length > 9) p = p.slice(0, 8) + '…';
  return esc(p) + (m ? m[2] : '');
}

// ---------------------------------------------------------------- 通信（带 cid，5 秒没回执重发，智能体那边去重）
const SESSION = Math.random().toString(36).slice(2, 8);
let ws = null, reqN = 1, reqs = new Map(), lastMsg = Date.now(), snapAt = 0;
const live = () => Date.now() - snapAt < 8000;
function connect() {
  ws = new WebSocket(`ws://${AGENT_HOST}/ws`);
  ws.onopen = () => { lastMsg = Date.now(); for (const r of reqs.values()) ws.send(r.msg); };
  ws.onclose = () => { $('conn').textContent = '● 无对局'; $('conn').className = 'bad'; setTimeout(connect, 1500); };
  ws.onmessage = e => {
    lastMsg = Date.now();
    const d = JSON.parse(e.data);
    if (d.type === 'snap') onSnap(d);
    else if (d.type === 'ack') { const r = reqs.get(d.req); if (!r) return; reqs.delete(d.req); say(`${r.label} → ${d.msg}`, d.ok ? 'ok' : 'bad'); }
  };
}
setInterval(() => {
  if (ws && ws.readyState === 1 && Date.now() - lastMsg > 8000) { ws.close(); return; }
  const now = Date.now();
  for (const [k, r] of reqs) {
    if (now - r.t0 > 40000) { reqs.delete(k); say(`${r.label} → 40 秒没回执，去客户端里看看下没下成功`, 'bad'); }
    else if (now - r.ts > 5000 && ws && ws.readyState === 1) { ws.send(r.msg); r.ts = now; }
  }
  if (!live()) { $('conn').textContent = '● 无对局'; $('conn').className = 'bad'; }
}, 1000);
function send(op, ids, extra, label) {
  if (!live()) { say('现在没有对局，指令没发', 'bad'); return; }
  if (!ids.length) { say('没有能下这条指令的单元', 'bad'); return; }
  const req = reqN++, msg = JSON.stringify({type: 'cmd', req, cid: `${SESSION}-${req}`, op, ids, ...extra});
  reqs.set(req, {label, msg, t0: Date.now(), ts: Date.now()});
  if (ws && ws.readyState === 1) ws.send(msg);
}
fetch('/catalog').then(r => r.json()).then(c => { if (c && c.weapons) CAT = c; }).catch(() => {});

function onSnap(d) {
  if (snap && d.t + 30 < snap.t) { sel.clear(); tgt = null; }
  snapAt = Date.now(); snap = d;
  const notes = d.notes || [];
  if (notes.length && notes[notes.length - 1][0] < noteSeq) noteSeq = 0;        // 智能体重启，序号从头来
  for (const [n, text, ok] of notes) if (n > noteSeq) { noteSeq = n; say(text, ok ? 'ok' : 'bad'); }
  units = new Map(d.units.map(u => [u.id, u]));
  contacts = new Map(d.contacts.filter(c => !c.ms).map(c => [c.id, c]));
  for (const id of [...sel]) if (!units.has(id)) sel.delete(id);
  $('clock').textContent = fmtT(d.t);
  $('conn').textContent = d.started ? '●' : '● 战前'; $('conn').className = 'ok';
  const me = d.side || '蓝方';
  $('brand').textContent = me; $('brand').style.color = me === '红方' ? '#ff6070' : '#3fd0e6';
  render();
}

// ---------------------------------------------------------------- 我方：大类按钮 + 小方块
function unitTip(u) {
  const w = (u.w || []).filter(r => !isGun(r)).map(r => `${wshort(r[0])}×${r[1]}`).join('，');
  const st = u.k === 'a' ? (u.air ? `在空 ${Math.round(u.alt)}米 ${Math.round(u.spd)}节 油${Math.round(fuelPct(u) * 100)}%` : `停放 ${u.rdy || ''}`) : `${Math.round(u.spd)}节`;
  return `${u.n}${u.host ? `（${u.host}）` : ''}\n${st}${u.dmg > 0 ? ` 损${Math.round(u.dmg)}%` : ''}${u.ch ? `\n追打 ${u.ch}` : ''}\n${w || '没有弹'}`;
}
function unitTile(u) {
  let c = 't';
  if (sel.has(u.id)) c += ' on';
  if (u.k === 'a') c += u.air ? (fuelPct(u) > .5 ? ' f1' : fuelPct(u) > .25 ? ' f2' : ' f3') : ' park';
  if (u.dmg >= 50) c += ' hurt';
  if (u.ch) c += ' ch';
  const a = ammo(u);
  return `<span class="${c}" data-id="${esc(u.id)}" title="${esc(unitTip(u))}">${numTile(u.n)}${a ? `<em>${a}</em>` : ''}</span>`;
}
function renderMine() {
  const q = matcher($('mQ').value), all = [...units.values()];
  const hit = q ? (u => q(u.n)) : (() => true);
  let cats = '';
  for (const [k, cn] of MCATS) {
    const n = all.filter(u => u.k === k && hit(u)).length;
    if (!n && k !== mCat) continue;
    cats += `<button class="cat${!q && k === mCat ? ' on' : ''}" data-mc="${k}">${cn}<i>${n}</i></button>`;
  }
  $('mCats').innerHTML = cats;
  const base = all.filter(q ? hit : (u => u.k === mCat && !(mCat === 'a' && airOnly && !u.air)));
  const showRegs = !q && mCat === 'a';
  $('mRegs').innerHTML = !showRegs ? '' : `<button class="cat${mReg ? '' : ' on'}" data-reg="">全部<i>${base.length}</i></button>` +
    REG_NAMES.map(k => `<button class="cat${mReg === k ? ' on' : ''}" data-reg="${k}">${k}<i>${base.filter(u => regOf(u) === k).length}</i></button>`).join('') +
    `<span class="grow"></span><button class="cat${airOnly ? ' on' : ''}" data-air="1">只看在空</button>`;
  const list = showRegs && mReg ? base.filter(u => regOf(u) === mReg) : base;
  mGroups = new Map();
  for (const u of list) { const n = typeOf(u.n); if (!mGroups.has(n)) mGroups.set(n, []); mGroups.get(n).push(u); }
  const gs = [...mGroups.entries()];
  for (const [, l] of gs) l.sort((a, b) => (b.air - a.air) || (+numOf(a.n) - +numOf(b.n)));
  const abc = !q && mCat === 'f';         // 地面单元：从上到下按第一个汉字的拼音首字母
  if (abc) { for (const [, l] of gs) l.sort((a, b) => +numOf(a.n) - +numOf(b.n)); gs.sort((a, b) => pyLetter(a[0]).localeCompare(pyLetter(b[0])) || PY.compare(hanzi(a[0]), hanzi(b[0]))); }
  else gs.sort((a, b) => (b[1].some(u => u.air) - a[1].some(u => u.air)) || b[1].length - a[1].length || a[0].localeCompare(b[0]));
  let html = '';
  for (const [n, l] of gs) {
    const on = l.every(u => sel.has(u.id));
    html += `<div class="gr"><span class="g${on ? ' on' : ''}" data-g="${esc(n)}" title="${esc(n)}">${abc ? `<u>${pyLetter(n)}</u>` : ''}${esc(n)}<i>${l.length}</i></span><span class="ts">${l.map(unitTile).join('')}</span></div>`;
  }
  keepScroll($('mine'), html || `<div class="empty">${units.size ? '无' : '等待对局'}</div>`);
}
function keepScroll(el, html) { const top = el.scrollTop; el.innerHTML = html; el.scrollTop = top; }
$('mCats').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  mCat = b.dataset.mc; localStorage.setItem('ovMCat', mCat); $('mQ').value = ''; $('mine').scrollTop = 0;
  renderMine();
});
$('mRegs').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.dataset.air) { airOnly = !airOnly; localStorage.setItem('ovAirOnly', airOnly ? '1' : ''); }
  else { mReg = b.dataset.reg; localStorage.setItem('ovMReg', mReg); $('mine').scrollTop = 0; }
  renderMine();
});
$('mine').addEventListener('click', e => {
  const multi = e.shiftKey || e.ctrlKey;
  const t = e.target.closest('.t');
  if (t) { const id = t.dataset.id; if (multi) sel.has(id) ? sel.delete(id) : sel.add(id); else sel = sel.size === 1 && sel.has(id) ? new Set() : new Set([id]); changed(); return; }
  const g = e.target.closest('.g'); if (!g) return;
  const ids = (mGroups.get(g.dataset.g) || []).map(u => u.id), all = ids.every(id => sel.has(id));
  if (multi) ids.forEach(id => all ? sel.delete(id) : sel.add(id)); else sel = all && sel.size === ids.length ? new Set() : new Set(ids);
  changed();
});
function changed() { qty = new Map(); render(true); focusQty(); }

function renderSel() {
  const us = selUnits();
  if (!us.length) { $('selbar').innerHTML = '<span class="sub">未选</span>'; return; }
  const chasing = us.filter(u => u.ch);
  const tc = new Map(); for (const u of us) tc.set(typeOf(u.n), (tc.get(typeOf(u.n)) || 0) + 1);
  $('selbar').innerHTML = `<b>${us.length}</b>` + [...tc].map(([n, c]) => `<span class="chip">${esc(n)}×${c}</span>`).join('') + '<span class="grow"></span>' + (chasing.length ? `<button id="selStop">停止追打 ${chasing.length}</button>` : '') + '<button id="selClr">清空</button>';
  $('selClr').onclick = () => { sel.clear(); tgt = null; changed(); };
  if (chasing.length) $('selStop').onclick = () => send('unchase', chasing.map(u => u.id), {}, `停止追打 ×${chasing.length}`);
}

// ---------------------------------------------------------------- 敌方：大类按钮 + 小方块（按离选中单元最近的距离排，够得着的绿边）
function shooters() { return selUnits().filter(u => u.lat != null && (u.w || []).length); }
function nearest(c, sh) {
  let best = null;
  for (const u of sh) { const d = km([u.lat, u.lon], [c.lat, c.lon]) / 1.852; if (best == null || d < best) best = d; }
  return best;
}
function reach(c, sh) {
  const dom = domOf(c);
  return sh.some(u => (u.w || []).some(r => !isGun(r) && (r[DOM_I[dom]] || 0) >= km([u.lat, u.lon], [c.lat, c.lon]) / 1.852));
}
function renderEnemy() {
  const q = matcher($('eQ').value), all = [...contacts.values()].filter(c => c.lat != null);
  const hit = q ? (c => q(c.n || c.id)) : (() => true);
  let cats = '';
  for (const [k, cn] of ECATS) {
    const n = all.filter(c => domOf(c) === k && hit(c)).length;
    if (!n && k !== eCat) continue;
    cats += `<button class="cat${!q && k === eCat ? ' on' : ''}" data-ec="${k}">${cn}<i>${n}</i></button>`;
  }
  $('eCats').innerHTML = cats;
  const sh = shooters(), list = all.filter(q ? hit : (c => domOf(c) === eCat));
  for (const c of list) { c._d = sh.length ? nearest(c, sh) : null; c._r = sh.length && reach(c, sh); }
  eGroups = new Map();
  for (const c of list) { const n = typeOf(c.n); if (!eGroups.has(n)) eGroups.set(n, []); eGroups.get(n).push(c); }
  const D = c => c._d ?? 1e9;
  const gs = [...eGroups.entries()];
  for (const [, l] of gs) l.sort((a, b) => D(a) - D(b) || (+numOf(a.n) - +numOf(b.n)));
  gs.sort((a, b) => D(a[1][0]) - D(b[1][0]) || b[1].length - a[1].length || a[0].localeCompare(b[0]));
  let html = '';
  for (const [n, l] of gs) {
    html += `<div class="gr"><span class="g" data-eg="${esc(n)}" title="${esc(n)}">${esc(n)}<i>${l.length}</i></span><span class="ts">` + l.map(c =>
      `<span class="t${c.id === tgt ? ' tg' : ''}${c._r ? ' rch' : ''}" data-t="${esc(c.id)}" title="${esc(c.n || c.id)}${c._d != null ? `\n最近 ${Math.round(c._d)} 海里` : ''}${c._r ? '\n有弹够得着' : ''}">` +
      `${numTile(c.n || '未识别')}${c._d != null ? `<em>${Math.round(c._d)}</em>` : ''}</span>`).join('') + '</span></div>';
  }
  keepScroll($('enemy'), html || `<div class="empty">${all.length ? '无' : '无目标'}</div>`);
}
$('eCats').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  eCat = b.dataset.ec; localStorage.setItem('ovECat', eCat); $('eQ').value = ''; $('enemy').scrollTop = 0; renderEnemy();
});
$('enemy').addEventListener('click', e => {
  const t = e.target.closest('.t'), g = e.target.closest('.g');
  const id = t ? t.dataset.t : g ? ((eGroups.get(g.dataset.eg) || [])[0] || {}).id : null;
  if (!id) return;
  tgt = tgt === id ? null : id; qty = new Map(); render(true); focusQty();
});

// ---------------------------------------------------------------- 武器分配（Shift+F1）
function weaponList(c) {
  const dom = domOf(c), agg = new Map();
  for (const u of shooters()) {
    const dnm = km([u.lat, u.lon], [c.lat, c.lon]) / 1.852;
    for (const r of u.w || []) {
      const rng = r[DOM_I[dom]] || 0;
      if (!(rng > 0) || isGun(r)) continue;
      const a = agg.get(r[0]) || {d: r[0], rng, total: 0, has: [], inr: [], fly: [], load: new Map(), min: 1e9};
      a.total += r[1]; a.has.push(u.id); a.load.set(u.id, r[1]); a.rng = Math.max(a.rng, rng); a.min = Math.min(a.min, dnm);
      if (dnm <= rng) a.inr.push(u.id); else if (u.k === 'a') a.fly.push(u.id);     // 飞机够不着：智能体带它飞过去打
      agg.set(r[0], a);
    }
  }
  return [...agg.values()].sort((a, b) => ((b.inr.length > 0) - (a.inr.length > 0)) || b.rng - a.rng);
}
function renderWeapon() {
  const c = contacts.get(tgt);
  if (!c) { tgt = null; return ''; }
  const list = weaponList(c), dom = domOf(c);
  let html = `<div class="pt"><b>→ ${esc(short(c.n || c.id))}</b><span class="sub">${DOM_CN[dom]}</span><span class="grow"></span><button id="wBack">×</button></div>`;
  if (!sel.size) return html + '<div class="bad">先选我方</div>';
  if (!list.length) return html + `<div class="bad">没有${DOM_CN[dom]}武器</div>`;
  html += '<table><colgroup><col><col style="width:34px"><col style="width:66px"><col style="width:40px"><col style="width:80px"></colgroup>' +
    '<tr><th>武器</th><th>余</th><th>射程/距</th><th>可发</th><th>每架</th></tr>';
  for (const a of list) {
    const ok = a.inr.length > 0, n = qty.get(a.d) || 0;
    html += `<tr class="${ok ? '' : a.fly.length ? 'far' : 'cant'}"><td title="${esc(wname(a.d))}">${esc(wshort(a.d))}</td><td>${a.total}</td>` +
      `<td>${Math.round(a.rng)}/${Math.round(a.min)}nm</td><td class="${ok ? 'ok' : a.fly.length ? '' : 'bad'}" title="${a.fly.length ? `${a.fly.length} 架够不着，下了就飞过去打` : ''}">${a.inr.length}/${a.has.length}${a.fly.length ? '飞' : ''}</td>` +
      `<td><span class="q"><button tabindex="-1" data-q="${a.d}" data-v="-1">−</button><input class="qi" type="tel" maxlength="3" data-qi="${a.d}" value="${n || ''}" placeholder="0"><button tabindex="-1" data-q="${a.d}" data-v="1">＋</button></span></td></tr>`;
  }
  const sum = list.reduce((s, a) => s + goIds(a).reduce((t, id) => t + Math.min(qty.get(a.d) || 0, a.load.get(id)), 0), 0);
  return html + `</table><div class="pt"><span class="sub">${sum ? `共 ${sum} 发` : '敲数字，⏎ 发射，Tab 下一种'}</span><span class="grow"></span><button id="wFire" class="fire" tabindex="-1">发射 ⏎</button></div>`;
}
// 在射程内的 + 够不着的飞机都下；一架都下不了（船、车够不着）才全下，让引擎回话
function goIds(a) { const go = [...a.inr, ...a.fly]; return go.length ? go : a.has; }
function fire() {
  const c = contacts.get(tgt); if (!c) return;
  const pick = weaponList(c).filter(a => (qty.get(a.d) || 0) > 0);
  if (!pick.length) { say('发数都是 0', 'bad'); return; }
  for (const a of pick) {
    const ids = goIds(a), n = qty.get(a.d);
    send('attack', ids, {target: tgt, weapons: [[a.d, n]]}, `打 ${short(c.n || '')} ${wshort(a.d)}×${n}×${ids.length}${a.fly.length ? `（${a.fly.length} 架飞过去）` : a.inr.length ? '' : '（都够不着）'}`);
  }
  qty = new Map(); tgt = null; render(true);
}
$('wp').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.id === 'wBack') { tgt = null; render(true); }
  else if (b.id === 'wFire') fire();
  else if (b.dataset.q) { const d = +b.dataset.q; qty.set(d, Math.max(0, (qty.get(d) || 0) + (+b.dataset.v))); renderWp(); }
});
$('wp').addEventListener('input', e => {
  if (!e.target.dataset.qi) return;
  const v = e.target.value.replace(/\D/g, '');
  qty.set(+e.target.dataset.qi, +v || 0);
  renderWp();
});
$('wp').addEventListener('focusin', e => { if (e.target.dataset.qi && !qiKeep) e.target.select(); });
let qiKeep = false;
// 快照随时来、整块重画：正在敲的框要接着敲，光标位置不能丢
function renderWp() {
  const a = document.activeElement, d = a && a.dataset ? a.dataset.qi : null, pos = d ? a.selectionStart : 0, end = d ? a.selectionEnd : 0;
  keepScroll($('wp'), tab === 'weapon' && tgt ? renderWeapon() : '');
  const el = d && $('wp').querySelector(`[data-qi="${d}"]`);
  if (el) { qiKeep = true; el.focus(); el.setSelectionRange(pos, end); qiKeep = false; }
}
function focusQty() {
  if (tab !== 'weapon' || !tgt) return;
  const el = $('wp').querySelector('tr:not(.cant) .qi') || $('wp').querySelector('.qi');
  if (el) { el.focus(); el.select(); }
}

// ---------------------------------------------------------------- 油门高度（F2）
function renderThrAlt() {
  const us = selUnits(), air = us.filter(u => u.k === 'a');
  if (!us.length) return '<div class="sub">先选我方</div>';
  const one = us.length === 1 ? us[0] : null;
  let html = one ? `<div class="now">${esc(short(one.n))}：${one.k === 'a' ? Math.round(one.alt) + ' 米　' : ''}${Math.round(one.spd)} 节</div>` : '';
  html += '<div class="hd">油门</div><div class="grid">' + THR_ORDER.map(t => `<button data-thr="${t}">${THR_CN[t]}</button>`).join('') + '</div>';
  if (!air.length) return html;
  html += '<div class="hd">高度</div><div class="grid">' +
    [300, 1000, 3000, 5000, 8000, 10000, 11000].map(v => `<button data-alt="${v}">${v}</button>`).join('') + '<button data-alt="+">+1000</button></div>' +
    '<div class="grid"><button data-alt="-">−1000</button><input id="altIn" type="number" min="30" step="100" placeholder="米" style="grid-column: span 2"><button id="altGo">设定</button></div>';
  return html;
}
function setAlt(v) {
  const air = selUnits().filter(u => u.k === 'a');
  if (!air.length) { say('选中的没有飞机', 'bad'); return; }
  if (v === '+' || v === '-') { for (const u of air) send('alt', [u.id], {alt: Math.max(300, Math.round((u.alt + (v === '+' ? 1000 : -1000)) / 500) * 500)}, `${short(u.n)} 高度 ${v}1000`); return; }
  send('alt', air.map(u => u.id), {alt: +v}, `高度 ${v} 米 ×${air.length}`);
}
$('thr').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.id === 'altGo') { const v = +$('altIn').value; if (v > 0) setAlt(v); return; }
  if (b.dataset.thr) { const t = b.dataset.thr; send('throttle', [...sel].filter(id => units.has(id)), {throttle: t}, `油门 ${THR_CN[t]} ×${sel.size}`); return; }
  if (b.dataset.alt) setAlt(b.dataset.alt);
});
$('thr').addEventListener('keydown', e => { if (e.target.id === 'altIn' && e.key === 'Enter') { e.stopPropagation(); $('altGo').click(); } });

// ---------------------------------------------------------------- 防空值班（地空导弹 / 雷达）
// 一个单元一个按钮：地空导弹「打击模式 ⇄ 机动模式」，可机动雷达「骗弹模式 ⇄ 机动模式」。
// 智能体那边（SamBattalionDefense）负责按模式下发停车/开雷达/全速机动，并在被弹瞄准时自动切回机动。
const SAM_MODE_CN = {strike: '打击模式', bait: '骗弹模式', maneuver: '机动模式'};
const SAM_DIR_CN = {N: '正北', E: '正东', S: '正南', W: '正西'};
const samRows = () => (snap && snap.sam) || [];
// 点一下切到对面那个模式（地空导弹：打击 ⇄ 机动；雷达：骗弹 ⇄ 机动）
const samNext = (role, mode) => role === 'radar'
  ? (mode === 'bait' ? 'maneuver' : 'bait')
  : (mode === 'strike' ? 'maneuver' : 'strike');
function renderSam() {
  const rows = samRows();
  const sam = rows.filter(r => r.role === 'sam'), rad = rows.filter(r => r.role === 'radar');
  const row = r => `<div class="samrow" data-id="${esc(r.id)}" data-role="${r.role}">
      <span class="sn" title="${esc(r.n)}">${esc(short(r.n))}</span>
      <span class="sy">${SAM_DIR_CN[r.dir] || ''}</span>
      <button class="mode ${esc(r.mode)}" data-go="${samNext(r.role, r.mode)}">${SAM_MODE_CN[r.mode] || esc(r.mode)}</button>
    </div>`;
  const html = `<div class="samh">地空导弹营系统<i>${sam.length} 个</i></div>` +
    (sam.length ? sam.map(row).join('') : '<div class="empty">没有识别到地空导弹单元</div>') +
    `<div class="samh">雷达系统<i>${rad.length} 个</i></div>` +
    (rad.length ? rad.map(row).join('') : '<div class="empty">没有识别到可机动雷达</div>') +
    '<div class="hd" style="margin-top:6px">地空导弹：打击模式=停车+开雷达+自由开火；机动模式=关雷达+全速离开。' +
    '雷达：骗弹模式=停车+开雷达；机动模式=关雷达+全速向南。被弹瞄准时会自动切回机动模式。</div>';
  keepScroll($('samPanel'), html);
}
$('samPanel').addEventListener('click', e => {
  const b = e.target.closest('button[data-go]'); if (!b) return;
  const r = b.closest('.samrow'); if (!r) return;
  const u = units.get(r.dataset.id);
  send('sam_mode', [r.dataset.id], {mode: b.dataset.go},
    `${short((u && u.n) || r.dataset.id)} → ${SAM_MODE_CN[b.dataset.go] || b.dataset.go}`);
});

// ---------------------------------------------------------------- 面板
function render(force) {
  renderSel(); renderMine();
  document.querySelectorAll('.top .tab').forEach(b => b.classList.toggle('on', b.dataset.t === tab));
  document.body.className = tab === 'thralt' ? 'thr' : tab === 'sam' ? 'sam' : 'weapon';
  if (tab === 'weapon') { renderEnemy(); renderWp(); }
  else if (tab === 'sam') renderSam();
  else if (force || document.activeElement.id !== 'altIn') $('thr').innerHTML = renderThrAlt();     // 正在输高度，不打断
}
function setTab(t) { tab = t; localStorage.setItem('ovTab', t); api('/tab?t=' + t); render(true); }
document.querySelectorAll('.top .tab').forEach(b => b.onclick = () => setTab(b.dataset.t));
$('mQ').addEventListener('input', renderMine);
$('eQ').addEventListener('input', renderEnemy);
document.addEventListener('keydown', e => {
  if (e.target.dataset && e.target.dataset.qi) {
    if (e.key === 'Enter') fire();
    else if (e.key === 'Escape') { tgt = null; render(true); }
    return;
  }
  if (e.target.tagName === 'INPUT') {
    if (e.key === 'Escape') { if (e.target.value) { e.target.value = ''; e.target.dispatchEvent(new Event('input')); } else e.target.blur(); }
    else if (e.key === 'Enter' && e.target.id === 'eQ') { const f = $('enemy').querySelector('.t'); if (f) f.click(); }
    else if (e.key === 'Enter' && e.target.id === 'mQ') { const ids = [...$('mine').querySelectorAll('.t')].map(t => t.dataset.id); if (ids.length) { sel = new Set(ids); changed(); } }
    return;
  }
  if (e.key === 'Escape') { if (tgt) { tgt = null; render(true); } else api('/hide'); }
  else if (e.key === 'Enter' && tab === 'weapon' && tgt) fire();
  else if (e.key === '1') setTab('weapon');
  else if (e.key === '2') setTab('thralt');
  else if (e.key === '3') setTab('sam');
  else if (e.key === 'f' || e.key === '/') { e.preventDefault(); $('mQ').focus(); }
  else if (e.key === 'g') { e.preventDefault(); $('eQ').focus(); }
});

// ---------------------------------------------------------------- 全局热键（launcher.py 抢到后记下，这里轮询）
let keyN = null;
async function pollKey() {
  try {
    const d = await (await fetch('/key')).json();
    if (d.keys) { $('kw').textContent = d.keys.weapon; $('kt').textContent = d.keys.thralt; $('ks').textContent = d.keys.sam || 'Alt+E'; }
    if (keyN != null && d.n !== keyN && (d.k === 'weapon' || d.k === 'thralt' || d.k === 'sam')) { window.focus(); setTab(d.k); }
    keyN = d.n;
  } catch (e) {}
}
setInterval(pollKey, 250); pollKey(); api('/tab?t=' + tab);
connect(); render(true);
