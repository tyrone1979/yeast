#!/usr/bin/env python3
"""Assemble digitized industrial yeast fermentation batch tables into publication-ready CSVs.

Primary scientific provenance is expert-completed industrial PDF batch logs (not redistributed
in this package). This script packages already-digitized tabular extracts into the public CSV layout.
"""

from __future__ import annotations

import csv
import json
import math
import statistics as stats
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "data.xlsx"
OUT = ROOT / "dataset"
ASSESS = "评价标准"

# Columns 2–9 in the source sheet: process variables + sugar feed / TFS.
# Helper fields (remark, delta_*, auto_*) alone do not make a valid hourly record.
PROCESS_VALUE_INDICES = range(1, 10)


def round_or_none(v, nd=6):
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return round(v, nd)
    return v


def to_float(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def describe(rows, key, batch_ids=None, exclude_batch_ids=None, exclude_predicate=None):
    vals = []
    for r in rows:
        if batch_ids is not None and r["batch_id"] not in batch_ids:
            continue
        if exclude_batch_ids is not None and r["batch_id"] in exclude_batch_ids:
            continue
        if exclude_predicate is not None and exclude_predicate(r):
            continue
        v = to_float(r.get(key))
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    return {
        "n": len(vals),
        "mean": round(sum(vals) / len(vals), 4),
        "std": round(stats.pstdev(vals), 4),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
    }


def write_csv(path: Path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def record_has_process_values(vals) -> bool:
    return any(vals[i] is not None for i in PROCESS_VALUE_INDICES)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(SRC, data_only=True)

    meta_fields = [
        "batch_id",
        "lot_no",
        "strain_id",
        "seed_lot_no",
        "seed_volume_m3",
        "seed_y30_kg",
        "yield_y30_kg",
        "n_records",
        "time_start_h",
        "time_end_h",
        "data_completeness",
        "has_process_variables",
        "notes",
    ]
    ts_fields = [
        "batch_id",
        "lot_no",
        "time_h",
        "airflow_m3_h",
        "volume_m3",
        "ph",
        "alcohol_vv_pct",
        "cell_concentration_gpl",
        "biomass_y30_kg",
        "growth_modulus",
        "sugar_feed_rate_kg_rs_h",
        "total_fermentable_sugar_kg",
        "remark",
        "delta_alcohol",
        "delta_growth_modulus",
        "auto_growth_modulus",
    ]

    meta_rows = []
    ts_rows = []
    dropped_empty_helper_rows = 0

    for name in wb.sheetnames:
        # Skip non-batch sheets (evaluation profiles handled separately; protocol sheets ignored).
        if name in ("DIFF", ASSESS):
            continue
        ws = wb[name]
        lot = ws.cell(2, 2).value
        seed_no = ws.cell(2, 5).value
        yield_y30 = ws.cell(2, 8).value
        strain = ws.cell(3, 2).value
        seed_m3 = ws.cell(3, 5).value
        seed_y30 = ws.cell(4, 5).value

        records = []
        for r in range(6, ws.max_row + 1):
            t = ws.cell(r, 1).value
            if t is None:
                continue
            vals = [ws.cell(r, c).value for c in range(1, 15)]
            if not record_has_process_values(vals):
                if any(v is not None for v in vals[1:]):
                    dropped_empty_helper_rows += 1
                continue
            records.append(vals)

        air_n = sum(1 for v in records if v[1] is not None)
        complete = "full_process" if air_n >= 10 else "alcohol_sugar_biomass"
        notes = []
        if name == "05":
            notes.append(
                "volume_m3 values appear ~10x larger than peer batches; retained as recorded"
            )
        if lot == 2616:
            if complete == "full_process":
                notes.append(
                    "lot_no 2616 also appears as sparse batch B11 with the same yield header"
                )
            else:
                notes.append(
                    "same lot_no/yield header as full-process B10; treated as incomplete duplicate sheet"
                )
        if lot == 2642:
            notes.append("lot_no 2642 appears in more than one sheet")
        if yield_y30 is None:
            notes.append("yield_y30_kg missing in source sheet header")

        # Flag extreme early biomass in sparse sheets (likely digitization artefacts).
        for vals in records:
            bm = to_float(vals[6])
            t = to_float(vals[0])
            if bm is not None and t is not None and t <= 4 and bm > 60000:
                notes.append(
                    f"biomass_y30_kg={bm:.0f} at time_h={t:.0f} exceeds typical early-phase range; retained as recorded"
                )
                break

        times = [v[0] for v in records if isinstance(v[0], (int, float))]
        batch_id = f"B{name}"
        meta_rows.append(
            {
                "batch_id": batch_id,
                "lot_no": lot if lot is not None else "",
                "strain_id": strain if strain is not None else "",
                "seed_lot_no": seed_no if seed_no is not None else "",
                "seed_volume_m3": round_or_none(seed_m3, 4),
                "seed_y30_kg": round_or_none(seed_y30, 4),
                "yield_y30_kg": round_or_none(yield_y30, 4),
                "n_records": len(records),
                "time_start_h": min(times) if times else "",
                "time_end_h": max(times) if times else "",
                "data_completeness": complete,
                "has_process_variables": "yes" if complete == "full_process" else "no",
                "notes": "; ".join(notes),
            }
        )

        for vals in records:
            ts_rows.append(
                {
                    "batch_id": batch_id,
                    "lot_no": lot if lot is not None else "",
                    "time_h": vals[0],
                    "airflow_m3_h": round_or_none(vals[1], 3),
                    "volume_m3": round_or_none(vals[2], 4),
                    "ph": round_or_none(vals[3], 4),
                    "alcohol_vv_pct": round_or_none(vals[4], 6),
                    "cell_concentration_gpl": round_or_none(vals[5], 4),
                    "biomass_y30_kg": round_or_none(vals[6], 4),
                    "growth_modulus": round_or_none(vals[7], 6),
                    "sugar_feed_rate_kg_rs_h": round_or_none(vals[8], 4),
                    "total_fermentable_sugar_kg": round_or_none(vals[9], 4),
                    "remark": vals[10] if vals[10] is not None else "",
                    "delta_alcohol": round_or_none(vals[11], 6),
                    "delta_growth_modulus": round_or_none(vals[12], 6),
                    "auto_growth_modulus": round_or_none(vals[13], 6),
                }
            )

    # Flag end-of-batch airflow outliers on full-process sheets.
    for m in meta_rows:
        if m["data_completeness"] != "full_process":
            continue
        bid = m["batch_id"]
        hi = [
            r
            for r in ts_rows
            if r["batch_id"] == bid and to_float(r.get("airflow_m3_h")) is not None
            and to_float(r["airflow_m3_h"]) > 40000
        ]
        if hi:
            extra = (
                "airflow_m3_h > 40000 at end-of-batch hour(s); retained as recorded"
            )
            m["notes"] = f"{m['notes']}; {extra}" if m["notes"] else extra

    write_csv(OUT / "batch_metadata.csv", meta_fields, meta_rows)
    write_csv(OUT / "fermentation_timeseries.csv", ts_fields, ts_rows)

    # Evaluation / quality profiles
    ws = wb[ASSESS]
    prof = []
    for r in range(6, ws.max_row + 1):
        t = ws.cell(r, 12).value
        if t is None:
            continue
        prof.append(
            {
                "time_h": t,
                "alcohol_profile_vv_pct": round_or_none(ws.cell(r, 13).value, 6),
                "growth_modulus_profile": round_or_none(ws.cell(r, 14).value, 6),
            }
        )
    write_csv(
        OUT / "evaluation_profiles.csv",
        ["time_h", "alcohol_profile_vv_pct", "growth_modulus_profile"],
        prof,
    )

    full_ids = {m["batch_id"] for m in meta_rows if m["data_completeness"] == "full_process"}
    full_yield_meta = [
        {"batch_id": m["batch_id"], "yield_y30_kg": m["yield_y30_kg"]}
        for m in meta_rows
        if m["data_completeness"] == "full_process"
    ]

    def extreme_airflow(r):
        a = to_float(r.get("airflow_m3_h"))
        return a is not None and a > 40000

    summary = {
        "n_batches": len(meta_rows),
        "n_full_process_batches": len(full_ids),
        "n_sparse_batches": len(meta_rows) - len(full_ids),
        "n_timeseries_rows": len(ts_rows),
        "dropped_helper_only_rows": dropped_empty_helper_rows,
        "strain_ids": sorted({str(m["strain_id"]) for m in meta_rows if m["strain_id"] != ""}),
        "lot_no_min": min(int(m["lot_no"]) for m in meta_rows if m["lot_no"] != ""),
        "lot_no_max": max(int(m["lot_no"]) for m in meta_rows if m["lot_no"] != ""),
        "records_per_batch": sorted({m["n_records"] for m in meta_rows}),
        "missing_sugar_feed": {
            "n_missing": sum(1 for r in ts_rows if r["sugar_feed_rate_kg_rs_h"] == ""),
            "n_total": len(ts_rows),
            "note": "Most missing sugar-feed values occur at time_h=0 (feed not yet started).",
        },
        "descriptive_all": {
            k: describe(ts_rows, k)
            for k in [
                "airflow_m3_h",
                "volume_m3",
                "ph",
                "alcohol_vv_pct",
                "cell_concentration_gpl",
                "biomass_y30_kg",
                "growth_modulus",
                "sugar_feed_rate_kg_rs_h",
                "total_fermentable_sugar_kg",
            ]
        },
        "descriptive_full_process": {
            k: describe(ts_rows, k, full_ids)
            for k in [
                "airflow_m3_h",
                "volume_m3",
                "ph",
                "alcohol_vv_pct",
                "cell_concentration_gpl",
                "biomass_y30_kg",
                "growth_modulus",
                "sugar_feed_rate_kg_rs_h",
                "total_fermentable_sugar_kg",
            ]
        },
        "descriptive_full_process_sensitivity": {
            "volume_excluding_B05": describe(
                ts_rows, "volume_m3", full_ids, exclude_batch_ids={"B05"}
            ),
            "airflow_excluding_end_of_batch_gt_40000": describe(
                ts_rows,
                "airflow_m3_h",
                full_ids,
                exclude_predicate=extreme_airflow,
            ),
        },
        "yield_stats_full_process": describe(full_yield_meta, "yield_y30_kg"),
        "quality_flags": {
            "volume_anomaly_batches": ["B05"],
            "duplicate_lot_pairs": [["B10", "B11", 2616], ["B25", "B26", 2642]],
            "airflow_outlier_note": "B04/B09 end-of-batch airflow values >40000 m3/h retained as recorded",
            "sparse_biomass_extremes_note": "Some sparse batches contain early-phase biomass >60000 kg; flagged in batch notes",
        },
    }
    (OUT / "summary_stats.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Wrote {len(meta_rows)} batches, {len(ts_rows)} timeseries rows to {OUT}")
    print(f"Dropped helper-only rows: {dropped_empty_helper_rows}")
    print(f"Full-process batches: {sorted(full_ids)}")


if __name__ == "__main__":
    main()
