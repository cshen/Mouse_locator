#!/usr/bin/env python3

from pathlib import Path
import shutil
import subprocess

import AppKit


ICON_SIZES = (16, 32, 128, 256, 512)


def draw_icon(size):
    image = AppKit.NSImage.alloc().initWithSize_((size, size))
    image.lockFocus()

    AppKit.NSColor.clearColor().set()
    AppKit.NSRectFill(AppKit.NSMakeRect(0, 0, size, size))

    center = size / 2
    halo_diameter = size * 0.82
    halo_rect = AppKit.NSMakeRect(
        center - halo_diameter / 2,
        center - halo_diameter / 2,
        halo_diameter,
        halo_diameter,
    )
    AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
        0.14, 0.55, 0.98, 0.18
    ).setFill()
    AppKit.NSBezierPath.bezierPathWithOvalInRect_(halo_rect).fill()

    ring_diameter = size * 0.58
    ring_rect = AppKit.NSMakeRect(
        center - ring_diameter / 2,
        center - ring_diameter / 2,
        ring_diameter,
        ring_diameter,
    )
    ring = AppKit.NSBezierPath.bezierPathWithOvalInRect_(ring_rect)
    ring.setLineWidth_(max(2, size * 0.055))
    AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
        0.24, 0.68, 1.0, 0.96
    ).setStroke()
    ring.stroke()

    dot_diameter = max(6, size * 0.1)
    dot_rect = AppKit.NSMakeRect(
        center - dot_diameter / 2,
        center - dot_diameter / 2,
        dot_diameter,
        dot_diameter,
    )
    AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
        0.24, 0.68, 1.0, 0.72
    ).setFill()
    AppKit.NSBezierPath.bezierPathWithOvalInRect_(dot_rect).fill()

    image.unlockFocus()
    return image


def save_png(image, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    bitmap = AppKit.NSBitmapImageRep.imageRepWithData_(image.TIFFRepresentation())
    png_data = bitmap.representationUsingType_properties_(
        AppKit.NSBitmapImageFileTypePNG,
        {},
    )
    png_data.writeToFile_atomically_(str(destination), True)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    resources_dir = root_dir / "resources"
    iconset_dir = resources_dir / "AppIcon.iconset"
    icns_path = resources_dir / "AppIcon.icns"

    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    iconset_dir.mkdir(parents=True)

    for size in ICON_SIZES:
        save_png(draw_icon(size), iconset_dir / f"icon_{size}x{size}.png")
        retina_size = size * 2
        save_png(
            draw_icon(retina_size),
            iconset_dir / f"icon_{size}x{size}@2x.png",
        )

    subprocess.run(
        [
            "iconutil",
            "-c",
            "icns",
            str(iconset_dir),
            "-o",
            str(icns_path),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
