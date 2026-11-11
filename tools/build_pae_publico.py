"""
Arma la versión pública de la presentación PAE Orinoquía–Amazonía a partir de la
versión de trabajo (la que publicó el chat del servidor como artifact).

Qué cambia frente a la versión de trabajo:
- Se quita la «cocina» del proyecto: etiquetas de estado, escenarios de cómputo,
  presupuestos de disco, tablas de datos pendientes y notas de descarga.
- Se ordena en seis preguntas: qué pasó, cuánto llueve normalmente, si 2017 fue
  raro, de dónde viene la humedad, cómo fue la tormenta y con cuánta anticipación
  se reconoce. Las dos últimas diapositivas de anticipación y el cierre son nuevas.
- Las regiones se nombran por lo que son (no R1…R6).

Uso:
    python tools/build_pae_publico.py <index.html de trabajo> docs/pae/index.html
"""
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text(encoding="utf-8")


def section(sid):
    m = re.search(rf'<section class="slide[^"]*" id="{sid}".*?</section>\n*', html, re.S)
    assert m, sid
    return m


def drop(*ids):
    global html
    for sid in ids:
        html = html.replace(section(sid).group(0), "")


def sub(old, new, count=1):
    global html
    assert html.count(old) >= 1, old[:80]
    html = html.replace(old, new, count)


def sec(sid, label):
    global html
    html = re.sub(rf'(id="{sid}"[^>]*data-sec=")[^"]+"', rf'\g<1>{label}"', html)


# ── 1. diapositivas que salen ────────────────────────────────────────────────
drop("s-clima", "cl-repaso", "s-anom", "an-indices", "an-estados", "an-repaso",
     "s-fuentes", "fs-escenarios", "fs-region", "fs-salidas",
     "s-extremos", "ex-umbral", "ex-repaso", "s-scm")

# ── 2. secciones nuevas en el encabezado ─────────────────────────────────────
NAV = [("ev-noche", "1", "Qué pasó"), ("cl-columna", "2", "Lluvia normal"), ("an-z", "3", "¿2017 fue raro?"),
       ("fs-hoyos", "4", "Origen de la humedad"), ("ex-2017", "5", "La tormenta"), ("pr-tiempo", "6", "Anticipación")]
html = re.sub(r'<nav class="series" aria-label="Secciones">.*?</nav>',
              '<nav class="series" aria-label="Secciones">' + "".join(
                  f'<button type="button" class="mod" data-go="{g}"><span>{n}</span> {t}</button>' for g, n, t in NAV)
              + "</nav>", html, flags=re.S)
for sid in ("s-problema", "p-regiones"):
    sec(sid, "1 · Qué pasó")
for sid in ("cl-columna", "cl-mapa", "cl-mocoa"):
    sec(sid, "2 · Cuánto llueve normalmente")
for sid in ("an-z", "an-anom", "an-tele"):
    sec(sid, "3 · ¿Fue 2017 un año raro?")
sec("fs-hoyos", "4 · De dónde viene la humedad")
for sid in ("ex-2017", "scm-goes"):
    sec(sid, "5 · Cómo fue la tormenta")

# el botón activo del encabezado ya dice la sección; la etiqueta de texto quedaba cortada a su lado
sub("""header.top .sec b{color:var(--fg);font-weight:500}""", """header.top .sec b{color:var(--fg);font-weight:500}
header.top .sec{display:none}""")

# ── 3. portada y contenido ───────────────────────────────────────────────────
sub("detonó una avenida torrencial con unas 330 víctimas.", "detonó una avenida torrencial en la que murieron más de 300 personas.")
sub("""<p class="tryit" style="margin:0">mueve el cursor por la pantalla: el fondo es el transporte de vapor real y el cursor, un sistema convectivo que lo hace converger; quieto sobre el piedemonte, su yunque frío crece.</p>""",
    """<p class="tryit" style="margin:0">mueve el cursor por la pantalla. Cada partícula es vapor de agua que viaja con el viento real (ERA5, promedio 1991–2020); el cursor es una tormenta que lo atrae. Déjalo quieto sobre Mocoa y mira crecer la nube.</p>""")
sub("""<h2>Seis secciones, de la escala regional a la cuenca</h2>
  <p class="note">Haz clic en un título para ir a esa diapositiva. Presentación interactiva con el sistema PAE de Carlos D. Hoyos (Universidad Nacional de Colombia); términos clave en español con el término en inglés <span class="en">(in English)</span>. Las etiquetas de estado se actualizan a medida que avanza el trabajo.</p>""",
    """<h2>Seis preguntas, de la noche del desastre a su anticipación</h2>
  <p class="note">Haz clic en un título para ir a esa diapositiva, o avanza con las flechas del teclado. Cada diapositiva tiene algo para mover o hacer clic, marcado con «Prueba esto». Presentación hecha con el sistema PAE de Carlos D. Hoyos (Universidad Nacional de Colombia).</p>""")
