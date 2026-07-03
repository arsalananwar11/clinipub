import numpy as np
import pandas as pd
import pytest
import warnings
from clinipub import ClinicalDataAuditor


def test_empty_dataframe_raises_error():
    """Ensures an empty dataframe explicitly triggers a ValueError."""
    with pytest.raises(ValueError, match="The provided DataFrame is empty."):
        ClinicalDataAuditor(pd.DataFrame())


def test_variable_type_detection_and_null_handling():
    """Tests variable type classification including null columns and extension strings."""
    df = pd.DataFrame(
        {
            "age": [23, 45, 67, 34, 51],
            "gender": ["F", "M", "F", "M", "F"],
            "stage": [1, 2, 1, 3, 2],  # Low cardinality integer -> categorical
            "all_null": [np.nan, np.nan, np.nan, np.nan, np.nan],  # Should be skipped
            "modern_str": pd.Series(
                ["A", "B", "A", "B", "A"], dtype="string"
            ),
        }
    )

    auditor = ClinicalDataAuditor(df)
    types = auditor.detect_variable_types(max_categorical_threshold=3)

    assert "age" in types["continuous"]
    assert "gender" in types["categorical"]
    assert "stage" in types["categorical"]
    assert "modern_str" in types["categorical"]
    assert "all_null" not in types["continuous"]
    assert "all_null" not in types["categorical"]


def test_normality_native_boolean_return():
    """Verifies that test_normality returns native python bool values, not numpy types."""
    np.random.seed(42)
    short_series = [1.0, 2.0] + [np.nan] * 48
    df = pd.DataFrame(
        {
            "normal_var": np.random.normal(10, 2, 50),
            "skewed_var": np.random.exponential(5, 50),
            "short_var": short_series,  # n < 3 -> automatically skewed/False
        }
    )

    auditor = ClinicalDataAuditor(df)
    results = auditor.test_normality(["normal_var", "skewed_var", "short_var"])

    # Ensure native python bool types
    assert isinstance(results["normal_var"], bool)
    assert isinstance(results["skewed_var"], bool)
    assert isinstance(results["short_var"], bool)

    assert results["normal_var"] is True
    assert results["skewed_var"] is False
    assert results["short_var"] is False


def test_normality_large_sample_uses_full_dataset_without_warning():
    """Ensures large-sample normality testing retains the original data and avoids Shapiro warnings."""
    np.random.seed(0)
    df = pd.DataFrame({"normal_var": np.random.normal(0, 1, 500000)})

    auditor = ClinicalDataAuditor(df)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        results = auditor.test_normality(["normal_var"])

    assert isinstance(results["normal_var"], bool)
