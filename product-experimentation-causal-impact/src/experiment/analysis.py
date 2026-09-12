"""Statistical analysis and decision report for the onboarding experiment."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2, norm, ttest_ind
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "experiment_users.csv"
OUTPUT_DIR = ROOT / "outputs"


def required_sample_size(baseline: float = 0.40, mde: float = 0.02, alpha: float = 0.05, power: float = 0.80) -> int:
    effect = proportion_effectsize(baseline + mde, baseline)
    per_arm = NormalIndPower().solve_power(effect_size=effect, alpha=alpha, power=power, ratio=1.0)
    return int(np.ceil(per_arm))


def validate_data(df: pd.DataFrame) -> None:
    required = {
        "user_id", "treatment", "device", "channel", "prior_activity", "activated_7d",
        "support_contact_7d", "transaction_latency_ms", "pre_engagement", "post_engagement",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["user_id"].duplicated().any():
        raise ValueError("Randomization unit user_id must be unique")
    if not set(df["treatment"].unique()).issubset({0, 1}):
        raise ValueError("treatment must be binary")
    if df[list(required)].isna().any().any():
        raise ValueError("Analysis columns cannot contain missing values")


def sample_ratio_mismatch(df: pd.DataFrame) -> dict:
    counts = df["treatment"].value_counts().reindex([0, 1], fill_value=0)
    expected = len(df) / 2
    statistic = float(((counts - expected) ** 2 / expected).sum())
    return {"control_n": int(counts[0]), "treatment_n": int(counts[1]), "p_value": float(chi2.sf(statistic, 1))}


def proportion_effect(df: pd.DataFrame, outcome: str) -> dict:
    grouped = df.groupby("treatment")[outcome].agg(["sum", "count", "mean"]).reindex([0, 1])
    count = np.array([grouped.loc[1, "sum"], grouped.loc[0, "sum"]])
    nobs = np.array([grouped.loc[1, "count"], grouped.loc[0, "count"]])
    z_stat, p_value = proportions_ztest(count, nobs)
    p1, p0 = grouped.loc[1, "mean"], grouped.loc[0, "mean"]
    difference = float(p1 - p0)
    standard_error = float(np.sqrt(p1 * (1 - p1) / nobs[0] + p0 * (1 - p0) / nobs[1]))
    return {
        "control_rate": float(p0), "treatment_rate": float(p1), "absolute_effect": difference,
        "relative_lift": float(difference / p0), "ci_low": difference - 1.96 * standard_error,
        "ci_high": difference + 1.96 * standard_error, "p_value": float(p_value), "z_stat": float(z_stat),
    }


def mean_effect(df: pd.DataFrame, outcome: str) -> dict:
    control = df.loc[df.treatment == 0, outcome]
    treated = df.loc[df.treatment == 1, outcome]
    result = ttest_ind(treated, control, equal_var=False)
    difference = float(treated.mean() - control.mean())
    se = float(np.sqrt(treated.var(ddof=1) / len(treated) + control.var(ddof=1) / len(control)))
    return {"control_mean": float(control.mean()), "treatment_mean": float(treated.mean()), "absolute_effect": difference,
            "ci_low": difference - 1.96 * se, "ci_high": difference + 1.96 * se, "p_value": float(result.pvalue)}


def regression_adjusted_effect(df: pd.DataFrame) -> dict:
    model = smf.ols("activated_7d ~ treatment + prior_activity + C(device) + C(channel)", data=df).fit(cov_type="HC3")
    return {"coefficient": float(model.params["treatment"]), "standard_error": float(model.bse["treatment"]),
            "ci_low": float(model.conf_int().loc["treatment", 0]), "ci_high": float(model.conf_int().loc["treatment", 1]),
            "p_value": float(model.pvalues["treatment"])}


def difference_in_differences(df: pd.DataFrame) -> dict:
    long = df.melt(id_vars=["user_id", "treatment"], value_vars=["pre_engagement", "post_engagement"],
                   var_name="period", value_name="engagement")
    long["post"] = (long["period"] == "post_engagement").astype(int)
    model = smf.ols("engagement ~ treatment + post + treatment:post", data=long).fit(cov_type="cluster", cov_kwds={"groups": long["user_id"]})
    term = "treatment:post"
    return {"effect": float(model.params[term]), "standard_error": float(model.bse[term]),
            "ci_low": float(model.conf_int().loc[term, 0]), "ci_high": float(model.conf_int().loc[term, 1]),
            "p_value": float(model.pvalues[term])}


def subgroup_effects(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in ["device", "channel"]:
        for segment, group in df.groupby(dimension):
            result = proportion_effect(group, "activated_7d")
            rows.append({"dimension": dimension, "segment": segment, "n": len(group), **result})
    output = pd.DataFrame(rows)
    output["adjusted_p_value"] = multipletests(output["p_value"], method="fdr_bh")[1]
    return output


def analyze(df: pd.DataFrame) -> dict:
    validate_data(df)
    primary = proportion_effect(df, "activated_7d")
    support = proportion_effect(df, "support_contact_7d")
    latency = mean_effect(df, "transaction_latency_ms")
    balance = mean_effect(df, "prior_activity")
    summary = {
        "design": {"users": len(df), "required_users_per_arm": required_sample_size(), "alpha": 0.05, "power": 0.80},
        "randomization": {"sample_ratio_mismatch": sample_ratio_mismatch(df), "prior_activity_balance_p_value": balance["p_value"]},
        "primary_activation": primary,
        "regression_adjusted_activation": regression_adjusted_effect(df),
        "guardrails": {"support_contact": support, "transaction_latency_ms": latency},
        "difference_in_differences_engagement": difference_in_differences(df),
    }
    no_guardrail_harm = support["ci_high"] < 0.01 and latency["ci_high"] < 15
    summary["decision"] = "launch_with_monitoring" if primary["ci_low"] > 0 and no_guardrail_harm else "do_not_launch"
    return summary


def write_outputs(df: pd.DataFrame, summary: dict) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    subgroup_effects(df).to_csv(OUTPUT_DIR / "subgroup_effects.csv", index=False)
    metrics = pd.DataFrame([
        {"metric": "7-day activation", **summary["primary_activation"]},
        {"metric": "support-contact rate", **summary["guardrails"]["support_contact"]},
        {"metric": "transaction latency (ms)", **summary["guardrails"]["transaction_latency_ms"]},
    ])
    metrics.to_csv(OUTPUT_DIR / "metric_table.csv", index=False)
    p = summary["primary_activation"]
    report = f"""# Experiment decision report

