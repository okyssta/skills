# Auto-Fix-Bugs Workflow (hermes-agent)

## Context

This cron job runs against the `NousResearch/hermes-agent` repository. It fetches open bug issues, analyzes candidates, implements fixes, creates PRs, and posts to a Discord webhook.

## Source of truth

The script lives at `/root/.hermes/scripts/auto-fix-bugs.py`. It:
1. Fetches issues labeled "bug" from GitHub sorted by creation date.
2. Deduplicates against open PRs (issues with linked PRs are skipped).
3. Writes the N most recent NEW candidates to `/tmp/bug_candidates.json`.
4. The agent reads that file and does the actual fix/PR/create work.

## Categorization Heuristics

When triaging bug candidates, the following patterns are consistent blockers for a fix on this Linux host:

### Skip — Platform-specific
- **macOS issues** (Desktop app, `.dmg`, Apple Silicon, macOS 27 beta)
- **Windows issues** (console hiding, `.exe`, WSL2, Smart App Control, Windows paths)
- **Desktop/Electron issues** (React renderer, sidebar, drag-drop, Electron freeze) — the desktop is a TypeScript/Electron app that cannot be modified from the Python backend

### Skip — Complex / Unreproducible
- **WhatsApp/Messaging bridge issues** (protocol-level, need account and bridge infra)
- **Model-specific tool behavior** (Qwen losing tool definitions, Ollama not sending tools) — model behavior can't be fixed from the agent side
- **Custom provider tool serialization** — requires running a real custom provider to verify

### Fixable
- **Python backend issues** with clear root cause and minimal code change
- **Config parsing / timeout handling** where the code ignores a documented config key
- **Auth/OIDC integration** where library API supports a simple workaround
- **Session persist/restore bugs** with clear data-flow trace
- **Documentation / broken external URL fixes** — simple text changes, verify the replacement exists

## Fix Pattern: Broken External URL in Skills/Documentation

When a GitHub issue reports a broken external URL in a SKILL.md or website doc:

1. **Find all references**: `search_files` for the URL or the org/repo name across the entire codebase. The URL may live in the source SKILL.md AND in generated website docs AND in translation copies.

2. **Verify the URL is broken**: `curl -sI <URL>` — check for HTTP 200 vs 404/5xx. GitHub returns `HTTP/2 404` for nonexistent repos.

