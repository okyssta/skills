# eBay API Timing Benchmarks

Real-world timing data from a production run (June 2026, 561 active listings, beekeeping supplies account).

## Setup
- **Account**: 561 total active listings (411 AU, 106 US, 41 UK)
- **Region**: Australia (but GetMyeBaySelling returns all sites regardless of Site ID)
- **Auth method**: OAuth (X-EBAY-API-IAF-TOKEN header)
- **Delay between calls**: 0.25s (sequential), 0.05s (parallel)
- **API timeout per call**: 60s
- **Retries**: 3 with 2s/4s/8s backoff (10s/20s/40s for rate-limit errors 218050, 21919165)

## Sequential Timing
| Metric | Value |
|--------|-------|
| Items processed | 561 |
| Time per item (avg) | ~1.3s |
| Total time | ~12 minutes |
| Bottleneck | API round-trip + 0.25s deliberate delay |
| AU items found | 411 (73% of total) |
| Non-AU found: | US=106, UK=41 |

## Parallel Timing (8 workers, ThreadPoolExecutor)
| Metric | Value |
|--------|-------|
| Items processed | 561 |
| Throughput | ~9-10 items/sec |
| Total time | ~60 seconds |
| Bottleneck | API-side concurrency limits (~60 calls/min per IP) |
| Risk | Rate-limit errors (codes 218050, 21919165) at higher worker counts |

## Two-Phase Approach
The eBay Trading API workflow requires two phases:
1. **GetMyeBaySelling** (phase 1): Collect all ItemIDs. Fast — ~3 pages @ 200/page.
2. **GetItem** (phase 2): Fetch details per ItemID. Slow — 1 call per listing (the bottleneck).

**Always prefer parallel (ThreadPoolExecutor, 8 workers) for phase 2.**

## Sequential Use Case
The sequential approach is useful when:
- eBay rate limits are tight (the sequential approach never hits them)
- You need to process items from a specific site only (and skip others)
- Python concurrency isn't available (limited environments)
- You want simple, debuggable output

Otherwise, the parallel script (`scripts/fetch_all_listings.py`) is strictly better.

## CSV Output Notes
- Use `encoding="utf-8-sig"` (UTF-8 with BOM) for CSV files — Excel on Windows requires the BOM to recognize UTF-8.
- The `utf-8-sig` encoding produces a byte-order-mark (BOM) at the start of the file that Excel reads as a UTF-8 signal.
