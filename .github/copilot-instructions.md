# Copilot Instructions

## Project Overview

A macOS CLI tool (`mouse_locating.py`) that triggers the system "find my cursor" animation when the user presses **Ctrl twice in quick succession**. It does this by posting rapid mouse-move events via CoreGraphics, which causes macOS to enlarge the pointer and show the animated locator circle.

## Running

```bash
chmod +x mouse_locating.py
./mouse_locating.py          # uv auto-installs dependencies on first run
```

> Requires **Accessibility permission** for Terminal:  
> System Settings → Privacy & Security → Accessibility

## Architecture

Single file (`mouse_locating.py`) with one class `MouseLocator`:

- **Event tap** (`CGEventTapCreate` with `kCGEventTapOptionListenOnly`) listens globally for `kCGEventFlagsChanged` to detect Ctrl key press/release transitions.
- **Double-press detection** timestamps each Ctrl keydown; if a second press arrives within `DOUBLE_CTRL_INTERVAL` (0.5 s), a shake is triggered.
- **`_shake_cursor()`** reads the current cursor position via `CGEventGetLocation`, then posts a series of `kCGEventMouseMoved` events alternating `±SHAKE_AMPLITUDE` px horizontally at `SHAKE_STEP_DELAY` intervals. This velocity triggers the native macOS animation.
- The CF run loop runs in a **daemon thread** so `KeyboardInterrupt` (Ctrl-C) cleanly exits the main thread.

## Key Constants (top of file)

| Constant | Default | Purpose |
|---|---|---|
| `DOUBLE_CTRL_INTERVAL` | 0.5 s | Window to detect double-press |
| `SHAKE_AMPLITUDE` | 300 px | Horizontal range of cursor shake |
| `SHAKE_CYCLES` | 8 | Back-and-forth repetitions |
| `SHAKE_STEP_DELAY` | 0.007 s | Delay between posted events |

## Stack

- Python 3 / `pyobjc-framework-Quartz` (provides `Quartz`, `CoreFoundation` bindings)
- macOS only — uses `CGEventTap`, `CGEventPost`, `CFRunLoop`
