"""
Логика распределения бюджета.

Чистый Python — без зависимостей от MAX.
"""

# core/budget.py

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


# ─────────────────────────────────────────────────────────────
# Детализация расходов по отраслям (модельные данные)
# ─────────────────────────────────────────────────────────────
EQUIPMENT_DETAILS = {
    "кофейня": [
        {"name": "Кофемашина профессиональная", "price": 250000, "qty": 1},
        {"name": "Кофемолка", "price": 50000, "qty": 1},
        {"name": "Витрина холодильная", "price": 80000, "qty": 1},
        {"name": "Мебель для зала", "price": 100000, "qty": 1},
        {"name": "ПО для учёта", "price": 20000, "qty": 1},
    ],
    "общепит": [
        {"name": "Плита профессиональная", "price": 120000, "qty": 1},
        {"name": "Холодильное оборудование", "price": 150000, "qty": 1},
        {"name": "Мебель для зала", "price": 100000, "qty": 1},
        {"name": "Посуда и инвентарь", "price": 50000, "qty": 1},
    ],
    "it": [
        {"name": "Ноутбуки для команды", "price": 80000, "qty": 3},
        {"name": "Сервер", "price": 150000, "qty": 1},
        {"name": "Лицензии на ПО", "price": 50000, "qty": 1},
    ],
    "it-услуги": [
        {"name": "Ноутбуки для команды", "price": 80000, "qty": 3},
        {"name": "Сервер", "price": 150000, "qty": 1},
        {"name": "Лицензии на ПО", "price": 50000, "qty": 1},
    ],
    "производство": [
        {"name": "Станок", "price": 500000, "qty": 1},
        {"name": "Инструменты", "price": 100000, "qty": 1},
        {"name": "Стеллажи", "price": 30000, "qty": 2},
    ],
    "торговля": [
        {"name": "Витрины", "price": 60000, "qty": 3},
        {"name": "Кассовое оборудование", "price": 40000, "qty": 1},
        {"name": "Стеллажи", "price": 25000, "qty": 4},
    ],
    "услуги": [
        {"name": "Оборудование для работы", "price": 150000, "qty": 1},
        {"name": "Мебель", "price": 80000, "qty": 1},
        {"name": "ПО для учёта", "price": 30000, "qty": 1},
    ],
    "туризм": [
        {"name": "Транспорт", "price": 300000, "qty": 1},
        {"name": "Снаряжение", "price": 100000, "qty": 1},
        {"name": "ПО для бронирования", "price": 50000, "qty": 1},
    ],
}

