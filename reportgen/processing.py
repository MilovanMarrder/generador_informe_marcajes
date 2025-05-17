import pandas as pd
from datetime import datetime
from collections import defaultdict


def compute_basic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas: Fecha, Entrada, Salida, Jornada, Mes, Dia_semana, Fin_de_semana.
    """
    df['Fecha/Hora'] = pd.to_datetime(df['Fecha/Hora'], errors='coerce')
    df['Nombre'] = df['Nombre'].str.title()
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


def detect_outliers_jornada(tabla: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
    """
    Detecta outliers en la duración de la jornada por IQR para cada persona.
    Devuelve un DataFrame con las filas atípicas e incluye columna 'Tipo' (Baja/Alta).
    """
    lista_outliers = []
    for nombre, grp in tabla.groupby('Nombre'):
        horas = grp['Jornada'].dt.total_seconds() / 3600
        q1, q3 = horas.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        mask = (horas < lower) | (horas > upper)
        out = grp.loc[mask].copy()
        out['Tipo'] = out['Jornada'].apply(
            lambda j: 'Baja' if (j.total_seconds()/3600) < lower else 'Alta'
        )
        lista_outliers.append(out)
    if lista_outliers:
        return pd.concat(lista_outliers).reset_index(drop=True)
    else:
        # Ningún outlier detectado, devolver DataFrame vacío con mismas columnas
        cols = list(tabla.columns) + ['Tipo']
        return pd.DataFrame(columns=cols)


def construir_resumen_fusionado(detalles_marcajes: dict) -> list:
    """
    Construye un resumen fusionado por Mes, Tipo de Día y Empleado
    basado en los detalles de marcajes.
    """
    registros = []
    for nombre, registros_empleado in detalles_marcajes.items():
        for r in registros_empleado:
            registros.append({
                "Nombre": nombre,
                "Fecha": pd.to_datetime(r["Fecha"]),
                "Horas_trabajadas": r["Jornada"].total_seconds() / 3600
            })

    df = pd.DataFrame(registros)
    if df.empty:
        return []

    df["Mes"] = df["Fecha"].dt.strftime("%B %Y")
    df["Tipo_dia"] = df["Fecha"].dt.weekday.apply(lambda x: "Fin de semana" if x >= 5 else "Día de semana")

    resumen = df.groupby(["Mes", "Tipo_dia", "Nombre"]).agg(
        Dias_trabajados=("Fecha", "count"),
        Total_horas=("Horas_trabajadas", "sum")
    ).reset_index()

    return resumen.to_dict(orient="records")



def agrupar_resumen_por_mes(resumen_fusionado: list) -> dict:
    """
    Agrupa el resumen fusionado por Mes.
    """
    resumen_por_mes = defaultdict(list)
    for row in resumen_fusionado:
        resumen_por_mes[row['Mes']].append(row)
    return dict(resumen_por_mes)



def agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado: list) -> dict:
    """
    Agrupa el resumen fusionado por Mes y Tipo de Día,
    y ordena por Días trabajados (descendente) y luego Promedio de jornada (descendente).
    """
    resumen_organizado = defaultdict(lambda: defaultdict(list))

    for row in resumen_fusionado:
        # Calcular horas promedio de jornada
        promedio_jornada = row["Total_horas"] / row["Dias_trabajados"] if row["Dias_trabajados"] else 0.0

        resumen_organizado[row["Mes"]][row["Tipo_dia"]].append({
            "Nombre": row["Nombre"],
            "Dias_trabajados": row["Dias_trabajados"],
            "Total_horas": row["Total_horas"],
            "Promedio_jornada": promedio_jornada
        })

    # Ordenar dentro de cada grupo
    for mes, tipos_dia in resumen_organizado.items():
        for tipo, registros in tipos_dia.items():
            registros.sort(
                key=lambda x: (x['Dias_trabajados'], x['Promedio_jornada']), 
                reverse=True
            )

    return {mes: dict(tipos_dia) for mes, tipos_dia in resumen_organizado.items()}