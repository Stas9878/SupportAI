import json
from app.agent.llm import llm
from app.agent.state import AgentState
from app.agent.retry import with_llm_retry


@with_llm_retry(max_attempts=3)
def tag_ticket(state: AgentState) -> dict:
    """Назначает теги заявке с retry и валидацией JSON."""

    prompt = f"""Ты назначаешь теги заявке в службу поддержки.
Выбери 0-3 наиболее релевантных тега из списка:

login, password, access, payment, billing, subscription,
refund, bug, error, crash, feature, improvement, ui, ux,
api, integration, mobile, web, documentation

Категория: {state.category or "other"}
Приоритет: {state.priority or "medium"}
Текст: {state.user_input}

Отвечай ТОЛЬКО валидным JSON-массивом строк: ["login", "bug"] или []

Теги:"""

    # Декоратор уже обработал retry — здесь только успех или fallback dict
    response = llm.invoke(prompt)

    # Проверка на fallback от декоратора
    if response is None or isinstance(response, dict) and "error" in response:
        return AgentState(
            thread_id=state.thread_id,
            user_input=state.user_input,
            category=state.category,
            priority=state.priority,
            tags=None,
            error=f"{state.error or ''} tagging_failed: max retries exceeded".strip(),
            reasoning=f"{state.reasoning or ''} | Ошибка теггирования".strip(" |")
        ).to_dict()

    try:
        content = response.content.strip()
        tags = json.loads(content)

        # Валидация структуры JSON
        if not isinstance(tags, list) or len(tags) > 3:
            tags = []
        elif not all(isinstance(t, str) for t in tags):
            tags = []

        # Валидация значений
        valid_tags = {
            "login", "password", "access", "payment", "billing",
            "bug", "error", "crash", "feature", "ui", "api"
        }
        tags = [t for t in tags if t in valid_tags][:3]

        return AgentState(
            thread_id=state.thread_id,
            user_input=state.user_input,
            category=state.category,
            priority=state.priority,
            tags=tags if tags else None,
            reasoning=f"{state.reasoning or ''} | Теги: {tags}".strip(" |")
        ).to_dict()

    except json.JSONDecodeError as e:
        return AgentState(
            thread_id=state.thread_id,
            user_input=state.user_input,
            category=state.category,
            priority=state.priority,
            tags=None,
            error=f"{state.error or ''} tagging_failed: {str(e)}".strip(),
            reasoning=f"{state.reasoning or ''} | Ошибка теггирования".strip(" |")
        ).to_dict()
