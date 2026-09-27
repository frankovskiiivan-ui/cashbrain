"""
Точка входа бота CashBrain.

Запускает polling, инициализирует БД, регистрирует все обработчики.
"""

import asyncio
import logging
from dotenv import load_dotenv
from maxapi import Bot, Dispatcher

from data.db import init_db
from data.loader import load_programs_from_json
from bot.handlers.start import register_start_handlers
from bot.handlers.profile import register_profile_handlers
from bot.handlers.programs import register_programs_handlers
from bot.handlers.budget import register_budget_handlers

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

# Регистрируем все обработчики
register_start_handlers(dp)
register_profile_handlers(dp)
register_programs_handlers(dp)
register_budget_handlers(dp)


async def main():
    """Инициализация БД, загрузка программ и запуск polling."""
    logger.info("🚀 Запуск CashBrain...")

    # 1. Создаём таблицы в SQLite (если их нет)
    init_db()
    logger.info("✅ База данных инициализирована")

    # 2. Загружаем программы из JSON в БД
    load_programs_from_json()
    logger.info("✅ Программы загружены")

    # 3. Запускаем polling
    logger.info("🤖 Бот запущен и слушает сообщения")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())