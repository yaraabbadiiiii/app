class VolumeRoller:
    def __init__(self, output_service, session_store):
        self.output = output_service
        self.session_store = session_store
        self.volume = self.session_store.get("volume", 50)

    def increase(self):
        if self.volume < 100:
            self.volume += 5
            self._save_and_feedback()

    def decrease(self):
        if self.volume > 0:
            self.volume -= 5
            self._save_and_feedback()

    def _save_and_feedback(self):
        self.session_store["volume"] = self.volume
        print(f"Volume set to {self.volume}")
        self.output.play_tone("volume_step")
