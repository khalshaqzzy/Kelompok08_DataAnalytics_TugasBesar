from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from config import (
    PROFILE_DIR,
    PROCESSED_DIR,
    PROJECT_END,
    PROJECT_START,
    SELECTED_METERS,
    T1440_DIR,
    TARGET_BUILDING,
)
from io_utils import write_csv
from ttl_entity_mapping import build_dim_entity_t1440


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
    df = df[(df["date"] >= PROJECT_START) & (df["date"] <= PROJECT_END)]
    df["daily_consumption"] = df.groupby("meter_id")["meter_reading"].diff()
    df["negative_diff_flag"] = df["daily_consumption"].lt(0)
    df.loc[df["daily_consumption"] < 0, "daily_consumption"] = pd.NA
    return df[
        ["date", "meter_id", "meter_reading", "daily_consumption", "negative_diff_flag"]
    ]


def profile_t1440_files(t1440_dir: Path = T1440_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    profiles = []

    for path in sorted(t1440_dir.glob("*.xlsx")):
        df = read_t1440_file(path)
        if df.empty:
            continue
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
        raise FileNotFoundError(f"No T1440 .xlsx files found in {t1440_dir}")

    energy_long = pd.concat(frames, ignore_index=True)
    inventory = pd.DataFrame(profiles)
    max_rows = inventory["row_count"].max()
    inventory["coverage_ratio"] = inventory["row_count"] / max_rows
    return inventory, energy_long


def add_decision_columns(inventory: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    out = inventory.merge(metadata, on="meter_id", how="left")
    active_positive = out.loc[out["total_consumption"].gt(0), "total_consumption"]
    near_zero_cutoff = active_positive.quantile(0.10)

    flags = []
    for row in out.itertuples(index=False):
        if row.all_zero_reading or row.total_consumption == 0:
            flags.append("zero_constant")
        elif row.coverage_ratio < 0.8:
            flags.append("short_coverage")
        elif row.total_consumption <= near_zero_cutoff:
            flags.append("near_zero_low_signal")
        else:
            flags.append("active")

    out["quality_flag"] = flags
    out["rank_total_consumption"] = out["total_consumption"].rank(
        ascending=False, method="min"
    ).astype(int)

    out["decision"] = "exclude_from_main_model"
    out.loc[out["meter_id"].isin(SELECTED_METERS), "decision"] = "selected_main_subset"
    out.loc[
        out["quality_flag"].eq("active")
        & out["mapping_status"].eq("mapped")
        & out["building"].fillna("").str.contains(TARGET_BUILDING, regex=False)
        & ~out["meter_id"].isin(SELECTED_METERS),
        "decision",
    ] = "comparison_or_secondary"

    return out.sort_values(["decision", "rank_total_consumption", "meter_id"])


def build_master_energy(
    inventory: pd.DataFrame, energy_long: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = inventory[inventory["decision"].eq("selected_main_subset")].copy()
    selected_long = energy_long[energy_long["meter_id"].isin(selected["meter_id"])].copy()
    master = selected_long.merge(
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
    master["year"] = master["date"].dt.year
    master["month"] = master["date"].dt.month
    master["month_name"] = master["date"].dt.month_name()
    master["quarter"] = "Q" + master["date"].dt.quarter.astype(str)
    master["day_of_week"] = master["date"].dt.day_name()
    master["day_of_week_num"] = master["date"].dt.dayofweek + 1
    master["is_weekend"] = master["date"].dt.dayofweek.ge(5).astype(int)
    master["is_first_reading"] = master["daily_consumption"].isna().astype(int)
    master["valid_for_analysis"] = (
        master["decision"].eq("selected_main_subset")
        & master["quality_flag"].eq("active")
        & master["daily_consumption"].notna()
        & ~master["negative_diff_flag"]
    ).astype(int)
    master = master.sort_values(["date", "meter_id"])
    return selected, master


def write_justification(inventory: pd.DataFrame, selected: pd.DataFrame) -> None:
    quality_counts = inventory["quality_flag"].value_counts().sort_index()
    selected_ids = ", ".join(f"`{meter}`" for meter in selected["meter_id"])
    excluded = {
        flag: ", ".join(
            f"`{meter}`"
            for meter in inventory.loc[inventory["quality_flag"].eq(flag), "meter_id"]
        )
        or "-"
        for flag in ["zero_constant", "near_zero_low_signal", "short_coverage"]
    }

    lines = [
        "# T1440 Subset Selection Justification",
        "",
        "## Objective",
        "",
        "Subset ini dibuat untuk mendukung tahap Obtain dan Scrub pada proyek Energy Efficiency Analytics. Pemilihan dilakukan secara objektif berdasarkan interval harian, coverage, kualitas sinyal, metadata TTL, dan fokus analitis pada satu gedung.",
        "",
        "## Selection Criteria",
        "",
        "1. Interval compatibility: hanya file T1440 yang dipilih karena selaras dengan HKO daily weather.",
        "2. Completeness: prioritas pada meter dengan coverage penuh 2022-01-01 sampai 2024-05-27.",
        "3. Data quality: zero constant, near-zero/low-signal, dan short coverage tidak dipakai dalam model utama.",
        "4. TTL interpretability: meter harus punya mapping building/room/equipment yang dapat dijelaskan.",
        "5. Analytical focus: subset difokuskan pada satu building agar perbandingan antar meter lebih konsisten.",
        "",
        "## Result",
        "",
        f"Building utama yang dipilih: `{TARGET_BUILDING}`.",
        "",
        f"Meter utama yang dipilih: {selected_ids}",
        "",
        "## Quality Flag Summary",
        "",
        "| Quality flag | Meter count |",
        "|---|---:|",
    ]
    lines.extend(f"| {flag} | {count} |" for flag, count in quality_counts.items())
    lines.extend(
        [
            "",
            "## Exclusion Notes",
            "",
            f"- Zero constant: {excluded['zero_constant']}",
            f"- Near-zero / low-signal: {excluded['near_zero_low_signal']}",
            f"- Short coverage: {excluded['short_coverage']}",
            "",
            "## Recommended Explanation for Report",
            "",
            f"Berdasarkan inventory awal, semua file T1440 dicatat terlebih dahulu. Pemilihan subset menggunakan kriteria objektif: kesesuaian interval harian dengan data HKO, coverage penuh, meter aktif non-zero, mapping TTL yang jelas, dan fokus pada `{TARGET_BUILDING}` agar analisis konsumsi, anomaly detection, dan dashboard Power BI tetap konsisten.",
            "",
        ]
    )
    write_path = PROFILE_DIR / "t1440_subset_selection_justification.md"
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text("\n".join(lines), encoding="utf-8")


def build_t1440_outputs() -> dict[str, Path]:
    inventory, energy_long = profile_t1440_files()
    metadata = build_dim_entity_t1440(set(inventory["meter_id"]))
    inventory = add_decision_columns(inventory, metadata)
    selected, master = build_master_energy(inventory, energy_long)
    selected_long = energy_long[energy_long["meter_id"].isin(selected["meter_id"])].copy()

    outputs = {
        "inventory": write_csv(
            inventory, DATASET_PROFILE_PATH := PROFILE_DIR / "t1440_meter_inventory_with_decision.csv"
        ),
        "inventory_compat": write_csv(
            inventory, PROCESSED_DIR.parent / "t1440_meter_inventory_with_decision.csv"
        ),
        "dim_entity_t1440": write_csv(metadata, PROCESSED_DIR / "dim_entity_t1440.csv"),
        "selected_meters": write_csv(selected, PROCESSED_DIR / "selected_t1440_meters.csv"),
        "fact_long": write_csv(
            selected_long, PROCESSED_DIR / "fact_energy_t1440_selected_long.csv"
        ),
        "master_energy": write_csv(
            master[master["daily_consumption"].notna()].copy(),
            PROCESSED_DIR / "master_energy_t1440_selected_daily.csv",
        ),
    }
    write_justification(inventory, selected)
    outputs["justification"] = PROFILE_DIR / "t1440_subset_selection_justification.md"
    return outputs


def main() -> None:
    outputs = build_t1440_outputs()
    print("Wrote T1440 canonical outputs:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()

