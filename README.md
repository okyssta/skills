# Hermes Skills Vault

**886 skills** for [Hermes Agent](https://hermes-agent.nousresearch.com/) — the largest public collection of custom Hermes skills.

Built from three sources:
- **55 original skills** — built through real-world use, not tutorials
- **14 Superpowers skills** — adapted from [obra/superpowers](https://github.com/obra/superpowers), converted to Hermes subagent/delegate_task patterns
- **817 cybersecurity skills** — adapted from [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills), comprehensive pentesting/forensics/detection/compliance coverage

---

## What's inside

| Category | Skills | Highlights |
|----------|--------|------------|
| **Creative** | 5 | Urdu poetry prosody (full Ilm-e-Arooz), indie game concept validation, Phaser 3 browser games, free CC0 game asset curation, Manim CE troubleshooting |
| **Cybersecurity** | 817 | Full-spectrum: packet analysis with Scapy, memory forensics with Volatility, malware RE with Ghidra, Active Directory attacks, cloud security (AWS/Azure/GCP), OT/ICS, purple teaming, threat hunting, compliance (NIST/PCI/SOC2), and more |
| **Data Science** | 1 | Fuzzy/partial CSV filtering with prefix matching |
| **DevOps** | 7 | Free-tier LLM setup, Docker auto-deploy pipelines, eBay Trading API integration, Pterodactyl panel deployment, Hermes gateway adapter dev, cron job management, dashboard deployment |
| **GitHub** | 2 | Fork-based PR workflows, GitHub automation beyond basic PR lifecycle |
| **Go** | 1 | Production API gateway patterns (routing, middleware, LLM proxies) |
| **Hermes** | 2 | JSON-RPC gateway protocol spec, ModelHub dashboard operations |
| **Infrastructure** | 1 | Hermes environment passthrough for terminal backends |
| **MLOps** | 3 | LLM API provider business blueprint, frontier model distillation, web-only AI → API proxy |
| **Productivity** | 2 | Project delivery playbook, docsify documentation site setup |
| **Research** | 4 | Multi-registry competitive landscape, systematic product ideation, Steam API indie game validation, Pakistani university admissions |
| **Software Development** | 33 | Original: debugging patterns, monorepo extraction, reference architecture research. **Superpowers-adapted**: subagent-driven development, writing plans, TDD, systematic debugging, parallel agent dispatch, code review workflows, git worktrees, verification |
| **Testing** | 1 | Service/daemon integration testing patterns |
| **Web** | 6 | Stealth web scraping, web content reconnaissance, competitive SEO audit, web app SEO, WordPress SEO, ModelBench dashboard |
| **Font Config** | 1 | Hermes Web UI font configuration |

## Highlights

### Original skills

- **urdu-poetry** — The most comprehensive Urdu poetry reference in any AI skill library. 14 common poetic meters with full scansion, 21 types of metrical variation, complete qafiya/radeef system.
- **stealth-web-scraping** — Battle-tested bot detection bypass: CloakBrowser, undetected-chromedriver, Firecrawl self-hosted.
- **llm-api-provider** — Full blueprint for running an LLM API business: cost modeling, routing, subscription billing.
- **open-source-extraction** — Extract packages from monorepos for standalone use. Dependency mapping, cloud dep stripping.
- **competitor-driven-development** — Systematic methodology: clone → audit → feature parity → ADRs → clean-room rebuild.

### Superpowers-adapted (software-development/)

All 14 Superpowers skills adapted for Hermes Agent:
- **subagent-driven-development** — Core autonomous workflow: delegate_task per task with review checkpoints
- **writing-plans** — Bite-sized implementation plans with spec verification
- **test-driven-development** — Classic red/green/refactor for Hermes
- **dispatching-parallel-agents** — Parallel subagent execution for independent tasks
- **systematic-debugging** — Root cause before fix, no random patches
- **requesting-code-review / receiving-code-review** — PR quality gates
- **using-git-worktrees** — Isolated workspaces for parallel feature work
- **brainstorming, executing-plans, verification, finishing-branch, writing-skills** — Full development lifecycle

### Cybersecurity (cybersecurity/)

817 skills organized by domain. Each has:
- MITRE ATT&CK technique mappings
- Tool-specific procedures (Volatility, Ghidra, Wireshark, BloodHound, etc.)
- Step-by-step methodology with verification steps

Major areas:
- **Network security**: packet analysis, traffic monitoring, firewall config, IDS/IPS
- **Endpoint forensics**: memory analysis, disk forensics, registry artifacts, timeline reconstruction
- **Cloud security**: AWS/Azure/GCP auditing, IAM hardening, container security, Kubernetes
- **Active Directory**: attack paths, privilege escalation, Kerberos abuse, ACL exploitation
- **Malware analysis**: static/dynamic RE, sandboxing, YARA rules, ransomware analysis
- **Web security**: pentesting, API testing, SSRF/XSS/SQLi, WAF bypass
- **OT/ICS**: SCADA security, PLC analysis, Purdue model, industrial protocols
- **Compliance**: NIST CSF, PCI DSS, SOC 2, ISO 27001, CMMC, GDPR
- **Threat intelligence**: MISP, STIX/TAXII, threat hunting, OSINT
- **Red teaming**: C2 infrastructure, phishing, adversary emulation, purple teaming

---

## Why this vault is different

1. **Scale** — 886 skills is the largest public Hermes skills collection. No other vault comes close.
2. **Real provenance** — Every skill was either built from real projects or adapted from proven open-source methodology collections. No filler.
3. **Cybersecurity depth** — 817 skills covering everything from packet-level forensics to C-suite compliance. If you work in security and use Hermes, this is your library.
4. **Superpowers methodology** — The complete Superpowers development workflow, retargeted for Hermes's `delegate_task` subagent system.
5. **Custom originals** — 55 skills built through actual debugging sessions and production deployments, not hypotheticals.

---

## Structure

```
skills/
├── creative/urdu-poetry/
│   └── SKILL.md
├── cybersecurity/analyzing-network-packets-with-scapy/
│   ├── SKILL.md
│   ├── references/           # Deep dives, research notes
│   └── scripts/              # Tools and helpers
├── software-development/superpowers-writing-plans/
│   ├── SKILL.md
│   └── references/
└── ...
```

Each skill directory has:
- `SKILL.md` — the reusable workflow: trigger conditions, step-by-step procedure, pitfalls, verification
- `references/` — research notes, architecture deep-dives (where applicable)
- `scripts/` — automation scripts, templates (where applicable)

---

## Usage

1. Install [Hermes Agent](https://hermes-agent.nousresearch.com/)
2. Copy a skill to `~/.hermes/skills/<category>/<name>/`:
   ```bash
   git clone https://github.com/kyssta-exe/skills.git
   cp -r skills/cybersecurity/analyzing-memory-dumps-with-volatility ~/.hermes/skills/cybersecurity/
   ```
3. Hermes automatically picks up skills placed in the skills directory

Or load on demand: `skill_view(name='superpowers-subagent-driven-development')`

---

## Credits

- **obra/superpowers** — Original Superpowers methodology for coding agents ([MIT](https://github.com/obra/superpowers/blob/main/LICENSE))
- **mukul975/Anthropic-Cybersecurity-Skills** — Original cybersecurity skills collection ([Apache-2.0](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/LICENSE))

---

## License

MIT — use freely, adapt, share back.
