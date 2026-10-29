#!/usr/bin/env python3
"""Build the app content from fuente/.

  fuente/lecciones/*.json   vocabulary per lesson  -> auto-generated questions + theory section
  fuente/preguntas/*.json   hand-written questions (grammar, functional, mistakes)
  fuente/teoria_base.json   hand-written theory sections

Usage:  python3 tools/generar.py [YYYY-MM-DD] [--publicar]
        --publicar bumps versionCache (config.json) and VERSION (sw.js): use it before every upload.
Then it runs unir.py and validar.py. Question ids are derived from the lesson slug and
the word itself, so they stay stable: never rename a slug or a word once published.
"""
import json, re, sys, hashlib, subprocess, pathlib, datetime

R = pathlib.Path(__file__).resolve().parent.parent
F = R / "fuente"
P = R / "parciales"
P.mkdir(exist_ok=True)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
version = args[0] if args else datetime.date.today().isoformat()
if "--publicar" in sys.argv:
    # bump cache version in config.json and sw.js so phones pick up the new content
    cfg = json.loads((R / "config.json").read_text(encoding="utf-8"))
    cfg["app"]["versionCache"] += 1
    cfg["app"]["versionContenido"] = version
    (R / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    sw = (R / "sw.js").read_text(encoding="utf-8")
    sw = re.sub(r"const VERSION = \d+;", f"const VERSION = {cfg['app']['versionCache']};", sw)
    (R / "sw.js").write_text(sw, encoding="utf-8")
    print("versionCache ->", cfg["app"]["versionCache"])

def slug(s):
    s = re.sub(r"^(to|a|an|the) ", "", s.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def pick(seed, pool, k):
    """Deterministic choice of k distractors."""
    pool = sorted(pool, key=lambda w: hashlib.md5((seed + w["w"]).encode()).hexdigest())
    return pool[:k]

def distractores(w, palabras, k=3):
    otras = [x for x in palabras if x["w"].lower() != w["w"].lower()]
    misma = [x for x in otras if x["pos"] == w["pos"]]
    elegidas = pick(w["w"], misma, k)
    if len(elegidas) < k:
        resto = [x for x in otras if x not in elegidas]
        elegidas += pick(w["w"] + "2", resto, k - len(elegidas))
    return [x["w"] for x in elegidas]

def explic(w):
    ex = w["ex"].replace("{", "**").replace("}", "**")
    s = f"**{w['w']}** ({w['pos']}) = {w['es']}. {w['def'][0].upper() + w['def'][1:]}.\n\n*{ex}*"
    if w.get("syn"):
        s += f"\n\n≈ {w['syn']} · ✕ {w['opp']}"
    return s

teoria = json.loads((F / "teoria_base.json").read_text(encoding="utf-8"))["secciones"]
todas_palabras = []
lecciones = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((F / "lecciones").glob("*.json"))]

for old in P.glob("*.json"):
    old.unlink()

for L in lecciones:
    ws, qs, sub, tid = L["words"], [], L["lesson"], "v-" + L["slug"]
    todas_palabras += ws
    for w in ws:
        base = f"v-{L['slug']}-{slug(w['w'])}"
        comun = {"tema": "Vocabulary", "subtema": sub, "teoria": tid, "explicacion": explic(w)}
        d = distractores(w, ws)
        qs.append({"id": base + "-d", "enunciado": f"Which word or phrase means: “{w['def']}”?",
                   "opciones": [w["w"]] + d, "correcta": 0, **comun})
        gap = re.sub(r"\{[^}]*\}", "_____", w["ex"])
        qs.append({"id": base + "-g", "enunciado": f"Complete the sentence (the form may change): “{gap}”",
                   "opciones": [w["w"]] + distractores(w, ws[::-1] if len(ws) > 4 else ws), "correcta": 0, **comun})
        if w.get("syn"):
            qs.append({"id": base + "-s", "enunciado": f"Which word from the lesson is closest in meaning to “{w['syn']}”?",
                       "opciones": [w["w"]] + d, "correcta": 0, **comun})
    (P / f"v{L['n']:02d}-{L['slug']}.json").write_text(json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8")
    lineas = []
    for w in ws:
        ex = w["ex"].replace("{", "").replace("}", "")
        extra = f" (≈ {w['syn']} · ✕ {w['opp']})" if w.get("syn") else ""
        lineas.append(f"- **{w['w']}** ({w['pos']}): {w['es']}. {w['def']}{extra}. *{ex}*")
    cab = f"Skill practised: {L['skill']}.\n\n" if L.get("skill") else ""
    teoria.append({"id": tid, "titulo": sub, "grupo": "Vocabulary", "contenido": cab + "\n".join(lineas)})

def completar(q):
    """Add the completed model sentence to gap-fill explanations."""
    m = re.search(r"“([^”]*___[^”]*)”", q["enunciado"])
    if not m or "✔" in q["explicacion"]:
        return q
    partes = [x.strip() for x in q["opciones"][q["correcta"]].split(" / ")]
    frase = m.group(1)
    for parte in partes:
        frase = frase.replace("___", parte, 1)
    if "___" not in frase:
        q = dict(q, explicacion=f"✔ *{frase}*\n\n{q['explicacion']}")
    return q

for f in sorted((F / "preguntas").glob("*.json")):
    qs = [completar(q) for q in json.loads(f.read_text(encoding="utf-8"))]
    (P / f.name).write_text(json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8")

(R / "teoria.json").write_text(json.dumps({"version": version, "secciones": teoria}, ensure_ascii=False, indent=1), encoding="utf-8")
# rebuild contenido.json from scratch so removed questions disappear (ids stay stable anyway)
c = R / "contenido.json"
if c.exists(): c.unlink()
subprocess.run([sys.executable, str(R / "tools/unir.py"), str(R), version], check=True)
subprocess.run([sys.executable, str(R / "tools/validar.py"), str(R)])
