import os
import re
from utils.templating import render_report
from utils.processing import (
    get_detalles_marcajes, 
    get_detalles_marcajes_por_mes,  # Importar la nueva función
    compute_outliers_por_persona,
    compute_outliers_por_persona_y_mes,  # Importar la nueva función
    compute_resumen_mensual,
    detect_outliers_jornada,
    construir_resumen_fusionado,
    agrupar_resumen_por_mes_y_tipo_dia
)
import pandas as pd
import subprocess


def generar_informe(df_marcajes: pd.DataFrame, output_dir: str):
    """
    Genera un informe en PDF y limpia los archivos intermedios.
    """
    # 1. PREPARACIÓN DE DATOS Y CONTEXTO
    departamento = df_marcajes['departamento'].iloc[0] if 'departamento' in df_marcajes.columns else "No especificado"
    empleados = sorted(df_marcajes['nombre'].unique())
    outliers = detect_outliers_jornada(df_marcajes)
    detalles_marcajes = get_detalles_marcajes(df_marcajes)
    outliers_por_persona = compute_outliers_por_persona(outliers)
    resumen_mensual = compute_resumen_mensual(detalles_marcajes)
    detalles_marcajes_por_mes = get_detalles_marcajes_por_mes(df_marcajes)
    outliers_por_persona_y_mes = compute_outliers_por_persona_y_mes(outliers)
    resumen_fusionado = construir_resumen_fusionado(detalles_marcajes)
    resumen_por_mes_y_tipo_dia = agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado)

    for empleado in empleados:
        if empleado not in outliers_por_persona:
            outliers_por_persona[empleado] = []
        if empleado not in outliers_por_persona_y_mes:
            outliers_por_persona_y_mes[empleado] = {}

    # Corregir la obtención de fechas para que siempre funcione
    min_fecha_dt = pd.to_datetime(df_marcajes['fecha'].min())
    max_fecha_dt = pd.to_datetime(df_marcajes['fecha'].max())

    contexto = {
        'departamento': departamento,
        'empleados': empleados,
        'inicio_fechas': min_fecha_dt.strftime('%d/%m/%Y'),
        'final_fechas': max_fecha_dt.strftime('%d/%m/%Y'),
        'detalles_marcajes': detalles_marcajes,
        'outliers_por_persona': outliers_por_persona,
        'resumen_mensual': resumen_mensual,
        'resumen_por_mes_y_tipo_dia': resumen_por_mes_y_tipo_dia,
        'resumen_fusionado': resumen_fusionado,
        'detalles_marcajes_por_mes': detalles_marcajes_por_mes,
        'outliers_por_persona_y_mes': outliers_por_persona_y_mes,
        'mes_inicio' : min_fecha_dt.strftime('%B').capitalize(),
        'mes_fin' : max_fecha_dt.strftime('%B').capitalize(),
        'año' : min_fecha_dt.strftime('%Y')
    }

    # 2. CONSTRUCCIÓN DE RUTAS
    departamento_saneado = re.sub(r'[^\w\-]', '_', departamento)
    mes_saneado = re.sub(r'[^\w\-]', '_', contexto['mes_inicio'])
    nombre_base = f"Reporte_{departamento_saneado}_{mes_saneado}_{contexto['año']}"

    extensiones_a_borrar = ['.tex', '.aux', '.log', '.toc', '.out']
    archivos_auxiliares = [os.path.join(output_dir, f"{nombre_base}{ext}") for ext in extensiones_a_borrar]
    ruta_tex = os.path.join(output_dir, f"{nombre_base}.tex")
    ruta_pdf = os.path.join(output_dir, f"{nombre_base}.pdf")
    
    # 3. RENDERIZADO DEL .TEX
    render_report(contexto, ruta_tex)
    print(f"Archivo .tex generado en: {ruta_tex}")

    # 4. COMPILACIÓN A PDF Y LIMPIEZA
    try:
        print(f"Compilando {ruta_tex} a PDF...")
        comando = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory",
            output_dir,
            ruta_tex
        ]
        
        # Ejecutamos el comando una vez, que es suficiente sin el índice
        subprocess.run(comando, capture_output=True, text=True, check=True)
        
        print(f"¡PDF generado con éxito en: {ruta_pdf}!")

    # --- BLOQUE EXCEPT CORREGIDO ---
    except FileNotFoundError:
        error_msg = ("ERROR: El comando 'pdflatex' no se encontró. Asegúrate de tener "
                     "una distribución de LaTeX (como TeX Live, MiKTeX) instalada y "
                     "accesible desde la línea de comandos.")
        print(error_msg)
        raise RuntimeError(error_msg)

    except subprocess.CalledProcessError as e:
        print("¡ERROR! Falló la compilación de LaTeX.")
        print("--- Log de pdflatex ---")
        print(e.stdout)
        print("-----------------------")
        ruta_log = next((f for f in archivos_auxiliares if f.endswith('.log')), 'no encontrado')
        error_msg = (f"Hubo un error al compilar el archivo .tex. Revisa la plantilla y el log de errores. "
                     f"Log guardado en:\n{ruta_log}")
        raise RuntimeError(error_msg)
    # --- FIN DEL BLOQUE EXCEPT CORREGIDO ---

    finally:
        print("Realizando limpieza de archivos auxiliares...")
        for archivo_a_borrar in archivos_auxiliares:
            if os.path.exists(archivo_a_borrar):
                try:
                    os.remove(archivo_a_borrar)
                    print(f"  - Borrado: {os.path.basename(archivo_a_borrar)}")
                except OSError as err:
                    print(f"  - No se pudo borrar {os.path.basename(archivo_a_borrar)}: {err}")

    return None