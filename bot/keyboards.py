# bot/keyboards.py

"""
Модуль клавиатур для бота CashBrain.
"""

from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard():
    """Главное меню — только один сценарий."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🏛 Подобрать госпрограмму", payload="menu:programs"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_programs_keyboard():
    """Действия после показа программ."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="📊 Рассчитать доход", payload="programs:calculate"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_budget_keyboard():
    """Выбор сценария бюджета."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🟢 Осторожный", payload="budget:cautious"),
        CallbackButton(text="🟡 Сбалансированный", payload="budget:balanced"),
        CallbackButton(text="🔴 Агрессивный", payload="budget:aggressive"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_after_budget_keyboard():
    """После выбора бюджета — автоматический переход к блогерам."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="📢 Подобрать блогеров", payload="bloggers:start"),
        CallbackButton(text="🏠 В главное меню", payload="menu:main"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_bloggers_topics_keyboard(topics: list[str]):
    """Кнопки выбора темы блога."""
    builder = InlineKeyboardBuilder()
    for i, topic in enumerate(topics):
        builder.add(
            CallbackButton(text=topic.capitalize(), payload=f"bloggers:topic:{i}")
        )
    builder.add(CallbackButton(text="🌐 Любая тема", payload="bloggers:topic:any"))
    builder.adjust(2)
    return builder.as_markup()


def get_bloggers_ads_keyboard():
    """Фильтр по рекламе."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="✅ Только с рекламой", payload="bloggers:ads:yes"),
        CallbackButton(text="➖ Не важно", payload="bloggers:ads:no"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_bloggers_skip_keyboard(step: str):
    """Кнопка «Пропустить» для шагов 2 и 3."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="⏭ Пропустить", payload=f"bloggers:skip:{step}")
    )
    builder.adjust(1)
    return builder.as_markup()


def get_bloggers_restart_keyboard():
    """После выдачи результатов."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🔄 Найти ещё блогеров", payload="bloggers:restart"),
        CallbackButton(text="🏠 В главное меню", payload="menu:main"),
    )
    builder.adjust(1)
    return builder.as_markup()