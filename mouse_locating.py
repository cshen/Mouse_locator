#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyobjc-framework-Cocoa",
#   "pyobjc-framework-Quartz",
# ]
# ///
"""
Console entrypoint for Mouse Locator.

Press Ctrl twice quickly to show a locator animation around the cursor.
"""

from mouse_locating_app.app import run_console_app


if __name__ == "__main__":
    raise SystemExit(run_console_app())
