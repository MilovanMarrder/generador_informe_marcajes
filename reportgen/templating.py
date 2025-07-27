from jinja2 import Template
from datetime import datetime, timedelta
# from reportgen.processing import dias_semana


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
\usepackage[table]{xcolor}

 

% Definición de colores
\definecolor{corporativo}{RGB}{45,55,72}
\definecolor{grisclaro}{RGB}{245,245,245}
\definecolor{jornadacero}{RGB}{211, 47, 47}

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
\fancyhead[R]{\textcolor{corporativo}{\textbf{Reporte Mensual de Asistencias}}}
\fancyfoot[C]{\textcolor{corporativo}{\thepage}}
\fancyfoot[L]{\textcolor{corporativo}{ Departamento de {{ departamento }}}}
\fancyfoot[R]{\textcolor{corporativo}{ {{mes_inicio}} {{año}}}}

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

  {\Huge\bfseries\textcolor{corporativo}{Reporte Mensual de Asistencias\\ Departamento de {{ departamento }}}\par}
  \vspace{1cm}
  {\color{gray}\rule{\textwidth}{0.4pt}\par}
  \vspace{0.5cm}
  {\large Per\'iodo Analizado: {{ inicio_fechas }} - {{ final_fechas }}\par}

  \vspace{1cm}

  {\large\bfseries Colaboradores:\par}
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
  {\large\textcolor{corporativo}{\textit{Cambiamos la vida de nuestros pacientitos}}\par}
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
\rowcolor{grisclaro} \textbf{Empleado} & \textbf{Trabajado} & \textbf{Total Hrs} & \textbf{Horas por Día}\\
\midrule
{% for row in resumen_fusionado %}
{% if row.tipo_dia == "Día de semana" %}
{{ row.nombre }} & {{ row.dias_trabajados }} & {{ "%.2f"|format(row.total_horas) }} & {{ "%.2f"|format(row.total_horas / row.dias_trabajados) }}\\
{% endif %}
{% endfor %}
\bottomrule
\end{tabular}
}
\end{table}

\subsection{Fines de semana}

\vspace{0.5cm}
\begin{table}[H]
\centering
\mejoradatabla{
\begin{tabular}{>{\bfseries}lllrr}
\toprule
\rowcolor{grisclaro} \textbf{Empleado} & \textbf{Trabajado} & \textbf{Total Hrs} & \textbf{Horas por Día}\\
\midrule
{% for row in resumen_fusionado %}
{% if row.tipo_dia != "Día de semana" %}
{{ row.nombre }} & {{ row.dias_trabajados }} & {{ "%.2f"|format(row.total_horas) }} & {{ "%.2f"|format(row.total_horas / row.dias_trabajados) }}\\
{% endif %}
{% endfor %}
\bottomrule
\end{tabular}
}
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
\rowcolor{grisclaro} \textbf{Empleado} & \textbf{Días} & \textbf{Total Hrs} & \textbf{Horas por Día}\\
\midrule
{% for row in registros %}
{{ row.nombre }} & {{ row.dias_trabajados }} & {{ "%.2f"|format(row.total_horas) }} & {{ "%.2f"|format(row.promedio_jornada) }}\\
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

\section{Detalles de Marcajes por Colaborador}
{% for nombre, meses in detalles_marcajes_por_mes.items() %}
\subsection{ {{ nombre }} }
{% for mes, regs in meses.items() %}

\begin{tabular}{p{0.6\textwidth}p{0.4\textwidth}}
% Columna izquierda con la tabla principal
\mejoradatabla{
\begin{tabular}{p{2cm} p{0.6cm} p{1.2cm} p{1.2cm} r}
\toprule
\rowcolor{grisclaro} \textbf{fecha} & \textbf{dia} & \textbf{entrada} & \textbf{salida} & \textbf{Hrs}\\
\midrule

{% for r in regs -%}
{% if r['jornada'].total_seconds() == 0 -%}
\rowcolor{jornadacero!20}
{%- else -%}
\rowcolor{white}
{%- endif -%}
{%- if r['dia'] in ['Sáb', 'Dom'] -%}
% -Fila de fin de semana (color corporativo)
\rowcolor{corporativo!20}
 {{ r['fecha'].strftime('%Y-%m-%d') }}  &  {{ r['dia'] }}  &  {{ r['entrada'].time() }}  &  {{ r['salida'].time() }}  &
    {%- if r['jornada'].total_seconds() == 0 -%}
        %-Jornada cero en fin de semana: negrita y texto rojo
         \textcolor{jornadacero}{ {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }} } 
    {%- else -%}
        %-Jornada normal en fin de semana: solo negrita
         {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }} 
    {%- endif %}
{%- else -%}
%---Fila de día de semana (sin negrita)
{{ r['fecha'].strftime('%Y-%m-%d') }} & {{ r['dia'] }} & {{ r['entrada'].time() }} & {{ r['salida'].time() }} &
    {%- if r['jornada'].total_seconds() == 0 -%}

        \textcolor{jornadacero}{ {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }} }
    {%- else -%}
        {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }}
    {%- endif %}
{%- endif -%}

