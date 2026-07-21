# Game Concept Competitor Vetting — Oct 13, 2026

Checked all 8 concepts from ~/.hermes/cache/game_concepts.md. Original research (July 2026) used Steam API with 50+ searches. This delta-check focuses on new releases since July and deeper verification of edge cases.

## FINAL RUN (hearse delivery, cargo physics, dead clients' wishes)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| Hearse Hero | 4159710 | Jul 2026 | Arcade racing (Crazy Taxi clone). No cargo physics, no will delivery, no ghost clients |
| My Funeral Home | 1214870 | Coming soon | Business management sim. Build hearse, transfer remains for income. No physics-based delivery gameplay |
| Death Delivery (horror) | 3515440 | Feb 2025 | Horror game about being stalked while delivering packages. No hearses, no dead wills |
| Death Delivery (FPS) | 3303790 | Nov 2024 | First-person shooter with slow-motion. No relation to funeral/hearse delivery |

Edge searches: "cargo physics game", "ashes delivery", "dead people wishes" — all unrelated.

## REMOTE OPERATOR 911 (remote vehicle piloting with input lag)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| Remote Reaper: FPV Combat Drone Simulator | 3295810 | EA | Realistic milsim drone sim. Serious tone, no input lag mechanic, no passengers, no comedy |
| REMOTE LIFE | 1126420 | Released | 2D space shooter shmup. Unrelated |
| Stormworks: Build and Rescue | 573090 | Released | Vehicle building/rescue sandbox. Not remote operation comedy |
| On Hold - Call Center Simulator | — | — | Dark comedy call center (answering phones). Not vehicle piloting |

Edge searches: "input lag mechanic", "remote driving comedy", "call center driving" — no matches.

## BREACH RESPONSE UNIT (dimensional breach sealing with equipment)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| Dimensional Breach | 4886830 | Q4 2026 | 4-player co-op action. You FIGHT inside rifts. BRU is comedy equipment sealing from outside |
| Breach Signal | 2546650 | Released | 1-6 player co-op cosmic horror investigation. Not comedy equipment management |
| GhostControl Inc. | — | — | Turn-based ghostbusting management. Different genre |

Edge searches: "reality sealing", "paranormal containment comedy" — no direct matches.

## END OF LINE (AI decommissioning, facility navigation)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| AI Confidential | 2982490 | TBA | Repair AI with empathy (narrative adventure). Not decommission them with facility navigation & shutdown mechanics |

## WRECKER (vehicle recovery with chain physics)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| Tow Game | 3690870 | Coming soon | Physics arcade action — swing car on cable for destruction. Not narrative recovery puzzles with clients |
| Auto Tow Truck Simulator | 2715660 | Released | Serious tow truck sim. No comedy, no physics chain chaos |

## LOT 7 (doomsday bunker parking)

**Status: CLEAR**

| Game | App ID | Released | Why not competitor |
|------|--------|----------|-------------------|
| Parking Garage Rally Circuit | 2737300 | Released | Retro arcade racing in parking garages. Not doomsday management |

## RETURN TO ABYSS (multiverse returns, manipulator arms)

**Status: CLEAR** — No matching games found.

## OUTSOURCE (temp worker, unqualified at jobs)

**Status: CLEAR** — No matching games found.

## Methodology note

This round used curl against Steam's REST API directly (web_search credits were exhausted). Both `api/storesearch/?term=...` and `api/appdetails?appids=...` endpoints worked reliably. HTML search page scraping with `grep -oP 'data-ds-appid="[^"]+"'` caught results the storesearch API missed.

Next re-check: ~3 months from this date, or before committing to prototyping any single concept.
