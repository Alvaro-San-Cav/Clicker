# Estructura del Proyecto

Este documento describe la organización del código de Clicker-SAP.

## Arquitectura

```
Clicker-SAP/
├── clicker_sap/              # 📦 Paquete principal de la aplicación
│   ├── __init__.py          # Inicialización del paquete, exporta clases principales
│   ├── app.py               # 🎨 Interfaz de usuario con Streamlit
│   ├── recorder.py          # 🎯 Lógica de grabación y reproducción de eventos
│   ├── scheduler.py         # ⏰ Sistema de alertas y ejecución programada
│   └── i18n.py              # 🌐 Traducciones (ES/EN)
│
├── recordings/              # 💾 Almacenamiento de rutinas (auto-generado)
│   ├── .gitkeep             # Mantiene la carpeta en Git
│   └── *.json               # Rutinas, alertas y config generados en ejecución
│
├── build/                   # 🔨 Herramientas de compilación
│   ├── build_exe.bat        # Script para compilar .exe con PyInstaller
│   └── clicker_sap.spec     # Configuración de PyInstaller
│
├── examples/                # 📚 Código legacy
│   ├── README.md
│   └── main_console.py      # Versión de consola (standalone)
│
├── .streamlit/              # ⚙️ Configuración de Streamlit
│   └── config.toml
│
├── launcher.py              # 🚀 Punto de entrada principal (modo ventana)
├── requirements.txt         # 📋 Dependencias del proyecto
├── README.md                # 📖 Documentación principal
├── LICENSE                  # ⚖️ Licencia MIT
└── .gitignore               # 🚫 Archivos ignorados por Git
```

## Módulos principales

### `clicker_sap/recorder.py` - MouseRecorder
Clase principal para grabación y reproducción:
- **Grabación**: Captura eventos de mouse (move, click, scroll) y teclado
- **Reproducción**: Reproduce eventos con control de velocidad
- **Persistencia**: Guarda/carga rutinas en JSON
- **Edición**: Renombra, duplica, elimina rutinas

### `clicker_sap/scheduler.py` - AlertManager
Sistema de tareas programadas:
- **Alertas**: Programación de rutinas para fechas/horas específicas
- **Repetición**: Una vez, diaria, semanal, laborables
- **Estado**: Activa/desactiva alertas sin eliminarlas

### `clicker_sap/app.py` - Interfaz Streamlit
Aplicación web interactiva con 4 pestañas:
1. **Grabación**: Crear nuevas rutinas
2. **Mis Rutinas**: Gestionar rutinas guardadas
3. **Alertas**: Programar ejecuciones automáticas
4. **Configuración**: Ajustes de idioma y comportamiento

### `clicker_sap/i18n.py` - Internacionalización
Sistema de traducciones multiidioma (ES/EN).

## Flujo de ejecución

### Modo aplicación nativa
```
launcher.py → streamlit run clicker_sap/app.py → abre en Chrome/Edge -app mode
```

### Modo navegador
```
streamlit run clicker_sap/app.py → abre en navegador con pestañas
```

### Compilado
```
ClickerSAP.exe → bundle con todo incluido (PyInstaller)
```

## Notas de desarrollo

### Imports
- Los archivos dentro de `clicker_sap/` usan imports relativos: `from .recorder import ...`
- El `__init__.py` exporta las clases principales para facilitar imports externos

### Paths
- Todos los paths de archivos usan rutas absolutas basadas en el directorio raíz del proyecto
- `app.py` ajusta el CWD al directorio raíz automáticamente

### Estado
- Streamlit usa `st.session_state` para mantener el estado entre reruns
- El recorder y alert_manager son singleton por sesión

### Build
- PyInstaller empaqueta todo en un ejecutable monolítico
- Los datos (recordings/) se incluyen en el bundle pero son modificables
