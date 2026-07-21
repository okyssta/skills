# soundimage.org — Fantasy/Game Music Catalog

## Overview
Eric Matyas's soundimage.org provides royalty-free MP3 music. Attribution required: "Music by Eric Matyas, Soundimage.org"

## Direct MP3 Download Pattern
```bash
curl -sL -o "track-name.mp3" "https://soundimage.org/wp-content/uploads/{year}/{month}/{Track-Name}.mp3"
```

## Fantasy Music Pages
| Page | URL | Content |
|------|-----|---------|
| Fantasy 1 | `https://soundimage.org/fantasywonder/` | RPG village, magic, adventure |
| Fantasy 2 | `https://soundimage.org/fantasy-2/` | Mystery, dragon, menu themes |
| Fantasy 3 | `https://soundimage.org/fantasy-3/` | More fantasy styles |
| Fantasy 5 | `https://soundimage.org/fantasy-5/` | Additional tracks |
| Fantasy 10 | `https://soundimage.org/fantasy-10/` | Newer fantasy tracks |

## Verified Tracks (tested download)

### Background/Ambient
| Track | URL | Duration | Use Case |
|-------|-----|----------|----------|
| Our Mountain_v003 | `.../uploads/2014/09/Our-Mountain_v003.mp3` | ~1:19 | Village, opening titles |
| Our Mountain_v003_Looping | `.../uploads/2018/10/Our-Mountain_v003_Looping.mp3` | ~1:19 | Seamless loop |
| Realm of Fantasy | `.../uploads/2014/06/Realm-of-Fantasy.mp3` | ~1:44 | Calm exploration |
| Sky Game Menu | `.../uploads/2014/04/Sky-Game-Menu.mp3` | ~2:07 | Menu/credits |

### Action/Magic
| Track | URL | Duration | Use Case |
|-------|-----|----------|----------|
| Spell's a Brewin' | `.../uploads/2023/12/Spells-a-Brewin.mp3` | ~1:21 | Crafting, magic events |
| Down Draft | `.../uploads/2023/12/Down-Draft.mp3` | ~0:36 | Transition/jingle |
| Updraft | `.../uploads/2023/12/Updraft.mp3` | ~0:36 | Level-up/reward |

## Validation
After downloading, verify:
```bash
# Check file sizes (valid MP3s are 500KB–5MB)
ls -lh *.mp3

# Check file type
file *.mp3  # Should show "MPEG ADTS, layer III"

# Remove suspiciously small files (<1KB = likely error page)
for f in *.mp3; do
  [ $(stat -c%s "$f") -lt 1000 ] && echo "FAIL: $f" && rm "$f"
done
```
