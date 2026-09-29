# simulate.py

# simulate.py

"""
Симулятор диалога с ботом CashBrain.

Позволяет пройти ЕДИНЫЙ сценарий в терминале, без MAX:
    1. Профиль ИП
    2. Подбор госпрограмм
    3. Расчёт дохода (3 сценария)
    4. Распределение бюджета
    5. Подбор блогеров под бюджет (автоматически)
    6. Финальный расчёт дохода с учётом PR
"""

from data.db import init_db
from data.loader import load_programs_from_json, load_bloggers_from_json
from core.matcher import find_matching_programs
from core.calculator import (
    calculate_all_scenarios,
    calculate_by_program,
    format_scenarios_report,
    format_programs_rating,
)
from core.budget import calculate_budget_allocation
from core.marketing import match_bloggers, get_all_topics
from utils.validators import parse_amount, normalize_industry, normalize_region


# ─────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────
def print_separator(title: str = ""):
    """Печатает разделитель для красоты."""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def ask_continue() -> str:
    """
    Спрашивает у пользователя, что делать дальше.
    Возвращает: 'retry' | 'restart' | 'exit'
    """
    print_separator("ЧТО ДЕЛАЕМ ДАЛЬШЕ?")
    print("1. 🔄 Изменить параметры (регион, отрасль, выручка)")
    print("2. 🔁 Начать заново (сбросить всё)")
    print("3. ❌ Выйти")

    choice = input("\nВаш выбор (1/2/3): ").strip()

    if choice == "1":
        return "retry"
    if choice == "2":
        return "restart"
    return "exit"


def map_industry_to_topics(industry: str) -> list[str] | None:
    """
    Сопоставляет отрасль ИП с темами блогеров.
    Возвращает список тем или None (если не нашли — берём все).
    """
    mapping = {
        "кофейня": ["бизнес и стартапы", "продажи"],
        "общепит": ["бизнес и стартапы", "продажи"],
        "it": ["бизнес и стартапы", "технологии", "карьера"],
        "it-услуги": ["бизнес и стартапы", "технологии", "карьера"],
        "производство": ["бизнес и стартапы", "продажи"],
        "торговля": ["продажи", "бизнес и стартапы"],
        "услуги": ["бизнес и стартапы", "продажи"],
        "туризм": ["путешествия", "бизнес и стартапы"],
        "логистика": ["бизнес и стартапы", "продажи"],
        "сельское хозяйство": ["бизнес и стартапы", "продажи"],
        "образование": ["образование", "карьера", "бизнес и стартапы"],
        "креативные индустрии": ["маркетинг pr реклама", "бизнес и стартапы"],
    }
    return mapping.get(industry.lower())


# ─────────────────────────────────────────────────────────────
# ШАГ 1: Сбор профиля ИП
# ─────────────────────────────────────────────────────────────
def collect_profile() -> dict | None:
    """Собирает профиль ИП через диалог."""
    print_separator("ШАГ 1 из 4: Отрасль")
    industry_raw = input("В какой сфере вы работаете? (например, «кофейня»): ")
    industry = normalize_industry(industry_raw)
    print(f"✅ Отрасль: {industry}")

    print_separator("ШАГ 2 из 4: Регион")
    region_raw = input("В каком регионе вы ведёте деятельность? (например, «Нижегородская область»): ")
    region = normalize_region(region_raw)
    print(f"✅ Регион: {region}")

    print_separator("ШАГ 3 из 4: Начальный капитал")
    capital_raw = input("Какой у вас начальный капитал? (например, «500000»): ")
    capital = parse_amount(capital_raw)
    if capital is None:
        print("❌ Не удалось распознать сумму.")
        return None
    print(f"✅ Капитал: {capital:,.0f} ₽")

    print_separator("ШАГ 4 из 4: Цель по выручке")
    revenue_raw = input("Какую ежемесячную выручку вы хотите получать? (например, «300000»): ")
    target_revenue = parse_amount(revenue_raw)
    if target_revenue is None:
        print("❌ Не удалось распознать сумму.")
        return None
    print(f"✅ Цель по выручке: {target_revenue:,.0f} ₽/мес")

    return {
        "region": region,
        "industry": industry,
        "target_revenue": target_revenue,
        "initial_capital": capital,
    }


