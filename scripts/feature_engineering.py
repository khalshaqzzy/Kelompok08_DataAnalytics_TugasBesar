from __future__ import annotations

import numpy as np
import pandas as pd

from config import PROCESSED_DIR
from io_utils import assert_required_columns, assert_unique_key, read_csv_dates, write_csv


FEATURE_SET_VERSION = "energy_anomaly_v1"

MODEL_FEATURE_COLUMNS = [
    "daily_consumption",
    "rolling_mean_7d",
    "rolling_std_7d",
    "deviation_from_rolling_mean_7d",
    "pct_deviation_from_rolling_mean_7d",
    "lag_1d_consumption",
    "lag_7d_consumption",
    "diff_from_lag_1d",
    "diff_from_lag_7d",
    "is_weekend",
    "month",
    "day_of_week_num",
    "mean_temperature_c",
    "relative_humidity_pct",
    "rainfall_mm_model",
    "global_solar_radiation_mj_m2_model",
    "mean_wind_speed_kmh",
    "cooling_degree_day_24c",
    "is_rainy_day",
    "is_hot_day_28c",
]

ENGINEERED_FEATURES = {
    "log_daily_consumption": {
        "group": "consumption_transform",
        "use": "eda,model,interpretation",
        "description": "Natural log transform of daily consumption using log1p.",
        "leakage": "none",
    },
    "consumption_rank_within_entity": {
        "group": "consumption_transform",
        "use": "eda,interpretation",
        "description": "Ascending rank of daily consumption within each entity.",
        "leakage": "uses full history for descriptive ranking; do not use for model training.",
    },
    "consumption_percentile_within_entity": {
        "group": "consumption_transform",
        "use": "eda,interpretation",
        "description": "Percentile rank of daily consumption within each entity.",
        "leakage": "uses full history for descriptive ranking; do not use for model training.",
    },
    "rolling_mean_7d": {
        "group": "rolling_consumption",
        "use": "model,interpretation",
        "description": "Trailing 7-row mean of daily consumption per entity, excluding the current row.",
        "leakage": "past_only",
    },
    "rolling_std_7d": {
        "group": "rolling_consumption",
        "use": "model,interpretation",
        "description": "Trailing 7-row standard deviation of daily consumption per entity, excluding the current row.",
        "leakage": "past_only",
    },
    "deviation_from_rolling_mean_7d": {
        "group": "rolling_consumption",
        "use": "model,interpretation",
        "description": "Difference between daily consumption and trailing 7-row mean.",
        "leakage": "past_only",
    },
    "pct_deviation_from_rolling_mean_7d": {
        "group": "rolling_consumption",
        "use": "model,interpretation",
        "description": "Percent deviation from trailing 7-row mean.",
        "leakage": "past_only",
    },
    "lag_1d_consumption": {
        "group": "lag_consumption",
        "use": "model,interpretation",
        "description": "Previous observed daily consumption for the same entity.",
        "leakage": "past_only",
    },
    "lag_7d_consumption": {
        "group": "lag_consumption",
        "use": "model,interpretation",
        "description": "Daily consumption seven rows earlier for the same entity.",
        "leakage": "past_only",
    },
    "diff_from_lag_1d": {
        "group": "lag_consumption",
        "use": "model,interpretation",
        "description": "Difference between current daily consumption and lag_1d_consumption.",
        "leakage": "past_only",
    },
    "diff_from_lag_7d": {
        "group": "lag_consumption",
        "use": "model,interpretation",
        "description": "Difference between current daily consumption and lag_7d_consumption.",
        "leakage": "past_only",
    },
    "is_month_start": {
        "group": "calendar",
        "use": "dashboard,model",
        "description": "1 when the date is the first calendar day of the month.",
        "leakage": "none",
    },
    "is_month_end": {
        "group": "calendar",
        "use": "dashboard,model",
        "description": "1 when the date is the last calendar day of the month.",
        "leakage": "none",
    },
    "temperature_band": {
        "group": "weather_context",
        "use": "eda,dashboard,interpretation",
        "description": "Categorical band for mean daily temperature.",
        "leakage": "none",
    },
    "rainfall_band": {
        "group": "weather_context",
        "use": "eda,dashboard,interpretation",
        "description": "Categorical band for daily rainfall.",
        "leakage": "none",
    },
    "feature_complete_flag": {
        "group": "feature_readiness",
        "use": "model,dashboard",
        "description": "1 when all selected numeric model features are non-null for an eligible row.",
        "leakage": "none",
    },
    "model_feature_set_version": {
        "group": "feature_readiness",
        "use": "model,dashboard",
        "description": "Version label for the selected model feature set.",
        "leakage": "none",
    },
}


