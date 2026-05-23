from pathlib import Path

from setuptools import find_packages, setup

from mouse_locating_app.constants import APP_BUNDLE_ID, APP_NAME, APP_VERSION


icon_path = Path("resources/AppIcon.icns")

py2app_options = {
    "argv_emulation": False,
    "packages": find_packages(),
    "includes": [
        "AppKit",
        "Foundation",
        "Quartz",
        "objc",
        "PyObjCTools.AppHelper",
    ],
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": APP_BUNDLE_ID,
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": "1",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
}

if icon_path.exists():
    py2app_options["iconfile"] = str(icon_path)


setup(
    name="mouse-locating",
    version=APP_VERSION,
    description="Menu bar utility that locates the cursor on double Ctrl press.",
    packages=find_packages(),
    app=["menubar_app.py"],
    options={"py2app": py2app_options},
    setup_requires=["py2app"],
)
