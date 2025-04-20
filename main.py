from reportgen.data_loader import load_pdf
from reportgen.processing import compute_basic_columns, fechas_inicio_fin, get_detalles_marcajes, detect_outliers_jornada, compute_outliers_por_persona, compute_resumen_mensual
from reportgen.analytics import summary_general, summary_employees
from reportgen.templating import render_report

import os

# 1. Cargar datos
df = load_pdf("data/MARCAJE CONTABILIDAD.pdf")

# 2. Procesamiento
tabla = compute_basic_columns(df)
fechas = fechas_inicio_fin(df)
detalles = get_detalles_marcajes(tabla)
outliers = detect_outliers_jornada(tabla)
outliers_dict = compute_outliers_por_persona(outliers)
resumen_mensual = compute_resumen_mensual(detalles)

# 3. Resúmenes
resumen_general = summary_general(tabla).to_dict(orient='records')
resumen_emps = summary_employees(tabla).to_dict(orient='records')

# 4. Contexto para LaTeX
context = {
    "inicio_fechas": fechas['inicio'].strftime("%d/%m/%Y"),
    "final_fechas": fechas['fin'].strftime("%d/%m/%Y"),
    "resumen_general": resumen_general,
    "resumen_emps": resumen_emps,
    "detalles_marcajes": detalles,
    "outliers_por_persona": outliers_dict,
    "resumen_mensual": resumen_mensual
}

# 5. Crear carpeta de salida si no existe
os.makedirs("output", exist_ok=True)

# 6. Renderizar .tex
render_report(context, "output/reporte.tex")
