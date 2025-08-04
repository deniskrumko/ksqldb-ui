import gettext
from pathlib import Path
from typing import (
    Optional,
    Union,
)

from .settings import get_settings

LOCALE_DIR = Path(__file__).parent.parent.parent.parent / "locale"
DOMAIN = "messages"
SUPPORTED_LANGUAGES = ["en", "ru"]

TranslationsType = Union[gettext.GNUTranslations, gettext.NullTranslations]
TRANSLATION_CACHE: dict[str, TranslationsType] = {}


def get_translations(language: Optional[str] = None) -> TranslationsType:
    """Get the translation object for the specified language."""
    if language is None:
        language = get_current_language()

    # Check supported languages
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}",
        )

    # Use cache
    if language in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[language]

    try:
        # Load translations
        translations = gettext.translation(
            domain=DOMAIN,
            localedir=LOCALE_DIR,
            languages=[language],
            fallback=True,
        )
    except FileNotFoundError:
        # If translation file is not found, use fallback
        translations = gettext.NullTranslations()

    TRANSLATION_CACHE[language] = translations
    return translations


def get_current_language() -> str:
    """Get the current language from settings."""
    settings = get_settings()
    return settings.global_settings.language


def _(message: str, language: Optional[str] = None) -> str:
    """Translate a message to the specified language."""
    translations = get_translations(language)
    return translations.gettext(message)


def ngettext(singular: str, plural: str, n: int, language: Optional[str] = None) -> str:
    """Translate a message with plural support."""
    translations = get_translations(language)
    return translations.ngettext(singular, plural, n)
