"""
Модуль клавиатур для бота CashBrain.

Возвращает готовые AttachmentButton — их нужно передавать
в message.answer(..., attachments=[...]).
"""

from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


# ─────────────────────────────────────────────────────────────
#  Главное меню
# ─────────────────────────────────────────────────────────────

def get_main_menu_keyboard():
    """Кнопки главного меню: программы / блогеры."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🏛 Госпрограммы", payload="menu:programs"),
        CallbackButton(text="📢 Найти блогера", payload="menu:bloggers"),
    )
    builder.adjust(1)
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
#  Сценарий госпрограмм
# ─────────────────────────────────────────────────────────────

def get_programs_keyboard():
    """Действия после показа программ."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="📊 Рассчитать доход", payload="programs:calculate"),
        CallbackButton(text="💰 Распределить бюджет", payload="programs:budget"),
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


def get_final_keyboard():
    """Финальный экран."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🔄 Начать заново", payload="final:restart"),
        CallbackButton(text="💾 Сохранить отчёт", payload="final:save"),
    )
    builder.adjust(2)
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
#  Сценарий блогеров
# ─────────────────────────────────────────────────────────────

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


def get_bloggers_restart_keyboard():
    """После выдачи результатов."""
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(text="🔄 Найти ещё блогеров", payload="bloggers:restart")
    )
    builder.adjust(1)
    return builder.as_markup()