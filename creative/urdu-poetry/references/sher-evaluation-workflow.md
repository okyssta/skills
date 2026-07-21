# Sher Evaluation & Correction Workflow

A structured method for auditing an Urdu sher (couplet) — derived from real evaluation work.

## 🚨 CRITICAL RULE — GRAMMAR FIRST, METER SECOND

**Never sacrifice natural Urdu wording to fix scansion.** If a word doesn't fit the meter naturally, change the bahr or restructure the line — do NOT force unnatural phrasing.

**Bad pattern (DO NOT DO):**
- User's sher has "mulaqat" as qafiya → agent changes to "raat" because it scans easier → user objects
- Agent suggests "tum ko aao" (ungrammatical Urdu) to fit meter → user rejects as nonsense

**Good pattern (DO THIS):**
- Honor the user's chosen qafiya word even when it's metrically challenging
- If no standard bahr fits, accept waqf convention or use a modified bahr
- Always verify: "Would a native Urdu speaker actually say this?" before presenting any correction

**Triple-check order:**
1. ✅ Grammar & naturalness — does this sound like real Urdu?
2. ✅ Qafiya/Radeef — do the rhyme and refrain work?
3. ✅ Meter — does it scan? (Accept waqf for final position when needed)

---

## The 6-Point Audit Checklist

### 1. Grammar & Naturalness (CHECK FIRST — most critical)
- Does every word make sense in context?
- Would a native speaker actually say this?
- Are postpositions correct (ka/ki/ke agreement, ne for ergative past)?
- If it sounds forced when read aloud, it's wrong — fix the wording before checking anything else.

### 2. Bahr (Meter) — Do both misras scan to a known bahr?
- Break each misra into syllables and assign weights (1=short, 2=long)
- Count total positions per misra — they MUST be equal
- Check if the weight pattern matches a known bahr
- Check the **same bahr appears in both misras**

**Signs of bahr problems:**
- Different syllable counts between misras
- Consecutive 1s in positions where a standard foot expects alternating 2-1-2-2
- Clusters of consecutive 2s that don't divide into standard arkan

### 3. Qafiya (Rhyme) — Do the rhyming words match?
- The qafiya word sits immediately before the radeef
- All qafiyas in a ghazal must share the same ending sound
- The qafiya must have the same metrical weight (wazn) in every sher

### 4. Radeef (Refrain) — Is the refrain identical each time?
- Appears at end of every second misra
- Appears at end of BOTH misras in the Matla
- Must be word-for-word identical — no variations

### 5. Matla — Does the opening work?
- Both misras have radeef + qafiya
- The first line establishes the musical/emotional tone

### 6. Self-Sufficiency — Does the sher stand alone?
- Must express a complete thought without needing preceding/following shers
- Should not use words that refer to other shers

## Worked Example: Session Sher

### Original (user's own composition):
```
Hai ye hasrat k mulaqat ho jaye
Tum ao ham bethe Kuch pal baat ho jaye
```

### Problems Found:
| Issue | Detail |
|-------|--------|
| **Bahr mismatch** | Line 1: 11 positions, Line 2: 12 — different meters. This is the #1 fatal flaw. |
| **Grammar** | `k` should be `ki` (کی). `bethe` ambiguous spelling. `Kuch` wrong capitalization. |
| **Radeef challenge** | `ho jaye` naturally scans 2-1-1 or 2-2-1 — hard to fit standard bahrs' final 2 |
| **Qafiya** | `mulaqat` ~ `baat` — WORKS (both -aat) |
| **Self-sufficiency** | WORKS — one clear thought |

### Taqti Comparison:
```
ORIGINAL:
Line 1: hai ye has-rat ki mu-la-qat ho ja-ye
         2  1   2-2   1  1-1-2   2  2-1  ← 11 positions
Line 2: tum aa-o ham bai-the kuchh pal baat ho ja-ye
         2  2-1  2   2-2   2    2   2    2  2-1  ← 12 positions
         ^^^ DIFFERENT lengths — can't share a bahr
```

