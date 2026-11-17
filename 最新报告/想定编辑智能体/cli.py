# -*- coding: utf-8 -*-
"""想定编辑智能体命令行。

典型用法
--------
    # 0) 引擎（靶机上无头拉起，Session 1 由计划任务保证）
    python cli.py engine status
    python cli.py engine start --port 21005

    # 1) 平台知识库
    python cli.py catalog search 052D
    python cli.py catalog verify            # 用引擎复核词表里所有 dbid
    python cli.py catalog scan              # 全量扫描引擎 DB（~100 秒）

    # 2) 自然语言 -> 想定（一步到位：解析 / 生成 Lua / 建想定 / 回读 / 验收）
    python cli.py nl examples/nl/01-东海反舰.md --build --smoke

    # 3) 只解析（看它"听懂了什么"）
    python cli.py nl "……" --explain

    # 4) 规格 -> 想定
    python cli.py build out/AGENT-xxx/spec.json --name my-scen --smoke

    # 5) 同类想定集
    python cli.py family out/AGENT-xxx/spec.json \
        --axis force_scale=0.5,1.0,2.0 --axis rotate=0,45 --axis seastate=2,5
    python cli.py family-from-scen "海洋空战" --axis force_scale=0.5,1,2 --n 6

    # 6) 冒烟（把已有想定真的跑 N 步）
    python cli.py smoke AGENT-donghai-1 --steps 40
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sce_agent import (Builder, Catalog, LuaClient, LuaError, Report,  # noqa: E402
                       RuleParser, ScenarioSpec, SpecError, digest_summary,
                       generate, parse, parse_scenario_xml, verify)
from sce_agent.engine import EngineManager, Target  # noqa: E402
from sce_agent.family import (AXES, AXIS_HELP, family_manifest,  # noqa: E402
                              make_variants, spec_from_digest)
from sce_agent.smoke import SmokeRunner  # noqa: E402

DEFAULT_PORT = int(os.environ.get("SCE_PORT", "21005"))
SCEN_DIR = os.environ.get("SCE_SCEN_DIR", "D:/LingYi/Data/Scenarios")


# ---------------------------------------------------------------- 公共
def log(msg: str):
    print(msg, flush=True)


def connect(args, start=True):
    t = Target()
    port = args.port
    if start and not t.listening(port):
        log("· 引擎未监听 %d，正在靶机上无头拉起……" % port)
        m = EngineManager(t, port=port, dds_port=port + 1000, room="sce-agent")
        info = m.start(wait=150)
        log("· 引擎就绪 pid=%s（%.1fs）" % (info.pid, time.time() - info.started_at))
    c = LuaClient(t.host, port, timeout=args.timeout)
    ok, ver = c.ping()
    if not ok:
        raise SystemExit("引擎 %s:%d 不可用：%s" % (t.host, port, ver))
    log("· 已连接引擎 %s:%d（build %s）" % (t.host, port, ver))
    return c, t


def load_text(path_or_text: str) -> str:
    if os.path.exists(path_or_text):
        return open(path_or_text, encoding="utf-8").read()
    return path_or_text


def print_report(rep: Report, title="验收"):
    log(rep.to_markdown(title))
    if not rep.ok:
        log("!! 有 %d 项未通过" % len(rep.failed))


def show_parse(pr, brief=False):
    log("== 自然语言解析（%d 条留痕）==" % len(pr.log))
    if not brief:
        for line in pr.log:
            log("   - " + line)
    if pr.unparsed:
        log("== 没听懂的部分 ==")
        for u in pr.unparsed:
            log("   ? " + u)
    spec = pr.spec
    log("== 规格摘要 ==")
    log("   标题：%s｜时长 %d 秒｜复杂度 %d｜难度 %d"
        % (spec.title, spec.duration_s, spec.complexity, spec.difficulty))
    log("   中心：(%.3f, %.3f)｜推演方：%s" % (spec.center["lat"], spec.center["lon"],
                                            "/".join(spec.side_names())))
    for name, kinds in spec.counts().items():
        log("   %s 兵力：%s" % (name, ", ".join("%s=%d" % (k, v) for k, v in kinds.items() if v)))
    for m in spec.missions:
        log("   任务 %s（%s/%s）区 %d 点，%d 个单元"
            % (m.name, m.mtype, m.subtype, len(m.zone), len(m.units)))


# ---------------------------------------------------------------- engine
def cmd_engine(args):
    t = Target()
    if args.action == "status":
        log("靶机 %s：Session1=%s，Plat 进程=%s，监听 %d=%s，监听 21001=%s"
            % (t.host, t.session_ok(), t.find_plat_pids(), args.port,
               t.listening(args.port), t.listening(21001)))
        return
    if args.action == "stop-all":
        EngineManager.stop_all(t)
        log("已清理全部 Plat.exe")
        return
    m = EngineManager(t, port=args.port, dds_port=args.port + 1000, room="sce-agent")
    if args.action == "start":
        info = m.start(wait=150, force=args.force)
        log("引擎就绪：pid=%s port=%d（%.1fs）" % (info.pid, info.port, time.time() - info.started_at))
    elif args.action == "stop":
        m.stop()
        log("已停止（port %d）" % args.port)
    elif args.action == "log":
        log(m.tail_log(args.lines))


# ---------------------------------------------------------------- catalog
def cmd_catalog(args):
    cat = Catalog()
    if args.action == "search":
        hits = cat.search(args.keyword, args.kind, args.limit)
        if not hits:
            log("没有命中：%r" % args.keyword)
        for p in hits:
            log("  %-10s %6d  %s" % (p.kind, p.dbid, p.klass))
        return
    if args.action == "show":
        for alias, d in sorted(cat.platforms.items()):
            log("  %-12s %-10s %6d  %s" % (alias, d["kind"], d["dbid"], d.get("class", "")))
        return
    if args.action == "verify":
        c, _ = connect(args)
        bad = 0
        for alias, d in sorted(cat.platforms.items()):
            ok, klass = c.query_db(d["kind"], d["dbid"])
            if not ok:
                bad += 1
                log("  BAD  %-12s %-10s %6d  %s" % (alias, d["kind"], d["dbid"], klass[:80]))
        log("共 %d 条别名，失效 %d 条" % (len(cat.platforms), bad))
        return
    if args.action == "scan":
        c, _ = connect(args)
        import concurrent.futures as cf
        ranges = {"ship": args.ship, "aircraft": args.aircraft, "submarine": args.sub,
                  "facility": args.facility, "satellite": 400}
        out = {}
        for kind, n in ranges.items():
            t0 = time.time()
            rows = []

            def one(dbid):
                ok, klass = c.query_db(kind, dbid)
                return dbid, klass if ok else None

            with cf.ThreadPoolExecutor(32) as ex:
                for dbid, klass in ex.map(one, range(1, n + 1), chunksize=32):
                    if klass is not None:
                        rows.append({"dbid": dbid, "class": klass})
            out[kind] = rows
            log("  %-10s 1..%-5d 有效 %-5d %.0fs" % (kind, n, len(rows), time.time() - t0))
        p = os.path.join(HERE, "sce_agent", "data", "db_catalog.json")
        json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        log("已写入 %s（%d 条）" % (p, sum(len(v) for v in out.values())))


# ---------------------------------------------------------------- nl / build
def cmd_nl(args):
    text = load_text(args.text)
    title = args.title or os.path.splitext(os.path.basename(args.text))[0][:40] or "NL想定"
    llm = None
    if args.parser == "llm":
        llm = {"base": os.environ.get("SCE_LLM_BASE", ""),
               "key": os.environ.get("SCE_LLM_KEY", ""),
               "model": os.environ.get("SCE_LLM_MODEL", "")}
    pr = parse(text, parser=args.parser, llm=llm,
               title=("AGENT-" + title if not title.startswith("AGENT-") else title))
    pr.spec.title = args.title or pr.spec.title
    show_parse(pr, brief=not args.explain)
    if args.out:
        pr.spec.to_json(args.out)
        log("· 规格已写入 %s" % args.out)
    for e in pr.spec.validate():
        log("   %s %s" % ("!" if not e.startswith("警告") else "?", e))
    if not (args.build or args.smoke):
        return
    build_and_maybe_smoke(args, pr.spec)


def cmd_build(args):
    spec = ScenarioSpec.from_json(args.spec)
    build_and_maybe_smoke(args, spec)


def build_and_maybe_smoke(args, spec: ScenarioSpec):
    c, t = connect(args)
    b = Builder(c, scen_dir=SCEN_DIR, out_dir=args.out_dir, target=t)
    res = b.build(spec, name=args.name)
    log("== 构建 ==")
    log("   结果：%s｜文件：%s（%d 字节）｜耗时 %.1fs"
        % ("OK" if res.ok else "FAIL", res.scen_path, res.size, res.elapsed))
    if res.error:
        log("   错误：%s" % res.error)
    if res.digest:
        log("   回读：%s" % digest_summary(res.digest))
    if res.report:
        print_report(res.report, "验收报告：%s" % spec.title)
    if args.smoke and res.ok:
        log("== 冒烟推演（官方框架，%d 步）==" % args.steps)
        EngineManager.stop_all(t)      # 框架与建想定引擎互斥，先清干净
        time.sleep(2)
        sr = SmokeRunner(steps=args.steps, decision_interval=args.decision_interval).run(res.name)
        log("   %s｜%s" % ("PASS" if sr.ok else "FAIL",
                          json.dumps(sr.raw or sr.error, ensure_ascii=False)[:400]))
        _append_smoke(res.out_dir, sr)
    return res


def _append_smoke(out_dir: str, sr):
    if not out_dir or not os.path.isdir(out_dir):
        return
    p = os.path.join(out_dir, "smoke.json")
    json.dump(sr.to_dict(), open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- family
def cmd_family(args):
    base = ScenarioSpec.from_json(args.spec)
    axes = _parse_axes(args)
    variants = make_variants(base, axes, n=args.n, seed=args.seed)
    log("== 族定义 ==")
    for k, v in axes.items():
        log("   %s：%s  （%s）" % (k, v, AXIS_HELP.get(k, "")))
    log("   变体数：%d（%s）" % (len(variants), "随机取样 seed=%s" % args.seed if args.n else "网格"))
    _run_family(args, variants, base)


def cmd_family_from_scen(args):
    c, t = connect(args)
    code, xml = c.scenario_content(args.scen if args.scen.endswith(".scen") else args.scen + ".scen")
    if code != 0:
        raise SystemExit("回读失败：%s" % xml[:200])
    digest = parse_scenario_xml(xml)
    log("== 源想定 ==")
    log("   " + digest_summary(digest))
    base = spec_from_digest(digest)
    check = base.validate()
    errs = [e for e in check if not e.startswith("警告")]
    if errs:
        log("   !! 复刻规格有 %d 个问题（前 5 条）：" % len(errs))
        for e in errs[:5]:
            log("      - " + e)
    axes = _parse_axes(args)
    variants = make_variants(base, axes, n=args.n, seed=args.seed)
    log("   变体数：%d" % len(variants))
    _run_family(args, variants, base)


def _parse_axes(args) -> dict:
    axes = {}
    for item in args.axis or []:
        k, _, vals = item.partition("=")
        k = k.strip()
        if k not in AXES:
            raise SystemExit("未知变量轴 %r；可用：%s" % (k, ", ".join(sorted(AXES))))
        parsed = []
        for v in vals.split(","):
            v = v.strip()
            if not v:
                continue
            try:
                parsed.append(int(v))
            except ValueError:
                try:
                    parsed.append(float(v))
                except ValueError:
                    parsed.append(v)
        axes[k] = parsed or [1]
    if not axes:
        axes = {"force_scale": [0.5, 1.0, 2.0], "rotate": [0, 45], "seastate": [2, 5]}
    return axes


def _run_family(args, variants, base):
    only = slice(args.only - 1, args.only) if args.only else None
    if only:
        variants = variants[only]
    c, t = connect(args)
    b = Builder(c, scen_dir=SCEN_DIR, out_dir=args.out_dir, target=t)
    rows = []
    ok_n = 0
    for i, v in enumerate(variants, 1):
        t0 = time.time()
        res = b.build(v.spec, name=v.name)
        ok_n += 1 if res.ok else 0
        log("[%2d/%2d] %-28s %s  %5.1fs  %s"
            % (i, len(variants), v.name, "OK  " if res.ok else "FAIL",
               time.time() - t0,
               digest_summary(res.digest) if res.digest else res.error[:120]))
        row = dict(variant=v.name, ok=res.ok, size=res.size,
                   elapsed=round(res.elapsed, 1),
                   units=len(res.digest["units"]) if res.digest else 0,
                   missions=len(res.digest["missions"]) if res.digest else 0,
                   refpoints=len(res.digest["reference_points"]) if res.digest else 0,
                   passed=res.report.passed if res.report else 0,
                   total=len(res.report.checks) if res.report else 0,
                   error=(res.error or "")[:80])
        row.update({("axis_" + k): str(val) for k, val in v.params.items()})
        rows.append(row)
    out = os.path.join(args.out_dir, "family_%s.csv" % (base.title.replace("/", "-")[:40]))
    os.makedirs(args.out_dir, exist_ok=True)
    family_manifest(out, rows)
    log("== 族结果 ==")
    log("   成功 %d/%d，清单：%s" % (ok_n, len(variants), out))


# ---------------------------------------------------------------- smoke / verify
def cmd_smoke(args):
    t = Target()
    EngineManager.stop_all(t)
    time.sleep(1)
    sr = SmokeRunner(steps=args.steps, decision_interval=args.decision_interval).run(
        args.scen, timeout=args.timeout)
    log("== 冒烟：%s ==" % args.scen)
    log("   %s" % ("PASS" if sr.ok else "FAIL"))
    log("   " + json.dumps(sr.raw or sr.error, ensure_ascii=False)[:1200])
    return 0 if sr.ok else 1


def cmd_verify(args):
    c, _ = connect(args)
    code, xml = c.scenario_content(args.scen if args.scen.endswith(".scen") else args.scen + ".scen")
    if code != 0:
        raise SystemExit("回读失败：%s" % xml[:200])
    digest = parse_scenario_xml(xml)
    log(digest_summary(digest))
    if args.spec:
        spec = ScenarioSpec.from_json(args.spec)
        print_report(verify(spec, digest), "对照验收：%s" % args.scen)
    if args.digest_out:
        json.dump(digest, open(args.digest_out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        log("digest -> %s" % args.digest_out)


def cmd_lua(args):
    # 只编译不下发：不需要引擎，也不需要靶机
    prog_spec = ScenarioSpec.from_json(args.spec)
    prog = generate(prog_spec, args.scen_path)
    if args.emit == "script":
        print(prog.to_text())
    else:
        for b in prog.blocks:
            print("-- == %s" % b.title)
            print(b.code)
            print()


def cmd_batch(args):
    """批量跑一批自然语言文件：解析→建想定→验收→（可选）冒烟。"""
    files = []
    for pat in args.paths:
        files.extend(sorted(glob.glob(pat)) or [pat])
    rows = []
    c, t = connect(args)
    b = Builder(c, scen_dir=SCEN_DIR, out_dir=args.out_dir, target=t)
    log("== 批量：%d 个自然语言输入 ==" % len(files))
    for i, f in enumerate(files, 1):
        text = load_text(f)
        pr = RuleParser().parse(text, default_title="AGENT-" + os.path.splitext(os.path.basename(f))[0])
        spec = pr.spec
        t0 = time.time()
        res = b.build(spec, name=args.prefix + spec.title.replace(" ", "-")[:40])
        log("[%d/%d] %-34s %s %5.1fs %s"
            % (i, len(files), spec.title[:34], "OK  " if res.ok else "FAIL",
               time.time() - t0,
               (digest_summary(res.digest) if res.digest else res.error[:100])))
        rows.append(dict(input=os.path.basename(f), title=spec.title, scen=res.name,
                         ok=res.ok, size=res.size, elapsed=round(res.elapsed, 1),
                         units=len(res.digest["units"]) if res.digest else 0,
                         missions=len(res.digest["missions"]) if res.digest else 0,
                         passed=res.report.passed if res.report else 0,
                         total=len(res.report.checks) if res.report else 0,
                         error=(res.error or "")[:80]))
        if args.smoke:
            EngineManager.stop_all(t)
            time.sleep(1)
            sr = SmokeRunner(steps=args.steps, decision_interval=args.decision_interval).run(res.name)
            rows[-1].update(smoke_ok=sr.ok,
                            smoke_steps=(sr.raw or {}).get("steps", 0),
                            smoke_time=(sr.raw or {}).get("sim_time", 0))
            log("        冒烟：%s（steps=%s sim_time=%s）"
                % ("PASS" if sr.ok else "FAIL", (sr.raw or {}).get("steps"),
                   (sr.raw or {}).get("sim_time")))
            c, t = connect(args)     # 冒烟会杀掉引擎，重新拉起
            b = Builder(c, scen_dir=SCEN_DIR, out_dir=args.out_dir, target=t)
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, "batch.csv")
    family_manifest(out, rows)
    log("== 批量结果：%s ==" % out)


# ---------------------------------------------------------------- argparse
def main(argv=None):
    p = argparse.ArgumentParser(description="想定编辑智能体（灵弈无头建想定）")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help="引擎 RPC 端口（默认 %d）" % DEFAULT_PORT)
    p.add_argument("--timeout", type=float, default=120.0, help="单次 RPC 超时秒")
    p.add_argument("--out-dir", default=os.path.join(HERE, "out"), help="产物目录")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("engine", help="无头引擎的起停/探活")
    e.add_argument("action", choices=["start", "stop", "status", "stop-all", "log"])
    e.add_argument("--force", action="store_true", help="start 时先杀再起")
    e.add_argument("--lines", type=int, default=20)
    e.set_defaults(func=cmd_engine)

    cat = sub.add_parser("catalog", help="平台词表 / DBID 知识库")
    cat.add_argument("action", choices=["search", "show", "verify", "scan"])
    cat.add_argument("keyword", nargs="?", default="")
    cat.add_argument("--kind", default=None, choices=["Ship", "Aircraft", "Submarine", "Facility", "Satellite"])
    cat.add_argument("--limit", type=int, default=20)
    cat.add_argument("--ship", type=int, default=9000)
    cat.add_argument("--aircraft", type=int, default=9000)
    cat.add_argument("--sub", type=int, default=2000)
    cat.add_argument("--facility", type=int, default=4200)
    cat.set_defaults(func=cmd_catalog)

    n = sub.add_parser("nl", help="自然语言 -> 想定规格/想定")
    n.add_argument("text", help="自然语言文本或 .md/.txt 文件")
    n.add_argument("--title", default=None)
    n.add_argument("--parser", default="rule", choices=["rule", "llm"])
    n.add_argument("--explain", action="store_true", help="打印全部解析留痕")
    n.add_argument("-o", "--out", default=None, help="规格 JSON 输出路径")
    n.add_argument("--build", action="store_true")
    n.add_argument("--smoke", action="store_true")
    n.add_argument("--name", default=None)
    n.add_argument("--steps", type=int, default=40)
    n.add_argument("--decision-interval", type=int, default=5)
    n.set_defaults(func=cmd_nl)

    b = sub.add_parser("build", help="规格 JSON -> 想定")
    b.add_argument("spec")
    b.add_argument("--name", default=None)
    b.add_argument("--smoke", action="store_true")
    b.add_argument("--steps", type=int, default=40)
    b.add_argument("--decision-interval", type=int, default=5)
    b.set_defaults(func=cmd_build)

    f = sub.add_parser("family", help="由规格生成同类想定集")
    f.add_argument("spec")
    f.add_argument("--axis", action="append", help="如 force_scale=0.5,1,2")
    f.add_argument("--n", type=int, default=0, help="随机取样个数（0=网格）")
    f.add_argument("--seed", type=int, default=7)
    f.add_argument("--only", type=int, default=0, help="只做网格里的第 N 个变体")
    f.set_defaults(func=cmd_family)

    fs = sub.add_parser("family-from-scen", help="由已有 .scen 复刻并派生同类想定集")
    fs.add_argument("scen")
    fs.add_argument("--axis", action="append")
    fs.add_argument("--n", type=int, default=0)
    fs.add_argument("--seed", type=int, default=7)
    fs.add_argument("--only", type=int, default=0)
    fs.set_defaults(func=cmd_family_from_scen)

    s = sub.add_parser("smoke", help="用官方框架跑 N 步，验证想定真能推演")
    s.add_argument("scen")
    s.add_argument("--steps", type=int, default=40)
    s.add_argument("--decision-interval", type=int, default=5)
    s.add_argument("--timeout", type=float, default=300)
    s.set_defaults(func=cmd_smoke)

    v = sub.add_parser("verify", help="回读想定并与规格比对")
    v.add_argument("scen")
    v.add_argument("--spec", default=None)
    v.add_argument("--digest-out", default=None)
    v.set_defaults(func=cmd_verify)

    l = sub.add_parser("lua", help="只输出 Lua 脚本（不执行）")
    l.add_argument("spec")
    l.add_argument("--scen-path", default="D:/LingYi/Data/Scenarios/out.scen")
    l.add_argument("--emit", default="script", choices=["script", "blocks"])
    l.set_defaults(func=cmd_lua)

    bt = sub.add_parser("batch", help="批量：一组自然语言文件 -> 一组想定")
    bt.add_argument("paths", nargs="+")
    bt.add_argument("--prefix", default="EXP-")
    bt.add_argument("--smoke", action="store_true")
    bt.add_argument("--steps", type=int, default=40)
    bt.add_argument("--decision-interval", type=int, default=5)
    bt.set_defaults(func=cmd_batch)

    args = p.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
