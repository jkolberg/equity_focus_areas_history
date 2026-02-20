from __future__ import annotations

import pandas as pd
from iteround import saferound


def xwalk_merge_sum(
    xwalk: pd.DataFrame,
    xwalk_left_index: str,
    xwalk_right_index: str,
    df: pd.DataFrame,
    df_index: str,
    wt_col: str,
    col_list: list[str],
) -> pd.DataFrame:
    xwalk = xwalk.merge(df, left_on=xwalk_left_index, right_on=df_index, how="left")

    for col in col_list:
        xwalk[col] = xwalk[col] * xwalk[wt_col]

    xwalk = xwalk[col_list + [xwalk_right_index]].groupby(xwalk_right_index).sum()
    return xwalk.reset_index()


def normalize_round(df: pd.DataFrame, index_col: str, col_dict: dict) -> pd.DataFrame:
    out_df = pd.DataFrame()

    for total_col in col_dict:
        tot_df = df[[index_col, total_col]].copy().rename(columns={total_col: "total"}).set_index(
            index_col
        )
        tot_df["total"] = saferound(tot_df["total"], 0)

        for group in col_dict[total_col]:
            tidy_df = df[[index_col] + col_dict[total_col][group]].melt(
                id_vars=[index_col],
                value_vars=col_dict[total_col][group],
                var_name="variable",
                value_name="total",
            )
            tidy_df = tidy_df.set_index(index_col)
            tidy_df["pct"] = tidy_df["total"] / tidy_df.groupby(index_col)["total"].transform(
                "sum"
            )
            tidy_df = tidy_df.drop(columns=["total"])

            tidy_df = tidy_df.merge(tot_df, how="left", left_index=True, right_index=True)

            tidy_df["new_total"] = tidy_df["pct"] * tidy_df["total"]

            for geog in tidy_df.index.unique():
                mask = tidy_df.index == geog
                if tidy_df.loc[mask, "pct"].sum() > 0:
                    tidy_df.loc[mask, "new_total"] = saferound(tidy_df.loc[mask, "new_total"], 0)

            tidy_df = tidy_df.drop(columns=["pct", "total"]).rename(columns={"new_total": total_col})

            result = tidy_df.reset_index().pivot(index=index_col, columns="variable", values=total_col)
            result.columns.name = None
            result[total_col] = result.sum(axis=1)

            out_df = out_df.merge(result, how="outer", left_index=True, right_index=True)

    return out_df.fillna(0).astype(int).reset_index()
