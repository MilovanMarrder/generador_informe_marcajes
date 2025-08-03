# main_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from threading import Thread

# --- Importaciones de módulos personalizados ---
from utils.data import etl_df
from utils.generador import generar_informe

class ModernReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes Mensuales de Asistencia")
        self.root.geometry("1300x800")  # Aumentado el ancho para acomodar dos columnas
        self.root.minsize(900, 600)
        
        # Configurar colores y estilo moderno
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'accent': '#F18F01',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'light': '#F8F9FA',
            'dark': '#343A40',
            'white': '#FFFFFF',
            'gray_light': '#E9ECEF',
            'gray_medium': '#6C757D'
        }
        
        self._configure_styles()
        
        # Variables de estado
        self.excel_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="🔄 Listo para iniciar")
        self.df = None
        self.department_vars = {}
        self.progress_var = tk.DoubleVar()

        self._create_widgets()

    def _configure_styles(self):
        """Configurar estilos modernos para ttk"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar frame principal
        self.style.configure('Main.TFrame', 
                           background=self.colors['light'],
                           relief='flat')
        
        # Configurar frames de sección
        self.style.configure('Section.TLabelframe',
                           background=self.colors['white'],
                           borderwidth=0,
                           relief='flat',
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('Section.TLabelframe.Label',
                           background=self.colors['white'],
                           foreground=self.colors['primary'],
                           font=('Segoe UI', 12, 'bold'))
        
        # Botones principales
        self.style.configure('Primary.TButton',
                           background=self.colors['primary'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8),
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Primary.TButton',
                      background=[('active', '#1e5f82'),
                                ('pressed', '#1a5170')])
        
        # Botones secundarios
        self.style.configure('Secondary.TButton',
                           background=self.colors['gray_light'],
                           foreground=self.colors['dark'],
                           font=('Segoe UI', 9),
                           padding=(10, 6),
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Secondary.TButton',
                      background=[('active', '#d6d8db'),
                                ('pressed', '#c5c7ca')])
        
        # Etiquetas de archivo
        self.style.configure('File.TLabel',
                           background=self.colors['gray_light'],
                           foreground=self.colors['dark'],
                           font=('Segoe UI', 9),
                           padding=8,
                           relief='flat',
                           borderwidth=1)
        
        # Checkboxes
        self.style.configure('Department.TCheckbutton',
                           background=self.colors['white'],
                           foreground=self.colors['dark'],
                           font=('Segoe UI', 9),
                           focuscolor='none')
        
        # Barra de estado
        self.style.configure('Status.TLabel',
                           background=self.colors['gray_light'],
                           foreground=self.colors['dark'],
                           font=('Segoe UI', 9),
                           padding=8,
                           relief='flat')

    def _create_widgets(self):
        """Crear la interfaz principal con diseño de dos columnas"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título principal
        title_frame = ttk.Frame(main_frame, style='Main.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame,
                              text="Reportes Mensuales de Asistencias",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['primary'],
                              bg=self.colors['light'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                 text="Reportes por departamento",
                                 font=('Segoe UI', 10),
                                 fg=self.colors['gray_medium'],
                                 bg=self.colors['light'])
        subtitle_label.pack(pady=(5, 0))
        
        # Container principal para las dos columnas
        columns_frame = ttk.Frame(main_frame, style='Main.TFrame')
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Configurar pesos de las columnas
        columns_frame.grid_columnconfigure(0, weight=0, minsize=350)  # Columna izquierda - tamaño fijo
        columns_frame.grid_columnconfigure(1, weight=1)  # Columna derecha - se expande
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # COLUMNA IZQUIERDA - Controles principales
        left_frame = ttk.Frame(columns_frame, style='Main.TFrame', padding=(0, 0, 10, 0))
        left_frame.grid(row=0, column=0, sticky='nsew')
        
        # COLUMNA DERECHA - Departamentos
        right_frame = ttk.Frame(columns_frame, style='Main.TFrame', padding=(10, 0, 0, 0))
        right_frame.grid(row=0, column=1, sticky='nsew')
        
        # Crear contenido de cada columna
        self._create_left_column_content(left_frame)
        self._create_right_column_content(right_frame)
        
        # Sección de acciones y estado (abajo, ocupando todo el ancho)
        self._create_action_section(main_frame)

    def _create_left_column_content(self, parent):
        """Crear contenido de la columna izquierda"""
        # Sección 1: Cargar archivo
        self._create_file_section(parent)
        
        # Sección 2: Carpeta de destino
        self._create_output_section(parent)
        
        # Espaciador para empujar el contenido hacia arriba
        spacer = ttk.Frame(parent, style='Main.TFrame')
        spacer.pack(fill=tk.BOTH, expand=True)

    def _create_right_column_content(self, parent):
        """Crear contenido de la columna derecha (departamentos)"""
        # Sección: Seleccionar departamentos (ocupa toda la columna derecha)
        self._create_departments_section(parent)

    def _create_file_section(self, parent):
        """Crear sección de carga de archivos"""
        file_frame = ttk.LabelFrame(parent, text="📁 Cargar Archivo de Marcajes", 
                                   style='Section.TLabelframe', padding=15)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Contenedor horizontal
        file_content = ttk.Frame(file_frame, style='Main.TFrame')
        file_content.pack(fill=tk.X)
        
        # Botón de selección
        file_button = ttk.Button(file_content, 
                                text="📂 Seleccionar Archivo",
                                command=self.load_file,
                                style='Secondary.TButton')
        file_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Campo de archivo seleccionado
        self.file_label = ttk.Label(file_content, 
                                   textvariable=self.excel_path,
                                   style='File.TLabel',
                                   width=35)  # Reducido para ajustarse a la columna
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        
        # Información de formatos soportados
        info_label = tk.Label(file_frame,
                             text="Formatos soportados: Excel (.xlsx, .xls)",
                             font=('Segoe UI', 8),
                             fg=self.colors['gray_medium'],
                             bg=self.colors['white'])
        info_label.pack(anchor=tk.W, pady=(8, 0))

    def _create_departments_section(self, parent):
        """Crear sección de selección de departamentos"""
        self.departments_main_frame = ttk.LabelFrame(parent, 
                                                    text="Seleccionar Departamentos",
                                                    style='Section.TLabelframe', 
                                                    padding=15)
        self.departments_main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        self.initial_dept_label = tk.Label(self.departments_main_frame,
                                          text="⬆️ Cargue un archivo para ver los departamentos disponibles",
                                          font=('Segoe UI', 10),
                                          fg=self.colors['gray_medium'],
                                          bg=self.colors['white'])
        self.initial_dept_label.pack(expand=True)

    def _create_output_section(self, parent):
        """Crear sección de carpeta de destino"""
        output_frame = ttk.LabelFrame(parent, text="📁 Seleccionar la Carpeta de Destino", 
                                     style='Section.TLabelframe', padding=15)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Contenedor horizontal
        output_content = ttk.Frame(output_frame, style='Main.TFrame')
        output_content.pack(fill=tk.X)
        
        # Botón de selección
        output_button = ttk.Button(output_content, 
                                  text="📂 Seleccionar Carpeta",
                                  command=self.select_output_folder,
                                  style='Secondary.TButton')
        output_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Campo de carpeta seleccionada
        self.output_label = ttk.Label(output_content, 
                                     textvariable=self.output_folder,
                                     style='File.TLabel',
                                     width=35)  # Reducido para ajustarse a la columna
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=False)

    def _create_action_section(self, parent):
        """Crear sección de acciones y estado"""
        action_frame = ttk.Frame(parent, style='Main.TFrame', padding=(0, 10))
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(action_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=300,
                                           mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.pack_forget()  # Ocultar inicialmente
        
        # Botón de generar reportes
        self.generate_button = ttk.Button(action_frame, 
                                         text="Generar Reportes", 
                                         command=self.run_generation_thread,
                                         style='Primary.TButton',
                                         state=tk.DISABLED)
        self.generate_button.pack(pady=(0, 15))
        
        # Barra de estado
        status_bar = ttk.Label(action_frame, 
                              textvariable=self.status_text,
                              style='Status.TLabel')
        status_bar.pack(fill=tk.X)

    def load_file(self):
        """Cargar y procesar archivo seleccionado"""
        filepath = filedialog.askopenfilename(
            title="Seleccione el archivo de marcajes",
            filetypes=(
                ("Archivos Excel", "*.xlsx;*.xls"),
                ("Archivos PDF", "*.pdf"),
                ("Todos los archivos", "*.*")
            )
        )
        if not filepath:
            return

        filename = os.path.basename(filepath)
        self.excel_path.set(f"📄 {filename}")
        self.status_text.set("🔄 Cargando y procesando archivo...")
        self.root.update_idletasks()
        
        try:
            self.df = etl_df(filepath)
            
            if self.df is not None and not self.df.empty:
                self.status_text.set("✅ Archivo cargado correctamente")
                self.populate_department_checkboxes()
            else:
                raise ValueError("El archivo no contiene datos válidos")
                
        except Exception as e:
            self.df = None
            self.excel_path.set("")
            self.status_text.set("❌ Error al cargar el archivo")
            messagebox.showerror("Error de Carga", 
                               f"No se pudo procesar el archivo:\n\n{str(e)}")
        
        self.update_generate_button_state()

    def populate_department_checkboxes(self):
        """Mostrar checkboxes de departamentos con diseño mejorado"""
        # Limpiar contenido anterior
        for widget in self.departments_main_frame.winfo_children():
            widget.destroy()
        
        self.department_vars = {}
        departments = sorted(self.df['departamento'].unique())
        
        if not departments:
            no_dept_label = tk.Label(self.departments_main_frame,
                                    text="⚠️ No se encontraron departamentos en el archivo",
                                    font=('Segoe UI', 10),
                                    fg=self.colors['warning'],
                                    bg=self.colors['white'])
            no_dept_label.pack(expand=True)
            return
        
        # Botones de selección masiva
        buttons_frame = ttk.Frame(self.departments_main_frame, style='Main.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        select_all_btn = ttk.Button(buttons_frame, 
                                   text="✅ Seleccionar Todos",
                                   command=self.select_all_depts,
                                   style='Secondary.TButton')
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        deselect_all_btn = ttk.Button(buttons_frame, 
                                     text="❌ Deseleccionar Todos",
                                     command=self.deselect_all_depts,
                                     style='Secondary.TButton')
        deselect_all_btn.pack(side=tk.LEFT)
        
        # Info de departamentos encontrados
        info_label = tk.Label(buttons_frame,
                             text=f" {len(departments)} departamentos encontrados",
                             font=('Segoe UI', 9),
                             fg=self.colors['primary'],
                             bg=self.colors['white'])
        info_label.pack(side=tk.RIGHT)
        
        # Frame scrollable para departamentos
        canvas_frame = ttk.Frame(self.departments_main_frame, style='Main.TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, 
                          background=self.colors['white'],
                          highlightthickness=0,
                          borderwidth=1,
                          relief='solid')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear checkboxes en menos columnas para la nueva disposición
        columns = 2  # Reducido de 3 a 2 para la columna más estrecha
        for i, dept in enumerate(departments):
            var = tk.BooleanVar(value=False)
            self.department_vars[dept] = var
            
            row = i // columns
            col = i % columns
            
            checkbox = ttk.Checkbutton(scrollable_frame, 
                                      text=f"{dept}",
                                      variable=var,
                                      style='Department.TCheckbutton')
            checkbox.grid(row=row, column=col, sticky='w', padx=10, pady=3)
            
            # Configurar peso de columnas
            scrollable_frame.grid_columnconfigure(col, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def select_all_depts(self):
        """Seleccionar todos los departamentos"""
        for var in self.department_vars.values():
            var.set(True)

    def deselect_all_depts(self):
        """Deseleccionar todos los departamentos"""
        for var in self.department_vars.values():
            var.set(False)

    def select_output_folder(self):
        """Seleccionar carpeta de destino"""
        folderpath = filedialog.askdirectory(title="Seleccione la carpeta de destino")
        if folderpath:
            self.output_folder.set(f"📁 {folderpath}")
            self.update_generate_button_state()

    def update_generate_button_state(self):
        """Actualizar estado del botón de generar"""
        if self.df is not None and self.output_folder.get():
            self.generate_button.config(state=tk.NORMAL)
        else:
            self.generate_button.config(state=tk.DISABLED)

    def run_generation_thread(self):
        """Ejecutar generación en hilo separado"""
        thread = Thread(target=self.generate_reports_logic, daemon=True)
        thread.start()

    def generate_reports_logic(self):
        """Lógica principal de generación de reportes con mejor UX"""
        selected_depts = [dept for dept, var in self.department_vars.items() if var.get()]
        
        if not selected_depts:
            messagebox.showwarning("Sin Selección", 
                                 "⚠️ Por favor, seleccione al menos un departamento.")
            return

        # Preparar UI para proceso
        self.generate_button.config(state=tk.DISABLED, text="🔄 Generando...")
        self.progress_bar.pack(pady=(0, 10))
        
        output_dir = self.output_folder.get().replace("📁 ", "")
        success_count = 0
        error_list = []
        total_reports = len(selected_depts)

        for i, dept in enumerate(selected_depts):
            try:
                # Actualizar progreso
                progress = (i / total_reports) * 100
                self.progress_var.set(progress)
                self.status_text.set(f"🔄 Generando reporte para '{dept}' ({i+1}/{total_reports})")
                self.root.update_idletasks()
                
                # Generar reporte
                df_dept = self.df[self.df['departamento'] == dept]
                generar_informe(df_dept, output_dir)
                success_count += 1

            except Exception as e:
                print(f"ERROR al generar para el departamento '{dept}': {e}")
                error_list.append(dept)
                continue

        # Completar progreso
        self.progress_var.set(100)
        self.root.update_idletasks()

        # Mostrar resultados
        if not error_list:
            self.status_text.set(f"✅ Reportes generados exitosamente")
            messagebox.showinfo("🎉 Proceso Completado", 
                              f"Se generaron reportes exitosamente.\n\n"
                              f"📁 Ubicación: {output_dir}")
        else:
            self.status_text.set(f"⚠️ {success_count} reportes generados, {len(error_list)} con errores")
            messagebox.showwarning("⚠️ Proceso Completado con Errores", 
                                 f"✅ Reportes generados: {success_count}\n"
                                 f"❌ Errores en: {len(error_list)} departamentos\n\n"
                                 f"Departamentos con error:\n• {chr(13).join(error_list)}\n\n"
                                 f"📁 Reportes exitosos guardados en: {output_dir}")

        # Restaurar UI
        self.generate_button.config(state=tk.NORMAL, text="Generar Reportes")
        self.progress_bar.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    
    # Configurar icono y estilo de ventana
    try:
        root.iconbitmap('assets\pulpo.ico')  # Puedes agregar un icono personalizado aquí
    except:
        pass
    
    # Centrar ventana en pantalla
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = ModernReportGeneratorApp(root)
    root.mainloop()