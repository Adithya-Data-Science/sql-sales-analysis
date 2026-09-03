"""Validate survey data and produce stakeholder-ready summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def analyze(input_csv: Path, output_dir: Path) -> dict[str, float | int]:
    df = pd.read_csv(input_csv)
    required = {"response_id", "department", "channel", "satisfaction", "completed"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df["response_id"].isna().any() or df["response_id"].duplicated().any():
        raise ValueError("response_id must be present and unique")

    df["department"] = df["department"].str.strip().str.title()
    df["channel"] = df["channel"].str.strip().str.title()
    df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
    if not df["satisfaction"].dropna().between(1, 5).all():
        raise ValueError("satisfaction must be between 1 and 5")

    output_dir.mkdir(parents=True, exist_ok=True)
    completed = df["completed"].astype(bool)
    valid_scores = df["satisfaction"].dropna()
    summary = {
        "responses": int(len(df)),
        "completion_rate_pct": round(float(completed.mean() * 100), 1),
        "average_satisfaction": round(float(valid_scores.mean()), 2),
        "positive_response_rate_pct": round(float((valid_scores >= 4).mean() * 100), 1),
        "missing_satisfaction_values": int(df["satisfaction"].isna().sum()),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    charts = [
        (df["department"].value_counts(), "Responses by Department", "department_responses.png"),
        (valid_scores.value_counts().sort_index(), "Satisfaction Distribution", "satisfaction_distribution.png"),
        (df["channel"].value_counts(), "Responses by Channel", "channel_responses.png"),
    ]
    for series, title, filename in charts:
        plt.figure(figsize=(6, 4))
        series.plot.bar(color="#24476b")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_dir / filename, dpi=150)
        plt.close()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.input_csv, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
