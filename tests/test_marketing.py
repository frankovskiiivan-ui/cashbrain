"""Тесты бизнес-логики подбора блогеров."""
from core.marketing import (
    filter_by_topics,
    filter_by_subscribers,
    filter_by_ads,
    calculate_er,
    calculate_reach,
    score_blogger,
    match_bloggers,
    get_all_topics,
    get_subscribers_range,
)


# ──────────── Фикстуры ────────────

def make_blogger(**kwargs) -> dict:
    """Быстрый конструктор блогера со значениями по умолчанию."""
    base = {
        "id": "test",
        "name": "Test",
        "url": "https://max.ru/test",
        "topics": ["бизнес и стартапы"],
        "subscribers": 1000,
        "posts_total": 100,
        "avg_views": 500,
        "avg_likes": 30,
        "has_ads": False,
    }
    base.update(kwargs)
    return base


# ──────────── filter_by_topics ────────────

def test_filter_by_topics_match():
    bloggers = [
        make_blogger(id="a", topics=["бизнес и стартапы"]),
        make_blogger(id="b", topics=["карьера"]),
        make_blogger(id="c", topics=["бизнес и стартапы", "продажи"]),
    ]
    result = filter_by_topics(bloggers, ["бизнес и стартапы"])
    assert {b["id"] for b in result} == {"a", "c"}


def test_filter_by_topics_empty():
    bloggers = [make_blogger(id="a"), make_blogger(id="b")]
    result = filter_by_topics(bloggers, [])
    assert len(result) == 2


def test_filter_by_topics_no_match():
    bloggers = [make_blogger(id="a", topics=["карьера"])]
    result = filter_by_topics(bloggers, ["продажи"])
    assert result == []


# ──────────── filter_by_subscribers ────────────

def test_filter_by_subscribers_min():
    bloggers = [
        make_blogger(id="a", subscribers=500),
        make_blogger(id="b", subscribers=1500),
        make_blogger(id="c", subscribers=5000),
    ]
    result = filter_by_subscribers(bloggers, min_subs=1000)
    assert {b["id"] for b in result} == {"b", "c"}


def test_filter_by_subscribers_max():
    bloggers = [
        make_blogger(id="a", subscribers=500),
        make_blogger(id="b", subscribers=1500),
        make_blogger(id="c", subscribers=5000),
    ]
    result = filter_by_subscribers(bloggers, max_subs=2000)
    assert {b["id"] for b in result} == {"a", "b"}


def test_filter_by_subscribers_range():
    bloggers = [
        make_blogger(id="a", subscribers=500),
        make_blogger(id="b", subscribers=1500),
        make_blogger(id="c", subscribers=5000),
    ]
    result = filter_by_subscribers(bloggers, min_subs=1000, max_subs=3000)
    assert {b["id"] for b in result} == {"b"}


def test_filter_by_subscribers_none():
    bloggers = [make_blogger(id="a", subscribers=500)]
    result = filter_by_subscribers(bloggers)
    assert len(result) == 1


# ──────────── filter_by_ads ────────────

def test_filter_by_ads_only():
    bloggers = [
        make_blogger(id="a", has_ads=True),
        make_blogger(id="b", has_ads=False),
        make_blogger(id="c", has_ads=None),
    ]
    result = filter_by_ads(bloggers, only_with_ads=True)
    assert {b["id"] for b in result} == {"a"}


def test_filter_by_ads_all():
    bloggers = [
        make_blogger(id="a", has_ads=True),
        make_blogger(id="b", has_ads=False),
    ]
    result = filter_by_ads(bloggers, only_with_ads=False)
    assert len(result) == 2


# ──────────── calculate_er ────────────

def test_calculate_er_basic():
    b = make_blogger(subscribers=1000, avg_likes=30)
    assert calculate_er(b) == 3.0


def test_calculate_er_zero_subs():
    b = make_blogger(subscribers=0, avg_likes=30)
    assert calculate_er(b) == 0.0


def test_calculate_er_high():
    b = make_blogger(subscribers=1000, avg_likes=150)
    assert calculate_er(b) == 15.0


# ──────────── calculate_reach ────────────

def test_calculate_reach_basic():
    b = make_blogger(subscribers=1000, avg_views=500)
    assert calculate_reach(b) == 50.0


def test_calculate_reach_over_100():
    b = make_blogger(subscribers=1000, avg_views=1500)
    assert calculate_reach(b) == 150.0


# ──────────── score_blogger ────────────

def test_score_blogger_has_ads_bonus():
    """Блогер с рекламой получает +20 баллов."""
    b_no_ads = make_blogger(has_ads=False)
    b_with_ads = make_blogger(has_ads=True)
    assert score_blogger(b_with_ads) > score_blogger(b_no_ads)


def test_score_blogger_in_range():
    b = make_blogger()
    score = score_blogger(b)
    assert 0 <= score <= 100


# ──────────── match_bloggers ────────────

def test_match_bloggers_full_pipeline():
    bloggers = [
        make_blogger(id="a", topics=["бизнес и стартапы"], subscribers=1500, avg_likes=30, has_ads=True),
        make_blogger(id="b", topics=["карьера"], subscribers=1500, avg_likes=30, has_ads=True),
        make_blogger(id="c", topics=["бизнес и стартапы"], subscribers=500, avg_likes=30, has_ads=True),
        make_blogger(id="d", topics=["бизнес и стартапы"], subscribers=1500, avg_likes=30, has_ads=False),
    ]
    result = match_bloggers(
        bloggers,
        topics=["бизнес и стартапы"],
        min_subs=1000,
        max_subs=2000,
        only_with_ads=True,
    )
    # Остаётся только "a"
    assert len(result) == 1
    assert result[0]["id"] == "a"
    assert "er" in result[0]
    assert "reach" in result[0]
    assert "score" in result[0]


def test_match_bloggers_sorting_by_score():
    bloggers = [
        make_blogger(id="low", subscribers=1000, avg_likes=5, has_ads=False),   # ER=0.5
        make_blogger(id="high", subscribers=1000, avg_likes=100, has_ads=True), # ER=10
    ]
    result = match_bloggers(bloggers)
    assert result[0]["id"] == "high"


def test_match_bloggers_limit():
    bloggers = [make_blogger(id=str(i)) for i in range(10)]
    result = match_bloggers(bloggers, limit=3)
    assert len(result) == 3


# ──────────── Утилиты ────────────

def test_get_all_topics():
    bloggers = [
        make_blogger(topics=["бизнес и стартапы", "карьера"]),
        make_blogger(topics=["карьера", "продажи"]),
    ]
    topics = get_all_topics(bloggers)
    assert topics == ["бизнес и стартапы", "карьера", "продажи"]


def test_get_subscribers_range():
    bloggers = [
        make_blogger(subscribers=500),
        make_blogger(subscribers=5000),
        make_blogger(subscribers=1500),
    ]
    assert get_subscribers_range(bloggers) == (500, 5000)