sub("""const PHASES = [""", """const PHASES_WORK = [""")
sub("""demo("cover", slide => {
  $("#pcCards").innerHTML = PHASES.map(([id, t, d, st, lab]) => `<button class="pick" type="button" data-go="${id}"><b>${t}</b><span>${d}</span><span class="tag ${st}">${lab}</span></button>`).join("");""",
    """const PHASES = [
  ["ev-noche", "1 · ¿Qué pasó?", "La noche del 31 de marzo de 2017, hora a hora."],
  ["cl-columna", "2 · ¿Cuánto llueve normalmente?", "Y por qué la mayor parte del agua llega de fuera."],
  ["an-z", "3 · ¿Fue 2017 un año raro?", "Temporada normal, evento extraordinario."],
  ["fs-hoyos", "4 · ¿De dónde viene la humedad?", "Orinoquía, Amazonía y Atlántico."],
  ["ex-2017", "5 · ¿Cómo fue la tormenta?", "Lo que vieron el satélite y la lluvia cada media hora."],
  ["pr-tiempo", "6 · ¿Con cuánta anticipación?", "Qué señales aparecen antes y cuánto antes."]];
demo("cover", slide => {
  $("#pcCards").innerHTML = PHASES.map(([id, t, d]) => `<button class="pick" type="button" data-go="${id}"><b>${t}</b><span>${d}</span></button>`).join("");""")

# regiones con nombres claros (también cambia el texto al pasar el cursor por los mapas)
sub("""<script>/* common/core.js */""", """<script>/* nombres de las regiones para la versión pública */
(function () {
  const R = window.__EMB && window.__EMB.geo && window.__EMB.geo.regions; if (!R) return;
  const N = {
    R1: ["Orinoquía y Amazonía", "Los mapas de lluvia y de anomalías cubren esta región."],
    R2: ["Norte de Sudamérica", "El marco amplio de la circulación que trae la humedad."],
    R4: ["Región de Mocoa", "Donde se mide si la lluvia fue extrema y adonde llega la humedad (Martinez et al., 2024)."],
    R6: ["Cuenca de Mocoa", "Las quebradas que crecieron esa noche: Mulato, Sangoyaco, Taruca y el alto río Mocoa."],
    C34: ["Chorro del Orinoco", "Donde se mide el viento de capas bajas que trae humedad desde los Llanos (Martinez et al., 2024; Robledo et al., 2026)."]};
  Object.entries(N).forEach(([k, [n, u]]) => { if (R[k]) { R[k].name = n; R[k].use = u; } });
})();
</script>
<script>/* common/core.js */""")

# ── 4. sección 1: la cadena sin etiquetas de estado ─────────────────────────
sub("""<p class="kicker k-data">1 · El problema · <span class="en">research question</span></p>""",
    """<p class="kicker k-data">1 · La pregunta</p>""")
sub("""<p class="tryit">haz clic en un eslabón: a la derecha aparece qué se sabe, qué hace este PAE y en qué sección.</p>""",
    """<p class="tryit">haz clic en un eslabón: a la derecha aparece qué se sabe y qué estudia este trabajo.</p>""")
sub("""<p class="note">Se buscan precursores, escalas de anticipación y probabilidades condicionales, no umbrales de alerta. Periodo base 1991–2020 (OMM).</p>""",
    """<p class="note">No se busca un sistema de alerta, sino entender qué condiciones hacen más probable un aguacero así y cuánto antes se pueden reconocer. «Normal» se mide siempre contra 1991–2020, el periodo de referencia de la Organización Meteorológica Mundial.</p>""")
sub("""`<button class="pick" type="button" data-i="${i}" aria-pressed="${i === sel}" style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px"><b>${t}</b><span class="tag ${st}">sección ${sec}</span></button>`""",
    """`<button class="pick" type="button" data-i="${i}" aria-pressed="${i === sel}" style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px"><b>${t}</b><span class="note">${sec}</span></button>`""")
sub("""<p style="margin:6px 0"><b>Lo que hace este PAE.</b> ${here}</p>
      <p style="margin:10px 0 0"><button class="btn" type="button" data-go="${id}">Ir a la sección ${sec} →</button> <span class="tag ${st}">${TAGS[st]}</span></p>`;""",
    """<p style="margin:6px 0"><b>Lo que estudia este trabajo.</b> ${here}</p>
      <p style="margin:10px 0 0"><button class="btn" type="button" data-go="${id}">Ver la sección ${sec} →</button></p>`;""")
