# reportgen/processing.py
import pandas as pd

def transformar_marcajes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa el dataframe de marcajes para obtener columnas de trabajo.
    Entrada, Salida, Jornada, Mes, Día de semana, Fin de semana, Estado.
    """
    # Copiamos para evitar SettingWithCopyWarning
    df = df.copy()

    # Asegura formato de fecha y capitaliza nombres
    df['Fecha/Hora'] = pd.to_datetime(df['Fecha/Hora'], errors='coerce')
    df.dropna(subset=['Fecha/Hora'], inplace=True) # Elimina filas donde la conversión de fecha falló
    df['Nombre'] = df['Nombre'].str.title()
    df['Fecha'] = df['Fecha/Hora'].dt.date

    # Agrupación por persona y fecha
    agrupado = df.sort_values('Fecha/Hora').groupby(['departamento', 'ID', 'Nombre', 'Fecha'])

    # Extraer primera y última marcación por día
    tabla = agrupado['Fecha/Hora'].agg(Entrada='first', Salida='last').reset_index()

    # Clasificar registros incompletos (cuando entrada == salida)
    tabla['Estado'] = tabla.apply(
        lambda row: 'Incompleto' if row['Entrada'] == row['Salida'] else 'Completo',
        axis=1
    )

    # Calcular jornada solo si es completo
    tabla['Jornada'] = tabla.apply(
        lambda row: row['Salida'] - row['Entrada'] if row['Estado'] == 'Completo' else pd.NaT,
        axis=1
    )

    # Agregar columnas adicionales
    tabla['Mes'] = pd.to_datetime(tabla['Fecha']).dt.strftime('%B %Y').str.title()
    tabla['Dia_semana'] = tabla['Entrada'].dt.weekday
    tabla['Fin_de_semana'] = tabla['Dia_semana'] >= 5

    return tabla