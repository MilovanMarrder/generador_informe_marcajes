# Funciones para extracción, limpieza y transformación de datos 
import re
import unicodedata
import pandas as pd

# ------------- Limpieza de nombres de columnas ---------------


def renombrar_columnas (df:pd.DataFrame)-> pd.DataFrame :
  """
  Renombra las columnas de un DataFrame de Pandas con un estilo
  más limpio y legible. eliminando espacios, guiones y barras,
  normalizando acentos y conservando solo letras minúsculas,
  números y guiones bajos.
  :Param: DataFrame a renombrar columnas
  :Return: DataFrame con columnas renombradas
  """
  def limpiar_nombre_columna (col):
      col = str(col).strip().replace('Nro','').replace('de', '')
      col = re.sub(r'[\s+/\-]+', '_', col)
      col = unicodedata.normalize('NFD', col)
      col = ''.join(c for c in col if unicodedata.category(c) != 'Mn')
      col = re.sub(r'[^a-zA-Z0-9_]', '', col).lower()
      return re.sub(r'_+', '_', col).strip('_') or 'col'
  df.columns = [limpiar_nombre_columna(col) for col in df.columns]
  return df

# -------------cargar y transformar DataFrame -----------------


def etl_df(ruta: str) -> pd.DataFrame:
    """
    Procesa el dataframe de marcajes para obtener columnas básicas:
    Entrada, Salida, Jornada, Mes, Día de semana, Fin de semana, Estado de marcaje (completo/incompleto).
    """
    df = pd.read_excel(ruta)
    df = renombrar_columnas(df.copy())
    # Asegura formato de fecha y capitaliza nombres
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'], errors='coerce')
    df['nombre'] = df['nombre'].str.title()
    df['fecha'] = df['fecha_hora'].dt.date

    # Agrupación por persona y fecha
    agrupado = df.sort_values('fecha_hora').groupby(['departamento','id_usuario','nombre', 'fecha'])

    # Extraer primera y última marcación por día
    tabla = agrupado['fecha_hora'].agg(entrada='first', salida='last').reset_index()

    # Clasificar registros incompletos (cuando entrada == salida)
    tabla['estado'] = tabla.apply(
        lambda row: 'Incompleto' if row['entrada'] == row['salida'] else 'Completo',
        axis=1
    )

    # Calcular jornada solo si es completo
    tabla['jornada'] = tabla.apply(
        lambda row: row['salida'] - row['entrada'] if row['estado'] == 'Completo' else pd.NaT,
        axis=1
    )

    # Agregar columnas adicionales
    tabla['mes'] = pd.to_datetime(tabla['fecha']).dt.strftime('%B %Y')
    tabla['dia_semana'] = tabla['entrada'].dt.weekday
    tabla['fin_de_semana'] = tabla['dia_semana'] >= 5

    return tabla


# -------- Crear diccionario de contexto ----------------

def extraer_contexto_general(df: pd.DataFrame) -> dict:
    """
    Extrae listas únicas de empleados, meses y departamentos del dataframe procesado.
    """
    contexto = {
        'empleados': sorted(df['nombre'].dropna().unique()),
        'meses': sorted(df['mes'].dropna().unique()),
        'departamento': sorted(df['departamento'].dropna().unique()) if 'departamento' in df.columns else [],
        'inicio': df['fecha'].min(),
        'fin': df['fecha'].max()
    }
    return contexto

