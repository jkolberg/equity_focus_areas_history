from __future__ import annotations

import pandas as pd


def calculate_efa_metric(
    df: pd.DataFrame,
    col: str,
    total_col: str,
    groupby_col: str | None = "year",
) -> pd.DataFrame:
    pct_col = f"pct_{col}"
    reg_pct_col = f"reg_pct_{col}"
    reg_std_dev_pct_col = f"reg_std_dev_pct_{col}"

    df[pct_col] = df[col] / df[total_col]

    if groupby_col:
        df[reg_pct_col] = df.groupby(groupby_col)[col].transform("sum") / df.groupby(groupby_col)[
            total_col
        ].transform("sum")
        df[reg_std_dev_pct_col] = df.groupby(groupby_col)[pct_col].transform("std")
    else:
        df[reg_pct_col] = df[col].sum() / df[total_col].sum()
        df[reg_std_dev_pct_col] = df[pct_col].std()

    df[f"{col}_pct_above_reg_avg"] = df[pct_col] > df[reg_pct_col]
    df[f"{col}_pct_above_1sd"] = df[pct_col] > (df[reg_pct_col] + df[reg_std_dev_pct_col])

    df[f"{col}_category"] = "Below Regional Average"
    df.loc[df[f"{col}_pct_above_reg_avg"], f"{col}_category"] = "Above Regional Average"
    df.loc[df[f"{col}_pct_above_1sd"], f"{col}_category"] = "Above 1 Std Dev"

    return df