# ─────────────────────────────────────────────────────────────
# ШАГ 2: Подбор госпрограмм
# ─────────────────────────────────────────────────────────────
def step_programs(profile: dict) -> list:
    """Подбирает и показывает программы. Возвращает список программ."""
    print_separator("ПОДБОР ГОСПРОГРАММ")

    programs = find_matching_programs(profile)

    if not programs:
        print("⚠️  Программ не найдено.")
        print("Это не страшно — продолжим расчёт без привлечённого финансирования.\n")
        return []

    print(f"✅ Найдено программ: {len(programs)}\n")

    federal = [p for p in programs if "все" in p.get("region", ["все"])]
    regional = [p for p in programs if "все" not in p.get("region", ["все"])]

    print(f"   🇷🇺 Федеральных: {len(federal)}")
    print(f"   📍 Региональных: {len(regional)}\n")

    if not regional:
        print(f"⚠️  Для региона «{profile['region']}» нет региональных программ.\n")

    for i, p in enumerate(programs, 1):
        print(f"{i}. {p['name']}")
        print(f"   💰 До {p['amount_max']:,.0f} ₽")
        if p.get("interest_rate"):
            print(f"   📉 Ставка: {p['interest_rate']}")
        print()

    return programs


# ─────────────────────────────────────────────────────────────
# ШАГ 3: Расчёт дохода (без маркетинга)
# ─────────────────────────────────────────────────────────────
def step_income_no_marketing(profile: dict, programs: list) -> dict:
    """Считает доход без маркетинга. Возвращает scenarios."""
    print_separator("РАСЧЁТ ДОХОДА (без маркетинга)")

    scenarios = calculate_all_scenarios(profile, programs, marketing_budget=0)
    by_program = calculate_by_program(profile, programs, marketing_budget=0)

    report = format_scenarios_report(scenarios)
    if by_program:
        report += format_programs_rating(by_program)
    print(report)

    return scenarios


# ─────────────────────────────────────────────────────────────
# ШАГ 4: Распределение бюджета
# ─────────────────────────────────────────────────────────────
def step_budget(profile: dict, programs: list, scenarios: dict) -> float:
    """
    Показывает 3 сценария бюджета, даёт пользователю выбрать.
    Возвращает marketing_budget.
    """
    total_funding = scenarios["realistic"]["total_funding"]

    if total_funding <= 0:
        print_separator("РАСПРЕДЕЛЕНИЕ БЮДЖЕТА")
        print("⚠️  Нет привлечённого финансирования — распределять нечего.")
        print("Но вы можете использовать собственный капитал.\n")
        return 0.0

    print_separator("РАСПРЕДЕЛЕНИЕ БЮДЖЕТА")
    print(f"Общая сумма: {total_funding:,.0f} ₽\n")

    for scenario_key in ["cautious", "balanced", "aggressive"]:
        allocation = calculate_budget_allocation(total_funding, scenario_key)
        print(f"{allocation['label']} — {allocation['description']}")
        print(f"   🏭 Оборудование: {allocation['equipment']:,.0f} ₽")
        print(f"   📢 Маркетинг: {allocation['marketing']:,.0f} ₽")
        print(f"   🏠 Аренда: {allocation['rent']:,.0f} ₽")
        print(f"   🛡 Резерв: {allocation['reserve']:,.0f} ₽")
        print()

    print_separator("ВЫБОР СЦЕНАРИЯ")
    scenario_choice = input(
        "Выберите сценарий (осторожный / сбалансированный / агрессивный): "
    ).strip().lower()

    mapping = {
        "осторожный": "cautious",
        "сбалансированный": "balanced",
        "агрессивный": "aggressive",
    }

    if scenario_choice not in mapping:
        print("❌ Неверный выбор. По умолчанию — сбалансированный.")
        scenario_choice = "сбалансированный"

    scenario_key = mapping[scenario_choice]
    allocation = calculate_budget_allocation(total_funding, scenario_key)
    marketing_budget = allocation["marketing"]

    print(f"\n✅ Выбран сценарий: {allocation['label']}")
    print(f"📢 Маркетинговый бюджет: {marketing_budget:,.0f} ₽")

    return marketing_budget


