from __future__ import annotations

import re
from collections import defaultdict, deque
from pathlib import Path

import pandas as pd

from config import PROCESSED_DIR, TTL_PATH
from io_utils import write_csv


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
        mapping_status = (
            "mapped"
            if subjects and buildings
            else "partial"
            if ttl_declared or subjects
            else "unmapped"
        )

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


def build_dim_entity_t1440(meter_ids: set[str]) -> pd.DataFrame:
    if not TTL_PATH.exists():
        raise FileNotFoundError(f"Missing TTL metadata: {TTL_PATH}")
    return parse_ttl_metadata(TTL_PATH, meter_ids)


def main() -> None:
    inventory_path = PROCESSED_DIR.parent / "t1440_meter_inventory_with_decision.csv"
    if not inventory_path.exists():
        raise FileNotFoundError(
            "Run scripts\\hkust_t1440.py before building standalone TTL mapping."
        )
    inventory = pd.read_csv(inventory_path)
    metadata = build_dim_entity_t1440(set(inventory["meter_id"]))
    write_csv(metadata, PROCESSED_DIR / "dim_entity_t1440.csv")
    print(PROCESSED_DIR / "dim_entity_t1440.csv")
    print(metadata.shape)


if __name__ == "__main__":
    main()

