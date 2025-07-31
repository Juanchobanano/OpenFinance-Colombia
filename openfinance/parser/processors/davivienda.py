import pandas as pd
from openfinance.parser.processors.processor import (
    FinancialStatementPreprocessor
)


class CreditCardDaviviendaStatementPreprocessor(FinancialStatementPreprocessor):
    """
    A class to preprocess Davivienda CSV data extracted
    from PDF statements for credit cards.
    """

    def __init__(self,
                 input_path: str,
                 csv_files: list[str],
                 output_folder: str):
        super().__init__(
            input_path=input_path,
            csv_files=csv_files,
            output_folder=output_folder)

    def preprocess(self, df: pd.DataFrame = None) -> pd.DataFrame:
        return df
