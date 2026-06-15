from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import (
    ANOMALY_SCENARIOS,
    PROFILE_DIR,
    PROCESSED_DIR,
    PROJECT_END,
    PROJECT_START,
    SELECTED_METERS,
    TARGET_BUILDING,
)
from io_utils import assert_required_columns, assert_unique_key, read_csv_dates, write_csv


WEATHER_COLUMNS = [
    "mean_temperature_c",
    "mean_temperature_c_completeness",
    "max_temperature_c",
    "max_temperature_c_completeness",
    "min_temperature_c",
    "min_temperature_c_completeness",
    "relative_humidity_pct",
    "relative_humidity_pct_completeness",
    "rainfall_mm",
    "rainfall_mm_completeness",
    "global_solar_radiation_mj_m2",
    "global_solar_radiation_mj_m2_completeness",
    "mean_wind_speed_kmh",
    "mean_wind_speed_kmh_completeness",
    "is_rainy_day",
    "is_hot_day_28c",
    "cooling_degree_day_24c",
]


def build_dim_date() -> pd.DataFrame:
    dates = pd.date_range(PROJECT_START, PROJECT_END, freq="D")
    dim = pd.DataFrame({"date": dates})
    dim["year"] = dim["date"].dt.year
    dim["quarter"] = "Q" + dim["date"].dt.quarter.astype(str)
    dim["month"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.month_name()
    dim["day"] = dim["date"].dt.day
    dim["day_of_week"] = dim["date"].dt.day_name()
    dim["day_of_week_num"] = dim["date"].dt.dayofweek + 1
    dim["is_weekend"] = dim["date"].dt.dayofweek.ge(5).astype(int)
    dim["year_month"] = dim["date"].dt.strftime("%Y-%m")
    return dim


def build_dim_scenario() -> pd.DataFrame:
    rows = []
    for scenario, config in ANOMALY_SCENARIOS.items():
        rows.append(
            {
                "scenario": scenario,
                "contamination": config["contamination"],
                "scenario_label": config["label"],
                "scenario_description": config["description"],
                "is_default": config["is_default"],
            }
        )
    return pd.DataFrame(rows)


def build_dim_entity(inventory: pd.DataFrame) -> pd.DataFrame:
    dim = inventory.copy()
    dim["entity_id"] = dim["meter_id"]
    dim["usage_type"] = dim["entity_type"].fillna("meter")
    dim["meter_quality_flag"] = dim["quality_flag"]
    dim["selection_decision"] = dim["decision"]
    dim["is_selected_main_subset"] = dim["meter_id"].isin(SELECTED_METERS).astype(int)
    dim["is_model_eligible_entity"] = (
        dim["is_selected_main_subset"].eq(1)
        & dim["meter_quality_flag"].eq("active")
        & dim["mapping_status"].eq("mapped")
    ).astype(int)
    for column in [
        "meter_name",
        "entity_type",
        "building",
        "floor",
        "room_or_equipment",
        "usage_type",
        "mapping_status",
    ]:
        dim[column] = dim[column].fillna("Unknown").replace("", "Unknown")
    columns = [
        "entity_id",
        "meter_id",
        "meter_name",
        "entity_type",
        "building",
        "floor",
        "room_or_equipment",
        "usage_type",
        "mapping_status",
        "meter_quality_flag",
        "selection_decision",
        "is_selected_main_subset",
        "is_model_eligible_entity",
        "coverage_ratio",
        "total_consumption",
        "rank_total_consumption",
    ]
    return dim[columns].sort_values(["selection_decision", "rank_total_consumption", "meter_id"])


def add_weather_model_fields(fact: pd.DataFrame) -> pd.DataFrame:
    out = fact.copy()
    out["rainfall_mm_was_imputed"] = out["rainfall_mm"].isna().astype(int)
    out["global_solar_radiation_mj_m2_was_imputed"] = out[
        "global_solar_radiation_mj_m2"
    ].isna().astype(int)
    out["rainfall_mm_model"] = out["rainfall_mm"].fillna(0)

    monthly_solar = out.groupby("month")["global_solar_radiation_mj_m2"].transform(
        "median"
    )
    global_solar = out["global_solar_radiation_mj_m2"].median()
    out["global_solar_radiation_mj_m2_model"] = out[
        "global_solar_radiation_mj_m2"
    ].fillna(monthly_solar)
    out["global_solar_radiation_mj_m2_model"] = out[
        "global_solar_radiation_mj_m2_model"
    ].fillna(global_solar)
    return out


def build_data_quality_flag(row: pd.Series) -> str:
    flags = []
    if row.get("meter_quality_flag") != "active":
        flags.append("excluded_meter_quality")
    if int(row.get("negative_diff_flag", 0)) == 1:
        flags.append("negative_diff")
    if pd.isna(row.get("daily_consumption")):
        flags.append("missing_consumption")
    if int(row.get("rainfall_mm_was_imputed", 0)) or int(
        row.get("global_solar_radiation_mj_m2_was_imputed", 0)
    ):
        flags.append("weather_imputed")
    model_fields = [
        "daily_consumption",
        "mean_temperature_c",
        "relative_humidity_pct",
        "rainfall_mm_model",
        "global_solar_radiation_mj_m2_model",
        "mean_wind_speed_kmh",
        "cooling_degree_day_24c",
    ]
    if any(pd.isna(row.get(column)) for column in model_fields):
        flags.append("missing_model_feature")
    return ";".join(flags) if flags else "valid"


def build_fact_energy_weather(energy: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    energy = energy.copy()
    weather = weather.copy()
    energy["date"] = pd.to_datetime(energy["date"], errors="coerce").dt.normalize()
    weather["date"] = pd.to_datetime(weather["date"], errors="coerce").dt.normalize()
    energy = energy[energy["meter_id"].isin(SELECTED_METERS)].copy()
    energy = energy[energy["daily_consumption"].notna()].copy()
    fact = energy.merge(weather[["date", *WEATHER_COLUMNS]], on="date", how="left")

    fact["entity_id"] = fact["meter_id"]
    fact["meter_quality_flag"] = fact["quality_flag"]
    fact = add_weather_model_fields(fact)
    fact["data_quality_flag"] = fact.apply(build_data_quality_flag, axis=1)
    fact["is_model_eligible"] = (
        fact["decision"].eq("selected_main_subset")
        & fact["meter_quality_flag"].eq("active")
        & fact["daily_consumption"].notna()
        & fact["mean_temperature_c"].notna()
        & fact["relative_humidity_pct"].notna()
        & fact["rainfall_mm_model"].notna()
        & fact["global_solar_radiation_mj_m2_model"].notna()
        & fact["mean_wind_speed_kmh"].notna()
    ).astype(int)

    for column in ["floor", "room_or_equipment", "entity_type", "building", "meter_name"]:
        fact[column] = fact[column].fillna("Unknown").replace("", "Unknown")

    columns = [
        "date",
        "entity_id",
        "meter_id",
        "meter_name",
        "entity_type",
        "building",
        "floor",
        "room_or_equipment",
        "year",
        "quarter",
        "month",
        "month_name",
        "day_of_week",
        "day_of_week_num",
        "is_weekend",
        "meter_reading",
        "daily_consumption",
        *WEATHER_COLUMNS,
        "rainfall_mm_model",
        "rainfall_mm_was_imputed",
        "global_solar_radiation_mj_m2_model",
        "global_solar_radiation_mj_m2_was_imputed",
        "meter_quality_flag",
        "data_quality_flag",
        "is_model_eligible",
        "coverage_ratio",
        "mapping_status",
        "selection_decision",
        "rank_total_consumption",
    ]
    fact["selection_decision"] = fact["decision"]
    return fact[columns].sort_values(["date", "entity_id"])


def build_data_quality_summary(
    inventory: pd.DataFrame, weather: pd.DataFrame, fact: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for flag, count in inventory["quality_flag"].value_counts().sort_index().items():
        rows.append(
            {
                "summary_group": "meter_quality_flag",
                "metric": flag,
                "value": int(count),
                "notes": "Count of T1440 meters by quality flag.",
            }
        )
    for decision, count in inventory["decision"].value_counts().sort_index().items():
        rows.append(
            {
                "summary_group": "selection_decision",
                "metric": decision,
                "value": int(count),
                "notes": "Count of T1440 meters by selection decision.",
            }
        )
    rows.extend(
        [
            {
                "summary_group": "weather_missing_days",
                "metric": "rainfall_mm",
                "value": int(weather["rainfall_mm"].isna().sum()),
                "notes": "Missing HKO rainfall days in project period.",
            },
            {
                "summary_group": "weather_missing_days",
                "metric": "global_solar_radiation_mj_m2",
                "value": int(weather["global_solar_radiation_mj_m2"].isna().sum()),
                "notes": "Missing HKO solar radiation days in project period.",
            },
            {
                "summary_group": "fact_rows",
                "metric": "fact_energy_weather_daily",
                "value": int(len(fact)),
                "notes": "Rows in final Date x Entity fact table.",
            },
            {
                "summary_group": "model_eligible_rows",
                "metric": "fact_energy_weather_daily",
                "value": int(fact["is_model_eligible"].sum()),
                "notes": "Rows eligible for downstream anomaly modelling.",
            },
        ]
    )
    return pd.DataFrame(rows)


def build_data_dictionary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    descriptions = {
        "entity_id": "Power BI entity key. Meter ID for the current meter-level grain.",
        "date": "Calendar date.",
        "daily_consumption": "Daily consumption derived from meter reading differencing.",
        "meter_quality_flag": "Meter-level quality category from T1440 profiling.",
        "data_quality_flag": "Row-level quality flag for dashboard and modelling interpretation.",
        "is_model_eligible": "1 when row can be used by downstream anomaly model.",
        "rainfall_mm_model": "Model-safe rainfall feature with missing values imputed to 0.",
        "global_solar_radiation_mj_m2_model": "Model-safe solar radiation feature with monthly median imputation.",
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
                    "source": "generated" if table_name.startswith("dim_") else "processed pipeline",
                    "treatment_notes": "",
                }
            )
    return pd.DataFrame(rows)


def write_final_data_sources() -> Path:
    text = f"""# Final Data Sources

Canonical dataset root: `Data_Acquisition/dataset`

## HKUST Smart Meter

- Source: Dryad, https://doi.org/10.5061/dryad.k3j9kd5h6
- Local raw files: `Data_Acquisition/dataset/hkust_raw_data/T1440`
- Metadata: `Data_Acquisition/dataset/hkust_raw_data/HKUST_Meter_Metadata.ttl`
- Analytical scope: T1440 daily meter readings.
- Selected building: `{TARGET_BUILDING}`
- Selected meters: {", ".join(SELECTED_METERS)}

## Hong Kong Observatory Weather

- Source: Hong Kong Observatory Open Data.
- Local raw files: `Data_Acquisition/dataset/weather_raw_data`
- Processed file: `Data_Acquisition/dataset/processed/hko_weather_daily.csv`
- Role: weather context for energy interpretation.

## Final Power BI Tables

- `fact_energy_weather_daily.csv`
- `dim_date.csv`
- `dim_entity.csv`
- `dim_scenario.csv`
- `data_quality_summary.csv`
- `data_dictionary_energy_dashboard.csv`

## Limitations

- T1440 has only 26 daily meters.
- The main fact table uses 12 selected active meters from one building.
- Weather is contextual and should not be interpreted as sole causal evidence.
- Final anomaly modelling outputs are backlog after this datamart foundation.
"""
    path = PROFILE_DIR / "final_data_sources.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_datamart() -> dict[str, Path]:
    inventory = pd.read_csv(PROCESSED_DIR.parent / "t1440_meter_inventory_with_decision.csv")
    energy = read_csv_dates(PROCESSED_DIR / "master_energy_t1440_selected_daily.csv")
    weather = read_csv_dates(PROCESSED_DIR / "hko_weather_daily.csv")

    required_inventory = ["meter_id", "quality_flag", "decision", "mapping_status"]
    required_energy = ["date", "meter_id", "daily_consumption", "quality_flag", "decision"]
    required_weather = ["date", "rainfall_mm", "global_solar_radiation_mj_m2"]
    assert_required_columns(inventory, required_inventory, "inventory")
    assert_required_columns(energy, required_energy, "master_energy")
    assert_required_columns(weather, required_weather, "hko_weather_daily")

    dim_date = build_dim_date()
    dim_entity = build_dim_entity(inventory)
    dim_scenario = build_dim_scenario()
    fact = build_fact_energy_weather(energy, weather)
    data_quality = build_data_quality_summary(inventory, weather, fact)

    assert_unique_key(dim_date, ["date"], "dim_date")
    assert_unique_key(dim_entity, ["entity_id"], "dim_entity")
    assert_unique_key(dim_scenario, ["scenario"], "dim_scenario")
    assert_unique_key(fact, ["date", "entity_id"], "fact_energy_weather_daily")
    selected_buildings = set(
        dim_entity.loc[dim_entity["meter_id"].isin(SELECTED_METERS), "building"]
    )
    if selected_buildings != {TARGET_BUILDING}:
        raise ValueError(f"Selected meters do not all map to {TARGET_BUILDING}: {selected_buildings}")
    excluded_count = int(dim_entity["is_selected_main_subset"].eq(0).sum())
    if excluded_count == 0:
        raise ValueError("dim_entity must retain excluded/non-selected meters.")

    tables = {
        "dim_date": dim_date,
        "dim_entity": dim_entity,
        "dim_scenario": dim_scenario,
        "fact_energy_weather_daily": fact,
        "data_quality_summary": data_quality,
    }
    data_dictionary = build_data_dictionary(tables)

    outputs = {
        "dim_date": write_csv(dim_date, PROCESSED_DIR / "dim_date.csv"),
        "dim_entity": write_csv(dim_entity, PROCESSED_DIR / "dim_entity.csv"),
        "dim_scenario": write_csv(dim_scenario, PROCESSED_DIR / "dim_scenario.csv"),
        "fact_energy_weather_daily": write_csv(
            fact, PROCESSED_DIR / "fact_energy_weather_daily.csv"
        ),
        "data_quality_summary": write_csv(
            data_quality, PROCESSED_DIR / "data_quality_summary.csv"
        ),
        "data_dictionary": write_csv(
            data_dictionary, PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
        ),
        "final_data_sources": write_final_data_sources(),
    }
    return outputs


def main() -> None:
    outputs = build_datamart()
    print("Wrote Power BI datamart foundation:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()

