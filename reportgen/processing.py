import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict



def get_detalles_marcajes(tabla: pd.DataFrame) -> dict:
    """
    Convierte el DataFrame de marcajes en un dict: Nombre → lista de registros.
    Cada registro es un dict con claves fecha, Entrada, Salida, Jornada.
    """
    detalles = {}
    for nombre, grp in tabla.groupby('nombre'):
        registros = []
        for _, row in grp.iterrows():
            registros.append({
                'fecha': row['fecha'],
                'entrada': row['entrada'],
                'salida': row['salida'],
                'jornada': row['jornada']
            })
        detalles[nombre] = registros
    return detalles


def compute_outliers_por_persona(outliers: pd.DataFrame) -> dict:
    """
    Agrupa el DataFrame de outliers por Nombre y devuelve dict: Nombre → lista de registros.
    """
    return {
        nombre: grp.to_dict('records')
        for nombre, grp in outliers.groupby('nombre')
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
        if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
            df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Si jornada es datetime, convertir a horas desde medianoche
        # Convertir jornada a horas numéricas
        if pd.api.types.is_timedelta64_dtype(df['jornada']):
            # Si es timedelta, convertir a horas numéricas
            df['horas_trabajadas'] = df['jornada'].dt.total_seconds() / 3600
        elif pd.api.types.is_datetime64_any_dtype(df['jornada']):
            # Si es datetime, extraer solo la parte de tiempo (horas desde medianoche)
            df['horas_trabajadas'] = df['jornada'].dt.hour + df['jornada'].dt.minute/60 + df['jornada'].dt.second/3600
        else:
            # Si es numérico, mantener como está
            df['horas_trabajadas'] = pd.to_numeric(df['jornada'], errors='coerce')         
            

        df['mes'] = df['fecha'].dt.to_period('M').dt.strftime('%Y-%m')
        pivot = (
            df.groupby('mes')
              .agg(
                Horas=('horas_trabajadas', lambda x: round(x.sum(),2)),
                Dias=('fecha', lambda x: x.dt.date.nunique())
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
    for nombre, grp in tabla.groupby('nombre'):
        horas = grp['jornada'].dt.total_seconds() / 3600
        q1, q3 = horas.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        mask = (horas < lower) | (horas > upper)
        out = grp.loc[mask].copy()
        out['tipo'] = out['jornada'].apply(
            lambda j: 'Baja' if (j.total_seconds()/3600) < lower else 'Alta'
        )
        lista_outliers.append(out)
    if lista_outliers:
        return pd.concat(lista_outliers).reset_index(drop=True)
    else:
        # Ningún outlier detectado, devolver DataFrame vacío con mismas columnas
        cols = list(tabla.columns) + ['tipo']
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
                "nombre": nombre,
                "fecha": pd.to_datetime(r["fecha"]),
                "horas_trabajadas": r["jornada"].total_seconds() / 3600
            })

    df = pd.DataFrame(registros)
    if df.empty:
        return []

    df["mes"] = df["fecha"].dt.strftime("%B %Y")
    df["tipo_dia"] = df["fecha"].dt.weekday.apply(lambda x: "Fin de semana" if x >= 5 else "Día de semana")

    resumen = df.groupby(["mes", "tipo_dia", "nombre"]).agg(
        dias_trabajados=("fecha", "count"),
        total_horas=("horas_trabajadas", "sum")
    ).reset_index()

    return resumen.to_dict(orient="records")


def agrupar_resumen_por_mes(resumen_fusionado: list) -> dict:
    """
    Agrupa el resumen fusionado por Mes.
    """
    resumen_por_mes = defaultdict(list)
    for row in resumen_fusionado:
        resumen_por_mes[row['mes']].append(row)
    return dict(resumen_por_mes)


def agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado: list) -> dict:
    """
    Agrupa el resumen fusionado por Mes y Tipo de Día,
    y ordena por Días trabajados (descendente) y luego Promedio de jornada (descendente).
    """
    resumen_organizado = defaultdict(lambda: defaultdict(list))

    for row in resumen_fusionado:
        # Calcular horas promedio de jornada
        promedio_jornada = row["total_horas"] / row["dias_trabajados"] if row["dias_trabajados"] else 0.0

        resumen_organizado[row["mes"]][row["tipo_dia"]].append({
            "nombre": row["nombre"],
            "dias_trabajados": row["dias_trabajados"],
            "total_horas": row["total_horas"],
            "promedio_jornada": promedio_jornada
        })

    # Ordenar dentro de cada grupo
    for mes, tipos_dia in resumen_organizado.items():
        for tipo, registros in tipos_dia.items():
            registros.sort(
                key=lambda x: (x['dias_trabajados'], x['promedio_jornada']), 
                reverse=True
            )

    return {mes: dict(tipos_dia) for mes, tipos_dia in resumen_organizado.items()}

