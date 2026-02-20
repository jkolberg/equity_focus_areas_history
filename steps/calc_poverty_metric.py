from __future__ import annotations

import pandas as pd

from util.metrics import calculate_efa_metric


def run_step(context: dict) -> None:
    artifacts = context["artifacts"]
    df = pd.read_parquet(artifacts["df_all"]).copy()
    cols_dict = context["cols_dict"]

    poverty_cols = cols_dict["total_poverty_status_pop"]["poverty_status"]
    df_poverty = df[["tr2020ge", "total_poverty_status_pop", "year"] + poverty_cols].copy()
    df_poverty = calculate_efa_metric(
        df_poverty,
        col="below_200_percent_poverty",
        total_col="total_poverty_status_pop",
        groupby_col="year",
    )

    out_path = artifacts["df_poverty"]
    df_poverty.to_parquet(out_path, index=False)
