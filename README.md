# Clicker-SAP 🖱️

Un grabador y reproductor de movimientos del mouse desarrollado en Python. Perfecto para automatizar tareas repetitivas que requieren interacción con el mouse.

## 📋 Características

- **Grabación de eventos del mouse**: Captura movimientos, clics y scroll
- **Reproducción precisa**: Reproduce los eventos grabados con timing exacto
- **Velocidad ajustable**: Reproduce a velocidad normal, lenta o rápida
- **Persistencia de rutinas**: Sistema completo de gestión de rutinas guardadas
- **Auto-guardado**: Opción para guardar automáticamente después de grabar
- **Gestión de rutinas**: Listar, cargar, eliminar rutinas guardadas
- **Metadata detallada**: Cada rutina incluye fecha, duración y cantidad de eventos
- **Cancelación con ESC**: Detén la grabación o reproducción en cualquier momento
- **Interfaz de consola intuitiva**: Menú organizado y fácil de usar

## 🚀 Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Alvaro-San-Cav/Clicker-SAP.git
cd Clicker-SAP
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
source .venv/bin/activate  # En Linux/Mac
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 📦 Dependencias

- `pynput`: Control y monitoreo del mouse y teclado

## 📁 Estructura del proyecto

```
autoclick/
├── main.py                          # Código principal del grabador
├── recordings/                      # Carpeta de rutinas guardadas
│   ├── .gitkeep                    # Mantiene la carpeta en Git
│   └── example_simple_clicks.json  # Ejemplo de rutina
├── requirements.txt                 # Dependencias de Python
├── README.md                        # Documentación
├── LICENSE                          # Licencia MIT
└── .gitignore                       # Archivos ignorados por Git
```

## 💻 Uso

Ejecuta el programa:
```bash
python main.py
```

### Menú principal:

**GRABACIÓN:**
1. **Grabar nuevos movimientos**: Inicia la grabación de tus movimientos del mouse
   - Al terminar, puedes guardar automáticamente la rutina
2. **Reproducir última grabación**: Reproduce la última sesión grabada
3. **Reproducir con velocidad personalizada**: Ajusta la velocidad de reproducción

**GESTIÓN DE RUTINAS:**
4. **Guardar grabación actual**: Guarda la grabación con un nombre específico
5. **Listar todas las rutinas guardadas**: Muestra todas las rutinas con detalles
6. **Cargar rutina específica**: Carga una rutina previamente guardada
7. **Eliminar rutina guardada**: Elimina rutinas que ya no necesites
8. **Auto-guardar grabación actual**: Guarda con nombre automático (timestamp)

**INFO:**
9. **Ver cantidad de eventos grabados**: Información de la sesión actual
0. **Salir**: Cierra el programa (pregunta si hay cambios sin guardar)

### Atajos de teclado:

- **ESC**: Detener grabación o reproducción en curso

### Sistema de persistencia:

Las rutinas se guardan en la carpeta `recordings/` con el siguiente formato:
- **Auto-generado**: `routine_YYYYMMDD_HHMMSS.json`
- **Personalizado**: `nombre_personalizado.json`

Cada rutina incluye:
- Nombre de la rutina
- Fecha y hora de creación
- Cantidad de eventos
- Duración total
- Todos los eventos grabados

## 📝 Formato de grabación

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

## ⚠️ Advertencias

- Asegúrate de tener permisos de accesibilidad habilitados en tu sistema operativo
- En macOS, puede ser necesario dar permisos en *Preferencias del Sistema > Seguridad y Privacidad > Accesibilidad*
- En Linux, asegúrate de que tu usuario tenga acceso a `/dev/uinput`
- Usa este software de manera responsable y ética

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado por Alvaro San Cav

## 🔗 Enlaces

- [Repositorio GitHub](https://github.com/Alvaro-San-Cav/Clicker-SAP)
- [Documentación de pynput](https://pynput.readthedocs.io/)
