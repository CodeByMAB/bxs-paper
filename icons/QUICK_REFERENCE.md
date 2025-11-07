# BXS Icons - Quick Reference Card

## 🎯 Most Common Use Cases

### For Web Development
```html
<!-- In your HTML <head> -->
<link rel="icon" type="image/png" sizes="32x32" href="/icons/web/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/icons/web/favicon-16.png">
<link rel="shortcut icon" href="/icons/web/favicon.ico">
<link rel="manifest" href="/icons/web/site.webmanifest">
```

### For Social Media Sharing
```html
<!-- Open Graph / Facebook / Twitter -->
<meta property="og:image" content="/icons/social/og-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="/icons/social/og-1200x630.png">
```

### For Start9 Package
```yaml
# manifest.yaml
icon: icon.png  # Located at icons/start9/icon.png
```

### For Mobile Apps
- **iOS App Store**: Use `icons/bxs-1024.png`
- **Android**: Use `icons/bxs-512.png`
- **PWA Home Screen**: Use `icons/bxs-192.png` (referenced in site.webmanifest)

## 📏 Size Selection Guide

| You Need... | Use This File |
|-------------|--------------|
| App store submission | `bxs-1024.png` |
| General purpose icon | `bxs-512.png` |
| Desktop app icon | `bxs-256.png` |
| PWA icon | `bxs-192.png` |
| Toolbar/menu icon | `bxs-128.png` |
| Notification icon | `bxs-64.png` |
| Browser tab | `web/favicon-32.png` |
| Dark mode UI | `bxs-512-mono-light.png` |
| Light mode UI | `bxs-512-mono-dark.png` |
| Social sharing | `social/og-1200x630.png` |
| Instagram/square post | `social/square-1080.png` |

## 🎨 Brand Colors

```css
--bxs-navy: #0B1E36;      /* Primary background */
--bxs-orange: #F7931A;     /* Bitcoin orange, accents */
--bxs-off-white: #FAF7F2;  /* Light background, text */
--bxs-gold: #FFC24A;       /* Accent, highlights */
```

## 🔧 Regenerating All Icons

If you update the source images, regenerate everything with:

```bash
python3 tools/generate_icons.py
```

**Prerequisites**: `pip install Pillow`  
**Optional** (better quality): `pip install cairosvg` or install ImageMagick

## 📁 File Locations

```
icons/
├── bxs-{size}.png          # Main icons (1024, 512, 256, 192, 128, 64)
├── bxs-512-mono-{variant}  # Monochrome (dark, light)
├── web/
│   ├── favicon-{size}.png  # 32, 16
│   ├── favicon.ico
│   └── site.webmanifest
├── start9/
│   └── icon.png
└── social/
    ├── og-1200x630.png
    └── square-1080.png
```

## ✅ Quality Checklist

- [x] All sizes generated from source
- [x] Monochrome variants for dark/light themes
- [x] Multi-size ICO file for browser compatibility
- [x] PWA manifest with correct paths and theme colors
- [x] Social media images with branded backgrounds
- [x] Start9 icon ready for deployment
- [x] Documentation complete
- [x] Regeneration script tested

## 📞 Need Help?

- Full documentation: See `README.md` in this directory
- Change history: See `CHANGELOG.md`
- Generator script: `../tools/generate_icons.py`

---

**Bitcoin Seconds Project** • [CC BY 4.0 License](../LICENSE)

