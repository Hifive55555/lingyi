#!/usr/bin/env python3
"""roundtrip.py — 用「日文枢纽」往返翻译把 main.typ 的中文正文洗一遍。

方法出自 arXiv 2610.29162（round-trip translation / bilingual pivoting）：
小模型先把句子译成日语，再译回中文；语义不变、措辞被替换，
AI 文本的特征句法（低频 n-gram、长依存、名词堆叠等）会被压平。

只替换「中文正文」，Typst 结构（数学、代码、引用、表格骨架）原样保留：
  - 内联数学 $...$、行内代码 `...` 用占位符 ⟦N⟧ 保护
  - 表格/图表/标题/字符串等结构元素完全不进入翻译单元

用法:
  python3 roundtrip.py extract          # 只做切分，打印统计
  python3 roundtrip.py translate        # 切分 + 往返翻译（带磁盘缓存，可断点续跑）
  python3 roundtrip.py apply            # 用缓存结果改写 main.typ
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import hashlib
import random
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / "paper"
CACHE = PAPER / ".roundtrip" / "cache.json"
LOG = PAPER / ".roundtrip" / "units.json"


def target_files(extra=None):
    """要处理的 .typ 文件。默认跟随文稿结构：有 verify/ 就处理 verify 全套。"""
    if extra:
        return [Path(x) for x in extra]
    verify = PAPER / "verify"
    if (verify / "main.typ").exists():
        cands = [verify / "main.typ"] + sorted((verify / "sections").glob("*.typ"))
    else:
        cands = [PAPER / "main.typ"]
    return [c for c in cands if c.exists()]

AUTH = Path.home() / ".pi" / "agent" / "auth.json"

# ---------------------------------------------------------------- 服务商
# 默认走 SiliconFlow（api.siliconflow.cn，OpenAI 兼容协议）：
# 官方规则是 ≤9B 参数的模型永久免费，因此用小模型做「日文枢纽」往返翻译。
BASE = os.environ.get("SILICONFLOW_BASE", "https://api.siliconflow.cn/v1").rstrip("/")
API = BASE + "/chat/completions"

# 免费池（参数 ≤9B）。Hunyuan-MT-7B 是专门的机器翻译模型（对应论文里的 NLLB-200），
# 只用它做往返翻译；另外两个通用小模型作备胎。
MODELS = [
    "tencent/Hunyuan-MT-7B",
    "THUDM/GLM-4-9B-0414",
    "Qwen/Qwen3-8B",
]
MT_MODELS = ("hunyuan-mt",)

MT_JA = "Translate the following segment into Japanese, without additional explanation.\n\n"
MT_ZH = "Translate the following segment into Simplified Chinese, without additional explanation.\n\n"

GLOSSARY = (
    "术语表（往返翻译时保持一致）：战术智能体=tactical agent，兵棋推演=wargame simulation，"
    "临界距离=critical distance，尾追=tail chase，迎头=head-on，掉头=turn away，"
    "垂直扭动=vertical weave，弹速=missile speed，拦截率=interception rate，"
    "受控对比=controlled comparison，蒙特卡洛=Monte Carlo，灵敏度/敏感性=sensitivity，"
    "裕度=margin，杀伤概率=kill probability，弹舱=magazine，雷达=radar，加力=afterburner。"
)

SYS_JA = (
    "You are a professional Chinese-to-Japanese translator working on a military operations-research paper. "
    "Translate faithfully, in natural written Japanese, keeping the technical meaning exact. "
    "Rules: (1) Keep every placeholder token of the form ⟦0⟧, ⟦1⟧ … exactly as-is, in the same order. "
    "(2) Keep all numbers, units, model names and code identifiers unchanged. "
    "(3) Keep the same sentence structure and information; do not add or explain anything. "
    "(4) Output ONLY the translation, no notes, no quotes. " + GLOSSARY
)

SYS_ZH = (
    "You are a professional Japanese-to-Chinese translator. Translate the text into natural, plain Simplified Chinese "
    "(the register of a Chinese engineering report; avoid translationese and avoid ornate wording). "
    "Rules: (1) Keep every placeholder token of the form ⟦0⟧, ⟦1⟧ … exactly as-is, in the same order. "
    "(2) Keep all numbers, units, model names and code identifiers unchanged. "
    "(3) Keep the same meaning and the same amount of information; do not add or explain anything. "
    "(4) Output ONLY the translation, no notes, no quotes. " + GLOSSARY
)

# ---------------------------------------------------------------- 切分

HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LABEL = re.compile(r"<[A-Za-z][A-Za-z0-9:_.\-]*>")
REF = re.compile(r"@[A-Za-z][A-Za-z0-9:_.\-]*")
TECH = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./:][A-Za-z0-9]+)*[A-Za-z0-9]|[A-Za-z][A-Za-z0-9]")
NUM = re.compile(r"\d+(?:\.\d+)?")
PH = re.compile(r"⟦\s*(\d+)\s*⟧")
KANA = re.compile(r"[\u3040-\u30ff]")


def piece_scan(s: str):
    """把源文件切成 ('S'|'P'|'T', start, end) 三类片段。
    S = 结构（保持原样，不进翻译）；P = 内联保护块（进单元但用占位符）；T = 正文文本。
    """
    n = len(s)
    out = []
    i = 0
    line_start = True
    text_start = None

    def flush(j):
        nonlocal text_start
        if text_start is not None:
            out.append(("T", text_start, j))
            text_start = None

    while i < n:
        c = s[i]
        j = None
        kind = None

        if c == "\n":
            if text_start is not None:
                out.append(("T", text_start, i + 1))
                text_start = None
            line_start = True
            i += 1
            continue

        # ---- 行首标记：标题 = / == ，列表 - + ，# 命令行
        if line_start:
            line_start = False
            m = re.match(r"=+ ", s[i:])
            if m:
                out.append(("S", i, i + m.end()))
                i += m.end()
                continue
            if c in "-+" and s[i + 1 : i + 2] == " ":
                out.append(("S", i, i + 2))
                i += 2
                line_start = False
                continue

        if s.startswith("//", i):
            flush(i)
            j = s.find("\n", i)
            j = n if j < 0 else j
            out.append(("S", i, j))
            i = j
            continue
        if s.startswith("/*", i):
            flush(i)
            j = s.find("*/", i)
            j = n if j < 0 else j + 2
            out.append(("S", i, j))
            i = j
            continue
        if s.startswith("```", i):
            flush(i)
            j = s.find("```", i + 3)
            j = n if j < 0 else j + 3
            out.append(("S", i, j))
            i = j
            continue
        if c == "`":
            flush(i)
            m = re.match(r"`+", s[i:])
            tick = m.group(0)
            j = s.find(tick, i + len(tick))
            j = n if j < 0 else j + len(tick)
            out.append(("P", i, j))
            i = j
            continue
        if c == "$":
            flush(i)
            j = i + 1
            while j < n:
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == "$":
                    j += 1
                    break
                j += 1
            out.append(("P", i, j))
            i = j
            continue
        if c == '"':
            flush(i)
            j = i + 1
            while j < n:
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == '"':
                    j += 1
                    break
                j += 1
            out.append(("S", i, j))
            i = j
            continue
        if c == "#":
            flush(i)
            j = s.find("\n", i)
            j = n if j < 0 else j
            out.append(("S", i, j))
            i = j
            continue
        if c in "[]":
            flush(i)
            out.append(("S", i, i + 1))
            i += 1
            continue
        if c == "<":
            m = LABEL.match(s, i)
            if m:
                flush(i)
                out.append(("S", i, m.end()))
                i = m.end()
                continue
        if c == "@":
            m = REF.match(s, i)
            if m:
                flush(i)
                out.append(("P", i, m.end()))
                i = m.end()
                continue
        if c == "\\":
            flush(i)
            out.append(("S", i, i + 2))
            i += 2
            continue

        if text_start is None:
            text_start = i
        i += 1

    flush(n)
    return out


def build_units(s: str):
    """把 P/T 片段合并成翻译单元；返回 [(start, end, template, tokens)]。"""
    pieces = piece_scan(s)
    units = []
    cur = []  # 待合并片段

    def close():
        nonlocal cur
        if not cur:
            return
        a, b = cur[0][1], cur[-1][2]
        cur = []
        if not HAN.search(s[a:b]):
            return
        # 去首尾空白
        while a < b and s[a] in " \t\n\r":
            a += 1
        while b > a and s[b - 1] in " \t\n\r":
            b -= 1
        if a >= b:
            return
        units.append((a, b))

    for kind, a, b in pieces:
        if kind == "S":
            close()
        else:
            cur.append((kind, a, b))
    close()

    out = []
    for a, b in units:
        # 重建模板，把 P 片段换成占位符
        tpl, toks = [], []
        pos = a
        for kind, pa, pb in [p for p in pieces if p[0] == "P" and p[1] >= a and p[2] <= b]:
            tpl.append(s[pos:pa])
            toks.append(s[pa:pb])
            tpl.append("⟦%d⟧" % (len(toks) - 1))
            pos = pb
        tpl.append(s[pos:b])
        out.append((a, b, "".join(tpl), toks))
    return out, pieces


# ---------------------------------------------------------------- 模型调用

def _load_key() -> str:
    for env in ("SILICONFLOW_CN_API_KEY", "SILICONFLOW_API_KEY", "SILICONFLOW_KEY"):
        if os.environ.get(env):
            return os.environ[env].strip()
    try:
        d = json.loads(AUTH.read_text())
    except Exception:  # noqa: BLE001
        d = {}
    for prov in ("siliconflow", "siliconflow-cn"):
        if isinstance(d.get(prov), dict) and d[prov].get("key"):
            return d[prov]["key"]
    raise SystemExit(
        "缺少 SiliconFlow API key：请设置环境变量 SILICONFLOW_CN_API_KEY，"
        "或写入 ~/.pi/agent/auth.json 的 {\"siliconflow\": {\"type\":\"api_key\",\"key\":\"sk-...\"}}"
    )


KEY = _load_key()
_lock = threading.Lock()
_model_fail = {m: 0 for m in MODELS}


def _post(model, system, user, temperature=0.3, max_tokens=4000, timeout=180):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": user})
    body = json.dumps(
        {
            "model": model,
            "messages": msgs,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
    ).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    if isinstance(d, dict) and d.get("code") and not d.get("choices"):
        raise RuntimeError(f"api error {d.get('code')}: {d.get('message')}")
    ch = d["choices"][0]["message"] or {}
    return ch.get("content")


def _messages(model: str, direction: str, text: str):
    """Hunyuan-MT 是专用翻译模型，用它自带的 MT 指令格式；其余用通用 system prompt。"""
    if any(k in model.lower() for k in MT_MODELS):
        return None, (MT_JA if direction == "ja" else MT_ZH) + text
    system = SYS_JA if direction == "ja" else SYS_ZH
    label = "Chinese" if direction == "ja" else "Japanese"
    return system, f"Text to translate from {label}:\n\n{text}"


def call(direction, text, tries=6, temperature=0.3, max_tokens=4000):
    """按模型优先级调用；限流/空回复/报错则换下一个模型并退避重试。"""
    err = None
    for k in range(tries):
        with _lock:
            model = sorted(MODELS, key=lambda m: (_model_fail[m], MODELS.index(m)))[0]
        system, user = _messages(model, direction, text)
        try:
            out = _post(model, system, user, temperature=temperature, max_tokens=max_tokens)
            if out and out.strip():
                with _lock:
                    _model_fail[model] = max(0, _model_fail[model] - 1)
                return out.strip(), model
            err = "empty"
            with _lock:
                _model_fail[model] += 1
        except urllib.error.HTTPError as e:
            err = f"HTTP{e.code}"
            with _lock:
                _model_fail[model] += 1 if e.code == 429 else 3
            if e.code == 429:
                time.sleep(min(2 + k * 2, 12))
                continue
            continue
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
            with _lock:
                _model_fail[model] += 1
        time.sleep(min(1 + k, 8))
    raise RuntimeError(f"all attempts failed: {err}")


# ---------------------------------------------------------------- 校验

def strip_ph(t):
    return PH.sub("", t)


def norm_ws(t):
    return re.sub(r"\s+", "", t)


def check(chunk, out, direction):
    """返回 (ok, reason)。"""
    ph_in = PH.findall(chunk)
    ph_out = PH.findall(out)
    if ph_in != ph_out:
        return False, f"placeholders {ph_in} -> {ph_out}"
    if chunk.count("*") != out.count("*"):
        return False, "asterisk count changed"
    d_in = sorted(NUM.findall(chunk))
    d_out = sorted(NUM.findall(out))
    if d_in != d_out:
        return False, f"numbers changed: {set(d_in) ^ set(d_out)}"
    # 技术词（英文/型号）应当保留
    t_in = sorted(t.upper() for t in TECH.findall(strip_ph(chunk)))
    t_out = sorted(t.upper() for t in TECH.findall(strip_ph(out)))
    if t_in != t_out:
        missing = [t for t in t_in if t not in t_out]
        extra = [t for t in t_out if t not in t_in]
        return False, f"terms changed missing={missing[:6]} extra={extra[:6]}"
    if direction == "ja":
        if len(KANA.findall(out)) < 0.15 * len(HAN.findall(chunk) or "x"):
            return False, "not japanese"
        if HAN.search(strip_ph(out)) and len(KANA.findall(out)) > 0 and out.count("。") / max(1, len(out)) > 0.2:
            pass
    else:
        if not HAN.search(out):
            return False, "not chinese"
        if len(KANA.findall(out)) > 2:
            return False, "kana left in chinese"
    r = len(norm_ws(out)) / max(1, len(norm_ws(chunk)))
    if direction == "ja" and not (0.6 < r < 2.6):
        return False, f"length ratio {r:.2f}"
    if direction == "zh" and not (0.4 < r < 2.2):
        return False, f"length ratio {r:.2f}"
    return True, ""


def clean(t):
    t = t.strip()
    t = re.sub(r"^```[a-z]*\n?", "", t)
    t = re.sub(r"\n?```$", "", t)
    t = t.strip().strip('"').strip()
    return t


def translate(text, direction, deep=0):
    for attempt in range(5):
        temp = 0.2 + 0.15 * attempt
        try:
            out, model = call(direction, text, temperature=min(temp, 0.9),
                              max_tokens=min(6000, 800 + 4 * len(text)))
        except RuntimeError:
            if attempt == 4:
                raise
            time.sleep(3)
            continue
        out = clean(out)
        ok, why = check(text, out, direction)
        if ok:
            return out, model
        last = why
        time.sleep(0.5)
    if deep < 2:
        # 退化路径：按中文句读切碎分段翻译，再拼回去
        parts = re.split(r"(?<=[。！？；])", text)
        parts = [p for p in parts if p.strip()]
        outs = []
        for p in parts:
            o, _m = translate(p, direction, deep + 1)
            outs.append(o)
        cand = "".join(outs)
        ok, why = check(text, cand, direction)
        if ok:
            return cand, "fragment-fallback"
    raise RuntimeError(f"validation failed: {last} :: {text[:80]!r}")


# ---------------------------------------------------------------- 主流程

def key_of(text, direction):
    return hashlib.sha1((direction + "\x00" + text).encode()).hexdigest()[:16]


def load_json(p, default):
    if p.exists():
        return json.loads(p.read_text())
    return default


def save_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1))
    tmp.replace(p)


def _units_of(path):
    s = path.read_text()
    units, pieces = build_units(s)
    return s, units, pieces


def cmd_extract():
    files = target_files(sys.argv[2:])
    total_u = total_c = total_h = total_tok = 0
    for path in files:
        s, units, pieces = _units_of(path)
        kinds = {}
        for k, a, b in pieces:
            kinds[k] = kinds.get(k, 0) + 1
        han = len(HAN.findall(s))
        cov = sum(len(HAN.findall(u[2])) for u in units)
        sizes = sorted(len(u[2]) for u in units) or [0]
        print(f"{path}: chars={len(s)} han={han} units={len(units)} "
              f"han-in-units={cov} tokens={sum(len(u[3]) for u in units)} "
              f"size min/med/max={sizes[0]}/{sizes[len(sizes)//2]}/{sizes[-1]}")
        total_u += len(units); total_c += sum(len(u[2]) for u in units)
        total_h += han; total_tok += sum(len(u[3]) for u in units)
    print(f"TOTAL files={len(files)} units={total_u} unit-chars={total_c} han={total_h} tokens={total_tok}")
    return files


def cmd_translate():
    files = cmd_extract()
    cache = load_json(CACHE, {})
    seen = set()
    for path in files:
        s, units, _ = _units_of(path)
        todo = [u for u in units if key_of(u[2], "zh") not in cache and u[2] not in seen]
        print(f"\n== {path.name}: {len(units)} units, {len(units)-len(todo)} cached, {len(todo)} to do")
        for idx, (a, b, tpl, toks) in enumerate(todo, 1):
            seen.add(tpl)
            t0 = time.time()
            ja, m1 = translate(tpl, "ja")
            back, m2 = translate(ja, "zh")
            rec = {"src": tpl, "tokens": toks, "ja": ja, "zh": back,
                   "model_ja": m1, "model_zh": m2}
            cache[key_of(tpl, "zh")] = rec
            cache[key_of(tpl, "ja")] = rec
            save_json(CACHE, cache)
            print(f"[{idx}/{len(todo)}] {time.time()-t0:5.1f}s {len(tpl):4d}->{len(back):4d} {tpl[:30]!r}", flush=True)
    print("\ncache:", CACHE)


def cmd_apply(*args):
    files = target_files(list(args))
    cache = load_json(CACHE, {})
    for path in files:
        s, units, _ = _units_of(path)
        chunks, pos = [], 0
        done = fail = 0
        for a, b, tpl, toks in units:
            rec = cache.get(key_of(tpl, "zh"))
            if not rec:
                fail += 1
                continue
            zh = rec["zh"]

            def rep(m, toks=toks):
                i = int(m.group(1))
                return toks[i] if i < len(toks) else ""

            zh = PH.sub(rep, zh)
            chunks.append(s[pos:a]); chunks.append(zh); pos = b
            done += 1
        chunks.append(s[pos:])
        bak = path.with_suffix(path.suffix + ".pre-roundtrip")
        if not bak.exists():
            bak.write_text(s)
        path.write_text("".join(chunks))
        print(f"applied {done}/{len(units)} units ({fail} missing) -> {path}  (backup: {bak.name})")


def cmd_probe():
    """连通性 / 模型可用性 / 单段往返质量的最小测试。"""
    print(f"base = {BASE}")
    try:
        req = urllib.request.Request(BASE + "/models", headers={"Authorization": f"Bearer {KEY}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        ids = [m["id"] for m in d.get("data", [])]
        print(f"models = {len(ids)}")
        small = [i for i in ids if any(k in i.lower() for k in
                 ("7b", "8b", "9b", "4b", "3b", "2b", "1.7b", "1.5b", "0.6b", "0.5b"))]
        print("候选小模型(" + str(len(small)) + "):")
        for i in small:
            print("   ", i, "<-- 池内" if i in MODELS else "")
    except Exception as e:  # noqa: BLE001
        print("models 列表拉取失败:", type(e).__name__, e)

    path = target_files()[0]
    s, units, _ = _units_of(path)
    sample = max(units, key=lambda u: len(u[2]))
    print("target:", path)
    print(f"\nsample unit ({len(sample[2])} chars):\n{sample[2][:300]}\n")
    t0 = time.time()
    ja, m1 = translate(sample[2], "ja")
    t1 = time.time()
    back, m2 = translate(ja, "zh")
    t2 = time.time()
    print(f"JA ({m1}, {t1-t0:.1f}s):\n{ja}\n")
    print(f"ZH ({m2}, {t2-t1:.1f}s):\n{back}\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if cmd == "extract":
        cmd_extract()
    elif cmd == "probe":
        cmd_probe()
    elif cmd == "translate":
        cmd_translate()
    elif cmd == "apply":
        cmd_apply(*sys.argv[2:])
    else:
        raise SystemExit("usage: roundtrip.py [extract|probe|translate|apply [outfile]]")
