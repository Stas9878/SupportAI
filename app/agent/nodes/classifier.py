from app.agent.llm import llm
from app.agent.state import AgentState
from app.agent.retry import with_llm_retry


@with_llm_retry(max_attempts=3)
def classify_ticket(state: AgentState) -> dict:
    """Определяет категорию заявки с retry-логикой."""

    prompt = f"""Ты классификатор заявок в службу поддержки.
Определи категорию обращения пользователя.

Доступные категории:
- technical: проблемы с входом, функционалом, ошибками, багами
- billing: вопросы по оплате, тарифам, подпискам, возврату средств
- feature: предложения новых функций, улучшения существующих
- other: всё, что не подходит под вышеперечисленное

Отвечай ТОЛЬКО одним словом из списка: technical, billing, feature, other.
Не добавляй пояснений, кавычек или дополнительного текста.

Запрос пользователя:
{state.user_input}

Категория:"""
    response = llm.invoke(prompt)
    category = response.content.strip().lower()

    valid_categories = {"technical", "billing", "feature", "other"}
    if category not in valid_categories:
        category = "other"

    return AgentState(
        thread_id=state.thread_id,
        user_input=state.user_input,
        category=category,
        reasoning=f"Классификация: {category}"
    ).to_dict()