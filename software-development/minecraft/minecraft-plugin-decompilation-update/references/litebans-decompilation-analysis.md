# LiteBans v2.12.0 — Full Decompilation Analysis

Decompiled with CFR 0.152. 734 Java files, heavy obfuscation.

## Identity

- **Author**: Ruan
- **Package**: `litebans` (obfuscated single-letter names)
- **Main classes**: `BukkitPlugin`, `BungeePlugin`, `VelocityPlugin`
- **API package**: `litebans.api` (NOT obfuscated) — `Database`, `Entry`, `Events`, `Events.Listener`, `PlayerProvider`, `RandomID`
- **Price**: ~$15 (premium, closed-source)
- **Platforms**: Spigot/Paper, BungeeCord, Velocity

## Obfuscation Techniques

- **Class names**: a-z, aa-zz (720+ internal classes)
- **String XOR**: all strings encrypted with Unicode codepoint arithmetic, decrypted at runtime via `b5.a()` static method (same as XyrisPlugins)
- **Constant mangling**: integers via XOR-shift expressions, e.g. `(1719249382 << 3 ^ 0x65D3BF4) ^ ...`
- **Reflection dispatch**: `MethodHandles.Lookup` + `ConstantCallSite` pattern
- **Anti-piracy**: prints "Spigotunlocked.com - ElitePusher" when cracked

## API Surface (Clean, Documented)

- `Database` — singleton: `isPlayerBanned(uuid, scope)`, `isPlayerMuted()`, `getUsersByIP()`, `prepareStatement()`
- `Entry` — 17-field data model: id, type, uuid, ip, reason, executor, dates, serverScope, silent, ipban, active
- `Events` + `Events.Listener` — event bus with `entryAdded(Entry)`, `entryRemoved(Entry)`, `broadcastSent()`
- `PlayerProvider` — resolve player data from external sources
- `RandomID` — reversible random ID conversion for punishment IDs

## Key Differentiators (Why LiteBans Is the Market Leader)

1. **Template Ladders**: Progressive discipline — first offense = 7d, second = 30d, final = permanent
2. **Template Groups**: Weighted multi-offense tracking across different rule violations (Spam=0.25, Advertising=0.50, Toxicity=0.20)
3. **Server Scopes**: Per-server punishments on shared DB — ban from Survival not Skyblock
4. **11+ Command Flags**: `-s` silent, `-S` extra silent, `-I` IP, `-m` modify, `-N` no-override, `--sender`, `--skip`, `--hide`
5. **Permission Group Limits**: Per-group duration caps, cooldowns, template enforcement
6. **Import from 10+ plugins**: MaxBans, Ultrabans, BanHammer, BanManager v4/5/7, BungeeAdminTools, AdvancedBan, LibertyBans, Vanilla
7. **Warning Auto-Actions**: 3 warn → auto-kick, 4 warn → auto-tempban
8. **Hierarchical Exemption**: Lower-weight groups cannot punish higher-weight groups
9. **GeoIP Blocking**: MaxMind GeoLite2 country-based blacklist/whitelist
10. **Full Multi-Platform**: Paper + Bungee + Velocity from single JAR

## Feature List (from decompiled config + wiki)

### Punishment Commands (12)
`/ban`, `/tempban`, `/ipban`, `/mute`, `/tempmute`, `/ipmute`, `/warn`, `/kick`, `/unban`, `/unmute`, `/unwarn`

### Investigation Commands (12)
`/history`, `/staffhistory`, `/checkban`, `/checkmute`, `/warnings`, `/banlist`, `/mutelist`, `/dupeip` (`/alts`), `/ipreport`, `/iphistory`, `/namehistory`, `/lastuuid`, `/geoip`

### Admin Commands (14+)
`/lockdown`, `/prunehistory`, `/staffrollback`, `/clearchat`, `/togglechat`, `/mutechat`, `/litebans reload`, `/litebans allow`, `/litebans import`, `/litebans info`, `/litebans servers`, `/litebans reset-database`, `/litebans reset-templates`

## Database

- **Default**: H2 (embedded, zero-setup)
- **Optional**: MySQL 8.0.29, MariaDB 3.1.2, PostgreSQL 42.4.0
- **Pool**: HikariCP (1-10 configurable connections)
- **Import-only**: SQLite

## Permission Structure (70+ nodes)

Per-type: `litebans.ban`, `.mute`, `.warn`, `.kick`, `.tempban`, `.tempmute`
Own removal: `.unban.own`, `.unmute.own`, `.unwarn.own`
Exempt: `.exempt`, `.exempt.ban`, `.exempt.mute`, `.exempt.kick`, `.exempt.bypass`
Notify: `.notify`, `.notify.silent`, `.notify.broadcast`, `.notify.bannedjoin`, `.notify.mutedchat`
Groups: `.group.moderator`, `.group.helper`, `.group.unlimited`

## What LiteBans Does NOT Have

- Built-in GUI menus (pure command-driven)
- Appeals system
- Native Discord bot (uses webhooks.yml)
- VPN/proxy detection (GeoIP only blocks countries)
- Staff notes/notes system
- Chat filter/auto-moderation
- Full Folia support (partial via detection)

## Competitor Comparison

| Plugin | Price | Open Source | Templates | Web UI | GeoIP |
|--------|-------|-------------|-----------|--------|-------|
| **LiteBans** | $15 | ❌ | ✅ Ladders | ✅ PHP | ✅ |
| **LibertyBans** | Free | ✅ AGPLv3 | ❌ | Community | ❌ |
| **AdvancedBan** | Free | ✅ GPL | ❌ | ❌ | ❌ |
| **BanManager** | Free | ✅ GPL | ❌ | ✅ Docker | ❌ |
| **UltraPunishments** | $10 | ❌ | ❌ | ❌ | ❌ |

**Key takeaway**: LiteBans' template ladders + server scopes + GeoIP + import system make it the most complete. LibertyBans is the best free alternative with cleaner architecture but lacks template ladders.
