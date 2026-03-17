from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


def save_html_map(df, tracts, col: str, out_dir: Path) -> None:
    for year in (1990, 2000, 2010, 2020):
        df_year = df.loc[df["year"] == year]
        out = tracts.merge(df_year, on="tr2020ge")
        out.explore(col, scheme="percentiles", cmap="YlOrRd_r").save(
            out_dir / f"reap_hist_{year}_{col}.html"
        )


def run_step(context: dict) -> None:
    out_dir: Path = context["paths"]["output"]
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = context["artifacts"]
    df_poc = pd.read_parquet(artifacts["df_poc"])
    df_poverty = pd.read_parquet(artifacts["df_poverty"])
    df_hh_w_children = pd.read_parquet(artifacts["df_hh_w_children"])
    df_limited_english = pd.read_parquet(artifacts["df_limited_english"])
    df_senior_population = pd.read_parquet(artifacts["df_senior_population"])
    tracts = gpd.read_parquet(artifacts["tracts"])

    save_html_map(df_poc, tracts, "poc_category", out_dir)
    save_html_map(
        df_poverty,
        tracts,
        "below_200_percent_poverty_category",
        out_dir,
    )
    save_html_map(df_hh_w_children, tracts, "hh_w_children_category", out_dir)
    save_html_map(df_limited_english, tracts, "limited_english_category", out_dir)
    save_html_map(df_senior_population, tracts, "age_65_plus_category", out_dir)
