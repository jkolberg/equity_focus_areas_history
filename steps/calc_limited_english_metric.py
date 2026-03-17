from __future__ import annotations

import pandas as pd

from util.metrics import calculate_efa_metric


def run_step(context: dict) -> None:
	artifacts = context["artifacts"]
	df = pd.read_parquet(artifacts["df_all"]).copy()
	cols_dict = context["cols_dict"]

	english_cols = cols_dict["total_persons_5_plus"]["english_proficiency"]
	df_limited_english = df[["tr2020ge", "total_persons_5_plus", "year"] + english_cols].copy()
	df_limited_english = calculate_efa_metric(
		df_limited_english,
		col="limited_english",
		total_col="total_persons_5_plus",
		groupby_col="year",
	)

	out_path = artifacts["df_limited_english"]
	df_limited_english.to_parquet(out_path, index=False)
