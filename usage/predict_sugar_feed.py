#!/usr/bin/env python3
"""
Simple usage example: predict nutrient (sugar) feed rate from the released dataset.

Demonstrates dataset usability with a lightweight sequence model
(BiLSTM by default; optional 1D-CNN). No pandas/sklearn required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"

FEATURE_COLS = [
    "airflow_m3_h",
    "volume_m3",
    "ph",
    "alcohol_vv_pct",
    "cell_concentration_gpl",
    "biomass_y30_kg",
    "growth_modulus",
]
TARGET_COL = "sugar_feed_rate_kg_rs_h"


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(v: str | None) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


@dataclass
class WindowSample:
    x: np.ndarray  # (window, n_features)
    y: float
    batch_id: str
    time_h: float


def load_full_process_batches(exclude_batches: set[str] | None = None) -> dict[str, list[dict]]:
    exclude_batches = exclude_batches or set()
    meta = read_csv(DATASET / "batch_metadata.csv")
    full_ids = {
        r["batch_id"]
        for r in meta
        if r.get("data_completeness") == "full_process"
        and r["batch_id"] not in exclude_batches
    }
    rows = read_csv(DATASET / "fermentation_timeseries.csv")
    by_batch: dict[str, list[dict]] = {bid: [] for bid in sorted(full_ids)}
    for r in rows:
        bid = r["batch_id"]
        if bid not in by_batch:
            continue
        by_batch[bid].append(r)
    for bid in by_batch:
        by_batch[bid].sort(key=lambda r: float(r["time_h"]))
    return by_batch


def build_windows(by_batch: dict[str, list[dict]], window: int) -> list[WindowSample]:
    samples: list[WindowSample] = []
    for bid, rows in by_batch.items():
        feats, targets, times = [], [], []
        for r in rows:
            vals = [to_float(r.get(c)) for c in FEATURE_COLS]
            y = to_float(r.get(TARGET_COL))
            t = to_float(r.get("time_h"))
            if any(v is None for v in vals) or y is None or t is None:
                continue
            # Skip B05 volume anomaly scale issues by keeping raw values;
            # normalization is batch-agnostic min-max later.
            feats.append(vals)
            targets.append(y)
            times.append(t)
        if len(feats) < window:
            continue
        x = np.asarray(feats, dtype=np.float32)
        y_arr = np.asarray(targets, dtype=np.float32)
        for i in range(window - 1, len(x)):
            samples.append(
                WindowSample(
                    x=x[i - window + 1 : i + 1],
                    y=float(y_arr[i]),
                    batch_id=bid,
                    time_h=float(times[i]),
                )
            )
    return samples


def fit_scaler(samples: list[WindowSample]) -> tuple[np.ndarray, np.ndarray, float, float]:
    xs = np.stack([s.x for s in samples], axis=0)  # N,W,F
    ys = np.asarray([s.y for s in samples], dtype=np.float32)
    x_min = xs.reshape(-1, xs.shape[-1]).min(axis=0)
    x_max = xs.reshape(-1, xs.shape[-1]).max(axis=0)
    # Avoid zero range
    x_max = np.where(x_max - x_min < 1e-8, x_min + 1.0, x_max)
    y_min = float(ys.min())
    y_max = float(ys.max())
    if abs(y_max - y_min) < 1e-8:
        y_max = y_min + 1.0
    return x_min.astype(np.float32), x_max.astype(np.float32), y_min, y_max


def transform(
    samples: list[WindowSample],
    x_min: np.ndarray,
    x_max: np.ndarray,
    y_min: float,
    y_max: float,
) -> tuple[np.ndarray, np.ndarray]:
    x = np.stack([s.x for s in samples], axis=0)
    y = np.asarray([s.y for s in samples], dtype=np.float32)
    x_n = 2.0 * (x - x_min) / (x_max - x_min) - 1.0  # [-1, 1]
    y_n = 2.0 * (y - y_min) / (y_max - y_min) - 1.0
    return x_n.astype(np.float32), y_n.astype(np.float32)


def invert_y(y_n: np.ndarray, y_min: float, y_max: float) -> np.ndarray:
    return (y_n + 1.0) * 0.5 * (y_max - y_min) + y_min


class BiLSTMRegressor(nn.Module):
    def __init__(self, n_features: int, hidden: int = 64, layers: int = 1, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden,
            num_layers=layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden * 2, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last).squeeze(-1)


class CNN1DRegressor(nn.Module):
    def __init__(self, n_features: int, channels: int = 32, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(n_features, channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(channels, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: B,T,F -> B,F,T
        h = self.net(x.transpose(1, 2))
        return self.head(h).squeeze(-1)


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    err = y_pred - y_true
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    mape = float(np.mean(np.abs(err) / np.maximum(np.abs(y_true), 1.0)) * 100.0)
    ss_res = float(np.sum(err**2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else float("nan")
    return {"mae": mae, "rmse": rmse, "mape_pct": mape, "r2": r2}


def train_one(
    model: nn.Module,
    train_x: np.ndarray,
    train_y: np.ndarray,
    val_x: np.ndarray,
    val_y: np.ndarray,
    epochs: int,
    batch_size: int,
    lr: float,
    device: torch.device,
) -> nn.Module:
    model = model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = nn.MSELoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train_x), torch.from_numpy(train_y)),
        batch_size=batch_size,
        shuffle=True,
    )
    best_state = None
    best_val = math.inf
    patience, bad = 15, 0

    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            vx = torch.from_numpy(val_x).to(device)
            vy = torch.from_numpy(val_y).to(device)
            vloss = float(loss_fn(model(vx), vy).item())
        if vloss < best_val - 1e-6:
            best_val = vloss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model


def build_model(name: str, n_features: int) -> nn.Module:
    if name == "bilstm":
        return BiLSTMRegressor(n_features)
    if name == "cnn":
        return CNN1DRegressor(n_features)
    raise ValueError(f"Unknown model: {name}")


def load_evaluation_profiles() -> dict[float, dict[str, float | None]]:
    rows = read_csv(DATASET / "evaluation_profiles.csv")
    out: dict[float, dict[str, float | None]] = {}
    for r in rows:
        t = to_float(r.get("time_h"))
        if t is None:
            continue
        out[t] = {
            "alcohol_profile_vv_pct": to_float(r.get("alcohol_profile_vv_pct")),
            "growth_modulus_profile": to_float(r.get("growth_modulus_profile")),
        }
    return out


def alcohol_profile_tracking(exclude_batches: set[str] | None = None) -> dict:
    """Compare measured alcohol to evaluation_profiles.csv (uses that file explicitly)."""
    exclude_batches = exclude_batches or set()
    profiles = load_evaluation_profiles()
    meta = read_csv(DATASET / "batch_metadata.csv")
    full_ids = {
        r["batch_id"]
        for r in meta
        if r.get("data_completeness") == "full_process"
        and r["batch_id"] not in exclude_batches
    }
    rows = read_csv(DATASET / "fermentation_timeseries.csv")
    per_batch: list[dict] = []
    all_abs = []
    for bid in sorted(full_ids):
        errs = []
        for r in rows:
            if r["batch_id"] != bid:
                continue
            t = to_float(r.get("time_h"))
            a = to_float(r.get("alcohol_vv_pct"))
            if t is None or a is None or t not in profiles:
                continue
            pref = profiles[t]["alcohol_profile_vv_pct"]
            if pref is None:
                continue
            errs.append(abs(a - pref))
        if not errs:
            continue
        mae = float(np.mean(errs))
        per_batch.append({"batch_id": bid, "n": len(errs), "mae_alcohol_vv_pct": mae})
        all_abs.extend(errs)
    overall = {
        "n_points": len(all_abs),
        "n_batches": len(per_batch),
        "mae_alcohol_vv_pct": float(np.mean(all_abs)) if all_abs else float("nan"),
        "excluded_batches": sorted(exclude_batches),
        "batches": per_batch,
        "source_files": [
            "batch_metadata.csv",
            "fermentation_timeseries.csv",
            "evaluation_profiles.csv",
        ],
    }
    return overall


def run_lobo(args: argparse.Namespace) -> dict:
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    exclude = {b.strip() for b in args.exclude_batches.split(",") if b.strip()}
    by_batch = load_full_process_batches(exclude_batches=exclude)
    samples = build_windows(by_batch, args.window)
    batches = sorted({s.batch_id for s in samples})
    if len(batches) < 3:
        raise RuntimeError("Need at least 3 full-process batches with valid windows.")

    fold_rows = []
    all_true, all_pred = [], []

    for test_batch in batches:
        test_s = [s for s in samples if s.batch_id == test_batch]
        train_s = [s for s in samples if s.batch_id != test_batch]
        # small validation split from train batches
        train_batches = sorted({s.batch_id for s in train_s})
        val_batch = train_batches[-1]
        val_s = [s for s in train_s if s.batch_id == val_batch]
        fit_s = [s for s in train_s if s.batch_id != val_batch]

        x_min, x_max, y_min, y_max = fit_scaler(fit_s)
        tr_x, tr_y = transform(fit_s, x_min, x_max, y_min, y_max)
        va_x, va_y = transform(val_s, x_min, x_max, y_min, y_max)
        te_x, te_y = transform(test_s, x_min, x_max, y_min, y_max)

        model = build_model(args.model, n_features=len(FEATURE_COLS))
        model = train_one(
            model,
            tr_x,
            tr_y,
            va_x,
            va_y,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            device=device,
        )
        model.eval()
        with torch.no_grad():
            pred_n = model(torch.from_numpy(te_x).to(device)).cpu().numpy()
        pred = invert_y(pred_n, y_min, y_max)
        true = invert_y(te_y, y_min, y_max)
        m = metrics(true, pred)
        m["test_batch"] = test_batch
        m["n_test"] = int(len(true))
        fold_rows.append(m)
        all_true.append(true)
        all_pred.append(pred)
        print(
            f"[{args.model}] holdout {test_batch}: "
            f"MAE={m['mae']:.2f} RMSE={m['rmse']:.2f} "
            f"MAPE={m['mape_pct']:.2f}% R2={m['r2']:.3f} (n={m['n_test']})"
        )

    y_true = np.concatenate(all_true)
    y_pred = np.concatenate(all_pred)
    overall = metrics(y_true, y_pred)
    overall["n"] = int(len(y_true))
    overall["n_batches"] = len(batches)
    overall["model"] = args.model
    overall["window"] = args.window
    overall["features"] = FEATURE_COLS
    overall["target"] = TARGET_COL
    overall["excluded_batches"] = sorted(exclude)
    overall["fold_mean_mae"] = float(np.mean([f["mae"] for f in fold_rows]))
    overall["fold_mean_rmse"] = float(np.mean([f["rmse"] for f in fold_rows]))
    overall["fold_mean_mape_pct"] = float(np.mean([f["mape_pct"] for f in fold_rows]))
    overall["fold_mean_r2"] = float(np.mean([f["r2"] for f in fold_rows]))
    overall["folds"] = fold_rows

    print("\n=== Overall leave-one-batch-out ===")
    print(
        f"Model={args.model}  batches={overall['n_batches']}  samples={overall['n']}"
        + (f"  excluded={sorted(exclude)}" if exclude else "")
    )
    print(
        f"Pooled: MAE={overall['mae']:.2f} kg RS/h | "
        f"RMSE={overall['rmse']:.2f} | "
        f"MAPE={overall['mape_pct']:.2f}% | "
        f"R2={overall['r2']:.3f}"
    )
    print(
        f"Fold-mean: MAE={overall['fold_mean_mae']:.2f} | "
        f"RMSE={overall['fold_mean_rmse']:.2f} | "
        f"MAPE={overall['fold_mean_mape_pct']:.2f}% | "
        f"R2={overall['fold_mean_r2']:.3f}"
    )
    return overall


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sugar feed-rate prediction usage example")
    p.add_argument("--model", choices=["bilstm", "cnn"], default="bilstm")
    p.add_argument("--window", type=int, default=5, help="Sliding window length (hours)")
    p.add_argument("--epochs", type=int, default=80)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cpu", action="store_true")
    p.add_argument(
        "--exclude-batches",
        default="B05",
        help="Comma-separated batch IDs to exclude (default: B05 volume anomaly)",
    )
    p.add_argument(
        "--profile-only",
        action="store_true",
        help="Only compute alcohol vs evaluation_profiles.csv MAE (no model training)",
    )
    p.add_argument(
        "--skip-profile",
        action="store_true",
        help="Skip alcohol-profile tracking when training",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "usage" / "results" / "lobo_metrics.json",
    )
    p.add_argument(
        "--profile-out",
        type=Path,
        default=ROOT / "usage" / "results" / "alcohol_profile_mae.json",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    exclude = {b.strip() for b in args.exclude_batches.split(",") if b.strip()}

    if not args.skip_profile or args.profile_only:
        prof = alcohol_profile_tracking(exclude_batches=exclude)
        args.profile_out.write_text(json.dumps(prof, indent=2), encoding="utf-8")
        print(
            f"Alcohol vs evaluation_profiles: "
            f"MAE={prof['mae_alcohol_vv_pct']:.4f} v/v% "
            f"(n={prof['n_points']} points, {prof['n_batches']} batches)"
        )
        print(f"Saved profile metrics to {args.profile_out}")
        if args.profile_only:
            return

    result = run_lobo(args)
    payload = {k: v for k, v in result.items() if k != "folds"}
    payload["folds"] = result["folds"]
    payload["dataset_files_used"] = [
        "batch_metadata.csv",
        "fermentation_timeseries.csv",
        "evaluation_profiles.csv",
    ]
    payload["dataset_files_not_used"] = ["summary_stats.json", "README.md"]
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nSaved metrics to {args.out}")


if __name__ == "__main__":
    main()
