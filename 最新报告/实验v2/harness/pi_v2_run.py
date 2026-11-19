# -*- coding: utf-8 -*-
"""灵弈平台 v2 实验 runner（无头，Session 1）

用法： PI_THETA='{"k_turn":1.2}' python pi_v2_run.py <job.json>
"""
import sys, os, json, time, traceback, importlib

AI = r'D:\LingYi\intelligent\ai'
sys.path.insert(0, AI)
os.chdir(AI)

THETA_MAP = {
    'agent.Mission_tactics_red': ('Agent', {
        'k_turn': 'EVADE_D0_COEF', 'use_d0': 'EVADE_USE_D0', 'evade_mode': 'EVADE_MODE',
        'vjink': 'VERTICAL_JINK', 'jink_cycles': 'JINK_SWITCH_CYCLES',
        'fire_k': 'FIRE_COEF', 'fire_fixed_km': 'FIRE_FIXED_KM',
        'fire_range_coef': 'FIRE_RANGE_COEF', 'fire_min_km': 'FIRE_MIN_KM',
        'evade_hi_km': 'EVADE_TURN_HI_KM', 'evade_lo_km': 'EVADE_TURN_LO_KM',
        'evade_always_km': 'EVADE_ALWAYS_KM', 'beam_km': 'EVADE_BEAM_KM',
    }),
    'agent.Mission_all_red': ('Agent', {'wra_nm': 'AIR_WRA_NM_OVERRIDE'}),
    'engine.LingYi.SamBattalionDefense': ('SamBattalionDefense', {'sam_ratio': 'FIRE_RATIO'}),
    'engine.LingYi.ShipClusterDefense': ('ShipClusterDefense', {'ship_layered': 'LAYERED'}),
}
_BOOL = ('EVADE_USE_D0', 'VERTICAL_JINK', 'LAYERED')


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


def apply_theta(mod):
    raw = os.environ.get('PI_THETA', '').strip()
    if not raw:
        return {}
    th = json.loads(raw)
    if mod.__name__ not in THETA_MAP:
        return {}
    cls_name, mapping = THETA_MAP[mod.__name__]
    cls = getattr(mod, cls_name, None)
    if cls is None:
        return {}
    used = {}
    for k, v in th.items():
        attr = mapping.get(k)
        if not attr or not hasattr(cls, attr):
            continue
        if attr in _BOOL:
            v = bool(int(v)) if not isinstance(v, bool) else v
        else:
            v = float(v)
        setattr(cls, attr, v)
        used[attr] = v
    if used:
        log('theta %s: %s' % (mod.__name__, json.dumps(used, ensure_ascii=False)))
    return used


