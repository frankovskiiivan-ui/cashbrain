# bot/handlers/start.py

from maxapi import Dispatcher, F
from maxapi.filters.command import CommandStart
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext

from bot.handlers.profile import ProfileForm
from bot.keyboards import get_main_menu_keyboard


def register_start_handlers(dp: Dispatcher):

    @dp.message_created(CommandStart())
    async def start(event: MessageCreated, context: MemoryContext):
        await context.clear()
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "👋 Здравствуйте! Я — CashBrain.\n\n"
            "Помогу подобрать госпрограммы, распределить бюджет "
            "и рассчитать доход с учётом рекламы у блогеров.\n\n"
            "**Шаг 1 из 4:** В какой сфере вы работаете?\n"
            "Например: «кофейня», «IT-услуги», «производство»."
        )

    @dp.message_callback(F.callback.payload == "menu:programs")
    async def menu_programs(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.clear()
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "**Шаг 1 из 4:** В какой сфере вы работаете?\n"
            "Например: «кофейня», «IT-услуги», «производство»."
        )

    @dp.message_callback(F.callback.payload == "menu:main")
    async def menu_main(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.clear()
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "👋 Начинаем заново!\n\n"
            "**Шаг 1 из 4:** В какой сфере вы работаете?"
        )