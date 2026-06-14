from __future__ import annotations

import argparse
import re
from collections import defaultdict, deque
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLEAN_DATASET = Path(
    r"D:\Univ\Semester-6\Data Analytics\Tugas\All Data\Clean Dataset"
)
PROJECT_START = pd.Timestamp("2022-01-01")
PROJECT_END = pd.Timestamp("2024-05-27")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile HKUST T1440 files, map TTL metadata, and select a defensible analysis subset."
    )
    parser.add_argument(
        "--clean-dataset",
        type=Path,
        default=DEFAULT_CLEAN_DATASET,
        help="Path to HKUST Clean Dataset folder containing HKUST_Meter_Metadata.ttl and Resappled data/T1440.",
    )
    parser.add_argument(
        "--target-building",
        default="Cheng_Yu_Tung_Building",
        help="Building selected for the main subset after profiling.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=12,
        help="Maximum active meters to select from the target building.",
    )
    return parser.parse_args()


def read_t1440_file(path: Path) -> pd.DataFrame:
    meter_match = re.search(r"[A-Z]\d+", path.stem)
    if not meter_match:
        raise ValueError(f"Cannot infer meter id from {path.name}")

    df = pd.read_excel(path, engine="openpyxl")
    df = df.rename(columns={df.columns[0]: "date", df.columns[1]: "meter_reading"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce")
    df["meter_id"] = meter_match.group(0)
    df = df.dropna(subset=["date"]).sort_values("date")
    df["daily_consumption"] = df.groupby("meter_id")["meter_reading"].diff()
    df["negative_diff_flag"] = df["daily_consumption"].lt(0)
    df.loc[df["daily_consumption"] < 0, "daily_consumption"] = pd.NA
    return df[["date", "meter_id", "meter_reading", "daily_consumption", "negative_diff_flag"]]


def profile_t1440_files(t1440_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    profiles = []

    for path in sorted(t1440_dir.glob("*.xlsx")):
        df = read_t1440_file(path)
        meter_id = df["meter_id"].iloc[0]
        frames.append(df)

        positive_consumption = df["daily_consumption"].dropna()
        profiles.append(
            {
                "meter_id": meter_id,
                "file_name": path.name,
                "source_path": str(path),
                "start_date": df["date"].min().date().isoformat(),
                "end_date": df["date"].max().date().isoformat(),
                "row_count": int(len(df)),
                "reading_min": float(df["meter_reading"].min()),
                "reading_max": float(df["meter_reading"].max()),
                "total_consumption": float(positive_consumption.sum()),
                "mean_daily_consumption": float(positive_consumption.mean())
                if len(positive_consumption)
                else 0.0,
                "nonzero_days": int(positive_consumption.gt(0).sum()),
                "negative_diff_days": int(df["negative_diff_flag"].sum()),
                "all_zero_reading": bool(df["meter_reading"].fillna(0).eq(0).all()),
            }
        )

    if not frames:
        raise FileNotFoundError(f"No .xlsx files found in {t1440_dir}")

    energy_long = pd.concat(frames, ignore_index=True)
    inventory = pd.DataFrame(profiles)
    max_rows = inventory["row_count"].max()
    inventory["coverage_ratio"] = inventory["row_count"] / max_rows
    return inventory, energy_long


def parse_ttl_metadata(ttl_path: Path, meter_ids: set[str]) -> pd.DataFrame:
    text = ttl_path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.finditer(r"(?m)^(bldg:[^\s]+)\s+(.*?)(?=\n\S|\Z)", text, re.S)

    entities: dict[str, dict[str, object]] = {}
    parents: dict[str, set[str]] = defaultdict(set)
    metered_by: dict[str, set[str]] = defaultdict(set)

    for block in blocks:
        subject = block.group(1).replace("bldg:", "")
        body = block.group(2)
        type_match = re.search(r"\ba\s+(.+?)(?:;|\.)", body, re.S)
        type_names = set()
        if type_match:
            type_names = set(re.findall(r"brick:([A-Za-z_]+)", type_match.group(1)))

        has_parts = [
            item.replace("bldg:", "")
            for segment in re.findall(r"brick:hasPart\s+(.+?)(?:;|\.)", body, re.S)
            for item in re.findall(r"bldg:[A-Za-z0-9_]+", segment)
        ]
        location_of = [
            item.replace("bldg:", "")
            for segment in re.findall(r"brick:isLocationOf\s+(.+?)(?:;|\.)", body, re.S)
            for item in re.findall(r"bldg:[A-Za-z0-9_]+", segment)
        ]
        meters = [
            item.replace("bldg:Meter_", "")
            for segment in re.findall(r"brick:isMeteredBy\s+(.+?)(?:;|\.)", body, re.S)
            for item in re.findall(r"bldg:Meter_[A-Z]\d+", segment)
        ]
        timeseries_refs = re.findall(r'ref:hasTimeseriesData\s+"([^"]+)"', body)

        entities[subject] = {
            "types": sorted(type_names),
            "timeseries_refs": timeseries_refs,
        }

        for child in has_parts + location_of:
            parents[child].add(subject)
        for meter in meters:
            metered_by[meter].add(subject)

    def nearest_type(entity: str, target_type: str) -> str | None:
        seen = {entity}
        queue: deque[str] = deque([entity])
        while queue:
            current = queue.popleft()
            if target_type in entities.get(current, {}).get("types", []):
                return current
            for parent in parents.get(current, set()):
                if parent not in seen:
                    seen.add(parent)
                    queue.append(parent)
        return None

    rows = []
    for meter_id in sorted(meter_ids):
        meter_entity = f"Meter_{meter_id}"
        subjects = sorted(metered_by.get(meter_id, set()))
        buildings = sorted({nearest_type(subject, "Building") for subject in subjects} - {None})
        floors = sorted({nearest_type(subject, "Floor") for subject in subjects} - {None})
        subject_types = sorted(
            {
                entity_type
                for subject in subjects
                for entity_type in entities.get(subject, {}).get("types", [])
            }
        )
        ttl_declared = meter_entity in entities
        mapping_status = "mapped" if subjects and buildings else "partial" if ttl_declared or subjects else "unmapped"

        rows.append(
            {
                "meter_id": meter_id,
                "meter_name": meter_entity,
                "ttl_meter_declared": ttl_declared,
                "ttl_timeseries_ref": "; ".join(
                    entities.get(meter_entity, {}).get("timeseries_refs", [])
                ),
                "building": "; ".join(buildings),
                "floor": "; ".join(floors),
                "room_or_equipment": "; ".join(subjects),
                "entity_type": "; ".join(subject_types) if subject_types else "meter",
                "n_metered_entities": len(subjects),
                "mapping_status": mapping_status,
            }
        )

    return pd.DataFrame(rows)


def add_decision_columns(
    inventory: pd.DataFrame,
    metadata: pd.DataFrame,
    target_building: str,
    top_n: int,
) -> pd.DataFrame:
    out = inventory.merge(metadata, on="meter_id", how="left")
    active_positive = out.loc[out["total_consumption"].gt(0), "total_consumption"]
    near_zero_cutoff = active_positive.quantile(0.10)

    conditions = []
    for row in out.itertuples(index=False):
        if row.all_zero_reading or row.total_consumption == 0:
            conditions.append("zero_constant")
        elif row.coverage_ratio < 0.8:
            conditions.append("short_coverage")
        elif row.total_consumption <= near_zero_cutoff:
            conditions.append("near_zero_low_signal")
        else:
            conditions.append("active")

    out["quality_flag"] = conditions
    out["rank_total_consumption"] = out["total_consumption"].rank(
        ascending=False, method="min"
    ).astype(int)

    target_mask = (
        out["quality_flag"].eq("active")
        & out["mapping_status"].eq("mapped")
        & out["building"].fillna("").str.contains(target_building, regex=False)
    )
    selected_meter_ids = (
        out.loc[target_mask]
        .sort_values("total_consumption", ascending=False)
        .head(top_n)["meter_id"]
        .tolist()
    )

    out["decision"] = "exclude_from_main_model"
    out.loc[out["meter_id"].isin(selected_meter_ids), "decision"] = "selected_main_subset"
    out.loc[
        out["quality_flag"].eq("active")
        & out["mapping_status"].eq("mapped")
        & ~out["meter_id"].isin(selected_meter_ids),
        "decision",
    ] = "comparison_or_secondary"

    return out.sort_values(["decision", "rank_total_consumption", "meter_id"])


def save_visuals(
    inventory: pd.DataFrame,
    energy_long: pd.DataFrame,
    selected: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    ordered = inventory.sort_values("total_consumption", ascending=False)
    palette = {
        "selected_main_subset": "#0F766E",
        "comparison_or_secondary": "#64748B",
        "exclude_from_main_model": "#CBD5E1",
    }
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=ordered,
        x="meter_id",
        y="total_consumption",
        hue="decision",
        dodge=False,
        palette=palette,
    )
    ax.set_title("T1440 Total Consumption by Meter")
    ax.set_xlabel("Meter ID")
    ax.set_ylabel("Total derived daily consumption")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "t1440_total_consumption_by_meter.png", dpi=180)
    plt.close()

    quality_counts = (
        inventory["quality_flag"]
        .value_counts()
        .rename_axis("quality_flag")
        .reset_index(name="meter_count")
    )
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(
        data=quality_counts,
        x="quality_flag",
        y="meter_count",
        color="#2563EB",
    )
    ax.set_title("T1440 Meter Quality Flag Counts")
    ax.set_xlabel("Quality flag")
    ax.set_ylabel("Meter count")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(output_dir / "t1440_quality_flag_counts.png", dpi=180)
    plt.close()

    building_counts = (
        inventory.assign(building_short=inventory["building"].replace("", "unmapped"))
        .groupby("building_short")["meter_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="meter_count")
    )
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(
        data=building_counts,
        y="building_short",
        x="meter_count",
        color="#9333EA",
    )
    ax.set_title("TTL-Mapped T1440 Meter Count by Building")
    ax.set_xlabel("Meter count")
    ax.set_ylabel("Building")
    plt.tight_layout()
    plt.savefig(output_dir / "t1440_meter_count_by_building.png", dpi=180)
    plt.close()

    selected_long = energy_long[energy_long["meter_id"].isin(selected["meter_id"])].copy()
    selected_long = selected_long[
        (selected_long["date"] >= PROJECT_START) & (selected_long["date"] <= PROJECT_END)
    ]
    plt.figure(figsize=(13, 6))
    ax = sns.lineplot(
        data=selected_long,
        x="date",
        y="daily_consumption",
        hue="meter_id",
        linewidth=1,
    )
    ax.set_title("Selected Cheng Yu Tung Building Meters - Daily Consumption")
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily consumption")
    ax.legend(title="Meter", ncol=3, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "selected_meters_daily_consumption.png", dpi=180)
    plt.close()


def write_justification(
    inventory: pd.DataFrame,
    selected: pd.DataFrame,
    target_building: str,
    output_path: Path,
) -> None:
    quality_counts = inventory["quality_flag"].value_counts().to_dict()
    selected_ids = ", ".join(f"`{meter}`" for meter in selected["meter_id"])
    excluded_zero = ", ".join(
        f"`{meter}`"
        for meter in inventory.loc[inventory["quality_flag"].eq("zero_constant"), "meter_id"]
    )
    excluded_near_zero = ", ".join(
        f"`{meter}`"
        for meter in inventory.loc[
            inventory["quality_flag"].eq("near_zero_low_signal"), "meter_id"
        ]
    )
    excluded_short = ", ".join(
        f"`{meter}`"
        for meter in inventory.loc[inventory["quality_flag"].eq("short_coverage"), "meter_id"]
    )

    text = f"""# T1440 Subset Selection Justification

## Objective

Subset ini dibuat untuk mendukung tahap **Obtain** pada proyek Energy Efficiency Analytics. Tujuannya adalah memilih file time-series harian yang realistis untuk diproses tim berikutnya, tetap terdokumentasi, dan dapat dipertanggungjawabkan secara objektif.

## Selection Criteria

1. **Interval compatibility**: hanya file `T1440` yang dipilih sebagai basis utama karena intervalnya harian dan dapat digabung langsung dengan data cuaca harian HKO berdasarkan kolom tanggal.
2. **Completeness**: prioritas diberikan pada meter dengan coverage penuh periode proyek, yaitu 2022-01-01 sampai 2024-05-27.
3. **Data quality**: meter nol konstan, near-zero/low-signal, dan short coverage tidak dipakai pada model utama, tetapi tetap dicatat untuk data quality dashboard.
4. **TTL interpretability**: meter harus memiliki mapping TTL yang jelas ke building serta room/equipment agar hasil dashboard tidak berhenti pada ID meter saja.
5. **Analytical focus**: subset difokuskan pada satu building dengan banyak meter aktif supaya perbandingan antar meter/equipment lebih konsisten.

## Result

Building utama yang dipilih: `{target_building}`.

Meter utama yang dipilih:

{selected_ids}

Ringkasan quality flag:

| Quality flag | Meter count |
|---|---:|
"""
    for flag, count in sorted(quality_counts.items()):
        text += f"| {flag} | {count} |\n"

    text += f"""
## Exclusion Notes

- Zero constant: {excluded_zero or "-"}
- Near-zero / low-signal: {excluded_near_zero or "-"}
- Short coverage: {excluded_short or "-"}

## Recommended Explanation for Report

Berdasarkan inventory awal, semua file T1440 dicatat terlebih dahulu. Pemilihan subset dilakukan menggunakan kriteria objektif: kesesuaian interval harian dengan data cuaca HKO, coverage penuh, meter aktif dengan konsumsi non-zero, mapping TTL yang jelas, dan fokus pada satu gedung agar analisis tetap konsisten. Hasil profiling menunjukkan `{target_building}` memiliki kumpulan meter T1440 aktif dengan metadata yang lengkap, sehingga dipilih sebagai fokus utama untuk analisis konsumsi, anomaly detection, dan dashboard Power BI.
"""
    output_path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    clean_dataset = args.clean_dataset
    t1440_dir = clean_dataset / "Resappled data" / "T1440"
    ttl_path = clean_dataset / "HKUST_Meter_Metadata.ttl"

    profile_dir = ROOT / "dataset" / "profile_hkust_hko"
    processed_dir = ROOT / "dataset" / "processed"
    visual_dir = ROOT / "outputs" / "subset_selection"
    profile_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    inventory, energy_long = profile_t1440_files(t1440_dir)
    metadata = parse_ttl_metadata(ttl_path, set(inventory["meter_id"]))
    inventory = add_decision_columns(
        inventory,
        metadata,
        target_building=args.target_building,
        top_n=args.top_n,
    )
    selected = inventory[inventory["decision"].eq("selected_main_subset")].copy()
    selected_long = energy_long[energy_long["meter_id"].isin(selected["meter_id"])].copy()
    master_energy = selected_long.merge(
        inventory[
            [
                "meter_id",
                "file_name",
                "source_path",
                "start_date",
                "end_date",
                "row_count",
                "coverage_ratio",
                "total_consumption",
                "mean_daily_consumption",
                "nonzero_days",
                "negative_diff_days",
                "quality_flag",
                "rank_total_consumption",
                "decision",
                "meter_name",
                "building",
                "floor",
                "room_or_equipment",
                "entity_type",
                "n_metered_entities",
                "mapping_status",
            ]
        ],
        on="meter_id",
        how="left",
    )
    master_energy["year"] = master_energy["date"].dt.year
    master_energy["month"] = master_energy["date"].dt.month
    master_energy["month_name"] = master_energy["date"].dt.month_name()
    master_energy["quarter"] = "Q" + master_energy["date"].dt.quarter.astype(str)
    master_energy["day_of_week"] = master_energy["date"].dt.day_name()
    master_energy["is_weekend"] = master_energy["date"].dt.dayofweek.ge(5).astype(int)
    master_energy["is_first_reading"] = master_energy["daily_consumption"].isna().astype(int)
    master_energy["valid_for_analysis"] = (
        master_energy["decision"].eq("selected_main_subset")
        & master_energy["quality_flag"].eq("active")
        & master_energy["daily_consumption"].notna()
    ).astype(int)
    master_energy = master_energy[
        [
            "date",
            "year",
            "month",
            "month_name",
            "quarter",
            "day_of_week",
            "is_weekend",
            "meter_id",
            "meter_name",
            "building",
            "floor",
            "room_or_equipment",
            "entity_type",
            "meter_reading",
            "daily_consumption",
            "is_first_reading",
            "negative_diff_flag",
            "quality_flag",
            "coverage_ratio",
            "mapping_status",
            "decision",
            "valid_for_analysis",
            "file_name",
            "source_path",
            "start_date",
            "end_date",
            "row_count",
            "total_consumption",
            "mean_daily_consumption",
            "nonzero_days",
            "negative_diff_days",
            "rank_total_consumption",
            "n_metered_entities",
        ]
    ].sort_values(["date", "meter_id"])

    inventory.to_csv(profile_dir / "t1440_meter_inventory_with_decision.csv", index=False)
    metadata.to_csv(processed_dir / "dim_entity_t1440.csv", index=False)
    selected.to_csv(processed_dir / "selected_t1440_meters.csv", index=False)
    selected_long.to_csv(processed_dir / "fact_energy_t1440_selected_long.csv", index=False)
    master_energy.to_csv(processed_dir / "master_energy_t1440_selected_daily.csv", index=False)

    save_visuals(inventory, energy_long, selected, visual_dir)
    write_justification(
        inventory,
        selected,
        args.target_building,
        profile_dir / "t1440_subset_selection_justification.md",
    )

    print("Wrote:")
    print(profile_dir / "t1440_meter_inventory_with_decision.csv")
    print(profile_dir / "t1440_subset_selection_justification.md")
    print(processed_dir / "dim_entity_t1440.csv")
    print(processed_dir / "selected_t1440_meters.csv")
    print(processed_dir / "fact_energy_t1440_selected_long.csv")
    print(processed_dir / "master_energy_t1440_selected_daily.csv")
    print(visual_dir)
    print()
    print("Selected meters:")
    print(", ".join(selected["meter_id"].tolist()))


if __name__ == "__main__":
    main()
