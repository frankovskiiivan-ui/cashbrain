"""
Модуль вывода и выбора программ поддержки.

Показывает пользователю подобранные программы, разделяя их на:
- федеральные (доступны всем регионам),
- региональные (только для конкретного региона).

Позволяет выбрать программы для дальнейшего расчёта.
"""

# bot/handlers/programs.py

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context.state_machine import State
from maxapi.context import MemoryContext
from maxapi.filters.callback_payload import CallbackPayload

from bot.keyboards import get_programs_keyboard, get_budget_keyboard

logger = logging.getLogger(__name__)


class ProgramsForm(State):
    """Состояния для модуля выбора программ."""
    waiting_for_program_selection = State()
    finished = State()


def split_programs_by_scope(programs: list, region: str) -> tuple[list, list]:
    """Разделяет программы на федеральные и региональные."""
    federal = []
    regional = []

    for p in programs:
        regions = p.get("region", ["все"])
        if "все" in regions:
            federal.append(p)
        else:
            regional.append(p)

    return federal, regional


def format_programs_list(programs: list, region: str) -> str:
    """Формирует текст со списком программ (без финальной подсказки)."""
    federal, regional = split_programs_by_scope(programs, region)

    text = f"✅ **Найдено программ: {len(programs)}**\n"
    text += f"   • 🇷🇺 Федеральных: {len(federal)}\n"
    text += f"   • 📍 Региональных: {len(regional)}\n\n"

    if not regional:
        text += (
            f"⚠️ _Для региона **{region}** в базе пока нет региональных программ. "
            f"Показаны только федеральные меры поддержки._\n\n"
        )

    if federal:
        text += "**🇷🇺 Федеральные программы:**\n\n"
        for i, p in enumerate(federal, 1):
            text += f"**{i}. {p['name']}**\n"
            text += f"   💰 До {p['amount_max']:,.0f} ₽\n"
            if p.get("interest_rate"):
                text += f"   📉 Ставка: {p['interest_rate']}\n"
            text += f"   🔗 [Источник]({p['source_url']})\n\n"

    if regional:
        text += f"**📍 Региональные программы ({region}):**\n\n"
        for i, p in enumerate(regional, 1):
            text += f"**{i}. {p['name']}**\n"
            text += f"   💰 До {p['amount_max']:,.0f} ₽\n"
            if p.get("interest_rate"):
                text += f"   📉 Ставка: {p['interest_rate']}\n"
            text += f"   🔗 [Источник]({p['source_url']})\n\n"

    # 👇 Убираем текстовую подсказку — её заменят кнопки
    # text += "Напишите «рассчитать»..." — УДАЛЕНО

    return text


def register_programs_handlers(dp: Dispatcher):

    # ─────────────────────────────────────────────────────────
    # Обработка текстовых команд (на случай, если пользователь пишет вручную)
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text, state=ProgramsForm.waiting_for_program_selection)
    async def process_program_action(event: MessageCreated, context: MemoryContext):
        text = event.message.body.text.strip().lower()

        if text in ("рассчитать", "расчёт", "расчет"):
            await _handle_calculate(event.message, context)
            return

        if text == "бюджет":
            await _handle_budget(event.message, context)
            return

        await event.message.answer(
            "Выберите действие с помощью кнопок ниже 👇",
            attachments=[get_programs_keyboard()],
        )

    # ─────────────────────────────────────────────────────────
    # Обработка нажатий на кнопки
    # ─────────────────────────────────────────────────────────
    @dp.message_callback(F.callback.payload == "programs:calculate")
    async def on_calculate(callback: MessageCallback, context: MemoryContext):
        await callback.answer()  # убираем «часики» на кнопке
        await _handle_calculate(callback.message, context)

    @dp.message_callback(F.callback.payload == "programs:calculate")
    async def on_budget(callback: MessageCallback, context: MemoryContext):
        await callback.answer()
        await _handle_budget(callback.message, context)


# ─────────────────────────────────────────────────────────────
# Вспомогательные функции для обработки действий
# ─────────────────────────────────────────────────────────────
async def _handle_calculate(message, context: MemoryContext):
    """Логика расчёта дохода."""
    from core.calculator import (
        calculate_all_scenarios,
        calculate_by_program,
        format_scenarios_report,
        format_programs_rating,
    )

    user_data = await context.get_data()
    programs = user_data.get("found_programs", [])

    profile = {
        "region": user_data.get("region"),
        "industry": user_data.get("industry"),
        "target_revenue": user_data.get("target_revenue", 0),
        "initial_capital": user_data.get("capital", 0),
    }

    marketing_budget = user_data.get("marketing_budget", 0)

    scenarios = calculate_all_scenarios(profile, programs, marketing_budget)
    by_program = calculate_by_program(profile, programs, marketing_budget, "realistic")

    report = format_scenarios_report(scenarios)
    report += format_programs_rating(by_program)

    # Сохраняем общую сумму финансирования для бюджета
    await context.update_data(total_funding=scenarios["realistic"]["total_funding"])

    # 👇 Убираем текстовую подсказку, добавляем клавиатуру
    await message.answer(
        report,
        attachments=[get_budget_keyboard()],  # 👈 кнопки выбора бюджета
    )
    await context.set_state(ProgramsForm.finished)


async def _handle_budget(message, context: MemoryContext):
    """Логика перехода к распределению бюджета."""
    from bot.handlers.budget import format_budget_report, BudgetForm

    user_data = await context.get_data()
    total_funding = user_data.get("total_funding", 0)

    if total_funding <= 0:
        await message.answer(
            "⚠️ Сначала нужно рассчитать доход. Нажмите **«Рассчитать доход»**.",
            attachments=[get_programs_keyboard()],
        )
        return

    report = format_budget_report(total_funding)

    # 👇 Добавляем клавиатуру для выбора сценария бюджета
    await message.answer(
        report,
        attachments=[get_budget_keyboard()], # 👈 кнопки бюджета
    )
    await context.set_state(BudgetForm.waiting_for_budget_choice)