# eslabones: secciones del nuevo orden y textos sin «pendiente de descarga»
for old, new in [('"s-anom", "prog", "3"', '"an-z", "prog", "3"'), ('"s-fuentes", "dec", "4"', '"fs-hoyos", "dec", "4"'),
                 ('"s-extremos", "pend", "5"', '"pr-tiempo", "pend", "6"'), ('"scm-goes", "prog", "6"', '"scm-goes", "prog", "5"'),
                 ('"s-scm", "pend", "6"', '"scm-goes", "pend", "5"'), ('"s-extremos", "prog", "5"', '"ex-2017", "prog", "5"')]:
    sub(old, new)
sub('"Repetir el rastreo con Mocoa como destino. El método (FLEXPART, WAM-2layers o ambos) es la decisión pendiente."',
    '"Repetir ese rastreo con Mocoa como destino: seguir el aire hacia atrás y sumar dónde ganó humedad."')
sub('"Índices horarios del chorro en 1991–2020 y su estado en los días extremos (ERA5, pendiente de descarga)."',
    '"Cuánto antes se intensifica el chorro en los días extremos, comparado con un día normal."')
sub('"Rastreo del sistema con los criterios de Robledo y su relación con el chorro y la humedad."',
    '"Seguir la tormenta en las imágenes del satélite GOES-16, desde que nace hasta que llega a Mocoa."')
sub('"Catálogo de extremos con IMERG, CHIRPS y lluvia antecedente, y compuestos de los días extremos."',
    '"Comparar la lluvia de satélite con la de las estaciones y ver qué tan bien se registra un aguacero así."')

# regiones: solo cuatro, con nombres
sub("""<h2>Cada pregunta tiene su escala: del Atlántico tropical a una cuenca de 357 km²</h2>""",
    """<h2>De dónde viene el agua hasta dónde cae: cuatro regiones, de los Llanos a una cuenca de 357 km²</h2>""")
sub("""<p class="kicker k-data">Regiones de trabajo · <span class="en">study domains</span></p>""",
    """<p class="kicker k-data">Dónde se mira</p>""")
sub("""const KEYS = ["R1", "R2", "R4", "R6", "C34", "C3", "C4", "RB2"];""", """const KEYS = ["R1", "C34", "R4", "R6"];""")
sub("""<p class="tryit">elige una región: el recuadro se resalta y abajo aparece para qué se usa. Pasa el cursor por los otros recuadros.</p>""",
    """<p class="tryit">elige una región: su recuadro se pone rojo en el mapa y abajo aparece para qué sirve.</p>""")
sub("""<p class="note" style="margin:4px 0 0">Costas, fronteras y ríos principales: Natural Earth 1:50 m. R3 (110–10 °W, 35 °S–35 °N) es más grande que el mapa.</p>""",
    """<p class="note" style="margin:4px 0 0">Costas, fronteras y ríos principales: Natural Earth 1:50 m.</p>""")

# ── 5. secciones 2 y 3: kickers sin jerga ────────────────────────────────────
sub("""<p class="kicker k-data">El balance de la columna · <span class="en">P − E = −∇·Q − ∂W/∂t</span></p>""",
    """<p class="kicker k-data">2 · Cuánto llueve normalmente · el balance del agua</p>""")
sub("""<p class="kicker k-data">Explorador de climatología · <span class="en">CHIRPS y ERA5, 1991–2020</span></p>""",
    """<p class="kicker k-data">El mapa de la lluvia normal · CHIRPS y ERA5, 1991–2020</p>""")
sub("""<p class="kicker k-data">Balance en la región de Mocoa · <span class="en">R4, 77,75–75,25 °W, 0–2 °N</span></p>""",
    """<p class="kicker k-data">El balance en la región de Mocoa</p>""")
sub("""<p class="kicker k-arch">Anomalía estandarizada · <span class="en">z-score</span></p>""",
    """<p class="kicker k-arch">3 · ¿Fue 2017 un año raro? · anomalía estandarizada</p>""")
sub("""<p class="kicker k-arch">Anomalías estandarizadas · <span class="en">standardized anomalies, CHIRPS y ERA5</span></p>""",
    """<p class="kicker k-arch">El mapa de lo raro · CHIRPS y ERA5</p>""")
sub("""<p class="kicker k-arch">Teleconexión con Niño 3.4 · <span class="en">seasonal correlation, CHIRPS y ERA5, 1991–2020</span></p>""",
    """<p class="kicker k-arch">El papel de El Niño · correlación con el Pacífico, 1991–2020</p>""")

