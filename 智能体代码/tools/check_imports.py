# -*- coding: utf-8 -*-
"""引用体检：比赛机只能用灵弈自带 Python（ray210），这句 import 会不会炸？

为什么要有这个脚本
------------------
CI 里只跑 `py_compile` 只能查语法。历史上真出过的问题：
  · 顺手 `import numpy / requests / pandas` —— 开发机有、比赛机没有，上机即崩；
  · 把 `.venv\\Scripts\\python.exe`、`site-packages` 写进 `sys.path`；
  · `tools/` 的开发依赖（openpyxl 之类）被运行时代码 import 进去。

检查五组规则（FAIL 会拦提交；WARN 只提示）
------------------------------------
R1 第三方依赖：运行时代码只允许 stdlib + `pyenv_ray210.txt` 的 [core] + 平台内部
   `engine.*`/`entitys.*`；[engine-deps] 只 WARN（未实测）；[dev] 在运行时代码里 FAIL。
R2 外部环境引用：`.venv` / `venvs` / `site-packages` / `pip install` /
   `requirements.txt` / `setup.py` / `PYTHONPATH` / 非 ray210 的 python.exe 路径。
R3 `sys.path` 洁癖：只允许 `dirname(__file__)` / `_agentpath.ensure()` /
   平台注入的 `intelligent\\ai`；出现绝对路径或 `..` 乱跳则 FAIL。
R4 引用是否干净：未使用 import、重复 import（WARN，可 `# noqa` / `# import-check: allow` 豁免）。
R5 兜底契约：运行时代码 `from engine.LingYi.… import` 必须有 `except ImportError:` 同级兜底
   （否则离线自测跑不了）。

用法
----
    python check_imports.py               # 体检全仓库
    python check_imports.py --verbose     # 把通过的文件也列出来
    python check_imports.py --dump-env     # 在目标机跑：按 ray210 实况重写清单

豁免：在某一行或文件任意位置写 `# import-check: allow 模块名, 另一个`。

退出码：0 = 无 FAIL；1 = 有 FAIL。
"""
from __future__ import print_function

import argparse
import ast
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # 仓库根
MANIFEST = os.path.join(HERE, 'pyenv_ray210.txt')

RUNTIME_GLOBS = (
    ('智能体代码', ('.py',), False),        # 两个 Mission + 三个战术模块
    ('小窗', ('.py',), False),              # overlay_ai.py
    ('小窗/overlay', ('.py',), False),      # agent/launcher/monitor/zmqlock…
)
TOOLS_GLOBS = (
    ('智能体代码/tools', ('.py',), True),
)
SKIP_DIRS = {'entitys', '__pycache__', '.git', 'dist', 'build'}

# 平台内部前缀（不是 pip 包，是灵弈自己的包）
PLATFORM_PREFIXES = ('engine', 'entitys')

# Python 3.9 标准库顶层模块名（CI 跑 3.11 时会用 sys.stdlib_module_names，
# 这里只是 3.9 的兜底；两边取并集，避免把 3.10+ 才有的当成合法）。
STDLIB_39 = set('''
__future__ _abc _ast _bisect _blake2 _bootlocale _bz2 _codecs _codecs_cn _codecs_hk
_codecs_iso2022 _codecs_jp _codecs_kr _codecs_tw _collections _collections_abc
_compat_pickle _compression _contextvars _csv _ctypes _curses _curses_panel _datetime
_decimal _elementtree _functools _gdbm _hashlib _heapq _imp _io _json _locale _lsprof
_lzma _markupbase _md5 _msi _multibytecodec _multiprocessing _opcode _operator _osx_support
_overlapped _pickle _posixshmem _posixsubprocess _py_abc _pydecimal _pyio _queue _random
_sha1 _sha256 _sha3 _sha512 _signal _sitebuiltins _socket _sqlite3 _sre _ssl _stat
_statistics _string _strptime _struct _symtable _thread _threading_local _tkinter
_tracemalloc _uuid _warnings _weakref _weakrefset _winapi _xxsubinterpreters abc aifc
antigravity argparse array ast asynchat asyncio asyncore atexit audioop base64 bdb binascii
binhex bisect builtins bz2 cProfile calendar cgi cgitb chunk cmath cmd code codecs
codeop collections colorsys compileall concurrent configparser contextlib contextvars copy
copyreg crypt csv ctypes curses dataclasses datetime dbm decimal difflib dis distutils
doctest dummy_threading email encodings ensurepip enum errno faulthandler fcntl filecmp
fileinput fnmatch formatter fractions ftplib functools gc getopt getpass gettext glob
graphlib grp gzip hashlib heapq hmac html http idlelib imaplib imghdr imp importlib
impure_wsgi inspect io ipaddress itertools json keyword lib2to3 linecache locale logging
lzma mailbox mailcap marshal math mimetypes mmap modulefinder msilib msvcrt multiprocessing
netrc nis nntplib nt ntpath nturl2path numbers opcode operator optparse os ossaudiodev
parser pathlib pdb pickle pickletools pipes pkgutil platform plistlib poplib posix
posixpath pprint profile pstats pty pwd py_compile pyclbr pydoc pydoc_data pyexpat queue
quopri random re readline reprlib resource rlcompleter runpy sched secrets select
selectors shelve shlex shutil signal site smtpd smtplib sndhdr socket socketserver
spwd sqlite3 sre_compile sre_constants sre_parse ssl stat statistics string stringprep
struct subprocess sunau symbol symtable sys sysconfig syslog tabnanny tarfile telnetlib
tempfile termios textwrap this threading time timeit tkinter token tokenize trace
traceback tracemalloc tty turtle turtledemo types typing unicodedata unittest urllib
uu uuid venv warnings wave weakref webbrowser winreg winsound wsgiref xdrlib xml
xmlrpc zipapp zipfile zipimport zlib zoneinfo
'''.split())


