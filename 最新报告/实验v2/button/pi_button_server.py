# -*- coding:utf-8 -*-
r"""
二态按钮页面服务（纯标准库 http.server）
========================================
低空导弹二态按钮的**人类意图输入端**：一个页面、两个按钮（打击模式 / 前进模式），
点一下 = 往命令文件追加一行 JSON；页面下方显示最近 10 条回执与往返时延。

    GET  /            二态按钮页面
    POST /press       {"action":"strike|move","unit":"…"} → 写一行命令，返回 {"seq":…}
    GET  /acks?n=10   最近 n 条回执（监听智能体写的 ack.jsonl）

三条设计约束（对应设计报告 1.3 节）：

* **只封装有限动作**：页面上只有两个按钮，没有自由输入。这样人的指令才是
  "可计数、可去重"的确定序列，才能和战术智能体共用那 500 条/10 秒的配额。
* **重复点击合并**：同一个 (动作, 单元) 在 ``PI_DEDUP_MS`` 内重复点击只写一条命令
  （手抖双击不会变成两次姿态切换）。
* **控制流旁路**：页面与智能体之间只通过一个本地文件通道交互，不走态势后端，
  也不和推演推进线程共用连接（采样端口只读）。

运行::

    python pi_button_server.py               # 默认 127.0.0.1:8764
    python pi_button_server.py --port 8764

环境变量：

    PI_BUTTON_CMD   命令文件，默认 D:/LingYi/exp/button/cmd.jsonl
    PI_BUTTON_LOG   回执文件，默认 D:/LingYi/exp/button/ack.jsonl
    PI_BUTTON_PORT  监听端口，默认 8764（8762/8763 已被 monitor-agent 占用）
    PI_BUTTON_UNIT  页面默认单元名；留空 = 监听智能体按关键字匹配全部地导单元
    PI_BUTTON_DEDUP_MS 重复点击合并窗口，默认 500（0 = 不合并）
"""

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CMD_FILE = os.environ.get('PI_BUTTON_CMD', 'D:/LingYi/exp/button/cmd.jsonl')
ACK_FILE = os.environ.get('PI_BUTTON_LOG', 'D:/LingYi/exp/button/ack.jsonl')
DEFAULT_UNIT = os.environ.get('PI_BUTTON_UNIT', '')
ACTIONS = ('strike', 'move')

