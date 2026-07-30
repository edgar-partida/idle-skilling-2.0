import os
import json


class MenuUtils:
    @staticmethod
    def limpiar_consola():
        # Opcional: limpiar pantalla si lo deseas
        print("\n" * 2)

    @staticmethod
    def mostrar_menu_principal():
        print("\n================== MENÚ PRINCIPAL ==================")
        print("1. Configurar / Capturar nuevas coordenadas (Shift + Clic)")
        print("2. Crear nueva rutina personalizada")
        print("3. Ejecutar rutina Secuencial guardada")
        print("4. Ejecutar rutina Paralela guardada")
        print("0. Salir")
        print("====================================================")

    @staticmethod
    def obtener_opcion() -> str:
        return input("Selecciona una opción: ").strip()

    @staticmethod
    def listar_y_seleccionar(ruta_archivo: str, tipo_nombre: str) -> str:
        if not os.path.exists(ruta_archivo):
            print(f"❌ No hay archivo de rutinas {tipo_nombre}s.")
            return None

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                rutinas = json.load(f)
        except:
            rutinas = {}

        if not rutinas:
            print(f"❌ No hay rutinas {tipo_nombre}s guardadas.")
            return None

        print(f"\n--- SELECCIONA UNA RUTINA {tipo_nombre.upper()} ---")
        nombres = list(rutinas.keys())
        for idx, nombre in enumerate(nombres, 1):
            print(f"{idx}. {nombre}")

        seleccion = input(
            "\nIngresa el número de la rutina a ejecutar (o presiona ENTER para cancelar): ").strip()
        return seleccion if seleccion else None
