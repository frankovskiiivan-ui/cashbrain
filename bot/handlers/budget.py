# bot/handlers/budget.py

"""
Модуль распределения бюджета.

Callback-хендлеры на кнопки:
- budget:cautious
- budget:balanced
- budget:aggressive
- budget:details
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCallback
from maxapi.context import MemoryContext

from bot.keyboards import (
    get_budget_keyboard,
    get_after_budget_keyboard,
    get_budget_details_keyboard,
)
from core.budget import (
    calculate_budget_allocation,
    format_budget_report,
    format_expenses_details,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Вспомогательная логика
# ─────────────────────────────────────────────────────────────
async def _apply_budget_choice(event: MessageCallback, context: MemoryContext, scenario_key: str):
    """Общая логика для трёх кнопок бюджета."""
    user_data = await context.get_data()
    total_funding = user_data.get("total_funding", 0)

    if total_funding <= 0:
        await event.message.answer(
            "⚠️ Не удалось определить сумму финансирования. "
            "Пройдите подбор программ заново.",
            attachments=[get_budget_keyboard()],
        )
        return

    allocation = calculate_budget_allocation(total_funding, scenario_key)

    # Сохраняем выбор — пригодится в модуле блогеров
    await context.update_data(
        budget_scenario=scenario_key,
        marketing_budget=allocation["marketing"],
        budget_allocation=allocation,
    )

    text = (
        f"✅ Выбран сценарий: {allocation['label']}\n"
        f"{allocation['description']}\n\n"
        f"Общая сумма: {allocation['total']:,.0f} ₽\n\n"
        f"🏭 Оборудование: {allocation['equipment']:,.0f} ₽\n"
        f"📢 Маркетинг: {allocation['marketing']:,.0f} ₽\n"
        f"🏠 Аренда: {allocation['rent']:,.0f} ₽\n"
        f"🛡 Резерв: {allocation['reserve']:,.0f} ₽\n\n"
        f"Хотите узнать, **на что именно** потратить эти деньги?"
    )

    await event.message.answer(
        text,
        attachments=[get_after_budget_keyboard()],
    )


async def _show_expenses_details(event: MessageCallback, context: MemoryContext):
    """Показывает детализацию расходов."""
    user_data = await context.get_data()

    industry = user_data.get("industry", "кофейня")
    allocation = user_data.get("budget_allocation", {})
    bloggers = user_data.get("found_bloggers", [])

    if not allocation:
        await event.message.answer(
            "⚠️ Сначала выберите сценарий бюджета.",
            attachments=[get_budget_keyboard()],
        )
        return

    text = format_expenses_details(
        industry=industry,
        equipment_budget=allocation.get("equipment", 0),
        rent_budget=allocation.get("rent", 0),
        marketing_budget=allocation.get("marketing", 0),
        bloggers=bloggers,
    )

    await event.message.answer(
        text,
        attachments=[get_budget_details_keyboard()],
    )


# ─────────────────────────────────────────────────────────────
# Регистрация хендлеров
# ─────────────────────────────────────────────────────────────
def register_budget_handlers(dp: Dispatcher):

    @dp.message_callback(F.callback.payload == "budget:cautious")
    async def on_cautious(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _apply_budget_choice(event, context, "cautious")

    @dp.message_callback(F.callback.payload == "budget:balanced")
    async def on_balanced(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _apply_budget_choice(event, context, "balanced")

    @dp.message_callback(F.callback.payload == "budget:aggressive")
    async def on_aggressive(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _apply_budget_choice(event, context, "aggressive")

    @dp.message_callback(F.callback.payload == "budget:details")
    async def on_details(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _show_expenses_details(event, context)