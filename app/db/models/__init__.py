"""
Центральный импорт всех моделей.

Импорт этого модуля гарантирует, что все модели зарегистрированы
в метаданных Base до начала работы с БД.
"""

from .ticket import Ticket, TicketPriority, TicketStatus
from .history import TicketHistory
from .checkpoint import Checkpoint

# Экспортируем для удобства
__all__ = [
    "Ticket",
    "TicketPriority",
    "TicketStatus",
    "TicketHistory",
    "Checkpoint"
]