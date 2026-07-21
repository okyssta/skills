# Dungeon Market Tycoon — Full Case Study

## Project Overview
A Phaser 3 browser tycoon game where players manage a dungeon marketplace — crafting weapons/armor, selling to heroes, and funding dungeon expeditions. Built for CrazyGames revenue via rewarded ads.

## Final Stats
| Metric | Value | CrazyGames Limit |
|--------|-------|-----------------|
| Total Build Size | 8.7 MB | 50 MB ✅ |
| Game Code | 70 KB | — |
| Source Files | 22 TypeScript | — |
| Audio Files | 14 (trimmed from 194) | — |
| UI Assets | 13 Kenney PNGs | — |
| Icons | 21 game-icons.net PNGs | — |
| Characters | 4 KayKit sprites | — |
| Build Time | ~6 seconds | — |

## Tech Stack
- Phaser 3.80.1 + TypeScript 5.4.5 + Vite 5.4.5
- tsconfig.json: strict: false, esModuleInterop: true, lib: ["ES2020", "DOM"]
- Vite config: @ alias to src/, Phaser manual chunk

## Project Structure (Final)
```
dungeon-market-tycoon/
├── src/
│   ├── main.ts                    # Phaser.Game init
│   ├── config/
│   │   ├── game.config.ts         # 800×600, auto-scale
│   │   ├── gameState.ts           # Central state
│   │   ├── items.ts               # 35+ items, 5 categories
│   │   ├── heroes.ts              # 6 classes
│   │   ├── enemies.ts             # 12 enemies + 4 bosses
│   │   ├── buildings.ts           # 10 buildings
│   │   └── resources.ts           # 10 resource types
│   ├── scenes/                    # 7 scenes
│   └── systems/                   # 7 systems
├── public/assets/
│   ├── ui/         # 13 Kenney UI elements
│   ├── icons/      # 21 game-icons.net PNGs
│   ├── audio/      # 14 files (SFX + 3 music tracks)
│   ├── characters/ # 4 KayKit character sprites
│   ├── fonts/      # 2 Kenney TTF fonts
│   └── buildings/  # 1 dungeon_bg.png
├── CREDITS.md
├── asset_manifest.json
├── .gitignore
└── CHAT_SUMMARY.md
```

## Asset Pipeline
### Source Packs (downloaded via parallel subagents)
- KayKit Dungeon Remastered: 622 files, 18 MB, CC0
- KayKit Character Pack: 72 files, 19 MB, CC0
- Kenney UI Pack: 1,315 files, 1.2 MB, CC0
- Kenney RPG Audio: 54 files, 943 KB, CC0
- Kenney Impact Sounds: 132 files, 783 KB, CC0
- game-icons.net: 21 PNGs, CC BY 3.0
- soundimage.org: 7 MP3 tracks, Royalty-Free

### Processing
1. KayKit 3D → 2D: ImageMagick resize 1024×1024 → 256×256 PNGs
2. Kenney UI: Copy matching PNGs with standardized names
3. Audio trimming: 194 → 14 essential files (saved 7 MB)

### Audio Files Used
```
handleCoins.ogg, click-a.ogg, tap-a.ogg, switch-a.ogg,
footstep_concrete_000.ogg, doorOpen_1.ogg, bookOpen.ogg,
knifeSlice.ogg, impactPunch_heavy_000.ogg, impactMetal_heavy_000.ogg,
impactWood_heavy_000.ogg, fantasy-village-theme.mp3,
fantasy-sky-menu.mp3, fantasy-magic-theme.mp3
```

## Key Patterns
- **BootScene**: Load real assets, fallback to procedural textures
- **Sound SFX**: Always wrap in try/catch
- **Save before transition**: Save state before scene.start()
- **Parallel delegation**: 3 subagents for asset downloads

## CrazyGames Compliance
- Build size: 8.7 MB (< 50 MB) ✅
- Zero TS errors ✅
- Playable in < 30s ✅
- Rewarded ads only ✅
- Credits screen + attribution files ✅
- PEGI 12 safe ✅

## Revenue Strategy
4 rewarded ad placements targeting $300+/month at 400 DAU.

## Git Setup
- Private repo: https://github.com/kyssta-exe/DMT
- .gitignore: node_modules/, dist/, assets/raw/
- First commit pitfall: accidentally included node_modules (5000+ files), fixed with git rm --cached + force push

## Lessons
1. Always verify audio file names before referencing in loader
2. Trim unused audio early (194 → 14 saved 7 MB)
3. Procedural fallbacks = game works without any assets
4. Parallel subagent downloads cut wait time dramatically
5. TS errors are cosmetic — Vite builds fine regardless
6. CHAT_SUMMARY.md enables session continuity
