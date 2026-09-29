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
        await context.clear()  # сбрасываем прошлый диалог
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "Шаг 1 из 4: В какой сфере вы работаете?\n"
            "Например: «кофейня», «IT-услуги», «производство»."
        )

    # ─── Кнопка «Найти блогера» ───
    @dp.message_callback(F.callback.payload == "menu:bloggers")
    async def menu_bloggers(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.clear()  # сбрасываем прошлый диалог
        from bot.handlers.bloggers import start_bloggers_flow
        await start_bloggers_flow(event, context)

    # ─── Кнопка «В главное меню» ───
    @dp.message_callback(F.callback.payload == "menu:main")
    async def menu_main(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.clear()
        await show_main_menu(event.message, context)