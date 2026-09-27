def parse_amount(text: str) -> float | None:
    """
    Превращает строку вида '500 000 ₽' в число 500000.0.
    Возвращает None, если распарсить не удалось.
    """
    cleaned = text.replace(" ", "").replace("₽", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_industry(text: str) -> str:
    """Приводит отрасль к нижнему регистру и убирает лишние пробелы."""
    return text.strip().lower()


def normalize_region(text: str) -> str:
    """Приводит регион к виду 'Нижегородская область' (первая буква заглавная)."""
    return text.strip().title()