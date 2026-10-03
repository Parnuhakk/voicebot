"""Call-local recovery from unclear input; only finalized turns change state."""

from dataclasses import dataclass


REPEAT_PROMPT = {
    "et": "Ma ei saanud päris aru. Palun korda oma vastust.",
    "en": "I didn't quite catch that. Please repeat your answer.",
    "ru": "Не удалось разобрать ответ. Повторите, пожалуйста.",
}
WRITE_LANGUAGE_PROMPT = {
    "et": "Ma ei saanud ikka aru. Palun kirjuta oma vastus eesti, vene või inglise keeles.",
    "en": "I still couldn't understand. Please type your answer in Estonian, Russian or English.",
    "ru": "Всё ещё не удалось понять. Напишите ответ по-эстонски, по-русски или по-английски.",
}


@dataclass
class InputRecovery:
    failures: int = 0
    waiting: bool = False

    def observe(self, status: str) -> None:
        if status in {"no_speech", "unsupported_language"}:
            self.failures = min(self.failures + 1, 2)
            self.waiting = True
        else:
            self.waiting = False
            if status in {"typed", "recognized"}:
                self.failures = 0
        # Provider/request failures neither blame the caller nor clear their
        # unfinished retry. No transcript or provider message is retained.

    def reply(self, language: str) -> str | None:
        if not self.waiting:
            return None
        copybook = WRITE_LANGUAGE_PROMPT if self.failures >= 2 else REPEAT_PROMPT
        return copybook.get(language, copybook["et"])
