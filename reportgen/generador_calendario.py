import calendar
import datetime
import jinja2
import os
from typing import Dict, List, Optional, Tuple

class CalendarioLatex:
    def __init__(self):
        # Definir nombres de los meses en español
        self.nombres_meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        # Definir los nombres de los días en español (abreviados)
        self.nombres_dias = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa']
        
        # Configurar Jinja2
        self.template_loader = jinja2.FileSystemLoader(searchpath="./")
        self.template_env = jinja2.Environment(loader=self.template_loader)
    
    def generar_calendario(self, 
                          anio: int, 
                          mes: int, 
                          dias_festivos: List[int] = None, 
                          dias_no_laborados: List[int] = None,
                          output_file: str = None) -> str:
        """
        Genera un calendario en formato LaTeX para el mes y año especificados.
        
        Args:
            anio: Año del calendario
            mes: Mes del calendario (1-12)
            dias_festivos: Lista de días del mes que son festivos
            dias_no_laborados: Lista de días del mes que no se trabajan (además de fines de semana)
            output_file: Ruta del archivo de salida (si None, solo retorna el contenido)
            
        Returns:
            Contenido del archivo LaTeX generado
        """
        if dias_festivos is None:
            dias_festivos = []
        if dias_no_laborados is None:
            dias_no_laborados = []
            
        # Obtener el calendario del mes
        cal = calendar.monthcalendar(anio, mes)
        
        # Preparar datos para la plantilla
        nombre_mes = self.nombres_meses[mes]
        semanas = []
        
        for semana in cal:
            semana_formateada = []
            for dia in semana:
                if dia == 0:
                    # Día vacío (no pertenece al mes)
                    semana_formateada.append({'numero': '', 'tipo': 'vacio'})
                else:
                    # Determinar el tipo de día (laboral, festivo, fin de semana, no laborado)
                    fecha = datetime.date(anio, mes, dia)
                    if fecha.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
                        tipo = 'fin_semana'
                    elif dia in dias_festivos:
                        tipo = 'festivo'
                    elif dia in dias_no_laborados:
                        tipo = 'no_laborado'
                    else:
                        tipo = 'laboral'
                    
                    semana_formateada.append({'numero': dia, 'tipo': tipo})
            
            semanas.append(semana_formateada)
        
        # Datos para la plantilla
        contexto = {
            'anio': anio,
            'mes': mes,
            'nombre_mes': nombre_mes,
            'semanas': semanas,
            'dias_semana': self.nombres_dias
        }
        
        # Cargar la plantilla desde una cadena
        template_str = self.get_template_string()
        #template = jinja2.Template(template_str)
        template = self.template_env.from_string(template_str)
        
        # Renderizar el calendario
        latex_output = template.render(contexto)
        
        # Guardar en archivo si se especificó
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(latex_output)
        
        return latex_output
    
    def get_template_string(self) -> str:
        """
        Devuelve la plantilla LaTeX como una cadena de texto.
        """
        return r"""
                    \documentclass{article}
                    \usepackage[utf8]{inputenc}
                    \usepackage[T1]{fontenc}
                    \usepackage{xcolor}
                    \usepackage{tikz} 

                    
                    \definecolor{mygreen}{HTML}{C8E6C9}
                    \definecolor{rose}{HTML}{d590b6} 
                    \definecolor{myred}{HTML}{FF4646}

                    
                    \tikzset{
                        
                        day_circle_base/.style={
                            circle,               
                            minimum size=7.5mm,   
                            inner sep=0pt,        
                            font=\sffamily\normalsize, 
                            text centered 
                        },
                       
                        day_green_circle/.style={
                            day_circle_base,
                            fill=mygreen   
                        },
                        
                        day_blue_circle/.style={
                            day_circle_base,
                            fill=rose  
                        },
                        day_red_circle/.style={
                            day_circle_base,
                            fill=myred
                        }, 
                        
                        day_text_only/.style={
                            minimum width=7.5mm, 
                            minimum height=7.5mm,  
                            font=\sffamily\normalsize,
                            text centered
                        },
                        
                        empty_day_cell/.style={
                            minimum width=7.5mm,
                            minimum height=7.5mm
                        }
                    }

                   
                    
                    \newcommand{\daycolored}[2]{\tikz{\node[#1] {#2};}}
                    
                    \newcommand{\daytext}[1]{\tikz{\node[day_text_only] {#1};}}
                    
                    \newcommand{\emptyday}{\tikz{\node[empty_day_cell] {};}}

                    \begin{document}

                    \begin{center}
                    \Large \textbf{{{ nombre_mes }} {{ anio }}}
                    \vspace{0.5cm}

                   
                    \renewcommand{\arraystretch}{1.5} 

                    \begin{tabular}{ccccccc}
                    
                    {% for dia in dias_semana %}
                    \textbf{{{ dia }}}{% if not loop.last %} & {% endif %}
                    {% endfor %}\\[3pt]

                    {% for semana in semanas %}
                    {% for dia in semana %}
                    {% if dia.numero == '' %}
                    \emptyday
                    {% elif dia.tipo == 'fin_semana' %}
                    \daytext{{{ dia.numero }}}
                    {% elif dia.tipo == 'festivo' %}
                    \daycolored{day_blue_circle}{{{ dia.numero }}}
                    {% elif dia.tipo == 'no_laborado' %}
                    \daycolored{day_red_circle}{{{ dia.numero }}}
                    {% else %}
                    \daycolored{day_green_circle}{{{ dia.numero }}}
                    {% endif %}
                    {% if not loop.last %} & {% endif %}
                    {% endfor %}
                    \\
                    {% endfor %}

                    \end{tabular}
                    \end{center}

                    \end{document}
                    """

