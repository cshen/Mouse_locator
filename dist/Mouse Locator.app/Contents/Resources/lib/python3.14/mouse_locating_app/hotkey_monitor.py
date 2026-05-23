import threading
import time

import Quartz
from PyObjCTools import AppHelper

from .constants import DOUBLE_CTRL_INTERVAL


class HotkeyMonitor:
    def __init__(self, on_locator_requested):
        self._on_locator_requested = on_locator_requested
        self._last_ctrl_press = 0.0
        self._ctrl_down = False
        self._enabled = True
        self._startup_error = None
        self._ready = threading.Event()
        self._thread = None
        self._run_loop = None
        self._tap = None
        self._stop_requested = False

    @property
    def last_error(self):
        return self._startup_error

    @property
    def enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.is_running():
            return True

        self._startup_error = None
        self._ready.clear()
        self._stop_requested = False
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        self._ready.wait()
        return self._startup_error is None

    def stop(self):
        self._stop_requested = True
        if self._run_loop is not None:
            Quartz.CFRunLoopStop(self._run_loop)
            Quartz.CFRunLoopWakeUp(self._run_loop)
        if self._thread is not None:
            self._thread.join(timeout=1)
        self._thread = None
        self._run_loop = None
        self._tap = None

    def _on_event(self, proxy, event_type, event, refcon):
        del proxy, refcon
        if event_type in (
            Quartz.kCGEventTapDisabledByTimeout,
            Quartz.kCGEventTapDisabledByUserInput,
        ):
            if self._tap is not None and not self._stop_requested:
                Quartz.CGEventTapEnable(self._tap, True)
            return event

        if event_type != Quartz.kCGEventFlagsChanged or not self._enabled:
            return event

        flags = Quartz.CGEventGetFlags(event)
        ctrl_now = bool(flags & Quartz.kCGEventFlagMaskControl)

        if ctrl_now and not self._ctrl_down:
            now = time.time()
            if now - self._last_ctrl_press <= DOUBLE_CTRL_INTERVAL:
                AppHelper.callAfter(self._on_locator_requested)
                self._last_ctrl_press = 0.0
            else:
                self._last_ctrl_press = now

        self._ctrl_down = ctrl_now
        return event

    def _run_event_loop(self):
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionListenOnly,
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
            self._on_event,
            None,
        )

        if tap is None:
            self._startup_error = "Could not create event tap."
            self._ready.set()
            return

        source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        self._tap = tap
        self._run_loop = Quartz.CFRunLoopGetCurrent()
        Quartz.CFRunLoopAddSource(self._run_loop, source, Quartz.kCFRunLoopDefaultMode)
        Quartz.CGEventTapEnable(tap, True)
        self._ready.set()
        Quartz.CFRunLoopRun()
        Quartz.CFMachPortInvalidate(tap)
        self._tap = None
        self._run_loop = None
