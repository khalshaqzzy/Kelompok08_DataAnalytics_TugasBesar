from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import FINAL_EDA_DIR, PROCESSED_DIR
from io_utils import assert_required_columns, assert_unique_key, ensure_dir, read_csv_dates, write_csv


PLOT_DPI = 160


FIGURES = {
    "daily_consumption_trend": "daily_consumption_trend.png",
    "monthly_consumption_trend": "monthly_consumption_trend.png",
    "weekday_weekend_consumption": "weekday_weekend_consumption.png",
    "top_meter_contribution_pareto": "top_meter_contribution_pareto.png",
    "weather_consumption_context": "weather_consumption_context.png",
    "data_quality_flags": "data_quality_flags.png",
    "anomaly_case_review": "anomaly_case_review.png",
}


def _save_figure(path: Path) -> None:
    ensure_dir(path.parent)
    plt.tight_layout()
    plt.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close()


def load_inputs() -> dict[str, pd.DataFrame]:
    fact = read_csv_dates(PROCESSED_DIR / "fact_energy_weather_daily.csv")
    anomaly = read_csv_dates(PROCESSED_DIR / "fact_anomaly_scenarios.csv")
    entity = pd.read_csv(PROCESSED_DIR / "entity_scorecard.csv")
    cases = read_csv_dates(PROCESSED_DIR / "anomaly_case_review.csv")
    model_eval = pd.read_csv(PROCESSED_DIR / "model_evaluation_summary.csv")
    data_quality = pd.read_csv(PROCESSED_DIR / "data_quality_summary.csv")
    dim_entity = pd.read_csv(PROCESSED_DIR / "dim_entity.csv")

    assert_required_columns(
        fact,
        [
            "date",
            "entity_id",
            "daily_consumption",
            "is_weekend",
            "mean_temperature_c",
            "rainfall_mm_model",
            "is_hot_day_28c",
            "is_rainy_day",
            "data_quality_flag",
        ],
        "fact_energy_weather_daily",
    )
    assert_required_columns(
        anomaly,
        ["date", "entity_id", "scenario", "anomaly_flag", "anomaly_score"],
        "fact_anomaly_scenarios",
    )
    assert_required_columns(
        entity,
        [
            "entity_id",
            "total_consumption",
            "entity_contribution_pct",
            "balanced_anomaly_count",
            "balanced_anomaly_rate",
            "entity_priority_rank",
        ],
        "entity_scorecard",
    )
    assert_required_columns(
        cases,
        [
            "date",
            "entity_id",
            "daily_consumption",
            "pct_deviation_from_rolling_mean_7d",
            "scenario_anomaly_count",
            "weather_context_label",
        ],
        "anomaly_case_review",
    )
    assert_unique_key(fact, ["date", "entity_id"], "fact_energy_weather_daily")
    assert_unique_key(anomaly, ["date", "entity_id", "scenario"], "fact_anomaly_scenarios")

    return {
        "fact": fact,
        "anomaly": anomaly,
        "entity": entity,
        "cases": cases,
        "model_eval": model_eval,
        "data_quality": data_quality,
        "dim_entity": dim_entity,
    }


def build_daily_summary(fact: pd.DataFrame, anomaly: pd.DataFrame) -> pd.DataFrame:
    daily = (
        fact.groupby("date", as_index=False)
        .agg(
            total_consumption=("daily_consumption", "sum"),
            average_meter_consumption=("daily_consumption", "mean"),
            mean_temperature_c=("mean_temperature_c", "mean"),
            rainfall_mm_model=("rainfall_mm_model", "mean"),
            is_hot_day_28c=("is_hot_day_28c", "max"),
            is_rainy_day=("is_rainy_day", "max"),
            is_weekend=("is_weekend", "max"),
        )
        .sort_values("date")
    )
    balanced = anomaly[anomaly["scenario"].eq("balanced")]
    balanced_daily = (
        balanced.groupby("date", as_index=False)
        .agg(
            balanced_anomaly_count=("anomaly_flag", "sum"),
            max_anomaly_score=("anomaly_score", "max"),
        )
    )
    daily = daily.merge(balanced_daily, on="date", how="left")
    daily["balanced_anomaly_count"] = daily["balanced_anomaly_count"].fillna(0).astype(int)
    daily["has_balanced_anomaly"] = daily["balanced_anomaly_count"].gt(0).astype(int)
    return daily


