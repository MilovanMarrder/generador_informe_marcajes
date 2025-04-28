from jinja2 import Template
import datetime

# dia en el formato de fecha %d %M de %Y
hoy = datetime.datetime.now().strftime("%d %B de %Y")

LATEX_TEMPLATE = r"""
\documentclass[11pt,a4paper]{article}

% Paquetes necesarios
\usepackage{tcolorbox}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{enumitem}
\usepackage{hyperref}

% Definición de colores
\definecolor{corporativo}{RGB}{180,0,0} % Rojo corporativo sobrio

% Configuración de geometría
\geometry{
  a4paper,
  top=2.5cm,
  bottom=2.5cm,
  left=2.5cm,
  right=2.5cm,
  headheight=1.5cm,
  footskip=1.5cm
}

% Configuración de encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\fancyhead[L]{\textcolor{corporativo}{\textbf{TechSolutions S.A.}}}
\fancyhead[R]{\textcolor{corporativo}{\textbf{Reporte de Tiempo}}}
\fancyfoot[C]{\textcolor{corporativo}{\thepage}}
\fancyfoot[L]{\textcolor{corporativo}{Confidencial}}
\fancyfoot[R]{\textcolor{corporativo}{Marzo 2025}}

% Estilo de títulos - Sin numeración y solo títulos en rojo
\titleformat{\section}
  {\normalfont\Large\bfseries\color{corporativo}}
  {}{0em}{}[\titlerule]
\titleformat{\subsection}
  {\normalfont\large\bfseries}
  {}{0em}{}

% Eliminar sangría en párrafos
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

% Estilo de listas
\setlist{noitemsep}

% Configuración de hipervínculos
\hypersetup{
  colorlinks=true,
  linkcolor=corporativo,
  urlcolor=corporativo
}

% Eliminar la numeración de secciones
\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}

% Comandos para crear boxes informativos
\newcommand{\infobox}[2]{
  \begin{tcolorbox}[
    colback=grisclaro,
    colframe=corporativo,
    title=#1,
    fonttitle=\bfseries
  ]
  #2
  \end{tcolorbox}
}

% Comando para tablas con estilo mejorado
\newcommand{\mejoradatabla}[1]{
  \renewcommand{\arraystretch}{1.3}
  \setlength{\tabcolsep}{10pt}
  #1
  \renewcommand{\arraystretch}{1}
  \setlength{\tabcolsep}{6pt}
}


\begin{document}

% --- PÁGINA DE TÍTULO ---
\begin{titlepage}
  \centering
  \vspace*{2cm} % Espacio superior

  % Logo de la empresa (si existe)
  % \includegraphics[width=0.3\textwidth]{logo_techsolutions} % Reemplazar con tu logo
  % \vspace{1.5cm}

  {\Huge\bfseries\textcolor{corporativo}{REPORTE DE TIEMPOS DE TRABAJO}\par}
  \vspace{1cm}
  {\color{gray}\rule{\textwidth}{0.4pt}\par} % Línea separadora sutil
  \vspace{1cm}
  {\Large\bfseries EMPRESA MARDER\par} % Nombre de la empresa cliente
  \vspace{0.5cm}
  {\large Período Analizado: {{inicio_fechas}} - {{final_fechas}}\par}

  \vspace{4cm} % Espacio considerable antes de los metadatos

  % Metadatos del informe
  \begin{tabular}{>{\bfseries}r @{\hspace{1em}} l} % Alineación: derecha negrita, espacio, izquierda
  Informe elaborado por: & Departamento de Recursos Humanos \\
  Fecha de elaboración: & \today \\
  Clasificación: & \textcolor{corporativo}{Confidencial} \\
  \end{tabular}

  \vfill % Empuja el contenido restante hacia abajo

  % Línea sutil en la parte inferior antes del logo (opcional)
  {\color{gray}\rule{0.6\textwidth}{0.4pt}\par}
  \vspace{0.5cm}
  % Logo de la empresa (alternativa: colocarlo aquí)
  % \includegraphics[width=0.2\textwidth]{logo_techsolutions}
  % O un texto si no hay logo:
  {\small \textcolor{gray}{\textit{Este informe es confidencial y no debe ser distribuido sin autorización.}}\\
  \textcolor{gray}{\textit{Generador creado por Milovan Marrder.}}}
  \vspace*{1cm} % Espacio inferior
\end{titlepage}




\tableofcontents\newpage

\section{Resumen General}
\begin{tabular}{lrrr}
\toprule
Tipo de día & Días trabajados & Total horas\\
\midrule
{% for row in resumen_general %}
{{ row.Tipo_dia }} & {{ row.Cantidad_Dias }} & {{ "%.2f"|format(row.Total_horas) }}\\
{% endfor %}
\bottomrule
\end{tabular}

\begin{tabular}{lrrr}
\toprule
Mes & Tipo de día & Días trabajados & Total horas\\
\midrule
{% for row in resumen_general %}
{{ row.Mes }} & {{ row.Tipo_dia }} & {{ row.Cantidad_Dias }} & {{ "%.2f"|format(row.Total_horas) }}\\
{% endfor %}
\bottomrule
\end{tabular}

\section{Horas por Empleado}
\begin{tabular}{lrr}
\toprule
Empleado & Mediana hrs/día & Horas totales\\
\midrule
{% for emp in resumen_emps %}
{{ emp.Nombre }} & {{ "%.2f"|format(emp.Mediana_hrs_dia) }} & {{ "%.2f"|format(emp.Horas_totales) }}\\
{% endfor %}
\bottomrule
\end{tabular}

\begin{tabular}{lrr}
\toprule
Empleado & Mediana hrs/día & Horas totales\\
\midrule
{% for emp in resumen_emps %}
{{ emp.Nombre }} & {{ "%.2f"|format(emp.Mediana_hrs_dia) }} & {{ "%.2f"|format(emp.Horas_totales) }}\\
{% endfor %}
\bottomrule
\end{tabular}

\newpage

\section{Detalles de Marcajes}
{% for nombre, regs in detalles_marcajes.items() %}
\subsection{ {{ nombre }} }

\begin{minipage}[t]{0.62\textwidth}
  \begin{tabular}{lccc}
    \toprule
    Fecha & Entrada & Salida & Hrs trabajadas\\
    \midrule
    {% for r in regs %}
    {{ r['Fecha'].strftime('%Y-%m-%d') }} &
    {{ r['Entrada'].time() }} &
    {{ r['Salida'].time() }} &
    {{ "%.2f"|format(r['Jornada'].total_seconds()/3600) }}\\
    {% endfor %}
    \bottomrule
  \end{tabular}
\end{minipage}
\hfill
\begin{minipage}[t]{0.35\textwidth}
  \textbf{Días Atípicos:}
  \begin{tabular}{lr}
    \toprule
    Fecha & Tipo\\
    \midrule
    {% for o in outliers_por_persona[nombre] %}
    {{ o['Fecha'].strftime('%Y-%m-%d') }} & {{ o['Tipo'] }}\\
    {% endfor %}
    \bottomrule
  \end{tabular}

  \vspace{1em}
  \textbf{Resumen Mensual:}
  \begin{tabular}{lrr}
    \toprule
    Mes & Horas & Días\\
    \midrule
    {% for m in resumen_mensual[nombre] %}
    {{ m.Mes }} & {{ "%.2f"|format(m.Horas) }} & {{ m.Dias }}\\
    {% endfor %}
    \bottomrule
  \end{tabular}
\end{minipage}

\newpage
{% endfor %}

\section{Análisis de Grupos de Empleados (Semana Laboral)}

\subsection{Variables utilizadas para formar los grupos}

\begin{itemize}
    \item \textbf{Duración promedio de jornada}: Número promedio de horas trabajadas por día.
    \item \textbf{Días trabajados}: Número total de días trabajados en el período evaluado.
    \item \textbf{Variabilidad de jornada}: Variabilidad en las horas trabajadas día a día.
\end{itemize}

{{ tabla_clusters_semana }}

{{ empleados_clusters_semana }}

{% if tabla_clusters_finde %}
\newpage
\section{Análisis de Grupos de Empleados (Fines de Semana)}

\subsection{Variables utilizadas para formar los grupos}

\begin{itemize}
    \item \textbf{Duración promedio de jornada}: Número promedio de horas trabajadas por día.
    \item \textbf{Días trabajados}: Número total de días trabajados en el período evaluado.
    \item \textbf{Variabilidad de jornada}: Variabilidad en las horas trabajadas día a día.
\end{itemize}

{{ tabla_clusters_finde }}

{{ empleados_clusters_finde }}
{% endif %}




\end{document}
"""

def render_report(context: dict, output_path: str):
    tex = Template(LATEX_TEMPLATE).render(**context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex)

