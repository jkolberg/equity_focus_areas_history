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
        "hispanic": ["P009002"],
        "white_nh": ["P009005"],
        "black_nh": ["P009006"],
        "aian_nh": ["P009007"],
        "asian_pac_nh": ["P009008", "P009009"],
        "other_nh": ["P009010", "P009011"],
    }
    df10 = c.get_dec_data(variables_dict, 2010, "tract", "sf1", county_ids, state_id)

    variables_dict = {
        "total_poverty_status_pop": ["C17002_001E"],
        "below_200_percent_poverty": [
            "C17002_002E",
            "C17002_003E",
            "C17002_004E",
            "C17002_005E",
            "C17002_006E",
            "C17002_007E",
        ],
        "above_200_percent_poverty": ["C17002_008E"],
    }
    acs10 = c.get_acs_data(variables_dict, 2010, "tract", "acs5", county_ids, state_id)
    df10 = df10.merge(acs10, on="geoid", how="outer")

    paths = context["paths"]
    xwalks_dir: Path = paths["xwalks"]
    xwalk10_path = xwalks_dir / "nhgis_tr2010_tr2020_53.csv"
    _require_file(xwalk10_path)

    xwalk10 = pd.read_csv(xwalk10_path)

    out10_to_20 = xwalk_merge_sum(
        xwalk10,
        "tr2010ge",
        "tr2020ge",
        df10,
        "geoid",
        "wt_pop",
        cols_to_get,
    )

    out10_to_20 = normalize_round(out10_to_20, "tr2020ge", cols_dict)

    out10_to_20["county_id"] = out10_to_20["tr2020ge"].astype(str).str[0:5].astype(int)
    out10_to_20 = out10_to_20.loc[out10_to_20["county_id"].isin(county_ids)].copy()

    out10_to_20["year"] = 2010

    out_path = context["artifacts"]["out10_to_20"]
    out10_to_20.to_parquet(out_path, index=False)
