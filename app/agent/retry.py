import logging
from functools import wraps
from typing import Callable, Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)

logger = logging.getLogger(__name__)


def with_llm_retry(max_attempts: int = 3, initial_wait: float = 1.0, max_wait: float = 10.0):
    """
    Декоратор для автоматических повторных попыток при вызовах LLM.

    Args:
        max_attempts: Максимальное число попыток (по умолчанию 3)
        initial_wait: Начальная задержка в секундах (по умолчанию 1.0)
        max_wait: Максимальная задержка в секундах (по умолчанию 10.0)

    Повторяет при:
    - ConnectionError — сетевые ошибки
    - TimeoutError — таймауты
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=initial_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError)),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _retryable(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return _retryable(*args, **kwargs)
            except RetryError as e:
                logger.error(f"LLM call failed after {max_attempts} retries: {e.last_attempt.exception()}")
                return {
                    "category": "other",
                    "error": "classification_failed: max retries exceeded",
                    "reasoning": "Ошибка классификации, использован дефолт"
                }
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {
                    "category": "other",
                    "error": f"classification_failed: {str(e)}",
                    "reasoning": "Ошибка классификации, использован дефолт"
                }
        return wrapper
    return decorator
