from abc import ABC, abstractmethod
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


class FinancialStatementPreprocessor(ABC):
    """Abstract base class for financial statement preprocessors."""

    def __init__(self,
                 input_path: str,
                 csv_files: list[str],
                 output_folder: str):
        self.input_path = input_path
        self.csv_files = csv_files
        self.output_folder = output_folder

    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the financial statement data."""
        return df

    def process_financial_statement(
        self
    ) -> pd.DataFrame:
        """
        Preprocess the CSV files and save the final result.

        Returns:
            str: Path to the final processed CSV file
        """
        logger.info("Preprocessing CSV files ...")
        df = self.concatenate_csv_files(
            csv_files=self.csv_files
        )
        df = self.preprocess(df)
        self.output_csv_path = (
            f"{self.output_folder}/{os.path.basename(self.input_path)}.csv")
        df.to_csv(self.output_csv_path, index=False)

        logger.info(f"CSV file saved to {self.output_csv_path}")
        return self.output_csv_path

    def concatenate_csv_files(
        self,
        csv_files: list[str],
    ) -> pd.DataFrame:
        """
        Concatenate multiple CSV files into a single DataFrame.
        If the CSV files have different columns,
        the function will return a DataFrame with the most common columns.
        """
        dfs = [pd.read_csv(f) for f in csv_files]
        # Only merge dataframes in dfs that have the same columns
        if dfs:
            # Find the set of columns for each dataframe
            columns_list = [tuple(df.columns) for df in dfs]
            # Find the most common columns set (mode)
            from collections import Counter
            most_common_columns = Counter(columns_list).most_common(1)[0][0]
            # Filter dfs to only those with the most common columns
            dfs_same_cols = [
                df for df in dfs if tuple(df.columns) == most_common_columns]
            if dfs_same_cols:
                merged_df = pd.concat(dfs_same_cols, ignore_index=True)
            else:
                merged_df = pd.DataFrame(columns=most_common_columns)
        else:
            merged_df = pd.DataFrame()
        return merged_df
