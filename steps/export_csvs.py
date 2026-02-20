from __future__ import annotations

from pathlib import Path

import pandas as pd


def run_step(context: dict) -> None:
    out_dir: Path = context["paths"]["output"]
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = context["artifacts"]
    run_tag = context.get("run_tag") or pd.Timestamp("today").strftime("%Y_%m%d")

    df_poc = pd.read_parquet(artifacts["df_poc"])
    df_poverty = pd.read_parquet(artifacts["df_poverty"])

    df_poc.to_csv(out_dir / f"reap_hist_poc_{run_tag}.csv", index=False)
    df_poverty.to_csv(out_dir / f"reap_hist_poverty_{run_tag}.csv", index=False)
