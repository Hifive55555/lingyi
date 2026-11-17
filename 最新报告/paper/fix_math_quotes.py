import pathlib
for f in sorted(pathlib.Path("sections").glob("0[1-7]-*.typ")):
    t = f.read_text(encoding="utf-8")
    out = []
    in_math = False
    in_raw = False
    i = 0
    lines = t.split("\n")
    res = []
    for ln in lines:
        if ln.strip().startswith("```"):
            in_raw = not in_raw
            res.append(ln)
            continue
        if in_raw:
            res.append(ln.replace("\u201c", '"').replace("\u201d", '"'))
            continue
        buf = []
        for ch in ln:
            if ch == "$":
                in_math = not in_math
                buf.append(ch)
            elif in_math and ch in "\u201c\u201d":
                buf.append('"')
            else:
                buf.append(ch)
        res.append("".join(buf))
    new = "\n".join(res)
    if new != t:
        f.write_text(new, encoding="utf-8")
        print("fixed", f.name)
