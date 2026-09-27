from data.db import get_session
from data.models import SupportProgram


def find_matching_programs(profile: dict) -> list:
    """
    Принимает профиль ИП:
    {
        "region": "Нижегородская область",
        "industry": "производство",
        "monthly_revenue": 150000
    }
    Возвращает список подходящих программ.
    """
    session = get_session()
    try:
        all_programs = session.query(SupportProgram).all()
        matched = []

        for program in all_programs:
            cond = program.conditions or {}

            # 1. Регион
            regions = cond.get("region", ["все"])
            if "все" not in regions and profile["region"] not in regions:
                continue

            # 2. Отрасль
            industries = cond.get("industry", ["все"])
            if "все" not in industries and profile["industry"] not in industries:
                continue

            # 3. Максимальная выручка
            if cond.get("max_revenue") and profile.get("target_revenue", 0) > cond["max_revenue"]:
                continue

            matched.append({
                "name": program.name,
                "type": program.type,
                "amount_max": program.amount_max,
                "interest_rate": program.interest_rate,
                "source_url": program.source_url
            })

        return matched
    finally:
        session.close() 