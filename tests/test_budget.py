"""
Тесты для bot/handlers/budget.py

Проверяем:
- расчёт распределения по сценариям
- сумму распределения (должна равняться общей)
- форматирование отчёта
"""

import pytest
from core.budget import (
    calculate_budget_allocation,
    format_budget_report,
    BUDGET_SCENARIOS,
)


class TestBudgetAllocation:
    """Тесты расчёта распределения бюджета."""

    def test_cautious_scenario(self):
        """Осторожный сценарий: 50% на оборудование."""
        result = calculate_budget_allocation(1000000, "cautious")

        assert result["label"] == "🟢 Осторожный"
        assert result["equipment"] == 500000
        assert result["marketing"] == 150000
        assert result["rent"] == 200000
        assert result["reserve"] == 150000

    def test_balanced_scenario(self):
        """Сбалансированный сценарий: 30% на маркетинг."""
        result = calculate_budget_allocation(1000000, "balanced")

        assert result["label"] == "🟡 Сбалансированный"
        assert result["equipment"] == 400000
        assert result["marketing"] == 300000
        assert result["rent"] == 200000
        assert result["reserve"] == 100000

    def test_aggressive_scenario(self):
        """Агрессивный сценарий: 45% на маркетинг."""
        result = calculate_budget_allocation(1000000, "aggressive")

        assert result["label"] == "🔴 Агрессивный"
        assert result["equipment"] == 300000
        assert result["marketing"] == 450000
        assert result["rent"] == 150000
        assert result["reserve"] == 100000

    def test_total_equals_sum(self):
        """Сумма всех статей должна равняться общей сумме."""
        for scenario in ["cautious", "balanced", "aggressive"]:
            result = calculate_budget_allocation(1000000, scenario)
            total = (
                result["equipment"]
                + result["marketing"]
                + result["rent"]
                + result["reserve"]
            )
            assert total == result["total"]

    def test_unknown_scenario_fallback(self):
        """Неизвестный сценарий → сбалансированный."""
        result = calculate_budget_allocation(1000000, "unknown")
        assert result["label"] == "🟡 Сбалансированный"


class TestBudgetFormatting:
    """Тесты форматирования отчёта."""

    def test_format_contains_all_scenarios(self):
        """Отчёт должен содержать все три сценария."""
        text = format_budget_report(1000000)

        assert "Осторожный" in text
        assert "Сбалансированный" in text
        assert "Агрессивный" in text
        assert "1,000,000" in text

    def test_format_contains_categories(self):
        """Отчёт должен содержать все категории расходов."""
        text = format_budget_report(1000000)

        assert "Оборудование" in text
        assert "Маркетинг" in text
        assert "Аренда" in text
        assert "Резерв" in text