# CLI Tool Saturation Map

Comprehensive landscape of 18 categories (as of Jul 2026). Based on GitHub API, npm, PyPI, and web search.

## 🔴 Saturated (Avoid building)

| Category | Dominant Tool(s) | Stars | Notes |
|----------|-----------------|-------|-------|
| Terminal Recording | asciinema, VHS (charmbracelet) | 17.6K, 20.4K | Multiple strong players |
| AI Commit Tools | aicommits, opencommit, commitlint, cz-cli | 9K, 7.5K, 18.6K, 17.5K | Endless tiny competitors too |
| Git Tools (general) | lazygit, gh (cli/cli), gitui, tig | 80K, 45K, 30K, 13K | Hyper-saturated |
| Code Review (CI/auto) | reviewdog, pre-commit | 9.4K, 15.4K | For automated review |
| Diff Rendering | delta, difftastic, diff-so-fancy | 31K, 23K, 18K | Multiple winners |
| Env Version Managers | nvm, pyenv, direnv | 94K, 45K, 15K | Established standard tools |
| Productivity Trackers | ActivityWatch, Timewarrior, WakaTime | 18K, 2.2K, 448 | ActivityWatch dominates automated tracking |

## 🟡 Moderate Opportunity (Can compete with fresh angle)

| Category | Weakness / Gap | Max Stars |
|----------|---------------|-----------|
| Standup Generators | No AI-native standup CLI with >100 stars | ~7K (git-quick-stats, not standup-specific) |
| Dangerous Command Protection | thefuck (97K) is post-hoc correction, not proactive guard | 97K (thefuck) but different category |
| Project Health Dashboards | onefetch is static, no actionable health metrics | 12K (onefetch) |
| Context Resume | tmux/zellij are terminal-level, not AI-session-level | 48K (tmux) but different focus |
| Diff Annotation | delta/difftastic render diffs but don't let you comment | 31K (delta) but no comment/annotation feature |
| Code Review (human TUI) | No good CLI for walking through & commenting on diffs | — |
| Env Secret/Dotenv Mgmt | direnv loads .env but doesn't manage/encrypt/rotate | 15K (direnv) but no vault/rotate features |

## 🟢 High Opportunity (Nearly Empty)

| Category | Max Stars | Why Gap Exists |
|----------|-----------|---------------|
| **AI Session Tracking** | 176 (toktrack) | Brand new category (2025-26). No standard. No winner. |
| **AI Cost Trackers** | 176 (toktrack/codeburn) | Same — fragmented, tiny entries, no winner. #1 pain point of 2026. |
| **Decision Tools CLI** | 0 | Completely empty. ADR creation, decision matrices, weighted comparison — no CLI does this well. |
| **Interview Coach CLI** | 29 (ds-trainer) | Biggest entry has 29 stars. AI makes this feasible and high-demand. |
| **Dev Affirmations** | — | No CLI dedicated to this. fortune-mod is generic. |
| **Relationship Trackers** | — | Empty. Personal CRM in CLI doesn't exist. |

## Top Gaps Ranked (Opportunity + Novelty)

1. **Decision Tools CLI** — 0 stars, completely empty, universal audience
2. **Interview Coach CLI** — 29 stars max, AI makes it feasible now
3. **AI Session Tracker** — 176 stars max, exploding category, no winner
4. **AI Cost Tracker** — 176 stars max, #1 pain point of 2026
5. **Relationship Tracker CLI** — Empty, novel concept in CLI space
6. **Dev Affirmations** — Simple, fun, viral potential
7. **Standup Generator (AI-native)** — Several attempts but none broke out
8. **Dangerous Command Guard (proactive)** — thefuck is post-hoc; proactive with context awareness
9. **Diff Annotation CLI** — Comment on diffs from terminal
10. **Project Health CLI** — onefetch but with trends, alerts, CI data

## Trap Categories (seem open but are deceptively hard)

- **"Better git" tools** — lazygit (80K), gh (45K), gitui (30K), tig (13K). To win, need 10x improvement. Not worth it.
- **"Better diff" tools** — delta (31K), difftastic (23K), diff-so-fancy (18K). Saturated.
- **"AI wrapper for X"** — Every major API call has 10+ wrappers. Need distribution, not code quality.
- **"Note-taking CLI"** — jrnl is the standard. Too many entrants.
