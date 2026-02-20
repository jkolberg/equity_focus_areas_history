from __future__ import annotations


def run_step(context: dict) -> None:
    cols_dict = {
        "total_population": {
            "race": [
                "hispanic",
                "white_nh",
                "black_nh",
                "aian_nh",
                "asian_pac_nh",
                "other_nh",
            ],
        },
        "total_poverty_status_pop": {
            "poverty_status": [
                "below_200_percent_poverty",
                "above_200_percent_poverty",
            ],
        },
    }

    cols_to_get: list[str] = []
    for total_col, group_dict in cols_dict.items():
        for cols in group_dict.values():
            cols_to_get.extend(cols)
    cols_to_get = cols_to_get + list(cols_dict.keys())

    context["cols_dict"] = cols_dict
    context["cols_to_get"] = cols_to_get
