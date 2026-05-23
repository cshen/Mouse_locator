import AppKit
import Foundation
import objc

from .constants import STATUS_ITEM_TITLE


class StatusItemController(Foundation.NSObject):
    def initWithCallbacks_(self, callbacks):
        self = objc.super(StatusItemController, self).init()
        if self is None:
            return None

        self._callbacks = callbacks
        self._enabled = False
        self._permission_granted = False
        self._status_message = "Starting..."
        self._status_item = None
        self._menu = None
        self._install_status_item()
        return self

    @objc.python_method
    def _install_status_item(self):
        self._status_item = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(
            AppKit.NSVariableStatusItemLength
        )
        button = self._status_item.button()
        button.setTitle_(STATUS_ITEM_TITLE)
        button.setToolTip_(self._status_message)
        self._rebuild_menu()

    @objc.python_method
    def refresh(self, enabled, permission_granted, status_message):
        self._enabled = enabled
        self._permission_granted = permission_granted
        self._status_message = status_message
        button = self._status_item.button()
        button.setTitle_(STATUS_ITEM_TITLE if permission_granted else f"{STATUS_ITEM_TITLE}!")
        button.setToolTip_(status_message)
        self._rebuild_menu()

    @objc.python_method
    def destroy(self):
        if self._status_item is not None:
            AppKit.NSStatusBar.systemStatusBar().removeStatusItem_(self._status_item)
            self._status_item = None
            self._menu = None

    @objc.python_method
    def _rebuild_menu(self):
        menu = AppKit.NSMenu.alloc().init()

        status_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            self._status_message, None, ""
        )
        status_item.setEnabled_(False)
        menu.addItem_(status_item)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        toggle_title = "Disable Monitoring" if self._enabled else "Enable Monitoring"
        toggle_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            toggle_title,
            "toggleMonitoring:",
            "",
        )
        toggle_item.setTarget_(self)
        menu.addItem_(toggle_item)

        test_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Show Locator Now",
            "showLocatorNow:",
            "",
        )
        test_item.setTarget_(self)
        menu.addItem_(test_item)

        permissions_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Open Permission Settings",
            "openPermissionSettings:",
            "",
        )
        permissions_item.setTarget_(self)
        menu.addItem_(permissions_item)

        menu.addItem_(AppKit.NSMenuItem.separatorItem())

        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit",
            "quitApp:",
            "q",
        )
        quit_item.setTarget_(self)
        menu.addItem_(quit_item)

        self._status_item.setMenu_(menu)
        self._menu = menu

    def toggleMonitoring_(self, sender):
        del sender
        callback = self._callbacks.get("toggle_monitoring")
        if callback is not None:
            callback(not self._enabled)

    def showLocatorNow_(self, sender):
        del sender
        callback = self._callbacks.get("show_locator")
        if callback is not None:
            callback()

    def openPermissionSettings_(self, sender):
        del sender
        callback = self._callbacks.get("open_permission_settings")
        if callback is not None:
            callback()

    def quitApp_(self, sender):
        del sender
        callback = self._callbacks.get("quit_app")
        if callback is not None:
            callback()
