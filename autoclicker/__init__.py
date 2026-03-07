"""
Autoclicker - Grabador y reproductor de eventos de mouse y teclado
"""

__version__ = "2.0.0"
__author__ = "Alvaro-San-Cav"

from .recorder import MouseRecorder
from .scheduler import AlertManager

__all__ = ['MouseRecorder', 'AlertManager']
