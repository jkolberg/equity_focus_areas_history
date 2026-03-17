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
            "senior_population": [
                "age_65_plus",
                "age_under_65",
            ],
        },
        "total_poverty_status_pop": {
            "poverty_status": [
                "below_200_percent_poverty",
                "above_200_percent_poverty",
            ],
        },
        "total_households": {
            "household_type": [
                "hh_w_children",
                "hh_no_children",
            ],
        },
        "total_persons_5_plus": {
            "english_proficiency": [
                "limited_english",
                "not_limited_english",
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