def main():
    job = json.load(open(sys.argv[1], encoding='utf-8'))
    out_path = job['out']
    d = os.path.dirname(out_path)
    if d and not os.path.isdir(d):
        os.makedirs(d)

    from agent.config import LingYiConfig
    from engine.LingYi.entitys.deduce_RL import Deduction

    cfg = LingYiConfig.get_server_config({})
    gs = cfg['game_server']
    sim = gs['simulate']
    sim.update({
        'scenario': job['scenario'], 'scen_check': True,
        'episodes': int(job.get('episodes', 1)),
        'compression': int(job.get('compression', 10001)), 'need_compression': True,
        'decision_interval': int(job.get('decision_interval', 30)),
        'step_interval': int(job.get('step_interval', 1)),
        'training': False, 'testing': False,
        'save_result': bool(job.get('save_result', True)),
        'load_scenario': True, 'main_client': True, 'clear_room': True,
        'save_situation_type': 0, 'simulate_complex': int(job.get('simulate_complex', 6)),
    })
    gs['server']['room_name'] = job.get('room', 'pi-v2')
    gs['server']['continuous'] = 0

    rule_config = {}
    for side, specs in (job.get('agents') or {}).items():
        rule_config[side] = {}
        for name, spec in specs.items():
            mod = importlib.import_module(spec['module'])
            apply_theta(mod)
            rule_config[side][name] = {'class': getattr(mod, spec['class']),
                                       'unit': [], 'contact': [], 'point': []}
    for _m in ('engine.LingYi.SamBattalionDefense', 'engine.LingYi.ShipClusterDefense'):
        try:
            apply_theta(importlib.import_module(_m))
        except Exception:
            pass
    cfg['rule_config'] = rule_config
    if not rule_config:
        cfg['RL_agents'] = {'红方': {'agents': {}}, '蓝方': {'agents': {}}}

    t0 = time.time()
    env = Deduction(cfg)
    log('Deduction built in %.1fs' % (time.time() - t0))

    episodes = int(job.get('episodes', 1))
    max_steps = int(job.get('max_steps', 0)) or 365
    fo = open(out_path, 'a', encoding='utf-8')
    try:
        for ep in range(1, episodes + 1):
            rec = {'ts': time.strftime('%Y-%m-%d %H:%M:%S'), 'arm': job.get('arm', ''),
                   'theta': os.environ.get('PI_THETA', ''), 'tap': os.environ.get('PI_TAP_TAG', ''),
                   'scenario': job['scenario'],
                   'episode': ep, 'decision_interval': sim['decision_interval']}
            t1 = time.time()
            try:
                r = env.reset(ep)
            except Exception:
                r = -99
                rec['reset_err'] = traceback.format_exc()[-400:]
            rec['reset'] = int(r)
            log('ep%s reset=%d (%.1fs)' % (ep, r, time.time() - t1))
            if r != 1:
                rec['ok'] = False
                rec['finished'] = True
                fo.write(json.dumps(rec, ensure_ascii=False) + '\n'); fo.flush()
                time.sleep(15)
                continue
            n, t_last, st = 0, time.time(), []
            err = ''
            done_streak = 0
            while n < max_steps:
                try:
                    env.step({})
                except Exception:
                    err = traceback.format_exc()[-500:]
                    log('ep%s STEP ERROR at %d: %s' % (ep, n, err.splitlines()[-1][:200]))
                    break
                n += 1
                now = time.time()
                st.append(now - t_last); t_last = now
                try:
                    if env.is_done():
                        # 平台偶发瞬时 is_done=True（实测约占一半的局），连续 3 次才认
                        done_streak += 1
                        if done_streak >= 3:
                            break
                    else:
                        done_streak = 0
                except Exception:
                    err = 'is_done failed'
                    break
                if n % 60 == 0:
                    log('  ep%s step %d wall %.0fs avg %.3fs' %
                        (ep, n, now - t1, sum(st[-60:]) / 60.0))
            # 性能读数：单步墙钟的均值与分位数、仿真时间与墙钟的比值。
            # 决策间隔从 30 s 改到 5 s 之后，步数会变成 6 倍，靠这几个数才能说清
            # "多花的时间是花在引擎推进上，还是花在规则判定上"。
            def _pct(xs, q):
                if not xs:
                    return 0.0
                ys = sorted(xs)
                k = max(0, min(len(ys) - 1, int(round(q * (len(ys) - 1)))))
                return round(ys[k], 4)
            sim_end = 0.0
            try:
                sim_end = float(getattr(env, 'sim_time', 0) or 0)
            except Exception:
                pass
            wall = round(time.time() - t1, 1)
            rec.update({'finished': True, 'steps': n, 'wall_s': wall,
                        'step_avg_s': round(sum(st) / max(1, len(st)), 4),
                        'step_p50_s': _pct(st, 0.5), 'step_p95_s': _pct(st, 0.95),
                        'step_max_s': round(max(st), 4) if st else 0.0,
                        'step_min_s': round(min(st), 4) if st else 0.0,
                        'sim_end': sim_end,
                        'speedup': round(sim_end / wall, 2) if wall else 0.0,
                        'ok': (not err) or n >= 355})
            if err:
                rec['step_err'] = err
            try:
                g = env.get_game_result()
                rec.update({'red_score': g.red_score, 'blue_score': g.blue_score,
                            'winner': g.bat_result, 'sim_end': float(g.time),
                            'error_side': str(g.error_side or '')})
            except Exception:
                rec['result_error'] = traceback.format_exc()[-300:]
            log('ep%s done %s' % (ep, json.dumps({k: rec.get(k) for k in
                                                 ('ok', 'steps', 'red_score', 'blue_score', 'sim_end')}, ensure_ascii=False)))
            fo.write(json.dumps(rec, ensure_ascii=False) + '\n'); fo.flush()
    finally:
        fo.close()
        log('ARM DONE')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
