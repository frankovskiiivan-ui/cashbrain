# simulate.py

"""
Симулятор диалога с ботом CashBrain.

Позволяет пройти сценарий в терминале, без MAX.
Имитирует ввод пользователя и вызывает те же функции,
что и обработчики бота.

Сценарии:
    1. Подбор госпрограмм поддержки (профиль ИП → программы → бюджет)
    2. Подбор блогеров для рекламы (тема → подписчики → реклама → выдача)
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
from core.budget import calculate_budget_allocation, BUDGET_SCENARIOS
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


def choose_scenario() -> str:
    """Главное меню симулятора."""
    print_separator("ГЛАВНОЕ МЕНЮ")
    print("1. 🏛 Подобрать госпрограмму поддержки")
    print("2. 📢 Найти блогера для рекламы")
    print("3. ❌ Выйти")

    choice = input("\nВаш выбор (1/2/3): ").strip()
    if choice == "1":
        return "programs"
    if choice == "2":
        return "bloggers"
    return "exit"


# ─────────────────────────────────────────────────────────────
# СБОР ПРОФИЛЯ ИП (сценарий госпрограмм)
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
# СЦЕНАРИЙ ГОСПРОГРАММ
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
            print(f"{allocation['label']} — {allocation['description']}")
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
# СБОР ЗАПРОСА НА БЛОГЕРОВ
# ─────────────────────────────────────────────────────────────
SKIP_WORDS = {"пропустить", "пропуск", "skip", "-", "нет", "не важно", ""}


def collect_blogger_request() -> dict | None:
    """
    Собирает запрос на подбор блогеров через диалог.
    Возвращает dict с параметрами или None при ошибке ввода.
    """
    bloggers = load_bloggers_from_json()
    topics = get_all_topics(bloggers)

    # ШАГ 1: Тема
    print_separator("ШАГ 1 из 4: Тема")
    for i, t in enumerate(topics, 1):
        print(f"  {i}. {t}")
    topic_raw = input("\nВыберите номер темы или напишите «любая»: ").strip().lower()

    if topic_raw in SKIP_WORDS or topic_raw in ("любая", "все"):
        selected_topics = None
    elif topic_raw.isdigit():
        idx = int(topic_raw) - 1
        if 0 <= idx < len(topics):
            selected_topics = [topics[idx]]
        else:
            print("❌ Такого номера нет. Берём все темы.")
            selected_topics = None
    else:
        # Пробуем как текстовое название темы
        matched = [t for t in topics if topic_raw in t.lower()]
        if matched:
            selected_topics = [matched[0]]
        else:
            print("❌ Тема не распознана. Берём все темы.")
            selected_topics = None

    print(f"✅ Темы: {selected_topics or 'все'}")

    # ШАГ 2: Мин. подписчики
    print_separator("ШАГ 2 из 4: Мин. подписчики")
    min_raw = input("Минимум (или «Пропустить»): ").strip().lower()
    if min_raw in SKIP_WORDS:
        min_subs = None
    else:
        min_subs = parse_amount(min_raw)
        if min_subs is None:
            print("⚠️  Не распознано, оставляем без ограничения.")
    print(f"✅ Мин. подписчиков: {min_subs if min_subs is not None else 'без ограничения'}")

    # ШАГ 3: Макс. подписчики
    print_separator("ШАГ 3 из 4: Макс. подписчики")
    max_raw = input("Максимум (или «Пропустить»): ").strip().lower()
    if max_raw in SKIP_WORDS:
        max_subs = None
    else:
        max_subs = parse_amount(max_raw)
        if max_subs is None:
            print("⚠️  Не распознано, оставляем без ограничения.")
    print(f"✅ Макс. подписчиков: {max_subs if max_subs is not None else 'без ограничения'}")

    # ШАГ 4: Только с рекламой?
    print_separator("ШАГ 4 из 4: Только с рекламой?")
    ads_raw = input("Показывать только тех, кто уже размещает рекламу? (Да/Нет): ").strip().lower()
    only_with_ads = ads_raw in ("да", "yes", "1", "y", "д")
    print(f"✅ Только с рекламой: {'да' if only_with_ads else 'нет'}")

    return {
        "topics": selected_topics,
        "min_subs": min_subs,
        "max_subs": max_subs,
        "only_with_ads": only_with_ads,
    }


# ─────────────────────────────────────────────────────────────
# СЦЕНАРИЙ ПОДБОРА БЛОГЕРОВ
# ─────────────────────────────────────────────────────────────
def run_bloggers_scenario() -> None:
    """Полный сценарий подбора блогеров для рекламы."""
    req = collect_blogger_request()
    if req is None:
        return

    print_separator("ПОДБОР БЛОГЕРОВ")

    results = match_bloggers(
        load_bloggers_from_json(),
        topics=req["topics"],
        min_subs=req["min_subs"],
        max_subs=req["max_subs"],
        only_with_ads=req["only_with_ads"],
        limit=5,
    )

    if not results:
        print("😔 По вашим параметрам ничего не найдено.")
        print("Попробуйте расширить диапазон подписчиков или выбрать другую тему.")
        return

    print(f"🔍 Найдено блогеров: {len(results)}\n")

    for i, b in enumerate(results, 1):
        print(f"{i}. {b['name']}")
        print(f"   🔗 {b['url']}")
        print(f"   🏷 {', '.join(b['topics'])}")
        print(f"   👥 {b['subscribers']:,} подписчиков")
        print(f"   📝 {b['posts_total']:,} постов всего")
        print(f"   👀 Ср. просмотры: {b['avg_views']:,}")
        print(f"   ❤️ Ср. реакции: {b['avg_likes']:,}")
        print(f"   📊 ER: {b['er']}% | Охват: {b['reach']}%")

        has_ads = b.get("has_ads")
        if has_ads is True:
            ads_line = "📢 Реклама: да (замечена)"
        elif has_ads is False:
            ads_line = "🚫 Реклама: не замечена"
        else:
            ads_line = "❓ Реклама: неизвестно"
        print(f"   {ads_line}")

        print(f"   ⭐ Оценка: {b['score']}/100")
        print()


# ─────────────────────────────────────────────────────────────
# Главный цикл
# ─────────────────────────────────────────────────────────────
def simulate():
    """Главный цикл симулятора с выбором сценария."""
    print("🔧 Инициализация базы данных...")
    init_db()
    load_programs_from_json()
    print("✅ База данных готова")

    print_separator("CASHBRAIN — СИМУЛЯТОР ДИАЛОГА")
    print("Этот скрипт имитирует прохождение сценария в MAX.")
    print("Введите данные, как будто вы пользователь бота.\n")

    profile = None

    while True:
        # ─── Если профиля нет — сначала выбор сценария ───
        if profile is None:
            scenario = choose_scenario()

            if scenario == "exit":
                print("\n👋 До свидания!")
                return

            if scenario == "bloggers":
                run_bloggers_scenario()
                # После сценария блогеров возвращаемся в главное меню
                continue

            # scenario == "programs"
            profile = collect_profile()
            if profile is None:
                print("❌ Не удалось собрать профиль.")
                continue

        # ─── Запускаем сценарий госпрограмм ───
        run_scenario(profile)

        # ─── Спрашиваем, что дальше ───
        action = ask_continue()

        if action == "retry":
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

            continue

        if action == "restart":
            profile = None
            print("\n🔄 Начинаем заново...\n")
            continue

        # exit
        print("\n👋 До свидания!")
        return


if __name__ == "__main__":
    simulate()