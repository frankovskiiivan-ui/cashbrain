"""
Бизнес-логика подбора блогеров для рекламы.

Чистый Python — без зависимостей от MAX, SQLAlchemy и FSM.
Все функции принимают список словарей (bloggers) и возвращают
отфильтрованный/отсортированный список или конкретные значения.

Это позволяет:
- тестировать логику без запуска бота (pytest);
- переиспользовать её в симуляторе и в реальном боте;
- менять источник данных (JSON → БД → API) без правки логики.
"""
from __future__ import annotations

from typing import Iterable


# ─────────────────────────────────────────────────────────────
#  Фильтры
# ─────────────────────────────────────────────────────────────

def filter_by_topics(bloggers: list[dict], topics: Iterable[str]) -> list[dict]:
    """Оставляет блогеров, у которых есть хотя бы одна из указанных тем."""
    topics_set = {t.strip().lower() for t in topics if t}
    if not topics_set:
        return list(bloggers)
    return [
        b for b in bloggers
        if topics_set & {t.lower() for t in b.get("topics", [])}
    ]


def filter_by_subscribers(
    bloggers: list[dict],
    min_subs: int | None = None,
    max_subs: int | None = None,
) -> list[dict]:
    """Фильтр по диапазону подписчиков. None = без ограничения."""
    result = bloggers
    if min_subs is not None:
        result = [b for b in result if b.get("subscribers", 0) >= min_subs]
    if max_subs is not None:
        result = [b for b in result if b.get("subscribers", 0) <= max_subs]
    return result


def filter_by_ads(bloggers: list[dict], only_with_ads: bool) -> list[dict]:
    """Если only_with_ads=True — оставляем только тех, у кого has_ads=True."""
    if not only_with_ads:
        return list(bloggers)
    return [b for b in bloggers if b.get("has_ads") is True]


# ─────────────────────────────────────────────────────────────
#  Метрики
# ─────────────────────────────────────────────────────────────

def calculate_er(blogger: dict) -> float:
    """
    Engagement Rate по реакциям (лайкам).

    Формула: avg_likes / subscribers × 100%
    Комментарии не учитываем, т.к. в MAX их не собираем в MVP.

    Возвращает процент (например, 3.2). Округление до 2 знаков.
    """
    subs = blogger.get("subscribers") or 0
    if subs <= 0:
        return 0.0
    likes = blogger.get("avg_likes") or 0
    return round(likes / subs * 100, 2)


def calculate_reach(blogger: dict) -> float:
    """
    Охват: avg_views / subscribers × 100%.
    Показывает, какая доля подписчиков видит посты.
    """
    subs = blogger.get("subscribers") or 0
    if subs <= 0:
        return 0.0
    views = blogger.get("avg_views") or 0
    return round(views / subs * 100, 2)


# ─────────────────────────────────────────────────────────────
#  Скоринг
# ─────────────────────────────────────────────────────────────

def score_blogger(blogger: dict) -> float:
    """
    Оценка блогера от 0 до 100.

    Логика:
    - ER (вовлечённость) — 50% веса. Чем выше, тем лучше.
    - Охват (reach) — 30% веса. Чем выше, тем лучше.
    - Наличие рекламы — 20% веса. Если блогер уже продаёт рекламу —
      с ним проще договориться (плюс 20 баллов).

    Нормировка:
    - ER: 0–10% → 0–50 баллов (10% и выше = максимум)
    - Reach: 0–100% → 0–30 баллов (100% и выше = максимум)
    - has_ads: True → +20, False/None → 0
    """
    er = calculate_er(blogger)
    reach = calculate_reach(blogger)
    has_ads = blogger.get("has_ads") is True

    er_score = min(er / 10.0, 1.0) * 50.0
    reach_score = min(reach / 100.0, 1.0) * 30.0
    ads_score = 20.0 if has_ads else 0.0

    return round(er_score + reach_score + ads_score, 1)


# ─────────────────────────────────────────────────────────────
#  Главная функция подбора
# ─────────────────────────────────────────────────────────────

def match_bloggers(
    bloggers: list[dict],
    topics: Iterable[str] | None = None,
    min_subs: int | None = None,
    max_subs: int | None = None,
    only_with_ads: bool = False,
    limit: int = 5,
) -> list[dict]:
    """
    Полный конвейер подбора:
    1. Фильтр по темам
    2. Фильтр по диапазону подписчиков
    3. Фильтр по наличию рекламы (опционально)
    4. Сортировка по score_blogger (убывание)
    5. Обрезка до limit

    Возвращает список словарей, обогащённых полями:
    - er (float)
    - reach (float)
    - score (float)
    """
    result = list(bloggers)
    if topics:
        result = filter_by_topics(result, topics)
    result = filter_by_subscribers(result, min_subs, max_subs)
    result = filter_by_ads(result, only_with_ads)

    # Обогащаем метриками
    enriched = []
    for b in result:
        b_copy = dict(b)
        b_copy["er"] = calculate_er(b)
        b_copy["reach"] = calculate_reach(b)
        b_copy["score"] = score_blogger(b)
        enriched.append(b_copy)

    enriched.sort(key=lambda b: b["score"], reverse=True)
    return enriched[:limit]


# ─────────────────────────────────────────────────────────────
#  Утилиты
# ─────────────────────────────────────────────────────────────

def get_all_topics(bloggers: list[dict]) -> list[str]:
    """Возвращает отсортированный список всех уникальных тем."""
    topics = {t for b in bloggers for t in b.get("topics", [])}
    return sorted(topics)


def get_subscribers_range(bloggers: list[dict]) -> tuple[int, int]:
    """Возвращает (min, max) подписчиков по всей базе."""
    if not bloggers:
        return (0, 0)
    subs = [b.get("subscribers", 0) for b in bloggers]
    return (min(subs), max(subs))