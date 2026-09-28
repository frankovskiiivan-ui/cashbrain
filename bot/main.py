"""
Точка входа бота CashBrain.

Запускает polling, инициализирует БД, регистрирует все обработчики.
"""

import asyncio
import logging
from dotenv import load_dotenv
from maxapi import Bot, Dispatcher
from maxapi.types import BotCommand

from data.db import init_db
from data.loader import load_programs_from_json
from bot.handlers.start import register_start_handlers
#from bot.handlers.profile import register_profile_handlers
from bot.handlers.programs import register_programs_handlers
from bot.handlers.budget import register_budget_handlers
from bot.handlers.bloggers import register_bloggers_handlers

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# Создаём бота и диспетчер
bot = Bot()
dp = Dispatcher()

from bot.handlers.router import register_text_router
register_start_handlers(dp)       # /start и callback'и меню
register_text_router(dp)          # ← ЕДИНЫЙ роутер текстовых сообщений

register_programs_handlers(dp)    # callback'и программ
register_budget_handlers(dp)      # callback'и бюджета
register_bloggers_handlers(dp)    # callback'и блогеров


async def main():
    """Инициализация БД, загрузка программ и запуск polling."""
    logger.info("🚀 Запуск CashBrain...")

    # 1. Создаём таблицы в SQLite (если их нет)
    init_db()
    logger.info("✅ База данных инициализирована")

    # 2. Загружаем программы из JSON в БД
    load_programs_from_json()
    logger.info("✅ Программы загружены")

    await bot.set_commands(
        BotCommand(name="start", description="Запустить бота"),
    )
    

    # 3. Запускаем polling
    logger.info("🤖 Бот запущен и слушает сообщения")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())