# Icons Changelog

## 2025-11-06 - Initial Icon Structure

### Created Structure

Organized icons into a professional directory structure with subdirectories for different use cases:

- **Main icons** (`/icons`): Multiple sizes from 64px to 1024px
- **Web assets** (`/icons/web`): Favicons and PWA manifest
- **Start9 package** (`/icons/start9`): Icon for Start9 deployment
- **Social media** (`/icons/social`): Open Graph and square images

### Source Files

- `bxs-emblem.svg` - Vector source (1024x1024)
- `bxs003.png` - Photo source (1800x1800)

### Generated Assets

#### Main Icons (in `/icons`)
- `bxs-1024.png` - Highest resolution for app stores
- `bxs-512.png` - Standard high-res icon
- `bxs-256.png` - Desktop application icon
- `bxs-192.png` - PWA icon size
- `bxs-128.png` - Medium UI elements
- `bxs-64.png` - Small UI elements

#### Monochrome Variants (in `/icons`)
- `bxs-512-mono-dark.png` - For light themes
- `bxs-512-mono-light.png` - For dark themes

#### Web Assets (in `/icons/web`)
- `favicon-32.png` - Standard favicon
- `favicon-16.png` - Small favicon
- `favicon.ico` - Multi-size ICO (16, 32, 48)
- `site.webmanifest` - PWA manifest with theme colors

#### Start9 Package (in `/icons/start9`)
- `icon.png` - 512x512 icon for Start9 manifest

#### Social Media (in `/icons/social`)
- `og-1200x630.png` - Open Graph / Twitter card
- `square-1080.png` - Square social sharing (Instagram, etc.)

### Tools Created

- `../tools/generate_icons.py` - Automated icon generation script
  - Handles SVG to PNG conversion (with cairosvg or ImageMagick)
  - Falls back to PNG resizing if SVG tools unavailable
  - Generates all sizes and variants
  - Creates favicons and web manifest
  - Generates social media images with branded backgrounds

### Documentation

- `README.md` - Complete documentation with:
  - Directory structure overview
  - Design elements and color palette
  - Usage guidelines for web, Start9, and apps
  - Size reference table
  - Regeneration instructions

### Integration

Updated main project `README.md` to reference the icons directory in the repository layout section.

### Color Palette Used

- Navy: `#0B1E36` (backgrounds, theme color)
- Orange: `#F7931A` (Bitcoin logo, accents)
- Off-white: `#FAF7F2` (text, light elements, PWA background)
- Gold: `#FFC24A` (orbital accents)

### Regeneration

All derived assets can be regenerated with:
```bash
python3 tools/generate_icons.py
```

This ensures reproducibility and makes it easy to update all sizes if the source images change.

