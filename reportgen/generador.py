from reportgen.templating import render_report
from reportgen.processing import (
    get_detalles_marcajes, 
    compute_outliers_por_persona,
    compute_resumen_mensual,
    detect_outliers_jornada,
    construir_resumen_fusionado,
    agrupar_resumen_por_mes_y_tipo_dia
)
import pandas as pd

def generar_informe(df_marcajes: pd.DataFrame, ruta_salida: str = "informe_jornadas.tex"):
    """
    Genera un informe de jornadas a partir de un DataFrame de marcajes procesado.
    
    Args:
        df_marcajes: DataFrame de marcajes procesado (con columnas Nombre, Fecha, Entrada, Salida, Jornada).
        ruta_salida: Ruta donde se guardará el informe LaTeX.
    """
    # Extraer información de contexto
    departamento = df_marcajes['Departamento'].iloc[0] if 'Departamento' in df_marcajes.columns else "No especificado"
    empleados = sorted(df_marcajes['Nombre'].unique())
    
    # Detectar outliers
    outliers = detect_outliers_jornada(df_marcajes)
    
    # Preparar datos para el informe
    detalles_marcajes = get_detalles_marcajes(df_marcajes)
    outliers_por_persona = compute_outliers_por_persona(outliers)
    resumen_mensual = compute_resumen_mensual(detalles_marcajes)
    
    # Preparar el resumen fusionado (formato nuevo integrado)
    resumen_fusionado = construir_resumen_fusionado(detalles_marcajes)
    
    # Generar también el formato antiguo para compatibilidad
    resumen_por_mes_y_tipo_dia = agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado)
    
    # Asegurarse de que cada empleado tenga una entrada en outliers_por_persona
    for empleado in empleados:
        if empleado not in outliers_por_persona:
            outliers_por_persona[empleado] = []
    
    # Preparar el contexto para la plantilla
    contexto = {
        'departamento': departamento,
        'empleados': empleados,
        'inicio_fechas': df_marcajes['Fecha'].min().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].min(), pd.Timestamp) else df_marcajes['Fecha'].min(),
        'final_fechas': df_marcajes['Fecha'].max().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].max(), pd.Timestamp) else df_marcajes['Fecha'].max(),
        'detalles_marcajes': detalles_marcajes,
        'outliers_por_persona': outliers_por_persona,
        'resumen_mensual': resumen_mensual,
        'resumen_por_mes_y_tipo_dia': resumen_por_mes_y_tipo_dia,
        'resumen_fusionado': resumen_fusionado
    }
    
    # Renderizar el informe
    render_report(contexto, ruta_salida)
    
    return ruta_salida