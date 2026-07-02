import numpy as np
import pandas as pd
from clinipub import BivariateTestSelector, ClinicalDataAuditor


class TableOneAssembler:
    """Assembles descriptive statistics and automated p-values into a structured,
    hierarchical multi-index pandas DataFrame.
    """

    def __init__(self, data: pd.DataFrame, stratify_by: str, columns: list = None):
        self.data = data.copy()
        self.stratify_by = stratify_by

        # Initialize the baseline auditors
        self.auditor = ClinicalDataAuditor(self.data)
        self.selector = BivariateTestSelector(self.data, stratify_by=stratify_by)

        # Automatically determine variable classifications
        detected_var_types = self.auditor.detect_variable_types()
        self.normality = self.auditor.test_normality(detected_var_types["continuous"])

        # Filter features based on user requested list or default to all valid columns
        if columns:
            self.continuous_cols = [
                c for c in columns if c in detected_var_types["continuous"]
            ]
            self.categorical_cols = [
                c for c in columns if c in detected_var_types["categorical"]
            ]
        else:
            self.continuous_cols = detected_var_types["continuous"]
            self.categorical_cols = [
                c for c in detected_var_types["categorical"] if c != stratify_by
            ]

        # Get cohort arms and order them cleanly
        self.groups = sorted(self.data[stratify_by].dropna().unique())

    def _assemble_continuous(self, col: str) -> list:
        """Calculates stratified summary statistics for a single continuous column."""
        is_normal = self.normality.get(col, False)
        test_results = self.selector.test_continuous(col, is_normal)

        row_data = {
            "Variable": col,
            "Distribution": "Cont. Normal" if is_normal else "Cont. Skewed",
            "Category": "Mean (SD)" if is_normal else "Median [IQR]",
            "p-value": f"{test_results['p_value']:.3f}" if test_results['p_value'] >= 0.001 else "<0.001",
        }

        # Calculate metrics split by trial arm
        for group in self.groups:
            group_series = self.data[self.data[self.stratify_by] == group][
                col
            ].dropna()

            if group_series.empty:
                row_data[group] = "0.0"
            elif is_normal:
                row_data[group] = (
                    f"{group_series.mean():.1f} ({group_series.std():.1f})"
                )
            else:
                q25, q50, q75 = np.percentile(group_series, [25, 50, 75])
                row_data[group] = f"{q50:.1f} [{q25:.1f} - {q75:.1f}]"

        return [row_data]

    def _assemble_categorical(self, col: str) -> list:
        """Calculates stratified counts and percentages for a single categorical column."""
        p_cat_test_results = self.selector.test_categorical(col)
        p_str = f"{p_cat_test_results['p_value']:.3f}" if p_cat_test_results['p_value'] >= 0.001 else "<0.001"

        # Get ordered categories, ignoring NaNs
        categories = sorted(self.data[col].dropna().unique())
        rows = []

        for i, cat in enumerate(categories):
            row_data = {
                "Variable": col,
                "Distribution": "Categorical",
                "Category": str(cat),
                "p-value": p_str if i == 0 else "",  # Only show p-value on header row
            }

            for group in self.groups:
                group_data = self.data[self.data[self.stratify_by] == group][col]
                total_n = len(group_data.dropna())
                count = len(group_data[group_data == cat])

                pct = (count / total_n * 100) if total_n > 0 else 0.0
                row_data[group] = f"{count} ({pct:.1f}%)"

            rows.append(row_data)

        return rows

    def build(self) -> pd.DataFrame:
        """Executes full assembly and sets up the final MultiIndex hierarchy layout.
        
        Returns a pandas DataFrame with a MultiIndex on rows and stratified columns"""
        all_rows = []

        # Process variables sequentially
        for col in self.continuous_cols:
            all_rows.extend(self._assemble_continuous(col))

        for col in self.categorical_cols:
            all_rows.extend(self._assemble_categorical(col))

        # Convert list of rows to a structured Pandas DataFrame
        df_flat = pd.DataFrame(all_rows)

        # Calculate Total Cohort Sizes for Header Row Labels
        header_mapping = {}
        for group in self.groups:
            group_n = len(self.data[self.data[self.stratify_by] == group])
            header_mapping[group] = f"{group} (N={group_n})"

        df_flat = df_flat.rename(columns=header_mapping)

        # Reorder columns to ensure p-value is last
        cols = [c for c in df_flat.columns if c != "p-value"] + ["p-value"]
        df_flat = df_flat[cols]

        # Set index to hierarchy
        df_flat.set_index(["Variable", "Distribution", "Category"], inplace=True)

        return df_flat
