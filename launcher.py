"""
launcher.py - Lanza Autoclicker en una ventana nativa estilo app.
Arranca Streamlit como subproceso y usa Chrome/Edge en "App Mode" (--app=URL)
para ocultar pestañas y menús, sin depender de librerías externas que fallan en compilar.
"""

import subprocess
import sys
import os
import time
import socket
import threading

# ──────────────────────────────────────────
# Configuración DPI Awareness para Windows
# ──────────────────────────────────────────
if sys.platform == "win32":
    try:
        import ctypes
        # Configurar el proceso como DPI aware para coordenadas precisas del mouse
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    except Exception:
        pass

STREAMLIT_PORT = 8501
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 650


def find_free_port(start=8501):
    """Encuentra un puerto libre."""
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start


def wait_for_server(port, timeout=15):
    """Espera hasta que el servidor Streamlit esté listo."""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                return True
        time.sleep(0.3)
    return False


def get_browser_path():
    """Busca Chrome o Edge en el sistema."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.join("C:\\Users", os.environ.get('USERNAME', ''), "AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def set_always_on_top():
    """Busca la ventana de Autoclicker y la pone siempre visible (always-on-top) usando Win32 API."""
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040

        # Esperar a que la ventana aparezca (hasta 10s)
        hwnd = None
        for _ in range(40):
            hwnd = user32.FindWindowW(None, "Autoclicker")
            if hwnd:
                break
            time.sleep(0.25)

        if hwnd:
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )
    except Exception:
        pass  # No es crítico, solo un extra de UX


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # En modo PyInstaller, los archivos están en _MEIPASS
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    app_py = os.path.join(script_dir, "autoclicker", "app.py")
    port = find_free_port(STREAMLIT_PORT)

    streamlit_args = [
        "--server.headless", "true",
        "--browser.serverAddress", "127.0.0.1",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--server.port", str(port),
        "--theme.base", "dark",
        "--theme.primaryColor", "#6c63ff",
        "--theme.backgroundColor", "#0f1117",
        "--theme.secondaryBackgroundColor", "#1a1d2e",
        "--theme.textColor", "#e8e8f0",
    ]

    if getattr(sys, 'frozen', False):
        # PyInstaller: arrancar Streamlit directamente en un hilo
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", app_py] + streamlit_args
        st_thread = threading.Thread(target=stcli.main, daemon=True)
        st_thread.start()
    else:
        # Modo desarrollo: arrancar Streamlit como subproceso
        env = os.environ.copy()
        env["STREAMLIT_SERVER_HEADLESS"] = "true"
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        env["STREAMLIT_SERVER_PORT"] = str(port)

        proc_streamlit = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", app_py] + streamlit_args,
            cwd=script_dir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    url = f"http://127.0.0.1:{port}"

    if not wait_for_server(port):
        print(f"⚠️  No se pudo conectar a Streamlit en el puerto {port}.")
        if not getattr(sys, 'frozen', False):
            proc_streamlit.terminate()
        sys.exit(1)

    # 2. Abrir la URL en modo App nativa
    browser_path = get_browser_path()
    if browser_path:
        # Usar un perfil aislado para garantizar que respeta el tamaño y guarda estado propio
        user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Autoclicker", "ChromeProfile")

        # Limpiar caché del perfil para evitar errores de módulos JS obsoletos
        cache_dirs = ["Cache", "Code Cache", "Service Worker"]
        for cdir in cache_dirs:
            cache_path = os.path.join(user_data_dir, "Default", cdir)
            if os.path.isdir(cache_path):
                import shutil
                shutil.rmtree(cache_path, ignore_errors=True)

        # Modo App abre el browser sin pestañas ni barra de búsqueda
        subprocess.Popen([
            browser_path, 
            f"--app={url}", 
            f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disk-cache-size=1",
            "--aggressive-cache-discard",
        ])

        # 2b. Poner la ventana siempre visible (always on top)
        threading.Thread(target=set_always_on_top, daemon=True).start()
    else:
        # Fallback a abrir el navegador por defecto normalmente si no encuentra Chrome/Edge
        import webbrowser
        webbrowser.open(url)
    
    # 3. Mantener el launcher vivo mientras streamlit corre, o matarlo si se pulsa Ctrl+C
    try:
        if getattr(sys, 'frozen', False):
            st_thread.join()
        else:
            proc_streamlit.wait()
    except KeyboardInterrupt:
        if not getattr(sys, 'frozen', False):
            proc_streamlit.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
