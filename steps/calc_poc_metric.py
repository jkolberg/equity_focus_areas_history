from __future__ import annotations

import pandas as pd

from util.metrics import calculate_efa_metric


def run_step(context: dict) -> None:
    artifacts = context["artifacts"]
    df = pd.read_parquet(artifacts["df_all"]).copy()
    cols_dict = context["cols_dict"]

    df["poc"] = df["total_population"] - df["white_nh"]
    race_cols = cols_dict["total_population"]["race"]
    df_poc = df[["tr2020ge", "total_population", "year"] + race_cols + ["poc"]].copy()
    df_poc = calculate_efa_metric(df_poc, col="poc", total_col="total_population", groupby_col="year")

    out_path = artifacts["df_poc"]
    df_poc.to_parquet(out_path, index=False)