# ── 6. sección 4: lo que se sabe y lo que se medirá ─────────────────────────
sub("""<p class="kicker k-arch">Lo que ya sabemos · <span class="en">Hoyos (2017), tablas 4 y 5</span></p>""",
    """<p class="kicker k-arch">4 · De dónde viene la humedad · lo que ya se sabe</p>""")
sub("""<ul class="pts" id="fhPts"></ul>""",
    """<ul class="pts" id="fhPts"></ul>
      <div class="callout violet"><b>Lo que medirá este trabajo.</b> El mismo rastreo con Mocoa como destino: seguir el aire unos 10 días hacia atrás y sumar dónde ganó humedad, en los días normales y en los extremos. Cuando esté listo, aquí aparecerá su mapa de fuentes.</div>""")

# ── 7. sección 5: el evento ─────────────────────────────────────────────────
sub("""<p class="kicker k-data">El evento en CHIRPS e IMERG · <span class="en">scale mismatch</span></p>""",
    """<p class="kicker k-data">5 · Cómo fue la tormenta · lluvia diaria frente a cada media hora</p>""")
sub("""<div class="callout amber"><b>Consecuencia para el catálogo.</b> CHIRPS sirve para la lluvia antecedente y la climatología; para fechar e intensificar los picos hace falta IMERG (diario 2001–2020 en descarga) y las estaciones del IDEAM.</div>""",
    """<div class="callout amber"><b>Por qué importa.</b> Un dato diario sirve para saber cuánto llueve en un mes o una temporada, pero diluye una tormenta de pocas horas. Para estudiar los aguaceros como el de Mocoa hace falta lluvia cada media hora (IMERG) y las estaciones del IDEAM.</div>""")
sub("""<p class="kicker k-arch">GOES-16 · canal 13 · <span class="en">cloud-top brightness temperature</span></p>""",
    """<p class="kicker k-arch">La tormenta vista desde el satélite · GOES-16, infrarrojo</p>""")

