#!/usr/bin/env python3
"""
Generate all icon sizes and variants for the BXS project.

This script creates:
- Multiple PNG sizes from the source image
- Monochrome variants (dark and light)
- Favicons for web
- Social media images
- Start9 icon
"""

import sys
from pathlib import Path
from PIL import Image, ImageOps
import subprocess

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
ICONS_DIR = PROJECT_ROOT / "icons"
SOURCE_PNG = ICONS_DIR / "bxs003.png"
SOURCE_SVG = ICONS_DIR / "bxs-emblem.svg"

# Output directories
WEB_DIR = ICONS_DIR / "web"
START9_DIR = ICONS_DIR / "start9"
SOCIAL_DIR = ICONS_DIR / "social"


def ensure_directories():
    """Create output directories if they don't exist."""
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    START9_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
    print("✓ Created directory structure")


def convert_svg_to_png(svg_path, output_path, size):
    """Convert SVG to PNG at specified size using cairosvg or ImageMagick."""
    try:
        import cairosvg

        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(output_path),
            output_width=size,
            output_height=size,
        )
        print(f"✓ Generated {output_path.name} ({size}x{size}) from SVG using cairosvg")
        return True
    except ImportError:
        # Fallback to ImageMagick if available
        try:
            subprocess.run(
                [
                    "convert",
                    "-background",
                    "none",
                    "-density",
                    "300",
                    "-resize",
                    f"{size}x{size}",
                    str(svg_path),
                    str(output_path),
                ],
                check=True,
                capture_output=True,
            )
            print(
                f"✓ Generated {output_path.name} ({size}x{size}) from SVG using ImageMagick"
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ Could not convert SVG: cairosvg and ImageMagick not available")
            return False


def generate_main_icons():
    """Generate main icon sizes."""
    sizes = [1024, 512, 256, 192, 128, 64]

    # Try to use SVG first for better quality
    use_svg = SOURCE_SVG.exists()

    if use_svg:
        print("\nGenerating main icons from SVG...")
        for size in sizes:
            output_path = ICONS_DIR / f"bxs-{size}.png"
            if not convert_svg_to_png(SOURCE_SVG, output_path, size):
                use_svg = False
                break

    # Fallback to resizing PNG
    if not use_svg:
        print("\nGenerating main icons from PNG...")
        if not SOURCE_PNG.exists():
            print(f"✗ Source image not found: {SOURCE_PNG}")
            return

        source = Image.open(SOURCE_PNG)
        # Convert to RGBA if not already
        if source.mode != "RGBA":
            source = source.convert("RGBA")

        for size in sizes:
            output_path = ICONS_DIR / f"bxs-{size}.png"
            resized = source.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(output_path, "PNG", optimize=True)
            print(f"✓ Generated {output_path.name} ({size}x{size})")


def generate_monochrome_variants():
    """Generate monochrome dark and light variants."""
    print("\nGenerating monochrome variants...")

    source_path = ICONS_DIR / "bxs-512.png"
    if not source_path.exists():
        print(f"✗ Source file not found: {source_path}")
        return

    source = Image.open(source_path)
    if source.mode != "RGBA":
        source = source.convert("RGBA")

    # Create monochrome dark (dark icon on transparent)
    dark = source.convert("L")  # Convert to grayscale
    dark = ImageOps.invert(dark)  # Invert
    # Convert back to RGBA keeping alpha channel
    dark_rgba = Image.new("RGBA", source.size)
    alpha = source.split()[3] if source.mode == "RGBA" else None
    if alpha:
        # Make it dark by reducing brightness
        dark_pixels = dark.point(lambda x: x * 0.3)  # Dark blue-ish
        dark_rgba = Image.merge("RGBA", (dark_pixels, dark_pixels, dark_pixels, alpha))

    output_dark = ICONS_DIR / "bxs-512-mono-dark.png"
    dark_rgba.save(output_dark, "PNG", optimize=True)
    print(f"✓ Generated {output_dark.name}")

    # Create monochrome light (light icon on transparent)
    light = source.convert("L")
    light_pixels = light.point(lambda x: 255 - (255 - x) * 0.3)  # Lighter
    light_rgba = Image.new("RGBA", source.size)
    if alpha:
        light_rgba = Image.merge(
            "RGBA", (light_pixels, light_pixels, light_pixels, alpha)
        )

    output_light = ICONS_DIR / "bxs-512-mono-light.png"
    light_rgba.save(output_light, "PNG", optimize=True)
    print(f"✓ Generated {output_light.name}")


def generate_web_icons():
    """Generate web favicons and manifest."""
    print("\nGenerating web icons...")

    source_path = ICONS_DIR / "bxs-512.png"
    if not source_path.exists():
        print(f"✗ Source file not found: {source_path}")
        return

    source = Image.open(source_path)
    if source.mode != "RGBA":
        source = source.convert("RGBA")

    # Generate PNG favicons
    for size in [32, 16]:
        output_path = WEB_DIR / f"favicon-{size}.png"
        resized = source.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(output_path, "PNG", optimize=True)
        print(f"✓ Generated {output_path.name} ({size}x{size})")

    # Generate ICO file (multi-size)
    ico_path = WEB_DIR / "favicon.ico"
    sizes = [(16, 16), (32, 32), (48, 48)]
    icons = []
    for size in sizes:
        resized = source.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    icons[0].save(ico_path, format="ICO", sizes=[(s[0], s[1]) for s in sizes])
    print("✓ Generated favicon.ico (multi-size)")

    # Generate site.webmanifest
    manifest = {
        "name": "Bitcoin Seconds",
        "short_name": "BXS",
        "icons": [
            {"src": "/icons/bxs-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icons/bxs-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": "#0B1E36",
        "background_color": "#FAF7F2",
        "display": "standalone",
    }

    import json

    manifest_path = WEB_DIR / "site.webmanifest"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print("✓ Generated site.webmanifest")


def generate_start9_icon():
    """Generate Start9 icon."""
    print("\nGenerating Start9 icon...")

    source_path = ICONS_DIR / "bxs-512.png"
    if not source_path.exists():
        print(f"✗ Source file not found: {source_path}")
        return

    source = Image.open(source_path)
    if source.mode != "RGBA":
        source = source.convert("RGBA")

    # Start9 typically uses 512x512
    output_path = START9_DIR / "icon.png"
    resized = source.resize((512, 512), Image.Resampling.LANCZOS)
    resized.save(output_path, "PNG", optimize=True)
    print("✓ Generated icon.png for Start9")


def generate_social_images():
    """Generate social media images."""
    print("\nGenerating social media images...")

    source_path = ICONS_DIR / "bxs-1024.png"
    if not source_path.exists():
        print(f"✗ Source file not found: {source_path}")
        return

    source = Image.open(source_path)
    if source.mode != "RGBA":
        source = source.convert("RGBA")

    # Open Graph image (1200x630)
    og = Image.new("RGB", (1200, 630), color=(11, 30, 54))  # Navy background
    # Center the icon
    icon_size = 500
    resized = source.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    x = (1200 - icon_size) // 2
    y = (630 - icon_size) // 2
    og.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)

    og_path = SOCIAL_DIR / "og-1200x630.png"
    og.save(og_path, "PNG", optimize=True)
    print("✓ Generated og-1200x630.png")

    # Square social image (1080x1080)
    square = Image.new("RGB", (1080, 1080), color=(11, 30, 54))
    icon_size = 900
    resized = source.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    x = (1080 - icon_size) // 2
    y = (1080 - icon_size) // 2
    square.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)

    square_path = SOCIAL_DIR / "square-1080.png"
    square.save(square_path, "PNG", optimize=True)
    print("✓ Generated square-1080.png")


def main():
    """Main execution function."""
    print("Bitcoin Seconds Icon Generator")
    print("=" * 50)

    if not SOURCE_PNG.exists() and not SOURCE_SVG.exists():
        print("✗ No source files found!")
        print(f"  Expected: {SOURCE_PNG}")
        print(f"  Or: {SOURCE_SVG}")
        sys.exit(1)

    print("\nSource files:")
    if SOURCE_PNG.exists():
        print(f"  • PNG: {SOURCE_PNG.name}")
    if SOURCE_SVG.exists():
        print(f"  • SVG: {SOURCE_SVG.name}")

    ensure_directories()
    generate_main_icons()
    generate_monochrome_variants()
    generate_web_icons()
    generate_start9_icon()
    generate_social_images()

    print("\n" + "=" * 50)
    print("✓ All icons generated successfully!")
    print("\nOutput directories:")
    print(f"  • Main icons: {ICONS_DIR}")
    print(f"  • Web icons: {WEB_DIR}")
    print(f"  • Start9 icon: {START9_DIR}")
    print(f"  • Social images: {SOCIAL_DIR}")


if __name__ == "__main__":
    main()
