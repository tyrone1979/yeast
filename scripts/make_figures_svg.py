#!/usr/bin/env python3
"""Generate SVG figures without matplotlib."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

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


def svg_header(w, h):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]


def mapx(x, xmin, xmax, left, right):
    if xmax == xmin:
        return left
    return left + (x - xmin) / (xmax - xmin) * (right - left)


def mapy(y, ymin, ymax, top, bottom):
    if ymax == ymin:
        return top
    return bottom - (y - ymin) / (ymax - ymin) * (bottom - top)


def polyline(points, color, width=1.5, dash=None):
    if len(points) < 2:
        return ""
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash_attr}/>'


def axis(left, right, top, bottom, xmin, xmax, ymin, ymax, xlabel, ylabel, title):
    parts = []
    parts.append(
        f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="none" stroke="#333"/>'
    )
    parts.append(
        f'<text x="{(left+right)/2:.1f}" y="24" text-anchor="middle" font-family="Arial" font-size="15" fill="#111">{title}</text>'
    )
    parts.append(
        f'<text x="{(left+right)/2:.1f}" y="{bottom+36}" text-anchor="middle" font-family="Arial" font-size="12" fill="#222">{xlabel}</text>'
    )
    parts.append(
        f'<text x="22" y="{(top+bottom)/2:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#222" transform="rotate(-90 22 {(top+bottom)/2:.1f})">{ylabel}</text>'
    )
    for i in range(5):
        x = xmin + i * (xmax - xmin) / 4
        px = mapx(x, xmin, xmax, left, right)
        parts.append(f'<line x1="{px:.1f}" y1="{bottom}" x2="{px:.1f}" y2="{bottom+4}" stroke="#333"/>')
        parts.append(
            f'<text x="{px:.1f}" y="{bottom+18}" text-anchor="middle" font-family="Arial" font-size="10">{x:.0f}</text>'
        )
        y = ymin + i * (ymax - ymin) / 4
        py = mapy(y, ymin, ymax, top, bottom)
        parts.append(f'<line x1="{left-4}" y1="{py:.1f}" x2="{left}" y2="{py:.1f}" stroke="#333"/>')
        parts.append(
            f'<text x="{left-8}" y="{py+3:.1f}" text-anchor="end" font-family="Arial" font-size="10">{y:.2g}</text>'
        )
    return parts


def save(path, lines):
    path.write_text("\n".join(lines + ["</svg>"]), encoding="utf-8")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    meta = load_csv(DATA / "batch_metadata.csv")
    ts = load_csv(DATA / "fermentation_timeseries.csv")
    prof = load_csv(DATA / "evaluation_profiles.csv")
    sp = load_csv(DATA / "protocol_hourly_setpoints.csv")
    full_ids = [m["batch_id"] for m in meta if m["data_completeness"] == "full_process"]
    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    # Fig1 sugar feed
    w, h = 900, 520
    left, right, top, bottom = 70, 860, 50, 430
    lines = svg_header(w, h)
    all_x, all_y = [], []
    series = []
    for i, bid in enumerate(full_ids):
        pts = []
        for r in ts:
            if r["batch_id"] != bid:
                continue
            x, y = fnum(r["time_h"]), fnum(r["sugar_feed_rate_kg_rs_h"])
            if x is not None and y is not None:
                pts.append((x, y))
                all_x.append(x)
                all_y.append(y)
        series.append((bid, pts, colors[i % len(colors)]))
    px, py = [], []
    for r in sp:
        x, y = fnum(r["brew_hour"]), fnum(r["sugar_feed_rate_kg_rs_h"])
        if x is not None and y is not None:
            px.append(x)
            py.append(y)
            all_x.append(x)
            all_y.append(y)
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = 0, max(all_y) * 1.05
    lines += axis(
        left,
        right,
        top,
        bottom,
        xmin,
        xmax,
        ymin,
        ymax,
        "Fermentation time (h)",
        "Sugar feed rate (kg RS / h)",
        "Measured sugar feed trajectories vs protocol setpoint",
    )
    for bid, pts, col in series:
        mapped = [
            (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
            for x, y in pts
        ]
        lines.append(polyline(mapped, col, 1.4))
    mapped = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(px, py)
    ]
    lines.append(polyline(mapped, "#000000", 2.2, dash="6 4"))
    # legend
    lx, ly = 80, 460
    for i, (bid, _, col) in enumerate(series):
        x0 = lx + (i % 5) * 150
        y0 = ly + (i // 5) * 18
        lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+22}" y2="{y0}" stroke="{col}" stroke-width="2"/>')
        lines.append(
            f'<text x="{x0+28}" y="{y0+4}" font-family="Arial" font-size="11">{bid}</text>'
        )
    lines.append(
        f'<line x1="{lx}" y1="{ly+40}" x2="{lx+22}" y2="{ly+40}" stroke="#000" stroke-width="2" stroke-dasharray="6 4"/>'
    )
    lines.append(
        f'<text x="{lx+28}" y="{ly+44}" font-family="Arial" font-size="11">Protocol setpoint</text>'
    )
    save(FIG / "fig1_sugar_feed_trajectories.svg", lines)

    # Fig2 alcohol/biomass B01
    rows = [r for r in ts if r["batch_id"] == "B01"]
    t = [fnum(r["time_h"]) for r in rows]
    alc = [fnum(r["alcohol_vv_pct"]) for r in rows]
    bio = [fnum(r["biomass_y30_kg"]) for r in rows]
    pt = [fnum(r["time_h"]) for r in prof]
    palc = [fnum(r["alcohol_profile_vv_pct"]) for r in prof]
    w, h = 900, 500
    left, right, top, bottom = 70, 780, 50, 430
    lines = svg_header(w, h)
    xmin, xmax = 0, max(max(t), max(pt))
    ymin, ymax = 0, max(v for v in alc + palc if v is not None) * 1.15
    lines += axis(
        left,
        right,
        top,
        bottom,
        xmin,
        xmax,
        ymin,
        ymax,
        "Fermentation time (h)",
        "Alcohol (v/v %)",
        "Representative batch alcohol–biomass dynamics (B01)",
    )
    mapped = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(t, alc)
        if x is not None and y is not None
    ]
    lines.append(polyline(mapped, "#1f4e79", 2))
    mapped = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(pt, palc)
        if x is not None and y is not None
    ]
    lines.append(polyline(mapped, "#c55a11", 2, dash="5 3"))
    # right axis for biomass
    bmin, bmax = 0, max(v for v in bio if v is not None) * 1.05
    for i in range(5):
        yv = bmin + i * (bmax - bmin) / 4
        py = mapy(yv, bmin, bmax, top, bottom)
        lines.append(f'<line x1="{right}" y1="{py:.1f}" x2="{right+4}" y2="{py:.1f}" stroke="#548235"/>')
        lines.append(
            f'<text x="{right+8}" y="{py+3:.1f}" font-family="Arial" font-size="10" fill="#548235">{yv:.0f}</text>'
        )
    lines.append(
        f'<text x="{right+55}" y="{(top+bottom)/2:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#548235" transform="rotate(90 {right+55} {(top+bottom)/2:.1f})">Biomass Y30 (kg)</text>'
    )
    mapped = [
        (
            mapx(x, xmin, xmax, left, right),
            mapy(y, bmin, bmax, top, bottom),
        )
        for x, y in zip(t, bio)
        if x is not None and y is not None
    ]
    lines.append(polyline(mapped, "#548235", 2))
    lines.append('<line x1="80" y1="460" x2="105" y2="460" stroke="#1f4e79" stroke-width="2"/>')
    lines.append('<text x="110" y="464" font-family="Arial" font-size="11">Alcohol (B01)</text>')
    lines.append(
        '<line x1="250" y1="460" x2="275" y2="460" stroke="#c55a11" stroke-width="2" stroke-dasharray="5 3"/>'
    )
    lines.append(
        '<text x="280" y="464" font-family="Arial" font-size="11">Alcohol evaluation profile</text>'
    )
    lines.append('<line x1="520" y1="460" x2="545" y2="460" stroke="#548235" stroke-width="2"/>')
    lines.append('<text x="550" y="464" font-family="Arial" font-size="11">Biomass Y30 (B01)</text>')
    save(FIG / "fig2_alcohol_biomass_b01.svg", lines)

    # Fig3 mean pH and airflow
    by_time = defaultdict(lambda: {"ph": [], "air": []})
    for r in ts:
        if r["batch_id"] not in full_ids:
            continue
        tv = fnum(r["time_h"])
        if tv is None:
            continue
        ph = fnum(r["ph"])
        air = fnum(r["airflow_m3_h"])
        if ph is not None:
            by_time[tv]["ph"].append(ph)
        if air is not None:
            by_time[tv]["air"].append(air)
    times = sorted(by_time)
    ph_mean = [sum(by_time[t]["ph"]) / len(by_time[t]["ph"]) for t in times if by_time[t]["ph"]]
    times_ph = [t for t in times if by_time[t]["ph"]]
    air_mean = [sum(by_time[t]["air"]) / len(by_time[t]["air"]) for t in times if by_time[t]["air"]]
    times_air = [t for t in times if by_time[t]["air"]]
    w, h = 900, 500
    left, right, top, bottom = 70, 780, 50, 430
    lines = svg_header(w, h)
    xmin, xmax = min(times), max(times)
    ymin, ymax = min(ph_mean) - 0.2, max(ph_mean) + 0.2
    lines += axis(
        left,
        right,
        top,
        bottom,
        xmin,
        xmax,
        ymin,
        ymax,
        "Fermentation time (h)",
        "pH",
        "Mean pH and airflow across full-process batches",
    )
    mapped = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(times_ph, ph_mean)
    ]
    lines.append(polyline(mapped, "#7030a0", 2))
    amin, amax = min(air_mean) * 0.9, max(air_mean) * 1.05
    for i in range(5):
        yv = amin + i * (amax - amin) / 4
        py = mapy(yv, amin, amax, top, bottom)
        lines.append(f'<line x1="{right}" y1="{py:.1f}" x2="{right+4}" y2="{py:.1f}" stroke="#2e75b6"/>')
        lines.append(
            f'<text x="{right+8}" y="{py+3:.1f}" font-family="Arial" font-size="10" fill="#2e75b6">{yv:.0f}</text>'
        )
    lines.append(
        f'<text x="{right+55}" y="{(top+bottom)/2:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#2e75b6" transform="rotate(90 {right+55} {(top+bottom)/2:.1f})">Airflow (m3/h)</text>'
    )
    mapped = [
        (mapx(x, xmin, xmax, left, right), mapy(y, amin, amax, top, bottom))
        for x, y in zip(times_air, air_mean)
    ]
    lines.append(polyline(mapped, "#2e75b6", 2))
    lines.append('<line x1="80" y1="460" x2="105" y2="460" stroke="#7030a0" stroke-width="2"/>')
    lines.append('<text x="110" y="464" font-family="Arial" font-size="11">Mean pH</text>')
    lines.append('<line x1="220" y1="460" x2="245" y2="460" stroke="#2e75b6" stroke-width="2"/>')
    lines.append('<text x="250" y="464" font-family="Arial" font-size="11">Mean airflow</text>')
    save(FIG / "fig3_mean_ph_airflow.svg", lines)

    # Fig4 histogram
    feeds = [fnum(r["sugar_feed_rate_kg_rs_h"]) for r in ts]
    feeds = [v for v in feeds if v is not None]
    bins = 24
    fmin, fmax = min(feeds), max(feeds)
    width = (fmax - fmin) / bins if fmax > fmin else 1
    counts = [0] * bins
    for v in feeds:
        idx = int((v - fmin) / width) if width else 0
        if idx == bins:
            idx = bins - 1
        counts[idx] += 1
    w, h = 820, 480
    left, right, top, bottom = 70, 780, 50, 400
    lines = svg_header(w, h)
    xmin, xmax = fmin, fmax
    ymin, ymax = 0, max(counts) * 1.1
    lines += axis(
        left,
        right,
        top,
        bottom,
        xmin,
        xmax,
        ymin,
        ymax,
        "Sugar feed rate (kg RS / h)",
        "Count",
        "Distribution of recorded sugar feed rates (all batches)",
    )
    bw = (right - left) / bins
    for i, c in enumerate(counts):
        x0 = left + i * bw
        y0 = mapy(c, ymin, ymax, top, bottom)
        lines.append(
            f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{bw-1:.2f}" height="{bottom-y0:.2f}" fill="#5b9bd5" stroke="white"/>'
        )
    save(FIG / "fig4_sugar_feed_hist.svg", lines)
    print("SVG figures written to", FIG)


if __name__ == "__main__":
    main()