# ── 8. diapositivas nuevas ──────────────────────────────────────────────────
NOCHE = """<section class="slide" id="ev-noche" data-g="d" data-sec="1 · Qué pasó">
  <p class="kicker k-data">1 · Qué pasó</p>
  <h2>En una noche, un aguacero de casi 15 mm por hora cayó sobre toda la cuenca de Mocoa, y sus quebradas bajaron como avenida torrencial</h2>
  <div class="two">
    <div>
      <div class="ctl"><label for="enH">Hora local</label><input id="enH" type="range" min="0" max="36" step="1" value="36"><output></output></div>
      <p class="tryit">lleva la hora al inicio (12:00 del 31 de marzo) y avanza despacio: mira cuándo empieza el aguacero y cómo crece la lluvia acumulada.</p>
      <div class="readout" id="enRead"></div>
      <ul class="pts" style="margin-top:14px">
        <li>La noche del <b>31 de marzo de 2017</b> las quebradas Mulato, Sangoyaco y Taruca crecieron de golpe y arrastraron lodo y rocas sobre Mocoa (Putumayo). Murieron más de 300 personas.</li>
        <li>No fue un aguacero cualquiera: en las estaciones del IDEAM fue el <b>cuarto día más lluvioso de 1984–2022</b> (Martinez et al., 2024).</li>
        <li>Lo produjo un <b>sistema convectivo de mesoescala</b>: un grupo de tormentas que se organiza y dura horas. Esta presentación pregunta qué lo hizo posible y cuánto antes se podía reconocer.</li>
      </ul>
    </div>
    <div class="panel"><div class="tshost" id="enFig" style="height:360px"></div>
      <p class="note" style="margin:4px 0 0">Lluvia media sobre la cuenca cada media hora, IMERG V07B (NASA), del 31 de marzo a las 12:00 al 1 de abril a las 06:00, hora de Colombia. El satélite promedia celdas de unos 11 km, así que subestima los picos que miden las estaciones.</p></div>
  </div>
</section>

"""
TIEMPO = """<section class="slide" id="pr-tiempo" data-g="a" data-sec="6 · Con cuánta anticipación">
  <p class="kicker k-arch">6 · Con cuánta anticipación</p>
  <h2>Las primeras señales del evento aparecieron unas 48 horas antes, pero la mayoría solo en las últimas 12</h2>
  <div class="two" style="grid-template-columns:minmax(0,1fr) minmax(0,1.5fr)">
    <div>
      <div class="ctl"><label for="ptH">Horas antes</label><input id="ptH" type="range" min="-48" max="4" step="1" value="-48"><output></output></div>
      <div class="chips" id="ptPre"><button class="chip" data-v="-48">2 días antes</button><button class="chip" data-v="-12">12 h antes</button><button class="chip" data-v="-3">3 h antes</button><button class="chip" data-v="2">durante</button></div>
      <p class="tryit">arrastra la línea desde «2 días antes» hasta el inicio del aguacero: cada señal se enciende cuando ya era visible.</p>
      <div class="readout" id="ptRead"></div>
      <div class="callout" id="ptDet" style="margin-top:10px"></div>
    </div>
    <div class="panel"><div class="tshost" id="ptFig" style="height:400px"></div>
      <div class="legend" style="margin:0 0 4px"><span><i style="background:var(--sw)"></i>Robledo et al. (2026)</span><span><i style="background:var(--accent)"></i>Martinez et al. (2024)</span><span>○ momento de máxima intensidad</span></div>
      <p class="note" style="margin:0">Horas contadas desde las 22:00 del 31 de marzo, hora local, cuando empezó la lluvia en las estaciones del IDEAM.</p></div>
  </div>
</section>

"""
PROB = """<section class="slide" id="pr-prob" data-g="a" data-sec="6 · Con cuánta anticipación">
  <p class="kicker k-arch">De la anécdota a la probabilidad</p>
  <h2>Saber si hay El Niño o La Niña casi no cambia la probabilidad de un día extremo en marzo–mayo</h2>
  <div class="two">
    <div>
      <p>Un caso no basta: hay que preguntar <b>con qué frecuencia</b> llueve extremo cuando se da una condición, y compararlo con la frecuencia de siempre. Si la condición la sube mucho, sirve para anticipar.</p>
      <div class="chips" id="ppSea"><button class="chip" data-v="DEF">Dic–feb</button><button class="chip" data-v="MAM" aria-pressed="true">Mar–may</button><button class="chip" data-v="JJA">Jun–ago</button><button class="chip" data-v="SON">Sep–nov</button></div>
      <div class="chips" id="ppTh"><button class="chip" data-v="0.95" aria-pressed="true">Muy lluvioso (5 % más alto)</button><button class="chip" data-v="0.99">Extremo (1 % más alto)</button></div>
      <p class="tryit">compara las tres barras de colores con la gris en cada temporada: ¿alguna fase del Pacífico sube mucho la probabilidad?</p>
      <div class="readout" id="ppRead"></div>
      <p class="note" id="ppNote"></p>
    </div>
    <div class="panel"><div class="tshost" id="ppFig" style="height:360px"></div>
      <p class="note" style="margin:4px 0 0">Porcentaje de días de cada temporada en que la lluvia media de la región de Mocoa superó el umbral. CHIRPS v2.0, 1981–2024; umbral calculado con 1991–2020. Fases de El Niño según el índice ONI de NOAA.</p></div>
  </div>
</section>

"""
CIERRE = """<section class="slide" id="cierre" data-g="" data-sec="Cierre">
  <p class="kicker">Cierre</p>
  <h2>Tres respuestas hasta ahora, y lo que falta para la pregunta completa</h2>
  <div class="two even">
    <div class="stack">
      <div class="card lift"><h4>La mayor parte del agua viene de fuera</h4><p>Entre el 60 y el 65 % de la lluvia de la región de Mocoa llega transportada por el viento; el resto lo evapora la propia región.</p><p style="margin-top:8px"><button class="btn" type="button" data-go="cl-mocoa">Ver →</button></p></div>
      <div class="card lift"><h4>2017 no fue una temporada rara: fue un evento</h4><p>Marzo–mayo de 2017 fue algo húmedo (+1σ) y el Pacífico estaba neutral. Lo extraordinario pasó en unas horas.</p><p style="margin-top:8px"><button class="btn" type="button" data-go="an-anom">Ver →</button></p></div>
      <div class="card lift"><h4>La anticipación está en horas y días, no en estaciones</h4><p>El estado del Pacífico casi no cambia la probabilidad de un día extremo; las señales útiles aparecen entre 2 días y unas horas antes.</p><p style="margin-top:8px"><button class="btn" type="button" data-go="pr-tiempo">Ver →</button></p></div>
    </div>
    <div class="panel">
      <h3>Lo que falta</h3>
      <ul class="pts">
        <li><b>De dónde viene la humedad de Mocoa</b>, rastreando el aire hacia atrás, en días normales y extremos.</li>
        <li><b>Un catálogo de aguaceros extremos</b> con lluvia cada media hora (IMERG, 2001–2020) y las estaciones del IDEAM.</li>
        <li><b>Las probabilidades a escala de días</b>: con qué frecuencia un chorro del Orinoco reforzado o mucha humedad en el aire terminan en un día extremo.</li>
      </ul>
      <p class="note">Cada una de estas preguntas se suma a la presentación a medida que avanza el trabajo.</p>
    </div>
  </div>
</section>

"""
toc_end = section("toc").end()
html = html[:toc_end] + NOCHE + html[toc_end:]
goes_end = section("scm-goes").end()
html = html[:goes_end] + TIEMPO + PROB + CIERRE + html[goes_end:]

