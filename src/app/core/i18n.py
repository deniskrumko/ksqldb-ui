import gettext
from pathlib import Path
from typing import Optional, Union

from .settings import get_settings

# Путь к переводам
LOCALE_DIR = Path(__file__).parent.parent.parent.parent / "locale"

# Домен для переводов
DOMAIN = "messages"

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ["en", "ru"]

# Тип для переводов
TranslationsType = Union[gettext.GNUTranslations, gettext.NullTranslations]

# Кеш переводов
_translations_cache: dict[str, TranslationsType] = {}


def get_translations(language: Optional[str] = None) -> TranslationsType:
    """Получить объект переводов для указанного языка."""
    if language is None:
        settings = get_settings()
        language = getattr(settings, "language", "en")

    # Проверяем поддерживаемые языки
    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    # Используем кеш
    if language in _translations_cache:
        return _translations_cache[language]

    try:
        # Загружаем переводы
        translations = gettext.translation(
            domain=DOMAIN,
            localedir=LOCALE_DIR,
            languages=[language],
            fallback=True,
        )
    except FileNotFoundError:
        # Если файл перевода не найден, используем fallback
        translations = gettext.NullTranslations()

    _translations_cache[language] = translations
    return translations


def get_current_language() -> str:
    """Получить текущий язык из настроек."""
    settings = get_settings()
    language = getattr(settings, "language", "en")
    return language if language in SUPPORTED_LANGUAGES else "en"


def _(message: str, language: Optional[str] = None) -> str:
    """Перевести сообщение на указанный язык."""
    translations = get_translations(language)
    return translations.gettext(message)


def ngettext(singular: str, plural: str, n: int, language: Optional[str] = None) -> str:
    """Перевести сообщение с поддержкой множественного числа."""
    translations = get_translations(language)
    return translations.ngettext(singular, plural, n)
