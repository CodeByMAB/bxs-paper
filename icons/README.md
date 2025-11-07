# Bitcoin Seconds (BXS) Icons

This directory contains all icon assets for the Bitcoin Seconds project in various sizes and formats.

## 📁 Directory Structure

```
/icons
├─ bxs-emblem.svg          # Source SVG emblem (vector)
├─ bxs003.png              # Source PNG image
├─ bxs-1024.png            # Main icon 1024x1024
├─ bxs-512.png             # Main icon 512x512
├─ bxs-256.png             # Main icon 256x256
├─ bxs-192.png             # Main icon 192x192
├─ bxs-128.png             # Main icon 128x128
├─ bxs-64.png              # Main icon 64x64
├─ bxs-512-mono-dark.png   # Monochrome dark variant
├─ bxs-512-mono-light.png  # Monochrome light variant
│
├─ /web
│  ├─ favicon-32.png       # 32x32 favicon
│  ├─ favicon-16.png       # 16x16 favicon
│  ├─ favicon.ico          # Multi-size ICO file (16, 32, 48)
│  └─ site.webmanifest     # Web manifest for PWA
│
├─ /start9
│  └─ icon.png             # Start9 package icon (512x512)
│
└─ /social
   ├─ og-1200x630.png      # Open Graph image for social sharing
   └─ square-1080.png      # Square social media image
```

## 🎨 Design Elements

The BXS icon features:
- **Central Bitcoin symbol** in orange (#F7931A)
- **Clock/time motif** representing the "seconds" concept
- **Concentric circles** with orbital patterns
- **Navy blue background** (#0B1E36)
- **Off-white accents** (#FAF7F2)

## 🔧 Regenerating Icons

All icons (except the source files) are generated from the source images using the included script:

```bash
python3 tools/generate_icons.py
```

### Prerequisites

The script requires:
- Python 3.7+
- Pillow (PIL) library

Optional (for higher quality SVG conversion):
- cairosvg library, or
- ImageMagick

Install dependencies:
```bash
pip install Pillow cairosvg
```

## 📝 Usage Guidelines

### Web Usage

Include in your HTML `<head>`:

```html
<!-- Favicons -->
<link rel="icon" type="image/png" sizes="32x32" href="/icons/web/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/icons/web/favicon-16.png">
<link rel="shortcut icon" href="/icons/web/favicon.ico">

<!-- Web App Manifest -->
<link rel="manifest" href="/icons/web/site.webmanifest">

<!-- Open Graph / Social Media -->
<meta property="og:image" content="/icons/social/og-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

### Start9 Package

The Start9 icon is automatically referenced in the manifest:

```yaml
# manifest.yaml
icon: icon.png  # Refers to /start9/icon.png
```

### General Application Icons

Use the appropriately sized PNG from the main icons directory:
- Desktop applications: `bxs-512.png` or `bxs-256.png`
- Mobile apps: `bxs-1024.png` (iOS), `bxs-512.png` (Android)
- Small UI elements: `bxs-128.png` or `bxs-64.png`
- Dark themes: `bxs-512-mono-light.png`
- Light themes: `bxs-512-mono-dark.png`

## 🎯 Size Reference

| Size | Use Case |
|------|----------|
| 1024×1024 | iOS App Store, high-res displays |
| 512×512 | Android, general purpose, Start9 |
| 256×256 | Desktop applications |
| 192×192 | PWA icons, Android home screen |
| 128×128 | List views, medium UI elements |
| 64×64 | Small UI elements, notifications |
| 32×32 | Browser tabs, small icons |
| 16×16 | Minimal display, legacy support |

## 📄 License

These icons are part of the Bitcoin Seconds project. See the main LICENSE file for details.

## 🔗 Related Files

- Source emblem: `bxs-emblem.svg`
- Source photo: `bxs003.png`
- Generator script: `../tools/generate_icons.py`

