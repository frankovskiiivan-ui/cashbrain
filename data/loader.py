import json
from data.db import get_session
from data.models import SupportProgram


def load_programs_from_json(filepath: str = "data/sources/programs.json"):
    """Читает JSON и заливает программы в БД. Пропускает дубликаты по названию."""
    with open(filepath, "r", encoding="utf-8") as f:
        programs = json.load(f)

    session = get_session()
    try:
        for p in programs:
            exists = session.query(SupportProgram).filter_by(name=p["name"]).first()
            if exists:
                continue

            program = SupportProgram(
                name=p["name"],
                type=p["type"],
                amount_min=p.get("amount_min", 0),
                amount_max=p.get("amount_max", 0),
                interest_rate=str(p.get("interest_rate")) if p.get("interest_rate") else None,
                conditions=p["conditions"],
                source_url=p.get("source_url", "")
            )
            session.add(program)

        session.commit()
        print(f"✅ Загружено программ: {session.query(SupportProgram).count()}")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка загрузки: {e}")
    finally:
        session.close()