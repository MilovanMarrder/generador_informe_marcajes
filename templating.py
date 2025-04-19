from jinja2 import Template

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

\begin{document}
\begin{document}

\begin{titlepage}
  \centering
  \vspace*{2cm}
  {\Huge\bfseries\textcolor{corporativo}{REPORTE DE TIEMPOS DE TRABAJO}\par}
  \vspace{1.5cm}
  {\Large\textbf{Empresa Marrder}\par}
  \vspace{1cm}
  {\large Período: {{inicio_fechas}} - {{final_fechas}}\par}
  \vspace{5cm}
  
  \begin{tabular}{rl}
    \textbf{Informe elaborado por:} & Departamento de Recursos Humanos \\
    \textbf{Fecha de elaboración:} & 03/04/2025 \\
    \textbf{Documento:} & Confidencial \\
  \end{tabular}
  
  \vfill
  \includegraphics[width=0.3\textwidth]{example-image} % Reemplazar con el logo real
\end{titlepage}



\tableofcontents\newpage

\section{Resumen General}
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


\end{document}
"""

def render_report(context: dict, output_path: str):
    tex = Template(LATEX_TEMPLATE).render(**context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex)

