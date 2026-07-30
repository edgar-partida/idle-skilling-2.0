import os
import json
import time
import threading
import keyboard
import pygetwindow as gw
import win32gui
import win32con
from utils.logger_utils import configurar_logger
from utils.screen_finder import traer_ventana_al_frente

logger = configurar_logger()


class RoutineManager:
    def __init__(self, titulo_objetivo: str, resources_dir: str = "resources"):
        self.titulo_objetivo = titulo_objetivo
        self.resources_dir = resources_dir
        self.coords_file = os.path.join(resources_dir, "relative-coords.json")
        self.seq_routines_file = os.path.join(
            resources_dir, "routines-sequential.json")
        self.par_routines_file = os.path.join(
            resources_dir, "routines-parallel.json")

        self.puntos_configurados = {}
        self.detenido = False
        self._cargar_recursos()

    def _cargar_recursos(self):
        if os.path.exists(self.coords_file):
            try:
                with open(self.coords_file, "r", encoding="utf-8") as f:
                    self.puntos_configurados = json.load(f)
            except Exception as e:
                logger.warning(f"Error al cargar coordenadas: {e}")

    def _cargar_json(self, ruta):
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _guardar_json(self, ruta, datos):
        if not os.path.exists(self.resources_dir):
            os.makedirs(self.resources_dir)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def crear_rutina_interactiva(self):
        logger.info("==================================================")
        logger.info("           CREADOR DE RUTINAS NUEVAS")
        logger.info("==================================================")

        if not self.puntos_configurados:
            logger.error(
                "No hay acciones configuradas en 'relative-coords.json'. Configura coordenadas primero.")
            return

        logger.info("Acciones disponibles que puedes usar:")
        for nombre in self.puntos_configurados.keys():
            logger.info(f" -> {nombre}")

        tipo = input("\n¿Qué tipo de rutina deseas crear?\n1. Secuencial (Paso a paso con delays)\n2. Paralela (Por intervalos de milisegundos)\nElige opción (1 o 2): ").strip()

        nombre_rutina = input(
            "Asigna un nombre único para esta rutina: ").strip()
        if not nombre_rutina:
            logger.warning("El nombre no puede estar vacío.")
            return

        if tipo == "1":
            pasos = []
            logger.info("--- Armando Secuencia ---")
            logger.info(
                "Escribe la acción o 'DELAY'. Escribe 'fin' cuando termines.")

            while True:
                accion = input("Paso (Acción o DELAY / fin): ").strip().upper()
                if accion == "FIN":
                    break
                if accion == "DELAY":
                    try:
                        ms = int(
                            input("  -> Duración del delay en milisegundos (ej: 500): "))
                        pasos.append(["DELAY", ms])
                    except ValueError:
                        logger.warning("Valor inválido.")
                elif accion in self.puntos_configurados:
                    pasos.append([accion, 0])
                    logger.info(f"  -> Añadido: {accion}")
                else:
                    logger.warning("Acción no reconocida.")

            if pasos:
                rutinas = self._cargar_json(self.seq_routines_file)
                rutinas[nombre_rutina] = pasos
                self._guardar_json(self.seq_routines_file, rutinas)
                logger.info(
                    f"¡Rutina secuencial '{nombre_rutina}' guardada exitosamente!")
            else:
                logger.warning("Rutina vacía, no se guardó.")

        elif tipo == "2":
            acciones_intervalos = {}
            logger.info("--- Armando Rutina Paralela ---")
            logger.info(
                "Escribe la acción y su intervalo en milisegundos. Escribe 'fin' para terminar.")

            while True:
                accion = input("Acción a repetir (o fin): ").strip().upper()
                if accion == "FIN":
                    break
                if accion in self.puntos_configurados:
                    try:
                        ms = int(
                            input(f"  -> ¿Cada cuántos milisegundos '{accion}'? (ej: 5000): "))
                        acciones_intervalos[accion] = ms
                        logger.info(f"  -> Configurado: {accion} cada {ms}ms")
                    except ValueError:
                        logger.warning("Debe ser un número válido.")
                else:
                    logger.warning("Acción no encontrada.")

            if acciones_intervalos:
                rutinas = self._cargar_json(self.par_routines_file)
                rutinas[nombre_rutina] = acciones_intervalos
                self._guardar_json(self.par_routines_file, rutinas)
                logger.info(
                    f"¡Rutina paralela '{nombre_rutina}' guardada exitosamente!")
            else:
                logger.warning("Rutina vacía, no se guardó.")

    def _obtener_render_hwnd(self, hwnd_padre):
        """Busca internamente la ventana hija de renderizado de Chromium/Electron."""
        render_hwnds = []

        def callback(hwnd, _):
            if win32gui.GetClassName(hwnd) == "Chrome_RenderWidgetHostHWND":
                render_hwnds.append(hwnd)
            return True

        win32gui.EnumChildWindows(hwnd_padre, callback, None)
        return render_hwnds[0] if render_hwnds else hwnd_padre

    def _hacer_clic(self, nombre_accion: str):
        if nombre_accion not in self.puntos_configurados:
            return

        data = self.puntos_configurados[nombre_accion]
        titulo_ventana = data['ventana_ref']

        # Búsqueda estricta (EQUALS) en lugar de parcial (CONTAINS)
        ventanas_candidatas = gw.getWindowsWithTitle(titulo_ventana)
        win = None
        for w in ventanas_candidatas:
            if w.title == titulo_ventana:
                win = w
                break

        if not win:
            logger.warning(
                f"No se encontró una ventana con el título exacto: '{titulo_ventana}'")
            return

        hwnd_padre = win._hWnd

        try:
            hwnd_render = self._obtener_render_hwnd(hwnd_padre)

            client_rect = win32gui.GetClientRect(hwnd_padre)
            ancho_cliente = client_rect[2]
            alto_cliente = client_rect[3]

            if ancho_cliente <= 0 or alto_cliente <= 0:
                ancho_cliente = win.width
                alto_cliente = win.height

            x_interna = int(data['porcentaje_x'] * ancho_cliente)
            y_interna = int(data['porcentaje_y'] * alto_cliente)

            l_param = (y_interna << 16) | (x_interna & 0xFFFF)

            win32gui.PostMessage(
                hwnd_render, win32con.WM_MOUSEMOVE, 0, l_param)
            win32gui.PostMessage(
                hwnd_render, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
            time.sleep(0.03)
            win32gui.PostMessage(
                hwnd_render, win32con.WM_LBUTTONUP, 0, l_param)

            logger.info(
                f"PostMessage en segundo plano [{nombre_accion}] -> X={x_interna}, Y={y_interna}")

        except Exception as e:
            logger.warning(
                f"Error al enviar PostMessage en '{nombre_accion}': {e}")

    def _escuchar_escape(self):
        """Monitorea de forma segura la tecla ESC sin bloquear instantáneamente."""
        while not self.detenido:
            if keyboard.is_pressed('esc'):
                self.detenido = True
                logger.info("Detenido por el usuario (ESC)!")
                break
            time.sleep(0.1)

    def ejecutar_rutina_por_indice(self, tipo: str, indice_str: str):
        ruta_archivo = self.seq_routines_file if tipo == "secuencial" else self.par_routines_file
        rutinas = self._cargar_json(ruta_archivo)

        if not rutinas:
            logger.error(f"No hay rutinas {tipo}s guardadas.")
            return

        nombres_rutinas = list(rutinas.keys())

        try:
            indice = int(indice_str) - 1
            if indice < 0 or indice >= len(nombres_rutinas):
                logger.error("Número de rutina fuera de rango.")
                return
        except ValueError:
            logger.error("Debes ingresar un número válido.")
            return

        nombre_seleccionado = nombres_rutinas[indice]

        # 1. Traer la ventana al frente obligatoriamente antes de ejecutar
        logger.info(f"Preparando ejecución de '{nombre_seleccionado}'...")
        if not traer_ventana_al_frente(self.titulo_objetivo):
            logger.error(
                "No se pudo enfocar la ventana del juego. Cancelando ejecución.")
            return

        self.detenido = False
        hilo_esc = threading.Thread(target=self._escuchar_escape, daemon=True)
        hilo_esc.start()

        if tipo == "secuencial":
            pasos = rutinas[nombre_seleccionado]
            logger.info(
                f"Ejecutando SECUENCIAL: '{nombre_seleccionado}'. Presiona [ESC] para salir.")

            while not self.detenido:
                for tipo_accion, valor in pasos:
                    if self.detenido:
                        break
                    if tipo_accion == "DELAY":
                        t_trans = 0
                        while t_trans < (valor / 1000.0) and not self.detenido:
                            time.sleep(0.05)
                            t_trans += 0.05
                    else:
                        self._hacer_clic(tipo_accion)

        elif tipo == "paralela":
            acciones_intervalos = rutinas[nombre_seleccionado]
            logger.info(
                f"Ejecutando PARALELA: '{nombre_seleccionado}'. Presiona [ESC] para salir.")

            def tarea(acc, ms):
                while not self.detenido:
                    self._hacer_clic(acc)
                    time.sleep(0.2)
                    t_trans = 0
                    s = ms / 1000.0
                    while t_trans < s and not self.detenido:
                        time.sleep(0.05)
                        t_trans += 0.05

            hilos = [threading.Thread(target=tarea, args=(
                acc, ms), daemon=True) for acc, ms in acciones_intervalos.items()]
            for h in hilos:
                h.start()

            while not self.detenido:
                time.sleep(0.2)
