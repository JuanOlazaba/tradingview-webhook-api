"""Biblioteca de ilustraciones profesionales de Finroots (SVG de marca, animables).

Estilo: trazo tinta #15120e de 4 px redondeado, colores planos de marca, sombra suave en el suelo.
Partes animadas con clases del motor: dw (se dibuja), pop (aparece), grow (crece), bob (flota).
Los agentes las combinan con el objeto `art`; no hace falta dibujar desde cero.
"""

INK, CO, BL, AM, CR, WH = "#15120e", "#e0522f", "#2c4fb5", "#f2b84b", "#f3ede2", "#ffffff"
S = f'stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'
SHADOW = f'<ellipse cx="100" cy="184" rx="62" ry="7" fill="{INK}" opacity=".10"/>'


def _svg(body: str) -> str:
    return f'<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">{SHADOW}{body}</svg>'


ASSETS = {
    # ---------------------------------------------------------------- fundamentos
    "umbrella": ("Paraguas que protege de la lluvia (fondo de emergencia, protección)", _svg(
        f'<g class="pop" style="--at:.2s"><path d="M28 98 Q100 18 172 98 Q154 86 136 98 Q118 86 100 98 Q82 86 64 98 Q46 86 28 98Z" fill="{BL}" {S}/>'
        f'<path d="M100 40 Q86 70 100 98 M100 40 Q114 70 100 98" fill="none" stroke="{INK}" stroke-width="3" opacity=".35"/></g>'
        f'<path class="grow" style="--at:.6s" d="M100 98 V158 q0 14 -14 14 q-12 0 -12 -12" fill="none" {S}/>'
        f'<g class="bob" style="--at:.0s" fill="{BL}" opacity=".55"><path d="M40 20 l-6 14"/><path d="M40 20 q-4 8 0 12 q4 -4 0 -12Z"/>'
        f'<path d="M150 14 q-4 8 0 12 q4 -4 0 -12Z"/><path d="M178 44 q-4 8 0 12 q4 -4 0 -12Z"/><path d="M18 58 q-4 8 0 12 q4 -4 0 -12Z"/></g>'
        f'<g class="pop" style="--at:1.1s"><circle cx="128" cy="150" r="16" fill="{AM}" {S}/><text x="128" y="156" text-anchor="middle" font-family="Anton" font-size="18" fill="{INK}">€</text></g>')),
    "shield": ("Escudo con euro (seguridad, protección del dinero)", _svg(
        f'<path class="pop" style="--at:.2s" d="M100 22 L160 44 V96 Q160 146 100 172 Q40 146 40 96 V44Z" fill="{BL}" {S}/>'
        f'<path d="M100 36 L148 54 V96 Q148 136 100 158Z" fill="#fff" opacity=".18"/>'
        f'<g class="pop" style="--at:.8s"><circle cx="100" cy="98" r="30" fill="{AM}" {S}/>'
        f'<text x="100" y="111" text-anchor="middle" font-family="Anton" font-size="36" fill="{INK}">€</text></g>'
        f'<path class="dw" pathLength="1" style="--at:1.3s" d="M28 70 q-10 30 4 60 M172 70 q10 30 -4 60" fill="none" stroke="{AM}" stroke-width="5" stroke-linecap="round"/>')),
    "jar": ("Tarro de cristal con monedas que se llena (ahorro)", _svg(
        f'<rect x="56" y="38" width="88" height="16" rx="5" fill="{CO}" {S}/>'
        f'<path d="M60 54 H140 Q156 64 156 84 V160 Q156 176 140 176 H60 Q44 176 44 160 V84 Q44 64 60 54Z" fill="#fff" fill-opacity=".55" {S}/>'
        f'<g class="grow" style="--at:.5s"><path d="M48 128 H152 V160 Q152 172 140 172 H60 Q48 172 48 160Z" fill="{AM}"/>'
        f'<circle cx="74" cy="124" r="11" fill="{AM}" {S}/><circle cx="100" cy="118" r="11" fill="{AM}" {S}/><circle cx="126" cy="124" r="11" fill="{AM}" {S}/></g>'
        f'<g class="pop" style="--at:1.3s"><circle cx="112" cy="96" r="11" fill="{AM}" {S}/></g>'
        f'<path d="M58 70 V150" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".8"/>')),
    "wallet": ("Cartera con billetes (dinero disponible, gasto)", _svg(
        f'<g class="pop" style="--at:.5s"><rect x="54" y="40" width="80" height="44" rx="6" fill="{AM}" {S} transform="rotate(-10 94 62)"/>'
        f'<rect x="70" y="34" width="80" height="44" rx="6" fill="#f6d27a" {S} transform="rotate(6 110 56)"/></g>'
        f'<rect x="30" y="70" width="140" height="100" rx="16" fill="{INK}"/>'
        f'<rect x="30" y="70" width="140" height="100" rx="16" fill="none" {S}/>'
        f'<rect x="112" y="102" width="62" height="36" rx="10" fill="{CO}" {S}/><circle cx="130" cy="120" r="6" fill="#fff"/>')),
    "calendar_alert": ("Calendario con una fecha marcada (gasto imprevisto, vencimiento)", _svg(
        f'<rect x="34" y="40" width="132" height="132" rx="14" fill="#fff" {S}/>'
        f'<path d="M34 54 Q34 40 48 40 H152 Q166 40 166 54 V74 H34Z" fill="{CO}" {S}/>'
        f'<path d="M66 28 V52 M134 28 V52" {S} fill="none"/>'
        + "".join(f'<rect x="{50+c*26}" y="{88+r*24}" width="16" height="14" rx="3" fill="{CR}"/>' for r in range(3) for c in range(4))
        + f'<g class="pop" style="--at:.9s"><circle cx="128" cy="119" r="18" fill="none" stroke="{CO}" stroke-width="5"/></g>'
        f'<g class="pop" style="--at:1.4s"><circle cx="160" cy="44" r="16" fill="{AM}" {S}/><path d="M160 34 V46 M160 52 V53" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g>')),
    "broken_car": ("Coche averiado echando humo (imprevisto, gasto inesperado)", _svg(
        f'<path d="M28 136 V118 Q28 106 40 104 L62 100 L80 72 Q84 66 92 66 H134 Q142 66 146 72 L162 100 Q174 102 174 114 V136Z" fill="{CO}" {S}/>'
        f'<path d="M88 76 H130 L144 100 H76Z" fill="#cfdaf5" {S}/>'
        f'<circle cx="62" cy="140" r="16" fill="{INK}"/><circle cx="62" cy="140" r="6" fill="{CR}"/>'
        f'<circle cx="142" cy="140" r="16" fill="{INK}"/><circle cx="142" cy="140" r="6" fill="{CR}"/>'
        f'<g class="bob" fill="#d5c9b3"><circle cx="40" cy="78" r="12"/><circle cx="30" cy="58" r="9"/><circle cx="42" cy="40" r="7"/></g>'
        f'<g class="pop" style="--at:.8s"><path d="M150 40 L172 78 H128Z" fill="{AM}" {S}/><path d="M150 54 V66 M150 72 V73" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g>')),
    "house": ("Casa (vivienda, inmobiliario, patrimonio)", _svg(
        f'<path d="M40 96 L100 46 L160 96 V172 H40Z" fill="#fff" {S}/>'
        f'<path class="pop" style="--at:.3s" d="M28 102 L100 40 L172 102" fill="none" stroke="{CO}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="86" y="122" width="28" height="50" rx="4" fill="{BL}" {S}/>'
        f'<rect x="54" y="110" width="22" height="22" rx="3" fill="{AM}" {S}/><rect x="124" y="110" width="22" height="22" rx="3" fill="{AM}" {S}/>'
        f'<rect x="130" y="52" width="14" height="28" fill="{INK}"/>')),
    "credit_card": ("Tarjeta de crédito (deuda, pago aplazado)", _svg(
        f'<g class="pop" style="--at:.2s" transform="rotate(-8 100 105)"><rect x="24" y="58" width="152" height="96" rx="14" fill="{BL}" {S}/>'
        f'<rect x="24" y="78" width="152" height="18" fill="{INK}"/>'
        f'<rect x="40" y="108" width="28" height="20" rx="4" fill="{AM}" {S}/>'
        f'<path d="M80 136 H156" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/></g>'
        f'<g class="pop" style="--at:1s"><circle cx="160" cy="54" r="20" fill="{CO}" {S}/><text x="160" y="62" text-anchor="middle" font-family="Anton" font-size="22" fill="#fff">%</text></g>')),
    "scale": ("Balanza (comparar, equilibrio riesgo/rentabilidad)", _svg(
        f'<path d="M100 40 V164 M70 172 H130" fill="none" {S}/>'
        f'<g class="bob"><path d="M40 70 H160" fill="none" {S}/>'
        f'<path d="M40 70 L22 116 H58Z M160 70 L142 116 H178Z" fill="none" stroke="{INK}" stroke-width="3"/>'
        f'<path d="M18 116 H62 Q60 132 40 132 Q20 132 18 116Z" fill="{AM}" {S}/><path d="M138 116 H182 Q180 132 160 132 Q140 132 138 116Z" fill="{BL}" {S}/></g>'
        f'<circle cx="100" cy="40" r="9" fill="{CO}" {S}/>')),
    "hourglass": ("Reloj de arena (tiempo, plazo, paciencia)", _svg(
        f'<rect x="52" y="26" width="96" height="14" rx="5" fill="{INK}"/><rect x="52" y="160" width="96" height="14" rx="5" fill="{INK}"/>'
        f'<path d="M62 40 Q62 86 100 100 Q138 86 138 40Z M62 160 Q62 114 100 100 Q138 114 138 160Z" fill="#fff" fill-opacity=".6" {S}/>'
        f'<path d="M74 52 Q80 82 100 92 Q120 82 126 52Z" fill="{AM}"/>'
        f'<path class="grow" style="--at:.4s;--d:2s" d="M70 158 Q74 128 100 120 Q126 128 130 158Z" fill="{AM}"/>'
        f'<path class="dw" pathLength="1" style="--at:.2s" d="M100 96 V150" stroke="{AM}" stroke-width="3" stroke-dasharray="1"/>')),
    "bank": ("Banco con columnas (sistema financiero, depósitos)", _svg(
        f'<path d="M26 72 L100 30 L174 72Z" fill="{BL}" {S}/><rect x="34" y="72" width="132" height="12" fill="#fff" {S}/>'
        + "".join(f'<rect class="grow" style="--at:{.2+i*.12:.2f}s" x="{46+i*30}" y="88" width="16" height="62" rx="3" fill="#fff" {S}/>' for i in range(4))
        + f'<rect x="26" y="150" width="148" height="20" rx="4" fill="{INK}"/>'
        f'<g class="pop" style="--at:1s"><circle cx="100" cy="56" r="10" fill="{AM}" {S}/></g>')),
    "vault": ("Caja fuerte (guardar a salvo, liquidez inmediata)", _svg(
        f'<rect x="32" y="34" width="136" height="136" rx="14" fill="#8f99ad" {S}/><rect x="46" y="48" width="108" height="108" rx="8" fill="#b7c0d1" {S}/>'
        f'<g class="pop" style="--at:.4s"><circle cx="100" cy="102" r="30" fill="{CR}" {S}/>'
        f'<path class="dw" pathLength="1" style="--at:.7s" d="M100 72 V132 M70 102 H130" stroke="{INK}" stroke-width="5"/>'
        f'<circle cx="100" cy="102" r="8" fill="{CO}"/></g><rect x="150" y="70" width="10" height="26" rx="3" fill="{INK}"/>')),
    "candles": ("Gráfico de velas de bolsa que sube (acciones, renta variable)", _svg(
        f'<rect x="24" y="26" width="152" height="148" rx="12" fill="#fff" {S}/>'
        + "".join(f'<g class="grow" style="--at:{.2+i*.15:.2f}s"><path d="M{44+i*24} {y1} V{y2}" stroke="{INK}" stroke-width="3"/>'
                  f'<rect x="{37+i*24}" y="{b1}" width="14" height="{bh}" rx="2" fill="{c}" stroke="{INK}" stroke-width="2.5"/></g>'
                  for i, (y1, y2, b1, bh, c) in enumerate([(120, 160, 128, 24, CO), (104, 150, 112, 28, "#1f8a5b"), (110, 146, 118, 18, CO),
                                                          (78, 128, 86, 30, "#1f8a5b"), (64, 112, 70, 32, "#1f8a5b"), (44, 92, 50, 30, "#1f8a5b")]))
        + f'<path class="dw" pathLength="1" style="--at:1.2s" d="M40 150 L84 118 L116 112 L160 52" fill="none" stroke="{BL}" stroke-width="4" stroke-linecap="round"/>')),
    "company_share": ("Edificio de empresa con un trozo destacado (ser dueño de una parte: acción)", _svg(
        f'<rect x="50" y="44" width="100" height="128" rx="6" fill="#fff" {S}/>'
        + "".join(f'<rect x="{62+c*28}" y="{58+r*26}" width="18" height="16" rx="2" fill="#cfdaf5"/>' for r in range(4) for c in range(3))
        + f'<g class="pop" style="--at:.8s"><rect x="62" y="110" width="18" height="16" rx="2" fill="{AM}" stroke="{INK}" stroke-width="3"/></g>'
        f'<rect x="88" y="146" width="24" height="26" fill="{BL}" {S}/>'
        f'<g class="pop" style="--at:1.3s"><circle cx="152" cy="52" r="20" fill="{AM}" {S}/><text x="152" y="60" text-anchor="middle" font-family="Anton" font-size="18" fill="{INK}">1/n</text></g>')),
    "bond": ("Certificado de bono con sello y cupones (renta fija)", _svg(
        f'<rect x="30" y="34" width="140" height="120" rx="6" fill="#fff7e3" {S}/><rect x="40" y="44" width="120" height="100" rx="3" fill="none" stroke="{AM}" stroke-width="3"/>'
        f'<path d="M56 66 H144 M56 82 H128" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
        + "".join(f'<g class="pop" style="--at:{.5+i*.25:.2f}s"><rect x="{44+i*40}" y="152" width="32" height="24" rx="3" fill="{AM}" {S}/></g>' for i in range(3))
        + f'<g class="pop" style="--at:1.4s"><circle cx="138" cy="116" r="18" fill="{CO}" {S}/><path d="M130 134 l-6 14 l14 -6 l14 6 l-6 -14" fill="{CO}" stroke="{INK}" stroke-width="3"/></g>')),
    "globe": ("Globo terráqueo (diversificar por el mundo, índices globales)", _svg(
        f'<circle class="pop" style="--at:.2s" cx="100" cy="98" r="64" fill="{BL}" {S}/>'
        f'<path d="M62 70 Q78 60 90 72 Q96 86 82 92 Q70 96 66 110 Q56 98 62 70Z M112 50 Q132 54 140 72 Q128 76 120 70 Q108 66 112 50Z M118 104 Q138 100 150 112 Q144 140 124 150 Q114 132 118 104Z" fill="#1f8a5b" stroke="{INK}" stroke-width="3"/>'
        f'<path class="dw" pathLength="1" style="--at:.8s" d="M24 120 Q100 170 176 76" fill="none" stroke="{AM}" stroke-width="5" stroke-linecap="round"/>')),
    "rocket": ("Cohete despegando (startup, venture capital, crecimiento)", _svg(
        f'<g class="bob"><path d="M100 24 Q132 52 130 110 H70 Q68 52 100 24Z" fill="#fff" {S}/>'
        f'<circle cx="100" cy="72" r="13" fill="#cfdaf5" {S}/><path d="M70 92 L48 124 L72 118Z M130 92 L152 124 L128 118Z" fill="{CO}" {S}/>'
        f'<path d="M82 110 H118 L110 126 H90Z" fill="{INK}"/>'
        f'<path class="grow" style="--at:.2s" d="M88 128 Q100 172 112 128Z" fill="{AM}"/></g>')),
    "wine": ("Botella y copa de vino (alternativos: vino, coleccionables)", _svg(
        f'<path d="M66 34 H86 V66 Q102 78 102 98 V166 Q102 174 94 174 H58 Q50 174 50 166 V98 Q50 78 66 66Z" fill="#7a1f2b" {S}/>'
        f'<rect x="54" y="110" width="44" height="34" rx="4" fill="{CR}" {S}/>'
        f'<g class="pop" style="--at:.7s"><path d="M120 80 H170 Q170 118 145 120 Q120 118 120 80Z" fill="#fff" fill-opacity=".7" {S}/>'
        f'<path d="M124 96 H166 Q162 116 145 116 Q128 116 124 96Z" fill="#a8323f"/>'
        f'<path d="M145 120 V160 M128 166 H162" fill="none" {S}/></g>')),
    "painting": ("Cuadro enmarcado en la pared (arte como inversión)", _svg(
        f'<rect x="30" y="34" width="140" height="120" rx="4" fill="#c98a1c" {S}/><rect x="44" y="48" width="112" height="92" fill="#fff" {S}/>'
        f'<circle class="pop" style="--at:.4s" cx="128" cy="74" r="12" fill="{AM}"/>'
        f'<path class="grow" style="--at:.7s" d="M44 140 L82 92 L106 120 L124 102 L156 140Z" fill="{BL}" stroke="{INK}" stroke-width="3"/>'
        f'<g class="pop" style="--at:1.3s"><rect x="118" y="156" width="56" height="22" rx="4" fill="{INK}"/>'
        f'<text x="146" y="172" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="12" fill="#fff">LOTE 27</text></g>')),
    "factory": ("Fábrica/empresa privada (private equity, deuda privada)", _svg(
        f'<path d="M26 172 V100 L66 76 V100 L106 76 V100 L146 76 V172Z" fill="#fff" {S}/>'
        f'<rect x="146" y="44" width="22" height="128" fill="{CO}" {S}/>'
        + "".join(f'<rect x="{40+i*36}" y="118" width="20" height="18" rx="2" fill="{AM}" stroke="{INK}" stroke-width="3"/>' for i in range(3))
        + f'<g class="bob" fill="#d5c9b3"><circle cx="160" cy="30" r="10"/><circle cx="176" cy="16" r="7"/></g>'
        f'<path d="M20 172 H180" {S}/>')),
    "lock_key": ("Candado y llave (dinero bloqueado, iliquidez, permanencia)", _svg(
        f'<path d="M68 92 V66 Q68 34 100 34 Q132 34 132 66 V92" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
        f'<rect class="pop" style="--at:.2s" x="50" y="90" width="100" height="82" rx="14" fill="{AM}" {S}/>'
        f'<circle cx="100" cy="124" r="11" fill="{INK}"/><path d="M100 128 V150" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
        f'<g class="pop" style="--at:1s" transform="rotate(-30 160 150)"><circle cx="160" cy="150" r="14" fill="none" stroke="{BL}" stroke-width="7"/>'
        f'<path d="M174 150 H196 M188 150 V160" stroke="{BL}" stroke-width="7" stroke-linecap="round"/></g>')),
    "phone_bank": ("Móvil con app del banco y aviso (notificación, saldo)", _svg(
        f'<rect x="58" y="22" width="84" height="156" rx="16" fill="{INK}"/><rect x="64" y="34" width="72" height="132" rx="9" fill="#fbf8f2"/>'
        f'<path d="M72 60 H112" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M72 76 H98" stroke="#c9bfad" stroke-width="4" stroke-linecap="round"/>'
        f'<rect class="grow" style="--at:.4s" x="72" y="96" width="14" height="50" rx="3" fill="{BL}"/><rect class="grow" style="--at:.55s" x="92" y="112" width="14" height="34" rx="3" fill="{AM}"/>'
        f'<rect class="grow" style="--at:.7s" x="112" y="104" width="14" height="42" rx="3" fill="{CO}"/>'
        f'<g class="pop" style="--at:1.2s"><rect x="96" y="30" width="78" height="30" rx="10" fill="#fff" {S}/><circle cx="110" cy="45" r="6" fill="{CO}"/>'
        f'<path d="M122 41 H162 M122 50 H148" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>')),
}


def catalog_text() -> str:
    return "\n".join(f"  · {k}: {v[0]}" for k, v in ASSETS.items())


def svg(name: str) -> str:
    return ASSETS[name][1]
