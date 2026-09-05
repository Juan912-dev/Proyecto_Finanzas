#Aplicacion para gestionar las finanzas personales para registrar ingresos, gastos y presupuestos mensuales, categorizando cada movimiento para entender a donde va el dinero
import datetime as dt
import mysql.connector as mysql
import customtkinter as ctk
from tkinter import ttk

class GestorFinanzas:
    def __init__(self):
        self.ingresos = 0
        self.gastos = 0
        self.movimientos = []
        self.db = mysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Juancitoprogamer1999.creandounabasededatosbig2026",
            database="finanzas_personales"
        )
        self.cursor = self.db.cursor()


    def registrar_movimiento(self, tipo, categoria, cantidad, fecha):
        # Guardamos en MySQL usando SQL parametrizado por seguridad (%s)
        sql = "INSERT INTO transacciones (tipo, categoria, cantidad, fecha) VALUES (%s, %s, %s, %s)"
        valores = (tipo, categoria, cantidad, fecha)
        self.cursor.execute(sql, valores)
        self.db.commit() # Confirma la transacción en la base de datos
        return f"Movimiento registrado en BD: {tipo.capitalize()} de ${cantidad} ({categoria}) el {fecha}"

    def obtener_saldo(self):
        # MySQL calcula la diferencia directamente entre los ingresos y los gastos
        self.cursor.execute("SELECT IFNULL(SUM(cantidad), 0) FROM transacciones WHERE tipo = 'ingreso'")
        total_ingresos = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT IFNULL(SUM(cantidad), 0) FROM transacciones WHERE tipo = 'gasto'")
        total_gastos = self.cursor.fetchone()[0]

        return total_ingresos - total_gastos

    def mostrar_resumen(self):
        self.cursor.execute("SELECT IFNULL(SUM(cantidad), 0) FROM transacciones WHERE tipo = 'ingreso'")
        total_ingresos = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT IFNULL(SUM(cantidad), 0) FROM transacciones WHERE tipo = 'gasto'")
        total_gastos = self.cursor.fetchone()[0]

        print(f"\n--- Resumen Financiero ---")
        print(f"Total Ingresos: ${total_ingresos}")
        print(f"Total Gastos: ${total_gastos}")
        print(f"Saldo actual: ${total_ingresos - total_gastos}")
        print("--------------------------\n")

    def mostrar_movimientos(self):
        # Leemos todos los registros guardados en la tabla
        self.cursor.execute("SELECT id, tipo, categoria, cantidad, fecha FROM transacciones ORDER BY fecha DESC")
        movimientos = self.cursor.fetchall()

        print("\n--- Historial de Movimientos ---")
        if not movimientos:
            print("No hay movimientos registrados en la base de datos.")
        else:
            for id_tx, tipo, categoria, cantidad, fecha in movimientos:
                print(f"[{id_tx}]  - {tipo.capitalize()}: ${cantidad} ({categoria}) el {fecha}")
        print("--------------------------------\n")

    def modificar_movimiento(self, id_movimiento, nuevo_tipo, nueva_categoria, nueva_cantidad):
        sql= "UPDATE transacciones SET tipo = %s, categoria = %s, cantidad = %s WHERE id = %s"
        valores = (nuevo_tipo, nueva_categoria, nueva_cantidad, id_movimiento)
        self.cursor.execute(sql, valores)
        self.db.commit()

        if self.cursor.rowcount > 0:
            return f"Movimiento con ID {id_movimiento} modificado correctamente."
        else:
            return f"No se encontró un movimiento con ID {id_movimiento}."

    def eliminar_movimiento(self, id_movimiento):
        sql = "DELETE FROM transacciones WHERE id = %s"
        self.cursor.execute(sql, (id_movimiento,))
        self.db.commit()


ctk.set_appearance_mode("Dark") # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # Opciones: "blue", "green", "dark-blue"

