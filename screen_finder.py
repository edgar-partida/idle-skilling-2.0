import time
import pygetwindow as gw
import win32gui
import win32con


def traer_ventana_al_frente_forzado():
    titulo_objetivo = "Idle Skilling"  # Título exacto de la ventana del juego

    print(f"Buscando la ventana exacta: '{titulo_objetivo}'...")

    # Buscamos todas las ventanas y filtramos por coincidencia exacta
    ventanas_encontradas = []
    for win in gw.getAllWindows():
        if win.title == titulo_objetivo:
            ventanas_encontradas.append(win)

    if not ventanas_encontradas:
        print(
            f"❌ No se encontró ninguna ventana con el título exacto '{titulo_objetivo}'.")
        print("Asegúrate de que el juego esté abierto y no minimizado.")
        return False

    win = ventanas_encontradas[0]
    print(f"¡Ventana encontrada con éxito: '{win.title}'!")

    try:
        hwnd = win._hWnd

        if win.isMinimized:
            win.restore()

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,
                              0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0,
                              0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetForegroundWindow(hwnd)

        print("✨ ¡La ventana del juego ha sido traída al frente a la fuerza!")
        return True

    except Exception as e:
        print(f"⚠️ Error al forzar la ventana al frente: {e}")
        return False


if __name__ == "__main__":
    traer_ventana_al_frente_forzado()
