"""
Unit-тесты на восстановление после сбоев.
Запуск: pytest tests/test_recovery.py -v
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agent.state import AgentState
from app.agent.graph import build_agent_graph
from app.agent.nodes.chat_handler import chat_handler


@pytest.fixture
def memory_checkpointer():
    """In-memory чекпоинтер для быстрых unit-тестов без PostgreSQL."""
    return InMemorySaver()


@pytest.fixture
def agent_graph(memory_checkpointer):
    """Скомпилированный граф с in-memory чекпоинтером."""
    return build_agent_graph(checkpointer=memory_checkpointer)


@pytest.fixture
def mock_db_session():
    """Async-сессия для saver в интеграционных сценариях графа."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


def _mock_llm_response(content: str):
    response = Mock()
    response.content = content
    return response


def _graph_config(thread_id: str, session=None):
    config = {"configurable": {"thread_id": thread_id}}
    if session is not None:
        config["configurable"]["session"] = session
    return config


class TestLLMFailureRecovery:
    """Тесты восстановления при сбоях LLM."""

    def test_chat_handler_retry_on_connection_error(self):
        call_count = 0

        def flaky_invoke(prompt: str):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network error")
            return _mock_llm_response("Здравствуйте! Чем могу помочь?")

        mock_llm = Mock()
        mock_llm.invoke = flaky_invoke

        with patch("app.agent.nodes.chat_handler.llm", mock_llm):
            result = chat_handler(AgentState(thread_id="t1", user_input="Привет"))

        assert call_count == 2
        assert result["last_response"] == "Здравствуйте! Чем могу помочь?"

    def test_chat_handler_fallback_on_retry_exhausted(self):
        mock_llm = Mock()
        mock_llm.invoke = Mock(side_effect=ConnectionError("Permanent error"))

        with patch("app.agent.nodes.chat_handler.llm", mock_llm):
            result = chat_handler(AgentState(thread_id="t1", user_input="Не работает вход"))

        assert "не могу сформировать ответ" in result["last_response"].lower()
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_chat_response_persisted_in_checkpointer(self, agent_graph):
        thread_id = "test_retry_checkpoint_001"
        config = _graph_config(thread_id)
        mock_llm = Mock(invoke=lambda _: _mock_llm_response("Здравствуйте!"))

        with patch("app.agent.nodes.chat_handler.llm", mock_llm), patch(
            "app.agent.nodes.classifier._classify_llm_call",
            return_value=_mock_llm_response("technical"),
        ), patch(
            "app.agent.nodes.prioritizer._prioritize_llm_call",
            return_value=_mock_llm_response("medium"),
        ):
            result = await agent_graph.ainvoke(
                AgentState(thread_id=thread_id, user_input="Привет"),
                config=config,
            )

        assert result.get("last_response") == "Здравствуйте!"
        snapshot = await agent_graph.aget_state(config)
        assert snapshot.values.get("last_response") == "Здравствуйте!"


