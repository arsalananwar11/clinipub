import numpy as np
import pandas as pd
import pytest
from clinipub.missingness import MissingDataAuditor


def test_missing_auditor_empty_df_error():
    """Fails instantly if an empty dataframe is passed."""
    with pytest.raises(ValueError, match="The provided DataFrame is empty."):
        MissingDataAuditor(pd.DataFrame())


def test_calculate_missingness_metrics():
    """Validates missing_counts and percentage math calculations."""
    df = pd.DataFrame(
        {
            "perfect": [1, 2, 3, 4],  # 0% missing
            "mild": [1, 2, 3, np.nan],  # 25% missing
            "severe": [1, np.nan, np.nan, np.nan],  # 75% missing
        }
    )

    auditor = MissingDataAuditor(df)
    metrics = auditor.calculate_missingness()

    assert isinstance(metrics, pd.DataFrame)
    assert metrics.loc["perfect", "missing_count"] == 0
    assert metrics.loc["perfect", "missing_percentage"] == 0.0

    assert metrics.loc["mild", "missing_count"] == 1
    assert metrics.loc["mild", "missing_percentage"] == 25.0

    assert metrics.loc["severe", "missing_count"] == 3
    assert metrics.loc["severe", "missing_percentage"] == 75.0


def test_html_report_generation_with_and_without_precomputed_df():
    """Confirms CSS styles and structured string keywords exist in final HTML,

    both when generated automatically and when passing a pre-calculated DataFrame.
    """
    df = pd.DataFrame({"age": [55, np.nan, 42]})
    auditor = MissingDataAuditor(df)

    # Test running without explicit parameters (auto-calculates internally)
    html_auto = auditor.to_html_report()
    assert "<table" in html_auto
    assert "background-color" in html_auto

    # Test passing a decoupled precomputed df explicitly
    metrics = auditor.calculate_missingness()
    html_decoupled = auditor.to_html_report(audit_df=metrics)

    assert "<table" in html_decoupled
    assert "background-color" in html_decoupled
    # Confirm both approaches generate structural parity
    assert len(html_auto) == len(html_decoupled)


def test_mcar_no_missing_values():
    """Ensures MCAR returns neutral results for a completely observed dataset."""
    df = pd.DataFrame({"age": [20, 30, 40], "bp": [120, 130, 140]})
    auditor = MissingDataAuditor(df)
    results = auditor.run_mcar_test()
    assert results["p_value"] == 1.0
    assert results["statistic"] == 0.0
    assert results["degrees_of_freedom"] == 0


def test_mcar_systematic_missingness_rejection():
    """Verifies MCAR detects systematic missingness and rejects the null hypothesis."""
    np.random.seed(42)
    n = 200
    age = np.random.normal(50, 10, n)
    biomarker = np.random.normal(10, 2, n)

    df = pd.DataFrame({"age": age, "biomarker": biomarker})
    df.loc[df["age"] > 62, "biomarker"] = np.nan

    auditor = MissingDataAuditor(df)
    results = auditor.run_mcar_test()

    assert results["p_value"] < 0.05
    assert results["statistic"] > 0
    assert results["degrees_of_freedom"] > 0


def test_mcar_random_missingness_acceptance():
    """Confirms MCAR accepts randomly missing data as consistent with MCAR."""
    np.random.seed(0)
    n = 1000
    df = pd.DataFrame(
        {
            "age": np.random.normal(50, 8, n),
            "bp": np.random.normal(120, 12, n),
        }
    )
    df.loc[np.random.rand(n) < 0.1, "age"] = np.nan
    df.loc[np.random.rand(n) < 0.1, "bp"] = np.nan

    auditor = MissingDataAuditor(df)
    results = auditor.run_mcar_test()

    assert results["p_value"] > 0.05
    assert results["degrees_of_freedom"] > 0
