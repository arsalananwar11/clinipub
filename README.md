# clinipub

[![DOI](https://zenodo.org/badge/1283440630.svg)](https://doi.org/10.5281/zenodo.21158151)
[![PyPI release](https://img.shields.io/pypi/v/clinipub)](https://pypi.org/project/clinipub/)
[![GitHub release](https://img.shields.io/github/v/release/arsalananwar11/clinipub)](https://github.com/arsalananwar11/clinipub/releases)
[![Tests](https://github.com/arsalananwar11/clinipub/actions/workflows/tests-suite.yml/badge.svg?branch=main)](https://github.com/arsalananwar11/clinipub/actions/workflows/tests-suite.yml)


A lightweight Python toolkit that turns clinical `pandas.DataFrame` datasets into publication-ready Table 1 summaries and missing-data audits.

`clinipub` automates clinical descriptive analytics, standard test selection, and publication-quality output for medical research manuscripts, registries, and regulatory reporting.

## Why this package exists

Baseline tables and missingness audits are essential in clinical research, but most teams still prepare them manually. `clinipub` delivers a reproducible, data-first workflow for clinical scientists and medical writers.

## Key features

- `MissingDataAuditor`: compute missingness, generate a styled HTML report, and run Little's MCAR test
- `ClinicalDataAuditor`: detect categorical vs continuous variables and test continuous normality
- `BivariateTestSelector`: select the appropriate clinical test automatically for continuous and categorical comparisons
- `TableOneAssembler`: assemble a stratified Table 1 with descriptive statistics and p-values

## Installation

Install from PyPI:

```bash
pip install clinipub
```

Install from source for development:

```bash
git clone https://github.com/arsalananwar11/clinipub.git
cd clinipub
uv sync
```

## Quick start

```python
import pandas as pd
from clinipub import (
    MissingDataAuditor,
    ClinicalDataAuditor,
    BivariateTestSelector,
    TableOneAssembler,
)

# Load clinical data

df = pd.read_csv("baseline.csv")

# Audit missing data and run Little's MCAR test
missing_auditor = MissingDataAuditor(df)
missing_df = missing_auditor.calculate_missingness()
mcar_results = missing_auditor.run_mcar_test()

html_report = missing_auditor.to_html_report(
    audit_df=missing_df,
    thresholds={"low": 1.0, "mid": 20.0},
)

# Detect variable types and assess normality
auditor = ClinicalDataAuditor(df)
var_types = auditor.detect_variable_types()
normality = auditor.test_normality(var_types["continuous"])

# Select and execute bivariate tests
selector = BivariateTestSelector(df, stratify_by="treatment")
continuous_result = selector.test_continuous("age", is_normal=normality["age"])
cat_result = selector.test_categorical("smoker_status")

# Assemble publication-ready Table 1
assembler = TableOneAssembler(df, stratify_by="treatment")
table1 = assembler.build()
```

## API overview

- `MissingDataAuditor(data: pd.DataFrame)`
  - `calculate_missingness()` → DataFrame with `missing_count` and `missing_percentage`
  - `to_html_report(audit_df: pd.DataFrame = None, thresholds: dict = {'low': 5.0, 'mid': 30.0})` → styled HTML output
  - `run_mcar_test()` → dict with `statistic`, `p_value`, and `degrees_of_freedom`

- `ClinicalDataAuditor(data: pd.DataFrame)`
  - `detect_variable_types(max_categorical_threshold: int = 10)` → `{'categorical': [...], 'continuous': [...]}`
  - `test_normality(continuous_cols: list, alpha: float = 0.05)` → dict mapping column names to booleans

- `BivariateTestSelector(data: pd.DataFrame, stratify_by: str)`
  - `test_continuous(col: str, is_normal: bool)` → `{'p_value': float, 'test': str}`
  - `test_categorical(col: str)` → `{'p_value': float, 'test': str}`

- `TableOneAssembler(data: pd.DataFrame, stratify_by: str, columns: list = None)`
  - `build()` → styled `pandas.DataFrame` with stratified descriptive statistics and p-values

## Developer workflow

Run tests with:

```bash
uv run pytest
```

## References

- Little, R. J. A. (1988). A test of missing completely at random for multivariate data with missing values. *Journal of the American Statistical Association*.
- CDISC, STROBE, and medical publication best practices for clinical summary reporting.

## License

MIT License.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for issue and pull request guidelines.

