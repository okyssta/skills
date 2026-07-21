# Game Bible Template

Use after concept selection and validation. This turns the chosen concept into a single production-ready document.

---

## GAME_BIBLE.md structure

```
# [GAME NAME] — Game Bible

## One-Sentence Steam Hook
[compelling sentence]

## Core Identity

| Element | Description |
|---------|-------------|
| Genre | [genre tags] |
| Engine | [Unity/Godot + render pipeline] |
| Target Price | $[$9.99/$14.99] Steam |
| Playtime | [4-8h full, ~30min demo] |
| Visual Style | [PS2 retro / low-poly / pixel art] |
| Key Emotion | [what player feels] |
| Player Phrase | [what they say] |

## Setting & Lore
[2-3 paragraphs describing the world, tone, and player's role]

## Core Gameplay Loop
```
1. [Step one]
2. [Step two]
...
N. [Step N → back to 1]
```

## Signature Mechanic
[the one mechanic that defines the game — deep dive]

### How it works
### How it creates comedy
### Edge cases to handle
### Implementation notes

## Progression Systems

### Unlock Tree
| Tier | Unlock | Cost | Effect |
|------|--------|------|--------|
| 1 | [item] | [req] | [effect] |
| ... | | | |

### Upgrade Economy
- [Currency name]: earned from [activity]
- [Second currency]: earned from [activity]
- Conversion rate / caps

## Event / Crisis System
[If procedural: describe how events are generated]

### Event Categories
- [Category 1]: [examples]
- [Category 2]: [examples]

### Difficulty Curve
[How difficulty scales across the game]

## NPC Roster

| Name | Role | Voice | Personality |
|------|------|-------|-------------|
| [Name] | [role] | [on-screen/voice] | [description] |

### Archetypes (procedural)
| Type | Behaviour |
|------|-----------|
| [Archetype] | [reaction pattern] |

## HUD / UI Mockups

### In-Game HUD (ASCII)
```
┌──────────────────────────────────────┐
│ [STATUS]            [INDICATOR]      │
│                                       │
│         [MAIN GAME VIEW]              │
│                                       │
│ [METER]    [METER]    [INDICATOR]    │
└──────────────────────────────────────┘
```

### Menu / Booth Screens
[ASCII or description of each screen]

## Visual Direction

### Colour Palette
| Context | Colours |
|---------|---------|
| [Environment 1] | [colours] |
| [Environment 2] | [colours] |

### Specific Visual Callouts
- [Key visual element]: [description]
- [Key visual element]: [description]

## Audio Direction

### Music
- [Context]: [genre, tempo, instrumentation]
- [Context]: [genre, tempo, instrumentation]

### SFX Table
| Sound | Description |
|-------|-------------|
| [action] | [sound description] |

### Voice Lines
[Character]: [line examples]

## Demo Plan ([30/45] minutes)
1. Tutorial ([X] min): [content]
2. First call ([X] min): [content]
3. Second call ([X] min): [content]
4. [Boss/final call] ([X] min): [content]

## Dev Roadmap
- Phase 1 — Prototype ([X] days): [what works at end]
- Phase 2 — Demo Content ([X] days): [what works at end]
- Phase 3 — Steam Page + Playtest ([X] days)
- Phase 4 — Full Game ([X] days)
- Phase 5 — Beta + Launch ([X] days)
- **Total: ~[N] days**

## Steam Page Materials

### Description
[2-3 paragraph Steam description]

### Trailer Opening (0:00-0:15)
```
[SCENE BY SCENE DESCRIPTION]
```

### Thumbnail Concept
[visual description]

### Name Options
1. [Name 1]
2. [Name 2]
3. [Name 3]

## Risk Assessment
| Risk | Probability | Mitigation |
|------|------------|------------|
| [risk] | [Low/Med/High] | [plan] |
```

---

## Asset Prompts Directory Structure

```
assets/prompts/
├── INDEX.md          # Master index + workflow order + tool recommendations
├── CHARACTERS.md     # Player + NPCs: prompts, polygon budgets, rig specs
├── ENVIRONMENTS.md   # All levels: prompts, prop breakdowns, tech notes
├── VEHICLES.md       # All vehicles: prompts, tier info, handling notes
├── UI_SCREENS.md     # HUD, menus, CRT overlays: prompts, mockups
├── AUDIO.md          # Music, SFX, voice scripts: prompts, placeholder lines
└── TECHNICAL.md      # Shaders, effects, performance targets
```

Each file follows this per-entry format:

```markdown
## [Asset Name]

**Purpose:** What it's used for in-game

**Prompt:**
```
[Full generation prompt — Midjourney/Stable Diffusion/Meshy ready]
```

**Polygon budget:** [N] tris
**Textures:** [resolution, type]
**Animations:** [rig specs if applicable]
**Tech specs:** [shader requirements, special notes]
```
