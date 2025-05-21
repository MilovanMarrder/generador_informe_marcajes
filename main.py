from reportgen.data_loader import procesar_archivo, cargar_historial
from reportgen.generador import generar_informe

import os
import pandas as pd
from datetime import datetime, timedelta

def ejemplo_generar_reporte():
    """
    Ejemplo de cómo usar la nueva funcionalidad para generar un reporte.
    
    Esta función puede ser usada con un archivo real de marcajes o con datos de prueba.
    """
    # Determinar si usar datos de prueba o un archivo real
    usar_datos_prueba = False  # Cambiar a False para usar un archivo real
    
    if usar_datos_prueba:
        # Generar datos de prueba
        df_marcajes = generar_datos_prueba()
    else:
        # Procesar un archivo real
        filename = cargar_historial()
        df_marcajes = procesar_archivo(filename)
    
    # Generar el informe
    ruta_salida = "informe_jornadas.tex"
    generar_informe(df_marcajes, ruta_salida)
    
    print(f"Informe generado correctamente en: {ruta_salida}")
    
    # Opcional: Compilar el archivo LaTeX (si se tiene pdflatex instalado)
    compilar = input("¿Deseas compilar el archivo LaTeX a PDF? (s/n): ")
    if compilar.lower() == 's':
        try:
            import subprocess
            resultado = subprocess.run(["pdflatex", ruta_salida], capture_output=True, text=True)
            if resultado.returncode == 0:
                print(f"PDF generado correctamente como {ruta_salida.replace('.tex', '.pdf')}")
            else:
                print("Error al generar el PDF. Asegúrate de tener pdflatex instalado.")
                print("Error:", resultado.stderr)
        except Exception as e:
            print(f"Error al intentar compilar: {e}")
            print("Asegúrate de tener pdflatex instalado en tu sistema.")
    
    return ruta_salida

def generar_datos_prueba():
    """
    Genera un DataFrame de prueba con datos de marcajes para demostrar la funcionalidad.
    """
    # Definir empleados y fechas de prueba
    empleados = ["Ana García", "Carlos López", "María Rodríguez"]
    
    # Fechas de prueba: últimos 30 días
    hoy = datetime.now().date()
    fechas = [(hoy - timedelta(days=i)) for i in range(30)]
    
    # Crear datos
    datos = []
    
    for empleado in empleados:
        for fecha in fechas:
            # Generar hora de entrada (entre 7:00 y 9:00)
            hora_entrada = datetime.combine(fecha, datetime.min.time()) + timedelta(hours=7 + (fecha.day % 3))
            
            # Generar hora de salida (entre 8 y 10 horas después)
            jornada_horas = 8 + (fecha.day % 3)
            hora_salida = hora_entrada + timedelta(hours=jornada_horas)
            
            # Algunos días sin marcaje (fines de semana)
            if fecha.weekday() >= 5 and (fecha.day % 3 != 0):  # Solo algunos fines de semana
                continue
                
            datos.append({
                'Departamento': 'Tecnología',
                'ID': f'EMP{empleados.index(empleado) + 100}',
                'Nombre': empleado,
                'Fecha': fecha,
                'Fecha/Hora': hora_entrada,  # Para compatibilidad
                'Entrada': hora_entrada,
                'Salida': hora_salida,
                'Jornada': hora_salida - hora_entrada
            })
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Añadir columnas adicionales
    df['Mes'] = pd.to_datetime(df['Fecha']).dt.strftime('%B %Y')
    df['Dia_semana'] = pd.to_datetime(df['Fecha']).dt.weekday
    df['Fin_de_semana'] = df['Dia_semana'] >= 5
    df['Estado'] = 'Completo'
    
    return df

if __name__ == "__main__":
    ejemplo_generar_reporte()