import logging


class OutputService:
    def __init__(self, tts_engine):
        self.tts = tts_engine
        self.feedback_lang = "AR"
        self.logger = logging.getLogger("OutputService")

    def play_tts(self, text: str, lang: str):
        self.logger.info(f"Play TTS in {lang}: {text}")
        self.tts.speak(text, lang)

    def play_tone(self, tone_type: str):
        tones = {
            "capture_ok": "Beep ✅",
            "mode_switch": "Beep 🔄",
            "volume_step": "Beep 🔊",
            "language_changed": "Beep 🌐",
        }
        tone = tones.get(tone_type, "Beep ❓")
        self.logger.info(f"Playing tone: {tone_type}")
        print(f"[Tone] {tone}")

    def toggle_feedback_language(self):
        self.feedback_lang = "EN" if self.feedback_lang == "AR" else "AR"
        msg = f"Language changed to {self.feedback_lang}"
        self.logger.info(msg)
        self.play_tone("language_changed")
        self.tts.speak(msg, self.feedback_lang)
