"""Allowed Azure voice/locale pairs shared by browser and telephone settings."""

import re

# Deliberately limited to the multilingual speakers/locales used by this app.
# Microsoft's voice prefix is the speaker's primary locale, not its only one.
MULTILINGUAL_LOCALES: dict[str, frozenset[str]] = {
    "en-US-EmmaMultilingualNeural": frozenset({"en-US", "ru-RU"}),
    "en-US-AndrewMultilingualNeural": frozenset({"en-US", "ru-RU"}),
}


def validated_voice(voice: object, lang: object) -> tuple[str, str]:
    voice = voice.strip() if isinstance(voice, str) else ""
    lang = lang.strip() if isinstance(lang, str) else ""
    supported_locale = lang in {"et-EE", "ru-RU"} or re.fullmatch(r"en-[A-Z]{2}", lang) is not None
    if voice in MULTILINGUAL_LOCALES:
        supported_voice = lang in MULTILINGUAL_LOCALES[voice]
    else:
        supported_voice = (
            "Multilingual" not in voice
            and re.fullmatch(re.escape(lang) + r"-[A-Za-z0-9]+Neural", voice) is not None
        )
    if not supported_locale or not supported_voice:
        raise ValueError("supported speech voice required")
    return voice, lang
