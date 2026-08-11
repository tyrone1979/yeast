#!/usr/bin/env python3
"""Generate descriptive figures for the yeast fermentation dataset paper."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset"
FIG = DATA / "figures"


def load_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    meta = load_csv(DATA / "batch_metadata.csv")
    ts = load_csv(DATA / "fermentation_timeseries.csv")
    prof = load_csv(DATA / "evaluation_profiles.csv")
    sp = load_csv(DATA / "protocol_hourly_setpoints.csv")

    full_ids = [m["batch_id"] for m in meta if m["data_completeness"] == "full_process"]

    # Fig 1: sugar feed rate trajectories for full-process batches
    plt.figure(figsize=(8.2, 4.8))
    for bid in full_ids:
        rows = [r for r in ts if r["batch_id"] == bid]
        x, y = [], []
        for r in rows:
            xv, yv = fnum(r["time_h"]), fnum(r["sugar_feed_rate_kg_rs_h"])
            if xv is not None and yv is not None:
                x.append(xv)
                y.append(yv)
        if x:
            plt.plot(x, y, marker="o", markersize=3, linewidth=1.2, label=bid)
    # protocol setpoint overlay
    px, py = [], []
    for r in sp:
        xv, yv = fnum(r["brew_hour"]), fnum(r["sugar_feed_rate_kg_rs_h"])
        if xv is not None and yv is not None:
            px.append(xv)
            py.append(yv)
    if px:
        plt.plot(px, py, "k--", linewidth=2.0, label="Protocol setpoint")
    plt.xlabel("Fermentation time (h)")
    plt.ylabel("Sugar feed rate (kg RS / h)")
    plt.title("Measured sugar feed trajectories vs protocol setpoint")
    plt.legend(ncol=3, fontsize=8, frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "fig1_sugar_feed_trajectories.png", dpi=300)
    plt.close()

    # Fig 2: alcohol and biomass for one representative full batch + profile
    bid = "B01"
    rows = [r for r in ts if r["batch_id"] == bid]
    t = [fnum(r["time_h"]) for r in rows]
    alc = [fnum(r["alcohol_vv_pct"]) for r in rows]
    bio = [fnum(r["biomass_y30_kg"]) for r in rows]
    pt = [fnum(r["time_h"]) for r in prof]
    palc = [fnum(r["alcohol_profile_vv_pct"]) for r in prof]

    fig, ax1 = plt.subplots(figsize=(8.2, 4.6))
    ax1.plot(t, alc, "o-", color="#1f4e79", label="Alcohol (B01)")
    ax1.plot(pt, palc, "s--", color="#c55a11", label="Alcohol evaluation profile")
    ax1.set_xlabel("Fermentation time (h)")
    ax1.set_ylabel("Alcohol (v/v %)")
    ax2 = ax1.twinx()
    ax2.plot(t, bio, "^-", color="#548235", label="Biomass Y30 (B01)")
    ax2.set_ylabel("Biomass Y30 (kg)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)
    ax1.set_title("Representative batch alcohol–biomass dynamics (B01)")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_alcohol_biomass_b01.png", dpi=300)
    plt.close(fig)

    # Fig 3: pH and airflow for full-process batches (mean +/- across batches)
    by_time = defaultdict(lambda: {"ph": [], "air": []})
    for r in ts:
        if r["batch_id"] not in full_ids:
            continue
        tval = fnum(r["time_h"])
        if tval is None:
            continue
        ph = fnum(r["ph"])
        air = fnum(r["airflow_m3_h"])
        if ph is not None:
            by_time[tval]["ph"].append(ph)
        if air is not None:
            by_time[tval]["air"].append(air)
    times = sorted(by_time)
    ph_mean = [sum(by_time[t]["ph"]) / len(by_time[t]["ph"]) for t in times]
    air_mean = [sum(by_time[t]["air"]) / len(by_time[t]["air"]) for t in times]

    fig, ax1 = plt.subplots(figsize=(8.2, 4.6))
    ax1.plot(times, ph_mean, "o-", color="#7030a0", label="Mean pH (full-process)")
    ax1.set_xlabel("Fermentation time (h)")
    ax1.set_ylabel("pH")
    ax2 = ax1.twinx()
    ax2.plot(times, air_mean, "d-", color="#2e75b6", label="Mean airflow")
    ax2.set_ylabel("Airflow (m$^3$/h)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best", frameon=False)
    ax1.set_title("Mean pH and airflow across full-process batches")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_mean_ph_airflow.png", dpi=300)
    plt.close(fig)

    # Fig 4: distribution of sugar feed rates (all available)
    feeds = [fnum(r["sugar_feed_rate_kg_rs_h"]) for r in ts]
    feeds = [v for v in feeds if v is not None]
    plt.figure(figsize=(7.2, 4.4))
    plt.hist(feeds, bins=30, color="#5b9bd5", edgecolor="white")
    plt.xlabel("Sugar feed rate (kg RS / h)")
    plt.ylabel("Count")
    plt.title("Distribution of recorded sugar feed rates (all batches)")
    plt.tight_layout()
    plt.savefig(FIG / "fig4_sugar_feed_hist.png", dpi=300)
    plt.close()

    print("Figures written to", FIG)


if __name__ == "__main__":
    main()
