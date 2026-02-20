from __future__ import annotations

from pathlib import Path
import subprocess

import geopandas as gpd
import pandas as pd


def run_step(context: dict) -> None:
    paths = context["paths"]
    repo_root: Path = paths["root"]

    # GitHub Pages-compatible output directory. By default, GitHub Pages can be
    # configured to serve from /docs.
    docs_dir_cfg = context.get("docs_dir", "docs")
    docs_dir = (
        (repo_root / docs_dir_cfg)
        if not Path(str(docs_dir_cfg)).is_absolute()
        else Path(str(docs_dir_cfg))
    )
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Keep dashboard output under docs/<dashboard_dir>/ to preserve existing
    # config defaults (dashboard_dir: dashboard).
    dashboard_subdir = context.get("dashboard_dir", "dashboard")
    dashboard_dir = docs_dir / dashboard_subdir
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # Prevent GitHub Pages/Jekyll from attempting to process Quarto output.
    (docs_dir / ".nojekyll").write_text("", encoding="utf-8")

    artifacts = context["artifacts"]
    df_poc = pd.read_parquet(artifacts["df_poc"])
    df_poverty = pd.read_parquet(artifacts["df_poverty"])
    tracts = gpd.read_parquet(artifacts["tracts"])

    # Ensure leaflet-friendly coordinates.
    if tracts.crs is not None and tracts.crs.to_epsg() != 4326:
        tracts = tracts.to_crs(4326)
    elif tracts.crs is None:
        # Best effort; TIGER tracts typically ship in geographic coords.
        tracts = tracts.set_crs(4326, allow_override=True)

    # Keep only what's needed for the interactive map.
    df_poc_small = df_poc[["tr2020ge", "year", "poc_category"]].copy()
    df_poverty_small = df_poverty[
        ["tr2020ge", "year", "below_200_percent_poverty_category"]
    ].copy()

    metrics = df_poc_small.merge(
        df_poverty_small,
        on=["tr2020ge", "year"],
        how="outer",
    )

    # Duplicate geometry per year (one feature per tract-year).
    gdf = tracts[["tr2020ge", "geometry"]].merge(metrics, on="tr2020ge", how="left")
    gdf["year"] = gdf["year"].astype("Int64")

    geojson_path = dashboard_dir / "efa_dashboard_data.geojson"
    gdf.to_file(geojson_path, driver="GeoJSON")

    qmd_path = dashboard_dir / "efa_dashboard.qmd"
    qmd_path.write_text(
        _render_qmd(title="Equity Metrics by Tract", geojson_file=geojson_path.name),
        encoding="utf-8",
    )

    # Render the Quarto dashboard HTML (and its *_files assets) into docs/ so it
    # can be hosted by GitHub Pages.
    subprocess.run(
        [
            "quarto",
            "render",
            str(qmd_path),
            "--output-dir",
            str(dashboard_dir),
        ],
        check=True,
    )


