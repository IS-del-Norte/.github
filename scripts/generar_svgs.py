"""Genera los SVG del perfil de la organización (banner, servicios, productos y contacto).

Uso: python3 scripts/generar_svgs.py

- Paleta y tipografía de la marca (Nunito 400/700/800, embebida en cada SVG porque
  GitHub muestra los SVG como <img> y ahí no cargan fuentes externas).
- Todo lo que no es el banner sale en dos versiones, -claro y -oscuro, y el README
  elige con <picture> según el tema de GitHub.
- Sin cifras ni datos nuevos: todo el texto viene del README original.
"""
import base64
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "profile", "assets")
FUENTES = os.path.join(RAIZ, "scripts", "fuentes")
ICONOS = os.path.join(ASSETS, "icons")


def css_fuentes():
    reglas = []
    for peso in (400, 700, 800):
        datos = base64.b64encode(open(os.path.join(FUENTES, f"nunito-{peso}.woff2"), "rb").read()).decode()
        reglas.append(f"@font-face {{ font-family: 'Nunito'; font-weight: {peso}; "
                      f"src: url(data:font/woff2;base64,{datos}) format('woff2'); }}")
    return "\n      ".join(reglas)


FONT = css_fuentes()

TEMAS = {
    "claro": dict(card="#FFFFFF", card2="#F2F7FC", borde="#D8E3EF", tinta="#101827", sub="#3A5A7A",
                  acento="#418ADC", acento2="#2D6CB5", tinte="#418ADC", tinte_op="0.12", fondo_icono="#EAF2FB"),
    "oscuro": dict(card="#131C27", card2="#0F1721", borde="#263548", tinta="#E6EDF3", sub="#9DB4CC",
                   acento="#5B9BE6", acento2="#8DBDF2", tinte="#5B9BE6", tinte_op="0.18", fondo_icono="#16263A"),
}


