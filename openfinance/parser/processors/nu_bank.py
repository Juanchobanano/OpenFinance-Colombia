import pandas as pd
import re
import openfinance.constants as ct
import numpy as np
from openfinance.parser.processors.processor import (
    FinancialStatementPreprocessor
)


class CreditCardNuBankStatementPreprocessor(FinancialStatementPreprocessor):
    """
    A class to preprocess Nu Bank CSV data extracted
    from PDF statements for credit cards.
    """

    def __init__(
            self,
            input_path: str,
            csv_files: list[str],
            output_folder: str):
        """Initialize the CreditCardNuBankStatementPreprocessor."""
        super().__init__(
            input_path=input_path,
            csv_files=csv_files,
            output_folder=output_folder
        )

    def preprocess(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Preprocess the Nu Bank dataframe.

        Args:
            df (pd.DataFrame, optional): DataFrame to preprocess.
                                       If None, uses self.df
        Returns:
            pd.DataFrame: Preprocessed DataFrame
        """
        if df is not None:
            self.df = df.copy()

        if self.df is None:
            raise ValueError(
                "No DataFrame to preprocess. "
                "Call concatenate_csv_files first.")

        # 1. Fecha: Convert to datetime
        self._process_fecha()

        # 2. Descripción: Keep as string (strip whitespace)
        self._process_descripcion()

        # 3. Process monetary values
        self._process_monetary_values()

        # 4. Process percentages
        self._process_percentages()

        # 5. Process installments
        self._process_installments()

        # 6. Clean column names
        self._clean_column_names()

        # 7. Rename columns to English
        self._rename_columns()

        # 8. Add bank_name column
        self.df["bank_name"] = "nu_bank"

        self.processed_df = self.df.copy()
        return self.processed_df

    def _process_fecha(self):
        """Process the Fecha column to convert to datetime."""
        for esp, eng in ct.month_map.items():
            self.df['Fecha'] = self.df['Fecha'].str.replace(
                esp, eng, regex=False)
        self.df['Fecha'] = pd.to_datetime(
            self.df['Fecha'], format='%d %b %Y', errors='coerce')

    def _process_descripcion(self):
        """Process the Descripción column."""
        self.df['Descripción'] = self.df['Descripción'].astype(str).str.strip()

    def _process_monetary_values(self):
        """Process all monetary value columns."""
        # Valor
        self.df['Valor'] = (
            self.df['Valor']
            .astype(str)
            .apply(lambda z: z.split(" ")[0])
            .apply(self._parse_money)
        )

        # Valor del mes
        self.df['Valor del mes'] = self.df['Valor del mes'].astype(str).apply(
            lambda z: z.split(" ")[0])
        self.df['Valor del mes'] = (
            self.df['Valor del mes']
            .apply(self._parse_money)
        )

        # del mes y valor
        self.df['del mes y valor'] = (
            self.df['del mes y valor']
            .astype(str)
            .apply(lambda z: z.split(" ")[0])
            .apply(self._parse_money)
        )

        # Comisión por cambio
        self.df['Comisión por cambio'] = (
            self.df['Total a pagar este mes']
            .astype(str)
            .apply(self._extract_comision)
            .apply(self._parse_money)
        )

        # Total a pagar este mes
        self.df['Total a pagar este mes'] = (
            self.df['Total a pagar este mes']
            .astype(str)
            .apply(lambda z: z.split(" ")[0])
            .apply(self._parse_money)
        )

        # Restante por pagar
        self.df['Restante por pagar'] = (
            self.df['Restante por pagar']
            .apply(self._parse_money)
        )

    def _process_percentages(self):
        """Process percentage columns."""
        self.df['Interés Porcentaje'] = (
            self.df['Interés Porcentaje']
            .apply(self._parse_percent)
        )

    def _process_installments(self):
        """Process installment information."""
        self.df[['num_cuota_actual', 'num_cuotas']] = (
            self.df['Cuotas']
            .apply(lambda x: pd.Series(self._parse_cuotas(x)))
        )

    def _clean_column_names(self):
        """Clean column names by removing accents and spaces."""
        self.df.columns = (
            self.df.columns.str.lower()
            .str.replace(' ', '_')
            .str.replace('á', 'a')
            .str.replace('é', 'e')
            .str.replace('í', 'i')
            .str.replace('ó', 'o')
            .str.replace('ú', 'u')
        )

    def _rename_columns(self):
        """Rename columns to English names."""
        columns_mapping_dict = {
            "fecha": "txn_date",
            "descripcion": "description",
            "valor": "amount",
            "valor_del_mes": "amount_this_month",
            "interes_porcentaje": "interest_percentage",
            "del_mes_y_valor": "interest_amount",
            "total_a_pagar_este_mes": "total_to_pay_this_month",
            "restante_por_pagar": "remaining_to_pay",
            "comision_por_cambio": "forex_comission",
            "num_cuota_actual": "current_installment_number",
            "num_cuotas": "total_installments"
        }
        self.df = self.df.rename(columns=columns_mapping_dict)
        self.df = self.df.drop(columns=["cuotas"])

    def _parse_fecha(self, fecha_str: str) -> pd.Timestamp:
        """Parse fecha string to timestamp."""
        # Example: '17 MAY 2025'
        try:
            return pd.to_datetime(
                fecha_str, format='%d %b %Y', errors='coerce')
        except Exception:
            return pd.NaT

    def _parse_money(self, val: str) -> float:
        """Parse money string to float."""
        if pd.isnull(val):
            return np.nan
        val = (
            str(val)
            .replace('.', '')
            .replace('$', '')
            .replace(' ', '')
            .replace(',', '.')
        )
        try:
            return float(val)
        except Exception:
            return np.nan

    def _parse_cuotas(self, cuota: str) -> tuple[int, int]:
        """Parse installment information."""
        if pd.isnull(cuota):
            return (np.nan, np.nan)
        m = re.search(r'(\d+)\s*de\s*(\d+)', str(cuota))
        if m:
            return int(m.group(1)), int(m.group(2))
        else:
            return (np.nan, np.nan)

    def _parse_percent(self, val: str) -> float:
        """Parse percentage string to float."""
        if pd.isnull(val):
            return np.nan
        val = str(val).replace('%', '').replace(',', '.')
        try:
            return float(val) / 100
        except Exception:
            return np.nan

    def _extract_comision(self, val):
        """Extract commission from string."""
        parts = str(val).split(" ")
        if len(parts) > 1:
            return parts[1]
        else:
            return np.nan
