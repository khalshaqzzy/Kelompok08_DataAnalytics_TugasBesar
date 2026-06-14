from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HKO_RAW = ROOT / "dataset" / "hko_open_data" / "raw"
PROCESSED_DIR = ROOT / "dataset" / "processed"
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
    for col in ["year", "month", "day", value_name]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw["date"] = pd.to_datetime(
        {"year": raw["year"], "month": raw["month"], "day": raw["day"]},
        errors="coerce",
    )
    return raw[["date", value_name, f"{value_name}_completeness"]]


def build_weather_daily() -> pd.DataFrame:
    frames = []
    for dataset_id, variable in HKO_VARIABLES.items():
        path = HKO_RAW / f"{dataset_id}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing HKO file: {path}")
        frames.append(parse_hko_csv(path, variable))

    weather = frames[0]
    for frame in frames[1:]:
        weather = weather.merge(frame, on="date", how="outer")

    weather = weather[
        (weather["date"] >= PROJECT_START) & (weather["date"] <= PROJECT_END)
    ].sort_values("date")
    weather["is_rainy_day"] = weather["rainfall_mm"].fillna(0).gt(0).astype(int)
    weather["is_hot_day_28c"] = weather["mean_temperature_c"].gt(28).astype(int)
    weather["cooling_degree_day_24c"] = (
        weather["mean_temperature_c"] - 24
    ).clip(lower=0)
    return weather


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    energy_path = PROCESSED_DIR / "master_energy_t1440_selected_daily.csv"
    fallback_energy_path = (
        ROOT
        / "Data_Acquisition"
        / "dataset"
        / "processed"
        / "master_energy_t1440_selected_daily.csv"
    )
    if not energy_path.exists() and fallback_energy_path.exists():
        energy_path = fallback_energy_path
    if not energy_path.exists():
        raise FileNotFoundError(
            "Run the energy subset workflow first; missing "
            f"{(PROCESSED_DIR / 'master_energy_t1440_selected_daily.csv').relative_to(ROOT)}"
        )

    energy = pd.read_csv(energy_path, parse_dates=["date"])
    weather = build_weather_daily()
    combined = energy.merge(weather, on="date", how="left")

    weather_path = PROCESSED_DIR / "hko_weather_daily.csv"
    combined_path = PROCESSED_DIR / "master_energy_weather_t1440_selected_daily.csv"
    weather.to_csv(weather_path, index=False)
    combined.to_csv(combined_path, index=False)

    print(weather_path)
    print(weather.shape)
    print(combined_path)
    print(combined.shape)
    print("Missing weather values in project period:")
    print(weather.isna().sum().loc[lambda s: s.gt(0)].to_string())


if __name__ == "__main__":
    main()
