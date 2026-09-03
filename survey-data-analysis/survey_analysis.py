"""Object-oriented survey validation and stakeholder reporting application."""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

@dataclass(frozen=True)
class SurveySchema:
    required_columns: frozenset[str] = frozenset(
        {"response_id", "department", "channel", "satisfaction", "completed"}
    )
    satisfaction_min: int = 1
    satisfaction_max: int = 5
    positive_threshold: int = 4

class SurveyDataValidator:
    """Load, standardize and validate survey responses before analysis."""
    def __init__(self, schema: SurveySchema | None = None) -> None:
        self.schema = schema or SurveySchema()

    def load(self, input_csv: Path) -> pd.DataFrame:
        return pd.read_csv(input_csv)

    def clean_and_validate(self, raw: pd.DataFrame) -> pd.DataFrame:
        missing = self.schema.required_columns.difference(raw.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        df = raw.copy()
        if df["response_id"].isna().any() or df["response_id"].duplicated().any():
            raise ValueError("response_id must be present and unique")
        for column in ("department", "channel"):
            df[column] = df[column].astype("string").str.strip().str.title()
            if df[column].isna().any() or df[column].eq("").any():
                raise ValueError(f"{column} must be present")
        df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
        valid_scores = df["satisfaction"].dropna()
        if not valid_scores.between(
            self.schema.satisfaction_min, self.schema.satisfaction_max
        ).all():
            raise ValueError(
                f"satisfaction must be between {self.schema.satisfaction_min} "
                f"and {self.schema.satisfaction_max}"
            )
        normalized = df["completed"].astype("string").str.strip().str.lower()
        if not normalized.isin({"true", "false"}).all():
            raise ValueError("completed must contain only true or false values")
        df["completed"] = normalized.eq("true")
        return df

class SurveyKPIAnalyzer:
    """Calculate four stakeholder KPIs plus a transparent quality count."""
    def __init__(self, positive_threshold: int = 4) -> None:
        self.positive_threshold = positive_threshold

    def calculate(self, df: pd.DataFrame) -> dict[str, float | int]:
        valid_scores = df["satisfaction"].dropna()
        return {
            "responses": int(len(df)),
            "completion_rate_pct": round(float(df["completed"].mean() * 100), 1),
            "average_satisfaction": round(float(valid_scores.mean()), 2),
            "positive_response_rate_pct": round(
                float((valid_scores >= self.positive_threshold).mean() * 100), 1
            ),
            "missing_satisfaction_values": int(df["satisfaction"].isna().sum()),
        }

class StakeholderReportGenerator:
    """Write machine-readable KPI output and three presentation-ready charts."""
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def write(self, df: pd.DataFrame, summary: dict[str, float | int]) -> list[Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = self.output_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        valid_scores = df["satisfaction"].dropna()
        charts = [
            (df["department"].value_counts(), "Responses by Department", "department_responses.png"),
            (valid_scores.value_counts().sort_index(), "Satisfaction Distribution", "satisfaction_distribution.png"),
            (df["channel"].value_counts(), "Responses by Channel", "channel_responses.png"),
        ]
        paths = [summary_path]
        for series, title, filename in charts:
            path = self.output_dir / filename
            fig, ax = plt.subplots(figsize=(6, 4))
            series.plot.bar(ax=ax, color="#24476b")
            ax.set_title(title)
            ax.set_xlabel("")
            fig.tight_layout()
            fig.savefig(path, dpi=150)
            plt.close(fig)
            paths.append(path)
        return paths

class SurveyReportingApplication:
    """Coordinate ingestion, validation, analysis and reporting."""
    def __init__(
        self,
        validator: SurveyDataValidator | None = None,
        analyzer: SurveyKPIAnalyzer | None = None,
    ) -> None:
        self.validator = validator or SurveyDataValidator()
        self.analyzer = analyzer or SurveyKPIAnalyzer(
            self.validator.schema.positive_threshold
        )

    def run(self, input_csv: Path, output_dir: Path) -> dict[str, float | int]:
        raw = self.validator.load(input_csv)
        clean = self.validator.clean_and_validate(raw)
        summary = self.analyzer.calculate(clean)
        StakeholderReportGenerator(output_dir).write(clean, summary)
        return summary

def analyze(input_csv: Path, output_dir: Path) -> dict[str, float | int]:
    """Backward-compatible entry point used by notebooks and scripts."""
    return SurveyReportingApplication().run(input_csv, output_dir)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.input_csv, args.output_dir), indent=2))

if __name__ == "__main__":
    main()
