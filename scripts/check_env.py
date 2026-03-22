"""
Скрипт проверки базовой готовности окружения.
Запуск: python scripts/check_env.py

Проверяет:
- Наличие виртуального окружения
- Установку ключевых пакетов
- Загрузку конфигурации из .env
"""
import sys
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_venv():
    """Проверка активации виртуального окружения."""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Виртуальное окружение не активировано")
        print("   Активируйте: source .venv/bin/activate")
        return False
    print("✅ Виртуальное окружение: активно")
    return True


def check_packages():
    """Проверка установки ключевых пакетов."""
    required = ["fastapi", "langgraph", "sqlalchemy", "pydantic"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"❌ Не установлены пакеты: {missing}")
        print("   Выполните: pip install -r requirements.txt")
        return False

    print(f"✅ Зависимости: установлены ({len(required)} пакетов)")
    return True


def check_config():
    """Проверка загрузки конфигурации."""
    try:
        from app.config import get_settings
        settings = get_settings()

        # Проверка обязательных полей
        if not settings.SECRET_KEY or settings.SECRET_KEY == "change-me-in-prod":
            print("⚠️  SECRET_KEY не настроен (используется дефолт)")

        print(f"✅ Конфигурация: загружена (режим: {settings.APP_ENV})")
        return True

    except Exception as e:
        print(f"❌ Конфигурация: ошибка загрузки — {e}")
        return False


def main():
    print("🔍 Проверка окружения...\n")

    checks = [
        check_venv(),
        check_packages(),
        check_config(),
    ]

    print()
    if all(checks):
        print("🎉 Окружение готово к разработке!")
        return 0
    else:
        print("⚠️  Исправьте предупреждения перед продолжением")
        return 1


if __name__ == "__main__":
    sys.exit(main())
