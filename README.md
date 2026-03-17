# equity-focus-areas-history

This project is a pypyr-driven data pipeline that creates a Quarto dashboard using 1990-2020 census data.

## Run

- Set your Census API key in `CENSUS_KEY` env variable
- install uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | more"`
- Make sure you are connected to the PSRC vpn to copy input files from Y:/ drive
- Run: `uv run run.py`