# Ejemplo de uso
if __name__ == "__main__":
    calendario = CalendarioLatex()
    
    # Configuración del calendario
    anio = 2025
    mes = 6  # Junio
    dias_festivos = [12, 13]  # Días festivos en junio
    dias_no_laborados = [4]  # Días no laborados adicionales
    
    # Generar el calendario
    latex_output = calendario.generar_calendario(
        anio=anio,
        mes=mes,
        dias_festivos=dias_festivos,
        dias_no_laborados=dias_no_laborados,
        output_file="calendario_junio_2025.tex"
    )
    
    print(f"Calendario para {calendario.nombres_meses[mes]} {anio} generado correctamente.")
    print("Archivo guardado como 'calendario_junio_2025.tex'")
    
    # Si deseas compilar automáticamente el archivo LaTeX (requiere pdflatex instalado)
    # import subprocess
    # subprocess.run(["pdflatex", "calendario_junio_2025.tex"])
    # print("PDF generado correctamente.")
    
def generar_calendario_personalizado():
    """
    Ejemplo de cómo generar un calendario personalizado con días festivos
    y días no laborados específicos.
    """
    calendario = CalendarioLatex()
    
    # Puedes configurar para el mes actual o cualquier otro mes
    hoy = datetime.date.today()
    anio = int(input("Introduce el año (YYYY): "))
    mes = int(input("Introduce el mes (1-12): "))
    
    # Solicitar los días festivos
    input_festivos = input("Introduce los días festivos separados por comas (ej: 1,5,24): ")
    dias_festivos = [int(d.strip()) for d in input_festivos.split(",") if d.strip()]
    
    # Solicitar los días no laborados
    input_no_laborados = input("Introduce los días no laborados separados por comas (ej: 2,15): ")
    dias_no_laborados = [int(d.strip()) for d in input_no_laborados.split(",") if d.strip()]
    
    # Nombre del archivo de salida
    nombre_archivo = f"calendario_{anio}_{mes}.tex"
    
    # Generar el calendario
    latex_output = calendario.generar_calendario(
        anio=anio,
        mes=mes,
        dias_festivos=dias_festivos,
        dias_no_laborados=dias_no_laborados,
        output_file=nombre_archivo
    )
    
    print(f"Calendario para {calendario.nombres_meses[mes]} {anio} generado correctamente.")
    print(f"Archivo guardado como '{nombre_archivo}'")
    
    # Preguntar si desea compilar el archivo LaTeX
    compilar = input("¿Deseas compilar el archivo LaTeX a PDF? (s/n): ")
    if compilar.lower() == 's':
        try:
            import subprocess
            resultado = subprocess.run(["pdflatex", nombre_archivo], capture_output=True, text=True)
            if resultado.returncode == 0:
                print(f"PDF generado correctamente como {nombre_archivo.replace('.tex', '.pdf')}")
            else:
                print("Error al generar el PDF. Asegúrate de tener pdflatex instalado.")
                print("Error:", resultado.stderr)
        except Exception as e:
            print(f"Error al intentar compilar: {e}")
            print("Asegúrate de tener pdflatex instalado en tu sistema.")
    
    return latex_output