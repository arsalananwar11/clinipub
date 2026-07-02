# clinipub
[![PyPI release](https://img.shields.io/pypi/v/clinipub)](https://pypi.org/project/clinipub/)
[![GitHub release](https://img.shields.io/github/v/release/arsalananwar11/clinipub)](https://github.com/arsalananwar11/clinipub/releases)
[![Tests](https://github.com/arsalananwar11/clinipub/actions/workflows/tests-suite.yml/badge.svg?branch=main)](https://github.com/arsalananwar11/clinipub/actions/workflows/tests-suite.yml)

A Python package to transform clinical dataframes into publication-ready, beautifully styled tables for medical journals and manuscripts

`clinipub` is a modern Python package designed for data scientists in the life sciences and clinical research fields. It bridges the gap between raw data analysis (`pandas.DataFrame`) and publication-ready medical writing reporting standards (matching *NEJM*, *JAMA*, *The Lancet*, and CDISC/STROBE guidelines).

Unlike existing packages, `clinipub` offers autonomous statistical decision-making, impeccable typography, and native exports to formats that medical writers can use out of the box without manual reformatting.

---

## Key Advantages Over Other Packages

* **Autonomous Statistics:** Automatically detects variable types and evaluates normality (Shapiro-Wilk) to map the correct parametric or non-parametric test.
* **Regulatory-Grade Precision:** Automatically falls back to Fisher's Exact test if any contingency cross-tab count drops below 5.

---

## 🛠️ Statistical Test Selection Matrix

The framework automatically maps and executes your bivariate comparative analytics using the following clinical logic:

| Variable Type | Distribution | Group Count | Test Executed |
| :--- | :--- | :--- | :--- |
| **Continuous** | Normal (Parametric) | 2 Groups | Independent Welch's $t$-test |
| **Continuous** | Normal (Parametric) | 3+ Groups | One-way ANOVA |
| **Continuous** | Skewed (Non-Parametric) | 2 Groups | Mann-Whitney U test |
| **Continuous** | Skewed (Non-Parametric) | 3+ Groups | Kruskal-Wallis test |
| **Categorical** | Any | 2x2 with Cell Count < 5 | Fisher's Exact test |
| **Categorical** | Any | Standard Configurations | Chi-Square ($\chi^2$) Contingency |

---

## Developer Setup & Installation

This project is managed efficiently using the **`uv`** package manager.

### Prerequisites
Ensure you have `uv` installed:
```bash
pip install uv
```

### Installation & Environment Setup
Clone the repository and sync the isolated project development container:

```bash
git clone https://github.com/arsalananwar11/clinipub.git

cd clinipub
uv sync
```

### Running Unit Tests
We maintain high test coverage for clinical accuracy using pytest:
```bash
uv run pytest
```

## Pipeline Flow
1. `MissingDataAuditor` computes raw missingness and validates data completeness.
2. `ClinicalDataAuditor` classifies variables and checks continuous normality.
3. `BivariateTestSelector` chooses tests automatically based on group count and distribution.
4. `TableOneAssembler` builds a stratified Table 1 with descriptive statistics and p-values.

## Quick Usage
```python
import pandas as pd
from clinipub import (
    MissingDataAuditor,
    ClinicalDataAuditor,
    BivariateTestSelector,
    TableOneAssembler,
)

# Load your clinical dataset
df = pd.read_csv("baseline.csv")

# 1. Audit missing data and generate an HTML report
missing_auditor = MissingDataAuditor(df)
missing_df = missing_auditor.calculate_missingness()
html_report = missing_auditor.to_html_report(
    audit_df=missing_df,
    thresholds={"low": 1.0, "mid": 20.0},
)

# 2. Audit variable types and normality
auditor = ClinicalDataAuditor(df)
var_types = auditor.detect_variable_types()
normality = auditor.test_normality(var_types["continuous"])

# 3. Run autonomous bivariate tests
selector = BivariateTestSelector(df, stratify_by="treatment")
continuous_result = selector.test_continuous("age", is_normal=normality["age"])
cat_result = selector.test_categorical("smoker_status")

# 4. Build publication-ready Table 1
assembler = TableOneAssembler(df, stratify_by="treatment")
table1 = assembler.build()
```

## Core API and Arguments
- `MissingDataAuditor(data: pd.DataFrame)`
  - `calculate_missingness()`
    - returns a raw `DataFrame` with `missing_count` and `missing_percentage`
  - `to_html_report(audit_df: pd.DataFrame = None, thresholds: dict = {'low': 5.0, 'mid': 30.0})`
    - returns styled HTML for publication-ready missingness reporting

- `ClinicalDataAuditor(data: pd.DataFrame)`
  - `detect_variable_types(max_categorical_threshold: int = 10)`
    - returns `{'categorical': [...], 'continuous': [...]}`
  - `test_normality(continuous_cols: list, alpha: float = 0.05)`
    - returns `{column_name: bool}`

- `BivariateTestSelector(data: pd.DataFrame, stratify_by: str)`
  - `test_continuous(col: str, is_normal: bool)`
    - returns `{'p_value': float, 'test': str}`
  - `test_categorical(col: str)`
    - returns `{'p_value': float, 'test': str}`

- `TableOneAssembler(data: pd.DataFrame, stratify_by: str, columns: list = None)`
  - `build()`
    - returns a styled `pandas.DataFrame` with stratified descriptive statistics and p-values

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on issues, pull requests, testing, and repository workflow.

