"""Genera los SVG del perfil de la organización, con estilo tipo shadcn/ui.

Uso: python3 scripts/generar_svgs.py

- Todo sale en dos versiones, -claro y -oscuro; el README elige con <picture>
  según el tema de GitHub.
- Tipografía Geist embebida (GitHub muestra los SVG como <img> y ahí no cargan
  fuentes externas). Íconos de marca de Simple Icons en scripts/marcas/.
- Sin cifras ni datos nuevos: el texto sale del README original.
"""
import base64
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "profile", "assets")
FUENTES = os.path.join(RAIZ, "scripts", "fuentes")
MARCAS = os.path.join(RAIZ, "scripts", "marcas")

ACENTO = "#418ADC"
TEMAS = {
    "claro": dict(card="#FFFFFF", borde="#E4E4E7", fg="#09090B", muted="#71717A", mutedbg="#F4F4F5",
                  primario="#18181B", primario_fg="#FAFAFA", sombra="0.07", logo="logo.svg", logo_escala=2.45),
    "oscuro": dict(card="#0D1117", borde="#27272A", fg="#FAFAFA", muted="#A1A1AA", mutedbg="#18181B",
                   primario="#FAFAFA", primario_fg="#18181B", sombra="0", logo="logo_blanco.svg", logo_escala=0.3),
}
M = 4  # margen del lienzo para que quepa la sombra


def fuente(archivo, familia, peso):
    datos = base64.b64encode(open(os.path.join(FUENTES, archivo), "rb").read()).decode()
    return f"@font-face {{ font-family: '{familia}'; font-weight: {peso}; src: url(data:font/woff2;base64,{datos}) format('woff2'); }}"


def css(mono=False):
    reglas = [fuente(f"geist-{p}.woff2", "Geist", p) for p in (400, 500, 600)]
    if mono:
        reglas.append(fuente("geist-mono-400.woff2", "Geist Mono", 400))
    return "\n      ".join(reglas)


