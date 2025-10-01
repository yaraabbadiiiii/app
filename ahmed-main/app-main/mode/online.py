
class OnlineOrchestrator:
    def __init__(self, bus):
        self.bus = bus
        self._started = False

    def name(self) -> str:
        return "online"

    def start(self):
        self._started = True
        # لاحقًا: ربط WS/HTTP وما يلزم

    def stop(self):
        self._started = False
