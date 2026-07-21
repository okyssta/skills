#!/usr/bin/env python3
"""Standalone reproduction script for config-propagation bugs.

Usage: Adjust the imports, field names, and transform function to match
the specific bug you're investigating. This script confirms the bug
WITHOUT running the full test suite.

Pattern:
  1. Create a temp HERMES_HOME
  2. Seed the config with the field that should be preserved
  3. Simulate what the endpoint does (build raw dict, transform, overwrite)
  4. Assert the field survived
"""
import os
import sys
import tempfile

# --- Adjust these to match the bug ---
# from hermes_cli.config import load_config, save_config
# from hermes_cli.some_module import normalize_config
#
# os.environ["HERMES_HOME"] = tempfile.mkdtemp()
#
# # Step 1: Seed the field
# cfg = load_config()
# cfg["moa"]["save_traces"] = True
# cfg["moa"]["trace_dir"] = "/tmp/moa-traces"
# save_config(cfg)
# print(f"BEFORE: save_traces={cfg['moa']['save_traces']}, trace_dir={cfg['moa']['trace_dir']}")
#
# # Step 2: Simulate the endpoint's transform
# raw = {
#     "reference_models": [...],
#     "aggregator": {...},
#     "max_tokens": 4096,
#     "enabled": True,
# }
# normalized = normalize_config(raw)
# print(f"normalized keys: {sorted(normalized.keys())}")
# print(f"save_traces in normalized? {'save_traces' in normalized}")
#
# # Step 3: Wholesale overwrite (the bug)
# cfg["moa"] = normalized
# save_config(cfg)
#
# # Step 4: Verify
# cfg2 = load_config()
# result = cfg2["moa"].get("save_traces", "<MISSING>")
# print(f"AFTER: save_traces={result}")
# assert result is True, f"BUG CONFIRMED: save_traces dropped (got {result})"
# print("OK: field survived the overwrite")
