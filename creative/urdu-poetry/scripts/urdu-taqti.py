#!/usr/bin/env python3
"""
Urdu Taqti (Scansion) Helper — for verifying Bahr (meter) in poetry.

Usage:
    python3 urdu-taqti.py '<romanized misra>'
    python3 urdu-taqti.py --bahr <bahr_name> '<misra1>' '<misra2>'

Example:
    python3 urdu-taqti.py 'hai ye hasrat aur koi raat ho jaye'
    python3 urdu-taqti.py --bahr ramal_musaddas_mahzuuf \\
        'hai ye hasrat aur koi raat ho jaye' \\
        'tum ko aao to koi baat ho jaye'

Accepts waqf: final syllable can be 1 or 2 in comparison.
"""

import sys
import re

# Standard Bahrs for matching
BAHRS = {
    "hazaj_musamman_saalim": {
        "name": "Bahr-e-Hazaj Musamman Saalim",
        "feet": "ma-faa-ii-lun × 4",
        "pattern": [1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2],
        "feel": "Epic, majestic — Iqbal"
    },
    "hazaj_musaddas_mahzuuf": {
        "name": "Bahr-e-Hazaj Musaddas Mahzuuf",
        "feet": "ma-faa-ii-lun / ma-faa-ii-lun / fa-uu-lun",
        "pattern": [1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2],
        "feel": "Lyrical, romantic — Firaq"
    },
    "ramal_musamman_mahzuuf": {
        "name": "Bahr-e-Ramal Musamman Mahzuuf",
        "feet": "faa-i-laa-tun ×3 + faa-i-lun",
        "pattern": [2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2],
        "feel": "Default ghazal meter — 40-50% of all ghazals"
    },
    "ramal_musaddas_mahzuuf": {
        "name": "Bahr-e-Ramal Musaddas Mahzuuf",
        "feet": "faa-i-laa-tun / faa-i-laa-tun / faa-i-lun",
        "pattern": [2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2],
        "feel": "Simple, profound — Meer"
    },
    "hazaj_musamman_akhrab": {
        "name": "Bahr-e-Hazaj Musamman Akhrab",
        "feet": "maf-uu-lu / ma-faa-ii-lun (×2)",
        "pattern": [2, 2, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2],
        "feel": "Driving, passionate — Jigar"
    },
    "mutaqarib_musamman_saalim": {
        "name": "Bahr-e-Mutaqarib Saalim",
        "feet": "fa-uu-lun × 4",
        "pattern": [1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2],
        "feel": "Narrative, epic — Bekhud"
    },
    "mutadaarik_musamman_saalim": {
        "name": "Bahr-e-Mutadaarik Saalim",
        "feet": "faa-i-lun × 4",
        "pattern": [2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2],
        "feel": "Strong, declarative — Nida Fazli"
    },
    "khafiif_musaddas_makhbuun_mahzuuf_maqtu": {
        "name": "Bahr-e-Khafiif Musaddas Makhbuun Mahzuuf Maqtu",
        "feet": "faa-i-laa-tun / fa-i-laa-tun / fa-i-lun",
        "pattern": [2, 1, 2, 2, 1, 2, 2, 1, 2],
        "feel": "Short, poignant — Ghalib's 'koii ummiid bar nahiiN aatii'"
    }
}


# Transliteration table for standardized syllable splitting
VOWELS = set('aeiouāīū')
LONG_VOWELS = set('āīū')
DIPHTHONGS = {'ai', 'au', 'ei', 'oi'}


def syllabify(word):
    """Split a Romanized Urdu word into syllables using CV pattern."""
    word = word.lower().strip().rstrip('.,;:!?،؛')
    if not word:
        return []

    syllables = []
    current = ''
    i = 0

    while i < len(word):
        c = word[i]

        # Handle diphthongs
        if i + 1 < len(word) and word[i:i+2] in DIPHTHONGS:
            # Check if current has a vowel already
            if any(v in current for v in VOWELS):
                if current:
                    syllables.append(current)
                current = ''
            current += word[i:i+2]
            i += 2
            continue

        # Handle long vowels
        if c in 'āīū' or (c in 'aeo' and c not in 'āīū'):
            # Vowel found — end previous syllable if it had a vowel already
            if any(v in current for v in VOWELS):
                if current:
                    syllables.append(current)
                current = ''
            # Check if next char is also part of this vowel
            if i + 1 < len(word) and word[i+1] == 'h' and c == 'e':
                # 'eh' or 'ah' — treat together
                pass

            current += c
            i += 1

            # Check for consonant cluster after vowel
            while i < len(word) and word[i] not in VOWELS | set('āīū'):
                if word[i] == 'n' and i+1 < len(word) and word[i+1] in VOWELS:
                    # 'n' might be nasalization — keep with vowel
                    break
                current += word[i]
                i += 1

            if current:
                # Check if current has vowel
                if any(v in current for v in VOWELS | set('āīū')):
                    syllables.append(current)
                    current = ''
                else:
                    # No vowel yet — keep collecting
                    pass
        else:
            current += c
            i += 1

    if current:
        # Check if it has a vowel
        if any(v in current for v in VOWELS | set('āīū')):
            syllables.append(current)

    return syllables