## Recommendation

**{summary['decision'].replace('_', ' ').title()}** for the simulated onboarding redesign.

The treatment changed 7-day activation from {p['control_rate']:.1%} to {p['treatment_rate']:.1%}, an absolute effect of {p['absolute_effect']:.2%} (95% CI {p['ci_low']:.2%} to {p['ci_high']:.2%}; p={p['p_value']:.4f}) and relative lift of {p['relative_lift']:.1%}.

Randomization passed the sample-ratio-mismatch check (p={summary['randomization']['sample_ratio_mismatch']['p_value']:.3f}) and prior-activity balance check (p={summary['randomization']['prior_activity_balance_p_value']:.3f}). Regression adjustment estimated an effect of {summary['regression_adjusted_activation']['coefficient']:.2%}. The engagement difference-in-differences estimate was {summary['difference_in_differences_engagement']['effect']:.3f} events per user.

## Decision rule

Launch only if the primary metric's 95% confidence interval is above zero and plausible harm remains below +1 percentage point for support contacts and +15 ms for latency. Continue monitoring long-term retention, segment stability, logging quality, and novelty effects.

## Limitations

The data are synthetic. Subgroups are exploratory after false-discovery-rate correction. Difference-in-differences depends on parallel trends, and one pre-period cannot establish that assumption. A real rollout should use preregistered metrics, an exposure audit, longer retention windows, and sequential-testing controls if results are monitored repeatedly.
"""
    (OUTPUT_DIR / "experiment_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    summary = analyze(df)
    write_outputs(df, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