class AplicacionGUI(ctk.CTk):
    def __init__(self, gestor_bd):
        super().__init__()
        self.gestor = gestor_bd
        
        self.title("Gestor de Finanzas Personales")
        self.geometry("850x500")
        
        # Dividir la ventana: Columna 0 (Menú estrecho) | Columna 1 (Datos ancha)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # PANEL LATERAL (Botones)
        # ==========================================
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        
        self.label_titulo = ctk.CTkLabel(self.frame_menu, text="Menú", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.btn_ingreso = ctk.CTkButton(self.frame_menu, text="Ingresar Dinero", command=self.simular_ingreso)
        self.btn_ingreso.grid(row=1, column=0, padx=20, pady=10)

        self.btn_gasto = ctk.CTkButton(self.frame_menu, text="Registrar Gasto", fg_color="#C0392B", hover_color="#922B21", command=self.simular_gasto)
        self.btn_gasto.grid(row=2, column=0, padx=20, pady=10)

        # Botones de Modificar y Eliminar
        self.btn_modificar = ctk.CTkButton(self.frame_menu, text="Modificar Selección", fg_color="#F39C12", hover_color="#D68910", command=self.modificar_seleccion)
        self.btn_modificar.grid(row=3, column=0, padx=20, pady=10)

        self.btn_eliminar = ctk.CTkButton(self.frame_menu, text="Eliminar Selección", fg_color="#8E44AD", hover_color="#732D91", command=self.eliminar_seleccion)
        self.btn_eliminar.grid(row=4, column=0, padx=20, pady=10)

        # ==========================================
        # PANEL PRINCIPAL (Saldo y Tabla)
        # ==========================================
        self.frame_datos = ctk.CTkFrame(self)
        self.frame_datos.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_datos.grid_rowconfigure(1, weight=1) # La tabla ocupará el espacio sobrante

        # Etiqueta de Saldo
        self.label_saldo = ctk.CTkLabel(self.frame_datos, text="Saldo Actual: $0", font=ctk.CTkFont(size=28, weight="bold"))
        self.label_saldo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Tabla (Treeview)
        columnas = ("ID", "Tipo", "Categoría", "Cantidad", "Fecha")
        self.tabla = ttk.Treeview(self.frame_datos, columns=columnas, show="headings")
        
        # Configurar encabezados y anchos de columna
        anchos = {"ID": 50, "Tipo": 80, "Categoría": 120, "Cantidad": 100, "Fecha": 150}
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos[col], anchor="center")
            
        self.tabla.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Cargar los datos desde MySQL al iniciar
        self.actualizar_pantalla()

    # ==========================================
    # FUNCIONES DE LA INTERFAZ
    # ==========================================
    def actualizar_pantalla(self):
        # 1. Actualizar el texto del saldo
        saldo = self.gestor.obtener_saldo()
        self.label_saldo.configure(text=f"Saldo Actual: ${saldo}")

        # 2. Limpiar la tabla actual
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        
        # 3. Traer datos de MySQL y llenar la tabla
        self.gestor.cursor.execute("SELECT id, tipo, categoria, cantidad, fecha FROM transacciones ORDER BY fecha DESC")
        movimientos = self.gestor.cursor.fetchall()
        
        for mov in movimientos:
            # Reemplaza valores None por "Sin categoría" para la vista
            mov_formateado = (mov[0], mov[1].capitalize(), mov[2] if mov[2] else "-", f"${mov[3]}", mov[4])
            self.tabla.insert("", "end", values=mov_formateado)

    def simular_ingreso(self):
        # 1. Crear la ventana emergente
        ventana_ingreso = ctk.CTkToplevel(self)
        ventana_ingreso.title("Registrar Ingreso")
        ventana_ingreso.geometry("350x350")
        ventana_ingreso.attributes("-topmost", True) # Mantiene la ventana al frente
        
        # 2. Elementos de la interfaz (Campos de texto)
        titulo = ctk.CTkLabel(ventana_ingreso, text="Nuevo Ingreso", font=ctk.CTkFont(size=20, weight="bold"))
        titulo.pack(pady=(20, 10))

        label_categoria = ctk.CTkLabel(ventana_ingreso, text="Categoría (ej. Sueldo, Venta):")
        label_categoria.pack(pady=(10, 0))
        entrada_categoria = ctk.CTkEntry(ventana_ingreso, width=250)
        entrada_categoria.pack(pady=5)

        label_cantidad = ctk.CTkLabel(ventana_ingreso, text="Monto ($):")
        label_cantidad.pack(pady=(10, 0))
        entrada_cantidad = ctk.CTkEntry(ventana_ingreso, width=250)
        entrada_cantidad.pack(pady=5)
        
        # Etiqueta oculta para mostrar errores de validación
        label_error = ctk.CTkLabel(ventana_ingreso, text="", text_color="red")
        label_error.pack(pady=5)

        # 3. Función interna para procesar el guardado
        def guardar_ingreso():
            categoria = entrada_categoria.get().strip()
            
            if not categoria:
                label_error.configure(text="La categoría no puede estar vacía.")
                return

            try:
                # Validamos que sea un número positivo
                cantidad = float(entrada_cantidad.get())
                if cantidad <= 0:
                    label_error.configure(text="El monto debe ser mayor a 0.")
                    return
                
                # Si todo está bien, generamos fecha y enviamos a MySQL
                import datetime as dt
                fecha = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.gestor.registrar_movimiento("ingreso", categoria, cantidad, fecha)
                
                # Refrescamos la pantalla principal y cerramos la ventana
                self.actualizar_pantalla()
                ventana_ingreso.destroy()

            except ValueError:
                label_error.configure(text="Error: Ingrese solo números válidos.")

        # 4. Botón de confirmación
        btn_guardar = ctk.CTkButton(ventana_ingreso, text="Guardar Ingreso", command=guardar_ingreso)
        btn_guardar.pack(pady=15)

    def simular_gasto(self):
        ventana_gasto = ctk.CTkToplevel(self)
        ventana_gasto.title("Registrar Gasto")
        ventana_gasto.geometry("350x350")
        ventana_gasto.attributes("-topmost", True) # Mantiene la ventana al frente

        titulo = ctk.CTkLabel(ventana_gasto, text="Nuevo Gasto", font=ctk.CTkFont(size=20, weight="bold"))
        titulo.pack(pady=(20, 10))

        label_categoria = ctk.CTkLabel(ventana_gasto, text="Categoría (ej. Comida, Transporte):")
        label_categoria.pack(pady=(10, 0))
        entrada_categoria = ctk.CTkEntry(ventana_gasto, width=250)
        entrada_categoria.pack(pady=5)

        label_cantidad = ctk.CTkLabel(ventana_gasto, text="Monto ($):")
        label_cantidad.pack(pady=(10, 0))
        entrada_cantidad = ctk.CTkEntry(ventana_gasto, width=250)
        entrada_cantidad.pack(pady=5)

        label_error = ctk.CTkLabel(ventana_gasto, text="", text_color="red")
        label_error.pack(pady=5)

        def guardar_gasto():
            categoria = entrada_categoria.get().strip().capitalize()
            
            if not categoria:
                label_error.configure(text="La categoría no puede estar vacía.")
                return

            try:
                cantidad = float(entrada_cantidad.get())
                if cantidad <= 0:
                    label_error.configure(text="El monto debe ser mayor a 0.")
                    return

                if cantidad > self.gestor.obtener_saldo():
                    label_error.configure(text="Error: No hay suficiente saldo para este gasto.")
                    return
                
                fecha = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.gestor.registrar_movimiento("gasto", categoria, cantidad, fecha)
                
                self.actualizar_pantalla()
                ventana_gasto.destroy()

            except ValueError:
                label_error.configure(text="Error: Ingrese solo números válidos.")

        boton_guardar = ctk.CTkButton(ventana_gasto, text="Guardar Gasto", command=guardar_gasto)
        boton_guardar.pack(pady=15)

    def eliminar_seleccion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            print("Selecciona un movimiento de la tabla primero.")
            return
        
        # Obtenemos los datos de la fila seleccionada (el ID está en la posición 0)
        valores_fila = self.tabla.item(seleccion[0])['values']
        id_movimiento = valores_fila[0]
        
        # Eliminamos de la base de datos y refrescamos
        self.gestor.eliminar_movimiento(id_movimiento)
        self.actualizar_pantalla()

    def modificar_seleccion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            print("Selecciona un movimiento de la tabla primero.")
            return

        # Extraemos los datos actuales
        valores_fila = self.tabla.item(seleccion[0])['values']
        id_mov = valores_fila[0]
        tipo_actual = valores_fila[1].lower() # Lo pasamos a minúscula para que coincida ("ingreso" o "gasto")
        cat_actual = valores_fila[2]
        cant_actual = str(valores_fila[3]).replace("$", "")

        ventana_mod = ctk.CTkToplevel(self)
        ventana_mod.title("Modificar Movimiento")
        ventana_mod.geometry("350x420") # Hicimos la ventana un poco más alta
        ventana_mod.attributes("-topmost", True)

        ctk.CTkLabel(ventana_mod, text=f"Modificando ID: {id_mov}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))

        # --- NUEVO: Menú desplegable para el Tipo ---
        ctk.CTkLabel(ventana_mod, text="Tipo de Movimiento:").pack(pady=(5, 0))
        opcion_tipo = ctk.CTkOptionMenu(ventana_mod, values=["ingreso", "gasto"])
        opcion_tipo.set(tipo_actual) # Deja seleccionado el tipo que ya tenía
        opcion_tipo.pack(pady=5)
        # --------------------------------------------

        ctk.CTkLabel(ventana_mod, text="Nueva Categoría:").pack(pady=(10, 0))
        entrada_categoria = ctk.CTkEntry(ventana_mod, width=250)
        entrada_categoria.insert(0, cat_actual)
        entrada_categoria.pack(pady=5)

        ctk.CTkLabel(ventana_mod, text="Nuevo Monto ($):").pack(pady=(10, 0))
        entrada_cantidad = ctk.CTkEntry(ventana_mod, width=250)
        entrada_cantidad.insert(0, cant_actual)
        entrada_cantidad.pack(pady=5)

        label_error = ctk.CTkLabel(ventana_mod, text="", text_color="red")
        label_error.pack(pady=5)

        def guardar_cambios():
            # Capturamos también el valor del menú desplegable
            nuevo_tipo = opcion_tipo.get()
            nueva_cat = entrada_categoria.get().strip().capitalize()
            
            if not nueva_cat:
                label_error.configure(text="La categoría no puede estar vacía.")
                return

            try:
                nueva_cant = float(entrada_cantidad.get())
                if nueva_cant <= 0:
                    label_error.configure(text="El monto debe ser mayor a 0.")
                    return
                
                # Ahora sí enviamos los 4 parámetros que espera la base de datos
                self.gestor.modificar_movimiento(id_mov, nuevo_tipo, nueva_cat, nueva_cant)
                
                self.actualizar_pantalla()
                ventana_mod.destroy()

            except ValueError:
                label_error.configure(text="Error: Ingrese solo números válidos.")

        ctk.CTkButton(ventana_mod, text="Guardar Cambios", command=guardar_cambios).pack(pady=15)

backend_db = GestorFinanzas()

# Arrancamos la interfaz gráfica conectada al backend
ventana = AplicacionGUI(backend_db)
ventana.mainloop()
