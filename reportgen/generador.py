import os
import re
from reportgen.templating import render_report
from reportgen.processing import (
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
    Genera un informe de jornadas a partir de un DataFrame de marcajes procesado.

    Args:
        df_marcajes: DataFrame de marcajes procesado (con columnas Nombre, Fecha, Entrada, Salida, Jornada).
        ruta_salida: Ruta donde se guardará el informe LaTeX.
    """
    # Extraer información de contexto
    departamento = df_marcajes['departamento'].iloc[0] if 'departamento' in df_marcajes.columns else "No especificado"
    empleados = sorted(df_marcajes['nombre'].unique())

    # Detectar outliers
    outliers = detect_outliers_jornada(df_marcajes)

    # Preparar datos para el informe (mantener versiones originales para compatibilidad)
    detalles_marcajes = get_detalles_marcajes(df_marcajes)
    outliers_por_persona = compute_outliers_por_persona(outliers)
    resumen_mensual = compute_resumen_mensual(detalles_marcajes)

    # Nuevas versiones organizadas por mes y empleado
    detalles_marcajes_por_mes = get_detalles_marcajes_por_mes(df_marcajes)
    outliers_por_persona_y_mes = compute_outliers_por_persona_y_mes(outliers)

    # Preparar el resumen fusionado (formato nuevo integrado)
    resumen_fusionado = construir_resumen_fusionado(detalles_marcajes)

    # Generar también el formato antiguo para compatibilidad
    resumen_por_mes_y_tipo_dia = agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado)

    # Asegurarse de que cada empleado tenga una entrada en outliers_por_persona
    for empleado in empleados:
        if empleado not in outliers_por_persona:
            outliers_por_persona[empleado] = []

        # También para la nueva estructura
        if empleado not in outliers_por_persona_y_mes:
            outliers_por_persona_y_mes[empleado] = {}

    inicio_fechas_v = df_marcajes['fecha'].min().strftime('%d/%m/%Y') if isinstance(df_marcajes['fecha'].min(), pd.Timestamp) else df_marcajes['fecha'].min()
    final_fechas_v = df_marcajes['fecha'].max().strftime('%d/%m/%Y') if isinstance(df_marcajes['fecha'].max(), pd.Timestamp) else df_marcajes['fecha'].max()
    # Preparar el contexto para la plantilla
    contexto = {
        'departamento': departamento,
        'empleados': empleados,
        'inicio_fechas': df_marcajes['fecha'].min().strftime('%d/%m/%Y') if isinstance(df_marcajes['fecha'].min(), pd.Timestamp) else df_marcajes['fecha'].min(),
        'final_fechas': df_marcajes['fecha'].max().strftime('%d/%m/%Y') if isinstance(df_marcajes['fecha'].max(), pd.Timestamp) else df_marcajes['fecha'].max(),
        'detalles_marcajes': detalles_marcajes,  # Mantener para compatibilidad
        'outliers_por_persona': outliers_por_persona,  # Mantener para compatibilidad
        'resumen_mensual': resumen_mensual,
        'resumen_por_mes_y_tipo_dia': resumen_por_mes_y_tipo_dia,
        'resumen_fusionado': resumen_fusionado,
        # Agregar las nuevas estructuras organizadas por mes
        'detalles_marcajes_por_mes': detalles_marcajes_por_mes,
        'outliers_por_persona_y_mes': outliers_por_persona_y_mes,
        'mes_inicio' : inicio_fechas_v.strftime('%B').capitalize(),
        'mes_fin' : final_fechas_v.strftime('%B').capitalize(),
        'año' : inicio_fechas_v.strftime('%Y')
    }

    # Renderizar el informe
    #--------------------- 
    # Construir el nombre del archivo de forma segura
    # nombre_archivo = f"{departamento}_informe_marcajes_{contexto['mes_inicio']}.tex"

    # # Unir la carpeta de salida con el nombre del archivo de forma segura
    # ruta_completa = os.path.join(output_path, nombre_archivo)

    # # Llamar a la función
    # render_report(contexto, ruta_completa)

    # return None
        # ===================================================================
    # 2. CONSTRUCCIÓN DE RUTAS Y NOMBRES DE ARCHIVO (Como lo corregimos antes)
    # ===================================================================
    departamento_saneado = re.sub(r'[^\w\-]', '_', departamento)
    mes_saneado = re.sub(r'[^\w\-]', '_', contexto['mes_inicio'])
    nombre_base = f"Reporte_{departamento_saneado}_{mes_saneado}_{contexto['año']}"

    # Creamos las rutas para los archivos que vamos a manejar
    ruta_tex = os.path.join(output_dir, f"{nombre_base}.tex")
    ruta_aux = os.path.join(output_dir, f"{nombre_base}.aux")
    ruta_log = os.path.join(output_dir, f"{nombre_base}.log")
    ruta_pdf = os.path.join(output_dir, f"{nombre_base}.pdf") # Ruta del resultado final

    # ===================================================================
    # 3. RENDERIZADO DEL ARCHIVO .TEX (Esta parte no cambia)
    # ===================================================================
    render_report(contexto, ruta_tex)
    print(f"Archivo .tex generado en: {ruta_tex}")

    # ===================================================================
    # 4. COMPILACIÓN A PDF Y LIMPIEZA (La nueva lógica)
    # ===================================================================
    try:
        print(f"Compilando {ruta_tex} a PDF...")
        # Comando para ejecutar pdflatex.
        # -interaction=nonstopmode: Evita que la compilación se detenga si hay errores menores.
        # -output-directory: Asegura que todos los archivos (pdf, log, aux) se creen en la carpeta de destino.
        comando = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory",
            output_dir,
            ruta_tex
        ]
        
        # Ejecutamos el comando
        resultado = subprocess.run(
            comando,
            capture_output=True,  # Captura la salida para poder verla si hay errores
            text=True,            # La salida se decodifica como texto
            check=True            # Lanza una excepción (CalledProcessError) si el comando falla
        )
        
        print(f"¡PDF generado con éxito en: {ruta_pdf}!")

    except FileNotFoundError:
        # Este error ocurre si `pdflatex` no está instalado o no está en el PATH del sistema
        error_msg = "ERROR: El comando 'pdflatex' no se encontró. Asegúrate de tener una distribución de LaTeX (como TeX Live, MiKTeX) instalada y accesible desde la línea de comandos."
        print(error_msg)
        raise RuntimeError(error_msg) # Relanzamos el error para que la GUI lo muestre

    except subprocess.CalledProcessError as e:
        # Este error ocurre si LaTeX falla durante la compilación
        print("¡ERROR! Falló la compilación de LaTeX.")
        # Imprimimos el log de errores de LaTeX, que es muy útil para depurar la plantilla
        print("--- Log de pdflatex ---")
        print(e.stdout)
        print("-----------------------")
        error_msg = f"Hubo un error al compilar el archivo .tex. Revisa la plantilla y el log de errores. Log guardado en: {ruta_log}"
        raise RuntimeError(error_msg)

    finally:
        # --- LIMPIEZA ---
        # Este bloque se ejecuta SIEMPRE, tanto si la compilación tuvo éxito como si falló.
        # Así nos aseguramos de no dejar archivos basura.
        print("Realizando limpieza de archivos auxiliares...")
        for archivo_a_borrar in [ruta_tex, ruta_aux, ruta_log]:
            if os.path.exists(archivo_a_borrar):
                try:
                    os.remove(archivo_a_borrar)
                    print(f"  - Borrado: {os.path.basename(archivo_a_borrar)}")
                except OSError as e:
                    print(f"  - No se pudo borrar {os.path.basename(archivo_a_borrar)}: {e}")

    return None