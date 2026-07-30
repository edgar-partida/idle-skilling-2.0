import os
import json
from utils.logger_utils import configurar_logger

logger = configurar_logger()


class MenuUtils:
    @staticmethod
    def limpiar_consola():
        # Opcional: limpiar pantalla si lo deseas
        logger.info("\n" * 2)

    @staticmethod
    def mostrar_menu_principal():
        logger.info("\n================== MENÚ PRINCIPAL ==================")
        logger.info(
            "1. Configurar / Capturar nuevas coordenadas (Shift + Clic)")
        logger.info("2. Crear nueva rutina personalizada")
        logger.info("3. Ejecutar rutina Secuencial guardada")
        logger.info("4. Ejecutar rutina Paralela guardada")
        logger.info("0. Salir")
        logger.info("====================================================")

    @staticmethod
    def obtener_opcion() -> str:
        return input("Selecciona una opción: ").strip()

    @staticmethod
    def listar_y_seleccionar(ruta_archivo: str, tipo_nombre: str) -> str:
        if not os.path.exists(ruta_archivo):
            logger.error(f"No hay archivo de rutinas {tipo_nombre}s.")
            return None

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                rutinas = json.load(f)
        except:
            rutinas = {}

        if not rutinas:
            logger.error(f"No hay rutinas {tipo_nombre}s guardadas.")
            return None

        logger.info(f"--- SELECCIONA UNA RUTINA {tipo_nombre.upper()} ---")
        nombres = list(rutinas.keys())
        for idx, nombre in enumerate(nombres, 1):
            logger.info(f"{idx}. {nombre}")

        seleccion = input(
            "\nIngresa el número de la rutina a ejecutar (o presiona ENTER para cancelar): ").strip()
        return seleccion if seleccion else None
