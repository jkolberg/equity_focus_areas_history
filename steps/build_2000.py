from __future__ import annotations

from pathlib import Path

import pandas as pd

from util.transforms import normalize_round, xwalk_merge_sum


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")


def run_step(context: dict) -> None:
    c = context["census"]
    county_ids = context["county_ids"]
    state_id = context["state_id"]
    cols_to_get = context["cols_to_get"]
    cols_dict = context["cols_dict"]

    variables_dict = {
        "total_population": ["P001001"],
        "hispanic": ["P004002"],
        "white_nh": ["P004005"],
        "black_nh": ["P004006"],
        "aian_nh": ["P004007"],
        "asian_pac_nh": ["P004008", "P004009"],
        "other_nh": ["P004010", "P004011"],
    }
    d00_sf1 = c.get_dec_data(variables_dict, 2000, "tract", "sf1", county_ids, state_id)

    variables_dict = {
        "total_poverty_status_pop": ["P088001"],
        "below_200_percent_poverty": [
            "P088002",
            "P088003",
            "P088004",
            "P088005",
            "P088006",
            "P088007",
            "P088008",
            "P088009",
        ],
        "above_200_percent_poverty": ["P088010"],
    }
    d00_sf3 = c.get_dec_data(variables_dict, 2000, "tract", "sf3", county_ids, state_id)
    d00 = d00_sf1.merge(d00_sf3, on="geoid")

    paths = context["paths"]
    xwalks_dir: Path = paths["xwalks"]
    xwalk00_path = xwalks_dir / "nhgis_tr2000_tr2010_53.csv"
    xwalk10_path = xwalks_dir / "nhgis_tr2010_tr2020_53.csv"

    for p in (xwalk00_path, xwalk10_path):
        _require_file(p)

    xwalk00 = pd.read_csv(xwalk00_path)
    xwalk10 = pd.read_csv(xwalk10_path)

    out00_to_10 = xwalk_merge_sum(
        xwalk00,
        "tr2000ge",
        "tr2010ge",
        d00,
        "geoid",
        "wt_pop",
        cols_to_get,
    )
    out00_to_20 = xwalk_merge_sum(
        xwalk10,
        "tr2010ge",
        "tr2020ge",
        out00_to_10,
        "tr2010ge",
        "wt_pop",
        cols_to_get,
    )

    out00_to_20["county_id"] = out00_to_20["tr2020ge"].astype(str).str[0:5].astype(int)
    out00_to_20 = out00_to_20.loc[out00_to_20["county_id"].isin(county_ids)].copy()

    out00_to_20 = normalize_round(out00_to_20, "tr2020ge", cols_dict)
    out00_to_20["year"] = 2000

    out_path = context["artifacts"]["out00_to_20"]
    out00_to_20.to_parquet(out_path, index=False)
