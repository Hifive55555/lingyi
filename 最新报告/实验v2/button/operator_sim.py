# -*- coding:utf-8 -*-
r"""
脚本化操作员（离线：不需要平台、不需要 Windows）
================================================
低空导弹二态按钮的**时延实验驱动器**：按 ``schedule.json`` 里的仿真时刻写按钮命令，
并记下每次"按下"的墙钟时间，最后把监听智能体的回执与按下时刻相减，得到往返时延
的 P50 / P95。人机时延实验因此可以脱离人工点击、自动重复 N 次。

两个时刻的锚定
--------------
页面服务只能写"现在的墙钟时间"，而 schedule 是"推演时间"。二者的换算靠一条
回执：``ack`` 里带 ``sim_t``（那一步的推演时刻）与 ``t_wall_ack``（写回执的墙钟），
于是::

    wall(t_sim) = t_wall_ack + (t_sim - sim_t) / speed

``speed`` 是推演的倍速（10 倍速 = 每墙钟秒 10 推演秒），与被测环境一致才准。
所以本脚本先**等第一条回执**（也就是对局真的跑起来、监听智能体已经开始工作），
再按上式排程。若实验无法等（比如对局已在中途），用 ``--anchor-sim`` 手工给锚点。

用法
----
::

    python operator_sim.py                                  # 读 schedule.json，10 倍速
    python operator_sim.py --speed 10 --schedule case01.json
    python operator_sim.py --dry-run                        # 只打印计划，不写命令
    python operator_sim.py --anchor-sim 600                 # 不等回执，按"现在=600 s"起算
    python operator_sim.py --unit "捷羚地空导弹排#1"         # 指定单元（默认=全部地导单元）

schedule.json::

    [{"t_sim": 1200, "action": "move"},
     {"t_sim": 1500, "action": "strike", "unit": "捷羚地空导弹排#1"}]

输出
----
* 命令写进 ``PI_BUTTON_CMD``（默认 D:/LingYi/exp/button/cmd.jsonl），序号接着
  已有文件里的最大值继续，不会和页面服务的序号撞车；
* 按下记录写进 ``presses.jsonl``（与命令文件同目录，可用 ``--press-log`` 改）；
* 终端打印每次点击的时延与 P50/P95/最大，退出码恒为 0（离线工具，不该因为
  等不到回执而"失败"，缺的条数会在表里列出来）。
"""

import argparse
import json
import math
import os
import sys
import time

DEFAULT_CMD = os.environ.get('PI_BUTTON_CMD', 'D:/LingYi/exp/button/cmd.jsonl')
DEFAULT_ACK = os.environ.get('PI_BUTTON_LOG', 'D:/LingYi/exp/button/ack.jsonl')
ACTIONS = ('strike', 'move')


# ======================================================================
# 小工具
# ======================================================================
def _pct(values, p):
    """线性插值分位数（p 取 0~100）；空列表返回 None。"""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = int(math.floor(k))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def _fmt(value):
    return '-' if value is None else '%.0f' % value


def _ensure_dir(path):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)


def max_seq(path):
    """命令文件里已出现过的最大 seq（页面服务也用同一规则，二者不会撞号）。"""
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
                if isinstance(rec, dict):
                    try:
                        best = max(best, int(rec.get('seq') or 0))
                    except (TypeError, ValueError):
                        pass
    except OSError:
        pass
    return best


class JsonlTail(object):
    """按字节偏移读 JSONL 增量，只返回完整行（后半个周期写的行留到下次）。"""

    def __init__(self, path):
        self.path = path
        self.offset = 0

    def read(self):
        try:
            size = os.path.getsize(self.path)
        except OSError:
            return []
        if size < self.offset:          # 文件被截断/轮转
            self.offset = 0
        if size == self.offset:
            return []
        try:
            with open(self.path, 'rb') as f:
                f.seek(self.offset)
                blob = f.read()
        except OSError:
            return []
        cut = blob.rfind(b'\n')
        if cut < 0:
            return []
        self.offset += cut + 1
        out = []
        for raw in blob[:cut].split(b'\n'):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw.decode('utf-8', 'replace'))
            except ValueError:
                continue
            if isinstance(rec, dict):
                out.append(rec)
        return out


# ======================================================================
# 计划与写命令
# ======================================================================
def load_schedule(path, default_unit):
    """读 schedule.json → [(t_sim, action, unit)]，按 t_sim 升序。"""
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError('schedule.json 必须是数组，例如 '
                         '[{"t_sim":1200,"action":"move"}]')
    plan = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            print('  跳过第 %d 条（不是对象）：%r' % (i + 1, item))
            continue
        try:
            t_sim = float(item.get('t_sim'))
        except (TypeError, ValueError):
            print('  跳过第 %d 条（t_sim 不是数字）：%r' % (i + 1, item))
            continue
        action = str(item.get('action', '') or '').strip().lower()
        if action not in ACTIONS:
            print('  跳过第 %d 条（action 只支持 %s）：%r'
                  % (i + 1, list(ACTIONS), item))
            continue
        unit = str(item.get('unit', default_unit) or '').strip()
        plan.append((t_sim, action, unit))
    plan.sort(key=lambda x: x[0])
    return plan


def write_press(cmd_path, seq, action, unit):
    """写一条按钮命令（与页面服务同一格式），返回记录 dict。"""
    rec = {'seq': seq, 't_wall': round(time.time(), 3),
           'action': action, 'unit': unit}
    _ensure_dir(cmd_path)
    with open(cmd_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n')
        f.flush()
    return rec


def wait_anchor(tail, ack_path, timeout, verbose=True):
    """等第一条带 sim_t 的回执，返回 (sim_t, t_wall_ack)；超时返回 None。"""
    deadline = time.time() + timeout
    while True:
        for rec in tail.read():
            sim_t = rec.get('sim_t')
            t_ack = rec.get('t_wall_ack')
            if sim_t is None or t_ack is None:
                continue
            try:
                return float(sim_t), float(t_ack)
            except (TypeError, ValueError):
                continue
        if timeout <= 0 or time.time() >= deadline:
            return None
        if verbose:
            sys.stdout.write('\r等待第一条回执以锚定仿真时间… %s（%s）'
                             % (os.path.basename(ack_path),
                                time.strftime('%H:%M:%S')))
            sys.stdout.flush()
        time.sleep(0.5)


# ======================================================================
# 主流程
# ======================================================================
def main():
    ap = argparse.ArgumentParser(
        description='二态按钮的脚本化操作员（按仿真时间写命令并统计往返时延）')
    ap.add_argument('--schedule', default='schedule.json', help='schedule.json 路径')
    ap.add_argument('--speed', type=float,
                    default=float(os.environ.get('PI_SPEED', '10')),
                    help='推演倍速（每墙钟秒多少推演秒），默认 10')
    ap.add_argument('--cmd', default=DEFAULT_CMD, help='命令文件（与页面服务同一份）')
    ap.add_argument('--ack', default=DEFAULT_ACK, help='回执文件（监听智能体写的）')
    ap.add_argument('--press-log', default='',
                    help='按下记录文件，默认与命令文件同目录的 presses.jsonl')
    ap.add_argument('--unit', default=os.environ.get('PI_BUTTON_UNIT', ''),
                    help='默认单元名；留空 = 监听智能体按关键字匹配全部地导单元')
    ap.add_argument('--anchor-sim', type=float, default=None,
                    help='不等回执，直接把"现在"当作该推演时刻（秒）')
    ap.add_argument('--await-anchor', type=float, default=300.0,
                    help='等第一条回执的最长墙钟秒数，默认 300')
    ap.add_argument('--wait-ack', type=float, default=120.0,
                    help='最后一次点击后等回执的最长墙钟秒数，默认 120')
    ap.add_argument('--decision-sec', type=float, default=5.0,
                    help='监听智能体的决策间隔（推演秒），只用于打印时延下界')
    ap.add_argument('--dry-run', action='store_true', help='只打印计划，不写任何文件')
    args = ap.parse_args()

    if args.speed <= 0:
        print('--speed 必须 > 0')
        return 2
    press_log = args.press_log or os.path.join(
        os.path.dirname(os.path.abspath(args.cmd)), 'presses.jsonl')

    try:
        plan = load_schedule(args.schedule, args.unit)
    except (OSError, ValueError) as e:
        print('读 %s 失败：%s' % (args.schedule, e))
        return 2
    if not plan:
        print('%s 里没有可执行条目（格式：[{"t_sim":1200,"action":"move"}]）'
              % args.schedule)
        return 2

    print('计划 %d 次点击（%s）：' % (len(plan), args.schedule))
    for t_sim, action, unit in plan:
        print('  t_sim=%7.0f s  %-6s  %s' % (t_sim, action, unit or '（全部地导单元）'))
    print('命令文件 %s' % args.cmd)
    print('回执文件 %s' % args.ack)
    print('按下记录 %s' % press_log)
    print('倍速 %.2f；决策间隔 %.0f 推演秒 ≈ 时延下界 %.0f ms'
          % (args.speed, args.decision_sec, args.decision_sec * 1000.0 / args.speed))
    if args.dry_run:
        print('\n--dry-run：不写命令、不写记录，结束。')
        return 0

    # ---------------------------------------------------------------- 锚点
    tail = JsonlTail(args.ack)
    if args.anchor_sim is not None:
        anchor_sim, anchor_wall = float(args.anchor_sim), time.time()
        print('\n锚点（手工）：t_sim=%.0f s ↔ 现在' % anchor_sim)
    else:
        got = wait_anchor(tail, args.ack, args.await_anchor)
        sys.stdout.write('\r' + ' ' * 70 + '\r')
        if got is None:
            print('等不到回执（%.0f s），改用"现在 = 第 1 条计划的 t_sim"作锚点；'
                  '若对局已在中途，请改用 --anchor-sim 手工指定。'
                  % args.await_anchor)
            anchor_sim, anchor_wall = plan[0][0], time.time()
        else:
            anchor_sim, anchor_wall = got
            print('锚点（来自第一条回执）：t_sim=%.0f s ↔ t_wall=%.3f'
                  % (anchor_sim, anchor_wall))

    def wall_for(t_sim):
        return anchor_wall + (t_sim - anchor_sim) / args.speed

    # ---------------------------------------------------------------- 点击
    seq = max_seq(args.cmd)
    presses = []
    _ensure_dir(press_log)
    for t_sim, action, unit in plan:
        delay = wall_for(t_sim) - time.time()
        if delay > 0:
            time.sleep(delay)
        elif delay < -1.0:
            print('  ⚠ t_sim=%.0f s 的计划时刻已过 %.1f 墙钟秒，立即补发'
                  % (t_sim, -delay))
        seq += 1
        rec = write_press(args.cmd, seq, action, unit)
        presses.append({'seq': seq, 'action': action, 'unit': unit,
                        't_sim': t_sim, 't_wall_press': rec['t_wall']})
        with open(press_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(presses[-1], ensure_ascii=False,
                               separators=(',', ':')) + '\n')
            f.flush()
        print('  按下 seq=%d t_sim=%.0f s %-6s %s'
              % (seq, t_sim, action, unit or '（全部地导单元）'))

    # ---------------------------------------------------------------- 收时延
    want = dict((p['seq'], p) for p in presses)
    acks = {}
    deadline = time.time() + args.wait_ack
    while want.keys() - acks.keys() and time.time() < deadline:
        for rec in tail.read():
            try:
                seq_no = int(rec.get('seq'))
            except (TypeError, ValueError):
                continue
            if seq_no in want:
                acks[seq_no] = rec
        if want.keys() - acks.keys():
            time.sleep(0.5)

    # ---------------------------------------------------------------- 汇总
    lat = []
    print('\n%-6s %-6s %-7s %-9s %-8s %s'
          % ('seq', '动作', 't_sim', '按下墙钟', '时延', '结果'))
    for p in presses:
        ack = acks.get(p['seq'])
        if ack is None:
            print('%-6d %-6s %-7.0f %-9.3f %-8s 未回执'
                  % (p['seq'], p['action'], p['t_sim'], p['t_wall_press'], '-'))
            continue
        ms = ack.get('latency_ms')
        if ms is None and ack.get('t_wall_ack') is not None:
            ms = (float(ack['t_wall_ack']) - float(p['t_wall_press'])) * 1000.0
        if ms is not None:
            lat.append(float(ms))
        print('%-6d %-6s %-7.0f %-9.3f %-8s %s'
              % (p['seq'], p['action'], p['t_sim'], p['t_wall_press'],
                 _fmt(ms) + ' ms', 'ok' if ack.get('ok') else '失败: %s'
                 % (ack.get('note') or '见监听日志')))

    missing = len(presses) - len(lat)
    print('\n往返时延：n=%d  P50=%s ms  P95=%s ms  max=%s ms  未回执 %d 条'
          % (len(lat), _fmt(_pct(lat, 50)), _fmt(_pct(lat, 95)),
             _fmt(max(lat) if lat else None), missing))
    print('参考：决策间隔 %.0f 推演秒 / %.2f 倍速 ⇒ 排队下界约 %.0f ms；'
          '明显高于它的部分才是『转译 + 下发』本身的开销。'
          % (args.decision_sec, args.speed,
             args.decision_sec * 1000.0 / args.speed))
    return 0


if __name__ == '__main__':
    sys.exit(main())
