from jinja2 import Template

LATEX_TEMPLATE = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\usepackage{xcolor}
\definecolor{corporativo}{RGB}{0,51,102}
\begin{document}

\begin{titlepage}
  \centering
  {\Huge\bfseries\textcolor{corporativo}{REPORTE DE TIEMPO DE TRABAJO}}\\
  {\Large Empresa: {{ empresa }}}\\
  {\normalsize Período: {{ periodo_inicio }} -- {{ periodo_fin }}}\\
  \vfill
  {\small Fecha de elaboración: {{ fecha_elaboracion }}}\\
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

\section{Detalles de Marcajes}
{% for nombre, regs in detalles_marcajes.items() %}
\subsection*{{ nombre }}
\begin{tabular}{lccc}
\toprule
Fecha & Entrada & Salida & Hrs trabajadas\\
\midrule
{% for r in regs %}
{{ r['Fecha'] }} & {{ r['Entrada'].time() }} & {{ r['Salida'].time() }} & {{ "%.2f"|format(r['Jornada'].total_seconds()/3600) }}\\
{% endfor %}
\bottomrule
\end{tabular}
{% endfor %}

\end{document}
"""

def render_report(context: dict, output_path: str):
    tex = Template(LATEX_TEMPLATE).render(**context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex)