3. **Search for a replacement** using multiple sources:
   - **GitHub API**: Search repos by possible org names (`blackboxaicode`, `blackboxai`, `blackbox-ai`, `llmcod`, `nicepkg`). Check both `users/<name>` and `orgs/<name>` endpoints.
   - **npm registry**: Check the npm package referenced by the skill (`curl -sL "https://registry.npmjs.org/@scope%2Fpackage"`) and read its `repository` and `homepage` fields in the version dict. Some packages have a repo URL that differs from what the skill claims.
   - **The product's website**: Scrape the product page for GitHub links (`grep -oiP 'href="[^"]*github[^"]*"`'). The schema.org `<meta>` tags and `sameAs` arrays often list the official repo.
   - **Google/web search** (when credits available): `web_search("blackbox cli github repository")`.

4. **Decision matrix**:
   - Replacement repo found and accessible → update the URL across all files
   - Replacement repo found but also 404 → include a `git clone` alternative (e.g. from npm or a mirror), or remove
   - **No replacement found** → remove the broken link entirely:
     - Remove the hyperlink and any "open-source" claim tied to the inaccessible repo
     - Remove `git clone` install-from-source instructions (they reference the dead repo)
     - Keep npm/pip install paths as the canonical installation method
     - Rewrite license/attribution text from `"is [open-source](URL) (License)"` to `"is available under the License"`

5. **Apply across all files**: The URL typically lives in 3 places — the source SKILL.md, the English website generated docs, and the Chinese (zh-Hans) translation. Patch all three with the same edit.

6. **Verify**: Re-read the patched files to confirm no stale URL references remain.

### Example: Blackbox CLI Broken Link (#65265, PR #65278)

The skill claimed `https://github.com/blackboxaicode/cli` as the open-source repo. curl confirmed HTTP 404. Searched GitHub (blackboxai, blackbox-ai, llmcod, nicepkg — all 404), npm (`@blackboxai/cli` has no repo URL; `@blackbox_ai/blackbox-cli` links `llmcod/blackbox_cli` — also 404), and the product website (mentions open-source but no working link). Fix: removed the broken link, removed git clone instructions, kept npm install as canonical. Patched SKILL.md + English docs + Chinese docs.

## Fix Pattern: Config Key Ignored

When a documented config key is ignored and a value is hardcoded:
1. Search for all callers of the function with the hardcoded default.
2. Read the config at the caller site using the same pattern the codebase already uses.
3. Pass the config value as a parameter.

## Fix Pattern: Missing Library Parameter

When a third-party API call lacks a parameter that would fix the issue:
1. Check `inspect.signature()` on the installed version to verify the parameter exists.
2. Search all callers of that API for the same omission.
3. The fix is additive — adding the parameter doesn't break existing behavior.

## Fix Pattern: Normalized Data Lost

When a value is normalized (provider name "custom:anthropic" → "custom") and the original is needed for restore:
1. Identify where normalization happens (`resolve_runtime_provider`).
2. Store the pre-normalization value as an underscored attribute on the object.
3. At persist time, prefer `_original_value` over `normalized_value`.
4. The fallback ensures backward compatibility with already-persisted data.

## Fix Pattern: Error Classification With Overlapping Guard Clauses

When an error classifier has multiple guard clauses (parameter mention → output-cap signal → input-override), a single error message can match at different guard levels, causing misclassification. **Always trace all three phases:**

1. **Parameter-mention gate** (`mentions_output_param`): checks for specific keywords like `"max_tokens"`. Some providers (vLLM, llama.cpp, Qwen) phrase this as `"you requested N output tokens"` instead — a keyword that does NOT match. If this gate is too narrow, the error never reaches the signal check.

2. **Signal-phrasing gate** (`output_cap_signal`): looks for descriptive phrasing. The vLLM format (`"requested" + "output tokens"`) is already here.

3. **Input-override gate** (`input_overflow_signal`): broad keyword patterns like `"input token"`, `"prompt contains"`, `"reduce the length"` catch errors that DESCRIPTIVELY mention input but are NOT input-overflows. The vLLM format says `"your prompt contains at least N input tokens"` and `"reduce the length of the input prompt OR the number of requested output tokens"` — both are informational/offering choices, not signaling overflow.

**Fix pattern:** When a well-known error format (vLLM output-cap) is misclassified as input overflow, add a precise exception for the known format before the broad override. Do not broaden the override — that would let genuine input overflows through.

```python
# Exact known format exemption before the broad override:
vllm_style = (
    "maximum context length" in error_lower
    and "requested" in error_lower
    and "output tokens" in error_lower
    and "prompt contains" in error_lower
)
return (not input_overflow_signal) or vllm_style
```

## Fix Pattern: Override Method Diverging From Base Class

When a subclass override does MORE than the base class and the extra work duplicates what the base already provides:

1. Read the base class method carefully — does it already do what the override adds?
2. Search for the stdout/stderr output your override reads — is it already available from the parent's parsing?
3. Remove the redundant work. The override should only add what the parent CANNOT do.
4. **Update tests** — tests that wrote directly to the now-removed intermediary (temp file, cache, etc.) need rewriting to test through the normal data path.

**Example:** `LocalEnvironment._update_cwd` read a temp file for the cwd, then called `_extract_cwd_from_output` (inherited) which already parsed the same value from the stdout marker. The temp-file read was pure overhead once the marker path handled Windows MSYS translation. Fix: delegate entirely to `_extract_cwd_from_output`.

## Fix Pattern: Config Not Bridged to Subprocess Environment

When a config value (terminal backend, Docker volumes) works in CLI mode but is ignored by a different entry point (Desktop `serve`, dashboard PTY):

1. Search for `apply_terminal_config_to_env()` calls in the codebase — they show which processes DO get the bridge.
2. Find the entry point that's missing the call (e.g. `start_server()` in `web_server.py`).
3. Add the same bridge call at startup, using the same try/except pattern the other callers use.
4. The bridge modifies `os.environ` in-place, so all subsequent tool calls in the process inherit the config.

## Investigation Pattern: Subprocess/Docker Environment Differences

When `subprocess.run(docker_exe, "version")` fails inside Hermes but `docker version` works in the user's shell:

1. Check if `stdin=subprocess.DEVNULL` or other subprocess params affect Docker CLI plugin initialization.
2. Check if environment variables (`DOCKER_HOST`, `DOCKER_CONTEXT`) are missing from the subprocess env.
3. Check if `find_docker()` resolves a different binary than the user's `$PATH`.
4. **Note:** On WSL2, Docker Desktop's CLI wrapper may behave differently when stdin is /dev/null — the CLI plugin system may need a live stdin to initialize. This is platform-specific and cannot be verified on plain Linux.
