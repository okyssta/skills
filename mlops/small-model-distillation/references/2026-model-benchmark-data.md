# 2026 Model Benchmark Reference

Quick-reference benchmark data for distillation decisions. All numbers sourced from public leaderboards (Jul 2026).

## Target teacher: DeepSeek V4 Flash

| Spec | Value |
|---|---|
| Total params | 284B |
| Active params | 13B (MoE) |
| Architecture | CSA + HCA sparse attention |
| Context | 1M tokens |
| MMLU-Pro | **86.2%** |
| GPQA Diamond | **88.1%** |
| Terminal Bench 2.0 | **56.9%** |
| License | MIT |
| API price | $0.14/M input, $0.28/M output |

## Target teacher: Nemotron 3 Ultra (free alternative)

| Spec | Value |
|---|---|
| Total params | 550B |
| Active params | 55B (MoE) |
| Architecture | Hybrid Mamba-Transformer MoE |
| Context | 1M tokens |
| Tool calling | Excels (NVIDIA's focus for this model) |
| Agentic reasoning | Designed for orchestration/planning |
| License | Open (NVIDIA Open Model) |
| API price | **$0 (free)** via OpenRouter free tier (200 req/day) or NVIDIA NIM (~1K free credits) |
| Paid API | Same $0.14/$0.28 range if you need rate limits |

## Student candidates: Qwen3.5 family

| Model | Params | Arch | Context | MMLU-Pro | GPQA Diamond |
|---|---|---|---|---|---|
| Qwen3.5-4B | 4B dense | Hybrid DeltaNet (3:1) | 262K | **79.1%** | **76.2%** |
| Qwen3.5-9B | 9B dense | Hybrid DeltaNet (3:1) | 262K | **82.5%** | **81.7%** |
| Qwen3.5-27B | 27B dense | Hybrid DeltaNet | 262K | ~85% | ~84% |
| Qwen3.5-35B-A3B | 35B/3B active MoE | Hybrid DeltaNet MoE | 262K | ~86% | ~85.5% |

Qwen3.5 architecture: 8×(3×DeltaNet→FFN→1×Attention→FFN) for 4B, 32 layers total. DeltaNet is a gated linear attention variant — O(n) instead of O(n²). This is why 9B punches above its weight.

## Inference VRAM

| Model | BF16 | Q4 (NF4) | Q4_K_M |
|---|---|---|---|
| Qwen3.5-4B | ~8 GB | ~3 GB | ~2.5 GB |
| Qwen3.5-9B | ~18 GB | ~5.5 GB | ~4.5 GB |
| Qwen3.5-27B | ~54 GB | ~14 GB | ~12 GB |

## Training VRAM (Unsloth)

Using Unsloth's optimized kernels. Default seq_len=4096, gradient checkpointing ON.

| Model | Full FT BF16 | LoRA BF16 | QLoRA NF4 |
|---|---|---|---|
| Qwen3.5-4B | 20-24 GB | 8-12 GB | **3-5 GB** |
| Qwen3.5-9B | 40-48 GB | 20-24 GB | **6-8 GB** |
| Qwen3.5-27B | 72-80 GB | 48-56 GB | **20-24 GB** |

## Tool calling (BFCLv4 / TIR-Bench)

| Model | Score | Notes |
|---|---|---|
| Claude Opus 4.5 | ~98% | Frontier closed |
| GPT-5.2 | ~98% | Frontier closed |
| DeepSeek V4 Flash | ~97% | Best open teacher |
| Qwen3.5-4B | **97.5%** | Beat models 5× its size |
| Qwen3.5-9B | ~98% | Near frontier |
| Qwen3-4B-Instruct-2507 | ~96% | Previous gen, still competitive |
| Hammer-4B (distilled) | 76 on leaderboard | Older SOTA for 4B |

## Data generation costs

### Direct API (DeepSeek V4 Flash at $0.14/M in, $0.28/M out)

| # Trajectories | Avg tok/traj | Output tokens | Cost |
|---|---|---|---|
| 1K | 5K | 5M | **$1.40** |
| 5K | 5K | 25M | **$7** |
| 10K | 5K | 50M | **$14** |
| 20K | 5K | 100M | **$28** |
| 100K | 5K | 500M | **$140** |

### OpenCode Go subscription ($10/mo, same per-token pricing as direct)

$12/5h + $30/week + $60/month. 10K trajectories = ~$4.20 (fits in one $12/5h window, ~90 min wall time).

| Dataset | Trajectories | Cost from credit | Windows needed | Wall time |
|---|---|---|---|---|
| Small | 1K | ~$0.42 | <1 | ~10 min |
| Medium | 10K | ~$4.20 | <1 | ~90 min |
| Large | 50K | ~$21 | 2 | ~8 hours |
| Max | 100K | ~$42 | 4 | ~18 hours |

### Free tiers (slow, good for proof-of-concept)

| Provider | Free model | Rate limit | 10K trajectories wall time |
|---|---|---|---|
| OpenRouter | Nemotron 3 Ultra | 200 req/day | ~50 days |
| NVIDIA NIM | Nemotron 3 Ultra | ~1K credits total, 40 req/min | Exhausts credits at ~1K samples |

### Key insight: best cost comes from matching provider to scale

- **<1K trajectories** (prototyping): use free OpenRouter/NVIDIA NIM tier
- **1K-20K** (serious training): use OpenCode Go $10/mo credit or direct API for ~$14-28
- **20K-100K** (maxing out): direct API at $28-140, no caps to manage

## Key papers / references

- PostTrainLLM: Mac-based frontier distillation (tool-calling parity)
- Qwen3.5 technical report: Hybrid DeltaNet architecture
- DeepSeek V4 technical report: CSA + HCA sparse attention
- Unsloth QLoRA benchmarks: VRAM/training time tables
