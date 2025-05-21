# 🕒 Generador de Informes de Jornadas Laborales

Este proyecto permite procesar marcajes laborales desde un archivo Excel, analizarlos y generar automáticamente un informe profesional en formato PDF usando LaTeX. Está diseñado para el Departamento de Talento Humano del Hospital María de Especialidades Pediátricas.

## 📄 Características

- Procesamiento de entradas y salidas de personal  
- Detección de días atípicos y jornadas incompletas  
- Análisis por mes, tipo de día (semana o fin de semana)  
- Informes detallados por empleado y resumen general  
- Exportación automatizada a PDF con diseño corporativo  

## 🚀 Requisitos

- Python 3.8+  
- TeX Live o similar (para compilar LaTeX)  
- Google Colab (opcional para ejecución en la nube)  

# 📂 Estructura del proyecto
reportgen/

├── data_loader.py         # Carga y validación del archivo de marcajes

├── processing.py          # Procesamiento y análisis de datos

├── templating.py          # Plantilla LaTeX con Jinja2

├── generador.py           # Función principal para generar el informe

# 📄 Licencia

MIT License. Desarrollado con fines educativos y de automatización interna.
