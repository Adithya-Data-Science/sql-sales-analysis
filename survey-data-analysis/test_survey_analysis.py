from pathlib import Path
import pandas as pd
import pytest
from survey_analysis import SurveyDataValidator, SurveyReportingApplication

SAMPLE = Path(__file__).with_name("sample_survey.csv")

def test_application_reproduces_verified_kpis_and_three_charts(tmp_path: Path) -> None:
    summary = SurveyReportingApplication().run(SAMPLE, tmp_path)
    assert summary == {
        "responses": 8,
        "completion_rate_pct": 87.5,
        "average_satisfaction": 3.86,
        "positive_response_rate_pct": 71.4,
        "missing_satisfaction_values": 1,
    }
    assert len(list(tmp_path.glob("*.png"))) == 3
    assert (tmp_path / "summary.json").is_file()

def test_duplicate_response_ids_are_rejected() -> None:
    raw = pd.read_csv(SAMPLE)
    raw.loc[1, "response_id"] = raw.loc[0, "response_id"]
    with pytest.raises(ValueError, match="unique"):
        SurveyDataValidator().clean_and_validate(raw)

def test_out_of_range_satisfaction_is_rejected() -> None:
    raw = pd.read_csv(SAMPLE)
    raw.loc[0, "satisfaction"] = 6
    with pytest.raises(ValueError, match="between 1 and 5"):
        SurveyDataValidator().clean_and_validate(raw)
