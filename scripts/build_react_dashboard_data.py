from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from config import PROCESSED_DIR, ROOT, SELECTED_METERS, TARGET_BUILDING
from io_utils import ensure_dir


DASHBOARD_DATA_DIR = ROOT / "web" / "public" / "data"
DEFAULT_SCENARIO = "balanced"


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return round(float(value), 6)
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    out = df.copy()
    for column in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[column]):
            out[column] = out[column].dt.strftime("%Y-%m-%d")
    return [
        {key: _clean_value(value) for key, value in row.items()}
        for row in out.to_dict(orient="records")
    ]


def _write_json(name: str, payload: Any) -> Path:
    ensure_dir(DASHBOARD_DATA_DIR)
    path = DASHBOARD_DATA_DIR / name
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return path


def _read(name: str, parse_dates: bool = False) -> pd.DataFrame:
    path = PROCESSED_DIR / name
    if parse_dates:
        return pd.read_csv(path, parse_dates=["date"])
    return pd.read_csv(path)


def build_daily_trend(fact: pd.DataFrame, anomalies: pd.DataFrame) -> pd.DataFrame:
    balanced = anomalies[anomalies["scenario"].eq(DEFAULT_SCENARIO)]
    anomaly_daily = (
        balanced.groupby("date", as_index=False)
        .agg(
            balanced_anomaly_count=("anomaly_flag", "sum"),
            average_anomaly_score=("anomaly_score", "mean"),
        )
    )
    trend = (
        fact.groupby("date", as_index=False)
        .agg(
            total_consumption=("daily_consumption", "sum"),
            average_consumption=("daily_consumption", "mean"),
            peak_meter_consumption=("daily_consumption", "max"),
            entity_count=("entity_id", "nunique"),
            mean_temperature_c=("mean_temperature_c", "mean"),
            rainfall_mm_model=("rainfall_mm_model", "mean"),
            is_weekend=("is_weekend", "max"),
            is_hot_day_28c=("is_hot_day_28c", "max"),
            is_rainy_day=("is_rainy_day", "max"),
            quality_issue_rows=("data_quality_flag", lambda s: int((s != "valid").sum())),
        )
        .merge(anomaly_daily, on="date", how="left")
        .sort_values("date")
    )
    trend["balanced_anomaly_count"] = trend["balanced_anomaly_count"].fillna(0).astype(int)
    trend["average_anomaly_score"] = trend["average_anomaly_score"].fillna(0)
    return trend


def build_monthly_trend(daily: pd.DataFrame) -> pd.DataFrame:
    daily = daily.copy()
    daily["year_month"] = pd.to_datetime(daily["date"]).dt.to_period("M").astype(str)
    return (
        daily.groupby("year_month", as_index=False)
        .agg(
            total_consumption=("total_consumption", "sum"),
            average_daily_consumption=("total_consumption", "mean"),
            peak_daily_consumption=("total_consumption", "max"),
            anomaly_count=("balanced_anomaly_count", "sum"),
            rainy_days=("is_rainy_day", "sum"),
            hot_days=("is_hot_day_28c", "sum"),
        )
        .sort_values("year_month")
    )


def main() -> None:
    ensure_dir(DASHBOARD_DATA_DIR)

    fact = _read("fact_energy_weather_daily.csv", parse_dates=True)
    anomalies = _read("fact_anomaly_scenarios.csv", parse_dates=True)
    dim_entity = _read("dim_entity.csv")
    dim_scenario = _read("dim_scenario.csv")
    scorecard = _read("entity_scorecard.csv")
    cases = _read("anomaly_case_review.csv", parse_dates=True)
    quality = _read("data_quality_summary.csv")
    model_eval = _read("model_evaluation_summary.csv")
    eda_summary = _read("eda_summary.csv")
    insights = _read("insight_recommendation_matrix.csv")

    daily = build_daily_trend(fact, anomalies)
    monthly = build_monthly_trend(daily)

    entity_daily_columns = [
        "date",
        "entity_id",
        "meter_id",
        "building",
        "floor",
        "room_or_equipment",
        "daily_consumption",
        "meter_reading",
        "mean_temperature_c",
        "rainfall_mm_model",
        "global_solar_radiation_mj_m2_model",
        "is_weekend",
        "is_hot_day_28c",
        "is_rainy_day",
        "temperature_band",
        "rainfall_band",
        "data_quality_flag",
        "meter_quality_flag",
        "is_model_eligible",
    ]
    anomaly_columns = [
        "date",
        "entity_id",
        "meter_id",
        "building",
        "floor",
        "room_or_equipment",
        "scenario",
        "contamination",
        "anomaly_score",
        "anomaly_flag",
        "anomaly_rank_within_scenario",
        "daily_consumption",
        "rolling_mean_7d",
        "deviation_from_rolling_mean_7d",
        "pct_deviation_from_rolling_mean_7d",
        "mean_temperature_c",
        "rainfall_mm_model",
        "is_weekend",
        "is_hot_day_28c",
        "is_rainy_day",
        "iqr_anomaly_flag",
        "zscore_anomaly_flag",
        "baseline_agreement_count",
        "baseline_agreement_label",
        "data_quality_flag",
        "is_model_eligible",
        "feature_complete_flag",
    ]

    output_files = {
        "manifest.json": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source": "Data_Acquisition/dataset/processed",
            "default_scenario": DEFAULT_SCENARIO,
            "target_building": TARGET_BUILDING,
            "selected_meters": SELECTED_METERS,
            "date_range": {
                "start": str(fact["date"].min().date()),
                "end": str(fact["date"].max().date()),
            },
            "row_counts": {
                "fact_energy_weather_daily": int(len(fact)),
                "fact_anomaly_scenarios": int(len(anomalies)),
                "selected_entities": int(fact["entity_id"].nunique()),
                "dim_entity": int(len(dim_entity)),
                "top_anomaly_cases": int(len(cases)),
            },
            "limitations": [
                "Selected T1440 daily meter-level analysis, not full-campus coverage.",
                "Selected active meters are focused on Cheng Yu Tung Building.",
                "Weather variables provide context and are not causal proof.",
                "No supervised anomaly labels are available.",
            ],
        },
        "daily_trend.json": _records(daily),
        "monthly_trend.json": _records(monthly),
        "entity_daily.json": _records(fact[entity_daily_columns].sort_values(["date", "entity_id"])),
        "anomalies.json": _records(anomalies[anomaly_columns].sort_values(["scenario", "date", "entity_id"])),
        "dimensions.json": {
            "entities": _records(dim_entity.sort_values(["is_selected_main_subset", "entity_id"], ascending=[False, True])),
            "scenarios": _records(dim_scenario.sort_values("contamination")),
        },
        "entity_scorecard.json": _records(scorecard.sort_values("entity_priority_rank")),
        "anomaly_case_review.json": _records(cases.sort_values("anomaly_rank_within_scenario")),
        "data_quality_summary.json": _records(quality),
        "model_evaluation_summary.json": _records(model_eval.sort_values("contamination")),
        "eda_summary.json": _records(eda_summary),
        "insight_recommendation_matrix.json": _records(insights),
    }

    written = [_write_json(name, payload) for name, payload in output_files.items()]

    manifest = output_files["manifest.json"]
    manifest["generated_files"] = [path.name for path in written]
    _write_json("manifest.json", manifest)

    print(f"Wrote {len(written)} dashboard JSON files to {DASHBOARD_DATA_DIR}")


if __name__ == "__main__":
    main()
