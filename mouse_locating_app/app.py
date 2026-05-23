import AppKit
from PyObjCTools import AppHelper

from .constants import (
    APP_NAME,
    MONITORING_ACTIVE_MESSAGE,
    MONITORING_PAUSED_MESSAGE,
)
from .hotkey_monitor import HotkeyMonitor
from .overlay import CursorLocatorOverlay
from .permissions import (
    has_listen_event_access,
    open_permission_settings,
    permission_instructions,
    request_listen_event_access,
)
from .status_item import StatusItemController


def _shared_application():
    app = AppKit.NSApplication.sharedApplication()
    if hasattr(AppKit, "NSApplicationActivationPolicyProhibited"):
        app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
    return app


class MenuBarController:
    def __init__(self):
        self._overlay = CursorLocatorOverlay.alloc().init()
        self._monitor = HotkeyMonitor(self.show_locator)
        self._status = StatusItemController.alloc().initWithCallbacks_(
            {
                "toggle_monitoring": self.toggle_monitoring,
                "show_locator": self.show_locator,
                "open_permission_settings": self.open_permission_settings,
                "quit_app": self.quit_app,
            }
        )

    def start(self):
        permission_granted = has_listen_event_access()
        if not permission_granted:
            request_listen_event_access()
            permission_granted = has_listen_event_access()

        if permission_granted:
            started = self._monitor.start()
            if not started:
                self._refresh_status(self._monitor.last_error or permission_instructions())
                return
            self._monitor.set_enabled(True)
            self._refresh_status()
            return

        self._monitor.set_enabled(False)
        self._refresh_status(permission_instructions())

    def stop(self):
        self._monitor.stop()
        self._status.destroy()

    def show_locator(self):
        self._overlay.show()

    def toggle_monitoring(self, should_enable):
        if should_enable:
            if not has_listen_event_access():
                request_listen_event_access()
            if not has_listen_event_access():
                self._monitor.set_enabled(False)
                self._refresh_status(permission_instructions())
                return
            if not self._monitor.is_running() and not self._monitor.start():
                self._refresh_status(self._monitor.last_error or permission_instructions())
                return
            self._monitor.set_enabled(True)
        else:
            self._monitor.set_enabled(False)

        self._refresh_status()

    def open_permission_settings(self):
        open_permission_settings()
        self._refresh_status()

    def quit_app(self):
        AppKit.NSApp().terminate_(None)

    def _refresh_status(self, override_message=None):
        permission_granted = has_listen_event_access()
        enabled = permission_granted and self._monitor.enabled
        if override_message is not None:
            message = override_message
        elif not permission_granted:
            message = permission_instructions()
        elif enabled:
            message = MONITORING_ACTIVE_MESSAGE
        else:
            message = MONITORING_PAUSED_MESSAGE

        self._status.refresh(enabled, permission_granted, message)


def run_console_app():
    _shared_application().finishLaunching()
    overlay = CursorLocatorOverlay.alloc().init()
    monitor = HotkeyMonitor(overlay.show)

    if not has_listen_event_access():
        request_listen_event_access()

    if not has_listen_event_access():
        print("❌  Input Monitoring access is required.")
        print(f"    {permission_instructions()}")
        return 1

    if not monitor.start():
        print(f"❌  {monitor.last_error}")
        print(f"    {permission_instructions()}")
        return 1

    print(f"✅  {APP_NAME} running — press Ctrl twice quickly to locate the cursor.")
    print("    Ctrl-C to quit.\n")

    try:
        AppHelper.runConsoleEventLoop(installInterrupt=True)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()
        print("\nExiting.")

    return 0


def run_menubar_app():
    app = _shared_application()
    controller = MenuBarController()
    controller.start()
    try:
        app.run()
    finally:
        controller.stop()
    return 0
