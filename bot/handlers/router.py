

"""
Единый роутер текстовых сообщений + callback'ов выбора отрасли/региона.
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext

from bot.handlers.profile import (
    ProfileForm,
    handle_industry,
    handle_region,
    handle_capital,
    handle_target_revenue,
)
from bot.handlers.bloggers import (
    BloggersForm,
    handle_topic_text,
    handle_min_subs,
    handle_max_subs,
    handle_ads_text,
)
from bot.keyboards import get_region_keyboard

logger = logging.getLogger(__name__)


def register_text_router(dp: Dispatcher):

    # ─────────────────────────────────────────────────────────
    # Текстовые сообщения
    # ─────────────────────────────────────────────────────────
    @dp.message_created(F.message.body.text)
    async def route_text(event: MessageCreated, context: MemoryContext):
        state = await context.get_state()

        # Профиль ИП
        if state == ProfileForm.waiting_for_industry:
            await handle_industry(event, context)
        elif state == ProfileForm.waiting_for_region:
            await handle_region(event, context)
        elif state == ProfileForm.waiting_for_capital:
            await handle_capital(event, context)
        elif state == ProfileForm.waiting_for_target_revenue:
            await handle_target_revenue(event, context)

        # Блогеры
        elif state == BloggersForm.waiting_for_topic:
            await handle_topic_text(event, context)
        elif state == BloggersForm.waiting_for_min_subs:
            await handle_min_subs(event, context)
        elif state == BloggersForm.waiting_for_max_subs:
            await handle_max_subs(event, context)
        elif state == BloggersForm.waiting_for_ads_filter:
            await handle_ads_text(event, context)

    # ─────────────────────────────────────────────────────────
    # Callback: выбор отрасли кнопкой
    # ─────────────────────────────────────────────────────────
    @dp.message_callback(F.callback.payload.startswith("profile:industry:"))
    async def on_industry_button(event: MessageCallback, context: MemoryContext):
        await event.answer()
        industry = event.callback.payload.split(":", 2)[2]
        await context.update_data(industry=industry.lower())
        await context.set_state(ProfileForm.waiting_for_region)
        await event.message.answer(
            f"✅ Отрасль: {industry}\n\n"
            "**Шаг 2 из 4:** В каком регионе вы ведёте деятельность?\n"
            "Выберите кнопкой ниже или напишите текстом.",
            attachments=[get_region_keyboard()],
        )

    # ─────────────────────────────────────────────────────────
    # Callback: выбор региона кнопкой
    # ─────────────────────────────────────────────────────────
    @dp.message_callback(F.callback.payload.startswith("profile:region:"))
    async def on_region_button(event: MessageCallback, context: MemoryContext):
        await event.answer()
        token = event.callback.payload.split(":", 2)[2]

        if token == "manual":
            await event.message.answer(
                "Напишите регион текстом:\n"
                "Например: «Нижегородская область»."
            )
            return

        region = token.replace("_", " ")
        await context.update_data(region=region)
        await context.set_state(ProfileForm.waiting_for_capital)
        await event.message.answer(
            f"✅ Регион: {region}\n\n"
            "**Шаг 3 из 4:** Какой у вас начальный капитал?\n"
            "Напишите сумму в рублях, например: «500000»."
        )