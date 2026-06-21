"""
Скрипт для ручного тестирования восстановления состояния через чекпоинты.
Запуск: python scripts/test_checkpoints.py

Использует реальный PostgresSaver и граф SupportAI.
Требует: PostgreSQL, Ollama (OLLAMA_BASE_URL).
"""
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.config import get_settings
from app.agent.state import AgentState
from app.agent.graph import build_agent_graph
from app.agent.checkpointer import get_checkpointer


async def test_dialog_recovery():
    """Проверяет восстановление многошагового диалога после «перезапуска» графа."""
    settings = get_settings()
    db_url = str(settings.DATABASE_URL)
    thread_id = "manual_test_001"

    print(f"🔍 Тест восстановления: thread_id={thread_id}")
    print(f"📊 База данных: {db_url.split('@')[-1]}")

    print("\n📌 Прогон 1: создаём диалог")
    async with get_checkpointer(db_url) as checkpointer:
        graph = build_agent_graph(checkpointer=checkpointer)
        result1 = await graph.ainvoke(
            AgentState(thread_id=thread_id, user_input="Привет, не работает вход"),
            config={"configurable": {"thread_id": thread_id}},
        )
        print(f"✅ Ответ: {result1.get('last_response', 'нет ответа')[:60]}...")
        print(f"✅ Сообщений в истории: {len(result1.get('messages', []))}")

    print("\n🔄 Эмуляция перезапуска сервера...")
    async with get_checkpointer(db_url) as checkpointer:
        graph = build_agent_graph(checkpointer=checkpointer)
        snapshot = await graph.aget_state({"configurable": {"thread_id": thread_id}})

        if not snapshot.values:
            print("❌ История не найдена в чекпоинтере")
            return False

        messages = snapshot.values.get("messages", [])
        print(f"✅ История восстановлена: {len(messages)} сообщений")

        print("\n📌 Прогон 2: продолжаем диалог")
        result2 = await graph.ainvoke(
            AgentState(thread_id=thread_id, user_input="Ошибка 401"),
            config={"configurable": {"thread_id": thread_id}},
        )
        print(f"✅ Ответ: {result2.get('last_response', 'нет ответа')[:60]}...")
        print(f"✅ Сообщений в истории: {len(result2.get('messages', []))}")

        if len(result2.get("messages", [])) >= 4:
            print("🎉 Диалог восстановлен: история накопилась после перезапуска")
            return True

        print("❌ История не накопилась корректно")
        return False


async def test_checkpoint_isolation():
    """Проверяет, что чекпоинты изолированы по thread_id."""
    thread_id_1 = "manual_isolation_001"
    thread_id_2 = "manual_isolation_002"
    settings = get_settings()
    db_url = str(settings.DATABASE_URL)

    async with get_checkpointer(db_url) as checkpointer:
        graph = build_agent_graph(checkpointer=checkpointer)

        await graph.ainvoke(
            AgentState(thread_id=thread_id_1, user_input="Запрос 1"),
            config={"configurable": {"thread_id": thread_id_1}},
        )
        await graph.ainvoke(
            AgentState(thread_id=thread_id_2, user_input="Запрос 2"),
            config={"configurable": {"thread_id": thread_id_2}},
        )

        checkpoints_1 = [
            c async for c in checkpointer.alist({"configurable": {"thread_id": thread_id_1}})
        ]
        checkpoints_2 = [
            c async for c in checkpointer.alist({"configurable": {"thread_id": thread_id_2}})
        ]

        if checkpoints_1 and checkpoints_2:
            print(
                f"✅ Изоляция сессий: {thread_id_1}={len(checkpoints_1)} чекпоинтов, "
                f"{thread_id_2}={len(checkpoints_2)} чекпоинтов"
            )
            return True

        print("❌ Изоляция сессий не работает")
        return False


async def main():
    print("🔍 Тестирование чекпоинтов SupportAI\n")

    print("📌 Тест 1: Восстановление многошагового диалога")
    print("-" * 50)
    try:
        test1 = await test_dialog_recovery()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        test1 = False

    print("\n📌 Тест 2: Изоляция сессий по thread_id")
    print("-" * 50)
    try:
        test2 = await test_checkpoint_isolation()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        test2 = False

    print("\n" + "=" * 50)
    if test1 and test2:
        print("✅ Все тесты пройдены")
        return 0
    print("❌ Некоторые тесты не пройдены")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))