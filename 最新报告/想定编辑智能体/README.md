# 想定编辑智能体（Scenario Editing Agent）

把「中文作战场景描述」变成「灵弈平台可加载、可推演、可批量派生的想定（`.scen`）」，
并给出**可审计的证据链**：规格 JSON → Lua 脚本 → 引擎回读 → 17 项验收 → 冒烟推演。

```
自然语言 ──► 想定规格(IR) ──► Lua 脚本 ──► 无头引擎(gRPC) ──► .scen ──► 回读验收/冒烟
                                                                           │
                                        同一份规格 ──► 变量轴取样 ──► 同类想定族
```

## 文档

| 文档 | 内容 |
| --- | --- |
| [`docs/想定编辑智能体-设计文档.md`](docs/想定编辑智能体-设计文档.md) | 架构、IR、解析器、Lua 生成、执行、验收、族生成、工程取舍 |
| [`docs/无头Lua建想定方法手册.md`](docs/无头Lua建想定方法手册.md) | 无头模式下用 Lua 建想定的完整方法 + 22 条实测坑表 |
| [`docs/实验报告.md`](docs/实验报告.md) | 8 条自然语言 → 8 份想定、12 变体族、诺曼底复刻族，全部带验收与冒烟数据 |

## 快速开始

```bash
# 0) 依赖（控制端）
uv venv .venv && uv pip install -r requirements.txt
#    如需重新生成 gRPC 桩：
#    .venv/bin/python -m grpc_tools.protoc -I sce_agent/proto \
#        --python_out=sce_agent/gen --grpc_python_out=sce_agent/gen \
#        sce_agent/proto/ServerInterface.proto

# 1) 靶机上的无头引擎（需要 Session 1 交互式桌面；由计划任务投递）
python cli.py engine status
python cli.py engine start            # ~7 s 后 21005 开始监听

# 2) 自然语言 → 想定（解析 → 生成 Lua → 建想定 → 回读验收 → 冒烟推演）
python cli.py nl examples/nl/01-东海反舰遭遇战.md --build --smoke

# 3) 规格 → 同类想定族（3 个变量轴的网格）
python cli.py family out/EXP1-东海反舰遭遇战/spec.json \
    --axis force_scale=0.5,1,2 --axis rotate=0,45 --axis seastate=2,5

# 4) 既有想定 → 同类想定族
python cli.py family-from-scen '诺曼底2027(人机协同-人机版V0.2.7)' --axis force_scale=0.5,1,2

# 5) 批量跑一组自然语言
python cli.py batch 'examples/nl/*.md' --prefix EXP1- --smoke
```

产物在 `out/<想定名>/`：`spec.json`（规格）、`scenario.lua`（脚本）、`build.json`（逐条执行记录）、
`digest.json`（引擎回读摘要）、`verify.md`（验收报告）。

## 目录

```
cli.py                 命令行入口
sce_agent/
  lyclient.py          gRPC 客户端（executeLua + 命名 RPC）
  engine.py            无头引擎起停（计划任务 Interactive 投递）
  spec.py              想定规格 IR + 校验 + 几何算子
  catalog.py           平台词表 / DB 目录 / 挂载方案 / 战区 / 任务类型
  nlu.py               自然语言 → 规格（规则解析器；可选 LLM 通道）
  lua_gen.py           规格 → Lua（分块 + 自包含）
  builder.py           建想定流水线（执行/抓 GUID/落盘/回读/验收/归档）
  digest.py            .scen XML → 结构化摘要
  verify.py            17 项验收
  family.py            同类想定族（变量轴 + 既有想定复刻）
  smoke.py             冒烟推演（官方 Deduction，跑 N 步）
  data/                aliases.json / db_catalog.json / loadouts.json
  proto/ gen/          ServerInterface.proto 与 protoc 产物
examples/nl/           实验用的 8 条自然语言
docs/                  设计文档 / 方法手册 / 实验报告
out/                   每次构建与族实验的产物
```

## 环境约束（踩过的坑，详见方法手册）

* 引擎 `Plat.exe` 是 Qt 程序，**必须在 Session 1**（交互式桌面）里起，否则进程在但永远不监听；
* 用 12 参数形态 `<guid> 127.0.0.1 <rpc> <dds> 0 127.0.0.1 0 0 127.0.0.1 0 "" <room>`，
  官方 `run.bat` 的 11 参数形态会挂住；
* `executeLua` **只把字符串返回值带回来**（原生值/Lua 表都是空串）→ 结构化查询走命名 RPC；
* 飞机必须带 `loadoutid`，且 `loadoutid=0` 的飞机进不了任务（用 `3` 兜底）；
* **不要下发 `STARTTIME`**（会把推演时钟搞坏，第 1 步就结束）；
* 官方框架跑推演时会清理所有 `Plat.exe`，所以「建想定」与「冒烟」要串行（CLI 已自动化）。
