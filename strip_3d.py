with open("app/static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for l in lines:
    if "// ── Three.js 3D Engine" in l:
        break
    out.append(l)

out.append("})();\n")

with open("app/static/app.js", "w", encoding="utf-8") as f:
    f.writelines(out)
