# Verified Free Asset Sources (CC0 / $0 Confirmed)

*Last verified: 2026-07-05*

## Tier 1: Complete Foundation Packs (Download First)

| Pack | Creator | Platform | License | Direct Link | Verified $0 |
|------|---------|----------|---------|-------------|-------------|
| **Kenney All Packs** (Tiny Town, Tiny Dungeon, Roguelike Characters, Fantasy UI Borders, 1-Bit Pack, Micro Roguelike, Mini Dungeon, Animated Characters 3, Roguelike Dungeon/City/Interior) | Kenney | itch.io | **CC0** | [kenney-assets.itch.io](https://kenney-assets.itch.io/) | ✅ "Name your own price" = $0 works |
| **RGS_Dev Free CC0 Top-Down Tileset Template** (5 color variations, 16×16) | RGS_Dev | itch.io | **CC0** | [rgsdev.itch.io/free-cc0-top-down-tileset-template-pixel-art](https://rgsdev.itch.io/free-cc0-top-down-tileset-template-pixel-art) | ✅ Free CC0 |
| **RGS_Dev Free CC0 Modular Animated Vector Characters 2D** (mix-and-match body parts) | RGS_Dev | itch.io | **CC0** | [rgsdev.itch.io/free-cc0-modular-animated-vector-characters-2d](https://rgsdev.itch.io/free-cc0-modular-animated-vector-characters-2d) | ✅ Free CC0 |
| **Monster Starter Pack** (Goblin, Skeleton, Slime, Bat — fully animated idle/walk/attack/hit/die) | bobddadoo | itch.io | Free | [bobddadoo.itch.io/monster-starter-pack](https://bobddadoo.itch.io/monster-starter-pack) | ✅ Free download |
| **Soulbit Free 16×16 RPG & Roguelike Item Icons** (swords, shields, potions, scrolls, food) | Soulbit | itch.io | Free | Search "Soulbit" on itch.io free assets | ✅ Free |
| **Free Pixel Character Base Pack** (32×32, farming-style animations, top-down) | Kettoman | itch.io | Free | [kettoman.itch.io/free-pixel-character-base-pack-32x32-top-down-farmer-animations](https://kettoman.itch.io/free-pixel-character-base-pack-32x32-top-down-farmer-animations) | ✅ Free |
| **Free Platformer - Retro Lines** (16×16 tileset + animated characters, platformer but usable) | VEXED | itch.io | **CC0** | [v3x3d.itch.io/retro-lines](https://v3x3d.itch.io/retro-lines) | ✅ CC0 Free |

## Tier 2: Specialized Assets

| Asset | Creator | Platform | License | Direct Link | Use Case |
|-------|---------|----------|---------|-------------|----------|
| **Free Pixel Animated Treasure Chests** (Basic & Fancy, 36×25px) | Fossil Bound / Otsoga | itch.io | Free | [itch.io/game-assets/free/tag-chest/tag-pixel-art](https://itch.io/game-assets/free/tag-chest/tag-pixel-art) | Chipp (talking chest) |
| **Free Pixel Gear** (19 lava weapon/armor sprites, 16×16) | Henry Software | itch.io | Free | Search "Free Pixel Gear" on itch.io free assets | Weapons/armor icons |
| **Old Shop Tile Set** (16×16 vector, top-down shop interior) | GabrielaTot | itch.io | Free | Search "Old Shop Tile Set" on itch.io free assets | Shop interior |
| **Free Pixel Art Dungeon Props** (animated doors, statues, pots) | Various | itch.io | Free | Search "dungeon props animated" on itch.io free | Dungeon interactive props |
| **Free Animated Portal** (128×128 pixel portal/door) | liz cheong | itch.io | Free | [itch.io/game-assets/free/tag-portal](https://itch.io/game-assets/free/tag-portal) | Dungeon entrance |
| **Free Pixel Character Base Pack** (3 fully animated, 32×32) | Kettoman | itch.io | Free | [itch.io/game-assets/free/tag-characters/tag-top-down](https://itch.io/game-assets/free/tag-characters/tag-top-down) (page 2) | Extra hero variants |
| **CraftPix Free Slime Mobs** (top-down sprite pack) | CraftPix | craftpix.net | Free | [craftpix.net/freebies/free-slime-mobs-pixel-art-top-down-sprite-pack](https://craftpix.net/freebies/free-slime-mobs-pixel-art-top-down-sprite-pack) | Extra slime variants |

## Tier 3: Audio (All CC0)

### Kenney Audio — Direct Downloads (Preferred over itch.io)

Kenney audio can be downloaded directly from `kenney.nl` — more reliable than itch.io for scripted downloads. All CC0, no price verification needed.

**Extract direct zip URL:** `curl -sL "https://kenney.nl/assets/<pack>" | grep -oP "href='[^']*kenney[^']*\.zip'"`

| Pack | Files | Content | Direct URL Pattern |
|------|-------|---------|-------------------|
| **Kenney UI Pack** | 870 PNG, 434 SVG, 6 sounds, 2 fonts | Buttons, panels, sliders, checkboxes, UI sounds, Kenney Future font | `kenney.nl/assets/ui-pack` |
| **Kenney RPG Audio** | 54 OGG | Footsteps, doors, coins, books, knives, cloth, creaks, metal | `kenney.nl/assets/rpg-audio` |
| **Kenney Impact Sounds** | 132 OGG | Footsteps (5 surfaces), impacts (bell/glass/metal/wood/plate/punch/mining) | `kenney.nl/assets/impact-sounds` |

**Download script pattern:**
```bash
DEST="/root/dungeon-market-tycoon/assets/raw/kenney"
for pack in ui-pack rpg-audio impact-sounds; do
  url=$(curl -sL "https://kenney.nl/assets/$pack" | grep -oP "href='[^']*kenney[^']*\.zip'" | head -1 | sed "s/href='//;s/'//")
  curl -L -o "$DEST/kenney_$pack.zip" "$url"
  unzip -o "$DEST/kenney_$pack.zip" -d "$DEST/$pack/"
done
```

### Other Kenney Audio (via itch.io)

| Pack | Creator | Platform | License | Direct Link |
|------|---------|----------|---------|-------------|
| **Kenney Audio Packs** (UI, impacts, magic, crafting, music) | Kenney | itch.io | **CC0** | [kenney-assets.itch.io](https://kenney-assets.itch.io/) → Audio tag |
| **itch.io CC0 Music** (fantasy, RPG, ambient) | Various | itch.io | **CC0** | [itch.io/game-assets/free/tag-cc0/tag-music](https://itch.io/game-assets/free/tag-cc0/tag-music) |
| **RPG Essentials SFX** (500+ character voices, UI, combat) | Various | itch.io | Free | [itch.io/game-assets/free/tag-sound-effects](https://itch.io/game-assets/free/tag-sound-effects) |

## Search Patterns That Work

```bash
# Kenney packs (all CC0)
site:kenney-assets.itch.io "CC0" "free"
site:kenney.nl/assets "tiny" "rogue" "dungeon"

# itch.io CC0 assets (guaranteed CC0)
itch.io/game-assets/assets-cc0/tag-16x16
itch.io/game-assets/assets-cc0/tag-top-down
itch.io/game-assets/assets-cc0/tag-characters
itch.io/game-assets/assets-cc0/tag-pixel-art
itch.io/game-assets/assets-cc0/tag-tileset
itch.io/game-assets/assets-cc0/tag-dungeon-crawler

# RGS_Dev (all CC0)
site:rgsdev.itch.io "CC0"

# bobddadoo monsters
site:bobddadoo.itch.io "monster" "free"

# Free character bases
site:itch.io "Free CC0 Modular Animated Vector Characters"
site:itch.io "Free Pixel Character Base Pack"

# Free UI
site:kenney-assets.itch.io "Fantasy UI Borders"
site:itch.io "Free CC0 Modular Animated Vector Characters"
```

## Assets That Are NOT Free (Common False Positives)

| Asset | Listed Price | Why It Appears in "Free" Searches |
|-------|--------------|-----------------------------------|
| Modern Interiors RPG Tileset (LimeZu) | $5 | Tagged "pixel-art", "top-down", "16x16" |
| 12 Fully Animated 16×16 Characters (PixelFight) | $3 | Tagged "CC0" in search results but paid |
| Cute Fantasy RPG 16×16 (Pixel_Poem) | Paid | Tagged "free" in collections |
| Tiny Farm RPG Asset Pack | Paid | Tagged "top-down", "pixel-art" |
| Sprout Lands Asset Pack | Paid | Often in "free" curated lists |
| KayKit Dungeon Pack | Paid | Tagged "roguelike", "dungeon" |

**Rule:** Always open the itch.io page → click "Download Now" → verify $0 works before listing.