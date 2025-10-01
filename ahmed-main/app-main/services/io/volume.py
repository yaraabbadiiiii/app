# io/volume.py
class Volume:
    """
    محاكاة للتحكم بالصوت.
    """
    def __init__(self, bus):
        self.bus = bus
        self.level = 0.5  # مستوى مبدئي 50%

    def increase(self):
        self.level = min(1.0, self.level + 0.1)
        self.bus.emit("VOL_CHANGED", {"level": self.level})

    def decrease(self):
        self.level = max(0.0, self.level - 0.1)
        self.bus.emit("VOL_CHANGED", {"level": self.level})
