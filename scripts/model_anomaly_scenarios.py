from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from config import ANOMALY_SCENARIOS, PROCESSED_DIR
from feature_engineering import FEATURE_SET_VERSION, MODEL_FEATURE_COLUMNS
from io_utils import assert_required_columns, assert_unique_key, read_csv_dates, write_csv


MODEL_NAME = "IsolationForest"
NO_GROUND_TRUTH_NOTE = (
    "No supervised anomaly labels are available; evaluation uses contamination sanity, "
    "IQR/Z-score agreement, scenario stability, and case review."
)


def add_baselines(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.copy()

    q1 = out.groupby("entity_id")["daily_consumption"].transform(lambda s: s.quantile(0.25))
    q3 = out.groupby("entity_id")["daily_consumption"].transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1
    out["iqr_lower_bound"] = q1 - (1.5 * iqr)
    out["iqr_upper_bound"] = q3 + (1.5 * iqr)
    out["iqr_anomaly_flag"] = (
        (out["daily_consumption"] < out["iqr_lower_bound"])
        | (out["daily_consumption"] > out["iqr_upper_bound"])
    ).astype(int)

    entity_mean = out.groupby("entity_id")["daily_consumption"].transform("mean")
    entity_std = out.groupby("entity_id")["daily_consumption"].transform("std").replace(0, np.nan)
    zscore = (out["daily_consumption"] - entity_mean) / entity_std
    out["zscore_daily_consumption"] = zscore.fillna(0)
    out["zscore_abs_daily_consumption"] = out["zscore_daily_consumption"].abs()
    out["zscore_anomaly_flag"] = out["zscore_abs_daily_consumption"].ge(3).astype(int)
    out["entity_zscore_daily_consumption"] = out["zscore_daily_consumption"]
    out["entity_zscore_anomaly_flag"] = out["zscore_anomaly_flag"]
    return out


def eligible_model_frame(fact: pd.DataFrame) -> pd.DataFrame:
    required = [
        "date",
        "entity_id",
        "is_model_eligible",
        "feature_complete_flag",
        *MODEL_FEATURE_COLUMNS,
    ]
    assert_required_columns(fact, required, "fact_energy_weather_daily")
    model_df = fact[
        fact["is_model_eligible"].eq(1)
        & fact["feature_complete_flag"].eq(1)
        & fact[MODEL_FEATURE_COLUMNS].notna().all(axis=1)
    ].copy()
    if model_df.empty:
        raise ValueError("No model-eligible rows with complete features.")
    return model_df


def build_scenario_outputs(model_df: pd.DataFrame) -> pd.DataFrame:
    feature_matrix = model_df[MODEL_FEATURE_COLUMNS].astype(float)
    scaled = StandardScaler().fit_transform(feature_matrix)
    scenario_frames = []
    for scenario, config in ANOMALY_SCENARIOS.items():
        contamination = float(config["contamination"])
        model = IsolationForest(
            n_estimators=100,
            max_samples="auto",
            contamination=contamination,
            random_state=42,
        )
        predictions = model.fit_predict(scaled)
        # Higher anomaly_score means more anomalous; rank handles Power BI sorting.
        anomaly_score = -model.decision_function(scaled)

        out = model_df.copy()
        out["scenario"] = scenario
        out["contamination"] = contamination
        out["model_name"] = MODEL_NAME
        out["model_feature_set_version"] = FEATURE_SET_VERSION
        out["anomaly_score"] = anomaly_score
        out["anomaly_flag"] = (predictions == -1).astype(int)
        out["anomaly_rank_within_scenario"] = (
            out["anomaly_score"].rank(method="first", ascending=False).astype(int)
        )
        scenario_frames.append(out)
    scenarios = pd.concat(scenario_frames, ignore_index=True)
    scenarios["baseline_agreement_count"] = (
        scenarios["iqr_anomaly_flag"].astype(int)
        + scenarios["zscore_anomaly_flag"].astype(int)
    )
    scenarios["baseline_agreement_label"] = np.select(
        [
            scenarios["baseline_agreement_count"].eq(2),
            scenarios["baseline_agreement_count"].eq(1),
        ],
        ["iqr_and_zscore", "one_baseline"],
        default="none",
    )
    return scenarios


def add_scenario_stability(scenarios: pd.DataFrame) -> pd.DataFrame:
    anomaly_sets = {
        scenario: set(
            zip(
                frame.loc[frame["anomaly_flag"].eq(1), "date"],
                frame.loc[frame["anomaly_flag"].eq(1), "entity_id"],
            )
        )
        for scenario, frame in scenarios.groupby("scenario")
    }
    out = scenarios.copy()
    keys = list(zip(out["date"], out["entity_id"]))
    out["is_strict_anomaly_candidate"] = [
        int(key in anomaly_sets.get("strict", set())) for key in keys
    ]
    out["is_balanced_anomaly_candidate"] = [
        int(key in anomaly_sets.get("balanced", set())) for key in keys
    ]
    out["is_sensitive_anomaly_candidate"] = [
        int(key in anomaly_sets.get("sensitive", set())) for key in keys
    ]
    out["scenario_anomaly_count"] = (
        out["is_strict_anomaly_candidate"]
        + out["is_balanced_anomaly_candidate"]
        + out["is_sensitive_anomaly_candidate"]
    )
    out["is_stable_anomaly_candidate"] = out["scenario_anomaly_count"].ge(2).astype(int)
    return out


def select_fact_anomaly_columns(scenarios: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "date",
        "entity_id",
        "meter_id",
        "meter_name",
        "entity_type",
        "building",
        "floor",
        "room_or_equipment",
        "scenario",
        "contamination",
        "model_name",
        "model_feature_set_version",
        "anomaly_score",
        "anomaly_flag",
        "anomaly_rank_within_scenario",
        "daily_consumption",
        "rolling_mean_7d",
        "rolling_std_7d",
        "deviation_from_rolling_mean_7d",
        "pct_deviation_from_rolling_mean_7d",
        "lag_1d_consumption",
        "lag_7d_consumption",
        "diff_from_lag_1d",
        "diff_from_lag_7d",
        "iqr_lower_bound",
        "iqr_upper_bound",
        "iqr_anomaly_flag",
        "zscore_daily_consumption",
        "zscore_abs_daily_consumption",
        "zscore_anomaly_flag",
        "entity_zscore_daily_consumption",
        "entity_zscore_anomaly_flag",
        "baseline_agreement_count",
        "baseline_agreement_label",
        "is_strict_anomaly_candidate",
        "is_balanced_anomaly_candidate",
        "is_sensitive_anomaly_candidate",
        "scenario_anomaly_count",
        "is_stable_anomaly_candidate",
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
        "temperature_band",
        "rainfall_band",
        "data_quality_flag",
        "is_model_eligible",
        "feature_complete_flag",
    ]
    return scenarios[columns].sort_values(["date", "entity_id", "scenario"])


def build_evaluation_summary(scenarios: pd.DataFrame) -> pd.DataFrame:
    strict_keys = set(
        zip(
            scenarios.loc[
                scenarios["scenario"].eq("strict") & scenarios["anomaly_flag"].eq(1),
                "date",
            ],
            scenarios.loc[
                scenarios["scenario"].eq("strict") & scenarios["anomaly_flag"].eq(1),
                "entity_id",
            ],
        )
    )
    balanced_keys = set(
        zip(
            scenarios.loc[
                scenarios["scenario"].eq("balanced") & scenarios["anomaly_flag"].eq(1),
                "date",
            ],
            scenarios.loc[
                scenarios["scenario"].eq("balanced") & scenarios["anomaly_flag"].eq(1),
                "entity_id",
            ],
        )
    )

    rows = []
    for scenario, frame in scenarios.groupby("scenario"):
        eligible_count = len(frame)
        anomaly_count = int(frame["anomaly_flag"].sum())
        expected = eligible_count * float(frame["contamination"].iloc[0])
        anomalies = frame[frame["anomaly_flag"].eq(1)]
        anomaly_keys = set(zip(anomalies["date"], anomalies["entity_id"]))
        rows.append(
            {
                "scenario": scenario,
                "contamination": float(frame["contamination"].iloc[0]),
                "eligible_row_count": eligible_count,
                "anomaly_count": anomaly_count,
                "anomaly_rate": anomaly_count / eligible_count if eligible_count else 0,
                "expected_anomaly_count": expected,
                "rate_delta_from_contamination": (
                    anomaly_count / eligible_count - float(frame["contamination"].iloc[0])
                    if eligible_count
                    else 0
                ),
                "iqr_agreement_count": int(
                    anomalies["iqr_anomaly_flag"].eq(1).sum()
                ),
                "iqr_agreement_rate": (
                    anomalies["iqr_anomaly_flag"].eq(1).mean() if anomaly_count else 0
                ),
                "zscore_agreement_count": int(
                    anomalies["zscore_anomaly_flag"].eq(1).sum()
                ),
                "zscore_agreement_rate": (
                    anomalies["zscore_anomaly_flag"].eq(1).mean() if anomaly_count else 0
                ),
                "both_baseline_agreement_count": int(
                    anomalies["baseline_agreement_count"].eq(2).sum()
                ),
                "stable_with_strict_count": len(anomaly_keys & strict_keys),
                "stable_with_balanced_count": len(anomaly_keys & balanced_keys),
                "no_ground_truth_note": NO_GROUND_TRUTH_NOTE,
            }
        )
    return pd.DataFrame(rows).sort_values("contamination")


def build_case_review(scenarios: pd.DataFrame) -> pd.DataFrame:
    balanced = scenarios[
        scenarios["scenario"].eq("balanced") & scenarios["anomaly_flag"].eq(1)
    ].copy()
    strict = scenarios[
        scenarios["scenario"].eq("strict") & scenarios["anomaly_flag"].eq(1)
    ].copy()
    selected_frames = [balanced.nsmallest(20, "anomaly_rank_within_scenario")]
    if len(strict) < 20:
        selected_frames.append(strict)
    selected = pd.concat(selected_frames, ignore_index=True)
    selected = selected.sort_values(
        ["anomaly_rank_within_scenario", "scenario", "date", "entity_id"]
    ).drop_duplicates(["date", "entity_id", "scenario"])
    selected["consumption_context_label"] = np.select(
        [
            selected["pct_deviation_from_rolling_mean_7d"].ge(0.20),
            selected["pct_deviation_from_rolling_mean_7d"].le(-0.20),
        ],
        ["above_recent_pattern", "below_recent_pattern"],
        default="near_recent_pattern",
    )
    selected["weather_context_label"] = np.select(
        [
            selected["is_hot_day_28c"].eq(1) & selected["is_rainy_day"].eq(1),
            selected["is_hot_day_28c"].eq(1),
            selected["is_rainy_day"].eq(1),
        ],
        ["hot_and_rainy", "hot_day", "rainy_day"],
        default="ordinary_weather_context",
    )
    columns = [
        "date",
        "entity_id",
        "meter_id",
        "building",
        "floor",
        "room_or_equipment",
        "scenario",
        "anomaly_rank_within_scenario",
        "anomaly_score",
        "daily_consumption",
        "rolling_mean_7d",
        "deviation_from_rolling_mean_7d",
        "pct_deviation_from_rolling_mean_7d",
        "mean_temperature_c",
        "rainfall_mm_model",
        "global_solar_radiation_mj_m2_model",
        "is_weekend",
        "is_hot_day_28c",
        "is_rainy_day",
        "iqr_anomaly_flag",
        "zscore_anomaly_flag",
        "baseline_agreement_count",
        "is_strict_anomaly_candidate",
        "is_balanced_anomaly_candidate",
        "is_sensitive_anomaly_candidate",
        "scenario_anomaly_count",
        "is_stable_anomaly_candidate",
        "data_quality_flag",
        "consumption_context_label",
        "weather_context_label",
    ]
    return selected[columns].reset_index(drop=True)


def _normalize(series: pd.Series) -> pd.Series:
    minimum = series.min()
    maximum = series.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series(0.0, index=series.index)
    return (series - minimum) / (maximum - minimum)


def build_entity_scorecard(fact: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    selected_fact = fact[fact["is_model_eligible"].eq(1)].copy()
    entity = (
        selected_fact.groupby(
            ["entity_id", "meter_id", "building", "floor", "room_or_equipment"],
            as_index=False,
        )
        .agg(
            total_consumption=("daily_consumption", "sum"),
            average_daily_consumption=("daily_consumption", "mean"),
            peak_daily_consumption=("daily_consumption", "max"),
            model_eligible_days=("date", "nunique"),
            data_quality_issue_count=(
                "data_quality_flag",
                lambda s: int((s != "valid").sum()),
            ),
        )
    )
    total = entity["total_consumption"].sum()
    entity["entity_contribution_pct"] = entity["total_consumption"] / total if total else 0

    anomaly_counts = (
        scenarios[scenarios["anomaly_flag"].eq(1)]
        .pivot_table(
            index="entity_id",
            columns="scenario",
            values="date",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )
    for scenario in ANOMALY_SCENARIOS:
        if scenario not in anomaly_counts.columns:
            anomaly_counts[scenario] = 0
    baseline_counts = (
        scenarios[scenarios["scenario"].eq("balanced")]
        .groupby("entity_id", as_index=False)
        .agg(
            iqr_anomaly_count=("iqr_anomaly_flag", "sum"),
            zscore_anomaly_count=("zscore_anomaly_flag", "sum"),
        )
    )
    entity = entity.merge(anomaly_counts, on="entity_id", how="left").merge(
        baseline_counts, on="entity_id", how="left"
    )
    for column in [
        "strict",
        "balanced",
        "sensitive",
        "iqr_anomaly_count",
        "zscore_anomaly_count",
    ]:
        entity[column] = entity[column].fillna(0).astype(int)
    entity = entity.rename(
        columns={
            "strict": "strict_anomaly_count",
            "balanced": "balanced_anomaly_count",
            "sensitive": "sensitive_anomaly_count",
        }
    )
    entity["balanced_anomaly_rate"] = (
        entity["balanced_anomaly_count"] / entity["model_eligible_days"]
    )
    quality_issue_rate = (
        entity["data_quality_issue_count"] / entity["model_eligible_days"]
    ).fillna(0)
    base_score = (
        0.50 * _normalize(entity["total_consumption"])
        + 0.30 * _normalize(entity["balanced_anomaly_rate"])
        + 0.20 * _normalize(entity["peak_daily_consumption"])
    )
    quality_penalty = np.where(quality_issue_rate.gt(0.10), 0.90, 1.0)
    entity["entity_priority_score"] = (base_score * quality_penalty * 100).round(2)
    entity["entity_priority_rank"] = (
        entity["entity_priority_score"].rank(method="first", ascending=False).astype(int)
    )
    return entity.sort_values("entity_priority_rank").reset_index(drop=True)


def update_data_dictionary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    dictionary_path = PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
    dictionary = pd.read_csv(dictionary_path)
    dictionary = dictionary[
        ~dictionary["table_name"].isin(tables.keys())
    ].copy()
    descriptions = {
        "scenario": "Anomaly model sensitivity scenario.",
        "contamination": "Isolation Forest contamination parameter for the scenario.",
        "model_name": "Model family used to produce the anomaly output.",
        "model_feature_set_version": "Version label for the selected feature set.",
        "anomaly_score": "Anomaly score oriented so higher values are more anomalous.",
        "anomaly_flag": "1 when the row is flagged as an anomaly by the scenario model.",
        "anomaly_rank_within_scenario": "Rank by anomaly_score within each scenario; 1 is most anomalous.",
        "iqr_anomaly_flag": "1 when daily consumption is outside the entity-level IQR bounds.",
        "zscore_daily_consumption": "Entity-relative Z-score for daily consumption.",
        "zscore_anomaly_flag": "1 when absolute entity-relative Z-score is at least 3.",
        "baseline_agreement_count": "Number of statistical baselines that also flag the row.",
        "baseline_agreement_label": "Text label summarizing baseline agreement.",
        "eligible_row_count": "Number of rows eligible for modelling in the scenario.",
        "anomaly_count": "Number of rows flagged as anomalies.",
        "anomaly_rate": "Anomaly count divided by eligible row count.",
        "no_ground_truth_note": "Evaluation note stating that supervised labels are unavailable.",
        "entity_priority_score": "Composite audit-priority score from consumption, anomaly rate, peak load, and quality.",
        "entity_priority_rank": "Rank of entity_priority_score; 1 is highest priority.",
    }
    rows = []
    for table_name, df in tables.items():
        for column in df.columns:
            rows.append(
                {
                    "table_name": table_name,
                    "column_name": column,
                    "dtype": str(df[column].dtype),
                    "description": descriptions.get(column, ""),
                    "source": "model output",
                    "treatment_notes": "Generated by scenario-based anomaly modelling pipeline.",
                }
            )
    if rows:
        dictionary = pd.concat([dictionary, pd.DataFrame(rows)], ignore_index=True)
    return dictionary.sort_values(["table_name", "column_name"]).reset_index(drop=True)


def build_anomaly_outputs() -> dict[str, object]:
    fact = read_csv_dates(PROCESSED_DIR / "fact_energy_weather_daily.csv")
    assert_unique_key(fact, ["date", "entity_id"], "fact_energy_weather_daily")
    fact = add_baselines(fact)
    model_df = eligible_model_frame(fact)
    scenarios = build_scenario_outputs(model_df)
    scenarios = add_scenario_stability(scenarios)
    fact_anomaly = select_fact_anomaly_columns(scenarios)
    evaluation = build_evaluation_summary(fact_anomaly)
    case_review = build_case_review(fact_anomaly)
    entity_scorecard = build_entity_scorecard(fact, fact_anomaly)
    data_dictionary = update_data_dictionary(
        {
            "fact_anomaly_scenarios": fact_anomaly,
            "model_evaluation_summary": evaluation,
            "anomaly_case_review": case_review,
            "entity_scorecard": entity_scorecard,
        }
    )

    assert_unique_key(
        fact_anomaly,
        ["date", "entity_id", "scenario"],
        "fact_anomaly_scenarios",
    )

    outputs = {
        "fact_anomaly_scenarios": write_csv(
            fact_anomaly, PROCESSED_DIR / "fact_anomaly_scenarios.csv"
        ),
        "model_evaluation_summary": write_csv(
            evaluation, PROCESSED_DIR / "model_evaluation_summary.csv"
        ),
        "anomaly_case_review": write_csv(
            case_review, PROCESSED_DIR / "anomaly_case_review.csv"
        ),
        "entity_scorecard": write_csv(
            entity_scorecard, PROCESSED_DIR / "entity_scorecard.csv"
        ),
        "data_dictionary": write_csv(
            data_dictionary, PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
        ),
        "eligible_rows": int(len(model_df)),
        "anomaly_rows": int(len(fact_anomaly)),
    }
    return outputs


def main() -> None:
    outputs = build_anomaly_outputs()
    print("Wrote anomaly modelling outputs:")
    for name, value in outputs.items():
        print(f"- {name}: {value}")


if __name__ == "__main__":
    main()
