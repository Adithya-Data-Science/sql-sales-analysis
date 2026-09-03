"""Create reproducible community-engagement KPI outputs from a CSV file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REQUIRED = {
    "record_id",
    "reporting_period",
    "participant_department",
    "partnership_type",
    "impact_area",
    "satisfaction_score",
    "funding_amount",
    "student_volunteers",
}


def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["reporting_period"])
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df["record_id"].isna().any() or df["record_id"].duplicated().any():
        raise ValueError("record_id must be present and unique")
    if not df["satisfaction_score"].dropna().between(1, 5).all():
        raise ValueError("satisfaction_score must be between 1 and 5")
    if (df[["funding_amount", "student_volunteers"]].fillna(0) < 0).any().any():
        raise ValueError("funding and volunteer values cannot be negative")
    return df


def build_outputs(df: pd.DataFrame, output_dir: Path) -> dict[str, float | int]:
    output_dir.mkdir(parents=True, exist_ok=True)

    participants = df.groupby("participant_department").size().rename("participants")
    partnerships = df.groupby("partnership_type").size().rename("partnerships")
    satisfaction = df.groupby("impact_area")["satisfaction_score"].mean().round(2)
    funding = df.groupby("impact_area")["funding_amount"].sum().round(2)
    volunteers = int(df["student_volunteers"].fillna(0).sum())

    participants.to_csv(output_dir / "participants_by_department.csv")
    partnerships.to_csv(output_dir / "partnerships_by_type.csv")
    satisfaction.to_csv(output_dir / "satisfaction_by_impact_area.csv")
    funding.to_csv(output_dir / "funding_by_impact_area.csv")

    plt.figure(figsize=(6, 4))
    partnerships.plot.pie(autopct="%1.0f%%", ylabel="")
    plt.title("Partnerships by Type")
    plt.tight_layout()
    plt.savefig(output_dir / "partnership_mix.png", dpi=150)
    plt.close()

    trend = df.groupby(df["reporting_period"].dt.to_period("M"))["student_volunteers"].sum()
    trend.index = trend.index.astype(str)
    plt.figure(figsize=(7, 4))
    trend.plot(marker="o")
    plt.title("Student Volunteers by Reporting Period")
    plt.xlabel("Reporting Period")
    plt.ylabel("Student Volunteers")
    plt.tight_layout()
    plt.savefig(output_dir / "volunteer_trend.png", dpi=150)
    plt.close()

    summary = {
        "records": int(len(df)),
        "departments": int(df["participant_department"].nunique()),
        "partnership_types": int(df["partnership_type"].nunique()),
        "impact_areas": int(df["impact_area"].nunique()),
        "average_satisfaction": round(float(df["satisfaction_score"].mean()), 2),
        "total_funding": round(float(df["funding_amount"].sum()), 2),
        "student_volunteers": volunteers,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_outputs(load_and_validate(args.input_csv), args.output_dir), indent=2))


if __name__ == "__main__":
    main()
