import pandas as pd
import pytest

from experiment.analysis import analyze, required_sample_size, validate_data
from experiment.generate_data import generate_experiment


def test_power_analysis_returns_practical_sample_size():
    assert 8_000 < required_sample_size() < 11_000


def test_duplicate_randomization_units_are_rejected():
    frame = generate_experiment(100)
    frame.loc[1, "user_id"] = frame.loc[0, "user_id"]
    with pytest.raises(ValueError, match="unique"):
        validate_data(frame)


def test_missing_analysis_values_are_rejected():
    frame = generate_experiment(100)
    frame.loc[0, "activated_7d"] = pd.NA
    with pytest.raises(ValueError, match="missing"):
        validate_data(frame)


def test_analysis_contains_primary_causal_and_guardrail_results():
    result = analyze(generate_experiment(24_000))
    assert result["primary_activation"]["absolute_effect"] > 0
    assert result["primary_activation"]["ci_low"] > 0
    assert "regression_adjusted_activation" in result
    assert "difference_in_differences_engagement" in result
    assert set(result["guardrails"]) == {"support_contact", "transaction_latency_ms"}

