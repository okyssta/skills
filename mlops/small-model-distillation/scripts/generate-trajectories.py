#!/usr/bin/env python3
"""Generate teacher trajectories via API, handling subscription caps.

Usage:
  OPENCODE_API_KEY=sk-... python3 generate-trajectories.py --tasks tasks.json
  OPENROUTER_API_KEY=sk-... python3 generate-trajectories.py --tasks tasks.json --provider openrouter

Handles OpenCode Go's $12/5h cap, OpenRouter's 200 req/day, and
any other rate-limited API transparently.
"""

import json
import os
import time
import glob
import argparse
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI

# ── defaults ────────────────────────────────────────────────────────────
DEFAULT_MODEL = "opencode-go/deepseek-v4-flash"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
BACKOFF_MINUTES = 30


def build_client(provider: str, api_key: str) -> OpenAI:
    if provider == "opencode":
        return OpenAI(api_key=api_key, base_url="https://api.opencode.ai/v1")
    elif provider == "openrouter":
        return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    elif provider == "nim":
        return OpenAI(api_key=api_key, base_url="https://api.nvcf.nvidia.com/v1")
    else:
        raise ValueError(f"Unknown provider: {provider}")


def generate_one(
    client: OpenAI, model: str, task: dict
) -> dict | None:
    """Make one API call. Returns parsed response dict or None on 429."""
    try:
        messages = []
        if task.get("system"):
            messages.append({"role": "system", "content": task["system"]})
        messages.extend(task.get("messages", []))

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": task.get("temperature", DEFAULT_TEMPERATURE),
            "max_tokens": task.get("max_tokens", DEFAULT_MAX_TOKENS),
        }
        if task.get("tools"):
            kwargs["tools"] = task["tools"]

        resp = client.chat.completions.create(**kwargs)
        return {
            "request": task,
            "response": resp.model_dump(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        err = str(e)
        if "429" in err or "rate" in err.lower():
            print("  [429] cap hit", flush=True)
            return None
        print(f"  [error] {e}", flush=True)
        return None


def backoff():
    print(f"  sleeping {BACKOFF_MINUTES} min...", flush=True)
    time.sleep(BACKOFF_MINUTES * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, help="JSON file with task array")
    parser.add_argument(
        "--provider", default="opencode", choices=["opencode", "openrouter", "nim"]
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--out", default="trajectories", help="output dir")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    api_key = os.environ.get(f"{args.provider.upper()}_API_KEY")
    if not api_key:
        # also try generic
        api_key = os.environ.get("API_KEY")
    if not api_key:
        print(f"Set {args.provider.upper()}_API_KEY or API_KEY")
        return

    client = build_client(args.provider, api_key)
    tasks = json.loads(Path(args.tasks).read_text())

    # skip already-done
    completed = {Path(f).stem for f in glob.glob(str(out_dir / "*.json"))}

    idx = 0
    for task in tasks:
        task_id = f"task_{idx:06d}"
        idx += 1
        if task_id in completed:
            continue

        print(f"[{task_id}] ", end="", flush=True)
        result = generate_one(client, args.model, task)

        if result is None:
            backoff()
            result = generate_one(client, args.model, task)  # retry once

        if result is None:
            print("skip (cap)", flush=True)
            continue

        (out_dir / f"{task_id}.json").write_text(json.dumps(result, indent=2))
        print("done", flush=True)

    total = len(list(out_dir.glob("*.json")))
    print(f"\nDone. {total} trajectories in {out_dir}")


if __name__ == "__main__":
    main()
