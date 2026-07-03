import numpy as np
import pandas as pd
from scipy import stats


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

    def run_mcar_test(self) -> dict:
        """Executes Roderick Little's MCAR multivariate hypothesis test on numeric features.

        Evaluates the null hypothesis (H0) that the data elements are Missing Completely
        At Random (MCAR).

        Returns
        -------
        dict
            A summary dictionary containing the following keys:
            
            `statistic` (float): The calculated Chi-Square (χ²) distance metric.
              Represents the global deviation between the missingness pattern subgroups
              and the grand dataset means.
              Range: [0.0, +∞). A value of 0.0 indicates perfect structural alignment.
              
            `degrees_of_freedom` (int): Degrees of Freedom. The number of independent pieces of 
              information across unique missingness configurations used to evaluate the statistic.
              Range: [1, +∞).
              
            `p_value` (float): The probability score used to accept or reject the null hypothesis.
              Range: [0.0, 1.0].
              
              - p >= 0.05: Fail to reject H0. Missingness is likely random (MCAR). Complete-case analysis is safe.
              - p < 0.05: Reject H0. Missingness is systematic (MAR/MNAR). Dropping rows introduces heavy bias; Multiple Imputation is mandatory.
        """
        numeric_data = self.data.select_dtypes(include=[np.number])

        if numeric_data.empty or numeric_data.isnull().sum().sum() == 0:
            return {"statistic": 0.0, "p_value": 1.0, "degrees_of_freedom": 0}

        # Vectorized calculations via underlying NumPy arrays
        X = numeric_data.values
        n_samples, n_features = X.shape

        global_mean = np.nanmean(X, axis=0)
        
        # Fast covariance computation skipping NaNs pairwise or via global fill
        # For global inversion structural integrity, we use an efficient mean-fill covariance matrix
        X_filled = np.where(np.isnan(X), global_mean, X)
        global_cov = np.cov(X_filled, rowvar=False)

        # Inversion with ridge regularization guardrail
        if np.linalg.det(global_cov) == 0:
            global_cov += np.diag(np.ones(n_features) * 1e-6)
        inv_global_cov = np.linalg.inv(global_cov)

        # Fast Vectorized Pattern Detection: Instead of iterating over rows, we identify unique missingness patterns and their counts
        missing_mask = np.isnan(X)
        unique_patterns, inverse_indices = np.unique(missing_mask, axis=0, return_inverse=True)

        chi_sq_stat = 0.0
        degrees_of_freedom = 0

        # Loop only over UNIQUE missingness configurations (typically very small, e.g., < 50 patterns)
        for pattern_idx, pattern in enumerate(unique_patterns):
            # Locate all row indices belonging to this specific missingness configuration
            group_mask = (inverse_indices == pattern_idx)
            n_pattern = np.sum(group_mask)

            # Identify completely observed columns in this pattern (where missing is False)
            obs_indices = np.where(~pattern)[0]
            if len(obs_indices) == 0:
                continue

            # Directly extract slice of rows matching this pattern using mask indexing
            sub_X_obs = X[group_mask[:, None] & ~missing_mask]
            # Reshape securely to match matrix requirements
            sub_X_obs = sub_X_obs.reshape(n_pattern, len(obs_indices))

            # Compute localized mean via highly efficient NumPy math
            pattern_mean = np.mean(sub_X_obs, axis=0)
            diff_vector = pattern_mean - global_mean[obs_indices]

            # Slice inverse covariance matrix using NumPy meshgrid indexing
            sub_inv_cov = inv_global_cov[np.ix_(obs_indices, obs_indices)]

            # Mahalanobis matrix distance multiplication
            pattern_chi_sq = n_pattern * (diff_vector @ sub_inv_cov @ diff_vector)
            chi_sq_stat += pattern_chi_sq
            degrees_of_freedom += len(obs_indices)

        degrees_of_freedom = max(1, degrees_of_freedom - n_features)
        p_value = 1.0 - stats.chi2.cdf(chi_sq_stat, degrees_of_freedom)

        return {
            "statistic": float(chi_sq_stat),
            "p_value": float(p_value),
            "degrees_of_freedom": int(degrees_of_freedom),
        }
