
# core/calculator.py

"""
Модуль расчёта дохода для ИП.

Принимает на вход:
- профиль ИП (target_revenue, initial_capital),
- список выбранных программ поддержки,
- бюджет на маркетинг (опционально),
- сценарий расчёта.

Возвращает прогноз выручки, расходов, чистой прибыли, ROI и срока окупаемости.

⚠️ ВАЖНО: Все расчёты являются прогнозными.
Используются упрощённые допущения, которые указаны в README.
"""

# ─────────────────────────────────────────────────────────────
# Базовые допущения (используются во всех сценариях)
# ─────────────────────────────────────────────────────────────
TAX_RATE = 0.06              # УСН 6% — самый распространённый режим для ИП
RENT_RATIO = 0.15            # Аренда — 15% от целевой выручки
SALARY_RATIO = 0.25          # Зарплаты — 25% от целевой выручки
LOAN_PAYMENT_RATIO = 0.05    # 5% от суммы финансирования в месяц


# ─────────────────────────────────────────────────────────────
# Коэффициенты для трёх сценариев
# ─────────────────────────────────────────────────────────────
SCENARIO_COEFFICIENTS = {
    "optimistic": {
        "revenue_growth_multiplier": 4.0,   # 1 руб. рекламы = 4 руб. выручки
        "base_growth_rate": 0.20,           # +20% к целевой выручке (органический рост)
        "label": "🟢 Оптимистичный",
    },
    "realistic": {
        "revenue_growth_multiplier": 3.0,   # 1 руб. рекламы = 3 руб. выручки
        "base_growth_rate": 0.10,           # +10%
        "label": "🟡 Реалистичный",
    },
    "pessimistic": {
        "revenue_growth_multiplier": 2.0,   # 1 руб. рекламы = 2 руб. выручки
        "base_growth_rate": 0.0,            # 0% (без роста)
        "label": "🔴 Пессимистичный",
    },
}


# ─────────────────────────────────────────────────────────────
# Основная функция расчёта
# ─────────────────────────────────────────────────────────────
def calculate_profit(
    profile: dict,
    programs: list,
    marketing_budget: float = 0,
    scenario: str = "realistic",
) -> dict:
    """
    Считает прогноз дохода для ИП по одному сценарию.

    :param profile: профиль ИП
        {
            "target_revenue": 300000,    # цель по выручке
            "initial_capital": 500000,   # начальный капитал
        }
    :param programs: список выбранных программ
        [{"name": "...", "amount_max": 500000}, ...]
    :param marketing_budget: бюджет на маркетинг (из модуля блогеров)
    :param scenario: "optimistic" | "realistic" | "pessimistic"
    :return: словарь с расчётами
    """
    coeffs = SCENARIO_COEFFICIENTS.get(scenario, SCENARIO_COEFFICIENTS["realistic"])

    # 1. Целевая выручка (то, что пользователь хочет получать)
    target_revenue = profile.get("target_revenue", 0)

    # 2. Сумма привлечённого финансирования
    total_funding = sum(p.get("amount_max", 0) for p in programs)

    # 3. Прогноз выручки:
    #    цель + базовый рост (органический) + прирост от маркетинга
    base_growth = target_revenue * coeffs["base_growth_rate"]
    revenue_growth = marketing_budget * coeffs["revenue_growth_multiplier"]
    forecast_revenue = target_revenue + base_growth + revenue_growth

    # 4. Расходы
    taxes = forecast_revenue * TAX_RATE          # УСН 6% от прогнозной выручки
    rent = target_revenue * RENT_RATIO           # Аренда — 15% от целевой
    salaries = target_revenue * SALARY_RATIO     # Зарплаты — 25% от целевой
    loan_payments = total_funding * LOAN_PAYMENT_RATIO  # 5% от финансирования
    marketing = marketing_budget

    total_expenses = taxes + rent + salaries + loan_payments + marketing

    # 5. Чистая прибыль
    net_profit = forecast_revenue - total_expenses

    # 6. ROI — возврат на вложенные средства
    roi = (net_profit / total_funding * 100) if total_funding > 0 else 0

    # 7. Срок окупаемости (в месяцах)
    payback_months = (total_funding / net_profit) if net_profit > 0 else None

    return {
        "scenario": scenario,
        "scenario_label": coeffs["label"],
        "total_funding": round(total_funding, 2),
        "forecast_revenue": round(forecast_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "roi": round(roi, 2),
        "payback_months": round(payback_months, 1) if payback_months else None,
        "marketing_budget": round(marketing_budget, 2),
    }


# ─────────────────────────────────────────────────────────────
# Расчёт по всем трём сценариям сразу
# ─────────────────────────────────────────────────────────────
def calculate_all_scenarios(
    profile: dict,
    programs: list,
    marketing_budget: float = 0,
) -> dict:
    """
    Считает три сценария: оптимистичный, реалистичный, пессимистичный.
    """
    return {
        "optimistic": calculate_profit(profile, programs, marketing_budget, "optimistic"),
        "realistic": calculate_profit(profile, programs, marketing_budget, "realistic"),
        "pessimistic": calculate_profit(profile, programs, marketing_budget, "pessimistic"),
    }


# ─────────────────────────────────────────────────────────────
# Расчёт по каждой программе отдельно
# ─────────────────────────────────────────────────────────────
def calculate_by_program(
    profile: dict,
    programs: list,
    marketing_budget: float = 0,
    scenario: str = "realistic",
) -> list:
    """
    Считает доход по каждой программе отдельно.
    Полезно, чтобы показать пользователю, какая программа выгоднее.
    """
    results = []
    for program in programs:
        result = calculate_profit(
            profile=profile,
            programs=[program],  # 👈 только одна программа
            marketing_budget=marketing_budget,
            scenario=scenario,
        )
        result["program_name"] = program.get("name", "Без названия")
        results.append(result)

    # Сортируем по ROI — самая выгодная программа сверху
    results.sort(key=lambda x: x["roi"], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────
# Форматирование результата в читаемый текст (для бота)
# ─────────────────────────────────────────────────────────────
def format_scenarios_report(scenarios: dict) -> str:
    """
    Превращает результат calculate_all_scenarios в текст для отправки в MAX.
    """
    text = "📊 **Прогноз дохода (3 сценария)**\n\n"

    for key in ["optimistic", "realistic", "pessimistic"]:
        s = scenarios[key]
        text += f"**{s['scenario_label']}**\n"
        text += f"   📈 Выручка: {s['forecast_revenue']:,.0f} ₽/мес\n"
        text += f"   ✅ Прибыль: {s['net_profit']:,.0f} ₽/мес\n"
        text += f"   🎯 ROI: {s['roi']}%\n"
        if s["payback_months"]:
            text += f"   ⏱ Окупаемость: {s['payback_months']} мес\n"
        text += "\n"

    return text


def format_programs_rating(by_program: list) -> str:
    """
    Превращает результат calculate_by_program в текст для отправки в MAX.
    """
    if len(by_program) <= 1:
        return ""

    text = "**🏆 Рейтинг программ по ROI:**\n\n"
    for i, p in enumerate(by_program[:3], 1):
        text += f"{i}. {p['program_name']}\n"
        text += f"   ROI: **{p['roi']}%** | Прибыль: {p['net_profit']:,.0f} ₽/мес\n"

    return text