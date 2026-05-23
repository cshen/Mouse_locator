Mouse Locator is a small macOS utility that shows a locator animation around the pointer when you press **Ctrl twice quickly**.

## Console mode

```bash
chmod +x mouse_locating.py
./mouse_locating.py
```

## Menubar app build

```bash
./scripts/build_app.sh
open "dist/Mouse Locator.app"
open "dist/Mouse Locator.dmg"
```

The build script now produces both `dist/Mouse Locator.app` and `dist/Mouse Locator.dmg`. It requires the `create-dmg` CLI (`brew install create-dmg`).

The generated app is a **menubar-only** app with:

- enable/disable monitoring
- show locator now
- open permission settings
- quit

## Permissions

Global key monitoring requires **Input Monitoring** access in System Settings. On some macOS versions you may also see Accessibility-related prompts or guidance.
