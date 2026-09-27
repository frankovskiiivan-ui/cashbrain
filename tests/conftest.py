"""
Общие фикстуры для всех тестов.

Фикстуры — это функции, которые подготавливают данные для тестов.
"""

import pytest


@pytest.fixture
def sample_profile():
    """Профиль ИП для тестов."""
    return {
        "region": "Нижегородская область",
        "industry": "кофейня",
        "target_revenue": 300000,
        "initial_capital": 500000,
    }


@pytest.fixture
def sample_programs():
    """Список программ для тестов."""
    return [
        {
            "name": "Грант для начинающих",
            "type": "грант",
            "amount_max": 500000,
            "interest_rate": None,
            "source_url": "https://example.com/1",
        },
        {
            "name": "Льготный кредит",
            "type": "кредит",
            "amount_max": 300000,
            "interest_rate": "ключ + 3%",
            "source_url": "https://example.com/2",
        },
    ]


@pytest.fixture
def empty_programs():
    """Пустой список программ."""
    return []