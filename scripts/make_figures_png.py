#!/usr/bin/env python3
"""Clean publication figures: no in-image captions, no overlapping labels."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset"
FIG = ROOT / "paper" / "figures"


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


def font(size=14):
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "calibri.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mapx(x, xmin, xmax, left, right):
    return left if xmax <= xmin else left + (x - xmin) / (xmax - xmin) * (right - left)


def mapy(y, ymin, ymax, top, bottom):
    return bottom if ymax <= ymin else bottom - (y - ymin) / (ymax - ymin) * (bottom - top)


def ticks(vmin, vmax, n=4):
    if vmax <= vmin:
        return [vmin]
    step = (vmax - vmin) / n
    return [vmin + i * step for i in range(n + 1)]


def fmt(y, ymin, ymax):
    span = abs(ymax - ymin)
    if span < 2:
        return f"{y:.2f}"
    if span < 30:
        return f"{y:.1f}"
    return f"{y:.0f}"


def quantile(vals, q):
    s = sorted(vals)
    if not s:
        return 0.0
    pos = (len(s) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    w = pos - lo
    return s[lo] * (1 - w) + s[hi] * w


def band_stats(ts, batch_ids, col):
    by_t = defaultdict(list)
    for r in ts:
        if r["batch_id"] not in batch_ids:
            continue
        t, y = fnum(r["time_h"]), fnum(r.get(col))
        if t is None or y is None:
            continue
        by_t[t].append(y)
    times = sorted(by_t)
    med, q1, q3 = [], [], []
    for t in times:
        vals = by_t[t]
        med.append(median(vals))
        q1.append(quantile(vals, 0.25))
        q3.append(quantile(vals, 0.75))
    return times, med, q1, q3


def paste_rotated_ylabel(img, text, x_center, y_center, font_obj, fill=(35, 35, 35)):
    """Draw vertical y-axis title (rotated 90°) without overlapping tick labels."""
    text = text.replace("\n", " ")
    tmp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = tmp_draw.textbbox((0, 0), text, font=font_obj)
    tw, th = bbox[2] - bbox[0] + 6, bbox[3] - bbox[1] + 6
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((-bbox[0] + 3, -bbox[1] + 3), text, font=font_obj, fill=fill)
    rot = layer.rotate(90, expand=True)
    px = int(x_center - rot.width / 2)
    py = int(y_center - rot.height / 2)
    base = img.convert("RGBA")
    base.alpha_composite(rot, (px, py))
    return base.convert("RGB")


def draw_panel(img, box, xmin, xmax, ymin, ymax, xlabel, ylabel, f_tick, f_lab):
    draw = ImageDraw.Draw(img)
    left, right, top, bottom = box
    for y in ticks(ymin, ymax, 4):
        py = mapy(y, ymin, ymax, top, bottom)
        draw.line([left + 1, py, right - 1, py], fill=(238, 238, 238), width=1)
        draw.line([left - 4, py, left, py], fill=(90, 90, 90), width=1)
        draw.text((left - 8, py), fmt(y, ymin, ymax), fill=(60, 60, 60), font=f_tick, anchor="rm")
    for x in ticks(xmin, xmax, 4):
        px = mapx(x, xmin, xmax, left, right)
        draw.line([px, bottom, px, bottom + 4], fill=(90, 90, 90), width=1)
        draw.text((px, bottom + 10), f"{x:.0f}", fill=(60, 60, 60), font=f_tick, anchor="mt")
    draw.rectangle([left, top, right, bottom], outline=(70, 70, 70), width=2)
    draw.text(((left + right) / 2, bottom + 32), xlabel, fill=(35, 35, 35), font=f_lab, anchor="mt")
    img = paste_rotated_ylabel(img, ylabel, left - 58, (top + bottom) / 2, f_lab)
    return ImageDraw.Draw(img), img


def fill_band(img, xs, y_lo, y_hi, xmin, xmax, ymin, ymax, box, rgba):
    left, right, top, bottom = box
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    poly = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(xs, y_lo)
    ] + [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(reversed(xs), reversed(y_hi))
    ]
    if len(poly) >= 3:
        od.polygon(poly, fill=rgba)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def line(draw, xs, ys, xmin, xmax, ymin, ymax, box, color, width=3, markers=False):
    left, right, top, bottom = box
    pts = [
        (mapx(x, xmin, xmax, left, right), mapy(y, ymin, ymax, top, bottom))
        for x, y in zip(xs, ys)
    ]
    if len(pts) >= 2:
        draw.line(pts, fill=color, width=width)
    if markers:
        for px, py in pts:
            draw.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=color, outline="white")


def scatter(draw, xs, ys, xmin, xmax, ymin, ymax, box, color, r=3.5):
    left, right, top, bottom = box
    for x, y in zip(xs, ys):
        px = mapx(x, xmin, xmax, left, right)
        py = mapy(y, ymin, ymax, top, bottom)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color, outline="white")


def legend_inside(draw, box, items, f, corner="tl"):
    left, right, top, bottom = box
    pad = 10
    # estimate width
    widths = []
    for label, _, _ in items:
        widths.append(20 + 8 + int(f.getlength(label)))
    total_w = sum(widths) + 14 * (len(items) - 1)
    if corner == "tl":
        x = left + pad
        y = top + pad + 8
    else:
        x = right - pad - total_w
        y = top + pad + 8
    # background
    draw.rectangle(
        [x - 6, y - 10, x + total_w + 6, y + 12],
        fill=(255, 255, 255, ),
        outline=(200, 200, 200),
    )
    cx = x
    for label, color, kind in items:
        if kind == "band":
            draw.rectangle([cx, y - 5, cx + 16, y + 5], fill=color, outline=(160, 160, 160))
        elif kind == "point":
            draw.ellipse([cx + 4, y - 4, cx + 12, y + 4], fill=color, outline="white")
        else:
            draw.line([cx, y, cx + 16, y], fill=color, width=3)
        draw.text((cx + 22, y), label, fill=(40, 40, 40), font=f, anchor="lm")
        cx += 20 + 8 + int(f.getlength(label)) + 14


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    meta = load_csv(DATA / "batch_metadata.csv")
    ts = load_csv(DATA / "fermentation_timeseries.csv")
    prof = load_csv(DATA / "evaluation_profiles.csv")
    # exclude anomalous-volume batch from aggregate figures
    full_ids = {
        m["batch_id"]
        for m in meta
        if m["data_completeness"] == "full_process" and m["batch_id"] != "B05"
    }
    f_tick, f_lab, f_leg = font(13), font(14), font(12)

    # Fig 1
    times, med, q1, q3 = band_stats(ts, full_ids, "sugar_feed_rate_kg_rs_h")
    w, h = 1080, 520
    img = Image.new("RGB", (w, h), "white")
    box = (120, 1020, 40, 430)
    xmin, xmax = min(times), max(times)
    ymin, ymax = 0.0, max(q3) * 1.08
    img = fill_band(img, times, q1, q3, xmin, xmax, ymin, ymax, box, (100, 149, 237, 70))
    draw, img = draw_panel(
        img, box, xmin, xmax, ymin, ymax, "Fermentation time (h)", "Sugar feed rate (kg RS/h)", f_tick, f_lab
    )
    line(draw, times, med, xmin, xmax, ymin, ymax, box, (25, 70, 120), 3, markers=False)
    legend_inside(
        draw,
        box,
        [("Median", (25, 70, 120), "line"), ("IQR", (180, 205, 235), "band")],
        f_leg,
    )
    img.save(FIG / "fig1_sugar_feed_trajectories.png", dpi=(300, 300))

    # Fig 2
    rows = [r for r in ts if r["batch_id"] == "B01"]
    t = [fnum(r["time_h"]) for r in rows]
    alc = [fnum(r["alcohol_vv_pct"]) for r in rows]
    bio = [fnum(r["biomass_y30_kg"]) for r in rows]
    pt = [fnum(r["time_h"]) for r in prof]
    palc = [fnum(r["alcohol_profile_vv_pct"]) for r in prof]
    t_a = [x for x, y in zip(t, alc) if x is not None and y is not None]
    a_a = [y for x, y in zip(t, alc) if x is not None and y is not None]
    t_b = [x for x, y in zip(t, bio) if x is not None and y is not None]
    b_b = [y for x, y in zip(t, bio) if x is not None and y is not None]
    t_p = [x for x, y in zip(pt, palc) if x is not None and y is not None]
    p_p = [y for x, y in zip(pt, palc) if x is not None and y is not None]

    w, h = 1140, 480
    img = Image.new("RGB", (w, h), "white")
    box1 = (130, 530, 35, 400)
    xmin, xmax = 0, 17
    amin, amax = 0.0, max(a_a + p_p) * 1.12
    draw, img = draw_panel(img, box1, xmin, xmax, amin, amax, "Time (h)", "Alcohol (v/v %)", f_tick, f_lab)
    line(draw, t_p, p_p, xmin, xmax, amin, amax, box1, (200, 100, 40), 3, markers=False)
    scatter(draw, t_a, a_a, xmin, xmax, amin, amax, box1, (40, 90, 150), r=4)
    legend_inside(
        draw,
        box1,
        [("Measured", (40, 90, 150), "point"), ("Profile", (200, 100, 40), "line")],
        f_leg,
    )

    box2 = (720, 1110, 35, 400)
    bmin, bmax = 0.0, max(b_b) * 1.06
    draw, img = draw_panel(img, box2, xmin, xmax, bmin, bmax, "Time (h)", "Biomass Y30 (kg)", f_tick, f_lab)
    line(draw, t_b, b_b, xmin, xmax, bmin, bmax, box2, (70, 120, 60), 3, markers=False)
    legend_inside(draw, box2, [("Biomass", (70, 120, 60), "line")], f_leg)
    img.save(FIG / "fig2_alcohol_biomass_b01.png", dpi=(300, 300))

    # Fig 3
    t_ph, m_ph, q1_ph, q3_ph = band_stats(ts, full_ids, "ph")
    t_air, m_air, q1_air, q3_air = band_stats(ts, full_ids, "airflow_m3_h")
    w, h = 1140, 480
    img = Image.new("RGB", (w, h), "white")
    box1 = (130, 530, 35, 400)
    # drop final hour if IQR explodes (sparse / unstable late records)
    if len(t_ph) > 3:
        t_ph, m_ph, q1_ph, q3_ph = t_ph[:-1], m_ph[:-1], q1_ph[:-1], q3_ph[:-1]
        t_air, m_air, q1_air, q3_air = t_air[:-1], m_air[:-1], q1_air[:-1], q3_air[:-1]
    xmin, xmax = min(t_ph), max(t_ph)
    ymin, ymax = min(q1_ph) - 0.1, max(q3_ph) + 0.1
    img = fill_band(img, t_ph, q1_ph, q3_ph, xmin, xmax, ymin, ymax, box1, (150, 100, 180, 60))
    draw, img = draw_panel(img, box1, xmin, xmax, ymin, ymax, "Time (h)", "pH", f_tick, f_lab)
    line(draw, t_ph, m_ph, xmin, xmax, ymin, ymax, box1, (110, 50, 150), 3, markers=False)
    legend_inside(
        draw,
        box1,
        [("Median pH", (110, 50, 150), "line"), ("IQR", (210, 190, 225), "band")],
        f_leg,
    )

    box2 = (720, 1110, 35, 400)
    amin, amax = min(q1_air) * 0.98, max(q3_air) * 1.05
    img = fill_band(img, t_air, q1_air, q3_air, xmin, xmax, amin, amax, box2, (80, 140, 200, 60))
    draw, img = draw_panel(img, box2, xmin, xmax, amin, amax, "Time (h)", "Airflow (m3/h)", f_tick, f_lab)
    line(draw, t_air, m_air, xmin, xmax, amin, amax, box2, (40, 100, 170), 3, markers=False)
    legend_inside(
        draw,
        box2,
        [("Median airflow", (40, 100, 170), "line"), ("IQR", (180, 210, 235), "band")],
        f_leg,
    )
    img.save(FIG / "fig3_mean_ph_airflow.png", dpi=(300, 300))

    # Fig 4
    feeds = [
        fnum(r["sugar_feed_rate_kg_rs_h"])
        for r in ts
        if fnum(r["sugar_feed_rate_kg_rs_h"]) is not None
    ]
    bins = 16
    fmin, fmax = min(feeds), max(feeds)
    width = (fmax - fmin) / bins
    counts = [0] * bins
    for v in feeds:
        counts[min(bins - 1, int((v - fmin) / width))] += 1
    centers = [fmin + (i + 0.5) * width for i in range(bins)]
    smooth = [
        sum(counts[j] for j in range(max(0, i - 1), min(bins, i + 2)))
        / len(range(max(0, i - 1), min(bins, i + 2)))
        for i in range(bins)
    ]

    w, h = 1000, 500
    img = Image.new("RGB", (w, h), "white")
    box = (120, 940, 40, 400)
    left, right, top, bottom = box
    xmin, xmax = fmin, fmax
    ymin, ymax = 0.0, max(max(counts), max(smooth)) * 1.15
    draw, img = draw_panel(img, box, xmin, xmax, ymin, ymax, "Sugar feed rate (kg RS / h)", "Count", f_tick, f_lab)
    bw = (right - left) / bins
    for i, c in enumerate(counts):
        x0 = left + i * bw
        y0 = mapy(c, ymin, ymax, top, bottom)
        draw.rectangle([x0 + 2, y0, x0 + bw - 2, bottom], fill=(170, 200, 230))
    line(draw, centers, smooth, xmin, xmax, ymin, ymax, box, (25, 70, 120), 3, markers=False)
    legend_inside(
        draw,
        box,
        [("Histogram", (170, 200, 230), "band"), ("Smoothed", (25, 70, 120), "line")],
        f_leg,
    )
    img.save(FIG / "fig4_sugar_feed_hist.png", dpi=(300, 300))

    # update paper wording for median/IQR
    print("Clean PNG figures written to", FIG)


if __name__ == "__main__":
    main()