def _render_qmd(*, title: str, geojson_file: str) -> str:
    # Use a Quarto dashboard layout, but keep the page minimal: one map.
    return f"""---
title: "{title}"
format:
  dashboard:
    orientation: rows
    nav-buttons: {{show: false}}
---

::: {{.card}}

<div style="display:flex; gap: 16px; align-items:center; flex-wrap: wrap; margin-bottom: 12px;">
  <label for="metricSelect"><strong>Metric</strong></label>
  <select id="metricSelect">
    <option value="poc_category">POC category</option>
    <option value="below_200_percent_poverty_category">Below 200% poverty category</option>
  </select>

  <label for="yearSlider" style="margin-left:12px;"><strong>Year</strong></label>
  <input id="yearSlider" type="range" min="0" max="3" step="1" value="0" list="yearTicks" />
  <datalist id="yearTicks">
    <option value="0" label="1990"></option>
    <option value="1" label="2000"></option>
    <option value="2" label="2010"></option>
    <option value="3" label="2020"></option>
  </datalist>
  <span id="yearLabel" style="min-width: 48px;">1990</span>
</div>

<div id="status" style="margin: 8px 0;"></div>

<div id="map" style="height: 700px; width: 100%;"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const YEARS = [1990, 2000, 2010, 2020];
const GEOJSON_URL = '{geojson_file}';

let map;
let geojsonAll;
let layer;
let hasFitBounds = false;

function setStatus(html) {{
  const el = document.getElementById('status');
  if (!el) return;
  el.innerHTML = html || '';
}}

function getColor(v) {{
  if (v === null || v === undefined) return '#cccccc';
  const s = String(v);
  if (s === 'Below Regional Average') return '#ffffcc';
  if (s === 'Above Regional Average') return '#fd8d3c';
  if (s === 'Above 1 Std Dev') return '#800026';
  return '#cccccc';
}}

function styleFeature(metric, year) {{
  return function(feature) {{
    const props = feature.properties || {{}};
    const v = props[metric];
    return {{
      color: '#666666',
      weight: 0.3,
      opacity: 1,
      fillColor: getColor(v),
      fillOpacity: 0.8
    }};
  }};
}}

function featureFilter(year) {{
  return function(feature) {{
    if (!feature || !feature.properties) return false;
    const y = feature.properties.year;
    if (y === null || y === undefined) return false;
    return Number(y) === year;
  }};
}}

function formatCategory(v) {{
  if (v === null || v === undefined) return 'NA';
  const s = String(v);
  return s.length ? s : 'NA';
}}

function updateLayer() {{
  if (!geojsonAll) return;
  const metric = document.getElementById('metricSelect').value;
  const yearIndex = parseInt(document.getElementById('yearSlider').value, 10);
  const year = YEARS[yearIndex];
  document.getElementById('yearLabel').textContent = String(year);

  if (layer) layer.remove();

  layer = L.geoJSON(geojsonAll, {{
    filter: featureFilter(year),
    style: styleFeature(metric, year),
    onEachFeature: function(feature, layer) {{
      const p = feature.properties || {{}};
      const tract = p.tr2020ge ?? 'unknown';
      const v = p[metric];
      const labelMetric = (metric === 'poc_category') ? 'POC category' : 'Below 200% poverty category';
      layer.bindTooltip(
        `Tract: ${{tract}}<br/>Year: ${{year}}<br/>${{labelMetric}}: ${{formatCategory(v)}}`,
        {{sticky: true}}
      );
    }}
  }}).addTo(map);

  if (!hasFitBounds) {{
    const bounds = layer.getBounds && layer.getBounds();
    if (bounds && bounds.isValid && bounds.isValid()) {{
      map.fitBounds(bounds, {{padding: [20, 20]}});
      hasFitBounds = true;
    }}
  }}
}}

async function init() {{
  map = L.map('map').setView([47.5, -122.2], 9);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  setStatus('Loading data…');
  try {{
    const resp = await fetch(GEOJSON_URL);
    if (!resp.ok) throw new Error('HTTP ' + resp.status + ' loading ' + GEOJSON_URL);
    geojsonAll = await resp.json();
    setStatus('');
  }} catch (err) {{
    console.error('Failed to load GeoJSON', err);
    setStatus(
      'Could not load <code>' + GEOJSON_URL + '</code>. ' +
      'If you opened this dashboard from <code>file://</code>, most browsers block <code>fetch()</code>. ' +
      'Try serving this folder with a local web server (e.g. <code>python -m http.server</code>) and open the <code>http://</code> URL.'
    );
    return;
  }}

  document.getElementById('metricSelect').addEventListener('change', updateLayer);
  document.getElementById('yearSlider').addEventListener('input', updateLayer);

  // Quarto dashboard layout can resize the card after load.
  setTimeout(() => map.invalidateSize(), 50);

  updateLayer();
}}

init();
</script>

:::
"""
