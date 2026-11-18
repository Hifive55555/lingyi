# -*- coding: utf-8 -*-
"""v2 实验批量驱动：**一局一进程**（崩溃只损失一局），可断点续跑，带时间预算。

python pi_v2_drive.py plan.json
"""
import json, os, subprocess, sys, time

PY = r'D:\LingYi\intelligent\new_env\ray210\python.exe'
AI = r'D:\LingYi\intelligent\ai'


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


def count_done(out_path, arm):
    """已成功完成的局数 + 已尝试次数"""
    ok = tried = 0
    if not os.path.exists(out_path):
        return 0, 0
    with open(out_path, encoding='utf-8') as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('arm') != arm or not r.get('finished'):
                continue
            tried += 1
            if r.get('ok') and r.get('steps', 0) > 30:
                ok += 1
    return ok, tried


def sh(cmd):
    try:
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def clean():
    sh('taskkill /f /im Plat.exe')
    time.sleep(5)
    sh('taskkill /f /im Plat.exe')
    time.sleep(2)


def main():
    plan = json.load(open(sys.argv[1], encoding='utf-8'))
    out, jobs_dir, logs_dir, tap_dir = plan['out'], plan['jobs_dir'], plan['logs'], plan['tap_dir']
    for d in (jobs_dir, logs_dir, tap_dir, os.path.dirname(out)):
        if d and not os.path.isdir(d):
            os.makedirs(d)
    budget = float(plan.get('budget_h', 6.0)) * 3600.0
    t_start = time.time()
    per_ep = float(plan.get('est_s_per_episode', 300))
    hard = float(plan.get('episode_timeout_s', 900))
    log('PLAN %d arms, budget %.1fh, est %.0fs/ep, timeout %.0fs' %
        (len(plan['arms']), budget / 3600.0, per_ep, hard))

    for arm in plan['arms']:
        name = arm['name']
        want = int(arm.get('episodes', 4))
        fails = 0
        while True:
            ok, tried = count_done(out, name)
            if ok >= want:
                log('%s: done %d/%d' % (name, ok, want))
                break
            left = budget - (time.time() - t_start)
            if left < per_ep * 0.7 + 150:
                log('BUDGET: %.0fs left -> stop' % left)
                return
            if fails >= 3:
                log('%s: %d 连续失败，跳过' % (name, fails))
                break
            job = {'scenario': plan['scenario'], 'arm': name, 'episodes': 1,
                   'decision_interval': plan.get('decision_interval', 30),
                   'compression': plan.get('compression', 10001),
                   'max_steps': plan.get('max_steps', 0), 'save_result': True,
                   'room': 'pi2-' + name[:12], 'out': out, 'agents': plan['agents']}
            jp = os.path.join(jobs_dir, name + '.json')
            json.dump(job, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            env = dict(os.environ)
            env.update({'PI_THETA': json.dumps(arm.get('theta') or {}, ensure_ascii=False),
                        'PI_TAP_TAG': '%s__%d' % (name, int(time.time())), 'PI_TAP_DIR': tap_dir,
                        'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'})
            clean()
            t_ep = time.time()
            log('=== %s  ep %d/%d (fail %d)  %.2fh ===' %
                (name, ok + 1, want, fails, (t_ep - t_start) / 3600.0))
            so = open(os.path.join(logs_dir, name + '.out'), 'a', encoding='utf-8')
            se = open(os.path.join(logs_dir, name + '.err'), 'a', encoding='utf-8')
            p = subprocess.Popen([PY, 'pi_v2_run.py', jp], cwd=AI, env=env, stdout=so, stderr=se)
            while p.poll() is None and (time.time() - t_ep) < hard:
                time.sleep(5)
            if p.poll() is None:
                log('TIMEOUT %.0fs -> kill' % (time.time() - t_ep))
                p.kill()
                time.sleep(3)
            so.close(); se.close()
            dt = time.time() - t_ep
            ok2, tried2 = count_done(out, name)
            if ok2 > ok:
                log('%s: OK %.0fs (total %d/%d)' % (name, dt, ok2, want))
                fails = 0
            else:
                fails += 1
                log('%s: FAIL %.0fs (fail %d)' % (name, dt, fails))
            clean()
    log('DRIVER DONE total %.1fh' % ((time.time() - t_start) / 3600.0))


if __name__ == '__main__':
    main()
