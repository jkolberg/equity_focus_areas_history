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

    # Get decennial SF1 variables for 2010
    variables_dict = {
        "total_population": ["P001001"],
        "hispanic": ["P009002"],
        "white_nh": ["P009005"],
        "black_nh": ["P009006"],
        "aian_nh": ["P009007"],
        "asian_pac_nh": ["P009008", "P009009"],
        "other_nh": ["P009010", "P009011"],
        "age_65_plus": [
            "P012020",
            "P012021",
            "P012022",
            "P012023",
            "P012024",
            "P012025",
            "P012044",
            "P012045",
            "P012046",
            "P012047",
            "P012048",
            "P012049",
        ],
        "total_households": ["P019001"],
        "hh_w_children": ["P019008", "P019012", "P019015"],
    }
    df10 = c.get_dec_data(variables_dict, 2010, "tract", "sf1", county_ids, state_id)
    df10["age_under_65"] = df10["total_population"] - df10["age_65_plus"]
    df10["hh_no_children"] = df10["total_households"] - df10["hh_w_children"]

    # Get ACS variables for 2010 that we don't have in the decennial SF1
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
        "total_persons_5_plus": ["B16004_001E"],
        "limited_english": [
            "B16004_007E",
            "B16004_008E",
            "B16004_012E",
            "B16004_013E",
            "B16004_017E",
            "B16004_018E",
            "B16004_022E",
            "B16004_023E",
            "B16004_029E",
            "B16004_030E",
            "B16004_034E",
            "B16004_035E",
            "B16004_039E",
            "B16004_040E",
            "B16004_044E",
            "B16004_045E",
            "B16004_051E",
            "B16004_052E",
            "B16004_056E",
            "B16004_057E",
            "B16004_061E",
            "B16004_062E",
            "B16004_066E",
            "B16004_067E",
        ],
    }
    acs10 = c.get_acs_data(variables_dict, 2010, "tract", "acs5", county_ids, state_id)
    acs10["not_limited_english"] = acs10["total_persons_5_plus"] - acs10["limited_english"]
    # combine acs and decennial data
    df10 = df10.merge(acs10, on="geoid", how="outer")
    
    input_files = context["input_files"]
    xwalk10_path: Path = input_files["xwalk_2010_2020"]
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