def get_detalles_marcajes_por_mes(tabla: pd.DataFrame) -> dict:
    """
    Convierte el DataFrame de marcajes en un dict:
    {nombre: {Mes: [registros]}}
    Cada registro es un dict con claves Fecha, Entrada, Salida, Jornada.
    Se asegura de que 'Jornada' sea un objeto datetime.timedelta nativo de Python.
    Los meses se ordenan cronológicamente.
    """
    detalles = {}
    tabla_copia = tabla.copy()

    if not pd.api.types.is_datetime64_any_dtype(tabla_copia['fecha']):
        tabla_copia['fecha'] = pd.to_datetime(tabla_copia['fecha'])

    # CAMBIO CLAVE: Añadir columna de mes como el primer día del mes
    tabla_copia['mes_ordenable'] = tabla_copia['fecha'].dt.to_period('M').dt.start_time

    for nombre, grp in tabla_copia.groupby('nombre'):
        # Aquí guardaremos temporalmente los meses para ordenarlos
        meses_temp = {}

        # Agrupar por la columna mes_ordenable
        for mes_dt, mes_grp in grp.groupby('mes_ordenable'):
            registros = []
            for _, row in mes_grp.iterrows():
                jornada_pandas = row['jornada']
                jornada_python = timedelta(seconds=0)

                if isinstance(jornada_pandas, pd.Timedelta):
                    jornada_python = timedelta(seconds=jornada_pandas.total_seconds())
                elif jornada_pandas is not pd.NaT:
                    try:
                        temp_timedelta = pd.Timedelta(jornada_pandas)
                        jornada_python = timedelta(seconds=temp_timedelta.total_seconds())
                    except Exception as e:
                        print(f"Advertencia: No se pudo convertir Jornada a Timedelta para {nombre}, {row['fecha']}. Error: {e}")

                registros.append({
                    'fecha': row['fecha'],
                    'entrada': row['entrada'],
                    'salida': row['salida'],
                    'jornada': jornada_python
                })
            if registros:
                # Almacenar el nombre legible del mes usando strftime
                mes_legible = mes_dt.strftime('%B %Y')
                meses_temp[mes_dt] = {'nombre_legible': mes_legible, 'registros': registros}

        # Ordenar los meses por su clave datetime (mes_dt)
        detalles[nombre] = {}
        for mes_dt_ordenado in sorted(meses_temp.keys()):
            # Usar el nombre legible para la clave del diccionario final
            detalles[nombre][meses_temp[mes_dt_ordenado]['nombre_legible']] = meses_temp[mes_dt_ordenado]['registros']

    return detalles




def compute_outliers_por_persona_y_mes(outliers: pd.DataFrame) -> dict:
    """
    Agrupa el DataFrame de outliers por nombre y Mes, devuelve:
    {nombre: {Mes: [registros]}}
    """
    if outliers is None or outliers.empty:
        return {}
    
    # Crear una copia para evitar modificar el DataFrame original    
    outliers_copia = outliers.copy()
        
    # Asegurar que fecha sea datetime para poder extraer el mes
    if not pd.api.types.is_datetime64_any_dtype(outliers_copia['fecha']):
        outliers_copia['fecha'] = pd.to_datetime(outliers_copia['fecha'])
    
    # Añadir columna de mes
    outliers_copia['mes'] = outliers_copia['fecha'].dt.strftime('%B %Y')
    
    resultado = {}
    for nombre, grp in outliers_copia.groupby('nombre'):
        resultado[nombre] = {}
        for mes, mes_grp in grp.groupby('mes'):
            resultado[nombre][mes] = mes_grp.to_dict('records')
            
    return resultado