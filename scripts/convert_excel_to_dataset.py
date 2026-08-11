#!/usr/bin/env python3
"""Assemble digitized industrial yeast fermentation batch tables into publication-ready CSVs.

Primary scientific provenance is expert-completed PDF batch logs under dataset/raw_pdfs/.
This script only packages already-digitized tabular extracts into the public CSV layout.
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


def describe(rows, key, batch_ids=None):
    vals = []
    for r in rows:
        if batch_ids is not None and r["batch_id"] not in batch_ids:
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(SRC, data_only=True)

    meta_fields = [
        "batch_id",
        "lot_no",
        "strain_id",
        "recipe",
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

    for name in wb.sheetnames:
        if name in ("DIFF", ASSESS):
            continue
        ws = wb[name]
        lot = ws.cell(2, 2).value
        seed_no = ws.cell(2, 5).value
        yield_y30 = ws.cell(2, 8).value
        strain = ws.cell(3, 2).value
        seed_m3 = ws.cell(3, 5).value
        recipe = ws.cell(4, 2).value
        seed_y30 = ws.cell(4, 5).value

        records = []
        for r in range(6, ws.max_row + 1):
            t = ws.cell(r, 1).value
            if t is None:
                continue
            vals = [ws.cell(r, c).value for c in range(1, 15)]
            if all(v is None for v in vals[1:]):
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
            notes.append("lot_no 2616 appears in more than one sheet")
        if yield_y30 is None:
            notes.append("yield_y30_kg missing in source sheet header")

        times = [v[0] for v in records if isinstance(v[0], (int, float))]
        batch_id = f"B{name}"
        meta_rows.append(
            {
                "batch_id": batch_id,
                "lot_no": lot if lot is not None else "",
                "strain_id": strain if strain is not None else "",
                "recipe": recipe if recipe is not None else "",
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
    summary = {
        "n_batches": len(meta_rows),
        "n_full_process_batches": len(full_ids),
        "n_sparse_batches": len(meta_rows) - len(full_ids),
        "n_timeseries_rows": len(ts_rows),
        "strain_ids": sorted({str(m["strain_id"]) for m in meta_rows if m["strain_id"] != ""}),
        "recipes": sorted({str(m["recipe"]) for m in meta_rows if m["recipe"] != ""}),
        "lot_no_min": min(int(m["lot_no"]) for m in meta_rows if m["lot_no"] != ""),
        "lot_no_max": max(int(m["lot_no"]) for m in meta_rows if m["lot_no"] != ""),
        "records_per_batch": sorted({m["n_records"] for m in meta_rows}),
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
        "yield_stats": describe(
            [
                {
                    "batch_id": m["batch_id"],
                    "yield_y30_kg": m["yield_y30_kg"],
                }
                for m in meta_rows
            ],
            "yield_y30_kg",
        ),
    }
    (OUT / "summary_stats.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Wrote {len(meta_rows)} batches, {len(ts_rows)} timeseries rows to {OUT}")
    print(f"Full-process batches: {sorted(full_ids)}")


if __name__ == "__main__":
    main()
