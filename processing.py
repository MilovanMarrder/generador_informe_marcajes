import pandas as pd
from datetime import datetime


def compute_basic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas: Fecha, Entrada, Salida, Jornada, Mes, Dia_semana, Fin_de_semana.
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


def fechas_inicio_fin(df: pd.DataFrame) -> dict:
    """
    Diccionario con fechas de inicio y fin de los datos.
    """
    return {
        'inicio': df['Fecha/Hora'].min(),
        'fin': df['Fecha/Hora'].max()
    }


def get_detalles_marcajes(tabla: pd.DataFrame) -> dict:
    """
    Convierte el DataFrame de marcajes en un dict: Nombre → lista de registros.
    Cada registro es un dict con claves Fecha, Entrada, Salida, Jornada.
    """
    detalles = {}
    for nombre, grp in tabla.groupby('Nombre'):
        registros = []
        for _, row in grp.iterrows():
            registros.append({
                'Fecha': row['Fecha'],
                'Entrada': row['Entrada'],
                'Salida': row['Salida'],
                'Jornada': row['Jornada']
            })
        detalles[nombre] = registros
    return detalles


def compute_outliers_por_persona(outliers: pd.DataFrame) -> dict:
    """
    Agrupa el DataFrame de outliers por Nombre y devuelve dict: Nombre → lista de registros.
    """
    return {
        nombre: grp.to_dict('records')
        for nombre, grp in outliers.groupby('Nombre')
    }


def compute_resumen_mensual(detalles_marcajes: dict) -> dict:
    """
    Para cada persona en detalles_marcajes, calcula un resumen mensual con horas y días trabajados.
    Devuelve dict: Nombre → lista de dicts con claves Mes, Horas, Dias.
    """
    resumen = {}
    for nombre, regs in detalles_marcajes.items():
        df = pd.DataFrame(regs)
        # Asegurar tipo datetime en Fecha
        if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
            df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Mes'] = df['Fecha'].dt.to_period('M').dt.strftime('%Y-%m')
        pivot = (
            df.groupby('Mes')
              .agg(
                Horas=('Jornada', lambda x: x.sum().total_seconds()/3600),
                Dias=('Fecha', lambda x: x.dt.date.nunique())
              )
              .reset_index()
              .to_dict('records')
        )
        resumen[nombre] = pivot
    return resumen