### Version A: Corrected with "raat" (easier scansion, used when user has no qafiya preference)
Bahr-e-Ramal Musaddas Mahzuuf (2-1-2-2 / 2-1-2-2 / 2-1-2):
```
Line 1: hai ye has-rat aur ko-ī raat ho ja-ye
         2  1   2-2   2   1-2  2    2  1-2  ← 11 ✓
Line 2: tum ko ā-o   to  ko-ī baat ho ja-ye
         2   1  2-1  2   1-2  2    2  1-2  ← 11 ✓
```

### Version B: Corrected preserving "mulaqat" (when user insists on the original qafiya)
Same bahr, different wording for positions 1-4:
```
Line 1: hai ye has-rat ik mu-laa-qat ho ja-ye
         2  1   2-2   2  1-2-2   2  1-2  ← 11 ✓
         ^^ ik gives the 2 needed at position 5 instead of relying on "aur ko-ī"
Line 2: aa-o  tum to   bas ko-ī baat ho ja-ye
         2-1  2  2    2   1-2  2   2  1-2  ← 11 ✓
```

**⚠️ IMPORTANT:** If the user chose a specific qafiya word (like "mulaqat"), always preserve it. Version B uses "ik mulaqat" instead of rewriting to "koi raat". The grammar stays natural — never suggest "tum ko aao" or other forced constructions just to fit meter. If the meter truly can't accommodate the user's qafiya, use waqf or a different bahr, but NEVER sacrifice grammatical Urdu.

### The "ho jaye" Radeef Challenge

**Why it's hard:**
- `ho` = weight 2 (long vowel)
- `jaa` = weight 2 (long vowel)  
- `ye` = weight 1 (short vowel)
- Pattern = 2-2-1 or 2-1-1

Most standard Urdu bahrs require the **final position (last syllable)** to be **weight 2**:
- faa-i-lun (2-1-2) ← ends in 2
- fa-uu-lun (1-2-2) ← ends in 2
- fa-uu-l (1-2-1) ← ends in 1 (rare — used in some modified bahrs)

**Solution: Waqf (وقف) Convention**
In Urdu prosody, the final syllable of a misra can be treated as long (2) because the natural pause at the end of recitation neutralizes quantity. This is called `waqf`.

So `ho ja-ye` = 2-1-1 → `ho ja-ye(waqf)` = 2-1-2 — fits faa-i-lun ✓

**When to use waqf:**
- Only for the absolute final syllable of a misra
- Not for internal positions
- Standard poetic license in ALL schools of Urdu poetry

**Alternative: Change the radeef**  
If poetic license is undesirable, choose a radeef that naturally ends with weight 2:
- `nahiiN hai` (nahiiN=2+1, hai=2) → ends in 2
- `karo` (2-2) → ends in 2
- `huaa` (2-2) → ends in 2
- `aaegi` (2-1-2) → ends in 2

---

## 📋 Triple-Check Protocol (use this ORDER every time)

Before presenting any sher correction, run through these three checks IN THIS ORDER:

### ✅ Check 1: GRAMMAR & NATURALNESS
- Read the Urdu line aloud. Does it sound like something a native speaker would say?
- Check postpositions: ka/ki/ke agreement with the POSSESSED noun, not the possessor
- Check verb agreement: gender+number with subject (or object if ergative past)
- Check word order: SOV
- If ANY part sounds forced or unnatural, fix the wording FIRST
- **NEVER suggest "tum ko aao" or similar ungrammatical constructions to fit a meter**

### ✅ Check 2: QAFIYA & RADEEF
- Radeef is EXACTLY the same every time (word for word)
- Qafiya rhyme: same ending consonant + vowel sound across all shers
- Qafiya weight: each qafiya must have the same metrical weight (wazn)
- Matla: both misras have radeef+qafiya
- Every subsequent sher: second misra has qafiya+radeef; first misra is free

### ✅ Check 3: METER (TAQTI)
- Count syllables per misra — both misras MUST have the same count
- Assign weights: 1=short vowel, 2=long vowel or closed syllable, 2+1=overlong
- Group into 4+4+3 positions (for Ramal) or match any standard bahr
- Accept waqf for the FINAL syllable only (treat as 2 when line-end calls for 2)
- If the user's chosen qafiya doesn't fit: restructure the line, change the bahr, or use waqf — NEVER change the user's qafiya without asking

**If all three checks pass, the sher is correct.**
