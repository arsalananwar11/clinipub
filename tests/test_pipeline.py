# test_run.py
import numpy as np
import pandas as pd
from clinipub import ClinicalDataAuditor, BivariateTestSelector

np.random.seed(42)
mock_df = pd.DataFrame(
    {
        "age": np.random.normal(loc=60, scale=12, size=150),
        "days_to_event": np.random.exponential(scale=30, size=150),
        "treatment": np.random.choice(["Drug A", "Placebo"], size=150),
        "smoker_status": np.random.choice(["Yes", "No"], size=150),
    }
)

# 1. Audit types and normality
auditor = ClinicalDataAuditor(mock_df)
var_types = auditor.detect_variable_types()
normality = auditor.test_normality(var_types["continuous"])

# 2. Select and calculate automated p-values stratified by treatment group
selector = BivariateTestSelector(mock_df, stratify_by="treatment")

print("Pipeline to Test End-to-End Automated Bivariate Statistical Analysis")

# Run continuous variables
for col in var_types["continuous"]:
    is_normal = normality[col]
    p_val = selector.test_continuous(col, is_normal=is_normal)
    test_used = "t-test" if is_normal else "Mann-Whitney U"
    print(f"Variable: {col:15} | Test: {test_used:15} | p-value: {p_val:.4f}")

# Run categorical variables (excluding the stratification tracker column itself)
for col in var_types["categorical"]:
    if col != "treatment":
        p_val = selector.test_categorical(col)
        print(f"Variable: {col:15} | Test: Chi-Square      | p-value: {p_val:.4f}")
