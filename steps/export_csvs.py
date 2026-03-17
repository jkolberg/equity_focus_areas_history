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
    df_hh_w_children = pd.read_parquet(artifacts["df_hh_w_children"])
    df_limited_english = pd.read_parquet(artifacts["df_limited_english"])
    df_senior_population = pd.read_parquet(artifacts["df_senior_population"])

    df_poc.to_csv(out_dir / f"reap_hist_poc_{run_tag}.csv", index=False)
    df_poverty.to_csv(out_dir / f"reap_hist_poverty_{run_tag}.csv", index=False)
    df_hh_w_children.to_csv(out_dir / f"reap_hist_hh_w_children_{run_tag}.csv", index=False)
    df_limited_english.to_csv(out_dir / f"reap_hist_limited_english_{run_tag}.csv", index=False)
    df_senior_population.to_csv(out_dir / f"reap_hist_senior_population_{run_tag}.csv", index=False)