\\
{% endfor %}
\bottomrule
\end{tabular}
}
&
% Columna derecha con las cajas de información
\begin{tabular}{c}
{% if nombre in outliers_por_persona_y_mes and mes in outliers_por_persona_y_mes[nombre] and outliers_por_persona_y_mes[nombre][mes]|length > 0 %}
\infobox{D\'ias At\'ipicos}{
\begin{tabular}{p{2cm} p{2cm}}
\toprule
\rowcolor{grisclaro} \textbf{fecha} & \textbf{Tipo}\\
\midrule
{% for o in outliers_por_persona_y_mes[nombre][mes] %}
{{ o['fecha'].strftime('%Y-%m-%d') }} & {{ o['tipo'] }}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\\
\\
{% endif %}

{% set dias_fin_semana = [] %}
{% for r in regs %}
    {% if r['fecha'].weekday() >= 5 %}
        {% set dias_fin_semana = dias_fin_semana.append(r) or dias_fin_semana %}
    {% endif %}
{% endfor %}
{% if dias_fin_semana and dias_fin_semana|length > 0 %}
\infobox{Fines de Semana Trabajados}{
\begin{tabular}{p{1.8cm} p{0.9cm} p{0.9 cm}}
\toprule
\rowcolor{grisclaro} \textbf{fecha} & \textbf{dia} & \textbf{Horas}\\
\midrule
{% for r in dias_fin_semana %}
{{ r['fecha'].strftime('%Y-%m-%d') }}& {{ r['dia'] }} & {{ "%.2f"|format(r['jornada'].total_seconds() / 3600) }}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\\
\\
{% endif %}

{% set marcajes_incompletos = [] %}
{% for r in regs %}
    {% if r['jornada'] is defined and r['jornada'].total_seconds() == 0 %}
        {% set marcajes_incompletos = marcajes_incompletos.append(r) or marcajes_incompletos %}
    {% endif %}
{% endfor %}
{% if marcajes_incompletos and marcajes_incompletos|length > 0 %}
\infobox{D\'ias con Marcaje Incompleto}{
\begin{tabular}{p{2.5cm} p{1.5cm}}
\toprule
\rowcolor{grisclaro} \textbf{fecha} & \textbf{dia}\\
\midrule
{% for r in marcajes_incompletos %}
{{ r['fecha'].strftime('%Y-%m-%d') }} & {{r['dia']}}\\
{% endfor %}
\bottomrule
\end{tabular}
}
\\
\\
{% endif %}

\infobox{Resumen del Mes}{
\begin{tabular}{p{2.5cm} p{1.5cm}}
\toprule
\rowcolor{grisclaro} \textbf{Total Días} & {{ regs|length }}\\
\midrule
\rowcolor{grisclaro} \textbf{Total Horas} &
{%- set total_horas = namespace(value=0) -%}
{%- for r in regs -%}
    {%- if r['jornada'] is defined and r['jornada'] is not none -%}
        {%- set total_horas.value = total_horas.value + r['jornada'].total_seconds() / 3600 -%}
    {%- endif -%}
{%- endfor -%}
{{ "%.2f"|format(total_horas.value) }}\\
\bottomrule
\end{tabular}
}
\end{tabular}
\end{tabular}
\clearpage
{% endfor %}
{% endfor %}

\end{document}
"""


def render_report(context: dict, output_path: str):
    tex = Template(LATEX_TEMPLATE).render(**context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex)