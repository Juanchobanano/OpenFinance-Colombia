from openfinance.parser.processors.processor import (
    FinancialStatementPreprocessor)
import pandas as pd
import numpy as np


class CreditCardItauStatementPreprocessor(FinancialStatementPreprocessor):
    """
    A class to preprocess Itau CSV data extracted
    from PDF statements for credit cards.
    """

    def __init__(self,
                 input_path: str,
                 csv_files: list[str],
                 output_folder: str):
        """Initialize the CreditCardItauStatementPreprocessor."""
        super().__init__(
            input_path=input_path,
            csv_files=csv_files,
            output_folder=output_folder
        )

    def preprocess(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Preprocess the Itau dataframe.
        """
        if df is not None:
            self.df = df.copy()

        if self.df is None:
            raise ValueError(
                "No DataFrame to preprocess. "
                "Call concatenate_csv_files first.")

        # 1. Remove rows with missing "Fecha"
        self.df = self.df[self.df["Fecha"].notna()].copy()

        # 2. Process "Fecha" column (DD/MM/YY to datetime)
        self._process_fecha()

        # 3. Drop unnecessary columns
        self._drop_unnecessary_columns()

        # 4. Process monetary columns
        self._process_monetary_columns()

        # 5. Process installments
        self._process_installments()

        # 6. Process interest percentage
        self._process_interest_percentage()

        # 7. Clean column names (optional, not strictly needed for Itau)

        # 8. Rename columns to English
        self._rename_columns()

        # 9. Add bank_name column
        self.df["bank_name"] = "itau"

        # 10. Drop original "Cuotas" column if present
        if "Cuotas" in self.df.columns:
            self.df = self.df.drop(columns=["Cuotas"])

        self.processed_df = self.df.copy()
        return self.processed_df

    def _process_fecha(self):
        """Convert 'Fecha' from DD/MM/YY to datetime."""
        self.df["Fecha"] = pd.to_datetime(
            self.df["Fecha"], format="%d/%m/%y", errors="coerce")

    def _drop_unnecessary_columns(self):
        """Drop columns not needed for analysis."""
        if "Número de Comprobante" in self.df.columns:
            self.df = self.df.drop(columns=["Número de Comprobante"])

    def _process_monetary_columns(self):
        """Process monetary columns to float."""
        for col in ["Valor original", "Valor cuota", "Saldo pendiente"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).apply(
                    self._process_money)

    def _process_installments(self):
        """Process 'Cuotas' column into
        'Cuota actual' and 'Total de cuotas'."""
        if "Cuotas" in self.df.columns:
            cuotas = self.df["Cuotas"].astype(str).apply(self._process_cuotas)
            self.df["Cuota actual"] = [c[0] for c in cuotas]
            self.df["Total de cuotas"] = [c[1] for c in cuotas]

    def _process_interest_percentage(self):
        """Convert 'Tasa EA' to float (as a fraction, not percent)."""
        if "Tasa EA" in self.df.columns:
            self.df["Tasa EA"] = (
                self.df["Tasa EA"]
                .astype(str)
                .apply(lambda z: self._parse_interest_percentage(z))
            )

    def _rename_columns(self):
        """Rename columns to English names."""
        columns_mapping_dict = {
            "Fecha": "txn_date",
            "Descripción": "description",
            "Valor original": "amount",
            "Valor cuota": "amount_this_month",
            "Tasa EA": "interest_percentage",
            "Valor Cuota": "total_to_pay_this_month",  # Not always present
            "Saldo pendiente": "remaining_to_pay",
            "Cuota actual": "current_installment_number",
            "Total de cuotas": "total_installments"
        }
        self.df = self.df.rename(columns=columns_mapping_dict)

    def _process_money(self, val: str) -> float:
        """Parse money string to float."""
        if pd.isnull(val):
            return np.nan
        val = (
            str(val)
            .replace(".", "")
            .replace(",", ".")
            .replace("$", "")
            .replace(" ", "")
        )
        try:
            return float(val)
        except Exception:
            return np.nan

    def _process_cuotas(self, val: str) -> tuple:
        """Parse installment string like '3/12' into (3, 12)."""
        if pd.isnull(val):
            return (np.nan, np.nan)
        if "/" in val:
            try:
                actual, total = val.split("/")
                return int(actual), int(total)
            except Exception:
                return (np.nan, np.nan)
        else:
            return (np.nan, np.nan)

    def _parse_interest_percentage(self, val: str) -> float:
        """Parse interest percentage string to float (as a fraction)."""
        if pd.isnull(val):
            return np.nan
        val = str(val).replace("%", "").replace(",", ".").strip()
        try:
            return float(val) / 100
        except Exception:
            return np.nan
