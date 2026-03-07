# autoclicker.spec
# PyInstaller spec file para Autoclicker
# Genera un .exe monolítico con todo incluido

import os
import importlib
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# Directorio raíz del proyecto (un nivel arriba de build/)
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))

# Localizar los archivos estáticos de Streamlit (necesarios en tiempo de ejecución)
streamlit_dir = os.path.dirname(importlib.import_module('streamlit').__file__)

a = Analysis(
    [os.path.join(project_dir, 'launcher.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        # Carpeta recordings vacía (se crea en ejecución)
        (os.path.join(project_dir, 'recordings', '.gitkeep'), 'recordings'),
        # Archivos estáticos de Streamlit
        (os.path.join(streamlit_dir, 'static'), os.path.join('streamlit', 'static')),
        (os.path.join(streamlit_dir, 'runtime'), os.path.join('streamlit', 'runtime')),
        # Configuración de Streamlit
        (os.path.join(project_dir, '.streamlit'), '.streamlit'),
        # Paquete de la app
        (os.path.join(project_dir, 'autoclicker'), 'autoclicker'),
    ],
    hiddenimports=[
        # Streamlit y sus dependencias
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        # pynput backends de Windows
        'pynput.mouse._win32',
        'pynput.keyboard._win32',
        # GUI / sistema
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'uuid',
        # Módulos de la app
        'autoclicker',
        'autoclicker.recorder',
        'autoclicker.scheduler',
        'autoclicker.i18n',
        'autoclicker.app',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Autoclicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # Sin ventana de consola (modo GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',       # Descomenta y pon tu .ico aquí si tienes uno
)
