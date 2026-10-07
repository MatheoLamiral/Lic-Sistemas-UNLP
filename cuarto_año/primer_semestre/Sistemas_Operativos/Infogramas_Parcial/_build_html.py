#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte los infogramas .md en HTML graficos autocontenidos."""
import os, re, glob, html as _html
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "html")
os.makedirs(OUT, exist_ok=True)

# Acento de color por archivo (para diferenciar temas visualmente)
ACCENTS = {
    "00": ("#6d28d9", "#a78bfa"), "01": ("#2563eb", "#60a5fa"),
    "02": ("#0891b2", "#22d3ee"), "03": ("#059669", "#34d399"),
    "04": ("#7c3aed", "#a78bfa"), "05": ("#d97706", "#fbbf24"),
    "06": ("#0284c7", "#38bdf8"), "07": ("#dc2626", "#f87171"),
    "08": ("#db2777", "#f472b6"), "09": ("#4f46e5", "#818cf8"),
    "10": ("#ea580c", "#fb923c"),
}

ICONS = {
    "00":"🎯","01":"🧩","02":"🔌","03":"🧵","04":"🖥️","05":"📦",
    "06":"🐳","07":"🔒","08":"💾","09":"⚙️","10":"⛓️",
}

CSS_TEMPLATE = """
:root {{ --accent:{accent}; --accent2:{accent2}; }}
* {{ box-sizing:border-box; }}
body {{
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  margin:0; background:#0f172a; color:#1e293b; line-height:1.55;
}}
.wrap {{ max-width:1100px; margin:0 auto; padding:0 16px 60px; }}
header.hero {{
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff; padding:38px 28px; border-radius:0 0 24px 24px;
  box-shadow:0 8px 30px rgba(0,0,0,.35); margin-bottom:26px;
}}
header.hero h1 {{ margin:0; font-size:2.0rem; display:flex; align-items:center; gap:14px; }}
header.hero .sub {{ opacity:.92; margin-top:8px; font-size:.95rem; }}
.topbar {{ background:#0f172a; padding:10px 16px; }}
.topbar a {{ color:#cbd5e1; text-decoration:none; font-size:.88rem; font-weight:600; }}
.topbar a:hover {{ color:#fff; }}
section.card {{
  background:#fff; border-radius:16px; padding:18px 22px; margin:18px 0;
  box-shadow:0 4px 18px rgba(0,0,0,.18); border-left:6px solid var(--accent);
}}
section.card h2 {{
  margin:0 0 12px; font-size:1.28rem; color:var(--accent);
  display:flex; align-items:center; gap:10px;
}}
section.card h3 {{ font-size:1.05rem; color:#334155; margin:16px 0 6px; }}
section.trampas {{
  border-left:6px solid #f59e0b; background:#fffbeb;
}}
section.trampas h2 {{ color:#b45309; }}
ul, ol {{ margin:8px 0 8px; padding-left:24px; }}
li {{ margin:4px 0; }}
table {{
  border-collapse:collapse; width:100%; margin:14px 0; font-size:.92rem;
  border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.10);
}}
th {{ background:var(--accent); color:#fff; text-align:left; padding:9px 12px; }}
td {{ padding:8px 12px; border-top:1px solid #e2e8f0; vertical-align:top; }}
tr:nth-child(even) td {{ background:#f8fafc; }}
code {{ background:#eef2ff; color:#3730a3; padding:1px 6px; border-radius:5px;
  font-family:'Fira Code',Consolas,monospace; font-size:.88em; }}
pre {{ background:#1e293b; color:#e2e8f0; padding:14px; border-radius:10px; overflow:auto; }}
pre code {{ background:none; color:inherit; padding:0; }}
strong {{ color:#0f172a; }}
blockquote {{ border-left:4px solid var(--accent2); margin:10px 0; padding:6px 16px;
  background:#f1f5f9; border-radius:0 8px 8px 0; color:#475569; }}
.vf-true {{ background:#16a34a; color:#fff; padding:1px 8px; border-radius:20px;
  font-weight:700; font-size:.8rem; letter-spacing:.3px; }}
.vf-false {{ background:#dc2626; color:#fff; padding:1px 8px; border-radius:20px;
  font-weight:700; font-size:.8rem; letter-spacing:.3px; }}
a {{ color:var(--accent); }}
hr {{ border:none; border-top:1px dashed #cbd5e1; margin:22px 0; }}
.home-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr));
  gap:16px; margin-top:10px; }}
.home-grid a {{ text-decoration:none; }}
.tile {{ background:#fff; border-radius:16px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,.18);
  border-top:5px solid var(--accent); transition:transform .12s,box-shadow .12s; height:100%; }}
.tile:hover {{ transform:translateY(-4px); box-shadow:0 10px 28px rgba(0,0,0,.30); }}
.tile .ico {{ font-size:2rem; }}
.tile .t {{ font-weight:700; color:#1e293b; margin:8px 0 4px; font-size:1.05rem; }}
.tile .d {{ color:#64748b; font-size:.85rem; }}
.badge {{ display:inline-block; background:#fef3c7; color:#b45309; font-size:.72rem;
  font-weight:700; padding:2px 8px; border-radius:20px; margin-top:8px; }}
@media print {{ body{{background:#fff;}} section.card{{box-shadow:none;border:1px solid #e2e8f0;}}
  header.hero{{box-shadow:none;}} .topbar{{display:none;}} }}
"""

