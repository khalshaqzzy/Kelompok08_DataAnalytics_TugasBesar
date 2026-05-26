from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HKUST_ROOT = ROOT / "dataset" / "doi_10_5061_dryad_k3j9kd5h6__v20240801"
HKUST_ALL = HKUST_ROOT / "All_Data" / "All Data"
HKO_RAW = ROOT / "dataset" / "hko_open_data" / "raw"
OUT_DIR = ROOT / "dataset" / "profile_hkust_hko"

PROJECT_START = pd.Timestamp("2022-01-01")
PROJECT_END = pd.Timestamp("2024-05-27")


def excel_profile(path: Path) -> dict[str, object]:
    df = pd.read_excel(path, engine="openpyxl")
    df = df.rename(columns={df.columns[0]: "time", df.columns[1]: "number"})
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["number"] = pd.to_numeric(df["number"], errors="coerce")
    return {
        "file": str(path.relative_to(ROOT)),
        "meter_id": path.stem.replace("GUI_NO.", ""),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "start": str(df["time"].min()),
        "end": str(df["time"].max()),
        "missing_time": int(df["time"].isna().sum()),
        "missing_number": int(df["number"].isna().sum()),
        "min_number": None if df["number"].dropna().empty else float(df["number"].min()),
        "max_number": None if df["number"].dropna().empty else float(df["number"].max()),
        "sample_rows": df.head(3).astype(str).to_dict(orient="records"),
    }


def parse_hko_csv(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, skiprows=2, header=None, encoding="utf-8-sig")
    raw = raw.iloc[:, :5].copy()
    raw.columns = ["year", "month", "day", "value", "data_completeness"]
    for col in ["year", "month", "day"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw["date"] = pd.to_datetime(
        {
            "year": raw["year"],
            "month": raw["month"],
            "day": raw["day"],
        },
        errors="coerce",
    )
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    return raw[["date", "value", "data_completeness"]]


def hko_profile(path: Path) -> dict[str, object]:
    df = parse_hko_csv(path)
    project = df[(df["date"] >= PROJECT_START) & (df["date"] <= PROJECT_END)]
    return {
        "file": str(path.relative_to(ROOT)),
        "dataset_id": path.stem,
        "rows_total": int(len(df)),
        "rows_project_period": int(len(project)),
        "columns": list(df.columns),
        "start": str(df["date"].min()),
        "end": str(df["date"].max()),
        "project_start": str(project["date"].min()) if len(project) else None,
        "project_end": str(project["date"].max()) if len(project) else None,
        "missing_value_total": int(df["value"].isna().sum()),
        "missing_value_project_period": int(project["value"].isna().sum()),
        "data_completeness_counts_project": project["data_completeness"].fillna("").value_counts().to_dict(),
        "sample_rows": project.head(3).astype(str).to_dict(orient="records"),
    }


def count_ttl_entities(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    subjects = set(re.findall(r"^([A-Za-z0-9_:-]+)\s+a\s+", text, flags=re.MULTILINE))
    gui_refs = set(re.findall(r"GUI[_./-]?NO[._-]?[A-Z0-9]+", text, flags=re.IGNORECASE))
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "lines": text.count("\n") + 1,
        "subject_count_estimate": len(subjects),
        "gui_reference_count_estimate": len(gui_refs),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_dir = HKUST_ALL / "Raw Dataset" / "Time-series data"
    clean_root = HKUST_ALL / "Clean Dataset" / "Resappled data"
    ttl_path = HKUST_ALL / "Raw Dataset" / "HKUST_Meter_Metadata.ttl"

    inventory_rows = []
    for label, path in [
        ("raw_time_series", raw_dir),
        ("clean_T15", clean_root / "T15"),
        ("clean_T30", clean_root / "T30"),
        ("clean_T60", clean_root / "T60"),
        ("clean_T1440", clean_root / "T1440"),
    ]:
        files = sorted(path.glob("*.xlsx")) if path.exists() else []
        inventory_rows.append(
            {
                "group": label,
                "path": str(path.relative_to(ROOT)),
                "file_count": len(files),
                "total_mb": round(sum(f.stat().st_size for f in files) / 1024 / 1024, 3),
                "sample_file": files[0].name if files else "",
            }
        )

    hkust_excel_profiles = {
        "T1440_all": [excel_profile(p) for p in sorted((clean_root / "T1440").glob("*.xlsx"))],
        "T60_sample": [excel_profile(p) for p in sorted((clean_root / "T60").glob("*.xlsx"))[:8]],
        "raw_sample": [excel_profile(p) for p in sorted(raw_dir.glob("*.xlsx"))[:5]],
    }

    hko_profiles = [hko_profile(p) for p in sorted(HKO_RAW.glob("*.csv"))]
    metadata_profile = count_ttl_entities(ttl_path)

    outputs = {
        "hkust_inventory": inventory_rows,
        "hkust_excel_profiles": hkust_excel_profiles,
        "hkust_metadata_profile": metadata_profile,
        "hko_profiles": hko_profiles,
    }

    (OUT_DIR / "dataset_profile.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    pd.DataFrame(inventory_rows).to_csv(OUT_DIR / "hkust_file_inventory.csv", index=False)
    pd.DataFrame(hko_profiles).to_csv(OUT_DIR / "hko_profile_summary.csv", index=False)

    t1440_rows = []
    for item in hkust_excel_profiles["T1440_all"]:
        t1440_rows.append({k: v for k, v in item.items() if k != "sample_rows"})
    pd.DataFrame(t1440_rows).to_csv(OUT_DIR / "hkust_t1440_profile.csv", index=False)

    print(f"Wrote profile outputs to {OUT_DIR.relative_to(ROOT)}")
    print(f"HKUST groups: {len(inventory_rows)}")
    print(f"HKO files profiled: {len(hko_profiles)}")


if __name__ == "__main__":
    main()
