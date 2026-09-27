# simulate.py

"""
Симулятор диалога с ботом CashBrain.

Позволяет пройти весь сценарий в терминале, без MAX.
Имитирует ввод пользователя и вызывает те же функции,
что и обработчики бота.
"""

from data.db import init_db
from data.loader import load_programs_from_json
from core.matcher import find_matching_programs
from core.calculator import (
    calculate_all_scenarios,
    calculate_by_program,
    format_scenarios_report,
    format_programs_rating,
)
from core.budget import calculate_budget_allocation, BUDGET_SCENARIOS
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


# ─────────────────────────────────────────────────────────────
# Сбор профиля
# ─────────────────────────────────────────────────────────────
def collect_profile() -> dict | None:
    """
    Собирает профиль ИП через диалог.
    Возвращает словарь с профилем или None, если ввод не удался.
    """
    # ШАГ 1: Отрасль
    print_separator("ШАГ 1 из 4: Отрасль")
    industry_raw = input("В какой сфере вы работаете? (например, «кофейня»): ")
    industry = normalize_industry(industry_raw)
    print(f"✅ Отрасль: {industry}")

    # ШАГ 2: Регион
    print_separator("ШАГ 2 из 4: Регион")
    region_raw = input("В каком регионе вы ведёте деятельность? (например, «Нижегородская область»): ")
    region = normalize_region(region_raw)
    print(f"✅ Регион: {region}")

    # ШАГ 3: Начальный капитал
    print_separator("ШАГ 3 из 4: Начальный капитал")
    capital_raw = input("Какой у вас начальный капитал? (например, «500000»): ")
    capital = parse_amount(capital_raw)
    if capital is None:
        print("❌ Не удалось распознать сумму.")
        return None
    print(f"✅ Капитал: {capital:,.0f} ₽")

    # ШАГ 4: Цель по выручке
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
# Запуск одного сценария
# ─────────────────────────────────────────────────────────────
def run_scenario(profile: dict) -> str:
    """
    Запускает один сценарий с заданным профилем.
    Возвращает: 'ok'
    """
    # ─────────────────────────────────────────────────────────
    # ПОДБОР ПРОГРАММ
    # ─────────────────────────────────────────────────────────
    print_separator("ПОДБОР ПРОГРАММ")

    programs = find_matching_programs(profile)

    if not programs:
        print("⚠️  Программ не найдено.")
        print("Это не страшно — продолжим расчёт без привлечённого финансирования.\n")
        programs = []
    else:
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

    # ─────────────────────────────────────────────────────────
    # РАСЧЁТ ДОХОДА (даже если programs = [])
    # ─────────────────────────────────────────────────────────
    print_separator("РАСЧЁТ ДОХОДА (3 сценария)")

    marketing_budget = 0
    scenarios = calculate_all_scenarios(profile, programs, marketing_budget)
    by_program = calculate_by_program(profile, programs, marketing_budget)

    report = format_scenarios_report(scenarios)
    if by_program:
        report += format_programs_rating(by_program)
    print(report)

    # ─────────────────────────────────────────────────────────
    # РАСПРЕДЕЛЕНИЕ БЮДЖЕТА
    # ─────────────────────────────────────────────────────────
    total_funding = scenarios["realistic"]["total_funding"]

    if total_funding <= 0:
        print_separator("РАСПРЕДЕЛЕНИЕ БЮДЖЕТА")
        print("⚠️  Нет привлечённого финансирования — распределять нечего.")
        print("Но вы можете использовать собственный капитал.\n")
    else:
        print_separator("РАСПРЕДЕЛЕНИЕ БЮДЖЕТА")
        print(f"Общая сумма: {total_funding:,.0f} ₽\n")

        for scenario_key in ["cautious", "balanced", "aggressive"]:
            allocation = calculate_budget_allocation(total_funding, scenario_key)
            print(f"**{allocation['label']}** — {allocation['description']}")
            print(f"   🏭 Оборудование: {allocation['equipment']:,.0f} ₽")
            print(f"   📢 Маркетинг: {allocation['marketing']:,.0f} ₽")
            print(f"   🏠 Аренда: {allocation['rent']:,.0f} ₽")
            print(f"   🛡 Резерв: {allocation['reserve']:,.0f} ₽")
            print()

        # ─── Выбор сценария бюджета ───
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

        # ─────────────────────────────────────────────────────────
        # ПЕРЕСЧЁТ ДОХОДА С МАРКЕТИНГОМ
        # ─────────────────────────────────────────────────────────
        print_separator("ПЕРЕСЧЁТ ДОХОДА (с учётом маркетинга)")

        scenarios_with_marketing = calculate_all_scenarios(
            profile, programs, marketing_budget
        )

        print(format_scenarios_report(scenarios_with_marketing))

    return "ok"


# ─────────────────────────────────────────────────────────────
# Главный цикл
# ─────────────────────────────────────────────────────────────
def simulate():
    """Главный цикл симулятора с возможностью продолжить."""
    print("🔧 Инициализация базы данных...")
    init_db()
    load_programs_from_json()
    print("✅ База данных готова")

    print_separator("CASHBRAIN — СИМУЛЯТОР ДИАЛОГА")
    print("Этот скрипт имитирует прохождение сценария в MAX.")
    print("Введите данные, как будто вы пользователь бота.\n")

    profile = None

    while True:
        # ─── Если профиля нет — собираем заново ───
        if profile is None:
            profile = collect_profile()
            if profile is None:
                print("❌ Не удалось собрать профиль.")
                return

        # ─── Запускаем сценарий ───
        run_scenario(profile)

        # ─── Спрашиваем, что дальше ───
        action = ask_continue()

        if action == "retry":
            # Меняем только часть параметров
            print_separator("ИЗМЕНЕНИЕ ПАРАМЕТРОВ")

            new_industry = input(
                f"Отрасль (текущая: «{profile['industry']}»): "
            ).strip()
            if new_industry:
                profile["industry"] = normalize_industry(new_industry)

            new_region = input(
                f"Регион (текущий: «{profile['region']}»): "
            ).strip()
            if new_region:
                profile["region"] = normalize_region(new_region)

            new_revenue = input(
                f"Цель по выручке (текущая: {profile['target_revenue']:,.0f} ₽): "
            ).strip()
            if new_revenue:
                parsed = parse_amount(new_revenue)
                if parsed is not None:
                    profile["target_revenue"] = parsed

            continue  # снова запускаем сценарий с обновлённым профилем

        if action == "restart":
            profile = None
            print("\n🔄 Начинаем заново...\n")
            continue

        # exit
        print("\n👋 До свидания!")
        return


if __name__ == "__main__":
    simulate()