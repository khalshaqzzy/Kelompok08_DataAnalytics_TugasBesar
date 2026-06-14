from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import HKO_RAW_DIR, HKO_VARIABLES, PROCESSED_DIR, PROJECT_END, PROJECT_START
from io_utils import write_csv


def parse_hko_csv(path: Path, value_name: str) -> pd.DataFrame:
    raw = pd.read_csv(path, skiprows=2, header=None, encoding="utf-8-sig")
    raw = raw.iloc[:, :5].copy()
    raw.columns = ["year", "month", "day", value_name, f"{value_name}_completeness"]
    for column in ["year", "month", "day", value_name]:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")
    raw["date"] = pd.to_datetime(
        {"year": raw["year"], "month": raw["month"], "day": raw["day"]},
        errors="coerce",
    )
    return raw[["date", value_name, f"{value_name}_completeness"]]


def build_weather_daily() -> pd.DataFrame:
    frames = []
    for dataset_id, variable in HKO_VARIABLES.items():
        path = HKO_RAW_DIR / f"{dataset_id}.csv"
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
    weather = build_weather_daily()
    output_path = write_csv(weather, PROCESSED_DIR / "hko_weather_daily.csv")
    print(output_path)
    print(weather.shape)
    missing = weather.isna().sum().loc[lambda s: s.gt(0)]
    if len(missing):
        print("Missing weather values in project period:")
        print(missing.to_string())


if __name__ == "__main__":
    main()

