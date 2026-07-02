import pandas as pd


class MissingDataAuditor:
    """Audits missing data patterns in a clinical dataset and generates a formatted,
    color-coded HTML health report.
    """

    def __init__(self, data: pd.DataFrame):
        if data.empty:
            raise ValueError("The provided DataFrame is empty.")
        self.data = data.copy()

    def calculate_missingness(self) -> pd.DataFrame:
        """Computes absolute counts and percentages of missing data for each column.
        
        Returns a raw pandas DataFrame with the following columns for custom user pipelines:
        - `missing_count`: The number of missing values for each column.
        - `missing_percentage`: The percentage of missing values for each column.
        """
        total_rows = len(self.data)

        missing_counts = self.data.isna().sum()
        missing_pct = (missing_counts / total_rows) * 100

        audit_df = pd.DataFrame(
            {"missing_count": missing_counts, "missing_percentage": missing_pct}
        )

        audit_df.index.name = "Variable"
        return audit_df.sort_values(by="missing_percentage", ascending=False)

    @staticmethod
    def _style_missing_cells(val: float, thresholds: dict) -> str:
        """Applies clinical safety boundary color-coding to HTML cells based on missingness percentage."""
        if val < thresholds["low"]:
            return "background-color: #d4edda; color: #155724; font-weight: bold;"  # Soft Green
        elif val <= thresholds["mid"]:
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"  # Soft Yellow
        else:
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"  # Soft Red

    def to_html_report(self, audit_df: pd.DataFrame = None, thresholds: dict = {"low": 5.0, "mid": 30.0}) -> str:
        """Generates a fully-styled HTML table string with embedded CSS color-coding.
        Accepts an optional pre-computed missingness DataFrame.
        """
        if not isinstance(thresholds, dict) or "low" not in thresholds or "mid" not in thresholds:
            raise ValueError("Thresholds must be a dictionary with 'low' and 'mid' keys.")
        
        if thresholds["low"] >= thresholds["mid"]:
            raise ValueError("Threshold 'low' must be less than 'mid' for proper color-coding.")
        
        if audit_df is not None:
            if not isinstance(audit_df, pd.DataFrame):
                raise ValueError(f"audit_df must be a pandas DataFrame if provided. Type received: {type(audit_df)}")

            if not {"missing_count", "missing_percentage"}.issubset(audit_df.columns):
                raise ValueError("audit_df must contain 'missing_count' and 'missing_percentage' columns.")

        # If the user didn't pass an existing audit dataframe, calculate it now
        if audit_df is None:
            audit_df = self.calculate_missingness()

        # Use Pandas Styler to map the color logic cleanly to the percentage column
        styled = audit_df.style.map(
            self._style_missing_cells, subset=["missing_percentage"], thresholds=thresholds
        )

        # Format percentages beautifully for display
        styled = styled.format({"missing_percentage": "{:.1f}%"})

        # Custom high-quality CSS for clean table structure
        custom_css = """
        <style>
            table { border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 25px 0; font-size: 0.9em; min-width: 400px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); }
            thead tr { background-color: #1e293b; color: #ffffff; text-align: left; font-weight: bold; }
            th, td { padding: 12px 15px; border-bottom: 1px solid #dddddd; }
            tbody tr:nth-of-type(even) { background-color: #f8fafc; }
            tbody tr:last-of-type { border-bottom: 2px solid #1e293b; }
        </style>
        """

        return custom_css + styled.to_html()