def svg(w, h, etiqueta, cuerpo, defs="", estilo="", recorte=True):
    clip = f'\n    <clipPath id="clip"><rect width="{w}" height="{h}" rx="16"/></clipPath>' if recorte else ""
    abre = '  <g clip-path="url(#clip)">' if recorte else "  <g>"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{etiqueta}">
  <defs>
    <style>
      {FONT}
      .n {{ font-family: 'Nunito', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}{estilo}
    </style>{clip}{defs}
  </defs>
{abre}
{cuerpo}
  </g>
</svg>
'''


def guardar(nombre, contenido):
    open(os.path.join(ASSETS, nombre), "w").write(contenido)


def texto(x, y, t, tam, color, peso=400, extra=""):
    return f'<text class="n" x="{x}" y="{y}" font-size="{tam}" font-weight="{peso}" fill="{color}"{extra}>{t}</text>'


def tarjeta(t, w, h, gid="cg"):
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["card"]}"/>'
            f'<stop offset="1" stop-color="{t["card2"]}"/></linearGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="16" fill="url(#{gid})"/>'
            f'<rect x="0.75" y="0.75" width="{w-1.5}" height="{h-1.5}" rx="15.25" fill="none" stroke="{t["borde"]}" stroke-width="1.5"/>')


# ---------- Ilustraciones propias (caja de 72×72) ----------
def ilustracion(nombre, t):
    a, tn, op = t["acento"], t["tinte"], t["tinte_op"]
    linea = f'fill="none" stroke="{a}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"'
    suave = f'fill="{tn}" fill-opacity="{op}" stroke="{a}" stroke-width="2.5" stroke-linejoin="round"'
    if nombre == "erp":  # módulos que se conectan en un solo sistema
        return (f'<rect x="8" y="8" width="24" height="24" rx="6" fill="{a}"/>'
                f'<rect x="40" y="8" width="24" height="24" rx="6" {suave}/>'
                f'<rect x="8" y="40" width="24" height="24" rx="6" {suave}/>'
                f'<rect x="40" y="40" width="24" height="24" rx="6" {suave}/>'
                f'<path d="M32 20h8M20 32v8M52 32v8M32 52h8" {linea}/>')
    if nombre == "movil":  # teléfono con tarjetas de app
        return (f'<rect x="20" y="4" width="32" height="64" rx="8" {linea}/>'
                f'<rect x="26" y="14" width="20" height="12" rx="3" fill="{a}"/>'
                f'<rect x="26" y="30" width="20" height="12" rx="3" {suave}/>'
                f'<path d="M26 48h14M26 54h9M32 62h8" {linea}/>')
    if nombre == "web":  # ventana de navegador con panel y gráfica
        return (f'<rect x="4" y="10" width="64" height="52" rx="7" {linea}/>'
                f'<path d="M4 22h64" {linea}/>'
                f'<circle cx="11" cy="16" r="1.8" fill="{a}"/><circle cx="17" cy="16" r="1.8" fill="{a}"/><circle cx="23" cy="16" r="1.8" fill="{a}"/>'
                f'<rect x="10" y="28" width="14" height="28" rx="3" {suave}/>'
                f'<rect x="30" y="44" width="7" height="12" rx="2" fill="{a}" fill-opacity="0.5"/>'
                f'<rect x="41" y="38" width="7" height="18" rx="2" fill="{a}" fill-opacity="0.75"/>'
                f'<rect x="52" y="30" width="7" height="26" rx="2" fill="{a}"/>')
    if nombre == "ecommerce":  # bolsa con pago confirmado
        return (f'<path d="M12 24h48l4 40H8z" {suave}/>'
                f'<path d="M26 30v-10a10 10 0 0 1 20 0v10" {linea}/>'
                f'<circle cx="48" cy="52" r="11" fill="{a}"/>'
                f'<path d="M43 52l3.5 3.5L53 49" fill="none" stroke="{t["card"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    if nombre == "respaldo":  # servidores con sincronización
        return (f'<rect x="6" y="10" width="46" height="18" rx="5" {suave}/>'
                f'<rect x="6" y="34" width="46" height="18" rx="5" {suave}/>'
                f'<circle cx="15" cy="19" r="2.2" fill="{a}"/><circle cx="15" cy="43" r="2.2" fill="{a}"/>'
                f'<path d="M24 19h20M24 43h20" {linea}/>'
                f'<circle cx="54" cy="54" r="13" fill="{a}"/>'
                f'<path d="M48.5 54a5.5 5.5 0 0 1 9.6-3.6M59.5 54a5.5 5.5 0 0 1-9.6 3.6" fill="none" stroke="{t["card"]}" stroke-width="2.4" stroke-linecap="round"/>'
                f'<path d="M58.6 46.6v4.2h-4.2M49.4 61.4v-4.2h4.2" fill="none" stroke="{t["card"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    if nombre == "consultoria":  # ruta por fases hasta la meta
        return (f'<path d="M12 60c18 0 10-24 24-24s10-22 24-22" fill="none" stroke="{a}" stroke-width="2.5" stroke-dasharray="4 5" stroke-linecap="round"/>'
                f'<circle cx="12" cy="60" r="6" {suave}/>'
                f'<circle cx="36" cy="36" r="6" fill="{a}"/>'
                f'<path d="M58 30V6" {linea}/><path d="M58 7h11l-4 5 4 5H58z" fill="{a}"/>')
    raise ValueError(nombre)


def icono_fa(nombre, x, y, tam, color):
    src = open(os.path.join(ICONOS, nombre + ".svg")).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', src).group(1).split()]
    d = re.search(r' d="([^"]*)"', src).group(1)
    s = tam / max(vb[2], vb[3])
    return (f'<path transform="translate({x + (tam - vb[2]*s)/2:.1f},{y + (tam - vb[3]*s)/2:.1f}) scale({s:.4f})" '
            f'fill="{color}" d="{d}"/>')


# ---------- Banner (único bloque en navy) ----------
def banner():
    logo = open(os.path.join(ASSETS, "logo_blanco.svg")).read()
    logo = logo[logo.index(">") + 1:logo.rindex("</svg>")].strip()
    defs = '''
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#071524"/>
      <stop offset="0.6" stop-color="#0A1C30"/>
      <stop offset="1" stop-color="#16324F"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#418ADC" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#418ADC" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="#ffffff" fill-opacity="0.06"/>
    </pattern>'''
    estilo = '''
      .flota { animation: flota 12s ease-in-out infinite; }
      .cursor { animation: parpadeo 1s steps(1) infinite; }
      @keyframes flota { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-60px,24px); } }
      @keyframes parpadeo { 50% { opacity: 0; } }'''
    c = [
        '<rect width="1200" height="340" fill="url(#bg)"/>',
        '<rect width="1200" height="340" fill="url(#dots)"/>',
        '<circle class="flota" cx="1040" cy="60" r="280" fill="url(#glow)"/>',
        f'<g transform="translate(72,96) scale(0.4)" fill="none">{logo}</g>',
        '<text class="n" x="74" y="258" font-size="15" font-weight="700" letter-spacing="4.2" fill="#BFDCF8">SOLUCIONES TECNOLÓGICAS</text>',
        '<line x1="430" y1="88" x2="430" y2="268" stroke="#BFDCF8" stroke-opacity="0.2" stroke-width="2"/>',
        '<g transform="translate(474,0)">',
        '<text class="n" x="0" y="112" font-size="16" font-weight="700" letter-spacing="3" fill="#418ADC">DESDE 1999 · MONTERREY, NL</text>',
        '<text class="n" x="-2" y="168" font-size="48" font-weight="800" fill="#FFFFFF">Software, ERP y apps</text>',
        '<text class="n" x="-2" y="222" font-size="48" font-weight="800" fill="#DCEAF9">para empresas mexicanas</text>',
        '<text class="mono" x="0" y="266" font-size="18" fill="#BFDCF8"><tspan fill="#418ADC">❯</tspan> Intelisis ERP · desarrollo a medida · consultoría<tspan class="cursor" fill="#418ADC">▍</tspan></text>',
        '</g>',
    ]
    guardar("banner.svg", svg(1200, 340, "IS del Norte — Soluciones tecnológicas. Software, ERP y apps para empresas mexicanas desde 1999",
                              "\n".join(c), defs, estilo))


# ---------- Servicios ----------
SERVICIOS = [
    ("erp", "Intelisis ERP", ["Implementación, personalización y soporte.", "Implementadores certificados, +19 años."]),
    ("movil", "Aplicaciones móviles", ["Apps empresariales para iOS y Android", "desde una sola base de código."]),
    ("web", "Aplicaciones web", ["Sistemas a la medida que centralizan la", "operación y eliminan procesos manuales."]),
    ("ecommerce", "E-commerce", ["Tiendas en línea con OXXO, SPEI y tarjetas,", "integradas con paqueterías."]),
    ("respaldo", "Respaldo Simple", ["Backup cifrado AES-256 para servidores", "Windows y SQL Server."]),
    ("consultoria", "Consultoría", ["Diagnóstico de operación, plan de", "transformación digital e implementación."]),
]


def servicios(tema):
    t = TEMAS[tema]
    w, h, gap = 590, 168, 20
    c = []
    for i, (il, titulo, desc) in enumerate(SERVICIOS):
        x, y = (i % 2) * (w + gap), (i // 2) * (h + gap)
        c.append(f'<g transform="translate({x},{y})">')
        c.append(tarjeta(t, w, h, f"cg{i}"))
        c.append(f'<rect x="28" y="36" width="96" height="96" rx="22" fill="{t["fondo_icono"]}"/>')
        c.append(f'<g transform="translate(40,48)">{ilustracion(il, t)}</g>')
        c.append(texto(150, 74, titulo, 28, t["tinta"], 800))
        for j, linea in enumerate(desc):
            c.append(texto(150, 108 + j * 28, linea, 19, t["sub"]))
        c.append("</g>")
    guardar(f"servicios-{tema}.svg", svg(1200, 3 * h + 2 * gap,
            "Qué hacemos: Intelisis ERP, aplicaciones móviles, aplicaciones web, e-commerce, Respaldo Simple y consultoría",
            "\n".join(c), recorte=False))


# ---------- Productos ----------
def chip(t, x, y, etiqueta):
    w = 22 + len(etiqueta) * 9.4
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="34" rx="17" fill="none" stroke="{t["acento"]}" stroke-opacity="0.55" stroke-width="1.5"/>'
            + texto(f"{x + w/2:.0f}", y + 23, etiqueta, 16, t["acento2"], 700, ' text-anchor="middle"')), w


def ilus_finanzas(t):
    a, tn, op, card = t["acento"], t["tinte"], t["tinte_op"], t["card"]
    return f'''<g transform="translate(420,34)">
      <rect x="0" y="0" width="132" height="250" rx="22" fill="{card}" stroke="{t["borde"]}" stroke-width="2"/>
      <rect x="14" y="18" width="50" height="7" rx="3.5" fill="{t["sub"]}" fill-opacity="0.45"/>
      <rect x="14" y="32" width="78" height="12" rx="6" fill="{t["tinta"]}" fill-opacity="0.85"/>
      <path d="M14 112 L36 98 L56 104 L78 80 L98 86 L118 62 V128 H14 Z" fill="{tn}" fill-opacity="{op}"/>
      <path d="M14 112 L36 98 L56 104 L78 80 L98 86 L118 62" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="118" cy="62" r="4.5" fill="{a}"/>
      <g fill="{t["sub"]}" fill-opacity="0.18">
        <rect x="14" y="146" width="104" height="22" rx="7"/><rect x="14" y="176" width="104" height="22" rx="7"/><rect x="14" y="206" width="104" height="22" rx="7"/>
      </g>
      <circle cx="26" cy="157" r="5" fill="{a}"/><circle cx="26" cy="187" r="5" fill="{a}" fill-opacity="0.6"/><circle cx="26" cy="217" r="5" fill="{a}" fill-opacity="0.35"/>
    </g>'''


def ilus_respaldo(t):
    a, tn, op, card = t["acento"], t["tinte"], t["tinte_op"], t["card"]
    filas = "".join(
        f'<rect x="0" y="{y}" width="120" height="40" rx="9" fill="{tn}" fill-opacity="{op}" stroke="{a}" stroke-width="2.5"/>'
        f'<circle cx="18" cy="{y+20}" r="4" fill="{a}"/><circle cx="32" cy="{y+20}" r="4" fill="{a}" fill-opacity="0.5"/>'
        f'<path d="M58 {y+20}h46" stroke="{a}" stroke-width="2.5" stroke-linecap="round"/>' for y in (96, 146, 196))
    return f'''<g transform="translate(424,24)">
      <path d="M38 62 a20 20 0 0 1 4-39 a26 26 0 0 1 50 6 a17 17 0 0 1 0 33 z" fill="{tn}" fill-opacity="{op}" stroke="{a}" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M60 88 V52 M50 62 l10-10 10 10" fill="none" stroke="{a}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      {filas}
      <g transform="translate(92,190)">
        <path d="M18 0 L36 6 V20 C36 31 28 38 18 42 C8 38 0 31 0 20 V6 Z" fill="{a}"/>
        <path d="M11 21 l5 5 9-10" fill="none" stroke="{card}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      </g>
    </g>'''


def producto(tema, archivo, ceja, titulo, desc, chips, ilus, etiqueta):
    t = TEMAS[tema]
    w, h = 590, 310
    c = [tarjeta(t, w, h), ilus(t)]
    c.append(texto(36, 60, ceja, 14, t["acento2"], 700, ' letter-spacing="2.4"'))
    c.append(texto(34, 108, titulo, 36, t["tinta"], 800))
    for j, linea in enumerate(desc):
        c.append(texto(36, 150 + j * 29, linea, 19, t["sub"]))
    x = 36
    for e in chips:
        s, cw = chip(t, x, 238, e)
        c.append(s)
        x += cw + 10
    guardar(f"{archivo}-{tema}.svg", svg(w, h, etiqueta, "\n".join(c)))


# ---------- Contacto ----------
def contacto(tema):
    t = TEMAS[tema]
    w, h = 1200, 220
    c = [tarjeta(t, w, h)]
    c.append(f'<rect x="0" y="0" width="6" height="{h}" fill="{t["acento"]}"/>')
    c.append(texto(64, 70, "PRIMERA CONSULTA SIN COSTO", 15, t["acento2"], 700, ' letter-spacing="3"'))
    c.append(texto(62, 124, "¿Platicamos tu proyecto?", 44, t["tinta"], 800))
    c.append(texto(64, 166, "Damos servicio a toda la República Mexicana.", 20, t["sub"]))
    c.append(f'<line x1="760" y1="44" x2="760" y2="176" stroke="{t["borde"]}" stroke-width="2"/>')
    filas = [("whatsapp", "81 2188 4423"), ("envelope", "contacto@isdelnorte.com"), ("location-dot", "Monterrey, NL, México")]
    for i, (ic, txt) in enumerate(filas):
        y = 58 + i * 44
        if ic == "whatsapp":
            c.append(f'<circle cx="811" cy="{y+11}" r="12" fill="#25D366"/>'
                     f'<path d="M805.5 {y+5.5}c.6-1 1.5-1 2-.2l1.4 2c.3.5.2 1.1-.2 1.5l-.8.7c.7 1.7 2 3 3.7 3.7l.7-.8c.4-.4 1-.5 1.5-.2l2 1.4c.8.5.8 1.4-.2 2-1.4 1-3.2 1.1-5.4-.3-1.9-1.2-3.4-2.7-4.6-4.6-1.4-2.2-1.3-4-.1-5.2z" fill="#fff"/>')
        else:
            c.append(icono_fa(ic, 800, y, 22, t["acento"]))
        c.append(texto(838, y + 18, txt, 20, t["tinta"], 700))
    guardar(f"contacto-{tema}.svg", svg(w, h, "¿Platicamos tu proyecto? Primera consulta sin costo. 81 2188 4423 · contacto@isdelnorte.com · Monterrey, NL", "\n".join(c)))


if __name__ == "__main__":
    banner()
    for tema in TEMAS:
        servicios(tema)
        producto(tema, "producto-finanzas", "APP · FINANZAS PERSONALES", "Mis Finanzas IS",
                 ["Cuentas, movimientos, pagos periódicos", "y reportes en un solo lugar."],
                 ["Web", "iOS", "Android"], ilus_finanzas, "Mis Finanzas IS: finanzas personales en web, iOS y Android")
        producto(tema, "producto-respaldo", "RECUPERACIÓN ANTE DESASTRES", "Respaldo Simple",
                 ["Backup cifrado para empresas con", "servidores físicos."],
                 ["AES-256", "Windows", "SQL Server"], ilus_respaldo, "Respaldo Simple: backup cifrado AES-256 para servidores Windows y SQL Server")
        contacto(tema)
    print("ok")
