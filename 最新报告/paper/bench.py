# 规则判定的纯计算耗时微基准（不含平台接口调用）
import timeit, math

V_TERM = 500.0
T = 240.0

def d0(V0, Va):
    if Va <= V_TERM: return T*(V0+V_TERM)/2 - T*Va
    return T*(V0-Va)**2/(2*(V0-V_TERM))

def monitor(unit, rounds):
    # 最近接近点判定：位置 + 速度矢量
    for r in rounds:
        dx = r[0]-unit[0]; dy = r[1]-unit[1]
        vx, vy = r[2], r[3]
        t = -(dx*vx+dy*vy)/(vx*vx+vy*vy+1e-9)
        if t > 0:
            px = dx+vx*t; py = dy+vy*t
            if px*px+py*py < 4.0:   # 2 km 门限
                return r[4], r[5]
    return None

def evade(plane, rounds):
    for r in rounds:
        d = math.hypot(r[0]-plane[0], r[1]-plane[1]); v = r[2]
        turn = 50.0 if v > 2500 else 20.0
        if d <= turn: return 'turn'
        if d < 20 and v > plane[2]:
            return 'weave'
        if v < 500: return 'counter'
    return 'keep'

def aircombat(me, tgts):
    for t in tgts:
        d = math.hypot(t[0]-me[0], t[1]-me[1])
        r = t[2]/me[2]
        if r < 0.9 or r > 1.2: continue
        if d < 0.8*d0(t[3], me[3]): return 'fire'
    return 'hold'

def sam(tgts, Dmax=100.8):
    for t in tgts:
        if t[0] <= 0.6*Dmax:
            p = min(1.0, (t[1]-V_TERM)/(0.6*t[2]))
            if p > 0: return p
    return 0.0

rounds = [(50.0+i*0.3, 3.0+i*0.1, -1.2, 0.02, 'AR', 2500+i) for i in range(60)]
tgts = [(40.0+i*0.5, 30.0, 1.05, 2500+i*20, 900.0) for i in range(60)]
unit = (49.0, 0.5)
plane = (49.0, 0.5, 900.0)

def t(fn, *a):
    n = 20000
    return timeit.timeit(lambda: fn(*a), number=n)/n*1e6   # µs

print('monitor 每单元每次调用: %.1f µs' % t(monitor, unit, rounds))
print('evade   每机每次调用:   %.1f µs' % t(evade, plane, rounds))
print('aircombat 每机每次调用: %.1f µs' % t(aircombat, plane, tgts))
print('sam     每营每次调用:   %.1f µs' % t(sam, tgts))
print('d0      单次:           %.3f µs' % t(d0, 2500.0, 900.0))
for n_unit in (50, 100, 200, 400):
    print('monitor %d 单元一步: %.2f ms' % (n_unit, t(monitor, unit, rounds)*n_unit/1000))

print('--- 无早退（全量遍历）---')
rounds_far = [(50.0+i*0.3, 30.0+i*0.2, 0.0, 0.02, 'AR', 2500+i) for i in range(60)]
tgts_far = [(20.0+i*0.5, 30.0, 1.05, 2500+i*20, 900.0) for i in range(60)]
print('evade 全量:    %.2f µs' % t(evade, plane, rounds_far))
print('aircombat 全量: %.2f µs' % t(aircombat, plane, tgts_far))
print('monitor 全量:  %.2f µs' % t(monitor, unit, rounds_far))

print('--- evade 全量遍历（距离 > 60 km，不触发早退）---')
rounds_vfar = [(100.0+i*0.5, 80.0+i*0.3, 0.0, 0.02, 'AR', 1000+i) for i in range(60)]
print('evade 全量:  %.2f µs' % t(evade, plane, rounds_vfar))
print('evade 200 架一步: %.2f ms' % (t(evade, plane, rounds_vfar)*200/1000))

print('--- evade 真·全量（速度 1500 km/h，距离 > 60 km）---')
rounds_ok = [(100.0+i*0.5, 80.0+i*0.3, 1500.0, 0.02, 'AR', 1000+i) for i in range(60)]
r = t(evade, plane, rounds_ok)
print('evade 全量:  %.2f µs ；200 架一步 %.2f ms' % (r, r*200/1000))