def plot_daily_consumption(daily: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["daily_consumption_trend"]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily["date"], daily["total_consumption"], color="#1f4e79", linewidth=1.3)
    anomaly_days = daily[daily["has_balanced_anomaly"].eq(1)]
    ax.scatter(
        anomaly_days["date"],
        anomaly_days["total_consumption"],
        s=22,
        color="#c43b3b",
        label="Balanced anomaly date",
        zorder=3,
    )
    ax.set_title("Daily Selected-Meter Consumption With Balanced Anomaly Dates")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total daily consumption")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")
    _save_figure(path)
    return path


def plot_monthly_consumption(fact: pd.DataFrame) -> tuple[Path, pd.DataFrame]:
    path = FINAL_EDA_DIR / FIGURES["monthly_consumption_trend"]
    monthly = fact.copy()
    monthly["year_month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly = (
        monthly.groupby("year_month", as_index=False)
        .agg(
            total_consumption=("daily_consumption", "sum"),
            average_daily_consumption=("daily_consumption", "mean"),
        )
        .sort_values("year_month")
    )
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.bar(monthly["year_month"], monthly["total_consumption"], color="#4c78a8")
    ax1.set_ylabel("Monthly total consumption")
    ax1.tick_params(axis="x", rotation=60)
    ax2 = ax1.twinx()
    ax2.plot(
        monthly["year_month"],
        monthly["average_daily_consumption"],
        color="#f58518",
        marker="o",
        linewidth=1.5,
    )
    ax2.set_ylabel("Average meter-day consumption")
    ax1.set_title("Monthly Consumption Trend")
    ax1.grid(True, axis="y", alpha=0.25)
    _save_figure(path)
    return path, monthly


