"""
Логика расчёта аренды земли.

Чистый Python — без зависимостей от MAX.
"""

import json
from pathlib import Path

RENT_JSON = Path(__file__).parent.parent / "data" / "sources" / "rent_prices.json"


def load_rent_prices() -> list[dict]:
    """Загружает цены на аренду из JSON."""
    with open(RENT_JSON, encoding="utf-8") as f:
        return json.load(f)


def find_rent_price(region: str, city: str = None, land_type: str = "городская") -> dict | None:
    """
    Находит цену аренды по региону, городу и типу земли.
    Если точного совпадения нет — ищет по региону.
    """
    prices = load_rent_prices()

    # 1. Точное совпадение: регион + город + тип
    for p in prices:
        if p["region"] == region and p["city"] == city and p["land_type"] == land_type:
            return p

    # 2. Совпадение: регион + тип
    for p in prices:
        if p["region"] == region and p["land_type"] == land_type:
            return p

    # 3. Совпадение: регион
    for p in prices:
        if p["region"] == region:
            return p

    # 4. Fallback — средняя цена по России
    return {
        "region": region,
        "city": city or "—",
        "land_type": land_type,
        "price_per_sqm_month": 1000,
        "min_area_sqm": 50,
        "updated_at": "—",
        "is_fallback": True,
    }


def calculate_rent(
    region: str,
    city: str,
    area_sqm: float,
    months: int,
    land_type: str = "городская",
) -> dict:
    """
    Считает стоимость аренды земли.

    Формула:
        Стоимость = Площадь × Цена за м² × Срок (мес)

    :param region: регион
    :param city: город
    :param area_sqm: площадь в м²
    :param months: срок аренды в месяцах
    :param land_type: тип земли
    :return: словарь с расчётом
    """
    price_data = find_rent_price(region, city, land_type)

    price_per_sqm = price_data["price_per_sqm_month"]
    monthly_cost = area_sqm * price_per_sqm
    total_cost = monthly_cost * months

    return {
        "region": region,
        "city": city,
        "land_type": land_type,
        "area_sqm": area_sqm,
        "price_per_sqm_month": price_per_sqm,
        "monthly_cost": round(monthly_cost, 2),
        "months": months,
        "total_cost": round(total_cost, 2),
        "updated_at": price_data.get("updated_at", "—"),
        "is_fallback": price_data.get("is_fallback", False),
    }


def format_rent_report(rent_data: dict) -> str:
    """Формирует текст с расчётом аренды."""
    text = "🏠 **РАСЧЁТ АРЕНДЫ ЗЕМЛИ**\n\n"
    text += f"📍 Регион: **{rent_data['region']}**\n"
    text += f"🏙 Город: **{rent_data['city']}**\n"
    text += f"🏷 Тип земли: **{rent_data['land_type']}**\n\n"
    text += f"📐 Площадь: **{rent_data['area_sqm']} м²**\n"
    text += f"💰 Цена за м²: **{rent_data['price_per_sqm_month']:,.0f} ₽/мес**\n"
    text += f"📅 Срок: **{rent_data['months']} мес**\n\n"
    text += f"💵 Стоимость в месяц: **{rent_data['monthly_cost']:,.0f} ₽**\n"
    text += f"💵 Общая стоимость: **{rent_data['total_cost']:,.0f} ₽**\n"

    if rent_data.get("is_fallback"):
        text += "\n⚠️ _Точных данных для региона нет. Использована средняя цена._\n"

    if rent_data.get("updated_at") != "—":
        text += f"\n📅 Данные актуальны на: **{rent_data['updated_at']}**\n"

    return text