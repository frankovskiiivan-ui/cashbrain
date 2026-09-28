from maxapi import Dispatcher, F
from maxapi.filters.command import CommandStart
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context.state_machine import State
from maxapi.context import MemoryContext

from bot.handlers.profile import ProfileForm
from bot.keyboards import get_main_menu_keyboard


class MainMenuForm(State):
    waiting_for_choice = State()


def _menu_text() -> str:
    return (
        "👋 Здравствуйте! Я — CashBrain.\n\n"
        "Помогу с двумя задачами:\n\n"
        "1. 🏛 Подобрать госпрограмму поддержки для бизнеса\n"
        "2. 📢 Найти блогеров для рекламы\n\n"
        "Выберите действие кнопкой ниже 👇"
    )


async def show_main_menu(message, context: MemoryContext):
    """Показывает главное меню кнопками. Используется и из callback, и из /start."""
    await context.set_state(MainMenuForm.waiting_for_choice)
    await message.answer(
        _menu_text(),
        attachments=[get_main_menu_keyboard()],
    )


def register_start_handlers(dp: Dispatcher):

    # ─── /start ───
    @dp.message_created(CommandStart())
    async def start(event: MessageCreated, context: MemoryContext):
        await show_main_menu(event.message, context)

    # ─── Кнопка «Госпрограммы» ───
    @dp.message_callback(F.callback.payload == "menu:programs")
    async def menu_programs(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "**Шаг 1 из 4:** В какой сфере вы работаете?\n"
            "Например: «кофейня», «IT-услуги», «производство»."
        )

    # ─── Кнопка «Найти блогера» ───
    @dp.message_callback(F.callback.payload == "menu:bloggers")
    async def menu_bloggers(event: MessageCallback, context: MemoryContext):
        await event.answer()
        from bot.handlers.bloggers import start_bloggers_flow

        # start_bloggers_flow ожидает event с .message, поэтому передаём сам event
        await start_bloggers_flow(event, context)

    # # ─── Текстовый ввод 1/2 как fallback ───
    # @dp.message_created(F.message.body.text)
    # async def handle_menu_text(event: MessageCreated, context: MemoryContext):
    #     current_state = await context.get_state()
    #     if current_state != MainMenuForm.waiting_for_choice:
    #         return  # это сообщение не для нас
    #     text = event.message.body.text.strip()
    #     if text == "1":
    #         await context.set_state(ProfileForm.waiting_for_industry)
    #         await event.message.answer(
    #             "**Шаг 1 из 4:** В какой сфере вы работаете?\n"
    #             "Например: «кофейня», «IT-услуги», «производство»."
    #         )
    #     elif text == "2":
    #         from bot.handlers.bloggers import start_bloggers_flow
    #         await start_bloggers_flow(event, context)
    #     else:
    #         await event.message.answer(
    #             "Пожалуйста, выберите действие кнопкой или напишите 1/2.",
    #             attachments=[get_main_menu_keyboard()],
    #         )