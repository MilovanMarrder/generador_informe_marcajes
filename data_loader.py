import tabula
import pandas as pd


def load_pdf(path: str) -> pd.DataFrame:
    """
    Lee el PDF de marcajes y devuelve un DataFrame con columna 'Fecha/Hora' en datetime.
    """
    df = tabula.read_pdf(path, pages="all", multiple_tables=False)[0]
    df.rename(columns={"ID de\rusuario": "ID"}, inplace=True)
    df.drop(columns=[col for col in df.columns if 'Unnamed' in col], inplace=True, errors='ignore')
    df['Fecha/Hora'] = pd.to_datetime(df['Fecha/Hora'], errors='coerce')
    return df