def weight(syl):
    """Compute metrical weight for a syllable."""
    s = syl.lower()

    has_long_vowel = any(v in s for v in 'āīū')
    has_short_vowel = any(v in s for v in 'aeiou')
    has_diphthong = any(d in s for d in ['ai', 'au', 'ei', 'oi'])
    ends_consonant = s[-1] not in 'aioueāīū' if s else False
    has_nasal = 'n' in s and s[-1] == 'n'

    # Overlong: long vowel + consonant (yaad, baat, kaam)
    if has_long_vowel and ends_consonant:
        return 3  # treated as 2+1 in taqti

    # Long vowel alone (aa, ii, ho, jaa)
    if has_long_vowel:
        return 2

    # Diphthong
    if has_diphthong:
        return 2

    # Closed syllable (consonant ending) with short vowel
    if ends_consonant and has_short_vowel:
        return 2

    # Open short vowel (ka, tu, se)
    if has_short_vowel and not ends_consonant:
        return 1

    # Single consonant (rare — usually part of overlong)
    return 2  # default


def scan(misra):
    """Scan a Romanized Urdu line. Returns (syllables, weights) tuple."""
    words = misra.strip().split()
    all_syllables = []
    all_weights = []

    for word in words:
        syls = syllabify(word)
        for s in syls:
            w = weight(s)
            all_syllables.append(s)
            all_weights.append(w)

    return all_syllables, all_weights


def match_bahr(weights, bahr_pat, use_waqf=True):
    """Check if weights match a bahr pattern (with optional waqf)."""
    w = list(weights)
    p = list(bahr_pat)

    if len(w) != len(p):
        return False, f"Length mismatch: {len(w)} != {len(p)}"

    for i in range(len(w)):
        if w[i] == p[i]:
            continue
        # Waqf: final syllable can be 1 or 2 interchangeably
        if use_waqf and i == len(w) - 1:
            continue  # waqf accepts both
        # 2+1 vs 2 or 1 — split overlong
        if w[i] == 3 and p[i] == 2:
            continue
        if w[i] == 3 and i + 1 < len(w) and p[i] == 2 and p[i+1] == 1:
            continue  # overlong (2+1) matches 2 + 1 across boundary
        return False, f"Position {i+1}: got {w[i]}, expected {p[i]}"

    return True, "Match"


def format_arkaan(weights, bahr_name):
    """Group weights into feet for display."""
    bahr = BAHRS.get(bahr_name)
    if not bahr:
        return str(weights)

    pat = bahr['pattern']
    w = list(weights)
    result = []
    idx = 0
    for foot_idx in range(len(pat)):
        pass

    # Simple: just return hyphen-separated
    return '-'.join(str(w) for w in weights)


def list_bahrs():
    """Display all known bahrs."""
    print("AVAILABLE BAHRS (Meters) for Urdu Poetry:\n")
    for key, b in sorted(BAHRS.items()):
        pat_str = '-'.join(str(p) for p in b['pattern'])
        print(f"  {b['name']}")
        print(f"    Arkan: {b['feet']}")
        print(f"    Pattern: {pat_str}")
        print(f"    Length: {len(b['pattern'])} positions")
        print(f"    Feel: {b['feel']}")
        print()

