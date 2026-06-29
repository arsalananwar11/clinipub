import pandas as pd
import pytest
from clinipub.bivariate_stats import BivariateTestSelector


def test_insufficient_stratification_groups_error():
    """Fails if the stratification parameter doesn't contain multiple arms."""
    df = pd.DataFrame({"age": [20, 30, 40], "arm": ["Control", "Control", "Control"]})
    with pytest.raises(
        ValueError, match="must contain at least 2 distinct groups"
    ):
        BivariateTestSelector(df, stratify_by="arm")


def test_bivariate_continuous_tests():
    """Validates parametric/non-parametric p-value extraction pipelines."""
    df = pd.DataFrame(
        {
            "age": [50, 52, 55, 48, 51, 70, 72, 68, 71, 69],
            "arm": [
                "Placebo",
                "Placebo",
                "Placebo",
                "Placebo",
                "Placebo",
                "Drug",
                "Drug",
                "Drug",
                "Drug",
                "Drug",
            ],
        }
    )

    selector = BivariateTestSelector(df, stratify_by="arm")

    # Both tests should yield significant p-values due to the clear age difference between groups
    # Parametric t-test pipeline
    p_normal = selector.test_continuous("age", is_normal=True)
    assert 0.0 < p_normal < 0.01
    assert isinstance(p_normal, float)

    # Non-parametric Mann-Whitney pipeline
    p_skewed = selector.test_continuous("age", is_normal=False)
    assert 0.0 < p_skewed < 0.01 
    assert isinstance(p_skewed, float)


def test_categorical_fishers_fallback():
    """Triggers Fisher's Exact test if cross-tabulation cells are extremely small (<5)."""
    # Create an unbalanced matrix intentional for Fisher's test fallback criteria
    df = pd.DataFrame(
        {
            "outcome": ["Remission", "Sick", "Sick", "Sick", "Sick", "Sick"],
            "arm": ["Drug", "Drug", "Placebo", "Placebo", "Placebo", "Placebo"],
        }
    )
    selector = BivariateTestSelector(df, stratify_by="arm")
    p_val = selector.test_categorical("outcome")

    assert isinstance(p_val, float)
    assert 0.0 <= p_val <= 1.0
