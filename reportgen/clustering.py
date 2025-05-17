import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- 1. Función para generar características para clustering ---
def compute_features(tabla: pd.DataFrame) -> pd.DataFrame:
    """
    A partir de la tabla de jornadas calculamos:
    - duracion_jornada: duración promedio de la jornada diaria (en horas)
    - dias_trabajados: número de días trabajados
    - variabilidad_jornada: desviación estándar de la duración de jornada
    """
    features = tabla.groupby('Nombre').agg(
        duracion_jornada=('Jornada', lambda x: x.mean().total_seconds()/3600),
        dias_trabajados=('Fecha', 'nunique'),
        variabilidad_jornada=('Jornada', lambda x: x.std().total_seconds()/3600)
    ).fillna(0)

    return features

# --- 2. Función para aplicar K-means y asignar cluster ---
def cluster_employees(features: pd.DataFrame, n_clusters=3) -> pd.DataFrame:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    features = features.copy()
    features['cluster'] = labels
    return features

# --- 3. Función para generar tabla LaTeX ---
def generate_latex_cluster_table(features: pd.DataFrame) -> str:
    header = r"""\begin{table}[H]
\centering
\begin{tabular}{lrrr}
\hline
Cluster & Duraci\'on Promedio (hrs) & D\'ias Trabajados & Variabilidad Jornada (hrs) \\ \hline
"""
    rows = []
    for c in sorted(features['cluster'].unique()):
        grp = features[features['cluster'] == c]
        rows.append(f"{c+1} & "
                    f"{grp['duracion_jornada'].mean():.2f} & "
                    f"{grp['dias_trabajados'].mean():.1f} & "
                    f"{grp['variabilidad_jornada'].mean():.2f} \\\\")
    footer = r"""\hline
\end{tabular}
\caption{Resumen de clusters de empleados basado en jornada laboral.}
\end{table}"""
    return header + '\n'.join(rows) + '\n' + footer

# Nota: Ya no incluimos el bloque __main__, el control estará en main.py
def generate_latex_employees_by_cluster(features: pd.DataFrame) -> str:
    """
    Genera un bloque LaTeX que lista los empleados agrupados por grupo,
    mostrando sus valores individuales de duración, días trabajados y variabilidad.
    """
    latex = r"\section{Detalle de Empleados por Grupo}" "\n"
    for cluster in sorted(features['cluster'].unique()):
        grp = features[features['cluster'] == cluster]
        descripcion = describe_cluster(grp)

        latex += r"\subsection*{Grupo " + str(cluster + 1) + "}" + "\n"
        latex += descripcion + "\n\n"
        latex += r"\begin{tabular}{lrrr}" + "\n"
        latex += r"\toprule" + "\n"
        latex += r"Empleado & Promedio(hrs) & Días Trabajados & Variación(hrs) \\\\" + "\n"
        latex += r"\midrule" + "\n"

        for nombre, fila in grp.iterrows():
            latex += f"{nombre} & {fila['duracion_jornada']:.2f} & {fila['dias_trabajados']:.0f} & {fila['variabilidad_jornada']:.2f} \\\\\n"

        latex += r"\bottomrule" + "\n"
        latex += r"\end{tabular}" + "\n\n"
    return latex



def describe_cluster(grp) -> str:
    """
    Genera una descripción humana de un grupo de empleados basado en sus características.
    """
    duracion = grp['duracion_jornada'].mean()
    dias = grp['dias_trabajados'].mean()
    variabilidad = grp['variabilidad_jornada'].mean()

    descripcion = []

    # Interpretar duración de jornada
    if duracion > 9:
        descripcion.append("jornadas largas")
    elif duracion > 7:
        descripcion.append("jornadas promedio")
    else:
        descripcion.append("jornadas cortas")

    # Interpretar días trabajados
    if dias >= 22:
        descripcion.append("trabajan casi todos los días")
    elif dias >= 15:
        descripcion.append("trabajan moderadamente")
    else:
        descripcion.append("trabajan pocos días")

    # Interpretar variabilidad
    if variabilidad > 1.5:
        descripcion.append("alta variabilidad en horarios")
    elif variabilidad > 0.5:
        descripcion.append("variabilidad moderada")
    else:
        descripcion.append("horarios consistentes")

    return "Grupo caracterizado por " + ", ".join(descripcion) + "."