def plot_weekday_weekend(daily: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["weekday_weekend_consumption"]
    plot_df = daily.copy()
    plot_df["day_type"] = np.where(plot_df["is_weekend"].eq(1), "Weekend", "Weekday")
    groups = [plot_df.loc[plot_df["day_type"].eq(label), "total_consumption"] for label in ["Weekday", "Weekend"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    box = ax.boxplot(
        groups,
        tick_labels=["Weekday", "Weekend"],
        patch_artist=True,
        showmeans=True,
    )
    for patch, color in zip(box["boxes"], ["#4c78a8", "#72b7b2"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
    ax.set_title("Weekday and Weekend Consumption Distribution")
    ax.set_ylabel("Total daily consumption")
    ax.grid(True, axis="y", alpha=0.25)
    _save_figure(path)
    return path


def plot_pareto(entity: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["top_meter_contribution_pareto"]
    pareto = entity.sort_values("total_consumption", ascending=False).copy()
    pareto["cumulative_contribution_pct"] = pareto["entity_contribution_pct"].cumsum()
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.bar(pareto["entity_id"], pareto["total_consumption"], color="#4c78a8")
    ax1.set_ylabel("Total consumption")
    ax1.tick_params(axis="x", rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(
        pareto["entity_id"],
        pareto["cumulative_contribution_pct"] * 100,
        color="#e45756",
        marker="o",
        linewidth=1.7,
    )
    ax2.set_ylabel("Cumulative contribution (%)")
    ax2.set_ylim(0, 105)
    ax1.set_title("Selected-Meter Contribution and Pareto Pattern")
    ax1.grid(True, axis="y", alpha=0.25)
    _save_figure(path)
    return path


def plot_weather_context(daily: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["weather_consumption_context"]
    colors = np.where(daily["has_balanced_anomaly"].eq(1), "#c43b3b", "#4c78a8")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(
        daily["mean_temperature_c"],
        daily["total_consumption"],
        c=colors,
        alpha=0.75,
        edgecolors="white",
        linewidths=0.3,
    )
    axes[0].set_title("Consumption vs Mean Temperature")
    axes[0].set_xlabel("Mean temperature (C)")
    axes[0].set_ylabel("Total daily consumption")
    axes[0].grid(True, alpha=0.25)
    axes[1].scatter(
        daily["rainfall_mm_model"],
        daily["total_consumption"],
        c=colors,
        alpha=0.75,
        edgecolors="white",
        linewidths=0.3,
    )
    axes[1].set_title("Consumption vs Rainfall")
    axes[1].set_xlabel("Rainfall model field (mm)")
    axes[1].set_ylabel("Total daily consumption")
    axes[1].grid(True, alpha=0.25)
    fig.suptitle("Weather Context for Daily Consumption")
    _save_figure(path)
    return path


def plot_data_quality(fact: pd.DataFrame, dim_entity: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["data_quality_flags"]
    meter_counts = dim_entity["meter_quality_flag"].value_counts().sort_index()
    row_counts = fact["data_quality_flag"].value_counts().sort_index()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(meter_counts.index.astype(str), meter_counts.values, color="#4c78a8")
    axes[0].set_title("Meter Quality Flags")
    axes[0].set_ylabel("Meter count")
    axes[0].tick_params(axis="x", rotation=35)
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[1].bar(row_counts.index.astype(str), row_counts.values, color="#72b7b2")
    axes[1].set_title("Fact Row Data Quality Flags")
    axes[1].set_ylabel("Row count")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].grid(True, axis="y", alpha=0.25)
    fig.suptitle("Data Quality Visibility")
    _save_figure(path)
    return path


def plot_anomaly_case_review(cases: pd.DataFrame) -> Path:
    path = FINAL_EDA_DIR / FIGURES["anomaly_case_review"]
    top = cases.nsmallest(12, "anomaly_rank_within_scenario").copy()
    top["label"] = top["date"].dt.strftime("%Y-%m-%d") + " " + top["entity_id"]
    colors = np.where(top["scenario_anomaly_count"].ge(3), "#c43b3b", "#f58518")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(top["label"], top["pct_deviation_from_rolling_mean_7d"] * 100, color=colors)
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_title("Top Balanced Anomaly Cases by Recent-Pattern Deviation")
    ax.set_xlabel("Deviation from rolling mean (%)")
    ax.set_ylabel("Date and entity")
    ax.grid(True, axis="x", alpha=0.25)
    _save_figure(path)
    return path


def build_eda_summary(
    daily: pd.DataFrame,
    monthly: pd.DataFrame,
    fact: pd.DataFrame,
    anomaly: pd.DataFrame,
    entity: pd.DataFrame,
    dim_entity: pd.DataFrame,
) -> pd.DataFrame:
    weekday = daily.loc[daily["is_weekend"].eq(0), "total_consumption"].mean()
    weekend = daily.loc[daily["is_weekend"].eq(1), "total_consumption"].mean()
    peak_month = monthly.loc[monthly["total_consumption"].idxmax()]
    low_month = monthly.loc[monthly["total_consumption"].idxmin()]
    pareto = entity.sort_values("total_consumption", ascending=False).copy()
    top_entity = pareto.iloc[0]
    top5_share = float(pareto.head(5)["entity_contribution_pct"].sum())
    balanced = anomaly[anomaly["scenario"].eq("balanced")]
    balanced_anomaly_count = int(balanced["anomaly_flag"].sum())
    balanced_entity = (
        balanced[balanced["anomaly_flag"].eq(1)]["entity_id"].value_counts().idxmax()
    )
    temp_corr = float(daily["total_consumption"].corr(daily["mean_temperature_c"]))
    rainfall_corr = float(daily["total_consumption"].corr(daily["rainfall_mm_model"]))
    active_meters = int(dim_entity["meter_quality_flag"].eq("active").sum())
    excluded_meters = int(len(dim_entity) - active_meters)
    quality_issue_rows = int(fact["data_quality_flag"].ne("valid").sum())

    rows = [
        {
            "analysis_area": "daily_trend",
            "metric_name": "average_daily_total_consumption",
            "metric_value": round(float(daily["total_consumption"].mean()), 3),
            "comparison_value": f"min={daily['total_consumption'].min():.3f}; max={daily['total_consumption'].max():.3f}",
            "interpretation_note": "Daily selected-meter consumption is relatively stable but still contains visible high and low periods for review.",
            "powerbi_page": "Consumption Trend",
            "evidence_table": "fact_energy_weather_daily",
            "evidence_visual": FIGURES["daily_consumption_trend"],
            "limitation_note": "Daily totals represent selected T1440 meters, not full-campus consumption.",
        },
        {
            "analysis_area": "monthly_trend",
            "metric_name": "peak_month_total_consumption",
            "metric_value": round(float(peak_month["total_consumption"]), 3),
            "comparison_value": f"peak={peak_month['year_month']}; low={low_month['year_month']}",
            "interpretation_note": "Monthly totals show seasonal and calendar-period variation that should be visible in dashboard filtering.",
            "powerbi_page": "Consumption Trend",
            "evidence_table": "fact_energy_weather_daily",
            "evidence_visual": FIGURES["monthly_consumption_trend"],
            "limitation_note": "Partial months at dataset boundaries should not be overcompared with full months.",
        },
        {
            "analysis_area": "weekday_weekend",
            "metric_name": "weekday_minus_weekend_average_daily_total",
            "metric_value": round(float(weekday - weekend), 3),
            "comparison_value": f"weekday={weekday:.3f}; weekend={weekend:.3f}",
            "interpretation_note": "Weekday daily totals are higher on average than weekend totals, consistent with operational activity differences.",
            "powerbi_page": "Consumption Trend",
            "evidence_table": "fact_energy_weather_daily",
            "evidence_visual": FIGURES["weekday_weekend_consumption"],
            "limitation_note": "Weekend differences are descriptive and do not isolate specific building activities.",
        },
        {
            "analysis_area": "meter_contribution",
            "metric_name": "top5_entity_contribution_pct",
            "metric_value": round(top5_share, 6),
            "comparison_value": f"top_entity={top_entity['entity_id']}; top_entity_pct={top_entity['entity_contribution_pct']:.6f}",
            "interpretation_note": "Consumption is concentrated in a small number of selected meters, so ranking and audit decisions should account for contribution bias.",
            "powerbi_page": "Meter / Building Ranking",
            "evidence_table": "entity_scorecard",
            "evidence_visual": FIGURES["top_meter_contribution_pareto"],
            "limitation_note": "High contribution does not automatically mean inefficient operation.",
        },
        {
            "analysis_area": "weather_context",
            "metric_name": "daily_total_weather_correlation",
            "metric_value": round(temp_corr, 6),
            "comparison_value": f"rainfall_corr={rainfall_corr:.6f}",
            "interpretation_note": "Weather fields provide useful context, but simple daily correlations are weak and should not be treated as causal proof.",
            "powerbi_page": "Weather Impact",
            "evidence_table": "fact_energy_weather_daily",
            "evidence_visual": FIGURES["weather_consumption_context"],
            "limitation_note": "Weather is measured from nearby HKO stations and matched at daily granularity.",
        },
        {
            "analysis_area": "data_quality",
            "metric_name": "quality_issue_fact_rows",
            "metric_value": quality_issue_rows,
            "comparison_value": f"active_meters={active_meters}; excluded_or_nonactive_meters={excluded_meters}",
            "interpretation_note": "Data quality is explicitly visible through meter quality and row quality flags, protecting ranking and modelling from silent exclusions.",
            "powerbi_page": "Data Quality and Methodology",
            "evidence_table": "data_quality_summary",
            "evidence_visual": FIGURES["data_quality_flags"],
            "limitation_note": "Excluded meters remain represented in dim_entity but are not part of the modelled fact grain.",
        },
        {
            "analysis_area": "anomaly_review",
            "metric_name": "balanced_anomaly_count",
            "metric_value": balanced_anomaly_count,
            "comparison_value": f"highest_count_entity={balanced_entity}",
            "interpretation_note": "Balanced anomaly candidates are concentrated in specific entities and should be used as prioritized review candidates.",
            "powerbi_page": "Anomaly Explorer",
            "evidence_table": "fact_anomaly_scenarios",
            "evidence_visual": FIGURES["anomaly_case_review"],
            "limitation_note": "Anomaly flags are unsupervised candidates, not confirmed operational faults.",
        },
    ]
    return pd.DataFrame(rows)


def build_visual_summary(eda_summary: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "visual_file": row.evidence_visual,
            "visual_title": row.analysis_area.replace("_", " ").title(),
            "question_answered": f"What does {row.analysis_area.replace('_', ' ')} show for selected meters?",
            "main_observation": row.interpretation_note,
            "dashboard_page": row.powerbi_page,
            "recommended_use": "Use as evidence for dashboard layout and notebook interpretation.",
            "limitation_note": row.limitation_note,
        }
        for row in eda_summary.itertuples(index=False)
    ]
    return pd.DataFrame(rows)


def build_insight_recommendation_matrix(
    eda_summary: pd.DataFrame,
    entity: pd.DataFrame,
    model_eval: pd.DataFrame,
) -> pd.DataFrame:
    top_entity = entity.sort_values("entity_priority_rank").iloc[0]
    balanced_eval = model_eval[model_eval["scenario"].eq("balanced")].iloc[0]
    top5_share = eda_summary.loc[
        eda_summary["metric_name"].eq("top5_entity_contribution_pct"), "metric_value"
    ].iloc[0]
    weekday_gap = eda_summary.loc[
        eda_summary["metric_name"].eq("weekday_minus_weekend_average_daily_total"),
        "metric_value",
    ].iloc[0]
    rows = [
        {
            "item_type": "insight",
            "priority": "P0",
            "target_user": "Pengelola gedung",
            "evidence_source": "entity_scorecard",
            "evidence_metric": f"top5_entity_contribution_pct={top5_share}",
            "finding": "Konsumsi selected meters terkonsentrasi pada sejumlah kecil entity.",
            "recommendation": "Gunakan ranking kontribusi sebagai pintu awal prioritas audit, bukan sebagai bukti efisiensi tunggal.",
            "expected_action": "Review meter dengan kontribusi terbesar bersama konteks anomali dan kualitas data.",
            "limitation": "Subset hanya merepresentasikan selected T1440 meters.",
        },
        {
            "item_type": "insight",
            "priority": "P0",
            "target_user": "Tim sarana prasarana",
            "evidence_source": "fact_energy_weather_daily",
            "evidence_metric": f"weekday_minus_weekend_average={weekday_gap}",
            "finding": "Rata-rata konsumsi harian weekday lebih tinggi daripada weekend.",
            "recommendation": "Gunakan filter weekday/weekend untuk meninjau pola operasi dan mencari konsumsi tinggi di luar ekspektasi.",
            "expected_action": "Bandingkan hari anomali dengan kalender operasi gedung.",
            "limitation": "Analisis ini belum memasukkan jadwal kegiatan aktual kampus.",
        },
        {
            "item_type": "insight",
            "priority": "P0",
            "target_user": "Data analyst",
            "evidence_source": "model_evaluation_summary",
            "evidence_metric": f"balanced_anomaly_rate={balanced_eval['anomaly_rate']:.6f}",
            "finding": "Skenario balanced menghasilkan proporsi kandidat anomali sesuai parameter modelling.",
            "recommendation": "Gunakan skenario balanced sebagai default dashboard dan gunakan strict/sensitive untuk pembanding.",
            "expected_action": "Filter anomaly explorer berdasarkan scenario sebelum menyimpulkan prioritas review.",
            "limitation": "Tidak ada ground-truth label untuk mengukur akurasi supervised.",
        },
        {
            "item_type": "insight",
            "priority": "P1",
            "target_user": "Tim sustainability",
            "evidence_source": "fact_energy_weather_daily",
            "evidence_metric": "temperature_and_rainfall_context",
            "finding": "Cuaca berguna sebagai konteks pembacaan konsumsi, tetapi korelasi sederhana tidak cukup untuk klaim kausal.",
            "recommendation": "Tampilkan hot/rainy context pada dashboard sebagai filter pendukung.",
            "expected_action": "Baca anomaly days bersama suhu, hujan, dan quality flag.",
            "limitation": "Cuaca harian tidak menjelaskan aktivitas internal gedung.",
        },
        {
            "item_type": "recommendation",
            "priority": "P0",
            "target_user": "Pengelola gedung",
            "evidence_source": "entity_scorecard",
            "evidence_metric": f"top_priority_entity={top_entity['entity_id']}",
            "finding": "Entity prioritas tertinggi menggabungkan kontribusi konsumsi, anomaly rate, dan peak load.",
            "recommendation": "Mulai audit dari entity prioritas tertinggi dan cek apakah pola tinggi konsisten dengan fungsi ruang atau peralatan.",
            "expected_action": "Buat daftar investigasi awal dari entity_priority_rank.",
            "limitation": "Priority score adalah screening awal, bukan diagnosis teknis.",
        },
        {
            "item_type": "recommendation",
            "priority": "P0",
            "target_user": "Tim data",
            "evidence_source": "data_quality_summary",
            "evidence_metric": "meter_quality_flag_and_data_quality_flag",
            "finding": "Meter excluded dan weather-imputed rows sudah dipisahkan dari model utama.",
            "recommendation": "Pertahankan halaman data quality agar batasan data transparan saat dashboard dipakai.",
            "expected_action": "Validasi excluded meter sebelum memperluas klaim ke level kampus.",
            "limitation": "Meter excluded tetap perlu investigasi data source jika akan digunakan pada versi berikutnya.",
        },
        {
            "item_type": "recommendation",
            "priority": "P1",
            "target_user": "Manajemen kampus",
            "evidence_source": "fact_anomaly_scenarios",
            "evidence_metric": "scenario_stability_and_baseline_agreement",
            "finding": "Kandidat anomali lebih kuat jika stabil lintas scenario atau mendapat dukungan baseline.",
            "recommendation": "Prioritaskan review kandidat yang stabil dan memiliki baseline agreement sebelum menindaklanjuti kandidat sensitif.",
            "expected_action": "Gunakan anomaly explorer untuk menyortir stability dan baseline agreement.",
            "limitation": "Stabilitas model tetap tidak menggantikan validasi lapangan.",
        },
    ]
    return pd.DataFrame(rows)


def build_dashboard_validation_checklist() -> pd.DataFrame:
    rows = [
        ("table_import", "Import fact_energy_weather_daily", "Table loads with date and entity_id columns.", "fact_energy_weather_daily", "ready"),
        ("table_import", "Import fact_anomaly_scenarios", "Table loads with date, entity_id, scenario, score, and flag.", "fact_anomaly_scenarios", "ready"),
        ("table_import", "Import dimension and summary tables", "dim_date, dim_entity, dim_scenario, entity_scorecard, summaries load successfully.", "multiple", "ready"),
        ("relationship", "Connect fact_energy_weather_daily to dim_date", "Many-to-one relationship on date.", "fact_energy_weather_daily;dim_date", "manual_check_required"),
        ("relationship", "Connect fact_energy_weather_daily to dim_entity", "Many-to-one relationship on entity_id.", "fact_energy_weather_daily;dim_entity", "manual_check_required"),
        ("relationship", "Connect fact_anomaly_scenarios to dimensions", "Many-to-one relationships on date, entity_id, and scenario.", "fact_anomaly_scenarios", "manual_check_required"),
        ("dax_measure", "Create consumption KPI measures", "Total, average, peak, and active entity measures return values.", "fact_energy_weather_daily", "manual_check_required"),
        ("dax_measure", "Create anomaly KPI measures", "Anomaly count, rate, and average anomaly score return values by scenario.", "fact_anomaly_scenarios", "manual_check_required"),
        ("slicer", "Create required slicers", "Date, scenario, anomaly flag, entity, weekend, rainy/hot day, and quality filters work.", "multiple", "manual_check_required"),
        ("dashboard_page", "Build six dashboard pages", "Executive, Trend, Anomaly, Weather, Ranking, and Quality pages exist.", "multiple", "manual_check_required"),
        ("interaction", "Validate cross-filter and tooltip behavior", "Selections propagate from dimensions to fact visuals.", "multiple", "manual_check_required"),
        ("screenshot", "Capture dashboard screenshots", "Six page screenshots are captured after dashboard validation.", "Power BI Desktop", "manual_check_required"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "validation_area",
            "check_item",
            "expected_result",
            "source_table",
            "status",
        ],
    ).assign(notes="Power BI Desktop validation is manual; Python outputs are ready.")


def update_data_dictionary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    path = PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
    dictionary = pd.read_csv(path)
    dictionary = dictionary[~dictionary["table_name"].isin(tables.keys())].copy()
    descriptions = {
        "analysis_area": "EDA evidence category.",
        "metric_name": "Primary metric name for the evidence row.",
        "metric_value": "Primary metric value for the evidence row.",
        "comparison_value": "Comparison or context value for interpretation.",
        "interpretation_note": "Concise evidence-backed interpretation.",
        "powerbi_page": "Power BI page where the evidence is most relevant.",
        "evidence_table": "Source table used for the evidence.",
        "evidence_visual": "Final EDA visual associated with the evidence.",
        "limitation_note": "Scope or methodology limitation for the evidence.",
        "visual_file": "Final EDA figure filename.",
        "visual_title": "Short visual title.",
        "question_answered": "Analytical question answered by the visual.",
        "main_observation": "Primary observation from the visual.",
        "recommended_use": "Recommended dashboard or notebook use.",
        "item_type": "Insight or recommendation row type.",
        "priority": "Priority label for action or interpretation.",
        "target_user": "Primary audience for the item.",
        "evidence_source": "Dataset or output supporting the item.",
        "evidence_metric": "Metric cited as support.",
        "finding": "Evidence-backed finding.",
        "recommendation": "Recommended action or dashboard use.",
        "expected_action": "Concrete follow-up action.",
        "validation_area": "Power BI validation category.",
        "check_item": "Manual dashboard check item.",
        "expected_result": "Expected validation result.",
        "source_table": "Primary table for the check.",
        "status": "Readiness status.",
        "notes": "Additional validation notes.",
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
                    "source": "final EDA and dashboard evidence",
                    "treatment_notes": "Generated by final EDA evidence pipeline.",
                }
            )
    if rows:
        dictionary = pd.concat([dictionary, pd.DataFrame(rows)], ignore_index=True)
    return dictionary.sort_values(["table_name", "column_name"]).reset_index(drop=True)


def validate_outputs(paths: list[Path], tables: dict[str, pd.DataFrame]) -> None:
    for path in paths:
        if not path.exists() or path.stat().st_size == 0:
            raise ValueError(f"Expected non-empty output is missing: {path}")
    required_table_columns = {
        "eda_summary": [
            "analysis_area",
            "metric_name",
            "metric_value",
            "comparison_value",
            "interpretation_note",
            "powerbi_page",
            "evidence_table",
            "evidence_visual",
            "limitation_note",
        ],
        "visual_interpretation_summary": [
            "visual_file",
            "visual_title",
            "question_answered",
            "main_observation",
            "dashboard_page",
            "recommended_use",
            "limitation_note",
        ],
        "insight_recommendation_matrix": [
            "item_type",
            "priority",
            "target_user",
            "evidence_source",
            "evidence_metric",
            "finding",
            "recommendation",
            "expected_action",
            "limitation",
        ],
        "dashboard_validation_checklist": [
            "validation_area",
            "check_item",
            "expected_result",
            "source_table",
            "status",
            "notes",
        ],
    }
    for table_name, columns in required_table_columns.items():
        assert_required_columns(tables[table_name], columns, table_name)
    matrix = tables["insight_recommendation_matrix"]
    if int(matrix["item_type"].eq("insight").sum()) < 3:
        raise ValueError("insight_recommendation_matrix requires at least 3 insights.")
    if int(matrix["item_type"].eq("recommendation").sum()) < 3:
        raise ValueError("insight_recommendation_matrix requires at least 3 recommendations.")


def build_final_eda_outputs() -> dict[str, object]:
    inputs = load_inputs()
    fact = inputs["fact"]
    anomaly = inputs["anomaly"]
    entity = inputs["entity"]
    cases = inputs["cases"]
    model_eval = inputs["model_eval"]
    dim_entity = inputs["dim_entity"]

    ensure_dir(FINAL_EDA_DIR)
    daily = build_daily_summary(fact, anomaly)
    monthly_path, monthly = plot_monthly_consumption(fact)
    figure_paths = [
        plot_daily_consumption(daily),
        monthly_path,
        plot_weekday_weekend(daily),
        plot_pareto(entity),
        plot_weather_context(daily),
        plot_data_quality(fact, dim_entity),
        plot_anomaly_case_review(cases),
    ]
    eda_summary = build_eda_summary(daily, monthly, fact, anomaly, entity, dim_entity)
    visual_summary = build_visual_summary(eda_summary)
    insight_matrix = build_insight_recommendation_matrix(eda_summary, entity, model_eval)
    checklist = build_dashboard_validation_checklist()
    tables = {
        "eda_summary": eda_summary,
        "visual_interpretation_summary": visual_summary,
        "insight_recommendation_matrix": insight_matrix,
        "dashboard_validation_checklist": checklist,
    }
    dictionary = update_data_dictionary(tables)

    output_paths = {
        "eda_summary": write_csv(eda_summary, PROCESSED_DIR / "eda_summary.csv"),
        "visual_interpretation_summary": write_csv(
            visual_summary, PROCESSED_DIR / "visual_interpretation_summary.csv"
        ),
        "insight_recommendation_matrix": write_csv(
            insight_matrix, PROCESSED_DIR / "insight_recommendation_matrix.csv"
        ),
        "dashboard_validation_checklist": write_csv(
            checklist, PROCESSED_DIR / "dashboard_validation_checklist.csv"
        ),
        "data_dictionary": write_csv(
            dictionary, PROCESSED_DIR / "data_dictionary_energy_dashboard.csv"
        ),
    }
    validate_outputs(figure_paths + list(output_paths.values()), tables)
    return {
        "figures": [str(path) for path in figure_paths],
        "tables": {name: str(path) for name, path in output_paths.items()},
        "insight_count": int(insight_matrix["item_type"].eq("insight").sum()),
        "recommendation_count": int(insight_matrix["item_type"].eq("recommendation").sum()),
    }


def main() -> None:
    outputs = build_final_eda_outputs()
    print("Wrote final EDA and dashboard evidence outputs:")
    for figure in outputs["figures"]:
        print(f"- figure: {figure}")
    for name, path in outputs["tables"].items():
        print(f"- {name}: {path}")
    print(
        textwrap.dedent(
            f"""
            Evidence matrix counts:
            - insights: {outputs['insight_count']}
            - recommendations: {outputs['recommendation_count']}
            """
        ).strip()
    )


if __name__ == "__main__":
    main()
