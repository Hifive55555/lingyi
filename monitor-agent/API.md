# 监控智能体 · 数据接口说明（给其他智能体 / 下游模块）

本文只讲**怎么用**。判定原理、频率、小窗实现在 `README.md`。

---

## 0. 两种接入方式，先选一个

| 方式 | 谁在用 | 适合什么 | 怎么接 |
| --- | --- | --- | --- |
| **A. 嵌入组件** `lymonitor.monitor.Monitor` | 其他智能体（地空导弹营、空战自卫、登陆船只……） | 你自己的智能体要**拿监控结论做决策** | `self.monitor = Monitor(self)`，在 `step` 里 `ensure(situation)` 然后查询 |
| **B. 独立智能体** `monitor_ai.py`（`class Agent`） | 本次测试 / 只想要小窗看态势 | 不想改自己的智能体代码，只要**看** | 客户端「智能体编辑」导入 `monitor_ai.py` 并启动 |

两者是**同一套判定**（`lymonitor/core.py`），结论完全一致；A 是函数调用，B 是进程内独立智能体 + 小窗。
可以**同时用**：先按 B 挂上去验证，再按 A 嵌进主智能体。

> 参考方案里 `BattlefieldMonitor` + `SamBattalionDefense` 的写法就是 A；
> 本仓库的 `MonitorAgent` 是 B。两者共用 `core.analyse()`。

---

## 1. 最小接入（A 方式，5 行）

```python
from lymonitor.monitor import Monitor

class Agent(RuleAgentBase):
    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        self.monitor = Monitor(self)                 # ← ① 建一个

    def initial(self, situation):
        self.monitor.setup(situation)                # ← ② 开局登记本方单位

    def step(self, time_elapse, situation):
        self.monitor.ensure(situation, time_elapse)  # ← ③ 每周期算一次（幂等）

        for guid, u in self.aircrafts.items():
            if self.monitor.has_incoming(guid):      # ← ④ 有没有弹朝我来
                name, speed = self.monitor.incoming(guid)   # ← ⑤ 弹型 + 当前弹速 km/h
                ...
```

`sys.path` 上要能找到 `lymonitor`：把整个 `monitor-agent/` 目录拷到
`D:\LingYi\intelligent\ai\agent\` 下，然后在主智能体文件开头

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor-agent'))
```

（`lymonitor/agent.py` 会自己往上找 `engine\LingYi`，包放哪一层都不影响。）

---

## 2. 公开 API 一览

所有方法都不下发指令、不抛异常（内部 catch 后记日志），返回值只读副本。

| 方法 | 返回 | 说明 | 每次开销 |
| --- | --- | --- | --- |
| `setup(situation)` | `dict` 自检摘要 | 开局调一次；登记本方单位并空跑一次 | 一次 `step` |
| `ensure(situation, time_elapse=None)` | `bool` 是否真的重算 | **幂等**：同一个推演时刻只算一次。判据是**时间**不是态势对象身份（平台会缓存复用同一个 tuple）；不传时间时读 `agent.time_elapse` | 0（已算过时） |
| `step(situation, time_elapse=None)` | `dict` 统计 | 强制重算。一般不用直接调，`ensure` 内部会调 | O(单元×弹) |
| `ready` (属性) | `bool` | 是否已成功跑过至少一次。**下游用前先判这个** | 0 |
| `has_incoming(guid)` | `bool` | 该单元是否被任何一枚弹朝我飞 | 字典查表 |
| `incoming(guid)` | `(弹型, 弹速km/h)` 或 `None` | **最紧迫的一枚**（按 `tgo` 升序取第一） | 字典查表 |
| `incoming_list(guid)` | `[(弹型, 弹速km/h), …]` | 所有朝它飞的弹，按紧急度排序 | 字典查表 |
| `threats_for(guid)` | `[dict, …]` | **要动作时用这个**：多带情报 guid 和几何量（见 §3） | 字典查表 |
| `route(category)` | `[(guid, 单元名), …]` | 按作用对象取“当前确实被瞄准”的清单（报告的一进三出） | 遍历一次 |
| `rows()` | `[dict, …]` | 本周期全量快照（空/海/陆三组，**含未被攻击的**），小窗/日志用 | 深一层副本 |
| `missiles()` | `[dict, …]` | 本周期枚举到的敌方弹药（诊断） | 拷贝列表 |
| `bare_contacts()` | `[dict, …]` | 看见了但没朝任何人飞的弹（诊断：看漏了什么） | 遍历一次 |
| `status()` | `dict` | 周期数、本方/弹药/被瞄准计数、当前门限 | 0 |

