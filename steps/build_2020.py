from __future__ import annotations

import pandas as pd


def run_step(context: dict) -> None:
    c = context["census"]
    county_ids = context["county_ids"]
    state_id = context["state_id"]

    variables_dict = {
        "total_population": ["P1_001N"],
        "hispanic": ["P9_002N"],
        "white_nh": ["P9_005N"],
        "black_nh": ["P9_006N"],
        "aian_nh": ["P9_007N"],
        "asian_pac_nh": ["P9_008N", "P9_009N"],
        "other_nh": ["P9_010N", "P9_011N"],
        "age_65_plus": [
            "P12_020N",
            "P12_021N",
            "P12_022N",
            "P12_023N",
            "P12_024N",
            "P12_025N",
            "P12_044N",
            "P12_045N",
            "P12_046N",
            "P12_047N",
            "P12_048N",
            "P12_049N",
        ],
        "total_households": ["P20_001N"],
        "hh_w_children": ["P20_003N", "P20_006N", "P20_011N", "P20_017N"],
    }
    df20 = c.get_dec_data(variables_dict, 2020, "tract", "dhc", county_ids, state_id)
    df20 = (
        df20.drop(columns="name")
        .rename(columns={"geoid": "tr2020ge"})
        .assign(
            county_id=lambda x: x["tr2020ge"].astype(str).str[0:5].astype(int),
            year=2020,
        )
        .set_index("tr2020ge")
        .astype(int)
        .reset_index()
    )

    variables_dict = {
        "total_poverty_status_pop": ["B17026_001E"],
        "below_200_percent_poverty": [
            "B17026_002E",
            "B17026_003E",
            "B17026_004E",
            "B17026_005E",
            "B17026_006E",
            "B17026_007E",
            "B17026_008E",
            "B17026_009E",
        ],
        "above_200_percent_poverty": [
            "B17026_010E",
            "B17026_011E",
            "B17026_012E",
            "B17026_013E",
        ],
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
    acs20 = c.get_acs_data(variables_dict, 2020, "tract", "acs5", county_ids, state_id)

    df20 = df20.merge(acs20, left_on="tr2020ge", right_on="geoid", how="outer").drop(
        columns=["geoid"]
    )
    df20["age_under_65"] = df20["total_population"] - df20["age_65_plus"]
    df20["hh_no_children"] = df20["total_households"] - df20["hh_w_children"]
    df20["not_limited_english"] = df20["total_persons_5_plus"] - df20["limited_english"]

    out_path = context["artifacts"]["df20"]
    df20.to_parquet(out_path, index=False)
