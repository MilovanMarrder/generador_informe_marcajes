import tabula
import xlrd
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
import tkinter as tk
from tkinter import filedialog

def seleccionar_pdf_gui() -> str:
    """
    Muestra un cuadro de diálogo para seleccionar un archivo PDF.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")],
        initialdir="data"
    )
    if not ruta_archivo:
        raise FileNotFoundError("No se seleccionó ningún archivo.")
    return ruta_archivo

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