`route()` 的 `category` 别名：
`'air'|'aircraft'` → 空，`'sea'|'ship'|'submarine'` → 海（舰+潜合并），`'land'|'facility'` → 陆。

---

## 3. `threats_for(guid)` 的字段

```python
# 例：地空导弹连#1 正被 2 枚反辐射弹盯上
[{'id': 'c_near',              # 情报 guid —— 直接当 attack_* / 算方位的 target
  'n':  'AGM-88E AARGM-ER',    # 弹型（情报里的 Name）
  'db': 2056,                  # 弹型 DBID
  'spd': 2963.2,               # 当前弹速 km/h（已从节换算）
  'd':   7.87,                 # 当前弹目距离 km
  'cpa': 2.29,                 # 最近接近距离 km
  'tgo': 6.1},                 # 到最近接近点的时间 s（None = 无航向且算不出）
 {...}]
```

用途分工（这是**刻意的接口分层**，和报告 2.3.1 的结论一致）：

- `incoming()` 只回 **弹型 + 弹速** 两个标量 → 下游用它做**距离判据**，几何自己重算，不依赖监控内部实现；
- `threats_for()` 多给 `id` → 下游**要真发弹、要算规避方向**时必须有情报 guid；
- `d / cpa / tgo` 是**给日志和诊断看的**，规则里别当判据用（报告明确说了下游不要依赖这些）。

---

## 4. 量纲（最容易踩的坑）

| 量 | 单位 | 说明 |
| --- | --- | --- |
| `CurrentSpeed`（平台原始） | **节（海里/小时）** | `entitys/unit.py:88` 注释写明“海里/小时” |
| 本模块所有 `spd` / 弹速 | **km/h** | 入口 `core.use_speed_kmh()` 已 ×1.852 |
| 距离 `d` / `cpa` | km | |
| 时间 `tgo` | 秒 | |
| 坐标 | `(纬度, 经度)` | 与 `plotted_course` 一致 |

> ⚠️ 旧 `Mission_tactics_red._cpa()` 把 `CurrentSpeed` 直接当 km/h 用，几何上偏了 1.852 倍
> （`d0`/掉头距离的门限因此失真）。本模块统一换算，**和报告里 2500 / 1500 km/h 的口径一致**。

---

## 5. 判定规则：「朝我就算」

```
对每个（我方单元, 敌方弹药）:
    t*, cpa = 最近接近点(弹, 单元)        # 相对运动
    if t* > 0:                           # 还在靠近 → 判定为威胁
        记一条：弹型 / 当前弹速 / d / cpa / tgo
```

**默认不设任何门限**（距离、时间、CPA 都不设）：对方弹的射程未知，保险起见放松判据。

三条后果，用之前必须知道：

1. **一枚穿场弹会同时标记航路上它前方的所有单元**。这是保守判据的必然结果，不是 bug。
   **实测数字**（诺曼底2027，红方 138 个单元，场上有 6~31 枚防空导弹在飞）：
   被标记的峰值是 **空 91/91、海 20/20、陆 27/27 —— 全部**。所以：
   - 只做小窗/日志展示 → 可以接受（按 `tgo` 排序，最紧急的在最前面）；
   - 要做决策 → **必须收紧**，推荐 `gate={'cpa_ratio': 0.2}`（CPA ≤ 当前距离 × 0.2，
     即“真朝我这点来”，而不是“朝我这一片来”），或沿用旧口径
     `{'cpa_km': 3, 'max_km': 90, 'tgo_s': 900}`。
2. **对“规避/关机”类动作可能过于敏感**。参考方案 `SamBattalionDefense._threatened()` 的注释里
   记过一个真实缺陷：判据放宽后“只要战场上还有别处的弹在飞（哪怕打的是别人），本营就一直被判定
   为被打，进入规避后**永远不恢复**——实测表现就是地空导弹连一直在逃跑”。
   如果你把监控接到**会改变自身状态**的动作上（关雷达、脱离、返航），**必须自己加一层退出条件**
   （比如“连续 N 周期无威胁才恢复”或“距离 > X km 且 cpa > Y 就恢复”）。
3. 只做**展示**（小窗 / 日志）时不受影响，越敏感越好。

需要收紧时不改代码，构造时传门限即可（三项独立，缺省 0 = 不启用）：

```python
Monitor(self, gate={'cpa_km': 3.0, 'max_km': 90.0, 'tgo_s': 900.0})   # 沿用旧实现口径
Monitor(self, gate={'cpa_ratio': 0.2})                                # 相对门限（推荐用于决策）
self.monitor.gate = {'max_km': 150.0}                                  # 运行中也能改
```

