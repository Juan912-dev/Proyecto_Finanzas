#Aplicacion para gestionar las finanzas personales para registrar ingresos, gastos y presupuestos mensuales, categorizando cada movimiento para entender a donde va el dinero
import datetime as dt
import mysql.connector as mysql

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
        self.cursor.execute("SELECT tipo, categoria, cantidad, fecha FROM transacciones ORDER BY fecha DESC")
        movimientos = self.cursor.fetchall()

        print("\n--- Historial de Movimientos ---")
        if not movimientos:
            print("No hay movimientos registrados en la base de datos.")
        else:
            for tipo, categoria, cantidad, fecha in movimientos:
                print(f"  - {tipo.capitalize()}: ${cantidad} ({categoria}) el {fecha}")
        print("--------------------------------\n")


# Instanciamos la aplicación
app = GestorFinanzas()

while True:
    print("Bienvenido a la aplicación de gestión de finanzas personales")
    print("            Seleccione una opción:")
    print("             1. Ingresar dinero")
    print("             2. Gastar dinero")
    print("             3. Ver saldo y movimientos")
    print("             4. Salir")
    opcion = input("Ingrese el número de la opción deseada: ")

    if opcion == "1":
        try:
            cantidad = float(input("Ingrese la cantidad de dinero a ingresar: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue
        if cantidad <= 0:
            print("La cantidad debe ser mayor a cero. Intente nuevamente.")
            continue
        categoria = input("Ingrese la categoría del ingreso: ").capitalize()
        fecha_ingreso = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(app.registrar_movimiento("ingreso", categoria, cantidad, fecha_ingreso))
        print("Dinero ingresado correctamente.")

    elif opcion == "2":
        try:
            cantidad = float(input("Ingrese la cantidad de dinero a gastar: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue
        if cantidad <= 0:
            print("La cantidad debe ser mayor a cero. Intente nuevamente.")
            continue
        categoria = input("Ingrese la categoría del gasto: ").capitalize()
        fecha_gasto = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Validamos saldo leyendo directamente de la BD
        saldo_actual = app.obtener_saldo()
        if cantidad > saldo_actual:
            print(f"No tiene suficiente saldo. Saldo disponible: ${saldo_actual}")
            continue

        print(app.registrar_movimiento("gasto", categoria, cantidad, fecha_gasto))
        print("Dinero gastado correctamente.")

    elif opcion == "3":
        app.mostrar_resumen()
        app.mostrar_movimientos()

    elif opcion == "4":
        print("Gracias por usar la aplicación. ¡Hasta luego!")
        break
    else:
        print("Opción no válida. Por favor, intente nuevamente.")