def add_consumption_features(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.copy()
    out["log_daily_consumption"] = np.log1p(out["daily_consumption"].clip(lower=0))
    grouped = out.groupby("entity_id")["daily_consumption"]
    out["consumption_rank_within_entity"] = grouped.rank(method="average", ascending=True)
    out["consumption_percentile_within_entity"] = grouped.rank(pct=True, ascending=True)
    return out


def add_rolling_and_lag_features(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.sort_values(["entity_id", "date"]).copy()
    grouped = out.groupby("entity_id", group_keys=False)["daily_consumption"]
    shifted = grouped.shift(1)
    out["rolling_mean_7d"] = shifted.groupby(out["entity_id"]).rolling(
        window=7, min_periods=3
    ).mean().reset_index(level=0, drop=True)
    out["rolling_std_7d"] = shifted.groupby(out["entity_id"]).rolling(
        window=7, min_periods=3
    ).std(ddof=0).reset_index(level=0, drop=True)
    out["rolling_std_7d"] = out["rolling_std_7d"].replace(0, np.nan)
    out["deviation_from_rolling_mean_7d"] = (
        out["daily_consumption"] - out["rolling_mean_7d"]
    )
    out["pct_deviation_from_rolling_mean_7d"] = (
        out["deviation_from_rolling_mean_7d"] / out["rolling_mean_7d"].replace(0, np.nan)
    )
    out["lag_1d_consumption"] = grouped.shift(1)
    out["lag_7d_consumption"] = grouped.shift(7)
    out["diff_from_lag_1d"] = out["daily_consumption"] - out["lag_1d_consumption"]
    out["diff_from_lag_7d"] = out["daily_consumption"] - out["lag_7d_consumption"]
    return out


def add_calendar_and_weather_context(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.copy()
    out["is_month_start"] = out["date"].dt.is_month_start.astype(int)
    out["is_month_end"] = out["date"].dt.is_month_end.astype(int)
    out["temperature_band"] = pd.cut(
        out["mean_temperature_c"],
        bins=[-np.inf, 18, 24, 28, np.inf],
        labels=["cool", "mild", "warm", "hot"],
    ).astype("string")
    out["rainfall_band"] = pd.cut(
        out["rainfall_mm_model"],
        bins=[-np.inf, 0, 5, 25, np.inf],
        labels=["none", "light", "moderate", "heavy"],
    ).astype("string")
    return out


def add_feature_readiness(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.copy()
    out["model_feature_set_version"] = FEATURE_SET_VERSION
    complete = out[MODEL_FEATURE_COLUMNS].notna().all(axis=1)
    out["feature_complete_flag"] = (
        out["is_model_eligible"].eq(1) & complete
    ).astype(int)
    return out


def build_feature_summary(fact: pd.DataFrame) -> pd.DataFrame:
    rows = []
    eligible = fact["is_model_eligible"].eq(1)
    for feature, meta in ENGINEERED_FEATURES.items():
        non_null = int(fact[feature].notna().sum())
        missing = int(fact[feature].isna().sum())
        rows.append(
            {
                "feature_name": feature,
                "feature_group": meta["group"],
                "non_null_count": non_null,
                "missing_count": missing,
                "missing_rate": missing / len(fact) if len(fact) else 0,
                "eligible_non_null_count": int(fact.loc[eligible, feature].notna().sum()),
                "intended_use": meta["use"],
                "leakage_risk_note": meta["leakage"],
            }
        )
    for feature in MODEL_FEATURE_COLUMNS:
        if feature in ENGINEERED_FEATURES:
            continue
        non_null = int(fact[feature].notna().sum())
        missing = int(fact[feature].isna().sum())
        rows.append(
            {
                "feature_name": feature,
                "feature_group": "model_input_existing",
                "non_null_count": non_null,
                "missing_count": missing,
                "missing_rate": missing / len(fact) if len(fact) else 0,
                "eligible_non_null_count": int(fact.loc[eligible, feature].notna().sum()),
                "intended_use": "model",
                "leakage_risk_note": "existing source or calendar/weather field",
            }
        )
    return pd.DataFrame(rows)


def update_data_dictionary(dictionary: pd.DataFrame, fact: pd.DataFrame) -> pd.DataFrame:
    existing = set(zip(dictionary["table_name"], dictionary["column_name"]))
    rows = []
    for column, meta in ENGINEERED_FEATURES.items():
        key = ("fact_energy_weather_daily", column)
        if key in existing:
            dictionary.loc[
                (dictionary["table_name"] == key[0]) & (dictionary["column_name"] == key[1]),
                ["description", "source", "treatment_notes"],
            ] = [
                meta["description"],
                "feature engineering",
                f"Intended use: {meta['use']}; leakage note: {meta['leakage']}",
            ]
            continue
        rows.append(
            {
                "table_name": "fact_energy_weather_daily",
                "column_name": column,
                "dtype": str(fact[column].dtype),
                "description": meta["description"],
                "source": "feature engineering",
                "treatment_notes": f"Intended use: {meta['use']}; leakage note: {meta['leakage']}",
            }
        )
    if rows:
        dictionary = pd.concat([dictionary, pd.DataFrame(rows)], ignore_index=True)
    return dictionary.sort_values(["table_name", "column_name"]).reset_index(drop=True)


def build_feature_layer() -> dict[str, object]:
    fact_path = PROCESSED_DIR / "fact_energy_weather_daily.csv"
    dictionary_path = PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
    fact = read_csv_dates(fact_path)
    dictionary = pd.read_csv(dictionary_path)

    assert_required_columns(
        fact,
        [
            "date",
            "entity_id",
            "daily_consumption",
            "is_model_eligible",
            "rainfall_mm_model",
            "global_solar_radiation_mj_m2_model",
        ],
        "fact_energy_weather_daily",
    )
    assert_unique_key(fact, ["date", "entity_id"], "fact_energy_weather_daily")

    fact = add_consumption_features(fact)
    fact = add_rolling_and_lag_features(fact)
    fact = add_calendar_and_weather_context(fact)
    fact = add_feature_readiness(fact)
    assert_unique_key(fact, ["date", "entity_id"], "fact_energy_weather_daily")

    summary = build_feature_summary(fact)
    dictionary = update_data_dictionary(dictionary, fact)

    outputs = {
        "fact_energy_weather_daily": write_csv(fact, fact_path),
        "feature_engineering_summary": write_csv(
            summary, PROCESSED_DIR / "feature_engineering_summary.csv"
        ),
        "data_dictionary": write_csv(dictionary, dictionary_path),
        "model_feature_rows": int(fact["feature_complete_flag"].sum()),
        "feature_complete_rows": int(fact["feature_complete_flag"].sum()),
    }
    return outputs


def main() -> None:
    outputs = build_feature_layer()
    print("Wrote feature engineering outputs:")
    for name, value in outputs.items():
        print(f"- {name}: {value}")


if __name__ == "__main__":
    main()
