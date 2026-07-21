# Quick-Start Template: Manim Explainer Video Project

Copy this structure to start a new explainer video project using the `manim-video` skill.

```
project-name/
├── plan.md              # Narrative arc, palette, scene breakdown
├── script.py            # All scene classes (one file)
├── concat.txt           # ffmpeg scene list (auto-generated after render)
└── final.mp4            # Stitched output
```

---

## plan.md Template

```markdown
# [Video Title]

## Overview
- **Topic**: [Core concept]
- **Hook**: [Opening question/statement]
- **Aha moment**: [Key insight]
- **Target audience**: [Prerequisites]
- **Length**: [seconds/minutes]
- **Resolution**: 480p (draft) / 1080p (final)

## Color Palette
- Background: #0D0D0D
- Primary: #00D4AA    # Brand/action
- Secondary: #FF6B9D  # Accent/highlight
- Accent: #FFD700     # Gold/key moments
- Dim: #4A4A4A        # Muted text

## Arc: [Discovery / Problem-Solution / Comparison / Build-Up]

## Scene 1: [Name] (~Ns)
**Purpose**: [One sentence]
**Layout**: [FULL_CENTER / LEFT_RIGHT / GRID / PROGRESSIVE]

### Visual elements
- [Mobject: type, position, color]

### Animation sequence
1. [Animation] — [what it reveals] (~Ns)

### Subtitle
"[text]"
```

---

## script.py Boilerplate

```python
from manim import *

# ─── Shared Constants ───
BG = "#0D0D0D"
PRIMARY = "#00D4AA"
SECONDARY = "#FF6B9D"
ACCENT = "#FFD700"
DIM = "#4A4A4A"
WHITE = "#FFFFFF"

MONO = "Monospace"
TITLE_SIZE = 48
HEADING_SIZE = 36
BODY_SIZE = 28
LABEL_SIZE = 22
CAPTION_SIZE = 20

FAST = 0.6
NORMAL = 1.2
SLOW = 2.0

# ─── Scene Classes ───
class Scene1_Hook(Scene):
    def construct(self):
        self.camera.background_color = BG
        # ... your scene code ...
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

# Repeat for each scene...

# ─── Render Commands ───
# Draft:  manim -ql script.py Scene1_Hook Scene2_Skills ...
# Final:  manim -qh script.py Scene1_Hook Scene2_Skills ...
# Stitch: cat > concat.txt << 'EOF'
# file 'media/videos/script/480p15/Scene1_Hook.mp4'
# file 'media/videos/script/480p15/Scene2_Skills.mp4'
# EOF
# ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

---

## Common Patterns (Copy-Paste)

### Orbiting Particles
```python
particles = VGroup(*[
    Dot(radius=0.06, color=ACCENT, fill_opacity=0.8)
    .move_to(center + 2.5 * np.array([np.cos(i*30*DEGREES), np.sin(i*30*DEGREES), 0]))
    for i in range(12)
])
orbit_anims = [Rotating(p, TAU, about_point=center, run_time=4, rate_func=linear) for p in particles]
self.play(Write(tagline), *orbit_anims, run_time=4)
```

### Staggered Card Reveal
```python
for i, card in enumerate(cards):
    self.play(FadeIn(card, shift=UP * 0.2), run_time=0.3)
    self.wait(0.05)
```

### Typewriter Code Effect
```python
for line in code_lines:
    self.play(Write(line), run_time=0.3)
    if output_lines:
        self.play(Write(output_lines.pop(0)), run_time=0.2)
    self.wait(0.1)
```

### Safe Scene Cleanup
```python
self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
```