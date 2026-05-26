from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
HKUST_ALL = ROOT / "dataset" / "doi_10_5061_dryad_k3j9kd5h6__v20240801" / "All_Data" / "All Data"
HKO_RAW = ROOT / "dataset" / "hko_open_data" / "raw"
PROCESSED_DIR = ROOT / "dataset" / "processed"
EDA_DIR = ROOT / "outputs" / "eda"
PROFILE_DIR = ROOT / "dataset" / "profile_hkust_hko"

PROJECT_START = pd.Timestamp("2022-01-01")
PROJECT_END = pd.Timestamp("2024-05-27")

HKO_VARIABLES = {
    "skg_mean_temperature": "mean_temperature_c",
    "skg_max_temperature": "max_temperature_c",
    "skg_min_temperature": "min_temperature_c",
    "skg_relative_humidity": "relative_humidity_pct",
    "ksc_total_rainfall": "rainfall_mm",
    "ksc_global_solar_radiation": "global_solar_radiation_mj_m2",
    "skg_mean_wind_speed": "mean_wind_speed_kmh",
}


def parse_hko_csv(path: Path, value_name: str) -> pd.DataFrame:
    raw = pd.read_csv(path, skiprows=2, header=None, encoding="utf-8-sig")
    raw = raw.iloc[:, :5].copy()
    raw.columns = ["year", "month", "day", value_name, f"{value_name}_completeness"]
    for col in ["year", "month", "day"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw["date"] = pd.to_datetime(
        {"year": raw["year"], "month": raw["month"], "day": raw["day"]},
        errors="coerce",
    )
    raw[value_name] = pd.to_numeric(raw[value_name], errors="coerce")
    return raw[["date", value_name, f"{value_name}_completeness"]]


def load_hko_weather() -> pd.DataFrame:
    frames = []
    for dataset_id, variable in HKO_VARIABLES.items():
        path = HKO_RAW / f"{dataset_id}.csv"
        frames.append(parse_hko_csv(path, variable))

    weather = frames[0]
    for frame in frames[1:]:
        weather = weather.merge(frame, on="date", how="outer")

    weather = weather[(weather["date"] >= PROJECT_START) & (weather["date"] <= PROJECT_END)].sort_values("date")
    weather["is_rainy_day"] = weather["rainfall_mm"].fillna(0).gt(0).astype(int)
    weather["is_hot_day_28c"] = weather["mean_temperature_c"].gt(28).astype(int)
    weather["cooling_degree_day_24c"] = (weather["mean_temperature_c"] - 24).clip(lower=0)
    return weather


def load_hkust_t1440() -> pd.DataFrame:
    t1440_dir = HKUST_ALL / "Clean Dataset" / "Resappled data" / "T1440"
    frames = []
    for path in sorted(t1440_dir.glob("*.xlsx")):
        meter_id = path.stem.replace("GUI_NO.", "")
        df = pd.read_excel(path, engine="openpyxl")
        df = df.rename(columns={df.columns[0]: "date", df.columns[1]: "meter_reading"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
        df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce")
        df["meter_id"] = meter_id
        df = df.sort_values("date")
        df["daily_consumption"] = df.groupby("meter_id")["meter_reading"].diff()
        df.loc[df["daily_consumption"] < 0, "daily_consumption"] = pd.NA
        frames.append(df[["date", "meter_id", "meter_reading", "daily_consumption"]])
    return pd.concat(frames, ignore_index=True)


def load_hkust_t60_sample(sample_size: int = 8) -> pd.DataFrame:
    t60_dir = HKUST_ALL / "Clean Dataset" / "Resappled data" / "T60"
    frames = []
    for path in sorted(t60_dir.glob("*.xlsx"))[:sample_size]:
        meter_id = path.stem.replace("GUI_NO.", "")
        df = pd.read_excel(path, engine="openpyxl")
        df = df.rename(columns={df.columns[0]: "timestamp", df.columns[1]: "meter_reading"})
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce")
        df["meter_id"] = meter_id
        df = df.sort_values("timestamp")
        df["hourly_consumption"] = df.groupby("meter_id")["meter_reading"].diff()
        df.loc[df["hourly_consumption"] < 0, "hourly_consumption"] = pd.NA
        df["hour"] = df["timestamp"].dt.hour
        frames.append(df[["timestamp", "meter_id", "meter_reading", "hourly_consumption", "hour"]])
    return pd.concat(frames, ignore_index=True)


def build_daily_dataset(energy_long: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    energy = energy_long[(energy_long["date"] >= PROJECT_START) & (energy_long["date"] <= PROJECT_END)].copy()
    daily = (
        energy.groupby("date")
        .agg(
            meter_count=("meter_id", "nunique"),
            valid_daily_consumption_count=("daily_consumption", "count"),
            total_daily_consumption=("daily_consumption", lambda s: s.sum(min_count=1)),
            mean_daily_consumption=("daily_consumption", "mean"),
            median_daily_consumption=("daily_consumption", "median"),
            max_meter_daily_consumption=("daily_consumption", "max"),
            missing_daily_consumption_count=("daily_consumption", lambda s: int(s.isna().sum())),
        )
        .reset_index()
    )
    daily = daily.merge(weather, on="date", how="left")
    daily["weekday"] = daily["date"].dt.day_name()
    daily["is_weekend"] = daily["date"].dt.dayofweek.ge(5).astype(int)
    daily["month"] = daily["date"].dt.month
    daily["year"] = daily["date"].dt.year
    return daily


def add_anomaly_and_model(daily: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    out = daily.copy()
    z = (out["total_daily_consumption"] - out["total_daily_consumption"].mean()) / out["total_daily_consumption"].std(ddof=0)
    out["zscore_total_daily_consumption"] = z
    q1 = out["total_daily_consumption"].quantile(0.25)
    q3 = out["total_daily_consumption"].quantile(0.75)
    iqr = q3 - q1
    out["iqr_anomaly_flag"] = ((out["total_daily_consumption"] < q1 - 1.5 * iqr) | (out["total_daily_consumption"] > q3 + 1.5 * iqr)).astype(int)

    feature_cols = [
        "mean_temperature_c",
        "max_temperature_c",
        "min_temperature_c",
        "relative_humidity_pct",
        "rainfall_mm",
        "global_solar_radiation_mj_m2",
        "mean_wind_speed_kmh",
        "cooling_degree_day_24c",
        "is_rainy_day",
        "is_weekend",
        "month",
    ]
    model_df = out.dropna(subset=["total_daily_consumption", *feature_cols]).copy()

    metrics: dict[str, object] = {"model_rows": int(len(model_df)), "feature_cols": feature_cols}
    if len(model_df) >= 30:
        iso = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
        out.loc[model_df.index, "isolation_forest_anomaly"] = (iso.fit_predict(model_df[feature_cols]) == -1).astype(int)

        train, test = train_test_split(model_df, test_size=0.25, random_state=42)
        reg = LinearRegression()
        reg.fit(train[feature_cols], train["total_daily_consumption"])
        pred = reg.predict(test[feature_cols])
        metrics.update(
            {
                "linear_regression_mae": float(mean_absolute_error(test["total_daily_consumption"], pred)),
                "linear_regression_r2": float(r2_score(test["total_daily_consumption"], pred)),
            }
        )
    else:
        out["isolation_forest_anomaly"] = pd.NA
        metrics["note"] = "Insufficient rows for model evaluation"
    return out, metrics


def save_plots(daily: pd.DataFrame, hourly: pd.DataFrame) -> None:
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 5))
    sns.lineplot(data=daily, x="date", y="total_daily_consumption")
    plt.title("HKUST T1440 subset - total daily consumption")
    plt.xlabel("Date")
    plt.ylabel("Daily consumption from meter reading difference")
    plt.tight_layout()
    plt.savefig(EDA_DIR / "daily_consumption_trend.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=daily, x="mean_temperature_c", y="total_daily_consumption", hue="is_weekend", palette="viridis")
    plt.title("Daily consumption vs mean temperature")
    plt.xlabel("Mean temperature (C)")
    plt.ylabel("Total daily consumption")
    plt.tight_layout()
    plt.savefig(EDA_DIR / "consumption_vs_temperature.png", dpi=150)
    plt.close()

    corr_cols = [
        "total_daily_consumption",
        "mean_temperature_c",
        "relative_humidity_pct",
        "rainfall_mm",
        "global_solar_radiation_mj_m2",
        "mean_wind_speed_kmh",
        "cooling_degree_day_24c",
    ]
    corr = daily[corr_cols].corr(numeric_only=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0)
    plt.title("Correlation matrix - energy and weather")
    plt.tight_layout()
    plt.savefig(EDA_DIR / "energy_weather_correlation.png", dpi=150)
    plt.close()

    if not hourly.empty:
        hourly_plot = hourly.dropna(subset=["hourly_consumption"]).copy()
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=hourly_plot, x="hour", y="hourly_consumption", estimator="median", errorbar=None)
        plt.title("T60 sample - median hourly consumption profile")
        plt.xlabel("Hour of day")
        plt.ylabel("Median hourly consumption")
        plt.tight_layout()
        plt.savefig(EDA_DIR / "t60_hourly_profile_sample.png", dpi=150)
        plt.close()


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    weather = load_hko_weather()
    energy_long = load_hkust_t1440()
    hourly_sample = load_hkust_t60_sample()
    daily = build_daily_dataset(energy_long, weather)
    daily, model_metrics = add_anomaly_and_model(daily)

    daily.to_csv(PROCESSED_DIR / "energy_weather_daily_sample.csv", index=False)
    energy_long.to_csv(PROCESSED_DIR / "hkust_t1440_energy_long.csv", index=False)
    weather.to_csv(PROCESSED_DIR / "hko_weather_daily.csv", index=False)

    save_plots(daily, hourly_sample)

    summary = {
        "energy_long_rows": int(len(energy_long)),
        "energy_meters": int(energy_long["meter_id"].nunique()),
        "energy_date_min": str(energy_long["date"].min()),
        "energy_date_max": str(energy_long["date"].max()),
        "weather_rows": int(len(weather)),
        "weather_date_min": str(weather["date"].min()),
        "weather_date_max": str(weather["date"].max()),
        "integrated_rows": int(len(daily)),
        "integrated_date_min": str(daily["date"].min()),
        "integrated_date_max": str(daily["date"].max()),
        "integrated_missing_by_column": daily.isna().sum().astype(int).to_dict(),
        "top_correlations_with_total_daily_consumption": daily.corr(numeric_only=True)["total_daily_consumption"].sort_values(ascending=False).to_dict(),
        "anomaly_counts": {
            "iqr_anomaly_flag": int(daily["iqr_anomaly_flag"].sum()),
            "isolation_forest_anomaly": int(daily["isolation_forest_anomaly"].fillna(0).sum()),
        },
        "model_metrics": model_metrics,
        "outputs": {
            "daily_dataset": str((PROCESSED_DIR / "energy_weather_daily_sample.csv").relative_to(ROOT)),
            "energy_long": str((PROCESSED_DIR / "hkust_t1440_energy_long.csv").relative_to(ROOT)),
            "weather_daily": str((PROCESSED_DIR / "hko_weather_daily.csv").relative_to(ROOT)),
            "eda_dir": str(EDA_DIR.relative_to(ROOT)),
        },
    }
    (PROFILE_DIR / "exploration_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote processed datasets to {PROCESSED_DIR.relative_to(ROOT)}")
    print(f"Wrote EDA plots to {EDA_DIR.relative_to(ROOT)}")
    print(f"Integrated rows: {len(daily)}")


if __name__ == "__main__":
    main()
