from maxapi import Dispatcher
from maxapi.filters.command import CommandStart
from maxapi.types import MessageCreated
from maxapi.context import MemoryContext
from bot.handlers.profile import ProfileForm


def register_start_handlers(dp: Dispatcher):

    @dp.message_created(CommandStart())
    async def start(event: MessageCreated, context: MemoryContext):
        await context.set_state(ProfileForm.waiting_for_industry)
        await event.message.answer(
            "👋 Здравствуйте! Я — CashBrain.\n\n"
            "Помогу подобрать меры поддержки для вашего бизнеса.\n\n"
            "**Шаг 1 из 4:** В какой сфере вы работаете?\n"
            "Например: «кофейня», «IT-услуги», «производство»."
        )
