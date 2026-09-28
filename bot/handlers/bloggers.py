"""
Модуль подбора блогеров для рекламы.
"""

import logging

from maxapi import Dispatcher, F
from maxapi.types import MessageCallback
from maxapi.context.state_machine import State
from maxapi.context import MemoryContext

from core.marketing import match_bloggers, get_all_topics
from data.loader import load_bloggers_from_json
from utils.validators import parse_amount
from bot.keyboards import (
    get_bloggers_topics_keyboard,
    get_bloggers_ads_keyboard,
    get_bloggers_restart_keyboard,
    get_bloggers_skip_keyboard,
)

logger = logging.getLogger(__name__)

_bloggers_cache: list[dict] | None = None
SKIP_WORDS = {"пропустить", "пропуск", "skip", "-", "нет", "не важно"}


def get_bloggers() -> list[dict]:
    global _bloggers_cache
    if _bloggers_cache is None:
        _bloggers_cache = load_bloggers_from_json()
    return _bloggers_cache


class BloggersForm(State):
    waiting_for_topic = State()
    waiting_for_min_subs = State()
    waiting_for_max_subs = State()
    waiting_for_ads_filter = State()
    finished = State()


# ─────────────────────────────────────────────────────────────
#  Утилиты
# ─────────────────────────────────────────────────────────────

def format_topic_prompt() -> str:
    return "📚 Выберите тему блога кнопкой ниже или напишите номер из списка.\n"


def resolve_topic_by_index(index: int) -> list[str] | None:
    topics = get_all_topics(get_bloggers())
    if 0 <= index < len(topics):
        return [topics[index]]
    return None


def resolve_topic_by_text(text: str) -> tuple[list[str] | None, str | None]:
    text = text.strip().lower()
    if text in SKIP_WORDS or text in ("любая", "все"):
        return None, None
    topics = get_all_topics(get_bloggers())
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(topics):
            return [topics[idx]], None
        return None, "Такого номера нет. Попробуйте снова."
    for t in topics:
        if t.lower() == text:
            return [t], None
    for t in topics:
        if text in t.lower():
            return [t], None
    return None, "Не удалось распознать тему. Выберите кнопкой или напишите номер."


def format_blogger_card(b: dict, index: int) -> str:
    name = b.get("name", "Без названия")
    url = b.get("url", "")
    subs = b.get("subscribers", 0)
    posts = b.get("posts_total", 0)
    views = b.get("avg_views", 0)
    likes = b.get("avg_likes", 0)
    er = b.get("er", 0)
    reach = b.get("reach", 0)
    score = b.get("score", 0)
    topics = ", ".join(b.get("topics", []))
    has_ads = b.get("has_ads")
    if has_ads is True:
        ads_line = "📢 Реклама: да (замечена)"
    elif has_ads is False:
        ads_line = "🚫 Реклама: не замечена"
    else:
        ads_line = "❓ Реклама: неизвестно"
    return (
        f"{index}. {name}\n"
        f"🔗 {url}\n"
        f"🏷 {topics}\n"
        f"👥 {subs:,} подписчиков\n"
        f"📝 {posts:,} постов всего\n"
        f"👀 Ср. просмотры: {views:,}\n"
        f"❤️ Ср. реакции: {likes:,}\n"
        f"📊 ER: {er}% | Охват: {reach}%\n"
        f"{ads_line}\n"
        f"⭐ Оценка: {score}/100\n"
    )


def format_bloggers_report(bloggers: list[dict]) -> str:
    if not bloggers:
        return (
            "😔 Не найдено блогеров по вашим параметрам.\n"
            "Попробуйте расширить диапазон подписчиков или выбрать другую тему."
        )
    lines = [f"🔍 Найдено блогеров: {len(bloggers)}\n"]
    for i, b in enumerate(bloggers, 1):
        lines.append(format_blogger_card(b, i))
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
#  Точка входа
# ─────────────────────────────────────────────────────────────

async def start_bloggers_flow(event, context: MemoryContext):
    await context.set_state(BloggersForm.waiting_for_topic)
    topics = get_all_topics(get_bloggers())
    await event.message.answer(
        format_topic_prompt(),
        attachments=[get_bloggers_topics_keyboard(topics)],
    )


# ─────────────────────────────────────────────────────────────
#  Финальная логика
# ─────────────────────────────────────────────────────────────

async def _finish_and_show(message, context: MemoryContext, only_with_ads: bool):
    user_data = await context.get_data()
    selected_topics = user_data.get("selected_topics")
    min_subs = user_data.get("min_subs")
    max_subs = user_data.get("max_subs")

    await message.answer("🔎 Ищу блогеров...")

    try:
        results = match_bloggers(
            get_bloggers(),
            topics=selected_topics,
            min_subs=min_subs,
            max_subs=max_subs,
            only_with_ads=only_with_ads,
            limit=5,
        )
    except Exception as e:
        logger.error(f"Ошибка подбора блогеров: {e}")
        await message.answer("⚠️ Произошла ошибка при подборе. Попробуйте позже.")
        await context.set_state(BloggersForm.finished)
        return

    await message.answer(
        format_bloggers_report(results),
        attachments=[get_bloggers_restart_keyboard()],
    )
    await context.set_state(BloggersForm.finished)


# ─────────────────────────────────────────────────────────────
#  Текстовые шаги (вызываются из router.py)
# ─────────────────────────────────────────────────────────────

async def _ask_min_subs(message):
    await message.answer(
        "Шаг 2 из 4: Минимальное число подписчиков?\n"
        "Напишите число или нажмите «Пропустить».",
        attachments=[get_bloggers_skip_keyboard("min")],
    )