# ---------------------------------------------------------------------- 清单
def load_manifest(path=MANIFEST):
    """读 pyenv_ray210.txt -> {'core': set(), 'engine-deps': set(), 'dev': set()}"""
    groups = {'core': set(), 'engine-deps': set(), 'dev': set()}
    cur = None
    if not os.path.exists(path):
        return groups
    with io.open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'^\[([\w.-]+)\]$', line)
            if m:
                cur = m.group(1) if m.group(1) in groups else None
                continue
            if cur is None:
                continue
            name = re.split(r'[\s#]', line, 1)[0].strip()
            if name:
                groups[cur].add(name)
    return groups


def dump_env(path=MANIFEST):
    """在目标机（ray210）上跑：按实际可导入的顶层包重写清单。"""
    import pkgutil
    seen = set()
    for mod in pkgutil.iter_modules():
        name = mod.name
        if name.startswith('_') or name in STDLIB_39 or name in seen:
            continue
        if name in ('site-packages', 'pip', 'setuptools', 'pkg_resources',
                    'wheel', 'easy_install'):
            continue
        seen.add(name)
    core = sorted(seen)
    lines = [
        '# 灵弈自带 Python（ray210, %s）可用的顶层模块清单' % sys.version.split()[0],
        '# 本文件由 `check_imports.py --dump-env` 在目标机生成，请勿手改段落结构。',
        '# 生成时间：%s' % __import__('time').strftime('%Y-%m-%d %H:%M'),
        '',
        '[core]',
    ]
    lines += core
    lines += ['', '[engine-deps]', '', '[dev]', '']
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('[OK] 已重写清单 %s（%d 个顶层模块）' % (path, len(core)))
    return 0


# ---------------------------------------------------------------------- 工具
def iter_files(globs, skip_tools=False):
    for rel, exts, is_tools in globs:
        base = os.path.join(ROOT, rel)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            drop = set(SKIP_DIRS)
            if skip_tools:
                drop.add('tools')             # tools 由 TOOLS_GLOBS 单独扫，别扫两遍
            dirnames[:] = [d for d in dirnames if d not in drop]
            for fn in sorted(filenames):
                if not fn.endswith(exts):
                    continue
                yield os.path.join(dirpath, fn), is_tools


def local_modules(path):
    """同目录里能直接 import 的名字（模块 + 包）。"""
    d = os.path.dirname(path)
    names = set()
    try:
        for e in os.listdir(d):
            full = os.path.join(d, e)
            if e.endswith('.py') and e != '__init__.py':
                names.add(e[:-3])
            elif os.path.isdir(full) and os.path.exists(os.path.join(full, '__init__.py')):
                names.add(e)
    except OSError:
        pass
    return names


def parent_modules(path):
    """上一级目录里的模块名（tools/ 脚本会 import 上级的 Mission_all_*）。"""
    d = os.path.dirname(os.path.dirname(path))
    names = set()
    try:
        for e in os.listdir(d):
            if e.endswith('.py') and e != '__init__.py':
                names.add(e[:-3])
            elif os.path.isdir(os.path.join(d, e)) and os.path.exists(
                    os.path.join(d, e, '__init__.py')):
                names.add(e)
    except OSError:
        pass
    return names


def stdlib_names():
    names = set(STDLIB_39)
    names |= set(getattr(sys, 'stdlib_module_names', ()) or ())
    names |= set(sys.builtin_module_names)
    return names