def svg(w, h, etiqueta, cuerpo, t, defs="", mono=False):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{etiqueta}">
  <defs>
    <style>
      {css(mono)}
      .s {{ font-family: 'Geist', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
      .m {{ font-family: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace; }}
    </style>
    <filter id="sombra" x="-5%" y="-5%" width="110%" height="120%">
      <feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-color="#000" flood-opacity="{t["sombra"]}"/>
    </filter>{defs}
  </defs>
{cuerpo}
</svg>
'''


def guardar(nombre, contenido):
    open(os.path.join(ASSETS, nombre), "w").write(contenido)


def texto(x, y, s, tam, color, peso=400, extra="", cls="s"):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{tam}" font-weight="{peso}" fill="{color}"{extra}>{s}</text>'


def tarjeta(t, x, y, w, h, r=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{t["card"]}" filter="url(#sombra)"/>'
            f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" rx="{r-0.5}" fill="none" stroke="{t["borde"]}"/>')


_METRICAS = {}


def ancho(s, tam, peso=500):
    """Ancho real del texto según las métricas de Geist."""
    if peso not in _METRICAS:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(FUENTES, f"geist-{peso}.woff2"))
        _METRICAS[peso] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _METRICAS[peso]
    return sum(hmtx[cmap[ord(ch)]][0] for ch in s if ord(ch) in cmap) * tam / upm


def insignia(t, x, y, s, variante="secundaria"):
    w = ancho(s, 15) + 24
    if variante == "contorno":
        fondo = f'fill="none" stroke="{t["borde"]}"'
    else:
        fondo = f'fill="{t["mutedbg"]}"'
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="7" {fondo}/>'
            + texto(f"{x + w/2:.0f}", y + 20.5, s, 15, t["fg"], 500, ' text-anchor="middle"')), w


# ---------- Íconos ----------
LUCIDE = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
}


def lucide(nombre, x, y, tam, color):
    return (f'<g transform="translate({x},{y}) scale({tam/24})" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{LUCIDE[nombre]}</g>')


def marca(nombre, x, y, tam, color):
    d = re.search(r' d="([^"]*)"', open(os.path.join(MARCAS, nombre + ".svg")).read()).group(1)
    return f'<path transform="translate({x},{y}) scale({tam/24})" fill="{color}" d="{d}"/>'


def ilustracion(nombre, t):
    """Íconos propios en una caja de 72×72: trazo en el color del texto y un solo toque de acento."""
    fg, a = t["fg"], ACENTO
    ln = f'fill="none" stroke="{fg}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
    sv = f'fill="{t["mutedbg"]}" stroke="{fg}" stroke-width="4" stroke-linejoin="round"'
    if nombre == "erp":
        return (f'<rect x="6" y="6" width="26" height="26" rx="6" fill="{a}"/>'
                f'<rect x="40" y="6" width="26" height="26" rx="6" {sv}/>'
                f'<rect x="6" y="40" width="26" height="26" rx="6" {sv}/>'
                f'<rect x="40" y="40" width="26" height="26" rx="6" {sv}/>')
    if nombre == "movil":
        return (f'<rect x="16" y="3" width="40" height="66" rx="9" {ln}/>'
                f'<rect x="25" y="14" width="22" height="14" rx="3" fill="{a}"/>'
                f'<path d="M25 38h22M25 47h14M31 60h10" {ln}/>')
    if nombre == "web":
        return (f'<rect x="3" y="9" width="66" height="54" rx="8" {ln}/>'
                f'<path d="M3 23h66" {ln}/>'
                f'<path d="M20 52V40M36 52V34" {ln}/><path d="M52 52V30" fill="none" stroke="{a}" stroke-width="5" stroke-linecap="round"/>')
    if nombre == "ecommerce":
        return (f'<path d="M12 24h48l4 42H8z" {ln}/>'
                f'<path d="M25 30V20a11 11 0 0 1 22 0v10" {ln}/>'
                f'<circle cx="36" cy="46" r="8" fill="{a}"/>')
    if nombre == "consultoria":
        return (f'<path d="M10 62c20 0 8-26 26-26s8-24 26-24" fill="none" stroke="{fg}" stroke-width="4" stroke-dasharray="1 8" stroke-linecap="round"/>'
                f'<circle cx="10" cy="62" r="6" {sv}/>'
                f'<circle cx="36" cy="36" r="6" {sv}/>'
                f'<path d="M60 32V6" {ln}/><path d="M60 7h10l-3.5 5 3.5 5H60z" fill="{a}"/>')
    raise ValueError(nombre)


def mosaico_icono(t, x, y, nombre, tam=64):
    return (f'<rect x="{x+0.5}" y="{y+0.5}" width="{tam-1}" height="{tam-1}" rx="10" fill="{t["card"]}" stroke="{t["borde"]}"/>'
            f'<g transform="translate({x + tam*0.2},{y + tam*0.2}) scale({tam*0.6/72})">{ilustracion(nombre, t)}</g>')


# ---------- Portada ----------
def portada(tema):
    t = TEMAS[tema]
    w, h = 1200, 340
    logo = open(os.path.join(ASSETS, t["logo"])).read()
    logo = logo[logo.index(">") + 1:logo.rindex("</svg>")].strip()
    defs = f'''
    <pattern id="rejilla" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{t["borde"]}" stroke-width="1"/>
    </pattern>
    <radialGradient id="desvanece" cx="0.78" cy="0.5" r="0.45">
      <stop offset="0" stop-color="#fff" stop-opacity="1"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="mascara"><rect width="{w}" height="{h}" fill="url(#desvanece)"/></mask>
    <clipPath id="recorte"><rect x="{M}" y="{M}" width="{w}" height="{h}" rx="12"/></clipPath>'''
    c = [tarjeta(t, M, M, w, h),
         f'<g clip-path="url(#recorte)"><rect x="{M}" y="{M}" width="{w}" height="{h}" fill="url(#rejilla)" mask="url(#mascara)"/></g>',
         f'<g transform="translate({M},{M})">']
    # anuncio
    s = "Desde 1999 · Monterrey, NL"
    pw = ancho(s, 16) + 46
    c.append(f'<rect x="56.5" y="54.5" width="{pw:.0f}" height="35" rx="17.5" fill="{t["card"]}" stroke="{t["borde"]}"/>')
    c.append(f'<circle cx="74" cy="72" r="4" fill="{ACENTO}"/>')
    c.append(texto(86, 78, s, 16, t["fg"], 500))
    c.append(texto(54, 158, "Software, ERP y apps", 54, t["fg"], 600, ' letter-spacing="-1.6"'))
    c.append(texto(54, 220, "para empresas mexicanas.", 54, t["muted"], 600, ' letter-spacing="-1.6"'))
    c.append(texto(56, 272, "Desarrollo a medida, Intelisis ERP y consultoría tecnológica.", 22, t["muted"]))
    # logo
    c.append(f'<rect x="830.5" y="88.5" width="300" height="164" rx="12" fill="{t["card"]}" stroke="{t["borde"]}"/>')
    c.append(f'<g transform="translate(860,112) scale({t["logo_escala"]})" fill="none">{logo}</g>')
    c.append(texto(980, 234, "SOLUCIONES TECNOLÓGICAS", 13, t["muted"], 500, ' text-anchor="middle" letter-spacing="3.5"'))
    c.append("</g>")
    guardar(f"portada-{tema}.svg", svg(w + 2*M, h + 2*M, "IS del Norte — Software, ERP y apps para empresas mexicanas. Desde 1999, Monterrey, NL", "\n".join(c), t, defs))


# ---------- Botones ----------
BOTONES = [
    ("whatsapp", "WhatsApp", ("marca", "whatsapp"), True),
    ("sitio", "isdelnorte.com", ("lucide", "globe"), False),
    ("linkedin", "LinkedIn", ("marca", "linkedin"), False),
    ("correo", "Correo", ("lucide", "mail"), False),
    ("appstore", "App Store", ("marca", "apple"), False),
    ("googleplay", "Google Play", ("marca", "googleplay"), False),
    ("web", "Versión web", ("lucide", "globe"), False),
]


def boton(tema, clave, etiqueta, ico, primario):
    t = TEMAS[tema]
    w = round(16 + 16 + 8 + ancho(etiqueta, 15) + 16)
    h = 40
    fondo, color = (t["primario"], t["primario_fg"]) if primario else (t["card"], t["fg"])
    c = [f'<rect x="{M}" y="{M}" width="{w}" height="{h}" rx="8" fill="{fondo}" filter="url(#sombra)"/>']
    if not primario:
        c.append(f'<rect x="{M+0.5}" y="{M+0.5}" width="{w-1}" height="{h-1}" rx="7.5" fill="none" stroke="{t["borde"]}"/>')
    tipo, nombre = ico
    c.append((marca if tipo == "marca" else lucide)(nombre, M + 16, M + 12, 16, color))
    c.append(texto(M + 40, M + 25.5, etiqueta, 15, color, 500))
    guardar(f"boton-{clave}-{tema}.svg", svg(w + 2*M, h + 2*M, etiqueta, "\n".join(c), t))


# ---------- Servicios ----------
SECUNDARIOS = [
    ("movil", "Aplicaciones móviles", ["Apps empresariales para iOS y Android", "desde una sola base de código."]),
    ("web", "Aplicaciones web", ["Sistemas a la medida que centralizan la", "operación y eliminan procesos manuales."]),
    ("ecommerce", "E-commerce", ["Tiendas en línea con pagos mexicanos (OXXO,", "SPEI, tarjetas) e integración de paqueterías."]),
    ("consultoria", "Consultoría", ["Diagnóstico de operación, plan de", "transformación digital e implementación."]),
]


def servicios(tema):
    t = TEMAS[tema]
    W, gap = 1200, 16
    c = []
    # destacado: Intelisis ERP
    hd = 140
    c.append(tarjeta(t, M, M, W, hd))
    c.append(mosaico_icono(t, M + 32, M + 38, "erp"))
    c.append(texto(M + 120, M + 64, "Intelisis ERP", 28, t["fg"], 600, ' letter-spacing="-0.5"'))
    c.append(texto(M + 120, M + 98, "Implementadores certificados con +19 años de experiencia.", 20, t["muted"]))
    x = M + W - 32
    for s in reversed(["Implementación", "Personalización", "Soporte"]):
        x -= ancho(s, 15) + 24
        sv, bw = insignia(t, x, M + 55, s)
        c.append(sv)
        x -= 8
    # 2×2
    cw, ch = (W - gap) / 2, 220
    for i, (il, titulo, desc) in enumerate(SECUNDARIOS):
        x0 = M + (i % 2) * (cw + gap)
        y0 = M + hd + gap + (i // 2) * (ch + gap)
        c.append(tarjeta(t, x0, y0, cw, ch))
        c.append(mosaico_icono(t, x0 + 32, y0 + 32, il))
        c.append(texto(x0 + 32, y0 + 136, titulo, 26, t["fg"], 600, ' letter-spacing="-0.4"'))
        for j, linea in enumerate(desc):
            c.append(texto(x0 + 32, y0 + 170 + j * 28, linea, 20, t["muted"]))
    H = hd + gap + 2 * ch + gap
    guardar(f"servicios-{tema}.svg", svg(W + 2*M, H + 2*M,
            "Qué hacemos: Intelisis ERP, aplicaciones móviles, aplicaciones web, e-commerce y consultoría", "\n".join(c), t))


# ---------- Producto ----------
def producto(tema):
    t = TEMAS[tema]
    w, h = 1200, 300
    defs = f'<clipPath id="recorte"><rect x="{M}" y="{M}" width="{w}" height="{h}" rx="12"/></clipPath>'
    c = [tarjeta(t, M, M, w, h), f'<g transform="translate({M},{M})">']
    s, bw = insignia(t, 56, 52, "App", "contorno")
    c.append(s)
    c.append(texto(56 + bw + 12, 73, "Finanzas personales", 17, t["muted"], 500))
    c.append(texto(54, 132, "Mis Finanzas IS", 44, t["fg"], 600, ' letter-spacing="-1.2"'))
    c.append(texto(56, 178, "Gestión de finanzas personales: múltiples cuentas,", 22, t["muted"]))
    c.append(texto(56, 210, "movimientos, pagos periódicos y reportes.", 22, t["muted"]))
    x = 56
    for e in ("Web", "iOS", "Android"):
        sv, bw = insignia(t, x, 240, e)
        c.append(sv)
        x += bw + 8
    c.append("</g>")
    # teléfono que se sale por abajo, recortado por la tarjeta
    fg, mu, a = t["fg"], t["muted"], ACENTO
    c.append(f'''<g clip-path="url(#recorte)"><g transform="translate({M+860},{M+44})">
      <rect x="0.5" y="0.5" width="250" height="330" rx="32" fill="{t["card"]}" stroke="{t["borde"]}" filter="url(#sombra)"/>
      <rect x="10.5" y="10.5" width="230" height="310" rx="24" fill="{t["mutedbg"]}" fill-opacity="0.6" stroke="{t["borde"]}"/>
      <rect x="95" y="20" width="60" height="8" rx="4" fill="{t["borde"]}"/>
      {texto(30, 66, "Saldo total", 13, mu, 500)}
      <rect x="30" y="78" width="132" height="22" rx="6" fill="{fg}"/>
      <path d="M30 186 L68 166 L100 174 L136 140 L168 150 L220 112 V214 H30 Z" fill="{a}" fill-opacity="0.12"/>
      <path d="M30 186 L68 166 L100 174 L136 140 L168 150 L220 112" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="220" cy="112" r="5" fill="{a}"/>
      <g fill="{t["card"]}" stroke="{t["borde"]}"><rect x="30.5" y="232.5" width="190" height="34" rx="8"/><rect x="30.5" y="274.5" width="190" height="34" rx="8"/></g>
      <circle cx="48" cy="250" r="6" fill="{a}"/><rect x="62" y="246" width="70" height="8" rx="4" fill="{mu}" fill-opacity="0.5"/>
      <circle cx="48" cy="292" r="6" fill="{mu}" fill-opacity="0.5"/><rect x="62" y="288" width="96" height="8" rx="4" fill="{mu}" fill-opacity="0.5"/>
    </g></g>''')
    guardar(f"producto-finanzas-{tema}.svg", svg(w + 2*M, h + 2*M, "Mis Finanzas IS: finanzas personales en web, iOS y Android", "\n".join(c), t, defs))


# ---------- Contacto ----------
def contacto(tema):
    t = TEMAS[tema]
    w, h = 1200, 210
    c = [tarjeta(t, M, M, w, h), f'<g transform="translate({M},{M})">']
    c.append(texto(54, 86, "¿Platicamos tu proyecto?", 36, t["fg"], 600, ' letter-spacing="-0.9"'))
    c.append(texto(56, 126, "Primera consulta sin costo.", 21, t["muted"]))
    c.append(texto(56, 156, "Damos servicio a toda la República Mexicana.", 21, t["muted"]))
    x0, x1 = 700, 1144
    filas = [("phone", "81 2188 4423"), ("mail", "contacto@isdelnorte.com"), ("pin", "Monterrey, NL, México")]
    for i, (ic, s) in enumerate(filas):
        y = 38 + i * 46
        if i:
            c.append(f'<line x1="{x0}" y1="{y-6}" x2="{x1}" y2="{y-6}" stroke="{t["borde"]}"/>')
        c.append(lucide(ic, x0, y + 8, 20, t["muted"]))
        c.append(texto(x0 + 34, y + 25, s, 20, t["fg"], 500))
    c.append("</g>")
    guardar(f"contacto-{tema}.svg", svg(w + 2*M, h + 2*M, "¿Platicamos tu proyecto? Primera consulta sin costo. 81 2188 4423 · contacto@isdelnorte.com · Monterrey, NL", "\n".join(c), t))


if __name__ == "__main__":
    for tema in TEMAS:
        portada(tema)
        servicios(tema)
        producto(tema)
        contacto(tema)
        for b in BOTONES:
            boton(tema, *b)
    print("ok")
