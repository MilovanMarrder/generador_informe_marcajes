import tabula
import xlrd
import pandas as pd
from google.colab import files
import os


def cargar_historial():
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

import os

def procesar_archivo(filename):
    # Obtener la extensión del archivo
    extension = os.path.splitext(filename)[1].lower()

    if extension in ['.xlsx', '.xls']:
        print("Procesando archivo Excel...")
        return leer_excel(filename)
    elif extension == '.pdf':
        print("Procesando archivo PDF...")
        return load_pdf(filename)
    else:
        raise ValueError("Extensión no soportada para procesamiento.")


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
    
    return df