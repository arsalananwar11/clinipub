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
- `JournalHTMLExporter`: export journal-formatted HTML tables for manuscript-ready output
- `JournalDocxExporter`: save publication-ready tables directly to `.docx`

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
    JournalHTMLExporter,
    JournalDocxExporter,
)

# Load your clinical dataset. Update the filepath to your own CSV file.
print("Loading dataset...")
df = pd.read_csv("baseline.csv")
print(f"Loaded {len(df)} rows and {len(df.columns)} columns")

# 1. Audit missing data
print("\nCalculating missingness...")
missing_auditor = MissingDataAuditor(df)
missing_df = missing_auditor.calculate_missingness()
print(missing_df)

print("\nWriting missing data report to missing_data_stats.html...")
missing_html = missing_auditor.to_html_report(audit_df=missing_df)
with open("missing_data_stats.html", "w") as f:
    f.write(missing_html)
print("Saved missing_data_stats.html")

# 2. Detect variable types and assess normality
print("\nDetecting variable types...")
clinical_auditor = ClinicalDataAuditor(df)
var_types = clinical_auditor.detect_variable_types()
print("Categorical:", var_types["categorical"])
print("Continuous:", var_types["continuous"])

print("\nTesting normality for continuous variables...")
normality = clinical_auditor.test_normality(var_types["continuous"])
print(normality)

# 3. Select appropriate bivariate tests
print("\nRunning bivariate tests stratified by treatment...")
test_selector = BivariateTestSelector(df, stratify_by="treatment")
print("Age test:", test_selector.test_continuous("age", is_normal=normality.get("age", False)))
print("Smoker status test:", test_selector.test_categorical("smoker_status"))

# 4. Assemble a publication-ready Table 1
print("\nAssembling Table 1...")
assembler = TableOneAssembler(df, stratify_by="treatment")
table1 = assembler.build()
print(table1)

# 5. Export publication-ready output
print("\nExporting journal-ready HTML (NEJM style shown as an example)...")
html_exporter = JournalHTMLExporter(table1, journal="nejm")
with open("table1_nejm_style.html", "w") as f:
    f.write(html_exporter.export())
print("Saved table1_nejm_style.html")

print("\nExporting manuscript-ready DOCX...")
docx_exporter = JournalDocxExporter(table1, journal="nejm")
docx_exporter.save("table1_nejm_manuscript.docx")
print("Saved table1_nejm_manuscript.docx")
```

For a full end-to-end pipeline example, see [examples/pipeline.py](examples/pipeline.py).

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

- `JournalHTMLExporter(table_df: pd.DataFrame, journal: str = "nejm")`
  - `export()` → HTML string for journal-formatted table output

- `JournalDocxExporter(table_df: pd.DataFrame, journal: str = "nejm")`
  - `save(path: str)` → write a Word `.docx` table file

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

