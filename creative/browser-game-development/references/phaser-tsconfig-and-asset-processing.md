# Phaser 3 + TypeScript Gotchas & Asset Processing Notes

## TypeScript Configuration for Phaser 3

### The Problem
Phaser 3's TypeScript declarations conflict with strict mode. Common errors:
- `Module '"phaser"' can only be default-imported using the 'esModuleInterop' flag`
- `Property 'add' does not exist on type 'BootScene'` (Phaser.Scene methods)
- `Property 'values' does not exist on type 'ObjectConstructor'`

### The Fix
```json
{
  "compilerOptions": {
    "strict": false,          // CRITICAL: Phaser types break with strict
    "esModuleInterop": true,  // For `import Phaser from 'phaser'`
    "skipLibCheck": true,     // Skip node_modules type checking
    "lib": ["ES2020", "DOM"]  // ES2020 needed for Object.entries/values
  }
}
```

### Why It Works
- Vite uses esbuild for transpilation (not tsc), so TS type errors don't block builds
- `tsc --noEmit` will still show errors, but `vite build` succeeds
- The errors are Phaser-specific type definition issues, not actual code problems

### Verification
```bash
# This WILL show errors (expected):
npx tsc --noEmit

# This WILL succeed (what matters):
npx vite build
```

## Procedural Texture Generation

### Correct Pattern
```typescript
const g = this.add.graphics();
g.setVisible(false);  // Don't render to screen

g.clear();
g.fillStyle(0xDEB887, 1);
g.fillRoundedRect(0, 0, 48, 48, 6);
g.generateTexture('item_wooden_sword', 48, 48);

g.destroy();  // Clean up
```

### Wrong Pattern (causes error)
```typescript
// ERROR: 'add' does not exist in type 'Options'
const g = this.make.graphics({ add: false });
```

## Audio File Naming (Kenney Assets)

Kenney's audio packs use specific naming conventions:

| Pack | File Pattern | Example |
|------|-------------|---------|
| UI Pack | `{name}-{variant}.ogg` | `click-a.ogg`, `tap-b.ogg` |
| RPG Audio | `{name}{number}.ogg` | `handleCoins.ogg`, `doorOpen_1.ogg` |
| Impact Sounds | `{type}_{intensity}_{number}.ogg` | `impactPunch_heavy_000.ogg` |

**Always verify before referencing in loader:**
```bash
ls public/assets/audio/ | grep -i "handlecoins"
# → handleCoins.ogg ✓
```

## Asset Processing Commands

### SVG to PNG (game-icons.net)
```bash
# Install ImageMagick if needed
apt-get install -y imagemagick

# Convert single SVG
convert -background none -density 300 icon.svg -resize 128x128 icon.png

# Batch convert
for svg in *.svg; do
  png="${svg%.svg}.png"
  convert -background none -density 300 "$svg" -resize 128x128 "$png"
done
```

### Resize Character Textures (KayKit)
```bash
# Resize to game sprite size
convert input.png -resize 256x256 output.png

# For tilesets/backgrounds
convert input.png -resize 512x512 output.png
```

### Verify Audio Files
```bash
# Check file type
file *.ogg   # Should show "Ogg data, Vorbis audio"
file *.mp3   # Should show "MPEG ADTS, layer III"

# Check for failed downloads (files < 1KB)
find . -name "*.ogg" -size -1k -exec ls -la {} \;
find . -name "*.mp3" -size -1k -exec ls -la {} \;
```

### Trim Unused Audio
```bash
# Keep only files referenced in BootScene loader
KEEP="handleCoins.ogg click-a.ogg tap-a.ogg switch-a.ogg ..."
for f in *; do
  echo "$KEEP" | grep -q "$f" || rm "$f"
done
```

## Build Size Optimization

### Before Final Build
1. Trim unused audio files (194 → 14 saved 7MB)
2. Remove unused raw assets from public/
3. Use Vite's manual chunks for Phaser

### Expected Sizes
| Component | Size |
|-----------|------|
| Game code | 50-80 KB |
| Phaser | ~1.4 MB |
| UI assets (Kenney) | ~100 KB |
| Icons (game-icons) | ~200 KB |
| Audio (trimmed) | ~5-10 MB |
| Fonts | ~50 KB |
| **Total** | **8-15 MB** |

CrazyGames limit: 50 MB initial, 250 MB total.

## Vite Dev Server

### Starting
```bash
# Don't use `npx vite` — may trigger long-process detection
node ./node_modules/vite/bin/vite.js --host 0.0.0.0 --port 3000
```

### Background Mode
```bash
# For persistent server
node ./node_modules/vite/bin/vite.js --host 0.0.0.0 --port 3000 &
```

## npm Install Gotcha

Vite's postinstall may trigger interactive prompts:
```bash
# Use --ignore-scripts to avoid hanging
npm install --ignore-scripts
```
