import sys
from utils.logger_utils import configurar_logger
from utils.screen_finder import traer_ventana_al_frente
from utils.coordinate_utils import CoordinateManager
from utils.routine_utils import RoutineManager
from utils.menu_utils import MenuUtils
from utils.logger_utils import configurar_logger

logger = configurar_logger()


class IdleSkillingApp:
    def __init__(self, titulo_objetivo: str = "Idle Skilling"):
        self.titulo_objetivo = titulo_objetivo
        self.coord_manager = CoordinateManager()
        self.routine_manager = RoutineManager(titulo_objetivo=titulo_objetivo)

    def iniciar(self) -> None:
        logger.info("==================================================")
        logger.info("         INICIANDO GAME MACROS - IDLE SKILLING    ")
        logger.info("==================================================")

        if not traer_ventana_al_frente(self.titulo_objetivo):
            logger.error(
                "No es posible continuar la ejecución porque la ventana no está disponible.")
            sys.exit(1)

        logger.info("Validación exitosa. Entrando al menú principal...")
        self._ejecutar_ciclo_menu()

    def _ejecutar_ciclo_menu(self) -> None:
        while True:
            MenuUtils.mostrar_menu_principal()
            opcion = MenuUtils.obtener_opcion()

            if opcion == "1":
                self.coord_manager.iniciar_captura()
                input(
                    "Presiona [ENTER] en esta terminal cuando desees dejar de capturar...\n")
                self.coord_manager.detener_captura()

            elif opcion == "2":
                self.routine_manager.crear_rutina_interactiva()

            elif opcion == "3":
                num = MenuUtils.listar_y_seleccionar(
                    self.routine_manager.seq_routines_file, "secuencial")
                if num:
                    self.routine_manager.ejecutar_rutina_por_indice(
                        "secuencial", num)

            elif opcion == "4":
                num = MenuUtils.listar_y_seleccionar(
                    self.routine_manager.par_routines_file, "paralela")
                if num:
                    self.routine_manager.ejecutar_rutina_por_indice(
                        "paralela", num)

            elif opcion == "0":
                self.coord_manager.detener_captura()
                logger.info("Saliendo de la aplicación. ¡Hasta luego!")
                break
            else:
                logger.warning("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    app = IdleSkillingApp()
    app.iniciar()