def main():
    if len(sys.argv) < 2:
        print("Urdu Taqti (Scansion) Helper\n")
        print("Usage:")
        print("  python3 urdu-taqti.py <romanized_misra>")
        print("  python3 urdu-taqti.py --list")
        print("  python3 urdu-taqti.py --bahr <name> <line1> <line2>")
        print("\nExamples:")
        print("  python3 urdu-taqti.py 'hai ye hasrat aur koi raat ho jaye'")
        print("  python3 urdu-taqti.py --bahr ramal_musaddas_mahzuuf \\")
        print("      'hai ye hasrat aur koi raat ho jaye' \\")
        print("      'tum ko aao to koi baat ho jaye'")
        return

    if sys.argv[1] == '--list':
        list_bahrs()
        return

    if sys.argv[1] == '--bahr':
        if len(sys.argv) < 5:
            print("Usage: --bahr <bahr_name> <misra1> <misra2>")
            print("Known bahrs:", ', '.join(BAHRS.keys()))
            return

        bahr_name = sys.argv[2]
        if bahr_name not in BAHRS:
            print(f"Unknown bahr: {bahr_name}")
            print(f"Known: {', '.join(BAHRS.keys())}")
            return

        bahr = BAHRS[bahr_name]
        print(f"{'='*60}")
        print(f"BAHR: {bahr['name']}")
        print(f"Pattern: {'-'.join(str(p) for p in bahr['pattern'])}")
        print(f"Length: {len(bahr['pattern'])} positions")
        print(f"{'='*60}")

        all_ok = True
        for i in range(2):
            misra = sys.argv[3 + i]
            syls, weights = scan(misra)
            ok, msg = match_bahr(weights, bahr['pattern'])

            print(f"\n--- Misra {i+1}: {misra} ---")
            print("Syllables:", ' / '.join(f"{s}({w})" for s, w in zip(syls, weights)))
            print(f"Pattern: {'-'.join(str(w) for w in weights)}")

            if ok:
                print("✓ ✅ BAHR MATCH!")
            else:
                print(f"✗ ❌ Bahr mismatch: {msg}")
                all_ok = False

            # Show foot grouping
            print(f"Grouped: ", end='')
            p = bahr['pattern']
            start = 0
            for fi in range(4):
                if start >= len(p):
                    break
                # find end of this foot
                end = start
                running = 0
                for j in range(start, len(p)):
                    end = j
                    running += 1
                    if running == 4 or (running == 3 and j == len(p) - 1 and len(bahr['pattern']) - j == 3):
                        if j + 1 >= len(p) or j == len(p) - 1:
                            break
                        if start + 4 <= len(p) and running == 4:
                            break

                # Simpler: just show in groups of 4 except last
                pass

            # Simple grouping
            remaining = list(weights)
            groups = []
            while remaining:
                if len(remaining) <= 3:
                    groups.append(remaining)
                    break
                if len(remaining) == 7:
                    groups.append(remaining[:4])
                    remaining = remaining[4:]
                else:
                    groups.append(remaining[:4])
                    remaining = remaining[4:]

            print(' / '.join('-'.join(str(w) for w in g) for g in groups))

        if all_ok:
            print(f"\n{'✅'} Both misras match {bahr['name']}")
        else:
            print(f"\n{'⚠️'} Meter issues found — see above")

        return

    # Single line mode
    misra = ' '.join(sys.argv[1:])
    syls, weights = scan(misra)
    pat_str = '-'.join(str(w) for w in weights)

    print(f"Misra: {misra}")
    print(f"Taqti: {' / '.join(f'{s}({str(w)})' for s, w in zip(syls, weights))}")
    print(f"Pattern: {pat_str}")
    print(f"Positions: {len(weights)}")
    print()

    # Try matching against all bahrs
    print("Matching Bahrs:")
    matched = False
    for key, b in sorted(BAHRS.items()):
        ok, msg = match_bahr(weights, b['pattern'])
        if ok:
            print(f"  ✅ {b['name']}")
            print(f"     Arkan: {b['feet']}")
            print(f"     Feel: {b['feel']}")
            matched = True
        else:
            if len(weights) == len(b['pattern']):
                print(f"  ❌ {b['name']}: {msg}")
            else:
                print(f"  ❌ {b['name']}: len diff ({len(weights)} vs {len(b['pattern'])})")

    if not matched:
        print("\n⚠️ No bahr match found. Check syllable weights or consider:")
        print("  - Did you use correct Romanization? (aa not a, ii not i)")
        print("  - Is waqf (pause) needed for the final syllable?")
        print("  - Is this free verse (nazm) rather than a metered ghazal?")


if __name__ == '__main__':
    main()
