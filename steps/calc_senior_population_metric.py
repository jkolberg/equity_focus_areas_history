from __future__ import annotations

import pandas as pd

from util.metrics import calculate_efa_metric


def run_step(context: dict) -> None:
	artifacts = context["artifacts"]
	df = pd.read_parquet(artifacts["df_all"]).copy()
	cols_dict = context["cols_dict"]

	senior_cols = cols_dict["total_population"]["senior_population"]
	df_senior_population = df[["tr2020ge", "total_population", "year"] + senior_cols].copy()
	df_senior_population = calculate_efa_metric(
		df_senior_population,
		col="age_65_plus",
		total_col="total_population",
		groupby_col="year",
	)

	out_path = artifacts["df_senior_population"]
	df_senior_population.to_parquet(out_path, index=False)
