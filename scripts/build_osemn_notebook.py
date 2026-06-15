from __future__ import annotations

import argparse
import shutil
import textwrap
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

from config import ROOT


NOTEBOOK_PATH = ROOT / "notebooks" / "energy_analytics_osemn.ipynb"
ARCHIVE_DIR = ROOT / "cache" / "archive" / "notebooks"
OLD_NOTEBOOKS = [
    ROOT / "notebooks" / "eksplorasi_hkust_hko.ipynb",
    ROOT / "Data_Acquisition" / "01_explore_and_select_subset.ipynb",
]


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(textwrap.dedent(text).strip())


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip())


def archive_old_notebooks() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for source in OLD_NOTEBOOKS:
        if source.exists():
            destination = ARCHIVE_DIR / source.name
            if not destination.exists():
                shutil.copy2(source, destination)
            source.unlink()


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md(
            """
            # Analisis Fondasi Data Energi HKUST dan Cuaca HKO

            Notebook ini menyajikan analisis data untuk topik konsumsi energi kampus menggunakan smart meter HKUST dan data cuaca Hong Kong Observatory. Struktur notebook mengikuti alur OSEMN pada bagian yang sudah memiliki data final: Obtain, Scrub, Explore awal, dan Model.

            Fokus analisis saat ini adalah dataset harian T1440 yang bersih, terdokumentasi, memiliki konteks metadata, memiliki fitur turunan untuk analisis, dan menghasilkan deteksi anomali yang siap digunakan sebagai sumber Power BI. Interpretasi rekomendasi akhir tidak disajikan karena membutuhkan matriks insight dan rekomendasi berbasis bukti yang terpisah.
            """
        ),
        md(
            """
            ## Setup Analisis

            Seluruh tabel yang digunakan di notebook ini berasal dari folder processed proyek. Notebook berperan sebagai ringkasan analitis, sedangkan proses parsing, cleaning, dan pembentukan datamart dilakukan melalui script pipeline.
            """
        ),
        code(
            """
            from pathlib import Path
            import sys
            import pandas as pd

            ROOT = Path.cwd()
            if str(ROOT / "scripts") not in sys.path:
                sys.path.insert(0, str(ROOT / "scripts"))

            from config import PROCESSED_DIR, PROFILE_DIR, TARGET_BUILDING, SELECTED_METERS
            """
        ),
        md(
            """
            ## O - Obtain: Sumber Data dan Cakupan

            Dataset utama berasal dari smart meter HKUST dengan interval harian T1440. Dataset pendukung berasal dari Hong Kong Observatory dan digunakan untuk memberikan konteks cuaca harian.

            Cakupan utama analisis diarahkan pada meter aktif di `Cheng_Yu_Tung_Building` karena kumpulan meter ini memiliki coverage penuh, sinyal konsumsi aktif, dan metadata yang dapat dipetakan. Meter lain tetap dicatat dalam inventory agar kualitas data dan keputusan eksklusi dapat ditelusuri.
            """
        ),
        code(
            """
            inventory = pd.read_csv(PROFILE_DIR / "t1440_meter_inventory_with_decision.csv")
            weather = pd.read_csv(PROCESSED_DIR / "hko_weather_daily.csv", parse_dates=["date"])
            obtain_summary = pd.DataFrame(
                [
                    ["Jumlah meter T1440", int(inventory["meter_id"].nunique())],
                    ["Jumlah meter subset utama", len(SELECTED_METERS)],
                    ["Gedung fokus", TARGET_BUILDING],
                    ["Jumlah hari cuaca HKO", len(weather)],
                    ["Awal periode cuaca", weather["date"].min().date().isoformat()],
                    ["Akhir periode cuaca", weather["date"].max().date().isoformat()],
                ],
                columns=["Metrik", "Nilai"],
            )
            display(obtain_summary)
            display(inventory["quality_flag"].value_counts().rename_axis("quality_flag").reset_index(name="meter_count"))
            """
        ),
        md(
            """
            ## S - Scrub: Pembersihan dan Integrasi Data

            Tahap Scrub menormalisasi tanggal, mengubah pembacaan meter menjadi konsumsi harian melalui differencing, menandai kasus kualitas data, dan menggabungkan konsumsi energi dengan cuaca harian berdasarkan tanggal.

            Tabel akhir disusun sebagai star schema sederhana agar mudah digunakan di Power BI. Grain utama fact table adalah satu baris per tanggal dan meter terpilih.
            """
        ),
        code(
            """
            dim_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv", parse_dates=["date"])
            dim_entity = pd.read_csv(PROCESSED_DIR / "dim_entity.csv")
            dim_scenario = pd.read_csv(PROCESSED_DIR / "dim_scenario.csv")
            fact = pd.read_csv(PROCESSED_DIR / "fact_energy_weather_daily.csv", parse_dates=["date"])

            scrub_summary = pd.DataFrame(
                [
                    ["Baris dim_date", len(dim_date)],
                    ["Baris dim_entity", len(dim_entity)],
                    ["Baris dim_scenario", len(dim_scenario)],
                    ["Baris fact_energy_weather_daily", len(fact)],
                    ["Jumlah entity di fact", int(fact["entity_id"].nunique())],
                    ["Awal periode fact", fact["date"].min().date().isoformat()],
                    ["Akhir periode fact", fact["date"].max().date().isoformat()],
                    ["Baris model eligible", int(fact["is_model_eligible"].sum())],
                ],
                columns=["Metrik", "Nilai"],
            )
            display(scrub_summary)
            """
        ),
        md(
            """
            Validasi berikut memastikan bahwa tabel dimensi memiliki key unik dan fact table tidak memiliki duplikasi kombinasi tanggal dan entity.
            """
        ),
        code(
            """
            checks = {
                "dim_date_unique": not dim_date.duplicated(["date"]).any(),
                "dim_entity_unique": not dim_entity.duplicated(["entity_id"]).any(),
                "dim_scenario_unique": not dim_scenario.duplicated(["scenario"]).any(),
                "fact_date_entity_unique": not fact.duplicated(["date", "entity_id"]).any(),
                "selected_meters_all_present": set(SELECTED_METERS).issubset(set(dim_entity["meter_id"])),
            }
            display(checks)
            assert all(checks.values()), checks
            """
        ),
        md(
            """
            ## E - Explore: Ringkasan Awal Konsumsi dan Kualitas Data

            Eksplorasi awal dilakukan untuk membaca skala konsumsi, kontribusi meter, dan status kualitas data. Hasil pada bagian ini belum dimaksudkan sebagai interpretasi akhir, tetapi memberikan dasar yang kuat untuk visualisasi dan modelling berikutnya.
            """
        ),
        code(
            """
            consumption_summary = fact["daily_consumption"].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).to_frame("daily_consumption")
            display(consumption_summary)

            top_meter = (
                fact.groupby(["entity_id", "meter_name"], as_index=False)["daily_consumption"]
                .sum()
                .sort_values("daily_consumption", ascending=False)
            )
            top_meter["contribution_pct"] = top_meter["daily_consumption"] / top_meter["daily_consumption"].sum()
            top_meter["cumulative_contribution_pct"] = top_meter["contribution_pct"].cumsum()
            display(top_meter.head(12))
            """
        ),
        md(
            """
            Ringkasan kualitas data menunjukkan bahwa meter bermasalah tetap terdokumentasi dalam dimensi entity, sedangkan fact utama hanya berisi meter aktif terpilih. Nilai cuaca yang hilang dipertahankan pada kolom asli dan disediakan kolom model-safe untuk kebutuhan analisis lanjutan.
            """
        ),
        code(
            """
            data_quality = pd.read_csv(PROCESSED_DIR / "data_quality_summary.csv")
            display(data_quality)
            display(fact["data_quality_flag"].value_counts().rename_axis("data_quality_flag").reset_index(name="rows"))
            """
        ),
        md(
            """
            ## M - Model: Deteksi Anomali Konsumsi Energi

            Tujuan pemodelan adalah menandai observasi tanggal dan meter yang memiliki pola konsumsi tidak biasa dibandingkan riwayat konsumsi entity yang sama serta konteks waktu dan cuaca. Dataset tidak memiliki label resmi normal atau anomali, sehingga pendekatan yang digunakan adalah unsupervised anomaly detection.

            Model utama menggunakan Isolation Forest dengan tiga skenario sensitivitas. Baseline IQR dan Z-score digunakan sebagai pembanding agar hasil model tidak berdiri sendiri.
            """
        ),
        code(
            """
            fact_anomaly = pd.read_csv(PROCESSED_DIR / "fact_anomaly_scenarios.csv", parse_dates=["date"])
            model_eval = pd.read_csv(PROCESSED_DIR / "model_evaluation_summary.csv")
            case_review = pd.read_csv(PROCESSED_DIR / "anomaly_case_review.csv", parse_dates=["date"])
            entity_scorecard = pd.read_csv(PROCESSED_DIR / "entity_scorecard.csv")
            feature_summary = pd.read_csv(PROCESSED_DIR / "feature_engineering_summary.csv")

            model_outputs = pd.DataFrame(
                [
                    ["fact_anomaly_scenarios", len(fact_anomaly)],
                    ["model_evaluation_summary", len(model_eval)],
                    ["anomaly_case_review", len(case_review)],
                    ["entity_scorecard", len(entity_scorecard)],
                    ["feature_engineering_summary", len(feature_summary)],
                ],
                columns=["Tabel", "Jumlah baris"],
            )
            display(model_outputs)
            """
        ),
        md(
            """
            Fitur model menggabungkan konsumsi harian, deviasi rolling 7 hari, lag konsumsi, kalender, dan cuaca model-safe. Kolom kualitas data digunakan untuk filter dan interpretasi, bukan sebagai sinyal utama model.
            """
        ),
        code(
            """
            feature_groups = (
                feature_summary.groupby(["feature_group", "intended_use"], as_index=False)
                .agg(feature_count=("feature_name", "count"), missing_rate_max=("missing_rate", "max"))
                .sort_values(["feature_group", "intended_use"])
            )
            display(feature_groups)
            """
        ),
        md(
            """
            Ringkasan evaluasi berikut menunjukkan jumlah anomali pada masing-masing skenario. Karena tidak ada ground-truth label, evaluasi dibaca melalui kesesuaian jumlah flag dengan parameter contamination, agreement dengan baseline IQR/Z-score, stabilitas antar skenario, dan tinjauan kasus.
            """
        ),
        code(
            """
            display(
                model_eval[
                    [
                        "scenario",
                        "contamination",
                        "eligible_row_count",
                        "anomaly_count",
                        "anomaly_rate",
                        "iqr_agreement_count",
                        "zscore_agreement_count",
                        "both_baseline_agreement_count",
                    ]
                ]
            )
            """
        ),
        md(
            """
            Skenario balanced digunakan sebagai skenario default untuk peninjauan dashboard. Tabel berikut menampilkan contoh kandidat anomali dengan skor tertinggi, deviasi dari pola konsumsi terkini, serta konteks cuaca dan baseline.
            """
        ),
        code(
            """
            display(
                case_review[
                    [
                        "date",
                        "entity_id",
                        "building",
                        "scenario",
                        "anomaly_rank_within_scenario",
                        "daily_consumption",
                        "pct_deviation_from_rolling_mean_7d",
                        "mean_temperature_c",
                        "rainfall_mm_model",
                        "baseline_agreement_count",
                        "scenario_anomaly_count",
                        "consumption_context_label",
                        "weather_context_label",
                    ]
                ].head(10)
            )
            """
        ),
        md(
            """
            Entity scorecard menggabungkan total konsumsi, tingkat anomali pada skenario balanced, konsumsi puncak, dan kualitas data untuk membantu menentukan prioritas audit energi pada level meter terpilih.
            """
        ),
        code(
            """
            display(
                entity_scorecard[
                    [
                        "entity_priority_rank",
                        "entity_id",
                        "building",
                        "total_consumption",
                        "balanced_anomaly_count",
                        "balanced_anomaly_rate",
                        "strict_anomaly_count",
                        "sensitive_anomaly_count",
                        "entity_contribution_pct",
                        "entity_priority_score",
                    ]
                ].head(12)
            )
            """
        ),
        md(
            """
            Keterbatasan model perlu dibaca secara eksplisit. Model tidak membuktikan penyebab anomali, tidak memiliki label supervised untuk validasi akurasi, dan hanya berlaku pada meter T1440 terpilih. Hasil anomali sebaiknya digunakan sebagai daftar kandidat investigasi, bukan sebagai keputusan operasional tunggal.
            """
        ),
        md(
            """
            ## Kesiapan Data untuk Power BI

            Tabel berikut merupakan dataset yang dapat diimpor ke Power BI Desktop. Relasi utama menghubungkan fact table ke `dim_date`, `dim_entity`, dan `dim_scenario`.
            """
        ),
        code(
            """
            outputs = [
                "fact_energy_weather_daily.csv",
                "fact_anomaly_scenarios.csv",
                "dim_date.csv",
                "dim_entity.csv",
                "dim_scenario.csv",
                "feature_engineering_summary.csv",
                "model_evaluation_summary.csv",
                "anomaly_case_review.csv",
                "entity_scorecard.csv",
                "data_quality_summary.csv",
                "data_dictionary_energy_dashboard.csv",
            ]
            pd.DataFrame({
                "file": outputs,
                "exists": [(PROCESSED_DIR / name).exists() for name in outputs],
                "path": [str(PROCESSED_DIR / name) for name in outputs],
            })
            """
        ),
        md(
            """
            ## Catatan Keterbatasan

            Dataset T1440 harian hanya mencakup 26 meter, dan fact utama pada notebook ini menggunakan 12 meter aktif dari satu gedung. Karena itu, hasil analisis pada notebook ini sebaiknya dibaca sebagai fondasi analisis meter terpilih, bukan klaim representatif untuk seluruh kampus. Data cuaca digunakan sebagai konteks pendukung dan tidak boleh ditafsirkan sebagai penyebab tunggal perubahan konsumsi.
            """
        ),
    ]
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb["metadata"]["language_info"] = {"name": "python", "pygments_lexer": "ipython3"}
    return nb


def write_notebook(execute: bool = False) -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    archive_old_notebooks()
    nb = build_notebook()
    if execute:
        client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
        client.execute()
    nbf.write(nb, NOTEBOOK_PATH)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the active datamart foundation notebook for the current implementation scope."
    )
    parser.add_argument("--execute", action="store_true", help="Execute notebook before writing.")
    args = parser.parse_args()
    write_notebook(execute=args.execute)
    print(NOTEBOOK_PATH)


if __name__ == "__main__":
    main()
