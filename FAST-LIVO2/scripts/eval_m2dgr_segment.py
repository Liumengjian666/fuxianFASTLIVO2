#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from typing import List, Tuple


def _split_tokens(line: str) -> List[str]:
    if "," in line:
        return [t.strip() for t in line.strip().split(",")]
    return re.split(r"\s+", line.strip())


def _try_parse_float_tokens(tokens: List[str]) -> List[float]:
    vals = []
    for t in tokens:
        if t == "":
            continue
        vals.append(float(t))
    return vals


def read_trajectory_like_file(path: str) -> List[Tuple[float, float, float, float, float, float, float, float]]:
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            tokens = _split_tokens(s)
            # Skip obvious non-data header lines.
            if len(tokens) < 4:
                continue
            try:
                vals = _try_parse_float_tokens(tokens)
            except ValueError:
                continue

            # Try common layouts:
            # 1) timestamp x y z qx qy qz qw (8)
            # 2) timestamp + many cols, pose starts from col 0 or 1
            if len(vals) >= 8:
                t, x, y, z, qx, qy, qz, qw = vals[:8]
                rows.append((t, x, y, z, qx, qy, qz, qw))
            elif len(vals) >= 4:
                # If no quaternion, pad identity quaternion.
                t, x, y, z = vals[:4]
                rows.append((t, x, y, z, 0.0, 0.0, 0.0, 1.0))

    if not rows:
        raise RuntimeError(f"No valid trajectory rows parsed from: {path}")

    # Heuristic: convert nanosecond timestamps to seconds.
    # Typical ROS sec timestamps are around 1e9; ns are around 1e18.
    first_t = rows[0][0]
    if first_t > 1e12:
        rows = [(t / 1e9, x, y, z, qx, qy, qz, qw) for t, x, y, z, qx, qy, qz, qw in rows]

    return rows


def write_tum(path: str, rows: List[Tuple[float, float, float, float, float, float, float, float]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("{:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f}\n".format(*r))


def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if p.returncode != 0:
        raise RuntimeError("Command failed:\n{}\n{}".format(" ".join(cmd), p.stdout))
    return p.stdout


def extract_rmse(evo_output: str) -> float:
    for line in evo_output.splitlines():
        if "rmse" in line.lower():
            parts = line.strip().split()
            if parts:
                try:
                    return float(parts[-1])
                except ValueError:
                    continue
    raise RuntimeError("Failed to parse RMSE from evo output")


def main() -> int:
    parser = argparse.ArgumentParser(description="Crop M2DGR GT to estimate time window and compute ATE/RPE.")
    parser.add_argument("--gt", required=True, help="Path to M2DGR GT file (txt/csv).")
    parser.add_argument(
        "--est",
        default="/home/liumengjian/catkin_ws/src/FAST-LIVO2/Log/result/M2DGR_lift04.txt",
        help="Path to estimated trajectory in TUM-like format.",
    )
    parser.add_argument(
        "--out-prefix",
        default="/home/liumengjian/catkin_ws/src/FAST-LIVO2/Log/result/M2DGR_lift04",
        help="Output prefix for converted/cropped files.",
    )
    parser.add_argument("--t-margin", type=float, default=0.0, help="Time margin (seconds) for GT crop window.")
    args = parser.parse_args()

    if not os.path.exists(args.gt):
        raise FileNotFoundError(f"GT file not found: {args.gt}")
    if not os.path.exists(args.est):
        raise FileNotFoundError(f"EST file not found: {args.est}")

    est_rows = read_trajectory_like_file(args.est)
    gt_rows = read_trajectory_like_file(args.gt)

    t0 = est_rows[0][0] - args.t_margin
    t1 = est_rows[-1][0] + args.t_margin

    gt_crop = [r for r in gt_rows if t0 <= r[0] <= t1]
    if len(gt_crop) < 5:
        raise RuntimeError(
            "Too few GT rows after crop. Check timestamp units / timezone / wrong GT file. "
            f"window=[{t0:.6f}, {t1:.6f}], kept={len(gt_crop)}"
        )

    os.makedirs(os.path.dirname(args.out_prefix), exist_ok=True)

    gt_tum = args.out_prefix + "_gt_tum.txt"
    gt_crop_tum = args.out_prefix + "_gt_crop.txt"
    est_tum = args.out_prefix + "_est_tum.txt"

    write_tum(gt_tum, gt_rows)
    write_tum(gt_crop_tum, gt_crop)
    write_tum(est_tum, est_rows)

    ape_out = run_cmd([
        sys.executable,
        "-m",
        "evo.main_ape",
        "tum",
        gt_crop_tum,
        est_tum,
        "-a",
    ])
    rpe_out = run_cmd([
        sys.executable,
        "-m",
        "evo.main_rpe",
        "tum",
        gt_crop_tum,
        est_tum,
        "-a",
        "--pose_relation",
        "trans_part",
    ])

    ape_rmse = extract_rmse(ape_out)
    rpe_rmse = extract_rmse(rpe_out)

    print("[INFO] EST time window: {:.6f} -> {:.6f} ({} poses)".format(est_rows[0][0], est_rows[-1][0], len(est_rows)))
    print("[INFO] GT kept in window: {} / {}".format(len(gt_crop), len(gt_rows)))
    print("[INFO] GT TUM: {}".format(gt_tum))
    print("[INFO] GT cropped: {}".format(gt_crop_tum))
    print("[INFO] EST TUM: {}".format(est_tum))
    print("[RESULT] APE_RMSE(m): {:.6f}".format(ape_rmse))
    print("[RESULT] RPE_RMSE(m): {:.6f}".format(rpe_rmse))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
