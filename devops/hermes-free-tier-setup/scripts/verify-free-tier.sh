#!/usr/bin/env bash
# verify-free-tier.sh — Quick verification of free-tier Hermes setup
# Usage: ./verify-free-tier.sh

set -euo pipefail

echo "🔍 Verifying Hermes Free-Tier Setup"
echo "===================================="

# 1. Check config exists and is migrated
echo ""
echo "1️⃣  Config version:"
hermes config check 2>&1 | grep -E "(version|migrated|OK)" || hermes doctor 2>&1 | grep "Config version"

# 2. Check custom providers registered
echo ""
echo "2️⃣  Custom providers registered:"
hermes doctor 2>&1 | grep -A 10 "Migrated.*custom provider" || echo "   Run 'hermes doctor --fix' if missing"

# 3. Check fallback providers count
echo ""
echo "3️⃣  Fallback providers in config:"
grep -c "^\s*- provider:" ~/.hermes/config.yaml || echo "   Check config.yaml"

# 4. Check auxiliary models
echo ""
echo "4️⃣  Auxiliary models configured:"
grep -c "^\s*[a-z_]*:" ~/.hermes/config.yaml | head -1 || echo "   Check config.yaml"

# 5. Test primary model
echo ""
echo "5️⃣  Testing primary model (Nemotron 3 Ultra)..."
timeout 30 hermes chat -q "Say OK" 2>&1 | grep -E "(OK|nemotron)" || echo "   ⚠️ Primary model test failed"

# 6. Test speed fallback (Groq)
echo ""
echo "6️⃣  Testing speed fallback (Groq Llama 3.3 70B)..."
timeout 30 hermes chat -q "Say OK" --provider groq 2>&1 | grep -E "(OK|llama)" || echo "   ⚠️ Groq test failed (check GROQ_API_KEY)"

# 7. Test long context fallback (Gemini)
echo ""
echo "7️⃣  Testing long context fallback (Gemini 2.5 Flash)..."
timeout 30 hermes chat -q "Say OK" --provider gemini 2>&1 | grep -E "(OK|gemini)" || echo "   ⚠️ Gemini test failed (check GOOGLE_API_KEY)"

# 8. Test coding fallback (OpenCode Zen)
echo ""
echo "8️⃣  Testing coding fallback (OpenCode Zen)..."
timeout 30 hermes chat -q "Say OK" --provider opencode-zen 2>&1 | grep -E "(OK|mimo)" || echo "   ⚠️ OpenCode Zen test failed (check OPENCODE_ZEN_API_KEY)"

# 9. Check LiteLLM custom provider
echo ""
echo "9️⃣  Testing LiteLLM custom provider..."
timeout 30 hermes chat -q "Say OK" --provider custom:litellm-free 2>&1 | grep -E "(OK|llm)" || echo "   ⚠️ LiteLLM test failed (check LITELLM_MASTER_KEY)"

# 10. Check credential pools
echo ""
echo "🔟  Credential pools configured:"
grep -A 20 "credential_pools:" ~/.hermes/config.yaml | head -25

echo ""
echo "✅ Verification complete"
echo ""
echo "Next steps if any failed:"
echo "  - Missing keys: add to ~/.hermes/.env"
echo "  - Config issues: run 'hermes doctor --fix'"
echo "  - Local models: install Ollama and pull qwen3.5:27b"