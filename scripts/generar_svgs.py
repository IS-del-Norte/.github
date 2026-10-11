"""Genera las tarjetas SVG del perfil (cifras, servicios, productos y contacto).

Uso: python3 scripts/generar_svgs.py profile/assets
"""
import re, sys, os

ASSETS = sys.argv[1]
ICONS = os.path.join(ASSETS, "icons")


def icon(name, x, y, size, color):
    src = open(os.path.join(ICONS, name + ".svg")).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', src).group(1).split()]
    d = re.search(r' d="([^"]*)"', src).group(1)
    s = size / max(vb[2], vb[3])
    dx = x + (size - vb[2] * s) / 2
    dy = y + (size - vb[3] * s) / 2
    return f'<path transform="translate({dx:.1f},{dy:.1f}) scale({s:.4f})" fill="{color}" d="{d}"/>'


DEFS = """
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#062646"/>
      <stop offset="1" stop-color="#0b3b6b"/>
    </linearGradient>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#001a33"/>
      <stop offset="0.55" stop-color="#003462"/>
      <stop offset="1" stop-color="#0a4d8c"/>
    </linearGradient>
    <linearGradient id="txt" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#9fdcff"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#418adc" stop-opacity="0.45"/>
      <stop offset="1" stop-color="#418adc" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="#ffffff" fill-opacity="0.07"/>
    </pattern>
    <style>
      .sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    </style>"""


