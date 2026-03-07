import time
import json
import threading
import os
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener

class MouseRecorder:
    def __init__(self):
        self.mouse_controller = MouseController()
        self.events = []
        self.recording = False
        self.start_time = None
        self.listener = None
        self.recordings_dir = "recordings"
        self.current_recording_name = None
        
        # Crear directorio de grabaciones si no existe
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
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
    
    def start_recording(self):
        """Inicia la grabación de eventos del mouse"""
        self.events = []
        self.recording = True
        self.start_time = time.time()
        
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()
        print("🔴 Grabación iniciada... Presiona 'ESC' para detener.")
    
    def stop_recording(self):
        """Detiene la grabación"""
        self.recording = False
        if self.listener:
            self.listener.stop()
        print(f"⏹️ Grabación detenida. {len(self.events)} eventos capturados.")
    
    def save_recording(self, filename=None):
        """Guarda la grabación en un archivo JSON con metadata"""
        if not self.events:
            print("⚠️ No hay eventos para guardar.")
            return False
        
        if filename is None:
            # Generar nombre automático con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"routine_{timestamp}.json"
        elif not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = os.path.join(self.recordings_dir, filename)
        
        # Crear metadata
        recording_data = {
            'metadata': {
                'name': filename.replace('.json', ''),
                'created': datetime.now().isoformat(),
                'events_count': len(self.events),
                'duration': self.events[-1]['time'] if self.events else 0
            },
            'events': self.events
        }
        
        with open(filepath, 'w') as f:
            json.dump(recording_data, f, indent=2)
        
        self.current_recording_name = filename
        print(f"💾 Grabación guardada en '{filepath}'")
        print(f"   📊 {len(self.events)} eventos | ⏱️ {recording_data['metadata']['duration']:.2f}s")
        return True
    
    def load_recording(self, filename):
        """Carga una grabación desde un archivo JSON"""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = os.path.join(self.recordings_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Soportar formato antiguo y nuevo
            if isinstance(data, dict) and 'events' in data:
                self.events = data['events']
                metadata = data.get('metadata', {})
                print(f"📂 Grabación cargada: {metadata.get('name', filename)}")
                print(f"   📊 {len(self.events)} eventos | ⏱️ {metadata.get('duration', 0):.2f}s")
            else:
                # Formato antiguo (solo lista de eventos)
                self.events = data
                print(f"📂 Grabación cargada: {len(self.events)} eventos")
            
            self.current_recording_name = filename
            return True
        except FileNotFoundError:
            print(f"❌ Archivo '{filepath}' no encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"❌ Error al leer el archivo '{filepath}'.")
            return False
    
    def play_recording(self, speed=1.0):
        """Reproduce la grabación"""
        if not self.events:
            print("⚠️ No hay eventos para reproducir.")
            return
        
        print(f"▶️ Reproduciendo {len(self.events)} eventos (velocidad: {speed}x)...")
        print("   Presiona 'ESC' para cancelar.")
        
        self.playing = True
        start_time = time.time()
        
        # Listener para cancelar con ESC
        def on_press(key):
            if key == Key.esc:
                self.playing = False
                return False
        
        cancel_listener = KeyboardListener(on_press=on_press)
        cancel_listener.start()
        
        for event in self.events:
            if not self.playing:
                print("⏹️ Reproducción cancelada.")
                break
            
            # Esperar hasta el momento correcto
            target_time = event['time'] / speed
            elapsed = time.time() - start_time
            if target_time > elapsed:
                time.sleep(target_time - elapsed)
            
            # Ejecutar el evento
            if event['type'] == 'move':
                self.mouse_controller.position = (event['x'], event['y'])
            
            elif event['type'] == 'click':
                self.mouse_controller.position = (event['x'], event['y'])
                button = Button.left if event['button'] == 'left' else Button.right
                if event['pressed']:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
            
            elif event['type'] == 'scroll':
                self.mouse_controller.position = (event['x'], event['y'])
                self.mouse_controller.scroll(event['dx'], event['dy'])
        
        cancel_listener.stop()
        if self.playing:
            print("✅ Reproducción completada.")
    
    def list_recordings(self):
        """Lista todas las grabaciones guardadas"""
        if not os.path.exists(self.recordings_dir):
            print("⚠️ No hay grabaciones guardadas.")
            return []
        
        recordings = [f for f in os.listdir(self.recordings_dir) if f.endswith('.json')]
        
        if not recordings:
            print("⚠️ No hay grabaciones guardadas.")
            return []
        
        print(f"\n📁 Rutinas guardadas ({len(recordings)}):")
        print("-" * 70)
        
        for i, filename in enumerate(sorted(recordings), 1):
            filepath = os.path.join(self.recordings_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and 'metadata' in data:
                    metadata = data['metadata']
                    name = metadata.get('name', filename.replace('.json', ''))
                    events_count = metadata.get('events_count', 0)
                    duration = metadata.get('duration', 0)
                    created = metadata.get('created', 'Desconocido')
                    
                    # Formatear fecha
                    try:
                        created_dt = datetime.fromisoformat(created)
                        created_str = created_dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        created_str = created
                    
                    print(f"{i}. {name}")
                    print(f"   📊 {events_count} eventos | ⏱️ {duration:.2f}s | 📅 {created_str}")
                else:
                    # Formato antiguo
                    events_count = len(data) if isinstance(data, list) else 0
                    print(f"{i}. {filename}")
                    print(f"   📊 {events_count} eventos")
            except:
                print(f"{i}. {filename} (error al leer)")
            
            print("-" * 70)
        
        return recordings
    
    def delete_recording(self, filename):
        """Elimina una grabación guardada"""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = os.path.join(self.recordings_dir, filename)
        
        try:
            os.remove(filepath)
            print(f"🗑️ Grabación '{filename}' eliminada.")
            return True
        except FileNotFoundError:
            print(f"❌ Archivo '{filename}' no encontrado.")
            return False
        except Exception as e:
            print(f"❌ Error al eliminar: {e}")
            return False
    
    def auto_save_recording(self):
        """Guarda automáticamente la grabación actual con nombre generado"""
        if not self.events:
            return False
        return self.save_recording()
    
    def get_recording_info(self, filename):
        """Obtiene información detallada de una grabación"""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = os.path.join(self.recordings_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'metadata' in data:
                return data['metadata']
            else:
                return {
                    'events_count': len(data) if isinstance(data, list) else 0,
                    'name': filename.replace('.json', '')
                }
        except:
            return None


def main():
    recorder = MouseRecorder()
    stop_event = threading.Event()
    
    def on_press(key):
        if key == Key.esc:
            if recorder.recording:
                recorder.stop_recording()
                stop_event.set()
                return False
    
    while True:
        print("\n" + "="*50)
        print("🖱️  GRABADOR DE MOUSE - AUTOCLICKER")
        print("="*50)
        print("GRABACIÓN:")
        print("  1. Grabar nuevos movimientos")
        print("  2. Reproducir última grabación")
        print("  3. Reproducir con velocidad personalizada")
        print("\nGESTIÓN DE RUTINAS:")
        print("  4. Guardar grabación actual")
        print("  5. Listar todas las rutinas guardadas")
        print("  6. Cargar rutina específica")
        print("  7. Eliminar rutina guardada")
        print("  8. Auto-guardar grabación actual")
        print("\nINFO:")
        print("  9. Ver cantidad de eventos grabados")
        print("  0. Salir")
        print("-"*50)
        
        option = input("Selecciona una opción: ").strip()
        
        if option == '1':
            stop_event.clear()
            recorder.start_recording()
            
            # Escuchar ESC para detener
            with KeyboardListener(on_press=on_press) as listener:
                listener.join()
            
            # Preguntar si desea guardar automáticamente
            if recorder.events:
                save_option = input("\n¿Guardar esta grabación? (s/n): ").strip().lower()
                if save_option == 's':
                    name = input("Nombre (Enter para auto-generar): ").strip()
                    if name:
                        recorder.save_recording(name)
                    else:
                        recorder.auto_save_recording()
        
        elif option == '2':
            recorder.play_recording()
        
        elif option == '3':
            try:
                speed = float(input("Velocidad (ej: 0.5 = lento, 2.0 = rápido): "))
                recorder.play_recording(speed=speed)
            except ValueError:
                print("❌ Velocidad inválida.")
        
        elif option == '4':
            if recorder.events:
                filename = input("Nombre del archivo (Enter para auto-generar): ").strip()
                if filename:
                    recorder.save_recording(filename)
                else:
                    recorder.auto_save_recording()
            else:
                print("⚠️ No hay grabación para guardar.")
        
        elif option == '5':
            recorder.list_recordings()
        
        elif option == '6':
            recordings = recorder.list_recordings()
            if recordings:
                choice = input("\nNúmero de rutina a cargar (o nombre): ").strip()
                try:
                    # Intentar convertir a número
                    idx = int(choice) - 1
                    if 0 <= idx < len(recordings):
                        recorder.load_recording(recordings[idx])
                    else:
                        print("❌ Número inválido.")
                except ValueError:
                    # Es un nombre
                    recorder.load_recording(choice)
        
        elif option == '7':
            recordings = recorder.list_recordings()
            if recordings:
                choice = input("\nNúmero de rutina a eliminar (o nombre): ").strip()
                confirm = input(f"⚠️ ¿Seguro que deseas eliminar? (s/n): ").strip().lower()
                if confirm == 's':
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(recordings):
                            recorder.delete_recording(recordings[idx])
                        else:
                            print("❌ Número inválido.")
                    except ValueError:
                        recorder.delete_recording(choice)
                else:
                    print("❌ Eliminación cancelada.")
        
        elif option == '8':
            if recorder.events:
                recorder.auto_save_recording()
            else:
                print("⚠️ No hay grabación para guardar.")
        
        elif option == '9':
            print(f"📊 Eventos grabados: {len(recorder.events)}")
            if recorder.current_recording_name:
                print(f"📝 Rutina actual: {recorder.current_recording_name}")
        
        elif option == '0':
            # Preguntar si hay cambios sin guardar
            if recorder.events and not recorder.current_recording_name:
                save_option = input("\n⚠️ Hay grabaciones sin guardar. ¿Guardar antes de salir? (s/n): ").strip().lower()
                if save_option == 's':
                    recorder.auto_save_recording()
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida.")


if __name__ == "__main__":
    main()
