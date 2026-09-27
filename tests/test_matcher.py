"""
Тесты для core/matcher.py

Проверяем:
- фильтрацию по региону
- фильтрацию по отрасли
- фильтрацию по выручке
- работу с программами "для всех"
"""

import pytest
from unittest.mock import patch, MagicMock

from core.matcher import find_matching_programs


class TestMatcher:
    """Тесты подбора программ."""

    @patch("core.matcher.get_session")
    def test_region_filter(self, mock_get_session):
        """Программа с конкретным регионом не должна подходить другому региону."""
        # Создаём мок-программу
        mock_program = MagicMock()
        mock_program.name = "Региональная программа"
        mock_program.type = "грант"
        mock_program.amount_max = 500000
        mock_program.interest_rate = None
        mock_program.source_url = "https://example.com"
        mock_program.conditions = {
            "region": ["Нижегородская область"],
            "industry": ["все"],
        }

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_program]
        mock_get_session.return_value = mock_session

        # Профиль из Татарстана — программа не должна подойти
        profile = {
            "region": "Республика Татарстан",
            "industry": "кофейня",
            "target_revenue": 300000,
        }
        result = find_matching_programs(profile)
        assert len(result) == 0

    @patch("core.matcher.get_session")
    def test_federal_program_matches_all(self, mock_get_session):
        """Программа с 'все' в регионе подходит любому."""
        mock_program = MagicMock()
        mock_program.name = "Федеральная программа"
        mock_program.type = "кредит"
        mock_program.amount_max = 1000000
        mock_program.interest_rate = "10%"
        mock_program.source_url = "https://example.com"
        mock_program.conditions = {
            "region": ["все"],
            "industry": ["все"],
        }

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_program]
        mock_get_session.return_value = mock_session

        profile = {
            "region": "Тюменская область",
            "industry": "IT",
            "target_revenue": 500000,
        }
        result = find_matching_programs(profile)
        assert len(result) == 1
        assert result[0]["name"] == "Федеральная программа"

    @patch("core.matcher.get_session")
    def test_industry_filter(self, mock_get_session):
        """Программа для IT не подходит кофейне."""
        mock_program = MagicMock()
        mock_program.name = "IT-грант"
        mock_program.type = "грант"
        mock_program.amount_max = 500000
        mock_program.interest_rate = None
        mock_program.source_url = "https://example.com"
        mock_program.conditions = {
            "region": ["все"],
            "industry": ["IT", "научно-техническая деятельность"],
        }

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_program]
        mock_get_session.return_value = mock_session

        profile = {
            "region": "Москва",
            "industry": "кофейня",
            "target_revenue": 300000,
        }
        result = find_matching_programs(profile)
        assert len(result) == 0

    @patch("core.matcher.get_session")
    def test_max_revenue_filter(self, mock_get_session):
        """Программа с ограничением по выручке не подходит, если выручка выше."""
        mock_program = MagicMock()
        mock_program.name = "Микрозайм"
        mock_program.type = "кредит"
        mock_program.amount_max = 5000000
        mock_program.interest_rate = "8.5%"
        mock_program.source_url = "https://example.com"
        mock_program.conditions = {
            "region": ["все"],
            "industry": ["все"],
            "max_revenue": 120000000,  # 120 млн
        }

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_program]
        mock_get_session.return_value = mock_session

        # Выручка 200 млн — больше лимита
        profile = {
            "region": "Москва",
            "industry": "производство",
            "target_revenue": 200000000,
        }
        result = find_matching_programs(profile)
        assert len(result) == 0

    @patch("core.matcher.get_session")
    def test_empty_result(self, mock_get_session):
        """Если ничего не подходит — возвращается пустой список."""
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        profile = {
            "region": "Тюменская область",
            "industry": "кофейня",
            "target_revenue": 300000,
        }
        result = find_matching_programs(profile)
        assert result == []