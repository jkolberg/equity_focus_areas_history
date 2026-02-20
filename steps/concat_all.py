from __future__ import annotations

import pandas as pd


def run_step(context: dict) -> None:
    artifacts = context["artifacts"]

    df = pd.concat(
        [
            pd.read_parquet(artifacts["out90_to_20"]),
            pd.read_parquet(artifacts["out00_to_20"]),
            pd.read_parquet(artifacts["out10_to_20"]),
            pd.read_parquet(artifacts["df20"]),
        ],
        ignore_index=True,
    )

    df = df.drop(columns=["county_id", "name"], errors="ignore")

    out_path = artifacts["df_all"]
    df.to_parquet(out_path, index=False)