# 页面（内联，单文件部署；所有请求都用相对 URL，端口无关）
PAGE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>低空导弹 · 二态按钮</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#10141a; color:#e8edf4;
         font:14px/1.5 "Microsoft YaHei", "Segoe UI", sans-serif; }
  header { padding:14px 20px; border-bottom:1px solid #232b36;
           display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }
  h1 { font-size:16px; margin:0; font-weight:600; letter-spacing:.5px; }
  .hint { color:#7d8da3; font-size:12px; }
  main { padding:20px; max-width:980px; }
  .row { display:flex; gap:14px; align-items:center; flex-wrap:wrap; }
  input[type=text] { background:#18202b; color:#e8edf4; border:1px solid #2b3543;
                     border-radius:6px; padding:8px 10px; width:300px; font-size:13px; }
  .btn { flex:1 1 300px; border:2px solid #2b3543; border-radius:10px;
         background:#18202b; color:#e8edf4; padding:22px 18px; cursor:pointer;
         text-align:left; transition:.12s; }
  .btn:hover { border-color:#3d78d8; background:#1d2734; }
  .btn .t { font-size:20px; font-weight:600; display:block; margin-bottom:6px; }
  .btn .d { font-size:12px; color:#93a3b8; }
  .btn.strike.on { border-color:#d9503f; background:#2a1a18; box-shadow:0 0 0 1px #d9503f inset; }
  .btn.move.on   { border-color:#2f9e6b; background:#14241d; box-shadow:0 0 0 1px #2f9e6b inset; }
  .state { margin:18px 0 6px; font-size:13px; color:#93a3b8; }
  .state b { color:#e8edf4; font-weight:600; }
  table { width:100%; border-collapse:collapse; margin-top:10px; font-size:13px; }
  th, td { text-align:left; padding:7px 8px; border-bottom:1px solid #1d2531; }
  th { color:#7d8da3; font-weight:500; font-size:12px; }
  td.num { font-variant-numeric:tabular-nums; }
  .ok  { color:#54c08a; }
  .bad { color:#e06a58; }
  .ms-good { color:#54c08a; } .ms-mid { color:#e0a63f; } .ms-bad { color:#e06a58; }
  .foot { margin-top:22px; color:#6a7a90; font-size:12px; line-height:1.7; }
  code { background:#18202b; padding:1px 5px; border-radius:4px; color:#b9c8dc; }
</style></head>
<body>
<header>
  <h1>低空导弹 · 二态按钮</h1>
  <span class="hint">人只决定「暴露 / 隐蔽」；停车、开雷达、航路、油门由监听智能体转译</span>
</header>
<main>
  <div class="row" style="margin-bottom:14px">
    <input id="unit" type="text" placeholder="单元名（留空 = 全部地导单元）">
    <span class="hint" id="unitHin"></span>
  </div>

  <div class="row">
    <button class="btn strike" id="btnStrike" onclick="press('strike')">
      <span class="t">打击模式</span>
      <span class="d">停车 · 开雷达 · 等目标进 0.6·Dmax 发弹（暴露高，但能打）</span>
    </button>
    <button class="btn move" id="btnMove" onclick="press('move')">
      <span class="t">前进模式</span>
      <span class="d">正北机动 · 全速 50 km/h · 关雷达 · 不交战（隐蔽，能活）</span>
    </button>
  </div>

  <div class="state" id="state">当前姿态：<b>—</b></div>

  <table>
    <thead><tr>
      <th>seq</th><th>动作</th><th>单元</th><th>往返时延</th>
      <th>仿真时刻</th><th>指令数</th><th>结果 / 备注</th>
    </tr></thead>
    <tbody id="acks"><tr><td colspan="7" style="color:#6a7a90">还没有回执…</td></tr></tbody>
  </table>

  <div class="foot">
    时延 = 按下墙钟 → 监听智能体写完回执，含"排队等一个决策周期"的时间
    （决策间隔 5 推演秒，10 倍速 ≈ 0.5 墙钟秒，所以 <code>&lt;600ms</code> 就是等于无排队）。<br>
    同一个动作 0.5 秒内重复点击只算一次；日志文件在监听智能体那台机器上。
  </div>
</main>
<script>
function fmtMs(v){ return (v===null||v===undefined) ? '—' : Math.round(v) + ' ms'; }
function msClass(v){
  if (v===null||v===undefined) return '';
  return v<=700 ? 'ms-good' : (v<=1500 ? 'ms-mid' : 'ms-bad');
}
async function press(action){
  const unit = document.getElementById('unit').value.trim();
  try {
    const r = await fetch('/press', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({action:action, unit:unit})});
    const j = await r.json();
    if (!j.ok) { alert('下发失败：' + (j.error || '未知错误')); return; }
    refresh();
  } catch (e) { alert('页面服务连不上：' + e); }
}
async function refresh(){
  try {
    const r = await fetch('/acks?n=10', {cache:'no-store'});
    const j = await r.json();
    const rows = j.acks || [];
    render(rows);
  } catch (e) { /* 服务重启中，下次轮询再试 */ }
}
function render(rows){
  const tb = document.getElementById('acks');
  if (!rows.length){
    tb.innerHTML = '<tr><td colspan="7" style="color:#6a7a90">还没有回执…</td></tr>';
    return;
  }
  tb.innerHTML = rows.slice().reverse().map(function(a){
    const act = a.action === 'strike' ? '打击' : (a.action === 'move' ? '前进' : (a.action || '?'));
    const units = (a.unit && a.unit.length) ? a.unit.join('、') : '—';
    const cls = a.ok ? 'ok' : 'bad';
    const res = (a.ok ? '成功' : '失败') + (a.note ? '：' + a.note : '');
    return '<tr>'
      + '<td class="num">' + a.seq + '</td>'
      + '<td>' + act + '</td>'
      + '<td>' + units + '</td>'
      + '<td class="num ' + msClass(a.latency_ms) + '">' + fmtMs(a.latency_ms) + '</td>'
      + '<td class="num">' + (a.sim_t === undefined || a.sim_t === null ? '—' : Math.round(a.sim_t) + ' s') + '</td>'
      + '<td class="num">' + ((a.orders && a.orders.length) || 0) + '</td>'
      + '<td class="' + cls + '">' + res + '</td>'
      + '</tr>';
  }).join('');
  const last = rows[rows.length - 1];
  const mode = last.ok && (last.action === 'strike' || last.action === 'move') ? last.action : null;
  document.getElementById('state').innerHTML = '当前姿态：<b>'
    + (mode === 'strike' ? '打击模式' : (mode === 'move' ? '前进模式' : '—'))
    + '</b>　（最近一次点击 seq ' + last.seq + '）';
  document.getElementById('btnStrike').classList.toggle('on', mode === 'strike');
  document.getElementById('btnMove').classList.toggle('on', mode === 'move');
}
var DEFAULT_UNIT = __UNIT_JSON__;
document.getElementById('unit').value = DEFAULT_UNIT;
document.getElementById('unitHin').textContent = DEFAULT_UNIT
  ? '（页面默认值，可在左侧改）' : '（留空 = 关键字匹配到的全部地导单元）';
refresh();
setInterval(refresh, 1000);
</script>
</body></html>
"""


# ======================================================================
# 命令写入（seq 单调，重启后接着上次的号继续）
# ======================================================================
def _max_seq(path):
    """读命令文件里已出现过的最大 seq（文件很小，一次全读最稳）。"""
    best = 0
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                try:
                    best = max(best, int(rec.get('seq') or 0))
                except (TypeError, ValueError):
                    continue
    except OSError:
        pass
    return best


class CmdWriter(object):
    """往命令文件追加一行；同 (动作, 单元) 在窗口内重复点击合并。"""

    def __init__(self, path, dedup_ms=500):
        self.path = path
        self.dedup_ms = float(dedup_ms or 0)
        self.lock = threading.Lock()
        self.seq = _max_seq(path)
        self._last = (None, None, 0.0, None)     # (action, unit, t_wall, seq)

    def press(self, action, unit):
        """返回 (记录 dict, 是否被合并)。写入失败抛 OSError，由调用方转成 500。"""
        if action not in ACTIONS:
            raise ValueError('action 只支持 %s，收到 %r' % (list(ACTIONS), action))
        with self.lock:
            now = time.time()
            la, lu, lt, lseq = self._last
            if (self.dedup_ms > 0 and action == la and unit == lu
                    and (now - lt) * 1000.0 < self.dedup_ms):
                return {'seq': lseq, 't_wall': lt, 'action': action,
                        'unit': unit}, True
            self.seq += 1
            rec = {'seq': self.seq, 't_wall': round(now, 3),
                   'action': action, 'unit': unit}
            d = os.path.dirname(os.path.abspath(self.path))
            if d and not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec, ensure_ascii=False,
                                   separators=(',', ':')) + '\n')
                f.flush()
            self._last = (action, unit, now, self.seq)
            return rec, False


def read_acks(path, n=10):
    """读回执文件尾部最多 n 条；文件不存在或行坏掉都不抛。"""
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 64 * 1024))
            blob = f.read()
    except OSError:
        return []
    out = []
    for raw in blob.split(b'\n'):
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw.decode('utf-8', 'replace'))
        except ValueError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out[-n:]


# ======================================================================
# HTTP
# ======================================================================
class Handler(BaseHTTPRequestHandler):
    server_version = 'pi-button/1.0'
    writer = None          # main() 里注入

    # ---------------------------------------------------------------- 工具
    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(body)
        except OSError:
            pass

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def log_message(self, fmt, *args):
        print('[%s] %s' % (time.strftime('%H:%M:%S'), fmt % args))

    # ---------------------------------------------------------------- GET
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path in ('/', '/index.html'):
            # 用字符串替换而不是 %-格式化：页面 CSS 里有 'width:100%;' 这类百分号
            self._send(200, PAGE.replace('__UNIT_JSON__',
                                         json.dumps(DEFAULT_UNIT)),
                       'text/html; charset=utf-8')
            return
        if path == '/acks':
            n = 10
            if '?' in self.path:
                for kv in self.path.split('?', 1)[1].split('&'):
                    if kv.startswith('n='):
                        try:
                            n = max(1, min(200, int(kv[2:])))
                        except ValueError:
                            pass
            self._json(200, {'acks': read_acks(ACK_FILE, n), 'ack_file': ACK_FILE})
            return
        if path == '/favicon.ico':
            self._send(204, b'', 'image/x-icon')
            return
        self._json(404, {'ok': False, 'error': 'not found: %s' % path})

    # ---------------------------------------------------------------- POST
    def do_POST(self):
        path = self.path.split('?', 1)[0]
        if path != '/press':
            self._json(404, {'ok': False, 'error': 'not found: %s' % path})
            return
        try:
            length = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b'{}'
        try:
            msg = json.loads(raw.decode('utf-8', 'replace') or '{}')
            if not isinstance(msg, dict):
                raise ValueError('body 必须是 JSON 对象')
            action = str(msg.get('action', '') or '').strip().lower()
            unit = str(msg.get('unit', DEFAULT_UNIT) or '').strip()
            rec, merged = self.writer.press(action, unit)
        except (ValueError, OSError) as e:
            self._json(400, {'ok': False, 'error': str(e)})
            return
        self._json(200, {'ok': True, 'seq': rec.get('seq'), 'action': action,
                         'unit': unit, 't_wall': rec.get('t_wall'),
                         'merged': merged, 'cmd_file': CMD_FILE})


def main():
    global CMD_FILE, ACK_FILE, DEFAULT_UNIT
    ap = argparse.ArgumentParser(description='低空导弹二态按钮页面服务（纯标准库）')
    ap.add_argument('--port', type=int,
                    default=int(os.environ.get('PI_BUTTON_PORT', '8764')))
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--cmd', default=CMD_FILE, help='命令文件')
    ap.add_argument('--ack', default=ACK_FILE, help='回执文件')
    ap.add_argument('--unit', default=DEFAULT_UNIT, help='页面默认单元名')
    ap.add_argument('--dedup-ms', type=int,
                    default=int(os.environ.get('PI_BUTTON_DEDUP_MS', '500')),
                    help='同一动作重复点击的合并窗口（毫秒），0=不合并')
    args = ap.parse_args()

    CMD_FILE, ACK_FILE, DEFAULT_UNIT = args.cmd, args.ack, args.unit
    Handler.writer = CmdWriter(CMD_FILE, args.dedup_ms)
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    srv.daemon_threads = True
    print('二态按钮页面： http://%s:%d/' % (args.host, args.port))
    print('  命令文件 %s（已有序号 %d，新命令从 %d 起）'
          % (CMD_FILE, Handler.writer.seq, Handler.writer.seq + 1))
    print('  回执文件 %s（由监听智能体写入）' % ACK_FILE)
    print('  重复点击合并 %d ms；Ctrl+C 结束' % args.dedup_ms)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
    finally:
        srv.server_close()


if __name__ == '__main__':
    main()
