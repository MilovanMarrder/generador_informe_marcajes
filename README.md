# Informe de Marcajes – Proyecto Modular en Google Colab

Este proyecto proporciona un **Google Colab Notebook** que permite:

1. Cargar registros de marcajes en formato PDF.
2. Procesar y limpiar los datos para extraer entradas, salidas, jornadas y estadísticas.
3. Generar un informe profesional en LaTeX con tablas y secciones dinámicas.
4. Compilar el documento `.tex` a PDF directamente en Colab.

El notebook crea automáticamente varios módulos Python para separar responsabilidades y facilitar el mantenimiento, la extensión y las pruebas.

---

## Estructura del Proyecto

```plain
├── data_loader.py           # Módulo para leer el PDF crudo con tabula-py
├── preprocessing.py         # Funciones para pivotar datos y calcular puntualidad
├── analytics.py             # Funciones de resumen general, detección de outliers y por empleado
├── templating.py            # Renderizado de plantilla LaTeX usando Jinja2
├── report_template.tex.jinja# Plantilla LaTeX parametrizada con Jinja2
├── reporte.tex              # Archivo LaTeX generado (output)
├── reporte.pdf              # Reporte compilado (output)
└── README.md                # Documentación del proyecto
```

---

## Requisitos

- **Google Colab**: no requiere instalación local de Python.
- **Librerías Python** (instaladas automáticamente en Colab):
  - `tabula-py`
  - `jinja2`
  - `pandas`, `numpy`
  - `pdflatex` (paquetes TeX Live básicos instalados en Colab)

---

## Uso en Google Colab

1. **Copiar el Notebook**
   - Abre este proyecto en Colab o importa el fichero `.ipynb` en https://colab.research.google.com.

2. **Ejecutar Celdas de Módulo**
   - Celda 1: Instala dependencias e importaciones globales.
   - Celdas 2–5: Generan automáticamente los módulos Python (`data_loader.py`, `preprocessing.py`, etc.) y la plantilla LaTeX (`report_template.tex.jinja`).

3. **Subir el PDF de marcajes**
   - Celda 7: Se abrirá el diálogo de `files.upload()`. Selecciona el archivo PDF con los marcajes.

4. **Procesar Datos**
   - El orquestador lee el PDF, pivota los datos, calcula jornadas y puntualidad, y genera resúmenes.

5. **Definir Parámetros**
   - Ajusta en la celda de contexto:
     ```python
     periodo_inicio = 'DD/MM/AAAA'
     periodo_fin    = 'DD/MM/AAAA'
     empresa        = 'Nombre de la Empresa'
     autor          = 'Departamento de RRHH'
     logo_path      = 'logo.png'  # opcional: subir imagen de logo
     ```

6. **Renderizar y Compilar**
   - El notebook renderizará `reporte.tex` desde la plantilla y contexto.
   - Se instalarán los paquetes TeX Live en Colab y se llamará a `pdflatex`.
   - Finalmente, se descargará `reporte.pdf` listo para imprimir o distribuir.

---

## Personalización

- **Plantilla**: `report_template.tex.jinja` contiene todo el layout en LaTeX. Puedes modificar colores, tipografías o secciones.
- **Módulos Python**:
  - `data_loader.py`: ajustes para diferentes formatos de PDF.
  - `preprocessing.py`: lógica de clasificación de horas y días.
  - `analytics.py`: métricas, outliers y agrupaciones.
  - `templating.py`: cambiar motor de plantillas o formatos de salida.

---

## Contribuciones

1. Haz un fork de este repositorio.
2. Crea una rama con tu mejora: `feature/mi-mejora`.
3. Asegúrate de probar en Colab.
4. Abre un Pull Request describiendo los cambios.

---

## Licencia

Este proyecto no tiene licencia