BAD_TEXT = (
    (re.compile(r'\.venv\b'), '引用了 .venv（比赛机没有虚拟环境）'),
    (re.compile(r'[\\/]venvs[\\/]'), '引用了 venvs 目录（本机环境）'),
    (re.compile(r'site-packages', re.I), '引用了 site-packages（外部环境路径）'),
    (re.compile(r'pip\s+install', re.I), '出现 pip install（比赛机不能联网装包）'),
    (re.compile(r'requirements[-\w]*\.txt', re.I), '出现 requirements.txt'),
    (re.compile(r'\bPYTHONPATH\b'), '依赖 PYTHONPATH（比赛机不设这个变量）'),
)
PY_PATH_RE = re.compile(r'python3\.\d+|Programs[\\/]Python|Python3\d[\\/]', re.I)


def line_of(node):
    return getattr(node, 'lineno', 1)


def check_file(path, is_tools, manifest, stdlib, verbose):
    """返回 (fails, warns)，每项是 (行号, 文本)。"""
    fails, warns = [], []
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    try:
        src = io.open(path, encoding='utf-8').read()
    except (IOError, OSError) as e:
        return [(1, '读不了文件：%s' % e)], []
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [(e.lineno or 1, '语法错误：%s（先跑 py_compile）' % e.msg)], []

    allowed_inline = set()
    for line in src.splitlines():
        m = re.search(r'#\s*import-check:\s*allow\s+([\w.,\s]+)', line)
        if m:
            allowed_inline |= {x.strip() for x in m.group(1).split(',') if x.strip()}
    noqa_lines = {i + 1 for i, line in enumerate(src.splitlines()) if '# noqa' in line}

    core = manifest['core']
    deps = manifest['engine-deps']
    dev = manifest['dev']
    loc = local_modules(path)
    loc |= parent_modules(path)

    # ---------- R2：外部环境引用（注释和 docstring 里提到不算） ----------
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            end = getattr(node, 'end_lineno', line_of(node))
            doc_lines.update(range(line_of(node), end + 1))
    PATH_CTX = re.compile(r'[A-Za-z]:[\\/]|sys\.path|open\(|Popen|subprocess|'
                          r'join\(|Path\(|os\.environ|expanduser|abspath')
    for i, line in enumerate(src.splitlines(), 1):
        if i in doc_lines or line.lstrip().startswith('#'):
            continue
        if not PATH_CTX.search(line):
            continue          # 只是提示文案里提到 .venv，不算引用
        for rx, why in BAD_TEXT:
            if rx.search(line):
                fails.append((i, '%s' % why))
        if PY_PATH_RE.search(line) and 'ray210' not in line and 'new_env' not in line:
            fails.append((i, '写死了非 ray210 的 python 路径'))

    # ---------- R3：sys.path 洁癖 ----------
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = getattr(f, 'attr', None) or getattr(f, 'id', None)
        if name not in ('append', 'insert', 'extend'):
            continue
        owner = getattr(f, 'value', None)
        if not (isinstance(owner, ast.Attribute) and owner.attr == 'path'):
            continue
        for arg in node.args:
            seg = ast.get_source_segment(src, arg) or ''
            if 'ray210' in seg or 'new_env' in seg:
                continue
            if any(k in seg for k in ('__file__', '_agentpath', 'ensure(',
                                      'AI', 'HERE', 'dir', 'path')):
                continue
            norm = seg.replace('\\\\', '\\')
            if re.search(r'[A-Za-z]:[\\/]', seg) or norm.startswith('/') or '..' in seg:
                fails.append((line_of(node),
                              'sys.path 里加了外部路径：%s' % seg.strip()[:60]))

    # ---------- R5：engine 导入必须有同级兜底 ----------
    # 只有两个 Mission 需要这层兜底：离线自测打桩驱动的是它们；
    # overlay/* 不进离线自测，engine 是平台保证存在的。
    entry_like = os.path.basename(path).startswith('Mission_all_')
    imports_engine = any(
        isinstance(n, ast.ImportFrom) and (n.module or '').startswith('engine')
        for n in ast.walk(tree))
    if entry_like and imports_engine and 'except ImportError' not in src and not is_tools:
        fails.append((1, 'from engine.… import 没有 except ImportError 同级兜底'
                         '（离线自测会跑不起来）'))

    # ---------- R1 + R4：逐个 import ----------
    seen = {}                      # (模块, 名字) -> 行号，用于重复导入
    bound = {}                     # 绑定名 -> (模块, 行号)
    star = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split('.')[0]
                alias = a.asname or top
                key = (a.name, alias)
                if key in seen and node.col_offset == 0:
                    warns.append((line_of(node), '重复 import %s' % a.name))
                seen[key] = line_of(node)
                bound.setdefault(alias, (top, line_of(node)))
                _judge(top, line_of(node), rel, is_tools, core, deps, dev,
                       loc, stdlib, allowed_inline, fails, warns)
        elif isinstance(node, ast.ImportFrom):
            if node.level:                       # 相对导入，同包，跳过
                continue
            top = (node.module or '').split('.')[0]
            _judge(top, line_of(node), rel, is_tools, core, deps, dev,
                   loc, stdlib, allowed_inline, fails, warns)
            for a in node.names:
                if a.name == '*':
                    star = True
                    continue
                alias = a.asname or a.name
                key = (node.module, alias)
                if key in seen and node.col_offset == 0:
                    warns.append((line_of(node), '重复 import %s.%s'
                                  % (node.module, a.name)))
                seen[key] = line_of(node)
                bound.setdefault(alias, (top, line_of(node)))

    # ---------- R4：未使用 import ----------
    if not star:
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                cur = node
                while isinstance(cur, ast.Attribute):
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    used.add(cur.id)
        exported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == '__all__':
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            exported = {getattr(e, 'value', '')
                                        for e in node.value.elts}
        for alias, (mod, ln) in sorted(bound.items()):
            if mod == '__future__' or alias == '__future__':
                continue
            if alias in used or alias in exported or alias.startswith('_'):
                continue
            if ln in noqa_lines or mod in allowed_inline or alias in allowed_inline:
                continue
            warns.append((ln, 'import 了但没用到：%s（确认后加 # noqa）' % alias))

    if verbose and not fails:
        print('  [OK]   %-52s 引用干净' % rel)
    return fails, warns


