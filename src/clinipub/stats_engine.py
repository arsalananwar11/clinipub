import numpy as np
import pandas as pd
from scipy import stats


class ClinicalDataAuditor:
    """Analyzes a clinical dataset to classify variable types and assess distribution
    normality for automatic statistical test selection.
    """

    def __init__(self, data: pd.DataFrame):
        if data.empty:
            raise ValueError("The provided DataFrame is empty.")
        self.data = data.copy()

    def detect_variable_types(self, max_categorical_threshold: int = 10) -> dict:
        """Classifies columns into 'categorical' or 'continuous'.
        Safely handles modern Pandas extension data types (like StringDtype).

        Returns a dictionary with two keys: 
        - `categorical`: A list of column names classified as categorical.
        - `continuous`: A list of column names classified as continuous.
        """
        classification = {"categorical": [], "continuous": []}

        for col in self.data.columns:
            # Skip empty or fully null columns
            if self.data[col].dropna().empty:
                continue

            # Check if it's explicitly a categorical dtype or a text string dtype (handles object & StringDtype)
            if (
                isinstance(self.data[col].dtype, pd.CategoricalDtype)
                or pd.api.types.is_string_dtype(self.data[col].dtype)
                or pd.api.types.is_object_dtype(self.data[col].dtype)
            ):
                classification["categorical"].append(col)

            # Check if it's a numeric type (handles integers, floats, and modern nullable types)
            elif pd.api.types.is_numeric_dtype(self.data[col].dtype):
                # If it's a boolean column, it's inherently categorical binary
                if pd.api.types.is_bool_dtype(self.data[col].dtype):
                    classification["categorical"].append(col)
                    continue

                unique_count = self.data[col].nunique()
                if unique_count <= max_categorical_threshold:
                    classification["categorical"].append(col)
                else:
                    classification["continuous"].append(col)

        return classification

    def test_normality(self, continuous_cols: list, alpha: float = 0.05) -> dict:
        """Runs a Shapiro-Wilk normality test on continuous variables.

        Returns a dictionary with column names as keys and boolean values indicating normality.
        Columns with fewer than 3 non-null observations are automatically classified as non-normal.
        - True indicates the variable is normally distributed (p >= alpha)
        - False indicates the variable is not normally distributed (p < alpha)
        """
        normality_results = {}

        for col in continuous_cols:
            clean_data = self.data[col].dropna()

            if len(clean_data) < 3:
                normality_results[col] = False
                continue

            _, p_value = stats.shapiro(clean_data)
            normality_results[col] = bool(p_value >= alpha)

        return normality_results
