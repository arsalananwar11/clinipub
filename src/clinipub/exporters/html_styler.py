import pandas as pd


class JournalHTMLExporter:
    """Applies journal-specific typography, padding, and border CSS styles
    to clinical data tables to match target manuscript guidelines.
    """

    STYLES = {
        "nejm": {
            "font-family": "'Times New Roman', Times, serif",
            "table-border-top": "2px solid #000000",
            "table-border-bottom": "2px solid #000000",
            "header-border-bottom": "1px solid #000000",
            "row-border-bottom": "none",
            "background": "#ffffff",
            "th-padding": "6px 12px",
            "td-padding": "4px 12px",
            "font-size": "13px",
            "text-transform": "none",
        },
        "jama": {
            "font-family": "Arial, Helvetica, sans-serif",
            "table-border-top": "3px solid #111111",
            "table-border-bottom": "3px solid #111111",
            "header-border-bottom": "1px solid #111111",
            "row-border-bottom": "1px solid #e2e8f0",
            "background": "#f8fafc",
            "th-padding": "10px 14px",
            "td-padding": "8px 14px",
            "font-size": "12px",
            "text-transform": "uppercase",
        },
        "lancet": {
            "font-family": "Geneva, Tahoma, sans-serif",
            "table-border-top": "1px solid #333333",
            "table-border-bottom": "1px solid #333333",
            "header-border-bottom": "1px solid #333333",
            "row-border-bottom": "1px solid #eeeeee",
            "background": "#ffffff",
            "th-padding": "4px 8px",
            "td-padding": "4px 8px",
            "font-size": "11px",
            "text-transform": "none",
        },
    }

    def __init__(self, table_df: pd.DataFrame, journal: str = "nejm"):
        if table_df.empty:
            raise ValueError("The input DataFrame cannot be empty.")

        journal_key = journal.lower().strip()
        if journal_key not in self.STYLES:
            raise ValueError(
                f"Unsupported journal style '{journal}'. Choose from: {list(self.STYLES.keys())}"
            )

        self.table_df = table_df.copy()
        self.journal = journal_key
        self.cfg = self.STYLES[self.journal]

    def export(self) -> str:
        """Compiles the DataFrame into an HTML string embedded with strict
        journal-specific CSS typography and alignment rules.
        """
        # Convert dataframe directly to basic HTML representation
        raw_html = self.table_df.to_html(classes="clinipub-table")

        # Construct targeted semantic wrapper injection
        styled_html = f"""
        <style>
            .clinipub-container {{
                padding: 20px;
                background-color: #ffffff;
                display: inline-block;
            }}
            table.clinipub-table {{
                font-family: {self.cfg['font-family']};
                font-size: {self.cfg['font-size']};
                border-collapse: collapse;
                border-top: {self.cfg['table-border-top']};
                border-bottom: {self.cfg['table-border-bottom']};
                min-width: 600px;
            }}
            table.clinipub-table thead tr th {{
                padding: {self.cfg['th-padding']};
                border-bottom: {self.cfg['header-border-bottom']};
                text-align: left;
                font-weight: bold;
                background-color: #ffffff;
            }}
            table.clinipub-table tbody tr td {{
                padding: {self.cfg['td-padding']};
                border-bottom: {self.cfg['row-border-bottom']};
            }}
            table.clinipub-table tbody tr:nth-of-type(even) {{
                background-color: {self.cfg['background']};
            }}
            /* Clean indentation for sub-indexed groups */
            table.clinipub-table tbody tr td:first-child {{
                padding-left: 20px;
            }}
        </style>
        <div class="clinipub-container">
            {raw_html}
        </div>
        """
        return styled_html
