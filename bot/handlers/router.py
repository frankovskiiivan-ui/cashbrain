# bot/handlers/router.py

"""
Единый роутер текстовых сообщений.

maxapi вызывает только первый подходящий хендлер и останавливается.
Поэтому вместо 8 конкурирующих хендлеров на F.message.body.text
у нас один, который смотрит на текущий state и делегирует
в нужную функцию.
"""

import logging
from maxapi import Dispatcher, F
from maxapi.types import MessageCreated
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

logger = logging.getLogger(__name__)


def register_text_router(dp: Dispatcher):

    @dp.message_created(F.message.body.text)
    async def route_text(event: MessageCreated, context: MemoryContext):
        state = await context.get_state()

        # ─── Профиль ИП ───
        if state == ProfileForm.waiting_for_industry:
            await handle_industry(event, context)
        elif state == ProfileForm.waiting_for_region:
            await handle_region(event, context)
        elif state == ProfileForm.waiting_for_capital:
            await handle_capital(event, context)
        elif state == ProfileForm.waiting_for_target_revenue:
            await handle_target_revenue(event, context)

        # ─── Блогеры ───
        elif state == BloggersForm.waiting_for_topic:
            await handle_topic_text(event, context)
        elif state == BloggersForm.waiting_for_min_subs:
            await handle_min_subs(event, context)
        elif state == BloggersForm.waiting_for_max_subs:
            await handle_max_subs(event, context)
        elif state == BloggersForm.waiting_for_ads_filter:
            await handle_ads_text(event, context)

        # Иначе — игнорируем (пользователь нажимает кнопки)