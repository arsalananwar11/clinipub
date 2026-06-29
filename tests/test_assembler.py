import pandas as pd
from clinipub import TableOneAssembler


def test_table_one_assembler_structure():
    """Validates the multi-index structural shapes and group size injections."""
    df = pd.DataFrame(
        {
            "age": [50, 60, 70, 40, 45, 55, 65],
            "gender": ["M", "F", "M", "F", "M", "F", "F"],
            "arm": ["Drug", "Drug", "Drug", "Placebo", "Placebo", "Placebo", "Placebo"],
        }
    )

    assembler = TableOneAssembler(df, stratify_by="arm")
    result_df = assembler.build()

    # Confirm MultiIndex holds the expected levels
    assert isinstance(result_df.index, pd.MultiIndex)
    assert "age" in result_df.index.get_level_values(0)
    assert "gender" in result_df.index.get_level_values(0)

    # Check the total count string injection in header column names
    assert "Drug (N=3)" in result_df.columns
    assert "Placebo (N=4)" in result_df.columns
    assert "p-value" in result_df.columns