class TestCheckpointRecovery:
    """Тесты восстановления состояния из чекпоинтера."""

    @pytest.mark.asyncio
    async def test_dialog_recovers_after_graph_recreate(
        self, memory_checkpointer, mock_db_session
    ):
        thread_id = "test_recovery_001"
        config = _graph_config(thread_id, session=mock_db_session)
        mock_ticket = Mock(id=10)

        with patch(
            "app.agent.nodes.chat_handler.llm",
            Mock(invoke=lambda _: _mock_llm_response("Проверьте логин и пароль.")),
        ), patch(
            "app.agent.nodes.classifier._classify_llm_call",
            return_value=_mock_llm_response("technical"),
        ), patch(
            "app.agent.nodes.prioritizer._prioritize_llm_call",
            return_value=_mock_llm_response("medium"),
        ), patch(
            "app.agent.nodes.saver.ticket_crud.create_ticket",
            new_callable=AsyncMock,
            return_value=mock_ticket,
        ), patch(
            "app.agent.nodes.saver.ticket_crud.add_ticket_history",
            new_callable=AsyncMock,
        ):
            graph_v1 = build_agent_graph(checkpointer=memory_checkpointer)
            result1 = await graph_v1.ainvoke(
                AgentState(thread_id=thread_id, user_input="Не могу войти"),
                config=config,
            )

        assert len(result1.get("messages", [])) == 2
        assert result1.get("ticket_id") == 10

        graph_v2 = build_agent_graph(checkpointer=memory_checkpointer)
        with patch(
            "app.agent.nodes.chat_handler.llm",
            Mock(invoke=lambda _: _mock_llm_response(
                "Ошибка 401 означает неверные учётные данные."
            )),
        ):
            result2 = await graph_v2.ainvoke(
                AgentState(thread_id=thread_id, user_input="Ошибка 401"),
                config=config,
            )

        messages = result2.get("messages", [])
        assert len(messages) == 4
        assert messages[0]["content"] == "Не могу войти"
        assert messages[2]["content"] == "Ошибка 401"

    @pytest.mark.asyncio
    async def test_hil_interrupt_recovers_after_confirmation(
        self, memory_checkpointer, mock_db_session
    ):
        thread_id = "test_hil_recovery_001"
        config = _graph_config(thread_id, session=mock_db_session)
        mock_ticket = Mock(id=42)

        with patch(
            "app.agent.nodes.chat_handler.llm",
            Mock(invoke=lambda _: _mock_llm_response("Понял. Опишите подробнее.")),
        ), patch(
            "app.agent.nodes.classifier._classify_llm_call",
            return_value=_mock_llm_response("technical"),
        ), patch(
            "app.agent.nodes.prioritizer._prioritize_llm_call",
            return_value=_mock_llm_response("high"),
        ), patch(
            "app.agent.nodes.saver.ticket_crud.create_ticket",
            new_callable=AsyncMock,
            return_value=mock_ticket,
        ), patch(
            "app.agent.nodes.saver.ticket_crud.add_ticket_history",
            new_callable=AsyncMock,
        ):
            graph_v1 = build_agent_graph(checkpointer=memory_checkpointer)
            result1 = await graph_v1.ainvoke(
                AgentState(thread_id=thread_id, user_input="Хочу удалить аккаунт"),
                config=config,
            )

            snapshot1 = await graph_v1.aget_state(config)
            assert snapshot1.interrupts
            assert result1.get("confirmed") is None

            graph_v2 = build_agent_graph(checkpointer=memory_checkpointer)
            result2 = await graph_v2.ainvoke(Command(resume="yes"), config=config)
            snapshot2 = await graph_v2.aget_state(config)

        assert result2.get("confirmed") is True
        assert result2.get("ticket_id") == 42


class TestIdempotentNodes:
    """Follow-up не перезапускает saver и не создаёт дубликат заявки."""

    @pytest.mark.asyncio
    async def test_follow_up_does_not_create_duplicate_ticket(
        self, memory_checkpointer, mock_db_session
    ):
        """
        Повторный ainvoke с тем же thread_id идёт в dialog_end,
        ticket_id из чекпоинтера сохраняется.
        """
        thread_id = "test_idempotent_001"
        config = _graph_config(thread_id, session=mock_db_session)
        mock_ticket = Mock(id=99)
        create_mock = AsyncMock(return_value=mock_ticket)

        with patch(
            "app.agent.nodes.chat_handler.llm",
            Mock(invoke=lambda _: _mock_llm_response("Понял.")),
        ), patch(
            "app.agent.nodes.classifier._classify_llm_call",
            return_value=_mock_llm_response("technical"),
        ), patch(
            "app.agent.nodes.prioritizer._prioritize_llm_call",
            return_value=_mock_llm_response("medium"),
        ), patch(
            "app.agent.nodes.saver.ticket_crud.create_ticket",
            create_mock,
        ), patch(
            "app.agent.nodes.saver.ticket_crud.add_ticket_history",
            new_callable=AsyncMock,
        ):
            graph = build_agent_graph(checkpointer=memory_checkpointer)
            result1 = await graph.ainvoke(
                AgentState(thread_id=thread_id, user_input="Тестовая заявка"),
                config=config,
            )

        ticket_id_1 = result1.get("ticket_id")
        assert ticket_id_1 == 99
        assert create_mock.call_count == 1

        with patch(
            "app.agent.nodes.chat_handler.llm",
            Mock(invoke=lambda _: _mock_llm_response("Уточнение принято.")),
        ):
            result2 = await graph.ainvoke(
                AgentState(thread_id=thread_id, user_input="Ещё вопрос"),
                config=config,
            )

        assert result2.get("ticket_id") == ticket_id_1
        assert create_mock.call_count == 1
