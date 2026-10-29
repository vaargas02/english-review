import json,pathlib,sys
out=[]
for f in sorted(pathlib.Path('fuente/lecciones').glob('*.json')):
    l=json.loads(f.read_text())
    out.append(f"### {l['lesson']}\n")
    out.append("| Word | Type | Español | Meaning | Example |\n| --- | --- | --- | --- | --- |")
    for w in l['words']:
        m=w['def']
        if 'syn' in w: m+=f" (≈ {w['syn']} · ✕ {w['opp']})"
        ex=w['ex'].replace('{','*').replace('}','*')
        out.append(f"| **{w['w']}** | {w['pos']} | {w['es']} | {m} | {ex} |")
    out.append("")
print("\n".join(out))
