import time
import psutil
import win32gui
import win32con
import win32process
import pygetwindow as gw


def buscar_ventana_exacta(titulo):
    ventanas = gw.getWindowsWithTitle(titulo)

    for w in ventanas:
        if w.title == titulo:
            return w

    return None


def buscar_render_widget(hwnd_padre):
    render = []

    def callback(hwnd, _):
        clase = win32gui.GetClassName(hwnd)
        print(f"Hijo -> HWND={hwnd} Clase={clase}")

        if clase == "Chrome_RenderWidgetHostHWND":
            render.append(hwnd)

        return True

    win32gui.EnumChildWindows(hwnd_padre, callback, None)

    if render:
        return render[0]

    return None


def main():
    ventana = buscar_ventana_exacta("Idle Skilling")

    if ventana is None:
        print("❌ No se encontró la ventana 'Idle Skilling'")
        return

    hwnd = ventana._hWnd

    print("=" * 60)
    print("Ventana encontrada")
    print("=" * 60)
    print("Título :", win32gui.GetWindowText(hwnd))
    print("HWND   :", hwnd)
    print("Clase  :", win32gui.GetClassName(hwnd))

    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    proceso = psutil.Process(pid)

    print("PID    :", pid)
    print("Proceso:", proceso.name())
    print("Ruta   :", proceso.exe())

    print("\nBuscando ventana de render...\n")

    render = buscar_render_widget(hwnd)

    if render is None:
        print("❌ No se encontró Chrome_RenderWidgetHostHWND")
        return

    print("\nRender HWND:", render)

    # Coordenadas internas del juego
    x = 100
    y = 100

    lparam = (y << 16) | (x & 0xFFFF)

    print("\nEnviando clic en 3 segundos...")
    time.sleep(3)

    win32gui.SendMessage(
        render,
        win32con.WM_MOUSEMOVE,
        0,
        lparam
    )

    win32gui.SendMessage(
        render,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    win32gui.SendMessage(
        render,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    print("✅ Mensajes enviados.")


if __name__ == "__main__":
    main()
