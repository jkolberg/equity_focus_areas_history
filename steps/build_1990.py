from __future__ import annotations

from pathlib import Path

import pandas as pd

from util.transforms import normalize_round, xwalk_merge_sum


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")


def run_step(context: dict) -> None:
    paths = context["paths"]
    data_dir: Path = paths["data"]
    xwalks_dir: Path = paths["xwalks"]

    race_path = data_dir / "nhgis0017_ds120_1990_tract.csv"
    poverty_path = data_dir / "nhgis0018_ds123_1990_tract.csv"
    hh_w_children_path = data_dir / "nhgis0019_ds123_1990_tract.csv"
    age_path = data_dir / "nhgis0019_ds120_1990_tract.csv"
    xwalk90_path = xwalks_dir / "nhgis_tr1990_tr2010_53.csv"
    xwalk10_path = xwalks_dir / "nhgis_tr2010_tr2020_53.csv"

    for p in (race_path, poverty_path, hh_w_children_path, xwalk90_path, xwalk10_path):
        _require_file(p)

    cols_to_get = context["cols_to_get"]
    cols_dict = context["cols_dict"]

    df90_1 = pd.read_csv(race_path)
    df90_1["hispanic"] = df90_1[["ET2006", "ET2007", "ET2008", "ET2009", "ET2010"]].sum(
        axis=1
    )
    df90_1 = df90_1.rename(
        columns={
            "ET1001": "total_population",
            "ET2001": "white_nh",
            "ET2002": "black_nh",
            "ET2003": "aian_nh",
            "ET2004": "asian_pac_nh",
            "ET2005": "other_nh",
        }
    )
    df90_1 = df90_1[['GISJOIN'] + [col for col in df90_1.columns if col in cols_to_get]]

    df90_2 = pd.read_csv(poverty_path)
    poverty_all_cols = [
        "E1C001",
        "E1C002",
        "E1C003",
        "E1C004",
        "E1C005",
        "E1C006",
        "E1C007",
        "E1C008",
        "E1C009",
    ]
    df90_2["total_poverty_status_pop"] = df90_2[poverty_all_cols].sum(axis=1)
    df90_2["above_200_percent_poverty"] = df90_2["E1C009"]
    df90_2["below_200_percent_poverty"] = (
        df90_2["total_poverty_status_pop"] - df90_2["above_200_percent_poverty"]
    )
    df90_2 = df90_2[['GISJOIN'] + [col for col in df90_2.columns if col in cols_to_get]]

    df90_3 = pd.read_csv(hh_w_children_path)
    w_children_cols = [
        "E2W001",
        "E2W003",
        "E2W005",
    ]
    no_children_cols = [
        "E2W002",
        "E2W004",
        "E2W006",
        "E2W007",
    ]
    df90_3["hh_w_children"] = df90_3[w_children_cols].sum(axis=1)
    df90_3["hh_no_children"] = df90_3[no_children_cols].sum(axis=1)
    df90_3['total_households'] = df90_3['hh_w_children'] + df90_3['hh_no_children']

    limited_english_cols = [
        "E26004",
        "E26007",
        "E26010",
        "E26014",
        "E26017",
        "E26020",
        "E26024",
        "E26027",
        "E26030"
    ]
    persons_5_plus_cols = [f"E{26000 + i}" for i in range(1, 31)]
    df90_3['limited_english'] = df90_3[limited_english_cols].sum(axis=1)
    df90_3['total_persons_5_plus'] = df90_3[persons_5_plus_cols].sum(axis=1)
    df90_3['not_limited_english'] = df90_3['total_persons_5_plus'] - df90_3['limited_english']
    df90_3 = df90_3[['GISJOIN'] + [col for col in df90_3.columns if col in cols_to_get]]

    df90_4 = pd.read_csv(age_path)
    age_65_plus_cols = [f"ET{3000 + i}" for i in range(27,32)]
    df90_4["age_65_plus"] = df90_4[age_65_plus_cols].sum(axis=1)
    under_65_cols = [f"ET{3000 + i}" for i in range(1, 27)]
    df90_4['age_under_65'] = df90_4[under_65_cols].sum(axis=1)
    df90_4 = df90_4[['GISJOIN'] + [col for col in df90_4.columns if col in cols_to_get]]

    df90 = (
        df90_1.merge(df90_2, on="GISJOIN", how="outer")
        .merge(df90_3, on="GISJOIN", how="outer")
        .merge(df90_4, on="GISJOIN", how="outer")
    )

    xwalk90 = pd.read_csv(xwalk90_path)
    xwalk10 = pd.read_csv(xwalk10_path)

    out90 = xwalk_merge_sum(
        xwalk90,
        "tr1990gj",
        "tr2010ge",
        df90,
        "GISJOIN",
        "wt_pop",
        cols_to_get,
    )
    out90_to_20 = xwalk_merge_sum(
        xwalk10,
        "tr2010ge",
        "tr2020ge",
        out90,
        "tr2010ge",
        "wt_pop",
        cols_to_get,
    )

    county_ids = context["county_ids"]
    out90_to_20["county_id"] = out90_to_20["tr2020ge"].astype(str).str[0:5].astype(int)
    out90_to_20 = out90_to_20.loc[out90_to_20["county_id"].isin(county_ids)].copy()

    out90_to_20 = normalize_round(out90_to_20, "tr2020ge", cols_dict)
    out90_to_20["year"] = 1990

    out_path = context["artifacts"]["out90_to_20"]
    out90_to_20.to_parquet(out_path, index=False)
