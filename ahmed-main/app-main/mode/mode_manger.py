# mode/mode_manager.py
from typing import Callable

class ModeManager:


    def __init__(self, bus, offline_mode, online_mode=None,
                 is_online_provider: Callable[[], bool] = lambda: False):
        self.bus = bus
        self.offline = offline_mode
        self.online = online_mode
        self.is_online_provider = is_online_provider
        self._active = None  # offline/online

        # اسمع تغيّر الشبكة من الـBus (يوافق main.py عندك)
        try:
            # Legacy NET_STATUS not used; listen to new events
            self.bus.subscribe("MODE_ONLINE_REQUESTED", self._on_mode_online_requested)
        except Exception as e:
            # لو بدك تشغّله بدون Bus بوضع تجريبي
            print("[ModeManager] WARN: no bus subscribe:", e)

    # -------- lifecycle --------
    def start(self):



        online_now = False
        try:
            online_now = bool(self.is_online_provider())
        except Exception:
            pass

        if online_now and self.online is not None:
            self._switch(self.online)
        else:
            self._switch(self.offline)

    # -------- event handler --------
    def _on_mode_online_requested(self, _data=None):
        try:
            if bool(self.is_online_provider()):
                self.switch_to_online()
        except Exception:
            pass

    # -------- switching --------
    def _switch(self, target):
        if target is None:
            print("[ModeManager] target mode is None (ignored).")
            return
        if self._active is target:
            # لا تعيد تشغيل نفس الوضع بلا داعي
            return

        # أوقف الوضع السابق إن أمكن
        if self._active and hasattr(self._active, "stop"):
            try:
                self._active.stop()
            except Exception as e:
                print("[ModeManager] stop() error:", e)

        self._active = target
        if hasattr(self._active, "start"):
            self._active.start()

    def switch_to_offline(self):
        self._switch(self.offline)

    def switch_to_online(self):
        if self.online is None:
            print("[ModeManager] online mode not provided (placeholder).")
            return
        self._switch(self.online)

    def current(self) -> str:
        return self._active.name() if self._active else "none"

