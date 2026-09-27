"""
Тесты для utils/validators.py

Проверяем:
- парсинг сумм
- нормализацию отрасли
- нормализацию региона
"""

import pytest
from utils.validators import parse_amount, normalize_industry, normalize_region


class TestParseAmount:
    """Тесты парсинга сумм."""

    def test_simple_number(self):
        assert parse_amount("500000") == 500000.0

    def test_with_spaces(self):
        assert parse_amount("500 000") == 500000.0

    def test_with_ruble_sign(self):
        assert parse_amount("500000 ₽") == 500000.0

    def test_with_comma(self):
        assert parse_amount("500,5") == 500.5

    def test_invalid_text(self):
        assert parse_amount("пятьсот тысяч") is None

    def test_empty_string(self):
        assert parse_amount("") is None


class TestNormalizeIndustry:
    """Тесты нормализации отрасли."""

    def test_lowercase(self):
        assert normalize_industry("Кофейня") == "кофейня"

    def test_with_spaces(self):
        assert normalize_industry("  IT-услуги  ") == "it-услуги"


class TestNormalizeRegion:
    """Тесты нормализации региона."""

    def test_title_case(self):
        assert normalize_region("нижегородская область") == "Нижегородская Область"

    def test_with_spaces(self):
        assert normalize_region("  москва  ") == "Москва"