# Autoclicker

Un grabador y reproductor de eventos de mouse y teclado desarrollado en Python con interfaz gráfica moderna. Perfecto para automatizar tareas repetitivas que requieren interacción precisa.

## Características

- **Grabación completa**: Captura movimientos del mouse, clics, scroll y teclas
- **Reproducción precisa**: Reproduce eventos con timing exacto
- **Velocidad ajustable**: Controla la velocidad de reproducción (0.5x - 10x)
- **Gestión de rutinas**: Guarda, carga, edita y elimina rutinas fácilmente
- **Sistema de alertas**: Programa rutinas para ejecutarse automáticamente
- **Recorte automático**: Elimina los últimos segundos de grabación (útil para quitar el clic de detener)
- **Grabación de teclado**: Opción para incluir pulsaciones de teclas
- **Multiidioma**: Interfaz en Español e Inglés
- **Interfaz moderna**: UI oscura y profesional con Streamlit
- **Modo ventana nativa**: Ejecuta como aplicación independiente

## Descarga rápida (Windows)

Si solo quieres usar la aplicación sin instalar Python:

1. Ve a la sección [**Releases**](https://github.com/Alvaro-San-Cav/Autoclicker/releases) del repositorio
2. Descarga `Autoclicker.exe` de la última versión
3. Ejecuta el `.exe` — no necesitas instalar nada más

> Nota: Windows puede mostrar una advertencia de SmartScreen al ejecutar el `.exe` por primera vez. Haz clic en **"Más información" → "Ejecutar de todas formas"**.

## Instalación desde código fuente

### Requisitos previos

- **Python 3.9+** ([descargar](https://www.python.org/downloads/))
- **Windows 10/11** (el modo ventana nativa usa Chrome/Edge)
- **Google Chrome** o **Microsoft Edge** (para el modo ventana nativa)

### Pasos

1. Clona este repositorio:
```bash
git clone https://github.com/Alvaro-San-Cav/Autoclicker.git
cd Autoclicker
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Modo aplicación (recomendado):
```bash
python launcher.py
```
Abre la aplicación en una ventana nativa sin pestañas del navegador.

### Modo navegador:
```bash
streamlit run autoclicker/app.py
```
Abre la aplicación en tu navegador predeterminado.

## Estructura del proyecto

Ver [STRUCTURE.md](STRUCTURE.md) para detalles completos de la arquitectura.

```
Autoclicker/
├── autoclicker/              # Paquete principal
│   ├── app.py               # Interfaz Streamlit
│   ├── recorder.py          # Lógica de grabación/reproducción
│   ├── scheduler.py         # Sistema de alertas programadas
│   └── i18n.py              # Traducciones (ES/EN)
├── launcher.py              # Lanzador de aplicación nativa
├── recordings/              # Rutinas guardadas (JSON)
├── build/                   # Scripts y configuración para compilar .exe
├── examples/                # Versión de consola (legacy)
└── requirements.txt         # Dependencias de Python
```

## Dependencias

| Paquete | Descripción |
|---------|-------------|
| `streamlit` | Framework de interfaz web interactiva |
| `pynput` | Control y monitoreo del mouse y teclado |

## Guía de uso

### 1. Grabar una rutina
1. Ve a la pestaña **"Grabación"**
2. Escribe un nombre y descripción (opcional)
3. Marca **"Grabar también el teclado"** si necesitas capturar teclas
4. Haz clic en **"INICIAR GRABACIÓN"**
5. Realiza las acciones que deseas automatizar
6. Haz clic en **"DETENER GRABACIÓN"**
7. La rutina se guarda automáticamente

### 2. Gestionar rutinas
1. Ve a la pestaña **"Mis Rutinas"**
2. Visualiza todas tus rutinas guardadas
3. Acciones disponibles:
   - Reproducir
   - Marcar como Favorito
   - Eliminar
4. Usa la sección de **edición rápida** para:
   - Renombrar rutinas
   - Ajustar velocidad predeterminada
   - Modificar descripción

### 3. Programar alertas
1. Ve a la pestaña **"Alertas"**
2. Rellena el formulario:
   - Nombre de la alerta
   - Rutina a ejecutar
   - Fecha y hora
   - Frecuencia (una vez, diaria, semanal, laborables)
3. Haz clic en **"Añadir Alerta"**
4. Activa/desactiva o elimina alertas según necesites

### 4. Configuración
1. Ve a la pestaña **"Configuración"**
2. Ajusta:
   - **Idioma**: Español o Inglés
   - **Recorte automático**: Elimina los últimos X segundos de cada grabación

## Compilar ejecutable (.exe)

Para generar un ejecutable independiente que no requiera Python instalado:

```bash
cd build
build_exe.bat
```

> Requiere PyInstaller (se instala automáticamente durante el build).

El ejecutable se generará en `dist/Autoclicker.exe`. Puedes distribuir este archivo directamente.

## Formato de grabación

Las grabaciones se guardan en formato JSON con metadata y eventos:

```json
{
  "metadata": {
    "name": "routine_20260306_143022",
    "created": "2026-03-06T14:30:22.123456",
    "events_count": 15,
    "duration": 5.43
  },
  "events": [
    {
      "type": "move",
      "x": 100,
      "y": 200,
      "time": 0.5
    },
    {
      "type": "click",
      "x": 150,
      "y": 250,
      "button": "left",
      "pressed": true,
      "time": 1.0
    },
    {
      "type": "scroll",
      "x": 200,
      "y": 300,
      "dx": 0,
      "dy": 1,
      "time": 2.0
    }
  ]
}
```

### Tipos de eventos:
- **move**: Movimiento del cursor
- **click**: Clic del mouse (left/right)
- **scroll**: Scroll de la rueda del mouse

El programa es compatible con grabaciones antiguas (solo array de eventos).

## Notas importantes

- **Solo Windows**: El modo ventana nativa y la compilación .exe están diseñados para Windows 10/11
- Asegúrate de tener **Google Chrome** o **Microsoft Edge** instalado para el modo ventana nativa
- En Linux/macOS puedes usar el modo navegador (`streamlit run autoclicker/app.py`) pero sin modo ventana nativa
- Usa este software de manera responsable y ética


## Enlaces

- [Repositorio GitHub](https://github.com/Alvaro-San-Cav/Autoclicker)
- [Documentación de pynput](https://pynput.readthedocs.io/)
