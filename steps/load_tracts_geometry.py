from __future__ import annotations

import geopandas as gpd


def run_step(context: dict) -> None:
    tracts = gpd.read_file(
        "https://www2.census.gov/geo/tiger/TIGER2025/TRACT/tl_2025_53_tract.zip"
    )[["GEOID", "geometry"]]

    tracts["tr2020ge"] = tracts["GEOID"].astype("int64")
    tracts = tracts.drop(columns=["GEOID"])

    out_path = context["artifacts"]["tracts"]
    tracts.to_parquet(out_path, index=False)
