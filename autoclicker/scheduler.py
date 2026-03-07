"""
scheduler.py - Sistema de alertas y avisos programados
Autoclicker - Módulo de programación de rutinas
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional


ALERTS_FILE = "recordings/alerts.json"

REPEAT_OPTIONS = {
    "Una vez": "once",
    "Diariamente": "daily",
    "Semanalmente": "weekly",
    "Laborables (L-V)": "weekdays",
}
REPEAT_LABELS = {v: k for k, v in REPEAT_OPTIONS.items()}


class Alert:
    def __init__(
        self,
        alert_id: str,
        name: str,
        recording: str,
        scheduled_dt: str,   # ISO format
        repeat: str = "once",
        active: bool = True,
        description: str = "",
    ):
        self.id = alert_id
        self.name = name
        self.recording = recording          # filename of the recording
        self.scheduled_dt = scheduled_dt    # ISO string
        self.repeat = repeat                # once | daily | weekly | weekdays
        self.active = active
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'recording': self.recording,
            'scheduled_dt': self.scheduled_dt,
            'repeat': self.repeat,
            'active': self.active,
            'description': self.description,
        }

    @staticmethod
    def from_dict(d):
        return Alert(
            alert_id=d['id'],
            name=d['name'],
            recording=d['recording'],
            scheduled_dt=d['scheduled_dt'],
            repeat=d.get('repeat', 'once'),
            active=d.get('active', True),
            description=d.get('description', ''),
        )

    @property
    def scheduled_datetime(self) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(self.scheduled_dt)
        except Exception:
            return None

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """Devuelve True si la alerta debe dispararse ahora (en el segundo 00-02 del minuto programado)."""
        if not self.active:
            return False
        dt = self.scheduled_datetime
        if dt is None:
            return False
        if now is None:
            now = datetime.now()
        
        # Solo disparar si coincide hora y minuto, y estamos en los primeros 3 segundos
        return (now.year == dt.year and now.month == dt.month and now.day == dt.day and
                now.hour == dt.hour and now.minute == dt.minute and now.second <= 2)

    def next_occurrence(self) -> Optional[str]:
        """Calcula la próxima fecha según la repetición y la actualiza."""
        dt = self.scheduled_datetime
        if dt is None:
            return None

        if self.repeat == "once":
            self.active = False
            return None
        elif self.repeat == "daily":
            next_dt = dt + timedelta(days=1)
        elif self.repeat == "weekly":
            next_dt = dt + timedelta(weeks=1)
        elif self.repeat == "weekdays":
            next_dt = dt + timedelta(days=1)
            while next_dt.weekday() >= 5:   # sáb=5, dom=6
                next_dt += timedelta(days=1)
        else:
            self.active = False
            return None

        self.scheduled_dt = next_dt.isoformat()
        return self.scheduled_dt


class AlertManager:
    def __init__(self, alerts_file: str = ALERTS_FILE, on_trigger: Optional[Callable] = None):
        """
        on_trigger(alert): callback que recibe la alerta cuando es hora de ejecutarla.
        """
        self.alerts_file = alerts_file
        self.on_trigger = on_trigger
        self._alerts: list[Alert] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._triggered_this_minute = set()  # Para evitar disparos duplicados

        os.makedirs(os.path.dirname(alerts_file), exist_ok=True)
        self._load()

    # ──────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────

    def add_alert(self, name: str, recording: str, scheduled_dt: str,
                  repeat: str = "once", description: str = "") -> Alert:
        import uuid
        with self._lock:
            alert = Alert(
                alert_id=str(uuid.uuid4())[:8],
                name=name,
                recording=recording,
                scheduled_dt=scheduled_dt,
                repeat=repeat,
                active=True,
                description=description,
            )
            self._alerts.append(alert)
            self._save()
        return alert

    def remove_alert(self, alert_id: str) -> bool:
        with self._lock:
            before = len(self._alerts)
            self._alerts = [a for a in self._alerts if a.id != alert_id]
            changed = len(self._alerts) < before
            if changed:
                self._save()
        return changed

    def toggle_alert(self, alert_id: str) -> Optional[bool]:
        with self._lock:
            for a in self._alerts:
                if a.id == alert_id:
                    a.active = not a.active
                    self._save()
                    return a.active
        return None

    def get_alerts(self) -> list:
        with self._lock:
            return list(self._alerts)

    def update_alert(self, alert_id: str, **kwargs) -> bool:
        with self._lock:
            for a in self._alerts:
                if a.id == alert_id:
                    for k, v in kwargs.items():
                        if hasattr(a, k):
                            setattr(a, k, v)
                    self._save()
                    return True
        return False

    # ──────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────

    def _load(self):
        if not os.path.exists(self.alerts_file):
            return
        try:
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._alerts = [Alert.from_dict(d) for d in data]
        except Exception:
            self._alerts = []

    def _save(self):
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump([a.to_dict() for a in self._alerts], f, indent=2)
        except Exception:
            pass

    # ──────────────────────────────────────────
    # Hilo de verificación
    # ──────────────────────────────────────────

    def start(self):
        """Arranca el hilo daemon que verifica alertas cada 30s."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _check_loop(self):
        while not self._stop_event.is_set():
            self._check_alerts()
            self._stop_event.wait(1)   # revisar cada segundo para precisión

    def _check_alerts(self):
        now = datetime.now()
        current_minute_key = (now.year, now.month, now.day, now.hour, now.minute)
        
        # Limpiar el set si cambió el minuto
        if hasattr(self, '_last_minute_key') and self._last_minute_key != current_minute_key:
            self._triggered_this_minute.clear()
        self._last_minute_key = current_minute_key
        
        triggered = []
        with self._lock:
            for alert in self._alerts:
                alert_key = f"{alert.id}_{current_minute_key}"
                if alert.is_due(now) and alert_key not in self._triggered_this_minute:
                    triggered.append(alert)
                    self._triggered_this_minute.add(alert_key)
                    alert.next_occurrence()
            if triggered:
                self._save()

        for alert in triggered:
            if self.on_trigger:
                try:
                    self.on_trigger(alert)
                except Exception:
                    pass
