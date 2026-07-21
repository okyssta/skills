#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# HERMES AGENT — FREE TIER SETUP SCRIPT
# Automates configuration of all free providers for 100% free usage
# Part of hermes-free-tier-setup skill
# ──────────────────────────────────────────────────────────────────────

set -euo pipefail

CONFIG_TEMPLATE="$(dirname "$0")/../templates/config-free-tier.yaml"
TARGET_CONFIG="$HOME/.hermes/config.yaml"
ENV_FILE="$HOME/.hermes/.env"

echo "═══════════════════════════════════════════════════════════════════"
echo "  HERMES AGENT — FREE TIER SETUP"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check if template exists
if [[ ! -f "$CONFIG_TEMPLATE" ]]; then
    echo "❌ Config template not found: $CONFIG_TEMPLATE"
    exit 1
fi

# Backup existing config
if [[ -f "$TARGET_CONFIG" ]]; then
    cp "$TARGET_CONFIG" "$TARGET_CONFIG.backup.$(date +%Y%m%d-%H%M%S)"
    echo "✅ Backed up existing config"
fi

# Copy free tier config
cp "$CONFIG_TEMPLATE" "$TARGET_CONFIG"
echo "✅ Applied free-tier config to $TARGET_CONFIG"

# Create .env template if not exists
if [[ ! -f "$ENV_FILE" ]]; then
    cat > "$ENV_FILE" << 'EOF'
# ──────────────────────────────────────────────────────────────────────
# HERMES AGENT — FREE TIER API KEYS
# Add your keys below (get them from the URLs in comments)
# ──────────────────────────────────────────────────────────────────────

# CORE PROVIDERS (recommended priority order)
OPENROUTER_API_KEY=           # https://openrouter.ai/keys
GROQ_API_KEY=                 # https://console.groq.com/keys
GOOGLE_API_KEY=               # https://aistudio.google.com/apikey
NVIDIA_API_KEY=               # https://build.nvidia.com/explore/discover

# ADDITIONAL FREE PROVIDERS
OPENCODE_ZEN_API_KEY=         # https://opencode.ai/auth
NOVITA_API_KEY=               # https://novita.ai/
HF_TOKEN=                     # https://huggingface.co/settings/tokens
GITHUB_MODELS_TOKEN=          # GitHub Personal Access Token (ghp_...)
CLOUDFLARE_API_TOKEN=         # https://dash.cloudflare.com/profile/api-tokens
KIMI_API_KEY=                 # https://platform.moonshot.cn/
COHERE_API_KEY=               # https://dashboard.cohere.com/api-keys
MISTRAL_API_KEY=              # https://console.mistral.ai/api-keys
CEREBRAS_API_KEY=             # https://cloud.cerebras.ai/

# LOCAL PROVIDERS (optional - leave blank for no auth)
OLLAMA_API_KEY=               # Local Ollama (usually not needed)
VLLM_API_KEY=                 # Local vLLM
SGLANG_API_KEY=               # Local SGLang
LM_API_KEY=                   # LM Studio
LITELLM_MASTER_KEY=           # Your LiteLLM proxy

# ──────────────────────────────────────────────────────────────────────
# OPTIONAL: Multiple keys per provider for key stacking (multiply limits)
# OPENROUTER_API_KEY_2=
# OPENROUTER_API_KEY_3=
# GROQ_API_KEY_2=
# GOOGLE_API_KEY_2=
# NVIDIA_API_KEY_2=
# ──────────────────────────────────────────────────────────────────────
EOF
    echo "✅ Created .env template at $ENV_FILE"
else
    echo "ℹ️  .env already exists, skipping template creation"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  NEXT STEPS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "1. EDIT YOUR API KEYS:"
echo "   nano $ENV_FILE"
echo ""
echo "2. GET FREE API KEYS (priority order):"
echo "   🥇 OpenRouter:   https://openrouter.ai/keys          (200 req/day, 27+ free models)"
echo "   🥈 Groq:         https://console.groq.com/keys       (1K req/day, 320 tok/s)"
echo "   🥉 Google AI:    https://aistudio.google.com/apikey  (1,500 RPD, 1M context)"
echo "   🏅 NVIDIA NIM:   https://build.nvidia.com/           (free credits, no expiry)"
echo "   🏅 OpenCode Zen: https://opencode.ai/auth             (5 free coding models)"
echo "   🏅 NovitaAI:     https://novita.ai/                  (free credits on signup)"
echo "   🏅 Hugging Face: https://huggingface.co/settings/tokens (monthly credits)"
echo "   🏅 GitHub Models: https://github.com/settings/tokens (Frontier models free)"
echo "   🏅 Cloudflare:   https://dash.cloudflare.com/profile/api-tokens (10K neurons/day)"
echo ""
echo "3. FOR LOCAL MODELS (zero cost, no limits):"
echo "   curl -fsSL https://ollama.ai/install.sh | sh"
echo "   ollama pull qwen3.5:27b   # Needs 16GB VRAM"
echo "   # Or for 8GB VRAM: ollama pull qwen3:8b"
echo ""
echo "4. TEST YOUR SETUP:"
echo "   hermes doctor                    # Check configuration"
echo "   hermes chat                      # Start chatting"
echo ""
echo "5. SWITCH MODELS ON THE FLY:"
echo "   /model openrouter/free           # Auto-select free model"
echo "   /model groq/llama-3.3-70b-versatile"
echo "   /model gemini/gemini-2.5-flash"
echo "   /model ollama/qwen3.5:27b"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  KEY STACKING TIP: Add multiple keys per provider to multiply limits!"
echo "  Edit ~/.hermes/.env and add OPENROUTER_API_KEY_2, OPENROUTER_API_KEY_3, etc."
echo "══════════════════════════════════════════════════════════════════════"