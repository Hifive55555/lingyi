#!/usr/bin/env python
"""论文去 AI 味的「小模型往返翻译」润色器（单文件版，只动纯正文段落）。

流程：中文正文段 →（Hunyuan-MT-7B）日文 →（Hunyuan-MT-7B）回译中文 → 写回镜像文件。
只处理「空行分隔、且不在标题/图注/表格/代码块里」的正文段；
段内的 $数学$、`代码`、@引用、<label>、专名一律换成 ⟦k⟧ 占位符，翻完原样还原。

用法：
  uv run --python 3.14 python scripts/polish.py plan     # 统计要处理哪些段
  uv run --python 3.14 python scripts/polish.py run      # 往返翻译（带缓存，可断点续跑）
  uv run --python 3.14 python scripts/polish.py write    # 写出 paper/design/润色后/main.typ
  uv run --python 3.14 python scripts/polish.py report   # 生成对照 markdown
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
from concurrent import futures
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / "paper"
SRC = PAPER / "design" / "main.typ"
OUTDIR = PAPER / "design" / "润色后"
CACHE = PAPER / ".roundtrip" / "design-cache.json"
REPORT = PAPER / "design" / "润色对照.md"

API = os.environ.get("SILICONFLOW_BASE", "https://api.siliconflow.cn/v1").rstrip("/") + "/chat/completions"
MODEL = os.environ.get("RT_MODEL", "tencent/Hunyuan-MT-7B")
CHAT_MODELS = ["THUDM/GLM-4-9B-0414", "Qwen/Qwen3-8B"]

SYS_HEAD = {
    "ja": "You translate Chinese section headings of a Chinese technical report into Japanese. "
          "Output ONE noun phrase, same length class as the input (usually 4-14 characters), "
          "no ending punctuation, no question marks, no explanation. "
          "Keep placeholder tokens ⟦0⟧ ⟦1⟧ … exactly as-is and in order. "
          "Keep numbers, units and code identifiers unchanged.",
    "zh": "You translate Japanese section headings of a technical report back into Chinese. "
          "Output ONE noun phrase (usually 4-14 characters), no ending punctuation, no question marks, "
          "no explanation, plain written Chinese. Keep placeholder tokens ⟦0⟧ ⟦1⟧ … exactly as-is and in order.",
}
AUTH = Path.home() / ".pi" / "agent" / "auth.json"

MT = {
    "ja": "Translate the following segment into Japanese, without additional explanation.\n\n",
    "zh": "Translate the following segment into Simplified Chinese, without additional explanation.\n\n",
}

# 专名保护表：翻译时换成占位符，回来再原样贴回，杜绝「海马斯→哈马斯」这类乱译
NAMES = [
    # 专名 / 型号 / 编号
    "雷鸣号", "海马斯", "卢卡斯", "霍克导弹", "船坞登陆舰", "苏-57",
    "158C", "154C", "TB3", "ABDE", "23900", "阵风 1", "阵风 2",
    # 五个智能体的固定叫法（避免「物理作战域三维监控」被译成「物理战斗领域…」）
    "物理作战域三维监控", "空战单元自卫", "空空作战", "登陆船只集群自卫",
    "地空导弹营攻击与自卫",
    # 关键术语
    "临界距离", "掉头距离", "分档", "裕度", "包线", "弹速",
]

# 标题里必须原样保留的核心词
EXTRA_TERMS = [
    "闭式解", "数值二分", "受控对比", "蒙特卡洛", "稳健性", "敏感性", "端到端",
    "火力分配", "分层补射", "生存率", "反打率", "拦截率", "命中率", "弹舱",
    "态势", "规则集", "伪代码", "作用空域", "决策域", "观测", "参数", "假设",
    # 全文核心词：标题里一律不许换说法
    "智能体", "掉头", "开火", "拦截距离", "补射", "仿真", "追逃", "查表",
    "引言", "结论", "应用", "局限", "架构", "配置",
]

HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
KANA = re.compile(r"[\u3040-\u30ff]")
NUM = re.compile(r"\d+(?:\.\d+)?")
PH = re.compile(r"⟦\s*(\d+)\s*⟧")
CORE_TOK = r"\$\$?[^$]+\$\$?|`[^`]+`|@[A-Za-z][A-Za-z0-9:_.\-]*|<[A-Za-z][A-Za-z0-9:_.\-]*>|\\[#$%&_*{}]"
TOK = re.compile("|".join([re.escape(n) for n in sorted(NAMES, key=len, reverse=True)] + [CORE_TOK, r"\*"]))

CN_DIGIT = dict(zip("零〇一二两兩三四五六七八九", [0, 0, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 9]))
CN_MULT = {"十": 10, "百": 100, "千": 1000}
CN_RUN = re.compile(r"[零〇一二两兩三四五六七八九十百千万]+")


def parse_cn(t):
    total = section = number = 0
    for ch in t:
        if ch in CN_DIGIT:
            number = CN_DIGIT[ch]
        elif ch in CN_MULT:
            section += (number or 1) * CN_MULT[ch]
            number = 0
        elif ch == "万":
            section = (section + number) * 10000
            total += section
            section = number = 0
    return total + section + number


def kanji_numbers(t):
    return {str(parse_cn(m.group(0))) for m in CN_RUN.finditer(t)}


# ---------------------------------------------------------------- 结构保护 / 切段

def _match_paren(s, i):
    """s[i] == '('，返回配对 ')' 之后的位置。"""
    depth = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '"':
            i += 1
            while i < n and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _match_bracket(s, i):
    depth = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '"':
            i += 1
            while i < n and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def protected_mask(s):
    n = len(s)
    m = bytearray(n)
    spans = []
    for pat, flags in ((r"```.*?```", re.S), (r"(?m)^=+ .*$", 0),
                       (r"(?m)^//.*$", 0), (r"/\*.*?\*/", re.S)):
        for g in re.finditer(pat, s, flags):
            spans.append((g.start(), g.end()))
    # #figure( / #table( / #grid( / #bibliography( … 整块
    for g in re.finditer(r"#(?:figure|table|grid|align|block|text|image|bibliography|set|show|let)\s*\(", s):
        spans.append((g.start(), _match_paren(s, g.end() - 1)))
    # #show: project.with( … ) 这类「带冒号的调用」
    for g in re.finditer(r"(?m)^#\w+:\s*[\w.]+\s*\(", s):
        spans.append((g.start(), _match_paren(s, g.end() - 1)))
    # 其余以 # 开头的命令行
    for g in re.finditer(r"(?m)^#[^\n]*$", s):
        spans.append((g.start(), g.end()))
    # caption: [ … ]
    for g in re.finditer(r"caption\s*:\s*\[", s):
        spans.append((g.start(), _match_bracket(s, g.end() - 1)))
    for a, b in spans:
        m[a:b] = b"\x01" * (b - a)
    return m


def prose_units(s):
    """返回 [(start, end)]：空行分隔、且不含任何结构块的正文段。"""
    prot = protected_mask(s)
    n = len(s)
    units, i = [], 0
    while i < n:
        if prot[i]:
            while i < n and prot[i]:
                i += 1
            continue
        j = i
        while j < n and not prot[j]:
            if s[j] == "\n":
                k = j + 1
                while k < n and s[k] in " \t":
                    k += 1
                if k < n and s[k] == "\n":
                    break
            j += 1
        a, b = i, j
        i = j + 1 if j < n and s[j] == "\n" else j      # 吃掉分隔空行，避免原地打转
        while a < b and s[a] in " \t\n":
            a += 1
        while b > a and s[b - 1] in " \t\n":
            b -= 1
        if b - a > 0 and len(HAN.findall(s[a:b])) >= 12:
            units.append((a, b))
    return units


# ---------------------------------------------------------------- 占位符

TOK_NONAME = re.compile(CORE_TOK + r"|\*")


def templatize(text, names=True, extra=()):
    pat = TOK if names else TOK_NONAME
    if extra:
        pat = re.compile("|".join([re.escape(x) for x in sorted(extra, key=len, reverse=True)] + [pat.pattern]))
    parts, toks, pos = [], [], 0
    for g in pat.finditer(text):
        parts.append(text[pos:g.start()])
        toks.append(g.group(0))
        parts.append("⟦%d⟧" % (len(toks) - 1))
        pos = g.end()
    parts.append(text[pos:])
    return "".join(parts), toks



FILLER = re.compile(
    r"(?:^|[，。；：])\s*(?:从实际情况来看|事实上|值得注意的是|需要注意的是|换句话说|也就是说|"
    r"简而言之|总体而言|总的来说|综上所述|由此可见|不难看出)\s*[，,]?"
)


def tidy(t):
    """去掉回译时模型加的连接词与省略号（不改动实义内容）。"""
    t = FILLER.sub(lambda m: m.group(0)[0] if m.group(0)[0] in "，。；：" else "", t)
    t = t.replace("……", "").replace("⋯⋯", "")
    return t


def fix_refs(tpl, toks, out):
    """@引用后面若紧贴汉字/字母，Typst 会把它算进 label 名；按源文边界补一个空格。"""
    for m in PH.finditer(tpl):
        k = int(m.group(1))
        tok = toks[k] if k < len(toks) else ""
        if not tok.startswith("@"):
            continue
        nxt = tpl[m.end():m.end() + 1]
        if nxt and not re.match(r"[A-Za-z0-9:_.\-]", nxt):
            out = re.sub(re.escape(tok) + r"(?=[A-Za-z0-9\u4e00-\u9fff])", tok + " ", out)
    return out


def restore(tpl, toks):
    return PH.sub(lambda m: toks[int(m.group(1))] if int(m.group(1)) < len(toks) else "", tpl)


# ---------------------------------------------------------------- 模型调用

KEY = None


def _key():
    global KEY
    if KEY:
        return KEY
    for env in ("SILICONFLOW_CN_API_KEY", "SILICONFLOW_API_KEY"):
        if os.environ.get(env):
            KEY = os.environ[env].strip()
            return KEY
    d = json.loads(AUTH.read_text())
    for prov in ("siliconflow", "siliconflow-cn"):
        if isinstance(d.get(prov), dict) and d[prov].get("key"):
            KEY = d[prov]["key"]
            return KEY
    raise SystemExit("缺少 SiliconFlow key")


def call(direction, text, temperature=0.3):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": MT[direction] + text}],
        "temperature": temperature,
        "max_tokens": min(8000, 1200 + 4 * len(text)),
        "stream": False,
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=240) as r:
        d = json.loads(r.read())
    if d.get("code") and not d.get("choices"):
        raise RuntimeError(f"api {d['code']}: {d.get('message')}")
    return (d["choices"][0]["message"].get("content") or "").strip()


def call_chat(direction, text, temperature=0.3):
    """标题用：带 system 指令的小模型（GLM-4-9B / Qwen3-8B，均关思维链）。"""
    msgs = [{"role": "system", "content": SYS_HEAD[direction]},
            {"role": "user", "content": text}]
    last = "?"
    for model in CHAT_MODELS:
        payload = {"model": model, "messages": msgs, "temperature": temperature,
                   "max_tokens": 200, "stream": False}
        if "qwen3" in model.lower():
            payload["enable_thinking"] = False
        req = urllib.request.Request(
            API, data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            out = (d["choices"][0]["message"].get("content") or "").strip()
            if out:
                return out
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
    raise RuntimeError(f"heading call failed: {last}")


def strip_end(t):
    return re.sub(r"[。．.：:；;！!？?、，,\s]+$", "", t).strip()


def check_head(tpl, out, direction, ja=None):
    """ja 侧只管「占位符没丢、没被句子化」；回译成中文那一侧才做严格结构比对。"""
    if PH.findall(tpl) != PH.findall(out):
        return False, "占位符变化"
    a, b = PH.sub("", tpl), PH.sub("", out)
    if "。" in b or "．" in b:
        return False, "标题内出现句号"
    if "第" in b and "第" not in a:
        return False, "加了「第」字（序数被误读）"
    r = len(b) / max(1, len(a))
    if direction == "ja":
        if len(HAN.findall(a)) >= 10 and not KANA.search(b):
            return False, "不像日文"
        if not 0.4 < r < 3.2:
            return False, f"长度比 {r:.2f}"
        return True, ""
    # ---- 以下只对回译中文生效
    if r > 1.8:
        return False, f"长度比 {r:.2f}（被扩写成句子）"
    if not a.count("、") and b.count("、"):
        return False, "多出顿号（并列句化）"
    for ch in "，,；;":
        if ch not in a and ch in b:
            return False, f"多出标点 {ch}（句子化）"
    if ("（" in b or "(" in b) and "（" not in a and "(" not in a:
        return False, "擅自加括号"
    if "了" in b or "→" in b:
        return False, "句子化（了/箭头）"
    if len(HAN.findall(a)) <= 4 and not set(HAN.findall(a)) <= set(HAN.findall(b)):
        return False, "短标题丢了原字"
    ph_s, ph_o = re.findall(r"⟦\d+⟧", tpl), re.findall(r"⟦\d+⟧", out)
    if ph_s:
        if tpl.lstrip().startswith(ph_s[0]) and not out.lstrip().startswith(ph_o[0]):
            return False, "开头的占位符被挪位"
        if re.sub(r"\s+$", "", tpl).endswith(ph_s[-1]) and \
                not re.sub(r"\s+$", "", out).endswith(ph_o[-1]):
            return False, "结尾的占位符被挪位"
    if ja is not None and re.sub(r"[\sの・]", "", KANA.sub("", ja)) == \
            re.sub(r"[\sの・]", "", KANA.sub("", b)):
        return False, "回译等于日文（没翻回来）"
    if not HAN.search(b):
        return False, "不像中文"
    if len([c for c in KANA.findall(b) if c not in "・ー"]) > 0:
        return False, "残留假名"
    return True, ""


def roundtrip_head(tpl, toks):
    """标题往返：名词短语、不带句末标点；不合规就保留原文。"""
    last = "?"
    for attempt in range(3):
        try:
            ja = strip_end(clean(call("ja", tpl, temperature=0.2 + 0.15 * attempt)))
            ok, why = check_head(tpl, ja, "ja")
            if not ok:
                last = f"ja: {why}"
                continue
            zh = strip_end(clean(call("zh", ja, temperature=0.2 + 0.15 * attempt)))
            ok, why = check_head(tpl, zh, "zh", ja=ja)
            if not ok:
                last = f"zh: {why}"
                continue
            return ja, zh, "", "head"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
    return tpl, tpl, last[:60], "keep-original"


def clean(t):
    t = re.sub(r"^```[a-z]*\n?", "", t.strip())
    t = re.sub(r"\n?```$", "", t)
    return t.strip().strip('"').strip()


# ---------------------------------------------------------------- 校验

def check(tpl, out, direction):
    """只允许「不丢东西 + 仍是目标语言 + 长度不失控」。返回 (ok, reason, warn)。"""
    if PH.findall(tpl) != PH.findall(out):
        return False, f"占位符 {PH.findall(tpl)} -> {PH.findall(out)}", ""
    a, b = PH.sub("", tpl), PH.sub("", out)
    lost = set(NUM.findall(a)) - (set(NUM.findall(b)) | kanji_numbers(b))
    if lost:
        return False, f"数字丢失 {sorted(lost)[:5]}", ""
    paren = lambda t: t.count("（") + t.count("(")
    if paren(b) > paren(a):                 # 模型爱加「（即……）」这类自我解释
        return False, "擅自添加括号解释", ""
    warn = ""
    if direction == "ja":
        if len(HAN.findall(a)) >= 6 and len(KANA.findall(b)) < 0.15 * max(1, len(HAN.findall(a))):
            return False, "不像日文", ""
        r = len(b) / max(1, len(a))
        if not 0.5 < r < 3.5:
            return False, f"长度比 {r:.2f}", ""
    else:
        if not HAN.search(b):
            return False, "不像中文", ""
        if len([c for c in KANA.findall(b) if c not in "・ー"]) > 1:
            return False, "残留假名", ""
        r = len(b) / max(1, len(a))
        if not 0.45 < r < 3.5:            # 日文/中文之间变长是正常的，只拦失控膨胀
            return False, f"长度比 {r:.2f}", ""
        if r > 1.45:            # 只记录，不重试、不删内容
            warn = f"偏长 {r:.2f}x"
    return True, "", warn


def roundtrip(tpl, toks):
    """tpl（占位符形式）→ 日文 → 回中文。失败降级：逐句；再不行返回原文。"""
    last = "?"
    for attempt in range(3):
        try:
            ja = strip_end(clean(call("ja", tpl, temperature=0.2 + 0.15 * attempt)))
            ok, why, _ = check(tpl, ja, "ja")
            if not ok:
                last = f"ja: {why}"
                continue
            zh = strip_end(clean(call("zh", ja, temperature=0.2 + 0.15 * attempt)))
            ok, why, warn = check(tpl, zh, "zh")
            if not ok:
                last = f"zh: {why}"
                continue
            return ja, zh, warn, "whole"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            time.sleep(1 + attempt)
    # 专名占位符把模型带偏（整段丢掉占位符）时，放开专名保护再整段试一次
    raw = restore(tpl, toks)
    tpl2, toks2 = templatize(raw, names=False)
    if (tpl2, toks2) != (tpl, toks):
        for attempt in range(2):
            try:
                ja = clean(call("ja", tpl2, temperature=0.25 + 0.15 * attempt))
                ok, why, _ = check(tpl2, ja, "ja")
                if not ok:
                    last = f"ja(无专名保护): {why}"
                    continue
                zh = clean(call("zh", ja, temperature=0.25 + 0.15 * attempt))
                ok, why, warn = check(tpl2, zh, "zh")
                if not ok:
                    last = f"zh(无专名保护): {why}"
                    continue
                return ja, zh, warn, "whole-loose"
            except Exception as e:  # noqa: BLE001
                last = f"{type(e).__name__}: {e}"
                time.sleep(1)

    # 逐句降级
    parts = [p for p in re.split(r"(?<=[。！？；])", tpl) if p.strip()]
    if len(parts) > 1:
        jas, zhs, warns = [], [], []
        for p in parts:
            try:
                ja = clean(call("ja", p))
                ok, why, _ = check(p, ja, "ja")
                if not ok:
                    raise RuntimeError(why)
                zh = clean(call("zh", ja))
                ok, why, warn = check(p, zh, "zh")
                if not ok:
                    raise RuntimeError(why)
                jas.append(ja)
                zhs.append(zh)
                if warn:
                    warns.append(warn)
            except Exception:  # noqa: BLE001
                jas.append(p)
                zhs.append(p)
        return "".join(jas), "".join(zhs), ("; ".join(warns) + " | " + last).strip(" |"), "sentence"
    return tpl, tpl, last[:60], "keep-original"


# ---------------------------------------------------------------- 流程

def load_cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


_save_lock = __import__("threading").Lock()


def save_cache(c):
    with _save_lock:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE.with_suffix(".tmp")
        tmp.write_text(json.dumps(c, ensure_ascii=False, indent=1))
        tmp.replace(CACHE)


def key_of(tpl):
    return hashlib.sha1(("zh\x00" + tpl).encode()).hexdigest()[:16]


def heading_units(s):
    """标题行（= / == / === …）的正文部分，标签 <sec:…> 由占位符保护。"""
    out = []
    for g in re.finditer(r"(?m)^(=+ )(.+?)[ \t]*$", s):
        a, b = g.start(2), g.end(2)
        if len(HAN.findall(s[a:b])) >= 2:
            out.append((a, b))
    return out


def units_of(src_path=SRC):
    s = src_path.read_text()
    out = []
    for a, b in prose_units(s):
        tpl, toks = templatize(s[a:b])
        if restore(tpl, toks) != s[a:b]:
            continue
        out.append((a, b, tpl, toks, "body"))
    for a, b in heading_units(s):
        tpl, toks = templatize(s[a:b], extra=EXTRA_TERMS)
        if restore(tpl, toks) != s[a:b]:
            continue
        out.append((a, b, tpl, toks, "head"))
    out.sort(key=lambda u: u[0])
    return s, out


def cmd_plan():
    s, units = units_of()
    tot = sum(b - a for a, b, _, _, _k in units)
    print(f"{SRC.name}: {len(s)} 字, 正文段 {len(units)} 段, 段内 {tot} 字 "
          f"({tot/max(1,len(s)):.0%})")
    sizes = sorted(b - a for a, b, _, _, _k in units)
    print(f"段长 min/med/max = {sizes[0]}/{sizes[len(sizes)//2]}/{sizes[-1]}")
    for a, b, tpl, _, _k in units[:2] + units[-2:]:
        print(f"\n--- [{a}:{b}] {b-a}字\n{tpl[:200]}")


def cmd_run():
    s, units = units_of()
    cache = load_cache()
    todo = [(i, u) for i, u in enumerate(units) if key_of(u[2]) not in cache]
    print(f"共 {len(units)} 段，待翻译 {len(todo)} 段（缓存 {len(units)-len(todo)}）")
    t_all = time.time()
    done = [0]

    def work(item):
        i, (a, b, tpl, toks, _kind) = item
        t0 = time.time()
        if _kind == "head":
            ja, zh, warn, how = roundtrip_head(tpl, toks)
        else:
            ja, zh, warn, how = roundtrip(tpl, toks)
        rec = {"ja": ja, "zh": zh, "warn": warn, "how": how, "src": tpl, "kind": _kind}
        cache[key_of(tpl)] = rec
        save_cache(cache)
        done[0] += 1
        print(f"[{done[0]}/{len(todo)}] {time.time()-t0:5.1f}s {b-a:4d}->{len(zh):4d} {how:12s} "
              f"{warn:12s} {tpl[:26]!r}", flush=True)

    jobs = int(os.environ.get("RT_JOBS", "8"))
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        list(ex.map(work, todo))
    print(f"\n完成，用时 {time.time()-t_all:.0f}s，缓存 {CACHE}")


def cmd_write():
    s, units = units_of()
    cache = load_cache()
    pieces, pos, done, miss = [], 0, 0, []
    for a, b, tpl, toks, _kind in units:
        rec = cache.get(key_of(tpl))
        if not rec:
            miss.append(tpl)
            continue
        zh = restore(rec["zh"], toks) if "⟦" in rec["zh"] else rec["zh"]
        zh = fix_refs(tpl, toks, tidy(zh))
        pieces.append(s[pos:a])
        pieces.append(zh)
        pos = b
        done += 1
    pieces.append(s[pos:])
    text = "".join(pieces)
    # 多嵌套一层目录：../shared/ → ../../shared/
    text = text.replace('"../shared/', '"../../shared/')
    dst = OUTDIR / "main.typ"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    print(f"写出 {dst}：替换 {done}/{len(units)} 段，缺 {len(miss)} 段")
    for m in miss[:5]:
        print("   缺:", m[:50])


def cmd_report():
    s, units = units_of()
    cache = load_cache()
    lines = ["# 往返翻译对照（design/main.typ）", "",
             "| # | 原文 | 日文 | 回译中文 | 标记 |", "|---|---|---|---|---|"]
    n = 0
    for i, (a, b, tpl, toks, _kind) in enumerate(units, 1):
        rec = cache.get(key_of(tpl))
        if not rec:
            continue
        n += 1
        ja = restore(rec["ja"], toks) if "⟦" in rec["ja"] else rec["ja"]
        zh = restore(rec["zh"], toks) if "⟦" in rec["zh"] else rec["zh"]
        zh = fix_refs(tpl, toks, tidy(zh))
        src = restore(tpl, toks)
        flag = " / ".join(x for x in (rec.get("warn", ""), "" if rec.get("how") == "whole" else rec["how"]) if x)
        lines.append(f"| {i} | {src} | {ja} | {zh} | {flag} |")
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"写出 {REPORT}：{n} 段")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    {"plan": cmd_plan, "run": cmd_run, "write": cmd_write, "report": cmd_report}.get(
        cmd, lambda: SystemExit("usage: polish.py [plan|run|write|report]")
    )()
