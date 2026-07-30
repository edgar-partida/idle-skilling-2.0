import os
import json
import tkinter as tk
from tkinter import simpledialog
import pygetwindow as gw
from pynput import mouse, keyboard
from utils.logger_utils import configurar_logger

logger = configurar_logger()


class CoordinateManager:
    def __init__(self, resources_dir: str = "resources"):
        self.resources_dir = resources_dir
        self.coords_file = os.path.join(
            self.resources_dir, "relative-coords.json")
        self.puntos_configurados = {}

        self.capturando = False
        self.shift_pressed = False
        self.listener_mouse = None
        self.listener_teclado = None

        self._cargar_coordenadas()

    def _asegurar_directorio(self):
        if not os.path.exists(self.resources_dir):
            os.makedirs(self.resources_dir)

    def _cargar_coordenadas(self):
        if os.path.exists(self.coords_file):
            try:
                with open(self.coords_file, "r", encoding="utf-8") as f:
                    self.puntos_configurados = json.load(f)
                logger.info(f"Coordenadas cargadas desde {self.coords_file}")
            except Exception as e:
                logger.warning(f"Error al cargar el archivo JSON: {e}")
                self.puntos_configurados = {}

    def _guardar_coordenadas(self):
        self._asegurar_directorio()
        try:
            with open(self.coords_file, "w", encoding="utf-8") as f:
                json.dump(self.puntos_configurados, f,
                          indent=4, ensure_ascii=False)
            logger.info(
                f"Coordenadas guardadas exitosamente en {self.coords_file}")
        except Exception as e:
            logger.warning(f"Error al guardar en el archivo JSON: {e}")

    def _pedir_nombre_gui(self) -> str:
        """Abre una ventana emergente de tkinter forzada al frente y con foco."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()

        nombre = simpledialog.askstring(
            "Capturar Coordenada",
            "Ingresa el nombre para esta acción:",
            parent=root
        )

        root.destroy()
        return nombre.strip() if nombre else None

    def _on_press(self, key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.shift_pressed = True

    def _on_release(self, key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.shift_pressed = False

    def _on_click(self, x, y, button, pressed):
        if self.capturando and pressed and button == mouse.Button.left and self.shift_pressed:
            logger.info(f"Shift + Clic detectado en pantalla: X={x}, Y={y}")

            try:
                ventana_activa = gw.getActiveWindow()
                if not ventana_activa:
                    logger.warning("No se detectó ninguna ventana activa.")
                    return

                win_x, win_y = ventana_activa.left, ventana_activa.top
                win_w, win_h = ventana_activa.width, ventana_activa.height

                rel_x = x - win_x
                rel_y = y - win_y

                porcentaje_x = rel_x / win_w
                porcentaje_y = rel_y / win_h

                nombre = self._pedir_nombre_gui()

                if nombre:
                    self.puntos_configurados[nombre] = {
                        "porcentaje_x": round(porcentaje_x, 4),
                        "porcentaje_y": round(porcentaje_y, 4),
                        "ventana_ref": ventana_activa.title
                    }
                    self._guardar_coordenadas()
                    logger.info(f"Acción '{nombre}' guardada correctamente.")
                else:
                    logger.warning("Captura cancelada por el usuario.")

            except Exception as e:
                logger.error(f"Error al procesar la captura: {e}")

    def iniciar_captura(self):
        logger.info("==================================================")
        logger.info("   MODO CAPTURA DE COORDENADAS ACTIVADO")
        logger.info("   -> Mantén presionado Shift y haz Clic en el juego.")
        logger.info("   -> Se abrirá una ventana para ponerle nombre.")
        logger.info("   -> Presiona ENTER en la terminal para terminar.")
        logger.info("==================================================")

        self.capturando = True
        self.listener_mouse = mouse.Listener(on_click=self._on_click)
        self.listener_teclado = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release)

        self.listener_mouse.start()
        self.listener_teclado.start()

    def detener_captura(self):
        self.capturando = False
        if self.listener_mouse:
            self.listener_mouse.stop()
        if self.listener_teclado:
            self.listener_teclado.stop()
        logger.info("Modo captura finalizado.")
