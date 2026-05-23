import time

import AppKit
import Foundation
import Quartz
import objc

from .constants import (
    LOCATOR_DURATION,
    LOCATOR_RING_WIDTH,
    LOCATOR_SIZE,
    LOCATOR_TICK_INTERVAL,
)


class LocatorView(AppKit.NSView):
    def setProgress_(self, progress):
        self.progress = progress
        self.setNeedsDisplay_(True)

    def setCursorCenter_(self, point):
        self.cursor_center = point

    def drawRect_(self, dirty_rect):
        del dirty_rect
        progress = min(max(getattr(self, "progress", 0.0), 0.0), 1.0)
        fade = max(0.0, 1.0 - progress)
        if fade <= 0.0:
            return

        bounds = self.bounds()
        cp = getattr(self, "cursor_center", None)
        if cp is not None:
            center_x = cp.x
            center_y = cp.y
        else:
            center_x = AppKit.NSMidX(bounds)
            center_y = AppKit.NSMidY(bounds)

        halo_diameter = 80 + 220 * progress
        halo_rect = AppKit.NSMakeRect(
            center_x - halo_diameter / 2,
            center_y - halo_diameter / 2,
            halo_diameter,
            halo_diameter,
        )
        AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.14, 0.55, 0.98, 0.16 * fade
        ).setFill()
        AppKit.NSBezierPath.bezierPathWithOvalInRect_(halo_rect).fill()

        ring_diameter = 48 + 180 * progress
        ring_rect = AppKit.NSMakeRect(
            center_x - ring_diameter / 2,
            center_y - ring_diameter / 2,
            ring_diameter,
            ring_diameter,
        )
        ring = AppKit.NSBezierPath.bezierPathWithOvalInRect_(ring_rect)
        ring.setLineWidth_(LOCATOR_RING_WIDTH)
        AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.24, 0.68, 1.0, 0.92 * fade
        ).setStroke()
        ring.stroke()

        dot_diameter = 10
        dot_rect = AppKit.NSMakeRect(
            center_x - dot_diameter / 2,
            center_y - dot_diameter / 2,
            dot_diameter,
            dot_diameter,
        )
        AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.24, 0.68, 1.0, 0.55 * fade
        ).setFill()
        AppKit.NSBezierPath.bezierPathWithOvalInRect_(dot_rect).fill()


class CursorLocatorOverlay(Foundation.NSObject):
    def init(self):
        self = objc.super(CursorLocatorOverlay, self).init()
        if self is None:
            return None

        self._window = None
        self._view = None
        self._timer = None
        self._animation_started_at = 0.0
        return self

    @objc.python_method
    def _ensure_window(self):
        if self._window is not None:
            return

        rect = AppKit.NSMakeRect(0, 0, LOCATOR_SIZE, LOCATOR_SIZE)
        window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            AppKit.NSWindowStyleMaskBorderless,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        window.setOpaque_(False)
        window.setBackgroundColor_(AppKit.NSColor.clearColor())
        window.setIgnoresMouseEvents_(True)
        window.setHasShadow_(False)
        window.setReleasedWhenClosed_(False)
        window.setLevel_(Quartz.CGWindowLevelForKey(Quartz.kCGOverlayWindowLevelKey))
        window.setCollectionBehavior_(
            AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
            | AppKit.NSWindowCollectionBehaviorStationary
            | AppKit.NSWindowCollectionBehaviorIgnoresCycle
        )

        view = LocatorView.alloc().initWithFrame_(rect)
        view.setWantsLayer_(True)
        view.layer().setBackgroundColor_(AppKit.NSColor.clearColor().CGColor())
        window.setContentView_(view)

        self._window = window
        self._view = view

    @objc.python_method
    def _screen_for_point(self, point):
        for screen in AppKit.NSScreen.screens():
            frame = screen.frame()
            if (
                frame.origin.x <= point.x <= frame.origin.x + frame.size.width
                and frame.origin.y <= point.y <= frame.origin.y + frame.size.height
            ):
                return screen

        screens = AppKit.NSScreen.screens()
        return screens[0] if screens else None

    @objc.python_method
    def _window_origin_for_point(self, point):
        origin_x = point.x - LOCATOR_SIZE / 2
        origin_y = point.y - LOCATOR_SIZE / 2
        screen = self._screen_for_point(point)
        if screen is None:
            return AppKit.NSMakePoint(origin_x, origin_y)

        frame = screen.frame()
        max_x = frame.origin.x + frame.size.width - LOCATOR_SIZE
        max_y = frame.origin.y + frame.size.height - LOCATOR_SIZE
        return AppKit.NSMakePoint(
            min(max(origin_x, frame.origin.x), max_x),
            min(max(origin_y, frame.origin.y), max_y),
        )

    def show(self):
        self._ensure_window()

        point = AppKit.NSEvent.mouseLocation()
        origin = self._window_origin_for_point(point)
        self._window.setFrameOrigin_(origin)
        local_center = AppKit.NSMakePoint(point.x - origin.x, point.y - origin.y)
        self._view.setCursorCenter_(local_center)
        self._view.setProgress_(0.0)
        self._window.orderFrontRegardless()

        if self._timer is not None:
            self._timer.invalidate()

        self._animation_started_at = time.monotonic()
        self._timer = Foundation.NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            LOCATOR_TICK_INTERVAL, self, "tick:", None, True
        )

    def tick_(self, timer):
        progress = min(
            (time.monotonic() - self._animation_started_at) / LOCATOR_DURATION, 1.0
        )
        self._view.setProgress_(progress)

        if progress >= 1.0:
            timer.invalidate()
            self._timer = None
            self._window.orderOut_(None)
