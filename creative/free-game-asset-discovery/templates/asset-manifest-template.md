# Asset Manifest Template

*Use this template for new game projects. Replace `[GAME_NAME]` and fill in each section.*

---

## ✅ VERIFIED FREE Assets for [GAME_NAME]

### Game Bible Specs
- **Perspective**: [top-down / side-scroller / isometric / platformer]
- **Resolution**: [16×16 / 32×32 / 64×64 / vector]
- **Style**: [pixel art / vector / hand-drawn]
- **License Requirement**: [CC0 only / CC-BY acceptable / no GPL]

---

### Tier 1: Foundation Packs (Download First)

| Pack | Creator | Platform | License | Direct Link | Verified $0 | Covers |
|------|---------|----------|---------|-------------|-------------|--------|
| [Pack Name] | [Creator] | [itch.io / kenney.nl / etc.] | [CC0 / Free] | [Direct URL] | ✅/❌ | [What entities this pack covers] |

---

### By Category

#### 🏪 Shop / Interior / UI Tilesets
| Asset | Resolution | License | Source | Covers |
|-------|------------|---------|--------|--------|

#### 🧙 Hero Characters (Player Classes)
| Class | Required Spec | Verified Asset Pack | License | Download Link |
|-------|---------------|---------------------|---------|---------------|

#### 👹 Monsters / Enemies
| Monster | Required Spec | Verified Asset Pack | License | Download Link |
|---------|---------------|---------------------|---------|---------------|

#### 🎒 Items / Icons / Crafting Materials
| Category | Verified Asset Pack | License | Download Link |
|----------|---------------------|---------|---------------|

#### 🎨 UI Kits (Panels, Buttons, HUD, Inventory)
| Pack | License | Download Link | Notes |
|------|---------|---------------|-------|

#### 🏰 Dungeon / World Tilesets (by Zone)
| Zone | Verified Asset Pack | License | Download Link |
|------|---------------------|---------|---------------|

#### 💰 Special NPCs / Props / Objects
| Entity | Verified Asset Pack | License | Download Link |
|--------|---------------------|---------|---------------|

#### 🔊 Audio (SFX + Music)
| Type | Verified Asset Pack | License | Download Link |
|------|---------------------|---------|---------------|

---

### ⚠️ Assets Reviewed But NOT Free (Explicitly Excluded)

| Asset | Apparent Price | Why Excluded |
|-------|----------------|--------------|

---

### Download Priority Order

```bash
# 1. [Pack Name] - [Reason]
#    → [Direct Link]

# 2. [Pack Name] - [Reason]
#    → [Direct Link]
```

---

### Phaser 3 Asset Manifest (JSON)

```json
{
  "atlas": [
    { "key": "atlas-key", "textureURL": "path/to/atlas.png", "atlasURL": "path/to/atlas.json" }
  ],
  "spritesheet": [
    { "key": "entity-key", "url": "path/to/spritesheet.png", "frameConfig": { "frameWidth": 16, "frameHeight": 16 } }
  ],
  "audio": [
    { "key": "audio-key", "urls": ["path/to/audio.ogg", "path/to/audio.mp3"] }
  ]
}
```

---

### Verification Checklist

- [ ] Every asset visited on source page
- [ ] $0 download confirmed working
- [ ] Resolution matches game bible
- [ ] Perspective matches game bible
- [ ] Animation frames verified
- [ ] License confirmed CC0/public domain
- [ ] Direct download links provided
- [ ] Non-free assets explicitly excluded