"""
Модуль распределения бюджета.

Показывает пользователю, как распределить привлечённые средства
между статьями расходов: оборудование, маркетинг, аренда, резерв.

Предлагает три сценария: осторожный, сбалансированный, агрессивный.
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCreated
from maxapi.context import State


from maxapi.context import MemoryContext
from bot.keyboards import get_budget_keyboard

from core.budget import (
    calculate_budget_allocation,
    format_budget_report,
    BUDGET_SCENARIOS,
)


logger = logging.getLogger(__name__)


class BudgetForm(State):
    """Состояния для модуля распределения бюджета."""
    waiting_for_budget_choice = State()
    finished = State()


# ─────────────────────────────────────────────────────────────
# Сценарии распределения бюджета (в процентах от общей суммы)
# ─────────────────────────────────────────────────────────────
BUDGET_SCENARIOS = {
    "cautious": {
        "label": "🟢 Осторожный",
        "description": "Минимум риска, плавный рост",
        "allocation": {
            "equipment": 0.50,   # 50% — оборудование и основные средства
            "marketing": 0.15,   # 15% — маркетинг
            "rent": 0.20,        # 20% — аренда и операционные расходы
            "reserve": 0.15,     # 15% — резервный фонд
        },
    },
    "balanced": {
        "label": "🟡 Сбалансированный",
        "description": "Оптимальное соотношение риска и роста",
        "allocation": {
            "equipment": 0.40,
            "marketing": 0.30,   # больше на маркетинг — быстрее рост
            "rent": 0.20,
            "reserve": 0.10,
        },
    },
    "aggressive": {
        "label": "🔴 Агрессивный",
        "description": "Максимум вложений в рост",
        "allocation": {
            "equipment": 0.30,
            "marketing": 0.45,   # почти половина — в рекламу
            "rent": 0.15,
            "reserve": 0.10,
        },
    },
}


def calculate_budget_allocation(total_funding: float, scenario: str) -> dict:
    """
    Считает распределение бюджета по статьям.

    :param total_funding: общая сумма привлечённых средств
    :param scenario: cautious / balanced / aggressive
    :return: словарь с суммами по статьям
    """
    scenario_data = BUDGET_SCENARIOS.get(scenario, BUDGET_SCENARIOS["balanced"])
    allocation = scenario_data["allocation"]

    result = {
        "scenario": scenario,
        "label": scenario_data["label"],
        "description": scenario_data["description"],
        "total": round(total_funding, 2),
    }

    for category, ratio in allocation.items():
        result[category] = round(total_funding * ratio, 2)

    return result


def format_budget_report(total_funding: float) -> str:
    """
    Формирует текст с тремя сценариями распределения бюджета.
    """
    text = f"💰 **Распределение бюджета: {total_funding:,.0f} ₽**\n\n"

    for scenario_key in ["cautious", "balanced", "aggressive"]:
        s = calculate_budget_allocation(total_funding, scenario_key)
        text += f"**{s['label']}** — _{s['description']}_\n"
        text += f"   🏭 Оборудование: {s['equipment']:,.0f} ₽\n"
        text += f"   📢 Маркетинг: {s['marketing']:,.0f} ₽\n"
        text += f"   🏠 Аренда: {s['rent']:,.0f} ₽\n"
        text += f"   🛡 Резерв: {s['reserve']:,.0f} ₽\n\n"

    text += (
        "Напишите **«осторожный»**, **«сбалансированный»** или **«агрессивный»**, "
        "чтобы выбрать сценарий."
    )
    return text


def register_budget_handlers(dp: Dispatcher):

    @dp.message_created(F.message.body.text, state=BudgetForm.waiting_for_budget_choice)
    async def process_budget_choice(event: MessageCreated, context: MemoryContext):
        text = event.message.body.text.strip().lower()

        mapping = {
            "осторожный": "cautious",
            "сбалансированный": "balanced",
            "агрессивный": "aggressive",
        }

        if text not in mapping:
            await event.message.answer(
                "Пожалуйста, выберите один из сценариев:\n"
                "**«осторожный»**, **«сбалансированный»** или **«агрессивный»**."
            )
            return

        scenario_key = mapping[text]
        user_data = await context.get_data()
        total_funding = user_data.get("total_funding", 0)

        if total_funding <= 0:
            await event.message.answer(
                "⚠️ Не удалось определить сумму финансирования. "
                "Пройдите подбор программ заново."
            )
            await context.set_state(BudgetForm.finished)
            return

        allocation = calculate_budget_allocation(total_funding, scenario_key)

        # Сохраняем выбранный сценарий — он понадобится для модуля блогеров
        await context.update_data(
            budget_scenario=scenario_key,
            marketing_budget=allocation["marketing"],
            budget_allocation=allocation,
        )

        text = (
            f"✅ Выбран сценарий: **{allocation['label']}**\n\n"
            f"📊 **Распределение {allocation['total']:,.0f} ₽:**\n"
            f"   🏭 Оборудование: {allocation['equipment']:,.0f} ₽\n"
            f"   📢 Маркетинг: {allocation['marketing']:,.0f} ₽\n"
            f"   🏠 Аренда: {allocation['rent']:,.0f} ₽\n"
            f"   🛡 Резерв: {allocation['reserve']:,.0f} ₽\n\n"
            f"Теперь можно перейти к подбору блогеров для маркетинга "
            f"с бюджетом **{allocation['marketing']:,.0f} ₽**."
        )

        await event.message.answer(text)
        await context.set_state(BudgetForm.finished)