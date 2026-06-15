from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATA_ACQUISITION_DIR = ROOT / "Data_Acquisition"
DATA_ROOT = DATA_ACQUISITION_DIR / "dataset"
HKUST_RAW_DIR = DATA_ROOT / "hkust_raw_data"
T1440_DIR = HKUST_RAW_DIR / "T1440"
TTL_PATH = HKUST_RAW_DIR / "HKUST_Meter_Metadata.ttl"
HKO_RAW_DIR = DATA_ROOT / "weather_raw_data"
PROCESSED_DIR = DATA_ROOT / "processed"
PROFILE_DIR = DATA_ROOT / "profile_hkust_hko"
OUTPUT_DIR = ROOT / "outputs"
FINAL_EDA_DIR = OUTPUT_DIR / "eda" / "final"

PROJECT_START = pd.Timestamp("2022-01-01")
PROJECT_END = pd.Timestamp("2024-05-27")

TARGET_BUILDING = "Cheng_Yu_Tung_Building"
SELECTED_METERS = [
    "D0849",
    "D0848",
    "D0854",
    "D0853",
    "D0862",
    "D0857",
    "D0851",
    "D0861",
    "D0852",
    "D0860",
    "D0850",
    "D0865",
]

ANOMALY_SCENARIOS = {
    "strict": {
        "contamination": 0.03,
        "label": "Strict",
        "description": "Flags only the most extreme anomaly candidates.",
        "is_default": 0,
    },
    "balanced": {
        "contamination": 0.05,
        "label": "Balanced",
        "description": "Default scenario for dashboard review and presentation.",
        "is_default": 1,
    },
    "sensitive": {
        "contamination": 0.10,
        "label": "Sensitive",
        "description": "Flags a wider candidate set for exploratory review.",
        "is_default": 0,
    },
}

HKO_VARIABLES = {
    "skg_mean_temperature": "mean_temperature_c",
    "skg_max_temperature": "max_temperature_c",
    "skg_min_temperature": "min_temperature_c",
    "skg_relative_humidity": "relative_humidity_pct",
    "ksc_total_rainfall": "rainfall_mm",
    "ksc_global_solar_radiation": "global_solar_radiation_mj_m2",
    "skg_mean_wind_speed": "mean_wind_speed_kmh",
}
