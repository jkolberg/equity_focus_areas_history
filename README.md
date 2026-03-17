# equity-focus-areas-history

This project is a pypyr-driven data pipeline converted from a single analysis notebook.

## Run

- Set your Census API key in `CENSUS_KEY`.
- Ensure required input files exist in `data/` and `xwalks/` (see below).
- Run: `python run.py`

## Pipeline definition

- The pipeline step list lives in [configs/settings.yaml](configs/settings.yaml).
- Each step is implemented as a Python module under `steps/`.

`configs/settings.yaml` also contains run configuration (county IDs, state ID, input directories). The Census API key is read from the `CENSUS_KEY` environment variable by the pipeline.

## Required inputs

### Local CSVs (1990)

Place these in `data/`:

- `nhgis0017_ds120_1990_tract.csv`
- `nhgis0018_ds123_1990_tract.csv`

### Crosswalks

Place these in `xwalks/` (or `data/`):

- `nhgis_tr1990_tr2010_53.csv`
- `nhgis_tr2000_tr2010_53.csv`
- `nhgis_tr2010_tr2020_53.csv`

## Outputs

- CSVs, intermediate artifacts, and HTML maps are written to `outputs/` (configurable in `configs/settings.yaml`).
- The Shiny app (`app.R`) and dashboard data are written to `docs/dashboard/`.
- Run the dashboard with R: `shiny::runApp("docs/dashboard")`.
