from __future__ import annotations

from datetime import datetime
from pathlib import Path

from util.census_api import CensusApi


def run_step(context: dict) -> None:
    api_key = context.get("api_key")
    if not api_key:
        raise ValueError(
            "Missing api_key in pypyr context. "
            "Ensure configs/settings.yaml reads CENSUS_KEY via pypyr.steps.envget."
        )

    county_ids = context.get("county_ids")
    state_id = context.get("state_id")
    if not county_ids:
        raise ValueError("Missing county_ids in pypyr context. Set it in configs/settings.yaml.")
    if state_id is None:
        raise ValueError("Missing state_id in pypyr context. Set it in configs/settings.yaml.")

    repo_root = Path.cwd()
    data_dir_cfg = context.get("data_dir", "data")
    xwalks_dir_cfg = context.get("xwalks_dir", "xwalks")
    output_dir_cfg = context.get("output_dir", "outputs")
    intermediate_dir_cfg = context.get("intermediate_dir", "intermediate")

    data_dir = (repo_root / data_dir_cfg) if not Path(str(data_dir_cfg)).is_absolute() else Path(str(data_dir_cfg))
    xwalks_dir = (
        (repo_root / xwalks_dir_cfg)
        if not Path(str(xwalks_dir_cfg)).is_absolute()
        else Path(str(xwalks_dir_cfg))
    )
    output_dir = (
        (repo_root / output_dir_cfg)
        if not Path(str(output_dir_cfg)).is_absolute()
        else Path(str(output_dir_cfg))
    )

    intermediate_dir = (
        (output_dir / intermediate_dir_cfg)
        if not Path(str(intermediate_dir_cfg)).is_absolute()
        else Path(str(intermediate_dir_cfg))
    )

    # Allow crosswalk csvs to live in data/ (common when copying inputs around).
    # Prefer xwalks/ if it contains nhgis_tr*.csv; otherwise fall back to data/.
    has_xwalks = xwalks_dir.exists() and any(xwalks_dir.glob("nhgis_tr*.csv"))
    resolved_xwalks_dir = xwalks_dir if has_xwalks else data_dir

    paths = {
        "root": repo_root,
        "data": data_dir,
        "xwalks": resolved_xwalks_dir,
        "output": output_dir,
        "intermediate": intermediate_dir,
    }

    paths["output"].mkdir(parents=True, exist_ok=True)
    paths["intermediate"].mkdir(parents=True, exist_ok=True)

    context["api_key"] = api_key
    context["county_ids"] = county_ids
    context["state_id"] = state_id
    context["paths"] = paths
    context["census"] = CensusApi(api_key)

    # A stable run tag for output file names.
    context["run_tag"] = datetime.now().strftime("%Y_%m%d")

    intermediate = paths["intermediate"]
    context["artifacts"] = {
        "out90_to_20": intermediate / "out90_to_20.parquet",
        "out00_to_20": intermediate / "out00_to_20.parquet",
        "out10_to_20": intermediate / "out10_to_20.parquet",
        "df20": intermediate / "df20.parquet",
        "df_all": intermediate / "df_all.parquet",
        "df_poc": intermediate / "df_poc.parquet",
        "df_poverty": intermediate / "df_poverty.parquet",
        "tracts": intermediate / "tracts.parquet",
    }
