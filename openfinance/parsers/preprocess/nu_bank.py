import pandas as pd
import os
import re
import openfinance.constants as ct
import numpy as np


def concatenate_csv_to_df(csv_files: list[str]) -> pd.DataFrame:

    # Extract chunk numbers from filenames
    chunk_files = [f for f in csv_files if "chunk_" in os.path.basename(f)]
    chunk_nums = []
    for f in chunk_files:
        m = re.search(r'chunk_(\d+)', os.path.basename(f))
        if m:
            chunk_nums.append(int(m.group(1)))
    if chunk_nums:
        last_chunk_num = max(chunk_nums)
        filtered_files = [
            f for f in csv_files
            if not (
                ("chunk_1" in os.path.basename(f)) or
                (f"chunk_{last_chunk_num}" in os.path.basename(f))
            )
        ]
    else:
        filtered_files = csv_files.copy()

    # filtered_files now contains only the files WITHOUT 'chunk_1'
    # and the last chunk
    df_list = [pd.read_csv(file) for file in filtered_files]
    concatenated_df = pd.concat(df_list, ignore_index=True)
    return concatenated_df


def preprocess_nu_bank(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the Nu Bank dataframe.
    """
    # 1. Fecha: Convert to datetime
    for esp, eng in ct.month_map.items():
        df['Fecha'] = df['Fecha'].str.replace(esp, eng, regex=False)
    df['Fecha'] = pd.to_datetime(
        df['Fecha'], format='%d %b %Y', errors='coerce')

    # 2. Descripción: Keep as string (strip whitespace)
    df['Descripción'] = df['Descripción'].astype(str).str.strip()

    # 3. Valor: Convert "$74.497,45" to float (74497.45)
    df['Valor'] = df['Valor'].astype(str).apply(lambda z: z.split(" ")[0])
    df['Valor'] = df['Valor'].apply(parse_money)

    df['Valor del mes'] = df['Valor del mes'].astype(str).apply(lambda z: z.split(" ")[0])
    df['Valor del mes'] = df['Valor del mes'].apply(parse_money)

    df['Interés Porcentaje'] = df['Interés Porcentaje'].apply(parse_percent)
    df['del mes y valor'] = df['del mes y valor'].astype(str).apply(lambda z: z.split(" ")[0])
    df['del mes y valor'] = df['del mes y valor'].apply(parse_money)

    df['Comisión por cambio'] = df['Total a pagar este mes'].astype(str).apply(extract_comision)
    df['Comisión por cambio'] = df['Comisión por cambio'].apply(parse_money)
    df['Total a pagar este mes'] = df['Total a pagar este mes'].astype(str).apply(lambda z: z.split(" ")[0])
    df['Total a pagar este mes'] = df['Total a pagar este mes'].apply(parse_money)

    df['Restante por pagar'] = df['Restante por pagar'].apply(parse_money)

    df[['num_cuota_actual', 'num_cuotas']] = df['Cuotas'].apply(
        lambda x: pd.Series(parse_cuotas(x)))

    # lower case and remove accents and spaces from columns names
    df.columns = (
        df.columns.str.lower()
        .str.replace(' ', '_')
        .str.replace('á', 'a')
        .str.replace('é', 'e')
        .str.replace('í', 'i')
        .str.replace('ó', 'o')
        .str.replace('ú', 'u')
    )
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
    df = df.rename(columns=columns_mapping_dict)
    df = df.drop(columns=["cuotas"])
    return df


def parse_fecha(fecha_str: str) -> pd.Timestamp:
    # Example: '17 MAY 2025'
    try:
        return pd.to_datetime(fecha_str, format='%d %b %Y', errors='coerce')
    except Exception:
        return pd.NaT


def parse_money(val: str) -> float:
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


def parse_cuotas(cuota: str) -> tuple[int, int]:
    if pd.isnull(cuota):
        return (np.nan, np.nan)
    m = re.search(r'(\d+)\s*de\s*(\d+)', str(cuota))
    if m:
        return int(m.group(1)), int(m.group(2))
    else:
        return (np.nan, np.nan)


def parse_percent(val: str) -> float:
    if pd.isnull(val):
        return np.nan
    val = str(val).replace('%', '').replace(',', '.')
    try:
        return float(val) / 100
    except Exception:
        return np.nan


def extract_comision(val):
    parts = str(val).split(" ")
    if len(parts) > 1:
        return parts[1]
    else:
        return np.nan
