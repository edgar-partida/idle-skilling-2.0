import os
import json
import time
import threading
import keyboard
import pyautogui
import pygetwindow as gw
import win32gui
from utils.screen_finder import traer_ventana_al_frente


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
                print(f"⚠️ Error al cargar coordenadas: {e}")

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
        print("\n==================================================")
        print("          CREADOR DE RUTINAS NUEVAS")
        print("==================================================")

        if not self.puntos_configurados:
            print(
                "❌ No hay acciones configuradas en 'relative-coords.json'. Configura coordenadas primero.")
            return

        print("Acciones disponibles que puedes usar:")
        for nombre in self.puntos_configurados.keys():
            print(f" -> {nombre}")

        tipo = input("\n¿Qué tipo de rutina deseas crear?\n1. Secuencial (Paso a paso con delays)\n2. Paralela (Por intervalos de milisegundos)\nElige opción (1 o 2): ").strip()

        nombre_rutina = input(
            "Asigna un nombre único para esta rutina: ").strip()
        if not nombre_rutina:
            print("❌ El nombre no puede estar vacío.")
            return

        if tipo == "1":
            pasos = []
            print("\n--- Armando Secuencia ---")
            print("Escribe la acción o 'DELAY'. Escribe 'fin' cuando termines.")

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
                        print("⚠️ Valor inválido.")
                elif accion in self.puntos_configurados:
                    pasos.append([accion, 0])
                    print(f"  -> Añadido: {accion}")
                else:
                    print("⚠️ Acción no reconocida.")

            if pasos:
                rutinas = self._cargar_json(self.seq_routines_file)
                rutinas[nombre_rutina] = pasos
                self._guardar_json(self.seq_routines_file, rutinas)
                print(
                    f"✅ ¡Rutina secuencial '{nombre_rutina}' guardada exitosamente!")
            else:
                print("⚠️ Rutina vacía, no se guardó.")

        elif tipo == "2":
            acciones_intervalos = {}
            print("\n--- Armando Rutina Paralela ---")
            print(
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
                        print(f"  -> Configurado: {accion} cada {ms}ms")
                    except ValueError:
                        print("⚠️ Debe ser un número válido.")
                else:
                    print("⚠️ Acción no encontrada.")

            if acciones_intervalos:
                rutinas = self._cargar_json(self.par_routines_file)
                rutinas[nombre_rutina] = acciones_intervalos
                self._guardar_json(self.par_routines_file, rutinas)
                print(
                    f"✅ ¡Rutina paralela '{nombre_rutina}' guardada exitosamente!")
            else:
                print("⚠️ Rutina vacía, no se guardó.")

    def _hacer_clic(self, nombre_accion: str):
        if nombre_accion not in self.puntos_configurados:
            return

        data = self.puntos_configurados[nombre_accion]
        titulo_ventana = data['ventana_ref']

        ventanas = gw.getWindowsWithTitle(titulo_ventana)
        if not ventanas:
            print(f"⚠️ No se encontró la ventana: '{titulo_ventana}'")
            return

        win = ventanas[0]

        try:
            # Usar la posición absoluta de la ventana en pantalla
            win_x, win_y = win.left, win.top
            win_w, win_h = win.width, win.height

            # Nota: Si el juego tiene barra de título superior, Windows a veces desplaza el contenido interno.
            # Si tus porcentajes se guardaron con la ventana en su estado actual, usamos directamente el tamaño total:
            target_x = win_x + int(data['porcentaje_x'] * win_w)
            target_y = win_y + int(data['porcentaje_y'] * win_h)

            # Protección de seguridad para que nunca haga clic en la barra de tareas o fuera de la pantalla
            if target_y > win_y + win_h:
                target_y = win_y + win_h - 10

            pyautogui.click(target_x, target_y)
            print(
                f"🖱️ Clic exacto en [{nombre_accion}] -> Pantalla X={target_x}, Y={target_y}")

        except Exception as e:
            print(f"⚠️ Error al calcular la posición exacta del clic: {e}")

    def _escuchar_escape(self):
        """Monitorea de forma segura la tecla ESC sin bloquear instantáneamente."""
        while not self.detenido:
            if keyboard.is_pressed('esc'):
                self.detenido = True
                print("\n🛑 ¡Detenido por el usuario (ESC)!")
                break
            time.sleep(0.1)

    def ejecutar_rutina_por_indice(self, tipo: str, indice_str: str):
        ruta_archivo = self.seq_routines_file if tipo == "secuencial" else self.par_routines_file
        rutinas = self._cargar_json(ruta_archivo)

        if not rutinas:
            print(f"❌ No hay rutinas {tipo}s guardadas.")
            return

        nombres_rutinas = list(rutinas.keys())

        try:
            indice = int(indice_str) - 1
            if indice < 0 or indice >= len(nombres_rutinas):
                print("❌ Número de rutina fuera de rango.")
                return
        except ValueError:
            print("❌ Debes ingresar un número válido.")
            return

        nombre_seleccionado = nombres_rutinas[indice]

        # 1. Traer la ventana al frente obligatoriamente antes de ejecutar
        print(f"\nPreparando ejecución de '{nombre_seleccionado}'...")
        if not traer_ventana_al_frente(self.titulo_objetivo):
            print("❌ No se pudo enfocar la ventana del juego. Cancelando ejecución.")
            return

        self.detenido = False
        hilo_esc = threading.Thread(target=self._escuchar_escape, daemon=True)
        hilo_esc.start()

        if tipo == "secuencial":
            pasos = rutinas[nombre_seleccionado]
            print(
                f"\n▶️ Ejecutando SECUENCIAL: '{nombre_seleccionado}'. Presiona [ESC] para salir.")

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
            print(
                f"\n▶️ Ejecutando PARALELA: '{nombre_seleccionado}'. Presiona [ESC] para salir.")

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


0
