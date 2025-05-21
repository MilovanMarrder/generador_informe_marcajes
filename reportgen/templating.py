from jinja2 import Template
from datetime import datetime, timedelta

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
\usepackage{float}
\usepackage{colortbl}
\usepackage{longtable}

% Definición de colores
\definecolor{corporativo}{RGB}{180,0,0}
\definecolor{grisclaro}{RGB}{245,245,245}

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

% Encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\fancyhead[L]{\textcolor{corporativo}{\textbf{Hospital María Especialidades Pediátricas}}}
\fancyhead[R]{\textcolor{corporativo}{\textbf{Reporte Jornadas de Trabajo}}}
\fancyfoot[C]{\textcolor{corporativo}{\thepage}}
\fancyfoot[L]{\textcolor{corporativo}{departamento}}
\fancyfoot[R]{\textcolor{corporativo}{Marzo 2025}}

% Estilos de títulos
\titleformat{\section}
  {\normalfont\Large\bfseries\color{corporativo}}
  {}{0em}{}[\titlerule]
\titleformat{\subsection}
  {\normalfont\large\bfseries\color{corporativo}}
  {}{0em}{}

% Eliminar sangría
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

% Listas
\setlist{noitemsep, leftmargin=1.5em}

% Hipervínculos
\hypersetup{
  colorlinks=true,
  linkcolor=corporativo,
  urlcolor=corporativo
}

% Sin numeración de secciones
\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}

% Comandos personalizados
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

\newcommand{\mejoradatabla}[1]{
  \renewcommand{\arraystretch}{1.3}
  \setlength{\tabcolsep}{10pt}
  #1
  \renewcommand{\arraystretch}{1}
  \setlength{\tabcolsep}{6pt}
}

\begin{document}

