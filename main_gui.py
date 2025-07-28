# main_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from threading import Thread

# --- ¡AQUÍ ESTÁ EL CAMBIO CLAVE! ---
# Importamos desde las ubicaciones que definimos
from utils.data import etl_df
from reportgen.generador import generar_informe

class ReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes Corporativos")
        self.root.geometry("600x600")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', padding=6, relief="flat", background="#e1e1e1", font=('Helvetica', 10))
        self.style.configure('TLabel', background="#f0f0f0", font=('Helvetica', 10))
        self.style.configure('TFrame', background="#f0f0f0")
        self.style.configure('TLabelframe', background="#f0f0f0", font=('Helvetica', 11, 'bold'))
        self.style.configure('TCheckbutton', background="#f0f0f0", font=('Helvetica', 10))

        self.excel_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="Listo para iniciar.")
        self.df = None
        self.department_vars = {}

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        load_frame = ttk.LabelFrame(main_frame, text="Paso 1: Cargar Archivo de Marcajes", padding="10")
        load_frame.pack(fill=tk.X, pady=5)
        load_button = ttk.Button(load_frame, text="Seleccionar Archivo (Excel/PDF)", command=self.load_file)
        load_button.pack(side=tk.LEFT, padx=(0, 10))
        load_label = ttk.Label(load_frame, textvariable=self.excel_path, relief="sunken", padding=5, width=50)
        load_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.departments_frame_container = ttk.LabelFrame(main_frame, text="Paso 2: Seleccionar Departamentos", padding="10")
        self.departments_frame_container.pack(fill=tk.BOTH, pady=10, expand=True)
        self.dept_buttons_frame = ttk.Frame(self.departments_frame_container)
        self.canvas = tk.Canvas(self.departments_frame_container, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.departments_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        initial_dept_label = ttk.Label(self.departments_frame_container, text="Cargue un archivo para ver los departamentos.")
        initial_dept_label.pack(pady=20)
        
        output_frame = ttk.LabelFrame(main_frame, text="Paso 3: Seleccionar Carpeta de Destino", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        output_button = ttk.Button(output_frame, text="Seleccionar Carpeta", command=self.select_output_folder)
        output_button.pack(side=tk.LEFT, padx=(0, 10))
        output_label = ttk.Label(output_frame, textvariable=self.output_folder, relief="sunken", padding=5, width=50)
        output_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.generate_button = ttk.Button(action_frame, text="Generar Reportes", command=self.run_generation_thread, state=tk.DISABLED)
        self.generate_button.pack(pady=10)
        status_bar = ttk.Label(action_frame, textvariable=self.status_text, relief=tk.RIDGE, anchor=tk.W, padding=5)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccione el archivo de marcajes",
            filetypes=(("Archivos Soportados", "*.xlsx;*.xls;*.pdf"), ("Todos los archivos", "*.*"))
        )
        if not filepath: return

        self.excel_path.set(os.path.basename(filepath))
        self.status_text.set("Cargando y procesando archivo...")
        self.root.update_idletasks()
        
        try:
            # LLAMADA A LA FUNCIÓN CORRECTA DE utils/data.py
            self.df = etl_df(filepath)
            
            if self.df is not None and not self.df.empty:
                self.status_text.set("Archivo cargado. Seleccione departamentos.")
                self.populate_department_checkboxes()
            else:
                raise ValueError("El archivo no contiene datos o el formato es incorrecto.")
        except Exception as e:
            self.df = None
            self.status_text.set("Error al cargar el archivo.")
            messagebox.showerror("Error de Carga", f"No se pudo cargar o procesar el archivo.\n\nError: {e}")
        
        self.update_generate_button_state()


    def generate_reports_logic(self):
        selected_depts = [dept for dept, var in self.department_vars.items() if var.get()]
        if not selected_depts:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione al menos un departamento.")
            return

        self.generate_button.config(state=tk.DISABLED)
        output_dir = self.output_folder.get()
        
        # --- BUCLE CORREGIDO ---
        success_count = 0
        error_list = []
        total_reports = len(selected_depts)

        for i, dept in enumerate(selected_depts):
            # Movemos el try...except DENTRO del bucle
            try:
                self.status_text.set(f"Generando reporte para '{dept}' ({i+1}/{total_reports})...")
                df_dept = self.df[self.df['departamento'] == dept]
                
                generar_informe(df_dept, output_dir)
                success_count += 1

            except Exception as e:
                # Si falla, añadimos el departamento a una lista de errores y continuamos
                print(f"ERROR al generar para el departamento '{dept}': {e}")
                error_list.append(dept)
                continue # <-- ¡Importante! Pasa al siguiente departamento

        # --- FIN DEL BUCLE CORREGIDO ---

        # Mostramos un resumen final
        self.status_text.set("Proceso completado.")
        if not error_list:
            messagebox.showinfo("Proceso Terminado", f"Se generaron {success_count} reportes con éxito en:\n\n{output_dir}")
        else:
            messagebox.showwarning("Proceso Terminado con Errores", 
                                f"Se generaron {success_count} reportes con éxito.\n\n"
                                f"No se pudieron generar reportes para los siguientes departamentos:\n"
                                f"- {', '.join(error_list)}\n\n"
                                f"Por favor, revisa los datos de esos departamentos.")

        self.generate_button.config(state=tk.NORMAL)

    def populate_department_checkboxes(self):
        for widget in self.departments_frame_container.winfo_children(): widget.pack_forget()
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.department_vars = {}
        departments = sorted(self.df['departamento'].unique())
        if not departments:
            ttk.Label(self.departments_frame_container, text="No se encontraron departamentos.").pack()
            return
        self.dept_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(self.dept_buttons_frame, text="Seleccionar Todos", command=self.select_all_depts).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.dept_buttons_frame, text="Deseleccionar Todos", command=self.deselect_all_depts).pack(side=tk.LEFT, padx=5)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for dept in departments:
            var = tk.BooleanVar(value=False)
            self.department_vars[dept] = var
            ttk.Checkbutton(self.scrollable_frame, text=dept, variable=var).pack(anchor=tk.NW, pady=2, padx=10)

    def select_all_depts(self):
        for var in self.department_vars.values(): var.set(True)

    def deselect_all_depts(self):
        for var in self.department_vars.values(): var.set(False)

    def select_output_folder(self):
        folderpath = filedialog.askdirectory(title="Seleccione la carpeta de destino")
        if folderpath:
            self.output_folder.set(folderpath)
            self.update_generate_button_state()

    def update_generate_button_state(self):
        if self.df is not None and self.output_folder.get(): self.generate_button.config(state=tk.NORMAL)
        else: self.generate_button.config(state=tk.DISABLED)

    def run_generation_thread(self):
        thread = Thread(target=self.generate_reports_logic)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()