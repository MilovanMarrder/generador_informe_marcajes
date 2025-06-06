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
from datetime import timedelta

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
    
    inicio_fechas_v = df_marcajes['Fecha'].min().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].min(), pd.Timestamp) else df_marcajes['Fecha'].min()
    final_fechas_v = df_marcajes['Fecha'].max().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].max(), pd.Timestamp) else df_marcajes['Fecha'].max()
    # Preparar el contexto para la plantilla
    contexto = {
        'departamento': departamento,
        'empleados': empleados,
        'inicio_fechas': df_marcajes['Fecha'].min().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].min(), pd.Timestamp) else df_marcajes['Fecha'].min(),
        'final_fechas': df_marcajes['Fecha'].max().strftime('%d/%m/%Y') if isinstance(df_marcajes['Fecha'].max(), pd.Timestamp) else df_marcajes['Fecha'].max(),
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
    render_report(contexto, ruta_salida)
    
    return ruta_salida