def _judge(top, ln, rel, is_tools, core, deps, dev, loc, stdlib,
           allowed_inline, fails, warns):
    if not top or top in loc or top in stdlib or top in allowed_inline:
        return
    if top.startswith('_'):
        return
    if top in PLATFORM_PREFIXES:
        if is_tools:
            return
        return
    if top in core:
        return
    if top in dev:
        if is_tools:
            return
        fails.append((ln, "引用了开发依赖 '%s'（只在 tools/ 允许，比赛机运行时会炸）" % top))
        return
    if top in deps:
        if is_tools:
            return
        warns.append((ln, "引用了 '%s'：清单里归为「引擎依赖，未实测」，"
                          "请 --dump-env 后确认" % top))
        return
    msg = ("未登记的第三方依赖 '%s' —— 比赛机是 ray210(3.9)，没有这个包。"
           "若确认 ray210 里有，跑 check_imports.py --dump-env 重建清单；"
           "否则改掉，或在行尾写 # import-check: allow %s" % (top, top))
    if is_tools:
        warns.append((ln, msg))
    else:
        fails.append((ln, msg))


def main():
    ap = argparse.ArgumentParser(description='引用体检（比赛机只能用 ray210）')
    ap.add_argument('--verbose', action='store_true', help='连通过的文件也列出来')
    ap.add_argument('--dump-env', action='store_true',
                    help='在目标机上按 ray210 实况重写 pyenv_ray210.txt')
    args = ap.parse_args()

    if args.dump_env:
        return dump_env()

    manifest = load_manifest()
    stdlib = stdlib_names()
    n_files = n_fail = n_warn = 0
    all_fails, all_warns = [], []

    targets = (list(iter_files(RUNTIME_GLOBS, skip_tools=True))
               + list(iter_files(TOOLS_GLOBS)))
    # 自检脚本自己会提到 .venv / pip install 这些词（在说明里），跳过；
    # 同时按真实路径去重（'小窗' 与 '小窗/overlay' 两个 glob 会重叠）
    uniq, seen_paths = [], set()
    for p_, t_ in targets:
        rp = os.path.realpath(p_)
        if os.path.basename(p_) == 'check_imports.py' or rp in seen_paths:
            continue
        seen_paths.add(rp)
        uniq.append((p_, t_))
    targets = uniq
    for path, is_tools in targets:
        n_files += 1
        fails, warns = check_file(path, is_tools, manifest, stdlib, args.verbose)
        rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
        for ln, txt in fails:
            n_fail += 1
            all_fails.append((rel, ln, txt))
        for ln, txt in warns:
            n_warn += 1
            all_warns.append((rel, ln, txt))

    for rel, ln, txt in all_fails:
        print('[FAIL] %s:%d  %s' % (rel, ln, txt))
    for rel, ln, txt in all_warns:
        print('[WARN] %s:%d  %s' % (rel, ln, txt))

    print('引用体检：%d 个文件，%d 项失败，%d 项提示（清单 %s）'
          % (n_files, n_fail, n_warn,
             'pyenv_ray210.txt' if os.path.exists(MANIFEST) else '缺失，按空处理'))
    if n_fail:
        print('→ 有失败项：比赛机上会 import 失败。改代码，或按提示登记/豁免。')
        return 1
    print('→ 通过：运行时代码只用到 ray210 有的模块，也没有外部环境路径。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
