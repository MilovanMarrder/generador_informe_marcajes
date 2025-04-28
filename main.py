from reportgen.data_loader import load_pdf, seleccionar_pdf_gui
from reportgen.processing import compute_basic_columns, fechas_inicio_fin, get_detalles_marcajes, detect_outliers_jornada, compute_outliers_por_persona, compute_resumen_mensual, construir_resumen_fusionado, agrupar_resumen_por_mes, agrupar_resumen_por_mes_y_tipo_dia
from reportgen.analytics import summary_general, summary_employees
from reportgen.clustering import compute_features, cluster_employees, generate_latex_cluster_table, generate_latex_employees_by_cluster
from reportgen.templating import render_report

import os

# 1. Cargar datos
pdf_path = seleccionar_pdf_gui()
df = load_pdf(pdf_path)

print('Cargando datos...')
print(f"Total de registros: {len(df)}")


print('Procesando datos...')
print(f"Total de registros después de limpieza: {len(df)}")
# 2. Procesamiento inicial
tabla = compute_basic_columns(df)
fechas = fechas_inicio_fin(df)
detalles = get_detalles_marcajes(tabla)
outliers = detect_outliers_jornada(tabla)
outliers_dict = compute_outliers_por_persona(outliers)
resumen_mensual = compute_resumen_mensual(detalles)

# 3. Resúmenes generales
resumen_general = summary_general(tabla).to_dict(orient='records')
resumen_emps = summary_employees(tabla).to_dict(orient='records')

# --- CLUSTERING ---
print('Realizando clustering...')
# 4. Separar semana laboral y fines de semana
tabla_semana = tabla[tabla['Fin_de_semana'] == False]
tabla_finde = tabla[tabla['Fin_de_semana'] == True]

# 5. Clustering sobre días de semana
features_semana = compute_features(tabla_semana)
features_clustered_semana = cluster_employees(features_semana, n_clusters=3)
latex_table_clusters_semana = generate_latex_cluster_table(features_clustered_semana)
latex_employees_by_cluster_semana = generate_latex_employees_by_cluster(features_clustered_semana)

# 6. (Opcional) Clustering sobre fines de semana, sólo si existen registros
if not tabla_finde.empty:
    features_finde = compute_features(tabla_finde)
    features_clustered_finde = cluster_employees(features_finde, n_clusters=3)
    latex_table_clusters_finde = generate_latex_cluster_table(features_clustered_finde)
    latex_employees_by_cluster_finde = generate_latex_employees_by_cluster(features_clustered_finde)
else:
    latex_table_clusters_finde = ""
    latex_employees_by_cluster_finde = ""

# 7. Contexto para LaTeX

resumen_fusionado = construir_resumen_fusionado(detalles)
resumen_por_mes_y_tipo_dia = agrupar_resumen_por_mes_y_tipo_dia(resumen_fusionado)

context = {
    "inicio_fechas": fechas['inicio'].strftime("%d %B de %Y"),
    "final_fechas": fechas['fin'].strftime("%d %B de %Y"),
    "detalles_marcajes": detalles,
    "outliers_por_persona": outliers_dict,
    "resumen_mensual": resumen_mensual,
    "tabla_clusters_semana": latex_table_clusters_semana,
    "empleados_clusters_semana": latex_employees_by_cluster_semana,
    "tabla_clusters_finde": latex_table_clusters_finde,
    "empleados_clusters_finde": latex_employees_by_cluster_finde,
    "resumen_por_mes_y_tipo_dia": resumen_por_mes_y_tipo_dia  # <--- nuevo
}




# 8. Crear carpeta de salida si no existe
os.makedirs("output", exist_ok=True)
print('Generando reporte...')


# 9. Renderizar .tex
render_report(context, "output/reporte.tex")
