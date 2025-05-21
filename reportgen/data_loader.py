import tabula
import xlrd
import pandas as pd
import os
from reportgen.processing import compute_resumen_mensual 

def cargar_historial():

    try:
        from google.colab import files
        print("Ejecutando en Google Colab.")
        # Solicita al usuario que cargue un archivo
        print("Por favor, selecciona un archivo Excel (.xlsx/.xls) o PDF (.pdf):")
        uploaded = files.upload()

        # Solo se admite un archivo a la vez
        if len(uploaded) != 1:
            raise ValueError("Por favor, sube un solo archivo.")

        filename = list(uploaded.keys())[0]
        extension = os.path.splitext(filename)[1].lower()

        # Validar extensión del archivo
        if extension not in ['.xlsx', '.xls', '.pdf']:
            raise ValueError("Tipo de archivo no permitido. Solo se permiten archivos .xlsx, .xls o .pdf")

        print(f"Archivo '{filename}' cargado correctamente.")
        return filename
    except ImportError:
        print("Ejecutando localmente.")
        # En tu PC, puedes pedir la ruta del archivo o usar una ruta predeterminada
        # Opción 1: Pedir al usuario la ruta del archivo
        # filename = input("Por favor, introduce la ruta completa del archivo (Excel o PDF): ")

        # Opción 2: Usar una ruta predeterminada
        filename = "data/MARCAJE CONTABILIDAD.pdf" # ¡CAMBIA ESTO!
        # Asegúrate de que el archivo exista en esta ruta para pruebas locales

        if not os.path.exists(filename):
            raise FileNotFoundError(f"El archivo '{filename}' no se encontró en la ruta especificada.")

        extension = os.path.splitext(filename)[1].lower()

        # Validar extensión del archivo
        if extension not in ['.xlsx', '.xls', '.pdf']:
            raise ValueError("Tipo de archivo no permitido. Solo se permiten archivos .xlsx, .xls o .pdf")

        print(f"Usando archivo local: '{filename}'.")
        return filename



def procesar_archivo(filename):
    # Obtener la extensión del archivo
    extension = os.path.splitext(filename)[1].lower()

    if extension in ['.xlsx', '.xls']:
        print("Procesando archivo Excel...")
        df = leer_excel(filename)
    elif extension == '.pdf':
        print("Procesando archivo PDF...")
        df = load_pdf(filename)
    else:
        raise ValueError("Extensión no soportada para procesamiento.")
    return transform_df(df)

def load_pdf(path: str) -> pd.DataFrame:
    """
    Lee el PDF de marcajes y devuelve un DataFrame con columna 'Fecha/Hora' en datetime.
    """
    df = tabula.read_pdf(path, pages="all", multiple_tables=False)[0]
    df.rename(columns={"ID de\rusuario": "ID"}, inplace=True)
    df.drop(columns=[col for col in df.columns if 'Unnamed' in col], inplace=True, errors='ignore')
    df['Fecha/Hora'] = pd.to_datetime(df['Fecha/Hora'], errors='coerce')
    return df



def leer_excel(archivo):
    # Lee el archivo Excel
    df_raw = pd.read_excel(archivo, engine='xlrd', header=None)
    
    # Busca la fila que contiene 'Departamento'
    start_row = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains('Departamento').any(), axis=1)].index[0]
    
    # Lee el archivo nuevamente, comenzando desde la fila encontrada
    df = pd.read_excel(archivo, engine='xlrd', header=start_row)
    
    # Filtra las filas donde 'Nombre' no es nulo
    df = df[df['Nombre'].notna()]
    
    # Elimina columnas completamente vacías
    df = df.dropna(axis=1, how='all')
    
    df.rename(columns={"Nro. de usuario": "ID"}, inplace=True)
    
    return df

def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa el dataframe de marcajes para obtener columnas básicas:
    Entrada, Salida, Jornada, Mes, Día de semana, Fin de semana, Estado de marcaje (completo/incompleto).
    """
    # Asegura formato de fecha y capitaliza nombres
    df['Fecha/Hora'] = pd.to_datetime(df['Fecha/Hora'], errors='coerce')
    df['Nombre'] = df['Nombre'].str.title()
    df['Fecha'] = df['Fecha/Hora'].dt.date

    # Agrupación por persona y fecha
    agrupado = df.sort_values('Fecha/Hora').groupby(['Departamento','ID','Nombre', 'Fecha'])

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
    tabla['Mes'] = pd.to_datetime(tabla['Fecha']).dt.strftime('%B %Y')
    tabla['Dia_semana'] = tabla['Entrada'].dt.weekday
    tabla['Fin_de_semana'] = tabla['Dia_semana'] >= 5

    return tabla

def extraer_contexto_general(df: pd.DataFrame) -> dict:
    """
    Extrae listas únicas de empleados, meses y departamentos del dataframe procesado.
    """
    contexto = {
        'empleados': sorted(df['Nombre'].dropna().unique()),
        'meses': sorted(df['Mes'].dropna().unique()),
        'departamento': sorted(df['Departamento'].dropna().unique()) if 'Departamento' in df.columns else [],
        'inicio': df['Fecha'].min(),
        'fin': df['Fecha'].max()
    }
    return contexto
