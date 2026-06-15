from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv_dates(path: Path, date_columns: Iterable[str] = ("date",)) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    ensure_dir(path.parent)
    df.to_csv(path, index=False)
    return path


def assert_required_columns(df: pd.DataFrame, columns: Iterable[str], table_name: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{table_name} missing required columns: {', '.join(missing)}")


def assert_unique_key(df: pd.DataFrame, columns: Iterable[str], table_name: str) -> None:
    key = list(columns)
    duplicated = int(df.duplicated(key).sum())
    if duplicated:
        raise ValueError(
            f"{table_name} has {duplicated} duplicate rows for key: {', '.join(key)}"
        )


def normalize_date_column(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    out = df.copy()
    out[column] = pd.to_datetime(out[column], errors="coerce").dt.normalize()
    return out

