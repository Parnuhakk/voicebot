"""Real restaurant routes with local synthetic audio; no paid providers."""

import os
import json
import tempfile
import httpx
from pathlib import Path
from unittest.mock import patch

from app.server import create_app as server_app
from app.providers.azure_tts import AzureTtsClient
from app.providers.transcription import Transcription
from app.providers.voice_config import VoiceConfig

_storage = tempfile.TemporaryDirectory(prefix="voicebot-restaurant-browser-")


class FixtureSpeech:
    def transcribe_with_metadata(self, audio, *, language=None):
        if audio == b"fixture-unsupported-recovery":
            return Transcription("private-rejected-language-fixture", None)
        selected = language if language in {"et", "en", "ru"} else "en"
        return Transcription(self.transcribe(audio, language=language), selected)

    def transcribe(self, audio, *, language=None):
        return {"et": "Milline on menüü?", "ru": "Что есть в меню?"}.get(
            language, "What is on the menu?"
        )

    def synthesize(self, text):
        return (Path(__file__).parent / "fixtures/speech-tone.mp3").read_bytes()

    def close(self):
        pass


class FixtureLlm:
    supports_restaurant_reasoning = True
    config = VoiceConfig()

    def chat(self, messages, tools=None, *, response_format=None, timeout=None):
        if response_format is not None:
            schema = response_format["json_schema"]
            language = schema["schema"]["properties"]["language"]["enum"][0]
            if schema["name"] == "restaurant_review":
                return {"content": json.dumps({"approved": True, "language": language})}
            facts = json.loads(messages[0]["content"].split("Trusted facts: ", 1)[1])
            question = messages[-1]["content"]
            examples = {
                "et": ("Üks meist on vegan, teisele meeldivad seened. Mida soovitaksite ja miks?",
                       "Veganile soovitan köögiviljasuppi. Seenerisoto sobib taimetoitlasele, kuid sisaldab piima."),
                "en": ("One of us is vegan, another likes mushrooms. What would you recommend and why?",
                       "I'd suggest vegetable soup for the vegan guest. Mushroom risotto suits a vegetarian, but contains milk."),
                "ru": ("Один из нас веган, другой любит грибы. Что вы посоветуете и почему?",
                       "Для вегана я предложу овощной суп. Грибное ризотто подходит вегетарианцу, но содержит молоко."),
            }
            if question == examples[language][0]:
                reply, references = examples[language][1], ["menu_items"]
            elif "current_question_facts" in facts:
                reply, references = facts["current_question_facts"], ["current_question_facts"]
            else:
                return {"content": "fixture reasoning unavailable"}
            return {"content": json.dumps({"reply": reply, "fact_ids": references,
                                           "language": language})}
        return {
            "content": "I can help with restaurant table reservations, the menu and opening hours. How can I help?"
        }


def create_app():
    with patch.dict(
        "os.environ",
        {
            "VOICEBOT_BUSINESS_TYPE": "restaurant",
            "RESTAURANT_DEMO_WRITES": "1",
            "RESTAURANT_STATE_DB": str(Path(_storage.name) / "restaurant.db"),
            "CALLS_DB": str(Path(_storage.name) / "calls.db"),
            "OPERATOR_TOKEN": "restaurant-fixture-operator",
        },
        clear=True,
    ):
        from app import callslog

        callslog.reset_default()
        app = server_app()
        callslog.get_default()
    os.environ["OPERATOR_TOKEN"] = "restaurant-fixture-operator"
    speech = FixtureSpeech()

    def respond(request):
        return httpx.Response(
            200, content=b"fixture-token" if request.url.path.endswith("issueToken")
            else speech.synthesize("fixture"),
        )

    tts = AzureTtsClient(
        "fixture", "fixture", "et-EE-AnuNeural", "et-EE",
        languages={
            "et": ("et-EE-AnuNeural", "et-EE"),
            "en": ("en-US-JennyNeural", "en-US"),
            "ru": ("ru-RU-SvetlanaNeural", "ru-RU"),
        },
        transport=httpx.MockTransport(respond),
    )
    app.state.stack.update(stt=speech, tts=tts, llm_primary=FixtureLlm())
    app.state.capabilities.update(text_turn_ready=True, audio_turn_ready=True)
    return app
