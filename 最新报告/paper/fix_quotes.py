import pathlib
for f in sorted(pathlib.Path("sections").glob("0[1-7]-*.typ")):
    t = f.read_text(encoding="utf-8")
    if t.count('"') % 2:
        print("ODD quotes, skipped:", f)
        continue
    out, open_q = [], True
    for ch in t:
        if ch == '"':
            out.append("\u201c" if open_q else "\u201d")
            open_q = not open_q
        else:
            out.append(ch)
    f.write_text("".join(out), encoding="utf-8")
    print("quotes fixed:", f.name)
