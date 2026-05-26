from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "dataset" / "hko_open_data" / "raw"
PROFILE_DIR = ROOT / "dataset" / "hko_open_data" / "profile"

DATASETS = [
    {
        "id": "skg_mean_temperature",
        "title": "Daily Mean Temperature All Year - Sai Kung",
        "station": "Sai Kung",
        "variable": "mean_temperature_c",
        "unit": "degC",
        "url": "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&rformat=csv&station=SKG",
    },
    {
        "id": "skg_max_temperature",
        "title": "Daily Maximum Temperature All Year - Sai Kung",
        "station": "Sai Kung",
        "variable": "max_temperature_c",
        "unit": "degC",
        "url": "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMAXT&rformat=csv&station=SKG",
    },
    {
        "id": "skg_min_temperature",
        "title": "Daily Minimum Temperature All Year - Sai Kung",
        "station": "Sai Kung",
        "variable": "min_temperature_c",
        "unit": "degC",
        "url": "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMINT&rformat=csv&station=SKG",
    },
    {
        "id": "skg_relative_humidity",
        "title": "Daily Mean Relative Humidity All Year - Sai Kung",
        "station": "Sai Kung",
        "variable": "relative_humidity_pct",
        "unit": "percent",
        "url": "https://data.weather.gov.hk/weatherAPI/cis/csvfile/SKG/ALL/daily_SKG_RH_ALL.csv",
    },
    {
        "id": "ksc_total_rainfall",
        "title": "Daily Total Rainfall All Year - Kau Sai Chau",
        "station": "Kau Sai Chau",
        "variable": "rainfall_mm",
        "unit": "mm",
        "url": "https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_RF_ALL.csv",
    },
    {
        "id": "ksc_global_solar_radiation",
        "title": "Daily Global Solar Radiation All Year - Kau Sai Chau",
        "station": "Kau Sai Chau",
        "variable": "global_solar_radiation_mj_m2",
        "unit": "MJ/m2",
        "url": "https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_GSR_ALL.csv",
    },
    {
        "id": "skg_mean_wind_speed",
        "title": "Daily Mean Wind Speed All Year - Sai Kung",
        "station": "Sai Kung",
        "variable": "mean_wind_speed_kmh",
        "unit": "km/h",
        "url": "https://data.weather.gov.hk/cis/csvfile/SKG/ALL/daily_SKG_WSPD_ALL.csv",
    },
]


def download(dataset: dict[str, str]) -> dict[str, object]:
    response = requests.get(dataset["url"], timeout=60)
    response.raise_for_status()

    path = RAW_DIR / f"{dataset['id']}.csv"
    path.write_bytes(response.content)

    preview = response.content.decode("utf-8-sig", errors="replace").splitlines()[:5]
    return {
        **dataset,
        "raw_path": str(path.relative_to(ROOT)),
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "bytes": len(response.content),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "preview": preview,
    }


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = [download(dataset) for dataset in DATASETS]

    json_path = PROFILE_DIR / "hko_download_manifest.json"
    csv_path = PROFILE_DIR / "hko_download_manifest.csv"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id",
            "title",
            "station",
            "variable",
            "unit",
            "url",
            "raw_path",
            "status_code",
            "content_type",
            "bytes",
            "downloaded_at_utc",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in manifest:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    print(f"Downloaded {len(manifest)} HKO datasets")
    print(json_path.relative_to(ROOT))
    print(csv_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
