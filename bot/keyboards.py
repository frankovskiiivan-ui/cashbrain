"""
Модуль клавиатур для бота CashBrain.

Содержит функции для создания inline-клавиатур,
которые используются в разных состояниях FSM.
"""

from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def get_programs_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура для выбора действия после показа программ.
    
    Кнопки:
    - «Рассчитать доход» → переход к calculator.py
    - «Распределить бюджет» → переход к budget.py
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Рассчитать доход", callback_data="programs:calculate")
    builder.button(text="💰 Распределить бюджет", callback_data="programs:budget")
    builder.adjust(1)  # по одной кнопке в ряд
    return builder


def get_budget_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура для выбора сценария распределения бюджета.
    
    Кнопки:
    - «🟢 Осторожный»
    - «🟡 Сбалансированный»
    - «🔴 Агрессивный»
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Осторожный", callback_data="budget:cautious")
    builder.button(text="🟡 Сбалансированный", callback_data="budget:balanced")
    builder.button(text="🔴 Агрессивный", callback_data="budget:aggressive")
    builder.adjust(1)
    return builder


def get_final_keyboard() -> InlineKeyboardBuilder:
    """
    Клавиатура для финального экрана.
    
    Кнопки:
    - «Начать заново» → сброс состояния
    - «Сохранить отчёт» → пока заглушка
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Начать заново", callback_data="final:restart")
    builder.button(text="💾 Сохранить отчёт", callback_data="final:save")
    builder.adjust(2)
    return builder