# ─────────────────────────────────────────────────────────────
# ШАГ 5: Подбор блогеров под бюджет
# ─────────────────────────────────────────────────────────────
def step_bloggers(profile: dict, marketing_budget: float) -> list:
    """
    Автоматически подбирает блогеров под бюджет и отрасль.
    Возвращает список блогеров.
    """
    print_separator("📢 ПОДБОР БЛОГЕРОВ ПОД БЮДЖЕТ")

    if marketing_budget <= 0:
        print("⚠️  Маркетинговый бюджет = 0. Блогеры не подбираются.\n")
        return []

    bloggers = load_bloggers_from_json()

    # Подбираем темы по отрасли
    topics = map_industry_to_topics(profile["industry"])

    results = match_bloggers(
        bloggers,
        topics=topics,
        min_subs=None,
        max_subs=None,
        only_with_ads=False,
        limit=5,
    )

    if not results:
        print("😔 По вашим параметрам блогеров не найдено.\n")
        return []

    print(f"Бюджет на маркетинг: {marketing_budget:,.0f} ₽")
    print(f"Подобрано блогеров: {len(results)}\n")

    for i, b in enumerate(results, 1):
        print(f"{i}. {b['name']}")
        print(f"   🔗 {b['url']}")
        print(f"   🏷 {', '.join(b['topics'])}")
        print(f"   👥 {b['subscribers']:,} подписчиков")
        print(f"   📈 ER: {b['er']}% | Охват: {b['reach']}%")
        print(f"   ⭐ Оценка: {b['score']}/100")
        print()

    return results


# ─────────────────────────────────────────────────────────────
# ШАГ 6: Финальный расчёт дохода с учётом PR
# ─────────────────────────────────────────────────────────────
def step_final_income(profile: dict, programs: list, marketing_budget: float):
    """Финальный расчёт дохода с учётом маркетинга."""
    print_separator("📊 ИТОГОВЫЙ ПРОГНОЗ ДОХОДА (с учётом PR)")

    final_scenarios = calculate_all_scenarios(profile, programs, marketing_budget)
    print(format_scenarios_report(final_scenarios))


# ─────────────────────────────────────────────────────────────
# ГЛАВНЫЙ СЦЕНАРИЙ
# ─────────────────────────────────────────────────────────────
def run_full_scenario(profile: dict) -> str:
    """Единый сценарий: программы → доход → бюджет → блогеры → итог."""
    programs = step_programs(profile)
    scenarios = step_income_no_marketing(profile, programs)
    marketing_budget = step_budget(profile, programs, scenarios)
    step_bloggers(profile, marketing_budget)
    step_final_income(profile, programs, marketing_budget)
    return "ok"


def simulate():
    """Главный цикл симулятора."""
    print("🔧 Инициализация базы данных...")
    init_db()
    load_programs_from_json()
    print("✅ База данных готова")

    print_separator("CASHBRAIN — НАВИГАТОР ПРИБЫЛИ")
    print("Помогу подобрать госпрограммы, распределить бюджет")
    print("и рассчитать доход с учётом рекламы у блогеров.\n")

    profile = None

    while True:
        if profile is None:
            profile = collect_profile()
            if profile is None:
                print("❌ Не удалось собрать профиль.")
                return

        run_full_scenario(profile)

        action = ask_continue()

        if action == "retry":
            print_separator("ИЗМЕНЕНИЕ ПАРАМЕТРОВ")
            new_industry = input(f"Отрасль (текущая: «{profile['industry']}»): ").strip()
            if new_industry:
                profile["industry"] = normalize_industry(new_industry)

            new_region = input(f"Регион (текущий: «{profile['region']}»): ").strip()
            if new_region:
                profile["region"] = normalize_region(new_region)

            new_revenue = input(f"Цель по выручке (текущая: {profile['target_revenue']:,.0f} ₽): ").strip()
            if new_revenue:
                parsed = parse_amount(new_revenue)
                if parsed is not None:
                    profile["target_revenue"] = parsed
            continue

        if action == "restart":
            profile = None
            print("\n🔄 Начинаем заново...\n")
            continue

        print("\n👋 До свидания!")
        return


if __name__ == "__main__":
    simulate()