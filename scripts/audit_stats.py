#!/usr/bin/env python3
"""Recompute and audit dataset statistics for consistency / reasonableness."""

from __future__ import annotations

import csv
import json
import statistics as stats
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def f(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def describe(rows, key, pred=None):
    vals = []
    for r in rows:
        if pred and not pred(r):
            continue
        v = f(r.get(key))
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


def main():
    meta = list(csv.DictReader((ROOT / "dataset/batch_metadata.csv").open(encoding="utf-8")))
    ts = list(
        csv.DictReader((ROOT / "dataset/fermentation_timeseries.csv").open(encoding="utf-8"))
    )
    prof = list(
        csv.DictReader((ROOT / "dataset/evaluation_profiles.csv").open(encoding="utf-8"))
    )
    summary = json.loads((ROOT / "dataset/summary_stats.json").read_text(encoding="utf-8"))
    paper = (ROOT / "paper/yeast_fermentation_dataset_DataInBrief.md").read_text(encoding="utf-8")

    issues: list[str] = []
    ok: list[str] = []

    n_meta, n_ts = len(meta), len(ts)
    sum_n = sum(int(m["n_records"]) for m in meta)
    full = [m for m in meta if m["data_completeness"] == "full_process"]
    sparse = [m for m in meta if m["data_completeness"] == "alcohol_sugar_biomass"]
    full_ids = {m["batch_id"] for m in full}

    print("=== COUNTS ===")
    print(f"meta={n_meta} ts={n_ts} sum(n_records)={sum_n}")
    print(f"full={len(full)} sparse={len(sparse)}")
    print(
        "summary:",
        summary["n_batches"],
        summary["n_timeseries_rows"],
        summary["n_full_process_batches"],
        summary["n_sparse_batches"],
    )

    if n_meta != 61:
        issues.append(f"meta count {n_meta} != 61")
    else:
        ok.append("61 batches")
    if n_ts != sum_n:
        issues.append(f"ts rows {n_ts} != sum n_records {sum_n}")
    else:
        ok.append("n_records sum matches timeseries")
    if n_ts != summary["n_timeseries_rows"]:
        issues.append("summary n_timeseries_rows mismatch")
    else:
        ok.append("summary row count matches")
    if len(full) != 10 or len(sparse) != 51:
        issues.append(f"completeness split {len(full)}/{len(sparse)}")
    else:
        ok.append("10/51 completeness split")

    if "recipe" in meta[0]:
        issues.append("recipe column still present in metadata")
    else:
        ok.append("no recipe column")

    for name in ["batch_metadata.csv", "fermentation_timeseries.csv", "summary_stats.json"]:
        txt = (ROOT / "dataset" / name).read_text(encoding="utf-8")
        if "Diff" in txt or "DIFF" in txt:
            issues.append(f"Diff/DIFF still in {name}")
    if not any("Diff" in i or "DIFF" in i for i in issues):
        ok.append("no Diff in released CSV/JSON")

    if (ROOT / "dataset/raw_pdfs").exists():
        issues.append("raw_pdfs still exists")
    else:
        ok.append("raw_pdfs removed")

    by_batch: dict[str, list] = defaultdict(list)
    for r in ts:
        by_batch[r["batch_id"]].append(r)

    for m in meta:
        bid = m["batch_id"]
        rows = by_batch[bid]
        if len(rows) != int(m["n_records"]):
            issues.append(f"{bid}: n_records {m['n_records']} != actual {len(rows)}")
        times = [f(r["time_h"]) for r in rows]
        if len(times) != len(set(times)):
            issues.append(f"{bid}: duplicate time_h")
        if times != sorted(times):
            issues.append(f"{bid}: time_h not sorted/monotonic")
        if times:
            if int(float(m["time_start_h"])) != int(min(times)) or int(
                float(m["time_end_h"])
            ) != int(max(times)):
                issues.append(
                    f"{bid}: time range meta {m['time_start_h']}-{m['time_end_h']} "
                    f"vs {min(times)}-{max(times)}"
                )

    proc_cols = [
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
    helper_only = sum(1 for r in ts if all(r.get(c, "") == "" for c in proc_cols))
    if helper_only:
        issues.append(f"{helper_only} helper-only rows remain")
    else:
        ok.append("no helper-only rows")

    b02 = next(m for m in meta if m["batch_id"] == "B02")
    if int(b02["n_records"]) != 17 or int(float(b02["time_end_h"])) != 16:
        issues.append(f"B02 unexpected: n={b02['n_records']} end={b02['time_end_h']}")
    else:
        ok.append("B02 empty row removed (n=17, end=16)")

    print("\n=== DESCRIPTIVE RECOMPUTE vs summary_stats ===")
    keys = [
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
    for section, pred in [
        ("descriptive_all", None),
        ("descriptive_full_process", lambda r: r["batch_id"] in full_ids),
    ]:
        for k in keys:
            a = describe(ts, k, pred)
            b = summary[section].get(k)
            if a != b:
                issues.append(f"{section}.{k}: recomputed {a} != summary {b}")
        if not any(section in i for i in issues):
            ok.append(f"{section} matches recompute")

    vol_ex = describe(
        ts, "volume_m3", lambda r: r["batch_id"] in full_ids and r["batch_id"] != "B05"
    )
    air_ex = describe(
        ts,
        "airflow_m3_h",
        lambda r: r["batch_id"] in full_ids
        and not (f(r["airflow_m3_h"]) is not None and f(r["airflow_m3_h"]) > 40000),
    )
    if vol_ex != summary["descriptive_full_process_sensitivity"]["volume_excluding_B05"]:
        issues.append(f"volume sensitivity mismatch {vol_ex}")
    else:
        ok.append("volume excl B05 sensitivity OK")
    if (
        air_ex
        != summary["descriptive_full_process_sensitivity"][
            "airflow_excluding_end_of_batch_gt_40000"
        ]
    ):
        issues.append(f"airflow sensitivity mismatch {air_ex}")
    else:
        ok.append("airflow excl >40k sensitivity OK")

    yield_vals = [f(m["yield_y30_kg"]) for m in full if f(m["yield_y30_kg"]) is not None]
    ys = {
        "n": len(yield_vals),
        "mean": round(sum(yield_vals) / len(yield_vals), 4),
        "std": round(stats.pstdev(yield_vals), 4),
        "min": round(min(yield_vals), 4),
        "max": round(max(yield_vals), 4),
    }
    if ys != summary["yield_stats_full_process"]:
        issues.append(f"yield mismatch {ys} vs {summary['yield_stats_full_process']}")
    else:
        ok.append("yield n=10 full-process OK")

    b11y = f(next(m for m in meta if m["batch_id"] == "B11")["yield_y30_kg"])
    b10y = f(next(m for m in meta if m["batch_id"] == "B10")["yield_y30_kg"])
    if b11y == b10y and ys["n"] == 10:
        ok.append("B11 yield present but excluded from yield_stats")

    sugar_miss = sum(1 for r in ts if r["sugar_feed_rate_kg_rs_h"] == "")
    alc_miss = sum(1 for r in ts if r["alcohol_vv_pct"] == "")
    sugar_miss_t0 = sum(
        1 for r in ts if r["sugar_feed_rate_kg_rs_h"] == "" and f(r["time_h"]) == 0
    )
    print("\n=== MISSINGNESS ===")
    print(
        f"sugar_miss={sugar_miss}/{n_ts} ({100 * sugar_miss / n_ts:.2f}%) "
        f"of which t=0: {sugar_miss_t0}"
    )
    print(f"alcohol_miss={alc_miss}/{n_ts}")
    if sugar_miss != summary["missing_sugar_feed"]["n_missing"]:
        issues.append("missing sugar count mismatch summary")
    else:
        ok.append("missing sugar count matches summary")
    if sugar_miss_t0 < sugar_miss * 0.9:
        issues.append(f"sugar missing not mostly t=0 ({sugar_miss_t0}/{sugar_miss})")
    else:
        ok.append("sugar missing mostly at t=0")

    print("\n=== FULL-PROCESS COVERAGE ===")
    for k in keys:
        n = sum(1 for r in ts if r["batch_id"] in full_ids and r.get(k, "") != "")
        print(f"  {k}: {n}")

    gm_miss_full = [
        (r["batch_id"], r["time_h"])
        for r in ts
        if r["batch_id"] in full_ids and r["growth_modulus"] == ""
    ]
    t0 = sum(1 for _, t in gm_miss_full if f(t) == 0)
    print(f"GM missing full: {len(gm_miss_full)} (t=0: {t0})")
    if t0 == 10 and len(gm_miss_full) == 10:
        ok.append("GM missing only at t=0 for all 10 full batches")
    else:
        issues.append(
            f"GM missing pattern unexpected: {len(gm_miss_full)} total, {t0} at t=0"
        )

    sugar_miss_full = [
        (r["batch_id"], r["time_h"])
        for r in ts
        if r["batch_id"] in full_ids and r["sugar_feed_rate_kg_rs_h"] == ""
    ]
    print(f"sugar missing full: {len(sugar_miss_full)} -> {sugar_miss_full}")

    print("\n=== OUTLIERS / REASONABLENESS ===")
    vol_b05 = [f(r["volume_m3"]) for r in ts if r["batch_id"] == "B05" and r["volume_m3"] != ""]
    vol_other = [
        f(r["volume_m3"])
        for r in ts
        if r["batch_id"] in full_ids - {"B05"} and r["volume_m3"] != ""
    ]
    print(f"B05 volume: {min(vol_b05):.1f}-{max(vol_b05):.1f}")
    print(f"other full volume: {min(vol_other):.1f}-{max(vol_other):.1f}")
    if min(vol_b05) > 5 * max(vol_other):
        ok.append("B05 volume ~10x peers (flagged)")

    air_hi = [
        (r["batch_id"], r["time_h"], f(r["airflow_m3_h"]))
        for r in ts
        if f(r["airflow_m3_h"]) and f(r["airflow_m3_h"]) > 40000
    ]
    print("airflow>40k:", air_hi)
    if len(air_hi) == 2 and {a[0] for a in air_hi} == {"B04", "B09"}:
        ok.append("exactly 2 airflow outliers B04/B09")
    else:
        issues.append(f"unexpected airflow outliers {air_hi}")

    strains = set(m["strain_id"] for m in meta)
    if strains != {"167"}:
        issues.append(f"strains {strains}")
    else:
        ok.append("all strain 167")

    lots = Counter(m["lot_no"] for m in meta)
    dup_lots = {k: v for k, v in lots.items() if v > 1}
    print("duplicate lots:", dup_lots)

    print("\n=== PAPER NUMBER CHECKS ===")
    for needle, bad_if_found, label in [
        ("1,128", True, "stale 1128"),
        ("raw_pdfs", True, "raw_pdfs mention"),
        ("62/1,128", True, "stale sugar miss"),
        ("Diff", True, "Diff in paper"),
        ("1,127", False, "updated 1127"),
        ("61/1,127", False, "updated sugar miss"),
        ("115.4", False, "volume sensitivity"),
        ("16080.6", False, "airflow sensitivity"),
        ("39009.2", False, "yield mean"),
    ]:
        found = needle in paper
        print(f"  {label}: {found}")
        if bad_if_found and found:
            issues.append(f"paper still has '{needle}'")
        if not bad_if_found and not found:
            issues.append(f"paper missing '{needle}'")

    fp = summary["descriptive_full_process"]
    pairs = [
        ("airflow", fp["airflow_m3_h"], 179, 16459.2, 5748.3, 4961, 49992),
        ("volume", fp["volume_m3"], 179, 219.9, 319.5, 87.7, 1470),
        ("ph", fp["ph"], 179, 5.77, 1.07, 3.91, 7.75),
        ("alcohol", fp["alcohol_vv_pct"], 179, 0.103, 0.071, 0.002, 0.393),
        ("cell", fp["cell_concentration_gpl"], 179, 206.3, 80.1, 57, 300),
        ("biomass", fp["biomass_y30_kg"], 179, 25346.4, 13016.4, 5056, 44253),
        ("gm", fp["growth_modulus"], 169, 1.135, 0.097, 1.00, 1.56),
        ("sugar", fp["sugar_feed_rate_kg_rs_h"], 169, 1342.7, 518.8, 127, 2194),
    ]
    for name, d, n, mean, sd, mn, mx in pairs:
        deltas = (
            abs(d["mean"] - mean),
            abs(d["std"] - sd),
            abs(d["min"] - mn),
            abs(d["max"] - mx),
        )
        print(
            f"  T5 {name}: n={d['n']} mean={d['mean']} (paper {mean}) "
            f"dmean={deltas[0]:.4f} dstd={deltas[1]:.4f}"
        )
        if d["n"] != n:
            issues.append(f"Table5 {name} n paper/summary mismatch")
        tol_mean = 0.05 if mean >= 1 else 0.0015
        tol_std = 0.05 if mean >= 1 else 0.0015
        if deltas[0] > tol_mean or deltas[1] > tol_std:
            issues.append(f"Table5 {name} mean/std rounding off vs paper")
        if abs(d["min"] - mn) > 0.01 or abs(d["max"] - mx) > 0.01:
            issues.append(f"Table5 {name} min/max mismatch")
        else:
            ok.append(f"Table5 {name} OK")

    alld = summary["descriptive_all"]
    t6 = [
        ("alcohol", alld["alcohol_vv_pct"], 1127, 0.104, 0.061, 0.001, 0.393),
        ("biomass", alld["biomass_y30_kg"], 1127, 25562.1, 13250.1, 1417, 71101),
        ("sugar", alld["sugar_feed_rate_kg_rs_h"], 1066, 1300.5, 478.2, 127, 2194),
    ]
    for name, d, n, mean, sd, mn, mx in t6:
        print(f"  T6 {name}: n={d['n']} mean={d['mean']} (paper {mean})")
        if d["n"] != n:
            issues.append(f"T6 {name} n")
        tol = 0.05 if mean >= 1 else 0.0015
        if abs(d["mean"] - mean) > tol or abs(d["std"] - sd) > tol:
            issues.append(f"T6 {name} mean/std vs paper")
        if abs(d["min"] - mn) > 0.01 or abs(d["max"] - mx) > 0.01:
            issues.append(f"T6 {name} min/max vs paper")
        else:
            ok.append(f"Table6 {name} OK")

    print("\n=== PROFILES ===")
    print(f"profile rows={len(prof)} times={[r['time_h'] for r in prof]}")
    gm_prof_empty = sum(1 for r in prof if r["growth_modulus_profile"] == "")
    alc_prof_empty = sum(1 for r in prof if r["alcohol_profile_vv_pct"] == "")
    print(f"profile empty GM={gm_prof_empty} alcohol={alc_prof_empty}")
    if gm_prof_empty == 1 and f(prof[0]["time_h"]) == 0:
        ok.append("GM profile empty only at t=0")
    elif gm_prof_empty:
        issues.append(f"unexpected empty GM profile cells: {gm_prof_empty}")

    print("\n=== PHYSICAL RANGES ===")
    checks_r = {
        "ph": (3, 9),
        "alcohol_vv_pct": (0, 1),
        "growth_modulus": (0.5, 3),
        "sugar_feed_rate_kg_rs_h": (0, 5000),
        "airflow_m3_h": (0, 60000),
        "volume_m3": (0, 2000),
        "cell_concentration_gpl": (0, 500),
    }
    for k, (lo, hi) in checks_r.items():
        vals = [f(r[k]) for r in ts if r.get(k, "") != ""]
        bad = [v for v in vals if v < lo or v > hi]
        if bad:
            issues.append(f"{k}: {len(bad)} values outside [{lo},{hi}] e.g. {bad[:3]}")
        else:
            ok.append(f"{k} within [{lo},{hi}]")

    early_hi = [
        (r["batch_id"], r["time_h"], f(r["biomass_y30_kg"]))
        for r in ts
        if f(r["time_h"]) is not None
        and f(r["time_h"]) <= 4
        and f(r["biomass_y30_kg"])
        and f(r["biomass_y30_kg"]) > 60000
    ]
    print("early biomass>60k:", early_hi)
    flagged = [
        m["batch_id"]
        for m in meta
        if "biomass_y30_kg=" in m["notes"] and "exceeds" in m["notes"]
    ]
    print("flagged biomass batches:", flagged)
    if set(b[0] for b in early_hi) <= set(flagged):
        ok.append("early biomass extremes flagged")
    else:
        issues.append(
            f"unflagged early biomass extremes: {set(b[0] for b in early_hi) - set(flagged)}"
        )

    # full-process process-var n should now be consistent (179) after B02 drop
    air_n = sum(1 for r in ts if r["batch_id"] in full_ids and r["airflow_m3_h"] != "")
    full_rows = sum(1 for r in ts if r["batch_id"] in full_ids)
    print(f"\nfull rows={full_rows}, airflow n={air_n}")
    if full_rows == air_n == 179:
        ok.append("full-process rows == airflow n == 179 (consistent)")
    else:
        issues.append(f"full rows/airflow inconsistent: {full_rows}/{air_n}")

    rpb = sorted({int(m["n_records"]) for m in meta})
    if rpb != summary["records_per_batch"]:
        issues.append(f"records_per_batch {rpb} vs {summary['records_per_batch']}")
    else:
        ok.append("records_per_batch OK")

    lots_i = [int(m["lot_no"]) for m in meta]
    if min(lots_i) != summary["lot_no_min"] or max(lots_i) != summary["lot_no_max"]:
        issues.append("lot range mismatch")
    else:
        ok.append(f"lot range {min(lots_i)}-{max(lots_i)}")

    # Abstract / Table3 records range
    if "17 to 21" in paper or "17–21" in paper or "17 to 21" in paper:
        ok.append("paper records-per-batch range stated")
    # After B02, min is still 17
    if min(int(m["n_records"]) for m in meta) != 17:
        issues.append("min records != 17")

    # Root/dataset README consistency
    root = (ROOT / "README.md").read_text(encoding="utf-8")
    ds = (ROOT / "dataset/README.md").read_text(encoding="utf-8")
    for label, txt in [("root README", root), ("dataset README", ds)]:
        if "1,128" in txt or "1128" in txt:
            issues.append(f"{label} still has 1128")
        if "raw_pdfs" in txt:
            issues.append(f"{label} still mentions raw_pdfs")
        if "1,127" in txt or "1127" in txt:
            ok.append(f"{label} has 1127")

    print("\n========== OK ==========")
    for x in ok:
        print(" +", x)
    print("\n========== ISSUES ==========")
    if not issues:
        print(" (none)")
    else:
        for x in issues:
            print(" !", x)
    print(f"\n{len(ok)} ok, {len(issues)} issues")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
