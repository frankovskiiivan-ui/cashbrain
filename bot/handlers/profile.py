"""
Модуль сбора профиля ИП.

Проводит пользователя по 4 шагам:
1. Отрасль
2. Регион
3. Начальный капитал
4. Цель по выручке

После сбора данных вызывает matcher.py для подбора программ
и передаёт управление в programs.py.
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCreated, State
from maxapi.context import MemoryContext

from core.matcher import find_matching_programs
from utils.validators import parse_amount, normalize_industry, normalize_region
from bot.keyboards import get_programs_keyboard

logger = logging.getLogger(__name__)


class ProfileForm(State):
    """Состояния для сбора профиля ИП."""
    waiting_for_industry = State()
    waiting_for_region = State()
    waiting_for_capital = State()
    waiting_for_target_revenue = State()
    finished = State()


def register_profile_handlers(dp: Dispatcher):

    # ─────────────────────────────────────────────────────────
    # Шаг 1: Отрасль
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text, state=ProfileForm.waiting_for_industry)
    async def process_industry(event: MessageCreated, context: MemoryContext):
        industry = normalize_industry(event.message.body.text)
        await context.update_data(industry=industry)
        await context.set_state(ProfileForm.waiting_for_region)
        await event.message.answer(
            "**Шаг 2 из 4:** В каком регионе вы ведёте деятельность?\n"
            "Например: «Нижегородская область», «Республика Татарстан»."
        )

    # ─────────────────────────────────────────────────────────
    # Шаг 2: Регион
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text, state=ProfileForm.waiting_for_region)
    async def process_region(event: MessageCreated, context: MemoryContext):
        region = normalize_region(event.message.body.text)
        await context.update_data(region=region)
        await context.set_state(ProfileForm.waiting_for_capital)
        await event.message.answer(
            "**Шаг 3 из 4:** Какой у вас начальный капитал?\n"
            "Напишите сумму в рублях, например: «500000»."
        )

    # ─────────────────────────────────────────────────────────
    # Шаг 3: Начальный капитал
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text, state=ProfileForm.waiting_for_capital)
    async def process_capital(event: MessageCreated, context: MemoryContext):
        capital = parse_amount(event.message.body.text)
        if capital is None:
            await event.message.answer(
                "Пожалуйста, напишите только число, например: «500000»."
            )
            return

        await context.update_data(capital=capital)
        await context.set_state(ProfileForm.waiting_for_target_revenue)
        await event.message.answer(
            "**Шаг 4 из 4:** Какую ежемесячную выручку вы хотите получать?\n\n"
            "• Если вы уже работаете — укажите текущую.\n"
            "• Если только планируете — укажите цель.\n\n"
            "Напишите сумму в рублях, например: «150000»."
        )

    # ─────────────────────────────────────────────────────────
    # Шаг 4: Цель по выручке + подбор программ
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text, state=ProfileForm.waiting_for_target_revenue)
    async def process_target_revenue(event: MessageCreated, context: MemoryContext):
        revenue = parse_amount(event.message.body.text)
        if revenue is None:
            await event.message.answer("Пожалуйста, напишите только число.")
            return

        await context.update_data(target_revenue=revenue)
        user_data = await context.get_data()

        profile = {
            "region": user_data.get("region"),
            "industry": user_data.get("industry"),
            "target_revenue": revenue,
            "initial_capital": user_data.get("capital", 0),
        }

        await event.message.answer("🔎 Подбираю подходящие меры поддержки...")

        # ─── Вызов «мозга» ───
        try:
            programs = find_matching_programs(profile)
        except Exception as e:
            logger.error(f"Ошибка подбора программ: {e}")
            await event.message.answer(
                "⚠️ Произошла ошибка при подборе. Попробуйте позже."
            )
            await context.set_state(ProfileForm.finished)
            return

        # ─── Если ничего не найдено ───
        if not programs:
            await event.message.answer(
                "К сожалению, по вашим параметрам не найдено подходящих программ.\n"
                "Попробуйте изменить регион или отрасль."
            )
            await context.set_state(ProfileForm.finished)
            return

        # ─── Сохраняем найденные программы ───
        await context.update_data(found_programs=programs)

        # ─── Передаём управление в programs.py ───
        from bot.handlers.programs import format_programs_list, ProgramsForm

        report = format_programs_list(programs, profile["region"])
        await event.message.answer(
            report,
            keyboard=get_programs_keyboard()   # 👈 клавиатура
        )
        await context.set_state(ProgramsForm.waiting_for_program_selection)



        