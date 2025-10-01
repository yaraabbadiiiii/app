import logging
from abc import ABC, abstractmethod


class ITTS(ABC):
    @abstractmethod
    def speak(self, text: str, lang: str):
        pass

    @abstractmethod
    def stop(self):
        pass


class TTSManager(ITTS):
    def __init__(self):
        self.logger = logging.getLogger("TTSManager")

    def speak(self, text: str, lang: str):
        self.logger.info(f"TTS speaking [{lang}]: {text}")
        print(f"[{lang}] {text}")

    def stop(self):
        self.logger.info("Stopping TTS")
        print("TTS stopped")
