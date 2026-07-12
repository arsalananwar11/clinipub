import numpy as np
import pandas as pd
from clinipub import (
    BivariateTestSelector,
    ClinicalDataAuditor,
    JournalHTMLExporter,
    MissingDataAuditor,
    TableOneAssembler,
)


def run_pipeline():
    """Demonstrates an end-to-end pipeline for automated bivariate statistical analysis,
    structured Table 1 assembly, and missing data auditing.
    """
    np.random.seed(42)
    n_samples = 500

    # 1. Generate clean mock clinical trial baseline data
    mock_df = pd.DataFrame(
        {
            "age": np.random.normal(loc=60, scale=12, size=n_samples),
            "days_to_event": np.random.exponential(scale=30, size=n_samples),
            "biomarker_level": np.random.normal(loc=5, scale=1.5, size=n_samples),
            "smoker_status": np.random.choice(["Yes", "No"], size=n_samples),
            "treatment": np.random.choice(["Drug A", "Placebo"], size=n_samples),
        }
    )

    # 2. INTRODUCE MISSING DATA (Simulating real-world clinical collection gaps)
    # Inject ~2% missingness in age (Green boundary)
    mock_df.loc[mock_df.sample(frac=0.02).index, "age"] = np.nan
    # Inject ~18% missingness in smoker_status (Yellow boundary)
    mock_df.loc[mock_df.sample(frac=0.18).index, "smoker_status"] = np.nan
    # Inject ~38% missingness in days_to_event (Red boundary)
    mock_df.loc[mock_df.sample(frac=0.38).index, "days_to_event"] = np.nan

    print("=================================================================")
    print(" STEP 1: AUDITING MISSING DATA PATTERNS AND SAFETY BOUNDARIES   ")
    print("=================================================================")
    missing_auditor = MissingDataAuditor(mock_df)

    # Fetch raw data calculations for downstream system pipelines
    raw_missing_df = missing_auditor.calculate_missingness()
    print("Raw Missing Data Analytics (DataFrame):")
    print(raw_missing_df)

    # Convert calculations to a color-coded publication report
    html_report = missing_auditor.to_html_report(audit_df=raw_missing_df, thresholds={"low": 1.0, "mid": 20.0})
    output_filename = "missing_data_stats.html"

    with open(output_filename, "w") as f:
        f.write(html_report)

    print(f"\nSuccess! Missing data stats written to '{output_filename}'.")
    print("Open this file in your browser to inspect the color-coded safety badges.\n")

    # MCAR test right from the same auditor instance
    mcar_res = missing_auditor.run_mcar_test()

    print(f"Little's Chi-Square Statistic: {mcar_res['statistic']:.2f}")
    print(f"Calculated p-value:           {mcar_res['p_value']:.4f}")
    print(f"Degrees of Freedom:           {mcar_res['degrees_of_freedom']}\n")

    print("=================================================================")
    print(" STEP 2: AUDITING VARIABLE TYPES AND NORMALITY DISPOSITION       ")
    print("=================================================================")
    auditor = ClinicalDataAuditor(mock_df)
    var_types = auditor.detect_variable_types()
    normality = auditor.test_normality(var_types["continuous"])

    print(f"Detected Categorical Variables: {var_types['categorical']}")
    print(f"Detected Continuous Variables:  {var_types['continuous']}")
    print(f"Continuous Normality Pass (True=Normal, False=Skewed): {normality}\n")

    print("=================================================================")
    print(" STEP 3: RUNNING AUTONOMOUS BIVARIATE STATISTICAL TESTS         ")
    print("=================================================================")
    selector = BivariateTestSelector(mock_df, stratify_by="treatment")

    # Evaluate continuous variables
    for col in var_types["continuous"]:
        is_normal = normality[col]
        test_results = selector.test_continuous(col, is_normal=is_normal)
        print(f"Variable: {col:15} | Test: {test_results['test']:15} | p-value: {test_results['p_value']:.4f}")

    # Evaluate categorical variables (ignoring treatment)
    for col in var_types["categorical"]:
        if col != "treatment":
            p_cat_test_results = selector.test_categorical(col)
            print(f"Variable: {col:15} | Test: {p_cat_test_results['test']:15} | p-value: {p_cat_test_results['p_value']:.4f}")
    print()

    print("=================================================================")
    print(" STEP 4: ASSEMBLING STRUCTURED SUMMARY TABLE ONE                ")
    print("=================================================================")
    assembler = TableOneAssembler(mock_df, stratify_by="treatment")
    table1_df = assembler.build()
    print(table1_df)
    print()

    print("=================================================================")
    print(" STEP 6: EXPORTING PUBLICATION-READY JOURNAL HTML TABLES          ")
    print("=================================================================")    
    # Pass our compiled Table 1 into the NEJM styling layout
    exporter = JournalHTMLExporter(table1_df, journal="nejm")
    nejm_table_html = exporter.export()
    
    with open("table1_nejm_style.html", "w") as f:
        f.write(nejm_table_html)
        
    print("Success! Styled 'table1_nejm_style.html' created.")
    print("=================================================================")



if __name__ == "__main__":
    run_pipeline()