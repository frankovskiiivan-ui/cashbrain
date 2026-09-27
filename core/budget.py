"""
Логика распределения бюджета.

Чистый Python — без зависимостей от MAX.
"""

# ─────────────────────────────────────────────────────────────
# Сценарии распределения бюджета (в процентах от общей суммы)
# ─────────────────────────────────────────────────────────────
BUDGET_SCENARIOS = {
    "cautious": {
        "label": "🟢 Осторожный",
        "description": "Минимум риска, плавный рост",
        "allocation": {
            "equipment": 0.50,
            "marketing": 0.15,
            "rent": 0.20,
            "reserve": 0.15,
        },
    },
    "balanced": {
        "label": "🟡 Сбалансированный",
        "description": "Оптимальное соотношение риска и роста",
        "allocation": {
            "equipment": 0.40,
            "marketing": 0.30,
            "rent": 0.20,
            "reserve": 0.10,
        },
    },
    "aggressive": {
        "label": "🔴 Агрессивный",
        "description": "Максимум вложений в рост",
        "allocation": {
            "equipment": 0.30,
            "marketing": 0.45,
            "rent": 0.15,
            "reserve": 0.10,
        },
    },
}


def calculate_budget_allocation(total_funding: float, scenario: str) -> dict:
    """
    Считает распределение бюджета по статьям.

    :param total_funding: общая сумма привлечённых средств
    :param scenario: cautious / balanced / aggressive
    :return: словарь с суммами по статьям
    """
    scenario_data = BUDGET_SCENARIOS.get(scenario, BUDGET_SCENARIOS["balanced"])
    allocation = scenario_data["allocation"]

    result = {
        "scenario": scenario,
        "label": scenario_data["label"],
        "description": scenario_data["description"],
        "total": round(total_funding, 2),
    }

    for category, ratio in allocation.items():
        result[category] = round(total_funding * ratio, 2)

    return result


def format_budget_report(total_funding: float) -> str:
    """
    Формирует текст с тремя сценариями распределения бюджета.
    """
    text = f"💰 **Распределение бюджета: {total_funding:,.0f} ₽**\n\n"

    for scenario_key in ["cautious", "balanced", "aggressive"]:
        s = calculate_budget_allocation(total_funding, scenario_key)
        text += f"**{s['label']}** — _{s['description']}_\n"
        text += f"   🏭 Оборудование: {s['equipment']:,.0f} ₽\n"
        text += f"   📢 Маркетинг: {s['marketing']:,.0f} ₽\n"
        text += f"   🏠 Аренда: {s['rent']:,.0f} ₽\n"
        text += f"   🛡 Резерв: {s['reserve']:,.0f} ₽\n\n"

    text += "Выберите сценарий с помощью кнопок ниже 👇"
    return text