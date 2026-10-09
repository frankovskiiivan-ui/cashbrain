

"""
Модуль клавиатур для бота CashBrain.
"""

from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


# ─────────────────────────────────────────────────────────────
# Главное меню
# ─────────────────────────────────────────────────────────────
def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="🏛 Подобрать госпрограмму", payload="menu:programs"),
    )
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
# Шаг 1: Отрасль (кнопки)
# ─────────────────────────────────────────────────────────────
def get_industry_keyboard():
    """Кнопки выбора сферы деятельности."""
    builder = InlineKeyboardBuilder()
    industries = [
        "Кофейня",
        "Общепит",
        "IT",
        "IT-услуги",
        "Производство",
        "Торговля",
        "Услуги",
        "Туризм",
        "Логистика",
        "Образование",
    ]
    for ind in industries:
        builder.row(
            CallbackButton(
                text=ind,
                payload=f"profile:industry:{ind.lower()}",
            )
        )
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
# Шаг 2: Регион (кнопки)
# ─────────────────────────────────────────────────────────────
def get_region_keyboard():
    """Кнопки выбора региона."""
    builder = InlineKeyboardBuilder()
    regions = [
        "Москва",
        "Санкт-Петербург",
        "Нижегородская область",
        "Республика Татарстан",
        "Свердловская область",
        "Краснодарский край",
        "Новосибирская область",
        "Ростовская область",
        "Самарская область",
        "Тюменская область",
    ]
    for reg in regions:
        builder.row(
            CallbackButton(
                text=reg,
                payload=f"profile:region:{reg}",
            )
        )
    builder.row(
        CallbackButton(text="✏️ Ввести вручную", payload="profile:region:manual"),
    )
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
# Кнопки выбора госпрограмм
# ─────────────────────────────────────────────────────────────
def get_programs_choice_keyboard(programs: list):
    """
    Клавиатура для ВЫБОРА программ.
    Кнопка для каждой программы + «Выбрать все» + «Рассчитать доход».
    """
    builder = InlineKeyboardBuilder()

    for i, p in enumerate(programs):
        name = p["name"][:35] + ("..." if len(p["name"]) > 35 else "")
        builder.row(
            CallbackButton(
                text=f"{name} — до {p['amount_max']:,.0f} ₽",
                payload=f"programs:select:{i}",
            )
        )

    builder.row(
        CallbackButton(text="✅ Выбрать все", payload="programs:select:all"),
    )
    builder.row(
        CallbackButton(text="📊 Рассчитать доход", payload="programs:calculate"),
    )
    return builder.as_markup()


def get_programs_keyboard():
    """Только кнопка «Рассчитать доход»."""
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="📊 Рассчитать доход", payload="programs:calculate"),
    )
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
# Бюджет
# ─────────────────────────────────────────────────────────────
def get_budget_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="🟢 Осторожный", payload="budget:cautious"),
    )
    builder.row(
        CallbackButton(text="🟡 Сбалансированный", payload="budget:balanced"),
    )
    builder.row(
        CallbackButton(text="🔴 Агрессивный", payload="budget:aggressive"),
    )
    return builder.as_markup()


def get_after_budget_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="📋 Показать детали расходов", payload="budget:details"),
    )
    builder.row(
        CallbackButton(text="📢 Подобрать блогеров", payload="bloggers:start"),
    )
    builder.row(
        CallbackButton(text="🏠 В главное меню", payload="menu:main"),
    )
    return builder.as_markup()


def get_budget_details_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="📢 Подобрать блогеров", payload="bloggers:start"),
    )
    builder.row(
        CallbackButton(text="🏠 В главное меню", payload="menu:main"),
    )
    return builder.as_markup()


# ─────────────────────────────────────────────────────────────
# Блогеры
# ─────────────────────────────────────────────────────────────
def get_bloggers_topics_keyboard(topics: list[str]):
    builder = InlineKeyboardBuilder()
    for i, topic in enumerate(topics):
        builder.row(
            CallbackButton(
                text=topic.capitalize(),
                payload=f"bloggers:topic:{i}",
            )
        )
    builder.row(
        CallbackButton(text="🌐 Любая тема", payload="bloggers:topic:any"),
    )
    return builder.as_markup()


def get_bloggers_ads_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="✅ Только с рекламой", payload="bloggers:ads:yes"),
    )
    builder.row(
        CallbackButton(text="➖ Не важно", payload="bloggers:ads:no"),
    )
    return builder.as_markup()


def get_bloggers_skip_keyboard(step: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="⏭ Пропустить", payload=f"bloggers:skip:{step}"),
    )
    return builder.as_markup()


def get_bloggers_restart_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="🔄 Найти ещё блогеров", payload="bloggers:restart"),
    )
    builder.row(
        CallbackButton(text="🏠 В главное меню", payload="menu:main"),
    )
    return builder.as_markup()