async def _ask_max_subs(message):
    await message.answer(
        "Шаг 3 из 4: Максимальное число подписчиков?\n"
        "Напишите число или нажмите «Пропустить».",
        attachments=[get_bloggers_skip_keyboard("max")],
    )


async def handle_topic_text(event, context: MemoryContext):
    topics, error = resolve_topic_by_text(event.message.body.text)
    if error:
        await event.message.answer(error)
        return
    await context.update_data(selected_topics=topics)
    await context.set_state(BloggersForm.waiting_for_min_subs)
    await _ask_min_subs(event.message)


async def handle_min_subs(event, context: MemoryContext):
    text = event.message.body.text.strip().lower()
    if text in SKIP_WORDS:
        min_subs = None
    else:
        min_subs = parse_amount(text)
        if min_subs is None:
            await event.message.answer("Напишите число или «Пропустить».")
            return
    await context.update_data(min_subs=min_subs)
    await context.set_state(BloggersForm.waiting_for_max_subs)
    await _ask_max_subs(event.message)


async def handle_max_subs(event, context: MemoryContext):
    text = event.message.body.text.strip().lower()
    if text in SKIP_WORDS:
        max_subs = None
    else:
        max_subs = parse_amount(text)
        if max_subs is None:
            await event.message.answer("Напишите число или «Пропустить».")
            return
    await context.update_data(max_subs=max_subs)
    await context.set_state(BloggersForm.waiting_for_ads_filter)
    await event.message.answer(
        "Шаг 4 из 4: Показывать только тех, кто уже размещает рекламу?",
        attachments=[get_bloggers_ads_keyboard()],
    )


async def handle_ads_text(event, context: MemoryContext):
    text = event.message.body.text.strip().lower()
    if text in ("да", "yes", "1", "y", "д"):
        only_with_ads = True
    elif text in ("нет", "no", "0", "n", "н"):
        only_with_ads = False
    else:
        await event.message.answer("Выберите кнопкой или напишите «Да»/«Нет».")
        return
    await _finish_and_show(event.message, context, only_with_ads)


# ─────────────────────────────────────────────────────────────
#  Callback-хендлеры
# ─────────────────────────────────────────────────────────────

def register_bloggers_handlers(dp: Dispatcher):
    @dp.message_callback(F.callback.payload == "bloggers:start")
    async def on_start_from_budget(event: MessageCallback, context: MemoryContext):
        await event.answer()
        # Состояние и данные (marketing_budget) уже сохранены в context
        await start_bloggers_flow(event, context)

    # ─── Шаг 1: тема кнопкой ───
    @dp.message_callback(F.callback.payload.startswith("bloggers:topic:"))
    async def on_topic_button(event: MessageCallback, context: MemoryContext):
        await event.answer()
        state = await context.get_state()
        if state != BloggersForm.waiting_for_topic:
            await event.message.answer("Эта кнопка уже неактуальна.")
            return
        token = event.callback.payload.split(":", 2)[2]
        if token == "any":
            selected_topics = None
        else:
            selected_topics = resolve_topic_by_index(int(token))
            if selected_topics is None:
                await event.message.answer("Тема не найдена. Попробуйте снова.")
                return
        await context.update_data(selected_topics=selected_topics)
        await context.set_state(BloggersForm.waiting_for_min_subs)
        await _ask_min_subs(event.message)

    # ─── Шаги 2 и 3: «Пропустить» ───
    @dp.message_callback(F.callback.payload.startswith("bloggers:skip:"))
    async def on_skip(event: MessageCallback, context: MemoryContext):
        await event.answer()
        payload = event.callback.payload  # bloggers:skip:min | bloggers:skip:max
        step = payload.split(":", 2)[2]

        if step == "min":
            state = await context.get_state()
            if state != BloggersForm.waiting_for_min_subs:
                await event.message.answer("Эта кнопка уже неактуальна.")
                return
            await context.update_data(min_subs=None)
            await context.set_state(BloggersForm.waiting_for_max_subs)
            await _ask_max_subs(event.message)

        elif step == "max":
            state = await context.get_state()
            if state != BloggersForm.waiting_for_max_subs:
                await event.message.answer("Эта кнопка уже неактуальна.")
                return
            await context.update_data(max_subs=None)
            await context.set_state(BloggersForm.waiting_for_ads_filter)
            await event.message.answer(
                "Шаг 4 из 4: Показывать только тех, кто уже размещает рекламу?",
                attachments=[get_bloggers_ads_keyboard()],
            )

    # ─── Шаг 4: реклама кнопкой ───
    @dp.message_callback(F.callback.payload.startswith("bloggers:ads:"))
    async def on_ads_button(event: MessageCallback, context: MemoryContext):
        await event.answer()
        state = await context.get_state()
        if state != BloggersForm.waiting_for_ads_filter:
            await event.message.answer("Эта кнопка уже неактуальна.")
            return
        token = event.callback.payload.split(":", 2)[2]
        only_with_ads = (token == "yes")
        await _finish_and_show(event.message, context, only_with_ads)

    # ─── «Найти ещё блогеров» ───
    @dp.message_callback(F.callback.payload == "bloggers:restart")
    async def on_restart(event: MessageCallback, context: MemoryContext):
        await event.answer()
        await context.clear()
        await context.set_state(BloggersForm.waiting_for_topic)
        topics = get_all_topics(get_bloggers())
        await event.message.answer(
            format_topic_prompt(),
            attachments=[get_bloggers_topics_keyboard(topics)],
        )