JS = r"""<script>/* pae/60-anticipacion.js · versión pública */
/* the night of the event: basin rainfall every 30 min (IMERG) with a time scrubber and running total */
demo("ev-noche", () => {
  let P = null, im = null, T = [], V = [];
  const lt = s => new Date(Date.parse(s + ":00Z") - 5 * 36e5);
  const gh = slider("enH", v => (T[v] ? T[v].toISOString().slice(11, 16) : ""), () => render());
  function render() {
    if (!P) return;
    const k = +gh(), acc = V.slice(0, k + 1).reduce((a, v) => a + v * 0.5, 0), tot = V.reduce((a, v) => a + v * 0.5, 0);
    const ipk = V.indexOf(Math.max(...V));
    const X = T.map(t => t.toISOString().slice(0, 16).replace("T", " ")); // texto: Plotly no debe aplicar la zona horaria del navegador
    P.react("enFig", [
      { type: "bar", x: X, y: V, marker: { color: T.map((_, i) => i <= k ? css("--lw") : css("--line")) }, hovertemplate: "%{x|%H:%M}: %{y:.1f} mm/h<extra></extra>", showlegend: false }],
      { autosize: true, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", font: MAPS.font(), margin: { l: 50, r: 10, t: 30, b: 34 }, bargap: 0.1,
        title: { text: "LLUVIA EN LA CUENCA DE MOCOA · CADA MEDIA HORA", font: MAPS.mono(12), x: 0.01, xanchor: "left" },
        xaxis: { tickfont: MAPS.mono(11), tickformat: "%H:%M", dtick: 3 * 36e5 }, yaxis: { tickfont: MAPS.mono(11), gridcolor: css("--line"), title: { text: "mm por hora", font: MAPS.mono(11) }, rangemode: "tozero" },
        shapes: [{ type: "line", x0: X[k], x1: X[k], yref: "paper", y0: 0, y1: 1, line: { color: css("--fg"), width: 1.5, dash: "dot" } }] }, MAPS.CONFIG);
    $("#enRead").innerHTML = `<div><span>Acumulado hasta esa hora</span><b class="c-lw">${fmt(acc, 0)} mm</b></div><div><span>Total de la noche</span><b>${fmt(tot, 0)} mm</b></div>`
      + `<div><span>Lo más intenso</span><b>${fmt(V[ipk], 1)} mm/h · ${T[ipk].toISOString().slice(11, 16)}</b></div>`;
  }
  MAPS.load(["imerg"]).then(([pl, x]) => {
    P = pl; im = x;
    const i0 = im.time.indexOf("2017-03-31T17:00"), i1 = im.time.indexOf("2017-04-01T11:30");
    T = im.time.slice(i0, i1 + 1).map(lt); V = im.R6_media.slice(i0, i1 + 1).map(v => v || 0);
    $("#enFig").innerHTML = "";
    const r = $("#enH"); r.max = T.length - 1; r.value = T.length - 1; r.dispatchEvent(new Event("input"));
  }).catch(e => MAPS.fail($("#enFig"), e));
  return render;
});

/* precursor timeline (Martinez et al. 2024; Robledo et al. 2026): signals light up once they were visible */
demo("pr-tiempo", () => {
  const ROWS = [ // [señal, inicio, fin, pico, fuente, explicación]
    ["Onda ecuatorial en fase húmeda", -48, 12, null, "R", "Una onda de Rossby ecuatorial, que viaja hacia el oeste en días, dejaba el ambiente más húmedo e inestable desde el 29 de marzo (Robledo et al., 2026)."],
    ["Tormentas en el Macizo Guayanés", -25, -12, -25, "R", "Un día antes nació convección en el Macizo Guayanés, en Venezuela; su aire húmedo viajó hacia el piedemonte (Robledo et al., 2026)."],
    ["Se refuerza el chorro del Orinoco", -17, -3, -3, "R", "El viento de capas bajas que entra desde los Llanos se reforzó en las 17 horas previas (Robledo et al., 2026)."],
    ["Humedad que entra, por encima de lo normal", -11, 1, null, "R", "El flujo de vapor cerca de Mocoa superó en más de 1,2 desviaciones estándar lo normal (Robledo et al., 2026)."],
    ["Nace la tormenta de Mocoa", -8, -8, -8, "R", "A las 14:00 hora local se inició el sistema convectivo que llegaría a Mocoa (Robledo et al., 2026)."],
    ["Chorro intenso en la caja C3", -8, 4, -5, "M", "El índice del chorro en la caja C3 estuvo por encima de lo normal desde la tarde, con un pico a las 17:00 (Martinez et al., 2024)."],
    ["El aire converge sobre el piedemonte", -6, 2, null, "M", "La humedad empezó a acumularse sobre el piedemonte: entra más vapor del que sale (Martinez et al., 2024)."],
    ["Salto del chorro en la caja C4", -6, 4, -2, "M", "El índice C4 dio un salto entre las 16 y las 17 horas y llegó a su máximo a las 20:00 (Martinez et al., 2024)."],
    ["Sube el agua en el aire", -5, 2, 1.5, "M", "El agua precipitable, toda el agua de la columna de aire, subió con fuerza y llegó a su pico entre las 23 y las 00 (Martinez et al., 2024)."]];
  const COL = { R: "--sw", M: "--accent" };
  let P = null, sel = 0;
  const gh = slider("ptH", v => v > 0 ? `+${v} h` : v === 0 ? "0 h" : `${v} h`, () => render());
  chips($("#ptPre"), v => { $("#ptH").value = v; $("#ptH").dispatchEvent(new Event("input")); });
  function render() {
    if (!P) return;
    const t = +gh(), on = ROWS.map(r => r[1] <= t), Y = ROWS.map(r => r[0]);
    const tr = ROWS.map((r, i) => ({ type: "bar", orientation: "h", y: [r[0]], base: [r[1]], x: [Math.max(r[2] - r[1], 0.8)], width: 0.55,
      marker: { color: on[i] ? css(COL[r[4]]) : css("--line"), opacity: on[i] ? 0.9 : 0.6 }, hovertemplate: `${r[0]}<br>de ${r[1]} h a ${r[2]} h<extra></extra>`, showlegend: false }));
    tr.push({ type: "scatter", mode: "markers", y: ROWS.filter(r => r[3] != null).map(r => r[0]), x: ROWS.filter(r => r[3] != null).map(r => r[3]),
      marker: { symbol: "circle", size: 10, color: css("--bg"), line: { color: css("--fg"), width: 2 } }, hovertemplate: "pico a %{x} h<extra></extra>", showlegend: false });
    P.react("ptFig", tr, { autosize: true, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", font: MAPS.font(), margin: { l: 10, r: 14, t: 30, b: 40 }, barmode: "overlay",
      title: { text: "SEÑALES ANTES DEL AGUACERO", font: MAPS.mono(12), x: 0.01, xanchor: "left" },
      xaxis: { range: [-49, 12], dtick: 6, tickfont: MAPS.mono(11), gridcolor: css("--line"), title: { text: "horas respecto al inicio de la lluvia", font: MAPS.mono(11) }, zeroline: false },
      yaxis: { autorange: "reversed", tickfont: MAPS.mono(11), automargin: true },
      shapes: [{ type: "rect", x0: -49, x1: t, yref: "paper", y0: 0, y1: 1, fillcolor: css("--accent"), opacity: 0.05, line: { width: 0 } },
        { type: "line", x0: t, x1: t, yref: "paper", y0: 0, y1: 1, line: { color: css("--fg"), width: 2 } },
        { type: "line", x0: 0, x1: 0, yref: "paper", y0: 0, y1: 1, line: { color: css("--lw"), width: 1.5, dash: "dash" } }],
      annotations: [{ x: 0, y: 1, yref: "paper", text: "empieza la lluvia", showarrow: false, xanchor: "right", yanchor: "bottom", font: MAPS.mono(11) }] }, MAPS.CONFIG);
    const n = on.filter(Boolean).length, last = ROWS.map((r, i) => [r, i]).filter(([r]) => r[1] <= t).pop();
    sel = last ? last[1] : 0;
    $("#ptRead").innerHTML = `<div><span>Señales visibles</span><b>${n} de ${ROWS.length}</b></div><div><span>Tiempo para el aguacero</span><b class="c-lw">${t < 0 ? -t + " h" : "ya llueve"}</b></div>`;
    const r = ROWS[sel];
    $("#ptDet").innerHTML = last ? `<b>${r[0]}.</b> ${r[5]}` : "Mueve la línea para ver la primera señal.";
  }
  MAPS.load([]).then(([pl]) => { P = pl; $("#ptFig").innerHTML = ""; render(); }).catch(e => MAPS.fail($("#ptFig"), e));
  return render;
});

/* conditional probability of a very wet / extreme day in the Mocoa region given the ENSO phase */
demo("pr-prob", () => {
  let P = null, d = null, ix = null, D = null, sea = "MAM", q = 0.95;
  chips($("#ppSea"), v => { sea = v; render(); });
  chips($("#ppTh"), v => { q = +v; render(); });
  const SM = { DEF: [12, 1, 2], MAM: [3, 4, 5], JJA: [6, 7, 8], SON: [9, 10, 11] };
  function render() {
    if (!P) return;
    const v = d.R4_media, [sy, sm] = ix.start.split("-").map(Number);
    const base = v.filter((x, i) => x != null && D[i] >= "1991-01-01" && D[i] <= "2020-12-31"), th = EX.quant(base, q);
    const cnt = { all: [0, 0], 1: [0, 0], "-1": [0, 0], 0: [0, 0] };
    D.forEach((s, i) => { const y = +s.slice(0, 4), m = +s.slice(5, 7); if (!SM[sea].includes(m) || v[i] == null) return;
      const ph = ix.enso[(y - sy) * 12 + m - sm]; const hit = v[i] > th ? 1 : 0;
      cnt.all[0] += hit; cnt.all[1]++; if (ph != null && cnt[ph]) { cnt[ph][0] += hit; cnt[ph][1]++; } });
    const pc = k => 100 * cnt[k][0] / cnt[k][1];
    const X = ["Todos los años", "El Niño", "Neutral", "La Niña"], K = ["all", 1, 0, -1], C = ["--muted", "--lw", "--ok", "--cool"];
    P.react("ppFig", [{ type: "bar", x: X, y: K.map(pc), marker: { color: C.map(css) }, text: K.map(k => fmt(pc(k), 1) + " %"), textposition: "outside", textfont: MAPS.mono(12),
      customdata: K.map(k => cnt[k][1]), hovertemplate: "%{x}: %{y:.1f} % de %{customdata} días<extra></extra>", showlegend: false }],
      { autosize: true, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", font: MAPS.font(), margin: { l: 50, r: 10, t: 30, b: 34 },
        title: { text: `DÍAS SOBRE EL UMBRAL · ${({ DEF: "DIC–FEB", MAM: "MAR–MAY", JJA: "JUN–AGO", SON: "SEP–NOV" })[sea]}`, font: MAPS.mono(12), x: 0.01, xanchor: "left" },
        xaxis: { tickfont: MAPS.mono(12) }, yaxis: { tickfont: MAPS.mono(11), gridcolor: css("--line"), title: { text: "% de los días", font: MAPS.mono(11) }, rangemode: "tozero", range: [0, Math.max(...K.map(pc)) * 1.3] } }, MAPS.CONFIG);
    const hi = [1, 0, -1].reduce((a, b) => (pc(b) > pc(a) ? b : a)), ratio = pc(hi) / pc("all");
    $("#ppRead").innerHTML = `<div><span>Umbral</span><b class="c-sw">${fmt(th, 1)} mm/día</b></div><div><span>Fase que más la sube</span><b>× ${fmt(ratio, 2)}</b></div>`;
    $("#ppNote").innerHTML = cnt[hi][0] < 20
      ? `Con tan pocos días sobre el umbral (${cnt[hi][0]} en la fase que más sube), estas diferencias pueden ser azar. Con el umbral «muy lluvioso» hay más casos y la comparación es más confiable.`
      : ratio < 1.3
      ?"La diferencia entre fases es pequeña: con este dato, el Pacífico no anticipa bien un día extremo en esta temporada. La anticipación hay que buscarla en escalas más cortas, de días a horas."
      : `${({ 1: "El Niño", 0: "Un año neutral", "-1": "La Niña" })[hi]} sube la frecuencia, pero sigue siendo un día de cada ${fmtN(100 / pc(hi))}: es un cambio de probabilidad, no una predicción.`;
  }
  MAPS.load(["extremos", "indices"]).then(([pl, x, i]) => { P = pl; d = x; ix = i; D = EX.dates(d); $("#ppFig").innerHTML = ""; render(); }).catch(e => MAPS.fail($("#ppFig"), e));
  return render;
});
</script>
<script>/* common/boot.js */"""
sub("""<script>/* common/boot.js */""", JS)

# ── 9. sin restos de la versión de trabajo ──────────────────────────────────
for bad in ("decisión pendiente", "este servidor", "en descarga", 'class="tag done"', 'class="tag pend"'):
    m = re.search(r'<section class="slide.*?</main>', html, re.S).group(0)
    assert bad not in m, f"queda «{bad}» en las diapositivas"

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"{out}: {len(re.findall(r'<section class=\"slide', html))} diapositivas, {out.stat().st_size / 1e6:.2f} MB")
