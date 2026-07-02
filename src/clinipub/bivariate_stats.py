from typing import Tuple

import pandas as pd
from scipy import stats


class BivariateTestSelector:
    """Selects and executes the appropriate statistical test for clinical variables
    stratified by a grouping variable.
    """

    def __init__(self, data: pd.DataFrame, stratify_by: str):
        self.data = data.dropna(subset=[stratify_by]).copy()
        self.stratify_by = stratify_by
        self.groups = self.data[stratify_by].unique()
        self.num_groups = len(self.groups)

        if self.num_groups < 2:
            raise ValueError(
                f"Stratification column '{stratify_by}' must contain at least 2 distinct groups."
            )

    def test_continuous(self, col: str, is_normal: bool) -> dict:
        """Executes the correct continuous test depending on normality and group count
           and returns the p-value.

           Returns a dictionary with: 
           - `p_value`: the p-value
           - `test`: the name of the test used
        """
        # Split data by grouping variable values
        grouped_data = [
            self.data[self.data[self.stratify_by] == g][col].dropna()
            for g in self.groups
        ]
        test_used = ""
        if is_normal:
            if self.num_groups == 2:
                # 2 groups + Normal -> t-test (Welch's if variances differ)
                test_used = "t-test"
                _, p_val = stats.ttest_ind(*grouped_data, equal_var=False)
            else:
                # 3+ groups + Normal -> One-way ANOVA
                test_used = "ANOVA"
                _, p_val = stats.f_oneway(*grouped_data)
        else:
            if self.num_groups == 2:
                # 2 groups + Skewed -> Mann-Whitney U
                test_used = "Mann-Whitney U"
                _, p_val = stats.mannwhitneyu(*grouped_data, alternative="two-sided")
            else:
                # 3+ groups + Skewed -> Kruskal-Wallis
                test_used = "Kruskal-Wallis"
                _, p_val = stats.kruskal(*grouped_data)

        return {"p_value": float(p_val), "test": test_used}

    def test_categorical(self, col: str) -> dict:
        """Executes a Chi-Square test or automatically falls back to Fisher's Exact Test
        if any expected cell count is less than 5 (for 2x2 configurations) and returns the p-value.
        
        Returns a dictionary with: 
           - `p_value`: the p-value
           - `test`: the name of the test used
        """
        contingency_table = pd.crosstab(self.data[self.stratify_by], self.data[col])
        test_used = "Chi-Square"
        if self.num_groups == 2 and contingency_table.shape == (2, 2):
            # Check for small cell counts to satisfy regulatory strictness
            if (contingency_table < 5).any().any():
                test_used = "Fisher's Exact"
                _, p_val = stats.fisher_exact(contingency_table)
                return {"p_value": float(p_val), "test": test_used}

        # Standard Chi-Square test
        test_used = "Chi-Square"
        _, p_val, _, _ = stats.chi2_contingency(contingency_table)
        return {"p_value": float(p_val), "test": test_used}