四项门限互相独立，缺省 0 = 不启用：`cpa_km` / `max_km` / `tgo_s` / **`cpa_ratio`**。

---

## 6. 三个典型下游怎么用

### 6.1 地空导弹营（关雷达 + 脱离 + 反打）

```python
self.monitor.ensure(situation, time_elapse)
for guid, b in self.battalions.items():
    if not self.monitor.has_incoming(guid):
        self._radar_on(b); self._attack_best(b)        # 正常值班
        continue
    rows = self.monitor.threats_for(guid)
    top = rows[0]                                      # 最紧迫的那枚
    contact = self._contact_by_id(top['id'])           # 情报 guid → 拿坐标
    brg = bearing(contact, b)                          # 来袭方位
    self._evade_away_from(b, brg)                      # 背对它脱离
    self._radar_off(b)                                 # 关雷达（反辐射弹的解法）
```
注意“连续 N 周期无威胁才恢复”，见 §5 第 2 条。

### 6.2 空战单元自卫（掉头/正横的触发条件）

```python
self.monitor.ensure(situation, time_elapse)
for guid, ac in self.aircrafts.items():
    hit = self.monitor.incoming(guid)                  # (弹型, 弹速km/h) 或 None
    if hit is None:
        continue
    _, v = hit
    d_turn = 1.2 * self.d0(v, my_speed)                # 门限自己按弹速算
    if self.distance_to_threat(guid) <= d_turn:
        self.beam_or_away(ac)
```

### 6.3 登陆船只集群自卫（选拦截顺序）

```python
self.monitor.ensure(situation, time_elapse)
targets = [r for r in self.monitor.rows()
           if r['g'] == 'sea' and r['hit'] and r['id'] in self.my_ships]
targets.sort(key=lambda r: (r['ms'][0]['tgo'] if r['ms'][0]['tgo'] is not None else 1e9))
for r in targets[:3]:                                  # 最危险的三艘优先
    self.assign_interceptor(r['id'], r['ms'][0])
```

---

## 7. 注意事项清单

1. **`ensure()` 是幂等的**，多个下游共用一个 `Monitor` 实例各调一次不会重复算；传了新的
   `time_elapse` 才会重算。别自己在 `step` 里再调 `step()`。
2. **不要叠加自己的几何兜底**。参考方案里写得很明白：有监控时以监控为唯一判据，否则
   “附近有弹就算被打”会让单元永远出不来。只有在 `self.monitor is None`（没装组件）时才退回自判。
3. **`ready` 要先判**。开局第一个周期可能还没本方单位清单。
4. **只读**。本组件不下发任何指令，也不占用指令配额，可以放心每周期调。
5. **`id` 是情报 guid**，不是单元 guid。要发弹、要算方位都用它去 `self.Contacts` 里反查。
6. 性能：`单元数 × 弹数` 次 CPA，单次约 10 µs；200 单元 × 60 枚 ≈ 2.2 ms。
7. `rows()` / `threats_for()` / `incoming_list()` / `missiles()` 返回的都是**只读副本**，
   你可以随便截断/改写（小窗就靠这个限宽），不会影响监控内部状态。
8. `ensure()` 的判断依据是**推演时刻**，不是你传的 `situation` 对象身份——因为平台的
   `Player.get_situation()` 会把同一个 tuple 缓存复用，靠身份判断会让监控永久停更。
9. **平台的“告警”情报也算 Type=1**。实测会出现 `防空导弹#40`（真弹，db=890）和
   `警告来袭#70` 两族条目。若确认重复，设 `Monitor.IGNORE_NAME_KEYS = ('警告来袭',)` 剔除。
10. **速度恒为 0 的情报不是弹**。`MIN_MISSILE_KMH = 50`（约 27 节）以下一律丢弃——
    实测平台会混进速度 0 的杂项，若不挡会让 `tgo` 失真、把军舰当弹。
11. **弹名可能缺失**：`incoming()` / `incoming_list()` 依次退 `Name → 弹<DBID> → 未知弹`，
    所以下游不要假设名字一定可读。

---

## 8. 验收怎么跑

```bash
python selftest_core.py     # 31 项：几何判定、量纲、分组、排序、兜底、可选门限、弹药识别
python selftest_api.py      # 43 项：上面每个 API 的行为 + 三个下游用法 + ensure 幂等 + 忽略名单
```

另外 `monitor-agent/` 已在**无头引擎**里跑过真实对局（见 `README.md` §4.5 的实测表：
138 个单元、峰值 31 枚弹、弹速 352–4908 km/h、小窗单帧 79 KB）。

两个都不需要灵弈平台、不需要 Windows（纯 Python 3.9+）。
