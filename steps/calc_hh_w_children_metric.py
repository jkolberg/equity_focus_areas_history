from __future__ import annotations

import pandas as pd

from util.metrics import calculate_efa_metric


def run_step(context: dict) -> None:
	artifacts = context["artifacts"]
	df = pd.read_parquet(artifacts["df_all"]).copy()
	cols_dict = context["cols_dict"]

	household_cols = cols_dict["total_households"]["household_type"]
	df_hh_w_children = df[["tr2020ge", "total_households", "year"] + household_cols].copy()
	df_hh_w_children = calculate_efa_metric(
		df_hh_w_children,
		col="hh_w_children",
		total_col="total_households",
		groupby_col="year",
	)

	out_path = artifacts["df_hh_w_children"]
	df_hh_w_children.to_parquet(out_path, index=False)