def svg(w, h, label, body, extra_style=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <defs>{DEFS}{extra_style}
    <clipPath id="clip"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#clip)">
{body}
  </g>
</svg>
'''


def card(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#card)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#dots)"/>'
            f'<rect x="{x+0.75}" y="{y+0.75}" width="{w-1.5}" height="{h-1.5}" rx="17.5" fill="none" stroke="#418adc" stroke-opacity="0.35" stroke-width="1.5"/>')


def lines(x, y, rows, size, color, gap, cls="sans", opacity=None):
    op = f' fill-opacity="{opacity}"' if opacity else ""
    return "".join(f'<text class="{cls}" x="{x}" y="{y + i*gap}" font-size="{size}" fill="{color}"{op}>{r}</text>' for i, r in enumerate(rows))


# ---------- Servicios: 2 columnas x 3 filas ----------
SERV = [
    ("building", "Intelisis ERP", ["Implementación, personalización y soporte.", "Implementadores certificados, +19 años."]),
    ("mobile-screen-button", "Aplicaciones móviles", ["Apps empresariales para iOS y Android", "desde una sola base de código."]),
    ("globe", "Aplicaciones web", ["Sistemas a la medida que centralizan la", "operación y eliminan procesos manuales."]),
    ("cart-shopping", "E-commerce", ["Tiendas en línea con OXXO, SPEI y tarjetas,", "integradas con paqueterías."]),
    ("cloud-arrow-up", "Respaldo Simple", ["Backup cifrado AES-256 para servidores", "Windows y SQL Server."]),
    ("magnifying-glass-chart", "Consultoría", ["Diagnóstico de operación, plan de", "transformación digital e implementación."]),
]
W, CW, CH, G = 1200, 590, 168, 20
body = []
for i, (ic, t, d) in enumerate(SERV):
    x = (i % 2) * (CW + G)
    y = (i // 2) * (CH + G)
    body.append(card(x, y, CW, CH))
    body.append(f'<rect x="{x+32}" y="{y+34}" width="64" height="64" rx="16" fill="#418adc" fill-opacity="0.18"/>')
    body.append(icon(ic, x + 48, y + 50, 32, "#7cd4ff"))
    body.append(f'<text class="sans" x="{x+122}" y="{y+62}" font-size="28" font-weight="800" fill="url(#txt)">{t}</text>')
    body.append(lines(x + 122, y + 100, d, 20, "#d6ecff", 30, opacity="0.85"))
H = 3 * CH + 2 * G
open(os.path.join(ASSETS, "servicios.svg"), "w").write(
    svg(W, H, "Qué hacemos: Intelisis ERP, apps móviles, apps web, e-commerce, Respaldo Simple y consultoría", "\n".join(body)))

# ---------- Cifras ----------
STATS = [("1999", "año de fundación"), ("+19", "años con Intelisis ERP"), ("3", "plataformas: iOS, Android, web"), ("32", "estados con servicio")]
body = [f'<rect width="1200" height="170" rx="18" fill="url(#bg)"/>', '<rect width="1200" height="170" rx="18" fill="url(#dots)"/>',
        '<circle cx="1050" cy="20" r="220" fill="url(#glow)"/>']
cw = 1200 / 4
for i, (n, l) in enumerate(STATS):
    cx = cw * i + cw / 2
    if i:
        body.append(f'<line x1="{cw*i}" y1="44" x2="{cw*i}" y2="126" stroke="#9fdcff" stroke-opacity="0.22" stroke-width="2"/>')
    body.append(f'<text class="sans" x="{cx}" y="96" text-anchor="middle" font-size="56" font-weight="800" fill="url(#txt)">{n}</text>')
    body.append(f'<text class="sans" x="{cx}" y="132" text-anchor="middle" font-size="20" fill="#d6ecff" fill-opacity="0.85">{l}</text>')
open(os.path.join(ASSETS, "cifras.svg"), "w").write(svg(1200, 170, "Desde 1999, +19 años con Intelisis ERP, 3 plataformas, servicio en 32 estados", "\n".join(body)))


# ---------- Productos ----------
def chip(x, y, label):
    w = 18 + len(label) * 11.2
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="38" rx="19" fill="#418adc" fill-opacity="0.2" stroke="#7cd4ff" stroke-opacity="0.35"/>'
            f'<text class="sans" x="{x + w/2:.0f}" y="{y+25}" text-anchor="middle" font-size="18" font-weight="600" fill="#d6ecff">{label}</text>'), w


def producto(fname, eyebrow, title, desc, chips, deco, label):
    w, h = 590, 300
    b = [card(0, 0, w, h), f'<circle cx="{w-40}" cy="40" r="200" fill="url(#glow)"/>', deco]
    b.append(f'<text class="mono" x="36" y="62" font-size="16" letter-spacing="2.5" fill="#7cd4ff">{eyebrow}</text>')
    b.append(f'<text class="sans" x="34" y="112" font-size="40" font-weight="800" fill="url(#txt)">{title}</text>')
    b.append(lines(36, 158, desc, 21, "#d6ecff", 31, opacity="0.85"))
    x = 36
    for c in chips:
        s, cwid = chip(x, 228, c)
        b.append(s)
        x += cwid + 10
    b.append(f'<text class="sans" x="{w-36}" y="254" text-anchor="end" font-size="26" fill="#7cd4ff">→</text>')
    open(os.path.join(ASSETS, fname), "w").write(svg(w, h, label, "\n".join(b)))


bars = "".join(f'<rect x="{430 + i*26}" y="{150 - v}" width="16" height="{v}" rx="4" fill="#7cd4ff" fill-opacity="{0.12 + i*0.05}"/>' for i, v in enumerate([34, 52, 44, 70, 62, 92]))
producto("producto-finanzas.svg", "APP · FINANZAS PERSONALES", "Mis Finanzas IS",
         ["Cuentas, movimientos, pagos periódicos", "y reportes en un solo lugar."],
         ["Web", "iOS", "Android"], bars, "Mis Finanzas IS: finanzas personales en web, iOS y Android")
shield = '<g transform="translate(470,60) scale(0.16)" fill="none" stroke="#7cd4ff" stroke-opacity="0.35" stroke-width="40" stroke-linejoin="round"><path d="M256 32 L448 96 V256 C448 368 352 448 256 480 C160 448 64 368 64 256 V96 Z"/><path d="M176 256 L236 316 L344 196" stroke-linecap="round"/></g>'
producto("producto-respaldo.svg", "RECUPERACIÓN ANTE DESASTRES", "Respaldo Simple",
         ["Backup cifrado para empresas con", "servidores físicos Windows y SQL Server."],
         ["AES-256", "Windows", "SQL Server"], shield, "Respaldo Simple: backup cifrado AES-256 para servidores Windows y SQL Server")

# ---------- Cierre / contacto ----------
b = ['<rect width="1200" height="230" rx="18" fill="url(#bg)"/>', '<rect width="1200" height="230" rx="18" fill="url(#dots)"/>',
     '<circle cx="1100" cy="200" r="260" fill="url(#glow)"/>']
b.append('<text class="mono" x="64" y="72" font-size="17" letter-spacing="3" fill="#7cd4ff">PRIMERA CONSULTA SIN COSTO</text>')
b.append('<text class="sans" x="62" y="128" font-size="44" font-weight="800" fill="url(#txt)">¿Platicamos tu proyecto?</text>')
b.append('<text class="mono" x="64" y="176" font-size="19" fill="#ffffff" fill-opacity="0.85"><tspan fill="#418adc">❯</tspan> escríbenos por WhatsApp<tspan class="caret" fill="#418adc">▍</tspan></text>')
b.append('<line x1="760" y1="44" x2="760" y2="186" stroke="#9fdcff" stroke-opacity="0.22" stroke-width="2"/>')
for i, (ic, t) in enumerate([("phone", "81 2188 4423"), ("envelope", "contacto@isdelnorte.com"), ("location-dot", "Monterrey, NL, México")]):
    y = 66 + i * 46
    b.append(icon(ic, 800, y, 22, "#7cd4ff"))
    b.append(f'<text class="sans" x="838" y="{y+18}" font-size="21" fill="#d6ecff">{t}</text>')
style = """
    <style>
      .caret { animation: blink 1s steps(1) infinite; }
      @keyframes blink { 50% { opacity: 0; } }
    </style>"""
open(os.path.join(ASSETS, "contacto.svg"), "w").write(svg(1200, 230, "¿Platicamos tu proyecto? 81 2188 4423 · contacto@isdelnorte.com · Monterrey, NL", "\n".join(b), style))
print("ok")
