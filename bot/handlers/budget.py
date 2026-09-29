"""
Модуль распределения бюджета.

Callback-хендлеры на кнопки:
- budget:cautious
- budget:balanced
- budget:aggressive
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCallback
from maxapi.context import MemoryContext

from bot.keyboards import get_after_budget_keyboard
from core.budget import (
    calculate_budget_allocation,
    format_budget_report,
)


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Вспомогательная логика
# ─────────────────────────────────────────────────────────────

async def _apply_budget_choice(event: MessageCallback, context: MemoryContext, scenario_key: str):
    """Общая логика для всех трёх кнопок бюджета."""
    user_data = await context.get_data()
    total_funding = user_data.get("total_funding", 0)

    if total_funding <= 0:
        await event.message.answer(
            "⚠️ Не удалось определить сумму финансирования. "
            "Пройдите подбор программ заново.",
            attachments=[get_after_budget_keyboard()],
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
        f"Теперь можно найти блогеров для рекламы "
        f"с бюджетом {allocation['marketing']:,.0f} ₽."
    )

    await event.message.answer(
        text,
        attachments=[get_after_budget_keyboard()],
    )


# ─────────────────────────────────────────────────────────────
#  Регистрация хендлеров
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