def style_inline(text):
    # Badges VERDADERO / FALSO (en mayusculas, palabra completa)
    text = re.sub(r'\bVERDADERO\b', '<span class="vf-true">VERDADERO</span>', text)
    text = re.sub(r'\bFALSO\b', '<span class="vf-false">FALSO</span>', text)
    return text

def split_cards(body_html, icon):
    """Envuelve cada bloque H2..siguiente-H2 en una <section class=card>."""
    parts = re.split(r'(?=<h2)', body_html)
    out = []
    # contenido antes del primer h2 (ej. blockquote/intro)
    if parts and not parts[0].lstrip().startswith('<h2'):
        intro = parts.pop(0).strip()
        if intro:
            out.append(f'<section class="card intro">{intro}</section>')
    for p in parts:
        m = re.match(r'<h2[^>]*>(.*?)</h2>', p, re.S)
        heading = re.sub('<.*?>', '', m.group(1)) if m else ''
        cls = "card"
        low = heading.lower()
        if 'trampa' in low or 'concepto' in low or 'posibles preguntas' in low:
            cls = "card trampas"
        # icono en el h2
        p = re.sub(r'(<h2[^>]*>)', r'\1<span>'+icon+'</span> ', p, count=1)
        out.append(f'<section class="{cls}">{p}</section>')
    return "\n".join(out)

def render(md_path):
    key = os.path.basename(md_path)[:2]
    accent, accent2 = ACCENTS.get(key, ("#2563eb","#60a5fa"))
    icon = ICONS.get(key, "📘")
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    # titulo H1
    m = re.search(r'^#\s+(.*)', text, re.M)
    title = re.sub(r'[#*`]', '', m.group(1)).strip() if m else os.path.basename(md_path)
    text = re.sub(r'^#\s+.*\n', '', text, count=1, flags=re.M)
    md = markdown.Markdown(extensions=['tables','fenced_code','sane_lists','attr_list'])
    body = md.convert(text)
    body = style_inline(body)
    cards = split_cards(body, icon)
    css = CSS_TEMPLATE.format(accent=accent, accent2=accent2)
    out_name = os.path.splitext(os.path.basename(md_path))[0] + ".html"
    nav = '<div class="topbar"><a href="index.html">⟵ Índice de infogramas</a></div>'
    htmldoc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(title)}</title>
<style>{css}</style></head>
<body>{nav}
<header class="hero"><h1><span>{icon}</span>{_html.escape(title)}</h1>
<div class="sub">Repaso parcial · Sistemas Operativos UNLP</div></header>
<div class="wrap">{cards}</div>
</body></html>"""
    with open(os.path.join(OUT, out_name), 'w', encoding='utf-8') as f:
        f.write(htmldoc)
    return out_name, title, key, icon, accent, accent2

DESCRIPTIONS = {
    "00":"Cheatsheet maestro — todo en una página","01":"Kernel, tipos, 7 pasos, initramfs",
    "02":"Módulos, drivers, major/minor, syscalls","03":"ULT vs KLT, fork/exec",
    "04":"Hypervisors, paravirt, LXC","05":"cgroups v1/v2, namespaces, chroot",
    "06":"Imagen/contenedor, union FS, compose","07":"ASLR, permisos, sticky/setuid",
    "08":"Inodo, RAID, LVM, BTRFS/XFS","09":"UMA/NUMA, SMP","10":"Coffman, banquero, grafo",
}
PRIORITY = {"00","02","08","01"}

def build_index(items):
    tiles = []
    for out_name, title, key, icon, accent, accent2 in items:
        if key == "00":
            continue
        desc = DESCRIPTIONS.get(key, "")
        badge = '<div class="badge">⭐ muy preguntado</div>' if key in {"02","08","01"} else ''
        tiles.append(f"""<a href="{out_name}"><div class="tile" style="--accent:{accent}">
<div class="ico">{icon}</div><div class="t">{_html.escape(title)}</div>
<div class="d">{desc}</div>{badge}</div></a>""")
    css = CSS_TEMPLATE.format(accent="#6d28d9", accent2="#a78bfa")
    cheat = next((i for i in items if i[2]=="00"), None)
    cheat_btn = ""
    if cheat:
        cheat_btn = f"""<section class="card" style="--accent:#6d28d9">
<h2><span>🎯</span> Empezá por acá</h2>
<p><a href="{cheat[0]}" style="font-size:1.1rem;font-weight:700">→ Cheatsheet maestro (todo en una página)</a></p></section>"""
    doc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Repaso Parcial SO — Infogramas</title>
<style>{css}</style></head>
<body>
<header class="hero"><h1><span>🎯</span> Repaso Parcial — Sistemas Operativos</h1>
<div class="sub">Prácticas 1–5 · Teorías 1–10 · UNLP</div></header>
<div class="wrap">{cheat_btn}
<section class="card"><h2><span>📚</span> Infogramas por tema</h2>
<div class="home-grid">{''.join(tiles)}</div></section></div>
</body></html>"""
    with open(os.path.join(OUT, "index.html"), 'w', encoding='utf-8') as f:
        f.write(doc)

items = []
for md_path in sorted(glob.glob(os.path.join(BASE, "*.md"))):
    items.append(render(md_path))
    print("OK", os.path.basename(md_path))
build_index(items)
print("\nÍndice: index.html  ·", len(items), "infogramas en", OUT)
