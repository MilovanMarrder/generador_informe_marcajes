import pandas as pd
from datetime import datetime


def compute_basic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas: Fecha, Entrada, Salida, Jornada, Mes, Fin_de_semana.
    """
    df['Fecha'] = df['Fecha/Hora'].dt.date
    df['tipo'] = df['Fecha/Hora'].apply(
        lambda h: 'Entrada' if h.time() < datetime.strptime('12:00','%H:%M').time() else 'Salida'
    )
    tabla = df.pivot_table(
        index=['Nombre','Fecha'],
        columns='tipo',
        values='Fecha/Hora',
        aggfunc='last'
    ).reset_index()
    tabla = tabla.dropna(subset=['Entrada','Salida'])
    tabla['Jornada'] = tabla['Salida'] - tabla['Entrada']
    tabla['Mes'] = tabla['Fecha'].apply(lambda d: d.strftime('%B %Y'))
    tabla['Dia_semana'] = tabla['Entrada'].dt.weekday
    tabla['Fin_de_semana'] = tabla['Dia_semana'] >= 5
    return tabla