% --- Página de título ---
\begin{titlepage}
  \centering
  \vspace*{2cm}

  {\Huge\bfseries\textcolor{corporativo}{Reporte de Jornadas en {{ departamento }}}\par}
  \vspace{1cm}
  {\color{gray}\rule{\textwidth}{0.4pt}\par}
  \vspace{0.5cm}
  {\large Per\'iodo Analizado: {{ inicio_fechas }} - {{ final_fechas }}\par}

  \vspace{1cm}

  {\large\bfseries Colaboradores analizados:\par}
  \begin{itemize*}
    \centering
    {% for empleado in empleados %}
      \item {{ empleado }}
    {% endfor %}
  \end{itemize*}

  \vspace{2cm}

  \begin{tabular}{>{\bfseries}r @{\hspace{1em}} l}
  Informe generado por: & Departamento de Talento Humano \\
  Fecha de generaci\'on: & \today \\
  \end{tabular}

  \vfill

  {\color{gray}\rule{0.6\textwidth}{0.4pt}\par}
  \vspace{0.5cm}
  {\large\bfseries\textcolor{corporativo}{Hospital María Especialidades Pediátricas}\par}
\end{titlepage}


\tableofcontents
\clearpage

{% if empleados|length > 1 %}
\section{Resumen General}

\infobox{Horas trabajadas por período, tipo de día y empleado}{
  A continuación se presenta el detalle de los días trabajados, horas totales y promedio de jornada por empleado, diferenciando entre días de semana y fines de semana.
}

{% if resumen_fusionado %}
% Resumen integrado con todos los meses en una sola tabla
\subsection{Días de semana}

\vspace{0.5cm}
\begin{table}[H]
\centering
\mejoradatabla{
\begin{tabular}{>{\bfseries}lllrr}
\toprule
\rowcolor{grisclaro} \textbf{Mes} & \textbf{Empleado} & \textbf{Días} & \textbf{Total Hrs} & \textbf{Promedio Jornada}\\
\midrule
{% for row in resumen_fusionado %}
{% if row.Tipo_dia == "Día de semana" %}
{{ row.Mes }} & {{ row.Nombre }} & {{ row.Dias_trabajados }} & {{ "%.2f"|format(row.Total_horas) }} & {{ "%.2f"|format(row.Total_horas / row.Dias_trabajados) }}\\
{% endif %}
{% endfor %}
\bottomrule
\end{tabular}
}
\caption{Detalle de días de semana para todos los períodos}
\end{table}

\subsection{Fines de semana}

\vspace{0.5cm}
\begin{table}[H]
\centering
\mejoradatabla{
\begin{tabular}{>{\bfseries}lllrr}
\toprule
\rowcolor{grisclaro} \textbf{Mes} & \textbf{Empleado} & \textbf{Días} & \textbf{Total Hrs} & \textbf{Promedio Jornada}\\
\midrule
{% for row in resumen_fusionado %}
{% if row.Tipo_dia == "Fin de semana" %}
{{ row.Mes }} & {{ row.Nombre }} & {{ row.Dias_trabajados }} & {{ "%.2f"|format(row.Total_horas) }} & {{ "%.2f"|format(row.Total_horas / row.Dias_trabajados) }}\\
{% endif %}
{% endfor %}
\bottomrule
\end{tabular}
}
\caption{Detalle de fines de semana para todos los períodos}
\end{table}

{% else %}
% Formato anterior (por si no está disponible resumen_fusionado)
{% for mes, tipos_dia in resumen_por_mes_y_tipo_dia.items() %}

\section{ {{ mes }} }

{% for tipo_dia, registros in tipos_dia.items() %}

\subsection{ {{ tipo_dia }} }

\vspace{0.5cm}
\begin{table}[H]
\centering
\mejoradatabla{
\begin{tabular}{>{\bfseries}lrrr}
\toprule
\rowcolor{grisclaro} \textbf{Empleado} & \textbf{Días} & \textbf{Total Hrs} & \textbf{Promedio Jornada}\\
\midrule
{% for row in registros %}
{{ row.Nombre }} & {{ row.Dias_trabajados }} & {{ "%.2f"|format(row.Total_horas) }} & {{ "%.2f"|format(row.Promedio_jornada) }}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\caption{Detalle de {{ tipo_dia }} en {{ mes }}}
\end{table}

{% endfor %}
{% endfor %}
{% endif %}
{% endif %}


\clearpage

\section{Detalles de Marcajes}

{% for nombre, meses in detalles_marcajes_por_mes.items() %}

\subsection{ {{ nombre }} }

{% for mes, regs in meses.items() %}

\subsubsection*{ {{ mes }} }

{{ nombre }}

\begin{minipage}[t]{0.62\textwidth}
\mejoradatabla{
\begin{tabular}{lccc}
\toprule
\rowcolor{grisclaro} \textbf{Fecha} & \textbf{Entrada} & \textbf{Salida} & \textbf{Hrs trabajadas}\\
\midrule
{% for r in regs %}
{{ r['Fecha'].strftime('%Y-%m-%d') }} & {{ r['Entrada'].time() }} & {{ r['Salida'].time() }} & {{ "%.2f"|format(r['Jornada'].total_seconds()/3600) }}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\end{minipage}
\hfill
\begin{minipage}[t]{0.35\textwidth}
{% if nombre in outliers_por_persona_y_mes and mes in outliers_por_persona_y_mes[nombre] and outliers_por_persona_y_mes[nombre][mes]|length > 0 %}
\infobox{D\'ias At\'ipicos}{
\begin{tabular}{lr}
\toprule
\rowcolor{grisclaro} \textbf{Fecha} & \textbf{Tipo}\\
\midrule
{% for o in outliers_por_persona_y_mes[nombre][mes] %}
{{ o['Fecha'].strftime('%Y-%m-%d') }} & {{ o['Tipo'] }}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\vspace{1em}
{% endif %}
\infobox{Resumen del Mes}{
\begin{tabular}{lr}
\toprule
\rowcolor{grisclaro} \textbf{Total Días} & {{ regs|length }}\\
\midrule
\rowcolor{grisclaro} \textbf{Total Horas} &
{%- set total_horas = namespace(value=0) -%}
{%- for r in regs -%}
    {%- if r['Jornada'] is defined and r['Jornada'] is not none -%}
        {%- set total_horas.value = total_horas.value + r['Jornada'].total_seconds() / 3600 -%}
    {%- endif -%}
{%- endfor -%}
{{ "%.2f"|format(total_horas.value) }}\\
\bottomrule
\end{tabular}
}
\end{minipage}

\clearpage
{% endfor %}
{% endfor %}

\end{document}
"""


def render_report(context: dict, output_path: str):
    tex = Template(LATEX_TEMPLATE).render(**context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex)