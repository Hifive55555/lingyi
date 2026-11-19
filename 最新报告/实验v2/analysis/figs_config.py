#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""配置级图：F1 任务矩阵（任务 × 分配单元数）、F2 配置下发序列（累计条数 × 时间）。

数据源
  · 任务定义 `最新报告/监控和地空导弹营智能体代码/Mission_all_red.py`
    （SUPPORT_TASKS / PATROL_TASKS，用 ast 解析，不 import 平台 SDK）
  · 运行日志 `最新报告/实验v2/raw/logs/V2_A0_new.err`
    红蓝两个智能体写在同一文件：只取「第一局」从 `AGENT_BUILD=…RED-21`
    到 `initial 完成` 之间的红方段落（蓝方的 31/31、3/3 不参与）

输出（PNG 300dpi + SVG）到 `最新报告/paper/shared/figures/`：
  fig_task_matrix.png       F1：22 条支援任务 + 16 条巡逻任务，条长 = 分配到的单元数
  fig_config_sequence.png   F2：一次 initial() 的六阶段下发序列

用法： cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/figs_config.py
"""
import ast
import os
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 最新报告/实验v2
REPORT = os.path.dirname(ROOT)                    # 最新报告
LOG = os.path.join(ROOT, 'raw', 'logs', 'V2_A0_new.err')
MISSION_PY = os.path.join(REPORT, '监控和地空导弹营智能体代码', 'Mission_all_red.py')
FIG = os.path.join(ROOT, 'fig')          # 写到实验目录，避免覆盖论文插图

RED_BUILD = 'AGENT_BUILD=2026-11-09-RED-21'       # 红方主智能体的构建标记（每局一条）
TS = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')

SUPPORT_COLOR = '#2f6db5'
PATROL_COLOR = '#3f9a5a'
EMPTY_COLOR = '#8a8a8a'
PHASE_COLORS = ('#8c8c8c', '#7b5aa6', '#c98b2f', '#2f8f8f',
                SUPPORT_COLOR, PATROL_COLOR)


# ---------------------------------------------------------------- 任务定义
def parse_mission_defs():
    """从 Mission_all_red.py 的 Agent 类属性里取任务名 + 选择器单元数（兜底来源）。"""
    with open(MISSION_PY, encoding='utf-8') as f:
        tree = ast.parse(f.read())

    def attr_items(cls_name, attr):
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                for stmt in node.body:
                    if (isinstance(stmt, ast.Assign)
                            and getattr(stmt.targets[0], 'id', '') == attr):
                        return stmt.value.elts
        return []

    names, counts = {'support': [], 'patrol': []}, {}
    for kind, attr in (('support', 'SUPPORT_TASKS'), ('patrol', 'PATROL_TASKS')):
        for item in attr_items('Agent', attr):
            name = item.elts[0].value
            names[kind].append(name)
            # 元组下标 3 是执行单元选择器元组；_sel(关键字, 编号...) 的编号个数
            # 就是该选择器能匹配的单元数
            total = 0
            for sel in getattr(item.elts[3], 'elts', []):
                idx = [a for a in sel.args[1:] if isinstance(a, ast.Constant)]
                total += len(idx) or 1
            counts[name] = total
    return names, counts


# ---------------------------------------------------------------- 运行日志
def red_blocks():
    """返回第一局红方段落的 (时间串, 整行) 列表。"""
    out, inside = [], False
    with open(LOG, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = TS.match(line)
            if not m:
                continue
            if RED_BUILD in line and not inside:
                inside = True
                continue
            if not inside:
                continue
            out.append((m.group(1), line))
            if 'initial 完成' in line:
                break
    return out


RE_SUP = re.compile(r'支援任务\[(.+?)\] 已创建：单元 (\d+) 个')
RE_PAT = re.compile(r'巡逻任务\[(.+?)\] 已创建：类型 [\w.]*，单元 (\d+) 个')


def parse_units(blocks):
    sup, pat = {}, {}
    for _, text in blocks:
        m = RE_SUP.search(text)
        if m:
            sup[m.group(1)] = int(m.group(2))
            continue
        m = RE_PAT.search(text)
        if m:
            pat[m.group(1)] = int(m.group(2))
    return sup, pat


def _t(blocks, idx):
    return datetime.strptime(blocks[idx][0], '%Y-%m-%d %H:%M:%S')


def _find(blocks, pattern, start=0):
    rx = re.compile(pattern)
    for i in range(start, len(blocks)):
        m = rx.search(blocks[i][1])
        if m:
            return i, m
    raise SystemExit('日志里没找到：%s' % pattern)


def parse_phases(blocks):
    """六个阶段的 (名称, 条数, 起, 止, 明细)。起止取该阶段首条/末条配置日志的时刻。"""
    phases = []

    def span(first_pat, last_pat, start=0):
        i0, _ = _find(blocks, first_pat, start)
        i1, m1 = _find(blocks, last_pat, i0)
        return i0, i1, _t(blocks, i0), _t(blocks, i1), m1

    # ① 总条令
    _, _, t0, t1, m = span(r'总条令已下发 (\d+) 条', r'总条令已下发 (\d+) 条')
    phases.append(('总条令', int(m.group(1)), t0, t1,
                   '对空/对海/对地/对潜开火 + 电磁管控与返航条令'))

    # ② 总条令 WRA（空空 + 对地/反辐射）
    i0, _, t0, t1, m = span(r'总条令 WRA\[', r'总条令对地/反辐射弹 WRA 共下发 (\d+) 条')
    _, ma = _find(blocks, r'总条令空空导弹 WRA 共下发 (\d+) 条', i0)
    phases.append(('总条令 WRA（空空 + 对地/反辐射）',
                   int(ma.group(1)) + int(m.group(1)), t0, t1,
                   '空空 %s 条 + 对地/反辐射 %s 条' % (ma.group(1), m.group(1))))

    # ③ 挂载 + 舰船对空条令
    i0, _, t0, t1, m = span(r'飞机\[.+?\] 挂载 →', r'“雷鸣”号对空条令设置完成 (\d+)/(\d+)')
    _, mm = _find(blocks, r'飞机挂载设置完成 (\d+) 架', i0)
    phases.append(('挂载 + 舰船对空条令', int(mm.group(1)) + int(m.group(1)), t0, t1,
                   '改挂 %s 架 + 舰船对空限制开火 %s 艘' % (mm.group(1), m.group(1))))

    # ④ 单元级 WRA + 战前移动
    i0, _, t0, t1, m = span(r'单元级武器使用规则共下发 (\d+) 条', r'战前移动完成 (\d+) 个单元')
    _, mw = _find(blocks, r'单元级武器使用规则共下发 (\d+) 条', i0)
    phases.append(('单元级 WRA + 战前移动', int(mw.group(1)) + int(m.group(1)), t0, t1,
                   '单元级 WRA %s 条 + 战前移动 %s 个单元' % (mw.group(1), m.group(1))))

    # ⑤ 支援任务
    i0, _, t0, t1, m = span(r'支援任务\[', r'支援任务创建完成 (\d+)/(\d+)')
    phases.append(('支援任务', int(m.group(1)), t0, t1,
                   '%s/%s 条支援任务逐个创建' % (m.group(1), m.group(2))))

    # ⑥ 巡逻任务 + 任务级 WRA + 开雷达
    i0, _, t0, t1, m = span(r'巡逻任务\[', r'单元开雷达设置完成 (\d+)/(\d+)')
    _, mp = _find(blocks, r'巡逻任务创建完成 (\d+)/(\d+)', i0)
    _, mw = _find(blocks, r'任务级武器使用规则共下发 (\d+) 条', i0)
    phases.append(('巡逻任务 + 任务级 WRA + 开雷达',
                   int(mp.group(1)) + int(mw.group(1)) + int(m.group(1)), t0, t1,
                   '巡逻任务 %s 条 + 任务级 WRA %s 条 + 开雷达 %s 个'
                   % (mp.group(1), mw.group(1), m.group(1))))
    return phases


def parse_summary(blocks):
    """initial() 末行的自报总数与节流睡眠秒数。"""
    for _, text in blocks:
        m = re.search(r'initial 完成：本周期下发 (\d+) 条'
                      r'（窗口节流累计睡眠 ([\d.]+) 秒）', text)
        if m:
            return int(m.group(1)), float(m.group(2))
    raise SystemExit('日志里没找到 initial 完成 的汇总行')


# ---------------------------------------------------------------- 画图
def setup_mpl():
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import font_manager, rcParams
    for cand in ('Noto Sans CJK SC', 'Source Han Sans SC', 'WenQuanYi Zen Hei'):
        if any(f.name == cand for f in font_manager.fontManager.ttflist):
            rcParams['font.sans-serif'] = [cand, 'DejaVu Sans']
            break
    rcParams['axes.unicode_minus'] = False
    rcParams['svg.fonttype'] = 'none'      # SVG 里保留文字（可编辑）
    return matplotlib


def fig_task_matrix(names, code_counts, sup_units, pat_units):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle

    rows, n_from_log, n_from_code = [], 0, 0

    def add(name_list, units):
        nonlocal n_from_log, n_from_code
        block = []
        for nm in name_list:
            if nm in units:
                n = units[nm]
                n_from_log += 1
            else:
                n = code_counts.get(nm, 0)
                n_from_code += 1
            block.append((nm, n))
        block.sort(key=lambda r: (-r[1], r[0]))       # 单元数降序，同数按名字
        rows.extend(block)
        return sum(r[1] for r in block)

    sum_sup = add(names['support'], sup_units)
    sum_pat = add(names['patrol'], pat_units)
    n_sup, n_pat, total = len(names['support']), len(names['patrol']), len(rows)

    fig, ax = plt.subplots(figsize=(9.2, 11.4))
    ypos = list(range(total))
    # 浅色底分块：支援任务（上）/ 巡逻任务（下）
    for y0, y1, color in ((-0.5, n_sup - 0.5, '#eef3fa'),
                          (n_sup - 0.5, total - 0.5, '#eef7f0')):
        ax.add_patch(Rectangle((-0.02, y0), 1.02, y1 - y0,
                               transform=ax.get_yaxis_transform(),
                               facecolor=color, edgecolor='none', zorder=0))

    for y, (nm, n) in zip(ypos, rows):
        color = SUPPORT_COLOR if y < n_sup else PATROL_COLOR
        if n == 0:
            ax.barh(y, 0.55, height=0.6, color='white', edgecolor=EMPTY_COLOR,
                    hatch='///', linewidth=0.6, zorder=2)
            ax.text(0.68, y, '0', va='center', ha='left', fontsize=6.4,
                    color=EMPTY_COLOR)
        else:
            ax.barh(y, n, height=0.6, color=color, edgecolor='white',
                    linewidth=0.5, zorder=2)
            ax.text(n + 0.18, y, str(n), va='center', ha='left', fontsize=6.4,
                    color='#333333')

    ax.set_yticks(ypos)
    ax.set_yticklabels([r[0] for r in rows], fontsize=7)
    ax.invert_yaxis()
    ax.set_ylim(total - 0.4, -0.8)
    ax.set_xlim(0, max(n for _, n in rows) + 0.9)
    ax.set_xticks(range(0, max(n for _, n in rows) + 1))
    ax.set_xlabel('该任务分配到的执行单元数（个）', fontsize=8.5)
    ax.tick_params(axis='x', labelsize=7)
    ax.grid(axis='x', color='#cccccc', linewidth=0.4, alpha=0.7, zorder=1)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)

    # 分块标题（含本块单元数合计）
    ax.text(0.995, 1.004, '支援任务 %d 条 · 合计 %d 个单元' % (n_sup, sum_sup),
            transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5,
            color=SUPPORT_COLOR, weight='bold')
    ax.annotate('巡逻任务 %d 条 · 合计 %d 个单元' % (n_pat, sum_pat),
                xy=(0.995, 1 - (n_sup - 0.5) / total), xycoords='axes fraction',
                xytext=(0, 7), textcoords='offset points',
                ha='right', va='bottom', fontsize=8.5, color=PATROL_COLOR,
                weight='bold')

    handles = [
        Patch(facecolor=SUPPORT_COLOR, label='支援任务（%d 条）' % n_sup),
        Patch(facecolor=PATROL_COLOR, label='巡逻任务（%d 条）' % n_pat),
        Patch(facecolor='white', edgecolor=EMPTY_COLOR, hatch='///',
              label='开局未分配执行单元（选择器为空）'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=7.2, frameon=True,
              framealpha=0.95, borderpad=0.6, handlelength=1.6,
              title='条长 = 该任务分配到的单元数', title_fontsize=7.4)
    fig.tight_layout()
    for ext in ('png', 'svg'):
        fig.savefig(os.path.join(FIG, 'fig_task_matrix.' + ext),
                    dpi=300 if ext == 'png' else None)
    plt.close(fig)
    return total, n_from_log, n_from_code


def fig_config_sequence(phases, summary):
    import matplotlib.pyplot as plt

    t_ref = phases[0][2]
    el = [{'name': n, 'n': c, 't0': (a - t_ref).total_seconds(),
           't1': (b - t_ref).total_seconds(), 'note': note, 'color': PHASE_COLORS[i]}
          for i, (n, c, a, b, note) in enumerate(phases)]
    total_n = sum(e['n'] for e in el)
    end_t = el[-1]['t1']

    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.94, bottom=0.20)
    ax.set_xlim(-0.7, end_t + 1.4)
    ax.set_ylim(0, total_n * 1.12)

    # 平台按“任意 10 秒窗口”计指令预算：每 10 s 一条虚线，正好是每段耗时的来源
    wins = list(range(10, int(end_t) + 1, 10))
    for win in wins:
        ax.axvline(win, color='#cfcfcf', linewidth=0.7, linestyle=(0, (3, 2)),
                   zorder=0)
        ax.text(win, total_n * 1.09, '%d s 指令窗口边界' % win, fontsize=6.6,
                color='#9a9a9a', ha='right' if win == wins[-1] else 'center',
                va='top')

    # 阶梯：水平段 = 该阶段等待窗口的时长；垂直段 = 该阶段新增的条数
    y = 0
    xs, ys = [0.0], [0.0]
    for e in el:
        c, n, t0, t1 = e['color'], e['n'], e['t0'], e['t1']
        if t1 > t0:
            ax.plot([t0, t1], [y, y], color=c, linewidth=3.0,
                    solid_capstyle='butt', zorder=3)
            xs += [t0, t1]
            ys += [y, y]
        ax.plot([t1, t1], [y, y + n], color=c, linewidth=3.0,
                solid_capstyle='butt', zorder=3)
        xs.append(t1)
        ys.append(y + n)
        y += n
    ax.fill_between(xs, ys, step=None, color='#eef3fa', alpha=0.9, zorder=1)

    ax.set_xlabel('日志时间（秒，自首条配置日志 %s 起）' % t_ref.strftime('%H:%M:%S'),
                  fontsize=8.6)
    ax.set_ylabel('累计下发条数', fontsize=8.6)
    ax.tick_params(labelsize=7.4)
    ax.set_xticks(range(0, int(end_t) + 1, 2))
    ax.set_yticks(range(0, total_n + 1, 25))
    ax.grid(axis='y', color='#dddddd', linewidth=0.4, alpha=0.8, zorder=2)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)

    def two_line(e, i):
        return ('%s %s\n%d 条 · %.1f s'
                % ('①②③④⑤⑥'[i], e['name'], e['n'], e['t1'] - e['t0']))

    # ①–④ 都在开局同一秒内完成：引线右移错开标注（dy 把最短的一段抬离横轴）
    leader = [(0.35, 1.45, 4.0), (0.35, 2.05, 0.0),
              (0.35, 2.65, 0.0), (0.35, 3.25, 0.0)]
    y = 0
    for i, (e, (xo, x, dy)) in enumerate(zip(el[:4], leader)):
        ax.annotate(two_line(e, i), xy=(e['t1'], y + e['n'] / 2.0 + dy),
                    xytext=(x + xo, y + e['n'] / 2.0 + dy), fontsize=7.2,
                    color=e['color'], va='center', ha='left',
                    arrowprops=dict(arrowstyle='-', color=e['color'],
                                    linewidth=0.6, shrinkA=0, shrinkB=0.5))
        y += e['n']

    # ⑤⑥ 时长可见（各 10 s），标注放在水平段上方的空白处
    for e, i, xy in ((el[4], 4, (1.4, 163)), (el[5], 5, (10.6, 188))):
        ax.text(xy[0], xy[1], '%s %s  %d 条 · %.1f s'
                % ('①②③④⑤⑥'[i], e['name'], e['n'], e['t1'] - e['t0']),
                fontsize=7.6, color=e['color'], va='center', ha='left',
                weight='bold')

    ax.text(1.6, 105, '①–④ 共 %d 条，均在同一秒内下发完成'
            % sum(e['n'] for e in el[:4]),
            fontsize=7.2, color='#555555', va='center', ha='left')

    fig.text(0.085, 0.045,
             '阶梯段颜色 = 六个阶段；段旁标注为「阶段名 / 条数 / 耗时」。'
             '⑤ 支援任务段内无条数增长、⑥ 段首已建完 16 条巡逻任务，两条水平段都是等平台 10 s 指令窗口滑出。\n'
             '日志自报：本周期下发 %d 条、窗口节流累计睡眠 %.1f s（占 %.1f s 的 %.0f%%），'
             '即 initial() 的墙钟时间几乎全部耗在等待指令窗口。'
             % (summary[0], summary[1], end_t, summary[1] / end_t * 100),
             fontsize=7.0, color='#444444', ha='left', va='bottom', linespacing=1.5)
    for ext in ('png', 'svg'):
        fig.savefig(os.path.join(FIG, 'fig_config_sequence.' + ext),
                    dpi=300 if ext == 'png' else None)
    plt.close(fig)
    return el, total_n, end_t


def main():
    os.makedirs(FIG, exist_ok=True)
    setup_mpl()
    names, code_counts = parse_mission_defs()
    blocks = red_blocks()
    sup_units, pat_units = parse_units(blocks)
    print('红方第一局：%d 条日志记录（%s ~ %s）' % (len(blocks), blocks[0][0], blocks[-1][0]))
    print('任务定义：支援任务 %d 条、巡逻任务 %d 条'
          % (len(names['support']), len(names['patrol'])))
    print('日志解析：支援任务 %d 条、巡逻任务 %d 条' % (len(sup_units), len(pat_units)))

    total, from_log, from_code = fig_task_matrix(names, code_counts, sup_units, pat_units)
    print('F1：%d 行（日志解析 %d / 代码推算 %d）→ fig_task_matrix.png|svg'
          % (total, from_log, from_code))

    phases = parse_phases(blocks)
    summary = parse_summary(blocks)
    el, total_n, end_t = fig_config_sequence(phases, summary)
    # 口径核对：日志里的“单元 N 个”与代码选择器的单元数应一致
    units = dict(sup_units)
    units.update(pat_units)
    diff = [(nm, units[nm], code_counts[nm]) for nm in units
            if code_counts.get(nm) != units[nm]]
    print('日志单元数 vs 代码选择器：%s' % ('一致' if not diff else diff))
    print('F2：六阶段（合计 %d 条、%.1f s；日志自报 %d 条、睡眠 %.1f s）'
          % (total_n, end_t, summary[0], summary[1]))
    for e in el:
        print('  %-26s %4d 条  %5.1f ~ %5.1f s  %.1f s  %s'
              % (e['name'], e['n'], e['t0'], e['t1'], e['t1'] - e['t0'], e['note']))
    print('  → fig_config_sequence.png|svg')


if __name__ == '__main__':
    main()
