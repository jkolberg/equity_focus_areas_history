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
    }
    acs20 = c.get_acs_data(variables_dict, 2020, "tract", "acs5", county_ids, state_id)

    df20 = df20.merge(acs20, left_on="tr2020ge", right_on="geoid", how="outer").drop(
        columns=["geoid"]
    )

    out_path = context["artifacts"]["df20"]
    df20.to_parquet(out_path, index=False)
