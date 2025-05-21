import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

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

def get_detalles_marcajes_por_mes(tabla: pd.DataFrame) -> dict:
    """
    Convierte el DataFrame de marcajes en un dict:
    {Nombre: {Mes: [registros]}}
    Cada registro es un dict con claves Fecha, Entrada, Salida, Jornada.
    Se asegura de que 'Jornada' sea un objeto datetime.timedelta nativo de Python.
    """
    detalles = {}

    # Crear una copia para evitar modificar el DataFrame original
    tabla_copia = tabla.copy()

    # Asegurar que Fecha sea datetime para poder extraer el mes
    if not pd.api.types.is_datetime64_any_dtype(tabla_copia['Fecha']):
        tabla_copia['Fecha'] = pd.to_datetime(tabla_copia['Fecha'])

    # Añadir columna de mes
    tabla_copia['Mes'] = tabla_copia['Fecha'].dt.strftime('%B %Y')

    for nombre, grp in tabla_copia.groupby('Nombre'):
        detalles[nombre] = {}

        for mes, mes_grp in grp.groupby('Mes'):
            registros = []
            for _, row in mes_grp.iterrows():
                # Obtener la jornada del DataFrame
                jornada_pandas = row['Jornada']

                # Convertir a datetime.timedelta nativo de Python
                # Usamos 'timedelta' directamente ya que lo importamos explícitamente
                jornada_python = timedelta(seconds=0) # Valor por defecto

                if isinstance(jornada_pandas, pd.Timedelta):
                    # Si ya es un Timedelta de Pandas, convertir a segundos y luego a timedelta de Python
                    jornada_python = timedelta(seconds=jornada_pandas.total_seconds())
                elif jornada_pandas is not pd.NaT:
                    # Si no es un Timedelta de Pandas y no es NaT, intentar convertir
                    try:
                        # Intentar convertir a Timedelta de Pandas primero, luego a Python
                        temp_timedelta = pd.Timedelta(jornada_pandas)
                        jornada_python = timedelta(seconds=temp_timedelta.total_seconds())
                    except Exception as e:
                        print(f"Advertencia: No se pudo convertir Jornada a Timedelta para {nombre}, {row['Fecha']}. Error: {e}")
                        # Si falla la conversión, jornada_python sigue siendo timedelta(0)

                registros.append({
                    'Fecha': row['Fecha'],
                    'Entrada': row['Entrada'],
                    'Salida': row['Salida'],
                    'Jornada': jornada_python # Usar el objeto datetime.timedelta nativo
                })
            if registros: # Asegurarse de que hay registros para ese mes
                detalles[nombre][mes] = registros

    return detalles




def compute_outliers_por_persona_y_mes(outliers: pd.DataFrame) -> dict:
    """
    Agrupa el DataFrame de outliers por Nombre y Mes, devuelve:
    {Nombre: {Mes: [registros]}}
    """
    if outliers is None or outliers.empty:
        return {}
    
    # Crear una copia para evitar modificar el DataFrame original    
    outliers_copia = outliers.copy()
        
    # Asegurar que Fecha sea datetime para poder extraer el mes
    if not pd.api.types.is_datetime64_any_dtype(outliers_copia['Fecha']):
        outliers_copia['Fecha'] = pd.to_datetime(outliers_copia['Fecha'])
    
    # Añadir columna de mes
    outliers_copia['Mes'] = outliers_copia['Fecha'].dt.strftime('%B %Y')
    
    resultado = {}
    for nombre, grp in outliers_copia.groupby('Nombre'):
        resultado[nombre] = {}
        for mes, mes_grp in grp.groupby('Mes'):
            resultado[nombre][mes] = mes_grp.to_dict('records')
            
    return resultado