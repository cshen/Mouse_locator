import AppKit
import Foundation
import Quartz

from .constants import PERMISSION_REQUIRED_MESSAGE

_SETTINGS_URLS = (
    "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
    "x-apple.systempreferences:com.apple.preference.security",
)


def has_listen_event_access():
    checker = getattr(Quartz, "CGPreflightListenEventAccess", None)
    if checker is None:
        return True
    return bool(checker())


def request_listen_event_access():
    requester = getattr(Quartz, "CGRequestListenEventAccess", None)
    if requester is None:
        return has_listen_event_access()
    return bool(requester())


def open_permission_settings():
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    for url_string in _SETTINGS_URLS:
        url = Foundation.NSURL.URLWithString_(url_string)
        if url is not None and workspace.openURL_(url):
            return True
    return False


def permission_instructions():
    return PERMISSION_REQUIRED_MESSAGE
