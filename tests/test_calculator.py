"""
Тесты для core/calculator.py

Проверяем:
- базовый расчёт дохода
- расчёт с маркетинговым бюджетом
- три сценария
- рейтинг программ
- обработку граничных случаев
"""

import pytest
from core.calculator import (
    calculate_profit,
    calculate_all_scenarios,
    calculate_by_program,
    format_scenarios_report,
    format_programs_rating,
)


class TestCalculateProfit:
    """Тесты основной функции расчёта."""

    def test_basic_calculation(self, sample_profile, sample_programs):
        """Базовый расчёт без маркетинга."""
        result = calculate_profit(sample_profile, sample_programs, marketing_budget=0)

        # Проверяем структуру результата
        assert "total_funding" in result
        assert "forecast_revenue" in result
        assert "net_profit" in result
        assert "roi" in result
        assert "payback_months" in result

        # Проверяем значения
        assert result["total_funding"] == 800000  # 500000 + 300000
        assert result["forecast_revenue"] == 300000  # без маркетинга = target
        assert result["net_profit"] > 0
        assert result["roi"] > 0

    def test_calculation_with_marketing(self, sample_profile, sample_programs):
        """Расчёт с маркетинговым бюджетом."""
        result = calculate_profit(
            sample_profile, sample_programs, marketing_budget=100000
        )

        # Прирост выручки: 100000 * 3 = 300000
        # Прогноз: 300000 + 300000 = 600000
        assert result["forecast_revenue"] == 600000
        assert result["marketing_budget"] == 100000

    def test_zero_funding(self, sample_profile, empty_programs):
        """Если программ нет — ROI должен быть 0."""
        result = calculate_profit(sample_profile, empty_programs)
        assert result["total_funding"] == 0
        assert result["roi"] == 0

    def test_payback_calculation(self, sample_profile, sample_programs):
        """Проверка срока окупаемости."""
        result = calculate_profit(sample_profile, sample_programs)

        if result["net_profit"] > 0:
            expected_payback = result["total_funding"] / result["net_profit"]
            assert abs(result["payback_months"] - round(expected_payback, 1)) < 0.1


class TestAllScenarios:
    """Тесты трёх сценариев."""

    def test_all_scenarios_structure(self, sample_profile, sample_programs):
        """Проверяем, что возвращаются все три сценария."""
        scenarios = calculate_all_scenarios(sample_profile, sample_programs)

        assert "optimistic" in scenarios
        assert "realistic" in scenarios
        assert "pessimistic" in scenarios

    def test_scenarios_ordering(self, sample_profile, sample_programs):
        """Оптимистичный > реалистичный > пессимистичный по прибыли."""
        scenarios = calculate_all_scenarios(
            sample_profile, sample_programs, marketing_budget=100000
        )

        opt = scenarios["optimistic"]["net_profit"]
        real = scenarios["realistic"]["net_profit"]
        pess = scenarios["pessimistic"]["net_profit"]

        assert opt > real > pess


class TestByProgram:
    """Тесты рейтинга программ."""

    def test_rating_sorted_by_roi(self, sample_profile, sample_programs):
        """Программы должны быть отсортированы по ROI (убывание)."""
        results = calculate_by_program(sample_profile, sample_programs)

        assert len(results) == 2
        assert results[0]["roi"] >= results[1]["roi"]

    def test_rating_has_program_name(self, sample_profile, sample_programs):
        """У каждой программы должно быть имя."""
        results = calculate_by_program(sample_profile, sample_programs)

        for r in results:
            assert "program_name" in r
            assert r["program_name"] != ""


class TestFormatting:
    """Тесты форматирования для MAX."""

    def test_format_scenarios_report(self, sample_profile, sample_programs):
        """Текст отчёта должен содержать ключевые слова."""
        scenarios = calculate_all_scenarios(sample_profile, sample_programs)
        text = format_scenarios_report(scenarios)

        assert "Прогноз дохода" in text
        assert "Оптимистичный" in text
        assert "Реалистичный" in text
        assert "Пессимистичный" in text
        assert "ROI" in text

    def test_format_programs_rating_empty(self):
        """Если одна программа — рейтинг пустой."""
        text = format_programs_rating([{"program_name": "Test", "roi": 10, "net_profit": 1000}])
        assert text == ""

    def test_format_programs_rating_multiple(self, sample_profile, sample_programs):
        """Рейтинг должен содержать все программы."""
        results = calculate_by_program(sample_profile, sample_programs)
        text = format_programs_rating(results)

        assert "Рейтинг программ" in text
        assert results[0]["program_name"] in text