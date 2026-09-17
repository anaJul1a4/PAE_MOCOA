// Funciones de render Plotly para el informe interactivo de Mocoa.
// Depende de REPORT_DATA (data.js) y de Plotly (plotly.min.js), ambos
// cargados antes que este script.

const INK = "#1A1A1A", INK_MUTED = "#5B6472", SURFACE = "#FFFFFF";
const SEQ_BLUE = [[0, "#EEF3F8"], [0.2, "#C5D9E8"], [0.4, "#8FB8D4"],
                  [0.6, "#548FB8"], [0.8, "#2A6592"], [1, "#0E3A5C"]];
const SEQ_ORANGE = [[0, "#FFF3E0"], [0.5, "#E8A25A"], [1, "#7A3B0E"]];
const DIV_BROWN_BLUE = [[0, "#7A3B0E"], [0.25, "#C97A2B"], [0.5, "#F2E4CE"],
                        [0.75, "#C5D9E8"], [1, "#0E3A5C"]];

const BASE_LAYOUT = {
  paper_bgcolor: SURFACE, plot_bgcolor: SURFACE,
  font: { color: INK, family: "-apple-system,Segoe UI,Roboto,sans-serif", size: 12 },
  margin: { l: 52, r: 20, t: 34, b: 40 },
  hovermode: "x unified",
  legend: { orientation: "h", y: -0.18, font: { size: 11 } },
};
const CONFIG = { responsive: true, displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d"] };

function withRangeslider(layout) {
  layout.xaxis = layout.xaxis || {};
  layout.xaxis.rangeslider = { thickness: 0.08, bgcolor: "#F7F8FA" };
  return layout;
}

/** Evita que un id de figura eliminada/renombrada rompa el resto del render:
 * cada renderXxx llama a esto antes de invocar Plotly.newPlot. */
function ensureDiv(divId) {
  const el = document.getElementById(divId);
  if (!el) console.warn(`[informe] contenedor "#${divId}" no existe en el HTML, se omite`);
  return el;
}

/** Serie temporal simple (una o mas trazas), con barra deslizadora. */
function renderSeries(divId, traces, opts = {}) {
  if (!ensureDiv(divId)) return;
  const layout = Object.assign({}, BASE_LAYOUT, {
    height: opts.height || 340,
    yaxis: Object.assign({ title: opts.yTitle || "", gridcolor: "#EEF1F4",
                          autorange: opts.invert ? "reversed" : true }, opts.yaxisExtra || {}),
    shapes: opts.eventLine ? [{
      type: "line", x0: opts.eventLine, x1: opts.eventLine, yref: "paper",
      y0: 0, y1: 1, line: { color: "#B3241C", width: 1.4, dash: "dash" },
    }] : [],
  });
  if (opts.rangeslider !== false) withRangeslider(layout);
  if (opts.xaxisRange) layout.xaxis.range = opts.xaxisRange;
  Plotly.newPlot(divId, traces, layout, CONFIG);
}

/** Barras (extremos, anomalias, lags) sin barra deslizadora por defecto. */
function renderBars(divId, traces, opts = {}) {
  if (!ensureDiv(divId)) return;
  const layout = Object.assign({}, BASE_LAYOUT, {
    height: opts.height || 320,
    yaxis: { title: opts.yTitle || "", gridcolor: "#EEF1F4" },
    xaxis: { title: opts.xTitle || "" },
    barmode: opts.barmode || "group",
  });
  Plotly.newPlot(divId, traces, layout, CONFIG);
}

/** Dispersion X-Y con linea 1:1 opcional. */
function renderScatter(divId, traces, opts = {}) {
  if (!ensureDiv(divId)) return;
  const layout = Object.assign({}, BASE_LAYOUT, {
    height: opts.height || 420,
    xaxis: { title: opts.xTitle, gridcolor: "#EEF1F4" },
    yaxis: { title: opts.yTitle, gridcolor: "#EEF1F4", scaleanchor: opts.square ? "x" : undefined },
  });
  Plotly.newPlot(divId, traces, layout, CONFIG);
}

/** Ciclo anual SIN boxplot: banda P25-P75 + mediana por mes, puntos de
 * todos los años en jitter, y 2017 marcado aparte con una estrella. */
function renderAnnualCycle(divId, byMonth, opts = {}) {
  if (!ensureDiv(divId)) return;
  const meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  const p10 = [], p25 = [], p50 = [], p75 = [], p90 = [], y2017 = [];

  function percentile(arr, p) {
    const s = [...arr].sort((a, b) => a - b);
    const idx = (s.length - 1) * p;
    const lo = Math.floor(idx), hi = Math.ceil(idx);
    return s[lo] + (s[hi] - s[lo]) * (idx - lo);
  }

  meses.forEach((_, i) => {
    const entry = byMonth[String(i + 1)] || { years: [], values: [] };
    const vals = entry.values;
    if (vals.length) {
      p10.push(percentile(vals, 0.10));
      p25.push(percentile(vals, 0.25));
      p50.push(percentile(vals, 0.5));
      p75.push(percentile(vals, 0.75));
      p90.push(percentile(vals, 0.90));
    } else { p10.push(null); p25.push(null); p50.push(null); p75.push(null); p90.push(null); }
    const j2017 = entry.years.indexOf(2017);
    y2017.push(j2017 >= 0 ? entry.values[j2017] : null);
  });

  // Envolvente climatologica estandar: banda P10-P90 (rango tipico), banda
  // P25-P75 (mitad central) mas oscura, mediana como referencia, y 2017
  // como una unica linea solida resaltada -- sin puntos individuales por
  // año (jitter) ni marcadores tipo estrella, que en un dominio con 38
  // años superpuestos generan una nube ilegible y de aspecto poco tecnico.
  const x = meses.map((_, i) => i + 1);
  const traces = [
    { x, y: p90, type: "scatter", mode: "lines", line: { width: 0, shape: "spline" },
      showlegend: false, hoverinfo: "skip" },
    { x, y: p10, type: "scatter", mode: "lines", line: { width: 0, shape: "spline" },
      fill: "tonexty", fillcolor: "rgba(15,58,92,0.10)", name: "rango P10-P90",
      hoverinfo: "skip" },
    { x, y: p75, type: "scatter", mode: "lines", line: { width: 0, shape: "spline" },
      showlegend: false, hoverinfo: "skip" },
    { x, y: p25, type: "scatter", mode: "lines", line: { width: 0, shape: "spline" },
      fill: "tonexty", fillcolor: "rgba(15,58,92,0.24)", name: "rango P25-P75",
      hoverinfo: "skip" },
    { x, y: p50, type: "scatter", mode: "lines", name: "mediana 1981-2018",
      line: { color: "#5B6472", width: 1.6, dash: "dot", shape: "spline" } },
    { x, y: y2017, type: "scatter", mode: "lines+markers", name: "2017",
      line: { color: "#B3241C", width: 2.6, shape: "spline" },
      marker: { color: "#B3241C", size: 6, line: { color: "white", width: 1 } },
      connectgaps: false },
  ];
  const layout = Object.assign({}, BASE_LAYOUT, {
    height: opts.height || 320,
    yaxis: { title: opts.yTitle || "mm/mes", gridcolor: "#EEF1F4", rangemode: "tozero" },
    xaxis: { tickmode: "array", tickvals: x, ticktext: meses },
  });
  Plotly.newPlot(divId, traces, layout, CONFIG);
}

/** Mapa raster con zoom/pan (heatmap) + overlays vectoriales opcionales. */
function renderMap(divId, grid, opts = {}) {
  if (!ensureDiv(divId)) return;
  const heat = {
    type: "heatmap", x: grid.lon, y: grid.lat, z: grid.z,
    colorscale: opts.colorscale || SEQ_BLUE,
    zmid: opts.zmid, zmin: opts.zmin, zmax: opts.zmax,
    colorbar: { title: opts.unit || "", titleside: "right", thickness: 14 },
    hovertemplate: "lon %{x:.3f}  lat %{y:.3f}<br>" + (opts.unit || "valor") + " %{z}<extra></extra>",
  };
  const traces = [heat];
  if (opts.basin) {
    traces.push({ type: "scatter", mode: "lines", x: opts.basin.lon, y: opts.basin.lat,
      line: { color: "#B3241C", width: 2.4 }, name: "límite de cuenca", hoverinfo: "name" });
  }
  if (opts.streams) {
    traces.push({ type: "scatter", mode: "lines", x: opts.streams.lon, y: opts.streams.lat,
      line: { color: "#FF7A00", width: 1.1 }, name: "red de drenaje", hoverinfo: "name" });
  }
  if (opts.stations) {
    traces.push({ type: "scatter", mode: "markers+text", x: opts.stations.map(s => s.lon),
      y: opts.stations.map(s => s.lat), text: opts.stations.map(s => s.name),
      textposition: "top center", textfont: { size: 9, color: "#6A3D9A" },
      marker: { color: "#6A3D9A", size: 8, line: { color: "white", width: 1 } },
      name: "estaciones IDEAM", hoverinfo: "text" });
  }
  const layout = {
    paper_bgcolor: SURFACE, plot_bgcolor: SURFACE,
    font: BASE_LAYOUT.font, margin: { l: 52, r: 20, t: 10, b: 40 },
    height: opts.height || 480,
    xaxis: { title: "Longitud (°)", gridcolor: "#EEF1F4", constrain: "domain" },
    yaxis: { title: "Latitud (°)", gridcolor: "#EEF1F4", scaleanchor: "x", scaleratio: 1 },
    legend: { orientation: "h", y: -0.14 },
  };
  Plotly.newPlot(divId, traces, layout, Object.assign({}, CONFIG, { scrollZoom: true }));
}

// ============================================================
// Llamadas de render, una por figura del informe
// ============================================================

function initReport() {
  const D = REPORT_DATA;

  // --- B. La noche del evento ---------------------------------------------
  // Vista inicial ya enfocada en el pico (31 mar - 2 abr); la barra
  // deslizadora conserva las 24 dias completas de contexto detras -- una
  // sola figura interactiva reemplaza la version panoramica y la de
  // "alta resolucion" que antes eran dos PNG estaticos separados.
  const PEAK_RANGE = ["2017-03-31 00:00:00", "2017-04-02 12:00:00"];
  const peakRangeLayout = { xaxis: { range: PEAK_RANGE } };

  renderSeries("chart-event-ideam",
    [{ x: D.event_window.ideam_aq_hourly.t, y: D.event_window.ideam_aq_hourly.v,
       type: "bar", name: "Acueducto Mocoa", marker: { color: "#2A6592" } },
     { x: D.event_window.ideam_pp_hourly.t, y: D.event_window.ideam_pp_hourly.v,
       type: "scatter", mode: "lines", name: "El Pepino", line: { color: "#C97A2B", width: 1.3 } }],
    { yTitle: "mm/hora", eventLine: "2017-04-01 04:45:00", height: 260, xaxisRange: PEAK_RANGE });

  renderSeries("chart-event-chirps",
    [{ x: D.event_window.chirps_daily.t, y: D.event_window.chirps_daily.v,
       type: "bar", name: "CHIRPS (promedio areal)", marker: { color: "#8FB8D4" } }],
    { yTitle: "mm/día", eventLine: "2017-04-01 04:45:00", height: 240 });   // diaria: se deja el rango completo

  renderSeries("chart-event-goes",
    [{ x: D.event_window.goes_tb.t, y: D.event_window.goes_tb.v, type: "scatter",
       mode: "lines", name: "Tb cuenca", line: { color: "#5C2E0A", width: 1 } }],
    { yTitle: "Tb (K)", invert: true, eventLine: "2017-04-01 04:45:00", height: 260, xaxisRange: PEAK_RANGE });

  // --- D. Convección GOES --------------------------------------------------
  renderSeries("chart-goes-p10",
    [{ x: D.goes_metrics.t, y: D.goes_metrics.tb_p10, type: "scatter", mode: "lines",
       name: "Tb P10", line: { color: "#5C2E0A", width: 1 } }],
    { yTitle: "K", invert: true, eventLine: "2017-04-01 04:45:00", height: 260 });

  renderSeries("chart-goes-fraction",
    [{ x: D.goes_metrics.t, y: D.goes_metrics.cf235, type: "scatter", mode: "lines",
       name: "<235 K", line: { color: "#E8B04B", width: 1 } },
     { x: D.goes_metrics.t, y: D.goes_metrics.cf225, type: "scatter", mode: "lines",
       name: "<225 K", line: { color: "#B36A18", width: 1 } },
     { x: D.goes_metrics.t, y: D.goes_metrics.cf215, type: "scatter", mode: "lines",
       name: "<215 K", line: { color: "#7A0C1A", width: 1 } }],
    { yTitle: "fracción de píxeles", eventLine: "2017-04-01 04:45:00", height: 260 });

  renderBars("chart-goes-lag",
    [{ x: D.goes_lag.map(r => r.lag), y: D.goes_lag.map(r => r.r), type: "bar",
       marker: { color: D.goes_lag.map(r => r.lag === -5 ? "#B3241C" : "#8FB8D4") },
       text: D.goes_lag.map(r => "n=" + r.n), hovertemplate: "lag %{x}h  r=%{y:.2f}<br>%{text}<extra></extra>" }],
    { xTitle: "lag (horas)", yTitle: "correlación r", height: 280 });

  // --- C. Por que CHIRPS no lo vio ------------------------------------------
  const anomDates = D.chirps_anomalies.anio.map((a, i) =>
    `${a}-${String(D.chirps_anomalies.mes[i]).padStart(2, "0")}-01`);
  const colors = D.chirps_anomalies.Z.map(z => z >= 0 ? "#2A6592" : "#C97A2B");
  const mar17i = D.chirps_anomalies.anio.findIndex((a, i) => a === 2017 && D.chirps_anomalies.mes[i] === 3);
  const abr17i = D.chirps_anomalies.anio.findIndex((a, i) => a === 2017 && D.chirps_anomalies.mes[i] === 4);
  renderSeries("chart-chirps-anomalies",
    [{ x: anomDates, y: D.chirps_anomalies.Z, type: "bar", marker: { color: colors }, name: "Z mensual" },
     { x: [anomDates[mar17i], anomDates[abr17i]],
       y: [D.chirps_anomalies.Z[mar17i], D.chirps_anomalies.Z[abr17i]],
       type: "scatter", mode: "markers+text", text: ["mar 2017", "abr 2017"],
       textposition: "top center", marker: { color: "#B3241C", size: 11, line: { color: "white", width: 1.5 } },
       name: "2017" }],
    { yTitle: "Z (anomalía estandarizada)", rangeslider: true, height: 320 });

  const yrs = D.chirps_extremes.anio;
  const mk2017 = yrs.map(y => y === 2017 ? "#B3241C" : "#8FB8D4");
  ["max_1d_mm", "max_3d_mm", "max_5d_mm", "max_7d_mm"].forEach((col, i) => {
    renderBars("chart-extremes-" + (i + 1),
      [{ x: yrs, y: D.chirps_extremes[col], type: "bar", marker: { color: mk2017 } }],
      { yTitle: "mm", height: 220 });
  });

  renderScatter("chart-ideam-chirps-scatter",
    [{ x: D.ideam_chirps_full.ideam, y: D.ideam_chirps_full.chirps, type: "scatter",
       mode: "markers", marker: { color: "#2A6592", size: 5, opacity: 0.5 }, name: "días 2016-2018" },
     { x: [0, 100], y: [0, 100], type: "scatter", mode: "lines",
       line: { color: "#5B6472", dash: "dash" }, name: "1:1" }],
    { xTitle: "IDEAM (mm/día)", yTitle: "CHIRPS (mm/día)", square: true, height: 420 });

  renderSeries("chart-ideam-chirps-series",
    [{ x: D.ideam_chirps_full.dates, y: D.ideam_chirps_full.ideam, type: "scatter",
       mode: "lines", name: "IDEAM (observado)", line: { color: "#B3241C", width: 0.9 } },
     { x: D.ideam_chirps_full.dates, y: D.ideam_chirps_full.chirps, type: "scatter",
       mode: "lines", name: "CHIRPS", line: { color: "#2A6592", width: 0.9 } }],
    { yTitle: "mm/día", height: 300 });

  // --- E. Antecedente y modelo -----------------------------------------------
  ["1d", "3d", "5d", "7d", "15d"].forEach((n, i) => {
    renderSeries("chart-antecedent-" + n,
      [{ x: D.antecedent.dates, y: D.antecedent["chirps_" + n], type: "scatter",
         mode: "lines", name: "CHIRPS", line: { color: "#8FB8D4", width: 1.8 } },
       { x: D.antecedent.dates, y: D.antecedent["ideam_" + n], type: "scatter",
         mode: "lines", name: "IDEAM", line: { color: "#B3241C", width: 1.8 } }],
      { yTitle: "mm", eventLine: "2017-03-31", rangeslider: false, height: 200 });
  });

  renderSeries("chart-runoff",
    [{ x: D.runoff.t, y: D.runoff["optimista (bosque conservado)"], type: "scatter",
       mode: "lines", name: "optimista (CN70)", line: { color: "#2A6592" } },
     { x: D.runoff.t, y: D.runoff["central (uso mixto, suelo húmedo)"], type: "scatter",
       mode: "lines", name: "central (CN90)", line: { color: "#C97A2B" } },
     { x: D.runoff.t, y: D.runoff["pesimista (suelo degradado/saturado)"], type: "scatter",
       mode: "lines", name: "pesimista (CN95)", line: { color: "#B3241C" } }],
    { yTitle: "caudal estimado (m³/s)", eventLine: "2017-04-01 04:45:00", height: 320 });

  // --- F. Comparación interanual (IDEAM) --------------------------------------
  renderSeries("chart-year-2017",
    [{ x: D.year_compare.labels2017, y: D.year_compare.y2017.v, type: "bar",
       marker: { color: "#2A6592" }, name: "2017" }],
    { yTitle: "mm/hora", rangeslider: false, height: 220, yaxisExtra: { range: [0, 65] } });
  renderSeries("chart-year-2018",
    [{ x: D.year_compare.labels2018, y: D.year_compare.y2018.v, type: "bar",
       marker: { color: "#C97A2B" }, name: "2018" }],
    { yTitle: "mm/hora", rangeslider: false, height: 220, yaxisExtra: { range: [0, 65] } });

  // --- A. Contexto físico: mapas ------------------------------------------------
  renderMap("map-cuenca-drenaje", D.map_wide_dem, {
    colorscale: SEQ_BLUE, basin: D.basin_outline, streams: D.streams,
    stations: D.stations, unit: "m s.n.m.", height: 560,
  });
  renderMap("map-regional", D.map_regional_dem_ampliado, {
    colorscale: SEQ_BLUE, basin: D.basin_outline, unit: "m s.n.m.", height: 460,
  });
  renderMap("map-topo-elev", D.map_topo.elevation, {
    colorscale: SEQ_BLUE, basin: D.basin_outline, streams: D.streams,
    unit: "m", height: 420,
  });
  renderMap("map-topo-flowacc", D.map_topo.flow_acc_log10, {
    colorscale: SEQ_ORANGE, basin: D.basin_outline, streams: D.streams,
    unit: "log10(celdas)", height: 420,
  });

  // --- C. mapas de anomalia CHIRPS ------------------------------------------------
  renderMap("map-chirps-marzo", D.map_chirps.precip_marzo2017, {
    colorscale: SEQ_BLUE, basin: D.basin_outline, unit: "mm/mes", height: 420,
  });
  renderMap("map-chirps-abril", D.map_chirps.precip_abril2017, {
    colorscale: SEQ_BLUE, basin: D.basin_outline, unit: "mm/mes", height: 420,
  });
  // Rango +-2 (no +-3): el 90% de las celdas cae dentro de +-1.7 en ambos
  // meses, asi que un rango mas ancho aplasta toda la variacion real en el
  // tercio central de la paleta y el mapa se ve "todo un color". Con +-2 se
  // usa la paleta completa y el patron espacial (si lo hay) se distingue.
  renderMap("map-chirps-Z-marzo", D.map_chirps.anom_Z_marzo2017, {
    colorscale: DIV_BROWN_BLUE, zmid: 0, zmin: -2, zmax: 2,
    basin: D.basin_outline, unit: "Z", height: 420,
  });
  renderMap("map-chirps-Z-abril", D.map_chirps.anom_Z_abril2017, {
    colorscale: DIV_BROWN_BLUE, zmid: 0, zmin: -2, zmax: 2,
    basin: D.basin_outline, unit: "Z", height: 420,
  });
  // (map_chirps.acumulado_evento y map_chirps.clima_marzo quedan calculados en
  // data.js pero no se muestran aqui: redundantes con los 4 mapas marzo/abril
  // ya incluidos arriba -- se omiten para no saturar la pagina)

  // --- ciclos anuales ------------------------------------------------------------
  renderAnnualCycle("chart-ideam-cycle", D.ideam_monthly.by_month, { yTitle: "mm/mes (IDEAM)" });
  renderAnnualCycle("chart-chirps-cycle", D.chirps_monthly.by_month, { yTitle: "mm/mes (CHIRPS)" });

  renderSeries("chart-ideam-daily", [
    { x: D.ideam_daily.dates.filter((_, i) => D.ideam_daily.source[i] === "observado"),
      y: D.ideam_daily.dates.map((_, i) => D.ideam_daily.source[i] === "observado" ? D.ideam_daily.precip[i] : null)
        .filter(v => v !== null),
      type: "bar", name: "observado", marker: { color: "#2A6592" } },
  ], { yTitle: "mm/día", height: 260 });

  renderSeries("chart-chirps-daily-full",
    [{ x: D.chirps_daily.dates, y: D.chirps_daily.precip, type: "scatter",
       mode: "lines", line: { color: "#8FB8D4", width: 0.6 }, name: "CHIRPS diario" }],
    { yTitle: "mm/día", height: 260 });

  // --- G. Umbrales de lluvia detonante (nuevo) --------------------------------
  ["1", "3", "4", "5", "7", "15"].forEach(n => {
    const w = D.rainfall_thresholds[n];
    if (!w) return;
    const traces = [
      { x: w.dates, y: w.chirps, type: "scatter", mode: "lines", name: "CHIRPS",
        line: { color: "#8FB8D4", width: 1.8 } },
      { x: w.dates, y: w.ideam, type: "scatter", mode: "lines", name: "IDEAM",
        line: { color: "#B3241C", width: 1.8 } },
    ];
    (w.lines || []).forEach((th, i) => {
      traces.push({ x: w.dates, y: w.dates.map(() => th.valor_mm), type: "scatter",
        mode: "lines", name: `${th.valor_mm} mm (${th.nombre.split("—")[0].trim()})`,
        line: { color: "#7A0C1A", width: 1, dash: i === 0 ? "dash" : "dot" } });
    });
    renderSeries("chart-threshold-" + n + "d", traces,
      { yTitle: "mm", rangeslider: false, eventLine: "2017-03-31", height: 280 });
  });

  // --- H. Anomalia pixel a pixel dentro de la cuenca (nuevo) --------------------
  renderSeries("chart-pixel-anomaly-Z",
    [{ x: D.pixel_anomaly.dates, y: D.pixel_anomaly.Z, type: "bar", name: "Z diario (cuenca)",
       marker: { color: D.pixel_anomaly.Z.map(z => z >= 0 ? "#2A6592" : "#C97A2B") } }],
    { yTitle: "Z (anomalía estandarizada diaria)", rangeslider: false,
      eventLine: "2017-03-31", height: 300 });

  renderScatter("chart-pixel-anomaly-elev",
    [{ x: D.pixel_anomaly.maxcell_dates, y: D.pixel_anomaly.maxcell_elev, type: "scatter",
       mode: "markers", marker: { size: 11, color: D.pixel_anomaly.maxcell_precip,
       colorscale: SEQ_BLUE, showscale: true, colorbar: { title: "mm", thickness: 12 },
       line: { color: INK, width: 0.6 } },
       text: D.pixel_anomaly.maxcell_dates, name: "celda más lluviosa del día" }],
    { xTitle: "fecha", yTitle: "elevación de la celda más lluviosa (m)", height: 340 });
}

document.addEventListener("DOMContentLoaded", initReport);
