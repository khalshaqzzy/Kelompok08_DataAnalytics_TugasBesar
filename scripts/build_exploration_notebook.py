from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
NOTEBOOK_PATH = NOTEBOOK_DIR / "eksplorasi_hkust_hko.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(dedent(text).strip())


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = [
        md(
            """
            # Eksplorasi Dataset HKUST Smart Meter + HKO Open Data

            Notebook ini mengikuti arah tugas besar Data Analitik berbasis OSEMN untuk topik **Energi dan Efisiensi Gedung/Kampus**. Urutan notebook:

            1. Load dan profil sumber data satu per satu.
            2. Eksplorasi biasa untuk HKUST dan HKO secara terpisah.
            3. Baru di akhir menggabungkan energi harian HKUST dengan data cuaca HKO.

            Catatan praktis: dataset HKUST lengkap berisi ribuan file Excel. Notebook ini menginventarisasi seluruh file dan membaca penuh subset analitik harian T1440, karena itulah interval yang paling sesuai dengan HKO daily climate data. Loader untuk T60 disediakan untuk eksplorasi pola jam pada sampel meter.
            """
        ),
        md(
            """
            ## Link Sumber Dataset

            | Peran | Dataset | Link |
            |---|---|---|
            | Utama | A 2.5-year campus-level smart meter database with equipment data for energy analytics | https://doi.org/10.5061/dryad.k3j9kd5h6 |
            | Artikel pendukung | Scientific Data paper | https://doi.org/10.1038/s41597-024-04106-1 |
            | Pendukung | Hong Kong Observatory Open Data | https://www.weather.gov.hk/en/abouthko/opendata_intro.htm |
            | HKO suhu mean Sai Kung | CLMTEMP SKG | https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&rformat=csv&station=SKG |
            | HKO suhu max Sai Kung | CLMMAXT SKG | https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMAXT&rformat=csv&station=SKG |
            | HKO suhu min Sai Kung | CLMMINT SKG | https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMMINT&rformat=csv&station=SKG |
            | HKO kelembapan Sai Kung | daily_SKG_RH_ALL.csv | https://data.weather.gov.hk/weatherAPI/cis/csvfile/SKG/ALL/daily_SKG_RH_ALL.csv |
            | HKO hujan Kau Sai Chau | daily_KSC_RF_ALL.csv | https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_RF_ALL.csv |
            | HKO radiasi matahari Kau Sai Chau | daily_KSC_GSR_ALL.csv | https://data.weather.gov.hk/weatherAPI/cis/csvfile/KSC/ALL/daily_KSC_GSR_ALL.csv |
            | HKO angin Sai Kung | daily_SKG_WSPD_ALL.csv | https://data.weather.gov.hk/cis/csvfile/SKG/ALL/daily_SKG_WSPD_ALL.csv |
            """
        ),
        code(
            """
            from pathlib import Path
            import json
            import warnings

            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns

            warnings.filterwarnings("ignore")
            sns.set_theme(style="whitegrid")

            ROOT = Path.cwd()
            HKUST_ROOT = ROOT / "dataset" / "doi_10_5061_dryad_k3j9kd5h6__v20240801"
            HKUST_ALL = HKUST_ROOT / "All_Data" / "All Data"
            HKO_RAW = ROOT / "dataset" / "hko_open_data" / "raw"
            PROCESSED = ROOT / "dataset" / "processed"
            PROFILE = ROOT / "dataset" / "profile_hkust_hko"

            PROJECT_START = pd.Timestamp("2022-01-01")
            PROJECT_END = pd.Timestamp("2024-05-27")

            assert HKUST_ROOT.exists(), HKUST_ROOT
            assert HKO_RAW.exists(), HKO_RAW
            print("Workspace:", ROOT)
            """
        ),
        md("## 1. Load dan Profil HKO per Dataset"),
        code(
            """
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

            hko_frames = {}
            hko_profile_rows = []
            for dataset_id, variable in HKO_VARIABLES.items():
                path = HKO_RAW / f"{dataset_id}.csv"
                df = parse_hko_csv(path, variable)
                project = df[(df["date"] >= PROJECT_START) & (df["date"] <= PROJECT_END)]
                hko_frames[dataset_id] = df
                hko_profile_rows.append({
                    "dataset_id": dataset_id,
                    "variable": variable,
                    "shape": df.shape,
                    "start": df["date"].min(),
                    "end": df["date"].max(),
                    "project_rows": len(project),
                    "project_missing": project[variable].isna().sum(),
                })

            hko_profile = pd.DataFrame(hko_profile_rows)
            hko_profile
            """
        ),
        code(
            """
            # Eksplorasi biasa HKO: statistik deskriptif setiap variabel pada periode proyek.
            hko_weather = None
            for dataset_id, variable in HKO_VARIABLES.items():
                df = hko_frames[dataset_id][["date", variable, f"{variable}_completeness"]]
                hko_weather = df if hko_weather is None else hko_weather.merge(df, on="date", how="outer")

            hko_weather = hko_weather[(hko_weather["date"] >= PROJECT_START) & (hko_weather["date"] <= PROJECT_END)].sort_values("date")
            hko_weather["is_rainy_day"] = hko_weather["rainfall_mm"].fillna(0).gt(0).astype(int)
            hko_weather["is_hot_day_28c"] = hko_weather["mean_temperature_c"].gt(28).astype(int)
            hko_weather["cooling_degree_day_24c"] = (hko_weather["mean_temperature_c"] - 24).clip(lower=0)

            value_cols = list(HKO_VARIABLES.values())
            display(hko_weather[value_cols].describe().T)
            display(hko_weather.head())
            """
        ),
        code(
            """
            fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
            sns.lineplot(data=hko_weather, x="date", y="mean_temperature_c", ax=axes[0])
            axes[0].set_title("HKO Sai Kung - Mean Temperature")
            sns.lineplot(data=hko_weather, x="date", y="relative_humidity_pct", ax=axes[1])
            axes[1].set_title("HKO Sai Kung - Relative Humidity")
            sns.lineplot(data=hko_weather, x="date", y="rainfall_mm", ax=axes[2])
            axes[2].set_title("HKO Kau Sai Chau - Rainfall")
            plt.tight_layout()
            plt.show()
            """
        ),
        md("## 2. Load dan Profil HKUST per Kelompok File"),
        code(
            """
            groups = {
                "raw_time_series": HKUST_ALL / "Raw Dataset" / "Time-series data",
                "clean_T15": HKUST_ALL / "Clean Dataset" / "Resappled data" / "T15",
                "clean_T30": HKUST_ALL / "Clean Dataset" / "Resappled data" / "T30",
                "clean_T60": HKUST_ALL / "Clean Dataset" / "Resappled data" / "T60",
                "clean_T1440": HKUST_ALL / "Clean Dataset" / "Resappled data" / "T1440",
            }

            inventory = []
            for group, path in groups.items():
                files = sorted(path.glob("*.xlsx"))
                inventory.append({
                    "group": group,
                    "path": str(path.relative_to(ROOT)),
                    "file_count": len(files),
                    "total_mb": round(sum(f.stat().st_size for f in files) / 1024 / 1024, 3),
                    "sample_file": files[0].name if files else None,
                })

            inventory_df = pd.DataFrame(inventory)
            inventory_df
            """
        ),
        code(
            """
            # Baca penuh semua file T1440 karena ringan dan cocok untuk gabungan harian.
            def load_hkust_group(files, time_col="time", value_col="number"):
                frames = []
                for path in files:
                    meter_id = path.stem.replace("GUI_NO.", "")
                    df = pd.read_excel(path, engine="openpyxl")
                    df = df.rename(columns={df.columns[0]: time_col, df.columns[1]: value_col})
                    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
                    df["meter_id"] = meter_id
                    frames.append(df[[time_col, "meter_id", value_col]])
                return pd.concat(frames, ignore_index=True)

            t1440_files = sorted(groups["clean_T1440"].glob("*.xlsx"))
            hkust_t1440 = load_hkust_group(t1440_files, time_col="date", value_col="meter_reading")
            hkust_t1440["date"] = hkust_t1440["date"].dt.normalize()
            hkust_t1440 = hkust_t1440.sort_values(["meter_id", "date"])
            hkust_t1440["daily_consumption"] = hkust_t1440.groupby("meter_id")["meter_reading"].diff()
            hkust_t1440.loc[hkust_t1440["daily_consumption"] < 0, "daily_consumption"] = pd.NA

            print("HKUST T1440 shape:", hkust_t1440.shape)
            display(hkust_t1440.head())
            display(hkust_t1440.groupby("meter_id").agg(
                rows=("date", "size"),
                start=("date", "min"),
                end=("date", "max"),
                missing_reading=("meter_reading", lambda s: s.isna().sum()),
                missing_consumption=("daily_consumption", lambda s: s.isna().sum()),
                min_reading=("meter_reading", "min"),
                max_reading=("meter_reading", "max"),
            ).reset_index().head(10))
            """
        ),
        code(
            """
            # Load sampel T60 untuk eksplorasi jam. Seluruh file T60 tersedia di inventory,
            # tetapi pembacaan penuh semua interval halus sengaja dibuat opsional agar notebook tetap responsif.
            t60_files = sorted(groups["clean_T60"].glob("*.xlsx"))
            t60_sample = load_hkust_group(t60_files[:8], time_col="timestamp", value_col="meter_reading")
            t60_sample = t60_sample.sort_values(["meter_id", "timestamp"])
            t60_sample["hourly_consumption"] = t60_sample.groupby("meter_id")["meter_reading"].diff()
            t60_sample.loc[t60_sample["hourly_consumption"] < 0, "hourly_consumption"] = pd.NA
            t60_sample["hour"] = t60_sample["timestamp"].dt.hour

            print("T60 sample shape:", t60_sample.shape)
            display(t60_sample.head())
            display(t60_sample.groupby("meter_id")["hourly_consumption"].describe())
            """
        ),
        code(
            """
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            daily_by_meter = hkust_t1440.groupby(["date", "meter_id"], as_index=False)["daily_consumption"].sum()
            sns.lineplot(data=daily_by_meter, x="date", y="daily_consumption", hue="meter_id", legend=False, ax=axes[0])
            axes[0].set_title("HKUST T1440 - Daily Consumption by Meter")

            sns.lineplot(data=t60_sample.dropna(subset=["hourly_consumption"]), x="hour", y="hourly_consumption", estimator="median", errorbar=None, ax=axes[1])
            axes[1].set_title("HKUST T60 Sample - Median Hourly Profile")
            plt.tight_layout()
            plt.show()
            """
        ),
        md("## 3. Integrasi Akhir: HKUST T1440 + HKO Daily Weather"),
        code(
            """
            energy_daily = (
                hkust_t1440[(hkust_t1440["date"] >= PROJECT_START) & (hkust_t1440["date"] <= PROJECT_END)]
                .groupby("date")
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

            combined = energy_daily.merge(hko_weather, on="date", how="left")
            combined["weekday"] = combined["date"].dt.day_name()
            combined["is_weekend"] = combined["date"].dt.dayofweek.ge(5).astype(int)
            combined["month"] = combined["date"].dt.month
            combined["year"] = combined["date"].dt.year

            combined.shape, combined.head()
            """
        ),
        code(
            """
            display(combined.isna().sum().sort_values(ascending=False).head(12))
            display(combined[[
                "total_daily_consumption",
                "mean_temperature_c",
                "relative_humidity_pct",
                "rainfall_mm",
                "global_solar_radiation_mj_m2",
                "mean_wind_speed_kmh",
            ]].describe().T)
            """
        ),
        code(
            """
            corr_cols = [
                "total_daily_consumption",
                "mean_temperature_c",
                "relative_humidity_pct",
                "rainfall_mm",
                "global_solar_radiation_mj_m2",
                "mean_wind_speed_kmh",
                "cooling_degree_day_24c",
                "is_weekend",
            ]
            corr = combined[corr_cols].corr(numeric_only=True)

            plt.figure(figsize=(8, 6))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0)
            plt.title("Correlation - HKUST Energy + HKO Weather")
            plt.tight_layout()
            plt.show()
            """
        ),
        code(
            """
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            sns.lineplot(data=combined, x="date", y="total_daily_consumption", ax=axes[0])
            axes[0].set_title("Integrated Dataset - Total Daily Consumption")
            sns.scatterplot(data=combined, x="mean_temperature_c", y="total_daily_consumption", hue="is_weekend", ax=axes[1])
            axes[1].set_title("Consumption vs Mean Temperature")
            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ## 4. Catatan Interpretasi Awal

            - Dataset HKO lengkap untuk periode proyek, kecuali rainfall dan solar radiation yang memiliki sedikit missing value.
            - HKUST T1440 cocok sebagai baseline harian, tetapi hanya mencakup 26 meter sehingga belum mewakili seluruh kampus.
            - Hubungan cuaca terhadap total konsumsi agregat cenderung lemah pada eksplorasi awal. Untuk tugas besar, analisis sebaiknya turun ke level meter/gedung/zona yang lebih spesifik.
            - Integrasi akhir sudah memenuhi arah OSEMN: raw data terpisah, cleaning eksplisit, fitur waktu/cuaca tersedia, dan dataset siap untuk EDA, anomaly detection, atau forecasting sederhana.
            """
        ),
    ]
    nb["cells"] = cells
    return nb


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    nbf.write(nb, NOTEBOOK_PATH)

    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute()
    nbf.write(nb, NOTEBOOK_PATH)
    print(NOTEBOOK_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