RENT_DETAILS = {
    "кофейня": {"area_sqm": 60, "price_per_sqm": 1500, "city": "Нижний Новгород"},
    "общепит": {"area_sqm": 80, "price_per_sqm": 1800, "city": "Нижний Новгород"},
    "it": {"area_sqm": 40, "price_per_sqm": 1200, "city": "Москва"},
    "it-услуги": {"area_sqm": 40, "price_per_sqm": 1200, "city": "Москва"},
    "производство": {"area_sqm": 200, "price_per_sqm": 800, "city": "Регион"},
    "торговля": {"area_sqm": 50, "price_per_sqm": 2000, "city": "Нижний Новгород"},
    "услуги": {"area_sqm": 45, "price_per_sqm": 1500, "city": "Нижний Новгород"},
    "туризм": {"area_sqm": 30, "price_per_sqm": 1000, "city": "Регион"},
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


def format_selected_budget(scenario_data: dict) -> str:
    """Формирует текст для одного выбранного сценария."""
    text = f"✅ Выбран сценарий: {scenario_data['label']}\n"
    text += f"{scenario_data['description']}\n\n"
    text += f"Общая сумма: {scenario_data['total']:,.0f} ₽\n\n"
    text += f"🏭 Оборудование: {scenario_data['equipment']:,.0f} ₽\n"
    text += f"📢 Маркетинг: {scenario_data['marketing']:,.0f} ₽\n"
    text += f"🏠 Аренда: {scenario_data['rent']:,.0f} ₽\n"
    text += f"🛡 Резерв: {scenario_data['reserve']:,.0f} ₽\n"
    return text


# ─────────────────────────────────────────────────────────────
# Детализация расходов
# ─────────────────────────────────────────────────────────────
def detail_equipment(industry: str, budget: float) -> list[dict]:
    """
    Разбивает бюджет на оборудование по конкретным позициям.
    """
    items = EQUIPMENT_DETAILS.get(industry.lower(), EQUIPMENT_DETAILS.get("услуги"))
    result = []
    remaining = budget

    for item in items:
        cost = item["price"] * item["qty"]
        if cost <= remaining:
            result.append({
                "name": item["name"],
                "qty": item["qty"],
                "price": item["price"],
                "total": cost,
            })
            remaining -= cost

    if remaining > 0:
        result.append({
            "name": "Резерв на оборудование",
            "qty": 1,
            "price": remaining,
            "total": remaining,
        })

    return result


def detail_rent(industry: str, budget: float) -> dict:
    """
    Разбивает бюджет на аренду: площадь, цена за м², срок.
    """
    rent = RENT_DETAILS.get(industry.lower(), RENT_DETAILS.get("услуги"))
    area = rent["area_sqm"]
    price_per_sqm = rent["price_per_sqm"]
    monthly_cost = area * price_per_sqm
    months = int(budget / monthly_cost) if monthly_cost > 0 else 0

    return {
        "area_sqm": area,
        "price_per_sqm": price_per_sqm,
        "monthly_cost": monthly_cost,
        "months": months,
        "city": rent["city"],
    }


def detail_bloggers(marketing_budget: float, bloggers: list[dict]) -> list[dict]:
    """
    Разбивает маркетинговый бюджет на конкретных блогеров.
    """
    result = []
    remaining = marketing_budget

    for b in bloggers:
        post_price = int(b.get("avg_views", 0) * 0.5)
        if post_price <= 0:
            post_price = 5000

        if post_price <= remaining:
            result.append({
                "name": b["name"],
                "url": b["url"],
                "subscribers": b["subscribers"],
                "post_price": post_price,
                "reach": b.get("reach", 0),
                "er": b.get("er", 0),
            })
            remaining -= post_price

    return result


def format_expenses_details(
    industry: str,
    equipment_budget: float,
    rent_budget: float,
    marketing_budget: float,
    bloggers: list[dict],
) -> str:
    """
    Формирует текст с детализацией расходов.
    """
    text = "📋 **ДЕТАЛИЗАЦИЯ РАСХОДОВ**\n\n"

    # ─── Оборудование ───
    text += f"🏭 **ОБОРУДОВАНИЕ: {equipment_budget:,.0f} ₽**\n\n"
    equipment = detail_equipment(industry, equipment_budget)
    if equipment:
        for item in equipment:
            text += f"• {item['name']}"
            if item['qty'] > 1:
                text += f" × {item['qty']}"
            text += f" — {item['total']:,.0f} ₽\n"
    else:
        text += "_Бюджет слишком мал для закупки оборудования._\n"
    text += "\n"

    # ─── Аренда ───
    text += f"🏠 **АРЕНДА: {rent_budget:,.0f} ₽**\n\n"
    rent = detail_rent(industry, rent_budget)
    text += f"• Площадь: **{rent['area_sqm']} м²**\n"
    text += f"• Цена за м²: **{rent['price_per_sqm']:,.0f} ₽/мес**\n"
    text += f"• Город: **{rent['city']}**\n"
    text += f"• Стоимость в месяц: **{rent['monthly_cost']:,.0f} ₽**\n"
    text += f"• Хватит на: **{rent['months']} мес**\n\n"

    # ─── Блогеры ───
    text += f"📢 **БЛОГЕРЫ: {marketing_budget:,.0f} ₽**\n\n"
    if bloggers:
        blogger_details = detail_bloggers(marketing_budget, bloggers)
        if blogger_details:
            for b in blogger_details:
                text += f"• **{b['name']}**\n"
                text += f"  👥 {b['subscribers']:,} подписчиков | "
                text += f"📊 ER: {b['er']}% | Охват: {b['reach']}%\n"
                text += f"  💰 Пост: **{b['post_price']:,.0f} ₽**\n"
                text += f"  🔗 {b['url']}\n\n"
        else:
            text += "_Бюджет слишком мал для оплаты постов._\n"
    else:
        text += "_Блогеры не подобраны._\n"

    return text