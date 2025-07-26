from jinja2 import Template
from datetime import datetime, timedelta
from reportgen.processing import dias_semana

LATEX_TEMPLATE = r"""
% ======================================================================
% PLANTILLA JINJA2 - ESTILO CORPORATIVO ELEGANTE
% Creado por: Asistente de IA
% Fecha: 2024-10-27
% ======================================================================
\documentclass[11pt,a4paper]{article}

% --- PAQUETES NECESARIOS ---
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage[table]{xcolor}
\usepackage{sectsty}        % Para estilos de sección sencillos
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tcolorbox}
\tcbuselibrary{skins}     % Para sombras y estilos avanzados en tcolorbox
\usepackage{array}
\usepackage{calc}
\usepackage{lato}           % Fuente profesional moderna
\usepackage{enumitem}
\usepackage{hyperref}
\renewcommand{\familydefault}{\sfdefault} % Hace que Lato sea la fuente por defecto

% --- CONFIGURACIÓN DE ESTILO ---
% 1. Desactivamos la numeración de secciones
\setcounter{secnumdepth}{-1}

% 2. Paleta de colores corporativa
\definecolor{primary}{RGB}{45,55,72}      % Gris azulado oscuro
\definecolor{secondary}{RGB}{113,128,150} % Gris medio
\definecolor{accent}{RGB}{235, 240, 247}  % Gris muy claro
\definecolor{text}{RGB}{74,85,104}        % Gris oscuro para texto
\definecolor{alert}{RGB}{197,48,48}       % Rojo discreto para alertas

% 3. Geometría de la página
\geometry{a4paper, margin=2cm, headheight=2cm, footskip=1.5cm}

% 4. Encabezado y pie de página con el nuevo estilo
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\headrule}{\color{secondary!50}\hrule width\headwidth height\headrulewidth}
\fancyhead[L]{\color{primary}\large\bfseries Hospital María Especialidades Pediátricas}
\fancyhead[R]{\color{text}\normalsize Reporte de Asistencias}
\fancyfoot[C]{\color{text}\thepage}
\fancyfoot[R]{\color{text}{{ mes_inicio }} {{ año }}}

% 5. Estilos de títulos (método sencillo y robusto con sectsty)
\sectionfont{\normalfont\huge\bfseries\color{primary}}
\subsectionfont{\normalfont\Large\bfseries\color{primary}}
\subsubsectionfont{\normalfont\large\bfseries\color{primary}}

% 6. Configuración de hipervínculos
\hypersetup{
    colorlinks=true,
    linkcolor=primary,
    urlcolor=secondary,
    citecolor=primary
}

% ======================================================================
% INICIO DEL DOCUMENTO
% ======================================================================
\begin{document}
\color{text} % Color de texto por defecto

% --- PÁGINA DE TÍTULO ---
\begin{titlepage}
  \centering
  \vspace*{3cm}
  \textcolor{secondary}{\large\bfseries REPORTE MENSUAL DE ASISTENCIAS}
  \vspace{0.5cm}
  \\
  {\huge\bfseries\color{primary}Departamento de {{ departamento }}\par}
  \vspace{1.5cm}
  {\large Período Analizado: {{ inicio_fechas }} - {{ final_fechas }}\par}
  \vspace{2.5cm}
  {\large\bfseries\color{primary}Colaboradores Analizados:\par}
  \vspace{0.5cm}
  \begin{itemize}[label=\color{secondary}\textbullet, itemsep=5pt, leftmargin=*]
    {% for empleado in empleados %}
      \item {{ empleado }}
    {% endfor %}
  \end{itemize}
  \vfill
  \begin{tabular}{r @{\hspace{1em}} l}
    \bfseries Informe generado por: & Departamento de Talento Humano \\
    \bfseries Fecha de generación: & \today \\
  \end{tabular}
\end{titlepage}

% --- TABLA DE CONTENIDOS ---
\tableofcontents
\clearpage

% --- PÁGINA DE RESUMEN GENERAL (SI HAY MÁS DE UN EMPLEADO) ---
{% if empleados|length > 1 %}
\section{Resumen General}
\vspace{0.5cm}
A continuación se presentan las tablas resumen con el total de horas laboradas, segmentado por días de semana y fines de semana.

\subsection{Días de Semana}
\begin{longtable}{l l r r}
    \toprule
    \rowcolor{primary}
    \textcolor{white}{\bfseries Empleado} & 
    \textcolor{white}{\bfseries Días} & 
    \textcolor{white}{\bfseries Total Horas} & 
    \textcolor{white}{\bfseries Promedio Jornada} \\
    \midrule
    \endfirsthead
    {# Lógica para el resumen fusionado (multi-mes) o el normal #}
    {% if resumen_fusionado %}
        {% for row in resumen_fusionado if row.Tipo_dia == "Día de semana" %}
            {{ row.Nombre }} & {{ row.Dias_trabajados }} & {{ "%.2f"|format(row.Total_horas) }} & {{ "%.2f"|format(row.Total_horas / row.Dias_trabajados if row.Dias_trabajados > 0 else 0) }}\\
        {% endfor %}
    {% else %}
        {# Asumimos que la estructura es resumen_por_mes_y_tipo_dia #}
        {% for mes, tipos_dia in resumen_por_mes_y_tipo_dia.items() %}
            {% if 'Día de semana' in tipos_dia %}
                {% for row in tipos_dia['Día de semana'] %}
                    {{ row.nombre }} & {{ row.dias_trabajados }} & {{ "%.2f"|format(row.total_horas) }} & {{ "%.2f"|format(row.promedio_jornada) }}\\
                {% endfor %}
            {% endif %}
        {% endfor %}
    {% endif %}
    \bottomrule
\end{longtable}

\subsection{Fines de Semana}
\begin{longtable}{l l r r}
    \toprule
    \rowcolor{primary}
    \textcolor{white}{\bfseries Empleado} & 
    \textcolor{white}{\bfseries Días} & 
    \textcolor{white}{\bfseries Total Horas} & 
    \textcolor{white}{\bfseries Promedio Jornada} \\
    \midrule
    \endfirsthead
    {% if resumen_fusionado %}
        {% for row in resumen_fusionado if row.Tipo_dia == "Fin de semana" %}
            {{ row.Nombre }} & {{ row.Dias_trabajados }} & {{ "%.2f"|format(row.Total_horas) }} & {{ "%.2f"|format(row.Total_horas / row.Dias_trabajados if row.Dias_trabajados > 0 else 0) }}\\
        {% endfor %}
    {% else %}
        {% for mes, tipos_dia in resumen_por_mes_y_tipo_dia.items() %}
            {% if 'Fin de semana' in tipos_dia %}
                {% for row in tipos_dia['Fin de semana'] %}
                    {{ row.nombre }} & {{ row.dias_trabajados }} & {{ "%.2f"|format(row.total_horas) }} & {{ "%.2f"|format(row.promedio_jornada) }}\\
                {% endfor %}
            {% endif %}
        {% endfor %}
    {% endif %}
    \bottomrule
\end{longtable}
\clearpage
{% endif %}


% --- SECCIÓN DE DETALLES POR EMPLEADO ---
\section{Detalles por Colaborador}
{% for nombre, meses in detalles_marcajes_por_mes.items() %}
    {% for mes, regs in meses.items() %}
        \subsection{ {{ nombre }} - ({{ mes }}) }

        {# Calculamos los totales del mes para los cuadros de resumen #}
        {% set ns = namespace(total_horas=0, dias_laborados=0, dias_fds=0) %}
        {% for r in regs %}
            {% set ns.total_horas = ns.total_horas + r['jornada'].total_seconds() / 3600 %}
            {% set ns.dias_laborados = ns.dias_laborados + 1 %}
            {% if r['dia'] in ['Sáb', 'Dom'] %}
                {% set ns.dias_fds = ns.dias_fds + 1 %}
            {% endif %}
        {% endfor %}

        {# Resumen numérico superior #}
        \begin{center}
        \begin{tabular}{@{}c@{\hspace{2cm}}c@{\hspace{2cm}}c@{}}
        \begin{minipage}{3.5cm}\centering
            {\color{primary}\Huge\bfseries {{ ns.dias_laborados }}}\\
            {\color{text}\small DÍAS LABORADOS}
        \end{minipage} &
        \begin{minipage}{3.5cm}\centering
            {\color{primary}\Huge\bfseries {{ "%.2f"|format(ns.total_horas) }}}\\
            {\color{text}\small HORAS TOTALES}
        \end{minipage} &
        \begin{minipage}{3.5cm}\centering
            {\color{primary}\Huge\bfseries {{ "%.2f"|format(ns.total_horas / ns.dias_laborados if ns.dias_laborados > 0 else 0) }}}\\
            {\color{text}\small PROMEDIO DIARIO (HRS)}
        \end{minipage}
        \end{tabular}
        \end{center}
        \vspace{1cm}

        {# Diseño de dos columnas con minipages #}
        \begin{minipage}[t]{0.58\textwidth}\parindent=0pt
            \subsubsection*{Registro Detallado de Marcajes}
            \begin{longtable}{p{2.2cm} p{1.3cm} p{1.7cm} p{1.7cm} r}
                \toprule
                \rowcolor{primary}
                \textcolor{white}{\bfseries Fecha} & 
                \textcolor{white}{\bfseries Día} & 
                \textcolor{white}{\bfseries Entrada} & 
                \textcolor{white}{\bfseries Salida} & 
                \textcolor{white}{\bfseries Horas} \\
                \midrule
                \endfirsthead
                {% for r in regs -%}
                    {% if r['jornada'].total_seconds() == 0 -%}
                        \rowcolor{alert!20}
                    {%- elif r['dia'] in ['Sáb', 'Dom'] -%}
                        \rowcolor{accent!60}
                    {%- endif -%}
                    
                    {%- if r['dia'] in ['Sáb', 'Dom'] -%}
                        \textbf{ {{ r['fecha'].strftime('%Y-%m-%d') }} } & \textbf{ {{ r['dia'] }} } & \textbf{ {{ r['entrada'].time() }} } & \textbf{ {{ r['salida'].time() }} } &
                    {%- else -%}
                        {{ r['fecha'].strftime('%Y-%m-%d') }} & {{ r['dia'] }} & {{ r['entrada'].time() }} & {{ r['salida'].time() }} &
                    {%- endif %}
                    
                    {%- if r['jornada'].total_seconds() == 0 -%}
                        \textcolor{alert}{ {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }} }
                    {%- elif r['dia'] in ['Sáb', 'Dom'] -%}
                         \textbf{ {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }} }
                    {%- else -%}
                        {{ "%.2f"|format(r['jornada'].total_seconds()/3600) }}
                    {%- endif -%}
                \\
                {% endfor %}
                \bottomrule
            \end{longtable}
            \vspace{0.5cm}
            \small\color{text}
            \textbf{Leyenda:} Filas en gris claro (\colorbox{accent!60}{\phantom{XX}}) son fines de semana. Filas en rojo (\colorbox{alert!20}{\phantom{XX}}) requieren verificación.
        \end{minipage}
        \hfill
        \begin{minipage}[t]{0.38\textwidth}\parindent=0pt
            \subsubsection*{Análisis Mensual}
            <tcolorbox>[enhanced, colback=accent!25, colframe=accent, boxrule=1pt, arc=2pt, drop shadow southeast]
                \small\renewcommand{\arraystretch}{1.3}
                {\bfseries\color{primary}Estadísticas Clave}\par\vspace{2mm}
                \begin{tabular}{@{}lr@{}}
                Días laborados: & \textbf{ {{ ns.dias_laborados }} } \\
                Días semana: & \textbf{ {{ ns.dias_laborados - ns.dias_fds }} } \\
                Días FDS: & \textbf{ {{ ns.dias_fds }} } \\
                \addlinespace
                Total Horas: & \textbf{ {{ "%.2f"|format(ns.total_horas) }} } \\
                \end{tabular}
            </tcolorbox>
            \vspace{4mm}
            
            {# Caja de Alertas: combina outliers y marcajes incompletos #}
            {% set alertas = namespace(items=[]) %}
            {# 1. Añadir outliers #}
            {% if nombre in outliers_por_persona_y_mes and mes in outliers_por_persona_y_mes[nombre] %}
                {% for o in outliers_por_persona_y_mes[nombre][mes] %}
                    {% set alertas.items = alertas.items + [(o['fecha'].strftime('%d %b'), o['Tipo'])] %}
                {% endfor %}
            {% endif %}
            {# 2. Añadir marcajes incompletos #}
            {% for r in regs if r['jornada'].total_seconds() == 0 %}
                 {% set alertas.items = alertas.items + [(r['fecha'].strftime('%d %b'), 'Marcaje 0 hrs')] %}
            {% endfor %}

            {% if alertas.items %}
            <tcolorbox>[enhanced, colback=accent!25, colframe=accent, boxrule=1pt, arc=2pt, drop shadow southeast]
                \small\renewcommand{\arraystretch}{1.2}
                {\bfseries\color{primary}Días con Alertas}\par\vspace{2mm}
                \begin{tabular}{@{}p{0.4\linewidth} p{0.55\linewidth}@{}}
                {% for fecha, motivo in alertas.items %}
                    \textbf{ {{ fecha }} } & {{ motivo }} \\
                {% endfor %}
                \end{tabular}
            </tcolorbox>
            {% endif %}
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