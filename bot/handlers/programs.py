# bot/handlers/programs.py

"""
Модуль вывода и выбора программ поддержки.
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCallback
from maxapi.context.state_machine import State
from maxapi.context import MemoryContext

from bot.keyboards import (
    get_programs_keyboard,
    get_programs_choice_keyboard,
    get_budget_keyboard,
)
from core.rent import calculate_rent

logger = logging.getLogger(__name__)


class ProgramsForm(State):
    waiting_for_program_selection = State()
    finished = State()


def split_programs_by_scope(programs: list, region: str) -> tuple[list, list]:
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

    text += "👇 **Выберите программы кнопками ниже**"
    return text


def register_programs_handlers(dp: Dispatcher):

    # ─── Выбор программы кнопкой ───
    @dp.message_callback(F.callback.payload.startswith("programs:select:"))
    async def on_program_select(event: MessageCallback, context: MemoryContext):
        await event.answer()

        token = event.callback.payload.split(":", 2)[2]
        user_data = await context.get_data()
        programs = user_data.get("found_programs", [])

        if token == "all":
            selected = programs
        else:
            try:
                idx = int(token)
                selected = [programs[idx]]
            except (ValueError, IndexError):
                await event.message.answer("⚠️ Программа не найдена.")
                return

        await context.update_data(selected_programs=selected)

        total = sum(p["amount_max"] for p in selected)
        text = (
            f"✅ **Выбрано программ: {len(selected)}**\n"
            f"💰 Общая сумма: **{total:,.0f} ₽**\n\n"
        )
        for p in selected:
            text += f"• {p['name']} — до {p['amount_max']:,.0f} ₽\n"

        text += "\nНажмите **«Рассчитать доход»**, чтобы продолжить."

        await event.message.answer(
            text,
            attachments=[get_programs_keyboard()],
        )

    # ─── Расчёт дохода ───
    @dp.message_callback(F.callback.payload == "programs:calculate")
    async def on_calculate(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _handle_calculate(event.message, context)

    # ─── Переход к бюджету ───
    @dp.message_callback(F.callback.payload == "programs:budget")
    async def on_budget(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await _handle_budget(event.message, context)


async def _handle_calculate(message, context: MemoryContext):
    from core.calculator import (
        calculate_all_scenarios,
        calculate_by_program,
        format_scenarios_report,
        format_programs_rating,
    )

    user_data = await context.get_data()

    programs = user_data.get("selected_programs")
    if not programs:
        programs = user_data.get("found_programs", [])

    profile = {
        "region": user_data.get("region"),
        "industry": user_data.get("industry"),
        "target_revenue": user_data.get("target_revenue", 0),
        "initial_capital": user_data.get("capital", 0),
    }

    rent_data = calculate_rent(
        region=profile["region"],
        city=user_data.get("city", profile["region"]),
        area_sqm=60,
        months=1,
        land_type="городская",
    )
    rent_monthly = rent_data["monthly_cost"]

    marketing_budget = user_data.get("marketing_budget", 0)

    scenarios = calculate_all_scenarios(
        profile, programs, marketing_budget, rent_monthly
    )
    by_program = calculate_by_program(
        profile, programs, marketing_budget, rent_monthly, "realistic"
    )

    report = format_scenarios_report(scenarios)
    report += format_programs_rating(by_program)

    await context.update_data(
        total_funding=scenarios["realistic"]["total_funding"],
        rent_monthly=rent_monthly,
    )

    await message.answer(
        report,
        attachments=[get_budget_keyboard()],
    )
    await context.set_state(ProgramsForm.finished)


async def _handle_budget(message, context: MemoryContext):
    from core.budget import format_budget_report

    user_data = await context.get_data()
    total_funding = user_data.get("total_funding", 0)

    if total_funding <= 0:
        await message.answer(
            "⚠️ Сначала нужно рассчитать доход. Нажмите **«Рассчитать доход»**.",
            attachments=[get_programs_keyboard()],
        )
        return

    report = format_budget_report(total_funding)

    await message.answer(
        report,
        attachments=[get_budget_keyboard()],
    )
    await context.set_state(ProgramsForm.finished)