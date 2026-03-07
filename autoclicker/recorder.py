"""
recorder.py - Lógica de negocio del grabador de mouse
Autoclicker - Módulo de grabación y reproducción
"""

import time
import json
import os
import sys
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener

# ──────────────────────────────────────────
# Configuración DPI Awareness para Windows
# ──────────────────────────────────────────
if sys.platform == "win32":
    try:
        import ctypes
        # Intenta configurar el proceso como DPI aware
        # Esto evita el escalado automático de Windows y permite coordenadas precisas
        try:
            # Para Windows 10 1607 y superior (SetProcessDpiAwarenessContext)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:
            try:
                # Para Windows Vista y superior (SetProcessDPIAware)
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass  # Si falla, continúa sin DPI awareness
    except Exception:
        pass  # Si ctypes no está disponible o hay error, continúa normalmente


class MouseRecorder:
    def __init__(self, recordings_dir="recordings"):
        self.mouse_controller = MouseController()
        self.keyboard_controller = keyboard.Controller()
        self.events = []
        self.recording = False
        self.playing = False
        self.start_time = None
        self.listener = None
        self.kb_listener = None
        self.recordings_dir = recordings_dir
        self.current_recording_name = None
        
        try:
            from .overlay import RecordingOverlay
            self.overlay = RecordingOverlay()
        except ImportError:
            try:
                from autoclicker.overlay import RecordingOverlay
                self.overlay = RecordingOverlay()
            except ImportError:
                self.overlay = None

        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)

    # ──────────────────────────────────────────
    # Callbacks de escucha
    # ──────────────────────────────────────────

    def on_move(self, x, y):
        if self.recording:
            self.events.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': time.time() - self.start_time
            })

    def on_click(self, x, y, button, pressed):
        if self.recording:
            self.events.append({
                'type': 'click',
                'x': x,
                'y': y,
                'button': 'left' if button == Button.left else 'right',
                'pressed': pressed,
                'time': time.time() - self.start_time
            })

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            self.events.append({
                'type': 'scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': time.time() - self.start_time
            })

    def on_key_press(self, key):
        if self.recording:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            self.events.append({
                'type': 'key_press',
                'key': char,
                'time': time.time() - self.start_time
            })

    def on_key_release(self, key):
        if self.recording:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            self.events.append({
                'type': 'key_release',
                'key': char,
                'time': time.time() - self.start_time
            })

    # ──────────────────────────────────────────
    # Grabación
    # ──────────────────────────────────────────

    def start_recording(self, record_keyboard=False):
        """Inicia la grabación de eventos del mouse (y teclado si record_keyboard=True)."""
        self.events = []
        self.recording = True
        self.start_time = time.time()

        if self.overlay:
            self.overlay.start()

        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()

        if record_keyboard:
            self.kb_listener = KeyboardListener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.kb_listener.start()
        else:
            self.kb_listener = None

    def stop_recording(self):
        """Detiene la grabación y devuelve el número de eventos capturados."""
        self.recording = False
        
        if self.overlay:
            self.overlay.stop()
            
        if self.listener:
            self.listener.stop()
            self.listener = None
        if self.kb_listener:
            self.kb_listener.stop()
            self.kb_listener = None
        return len(self.events)

    # ──────────────────────────────────────────
    # Reproducción
    # ──────────────────────────────────────────

    def play_recording(self, speed=1.0, on_progress=None, on_cancel_check=None):
        if not self.events:
            return False

        self.playing = True
        start_time = time.time()

        for i, event in enumerate(self.events):
            if on_cancel_check and on_cancel_check():
                self.playing = False
                break

            target_time = event['time'] / speed
            elapsed = time.time() - start_time
            if target_time > elapsed:
                time.sleep(target_time - elapsed)

            etype = event['type']
            if etype == 'move':
                self.mouse_controller.position = (event['x'], event['y'])
            elif etype == 'click':
                self.mouse_controller.position = (event['x'], event['y'])
                button = Button.left if event['button'] == 'left' else Button.right
                if event['pressed']:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
            elif etype == 'scroll':
                self.mouse_controller.position = (event['x'], event['y'])
                self.mouse_controller.scroll(event['dx'], event['dy'])
            elif etype == 'key_press':
                try:
                    k = event['key']
                    if k.startswith('Key.'): 
                        k = getattr(Key, k[4:], None)
                    if k:
                        self.keyboard_controller.press(k)
                except Exception:
                    pass
            elif etype == 'key_release':
                try:
                    k = event['key']
                    if k.startswith('Key.'):
                        k = getattr(Key, k[4:], None)
                    if k:
                        self.keyboard_controller.release(k)
                except Exception:
                    pass

            if on_progress:
                on_progress(i + 1, len(self.events))

        self.playing = False
        return True

    def stop_playback(self):
        """Cancela la reproducción en curso."""
        self.playing = False

    # ──────────────────────────────────────────
    # Edición de grabación
    # ──────────────────────────────────────────

    def trim_last_seconds(self, seconds: float):
        """
        Elimina los eventos capturados en los últimos `seconds` segundos.
        Útil para borrar el movimiento de ratón cuando vas a pulsar 'Detener'.
        Returns: la cantidad de eventos eliminados.
        """
        if not self.events or seconds <= 0:
            return 0
            
        total_duration = self.recording_duration
        cutoff_time = total_duration - seconds
        
        if cutoff_time <= 0:
            count = len(self.events)
            self.events = []
            return count
            
        # Keep events that happened before the cutoff
        original_count = len(self.events)
        self.events = [e for e in self.events if e['time'] <= cutoff_time]
        
        return original_count - len(self.events)

    # ──────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────

    def save_recording(self, name=None, description="", default_speed=1.0):
        """
        Guarda la grabación actual.
        Returns (filepath, metadata) o (None, None) si no hay eventos.
        """
        if not self.events:
            return None, None

        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"routine_{timestamp}"

        filename = name if name.endswith('.json') else f"{name}.json"
        filepath = os.path.join(self.recordings_dir, filename)

        duration = self.events[-1]['time'] if self.events else 0

        recording_data = {
            'metadata': {
                'name': name.replace('.json', ''),
                'description': description,
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'events_count': len(self.events),
                'duration': duration,
                'default_speed': default_speed,
            },
            'events': self.events
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recording_data, f, indent=2)

        self.current_recording_name = filename
        return filepath, recording_data['metadata']

    def load_recording(self, filename):
        """Carga una grabación. Devuelve metadata o None si falla."""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"

        filepath = os.path.join(self.recordings_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and 'events' in data:
                self.events = data['events']
                metadata = data.get('metadata', {})
            else:
                self.events = data
                metadata = {
                    'name': filename.replace('.json', ''),
                    'events_count': len(self.events)
                }

            self.current_recording_name = filename
            return metadata
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def list_recordings(self):
        """Devuelve lista de dicts con metadata de cada grabación."""
        result = []
        if not os.path.exists(self.recordings_dir):
            return result

        # Archivos de sistema que no son rutinas
        system_files = {'alerts.json', 'config.json', '.gitkeep'}
        
        for filename in sorted(os.listdir(self.recordings_dir)):
            if not filename.endswith('.json') or filename in system_files:
                continue
            filepath = os.path.join(self.recordings_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, dict) and 'metadata' in data:
                    meta = data['metadata'].copy()
                else:
                    events = data if isinstance(data, list) else []
                    meta = {
                        'name': filename.replace('.json', ''),
                        'events_count': len(events),
                        'duration': 0,
                        'created': '',
                        'description': '',
                        'default_speed': 1.0,
                    }
                meta['filename'] = filename
                result.append(meta)
            except Exception:
                result.append({
                    'name': filename.replace('.json', ''),
                    'filename': filename,
                    'events_count': 0,
                    'duration': 0,
                    'created': '',
                    'description': '',
                    'default_speed': 1.0,
                })
        return result

    def delete_recording(self, filename):
        """Elimina una grabación. Devuelve True si tuvo éxito."""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        filepath = os.path.join(self.recordings_dir, filename)
        try:
            os.remove(filepath)
            if self.current_recording_name == filename:
                self.current_recording_name = None
            return True
        except Exception:
            return False

    def rename_recording(self, old_filename, new_name):
        """Renombra una grabación y actualiza su metadata interna."""
        if not old_filename.endswith('.json'):
            old_filename = f"{old_filename}.json"

        new_filename = new_name if new_name.endswith('.json') else f"{new_name}.json"
        old_path = os.path.join(self.recordings_dir, old_filename)
        new_path = os.path.join(self.recordings_dir, new_filename)

        if not os.path.exists(old_path):
            return False
        if os.path.exists(new_path):
            return False

        try:
            with open(old_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'metadata' in data:
                data['metadata']['name'] = new_name.replace('.json', '')
                data['metadata']['modified'] = datetime.now().isoformat()
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.remove(old_path)
            if self.current_recording_name == old_filename:
                self.current_recording_name = new_filename
            return True
        except Exception:
            return False

    def update_metadata(self, filename, **kwargs):
        """Actualiza campos de metadata (description, default_speed, etc.)."""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        filepath = os.path.join(self.recordings_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'metadata' not in data:
                data = {'metadata': {}, 'events': data}

            data['metadata'].update(kwargs)
            data['metadata']['modified'] = datetime.now().isoformat()

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def duplicate_recording(self, filename):
        """Crea una copia de la grabación con sufijo _copy."""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        filepath = os.path.join(self.recordings_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            base = filename.replace('.json', '')
            new_name = f"{base}_copy"
            new_filename = f"{new_name}.json"
            new_path = os.path.join(self.recordings_dir, new_filename)

            # Evitar colisiones
            counter = 2
            while os.path.exists(new_path):
                new_name = f"{base}_copy{counter}"
                new_filename = f"{new_name}.json"
                new_path = os.path.join(self.recordings_dir, new_filename)
                counter += 1

            if isinstance(data, dict) and 'metadata' in data:
                data['metadata']['name'] = new_name
                data['metadata']['created'] = datetime.now().isoformat()
                data['metadata']['modified'] = datetime.now().isoformat()

            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return new_filename
        except Exception:
            return None

    @property
    def events_count(self):
        return len(self.events)

    @property
    def recording_duration(self):
        if not self.events:
            return 0.0
        return self.events[-1]['time']
