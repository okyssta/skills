# Benchmark Bars & Compare Page Reference

## Model Page Benchmark Bars

Model pages show horizontal bar charts comparing the current model to top 7 models per benchmark. The current model always appears (injected even if below top 7, then re-sorted).

### Route Pattern (app.py)

```python
benchmark_leaderboards = {}
bench_names = list(dict.fromkeys(r.benchmark_name for r in result_rows))
for bname in bench_names[:30]:
    top_results = session.query(BenchmarkResult, Model.name).join(
        Model, Model.slug == BenchmarkResult.model_slug
    ).filter(
        BenchmarkResult.benchmark_name == bname,
        BenchmarkResult.harness == "",
    ).order_by(desc(BenchmarkResult.score)).limit(7).all()

    entries = []
    seen = set()
    for br, mname in top_results:
        seen.add(br.model_slug)
        entries.append({"name": mname or br.model_slug, "slug": br.model_slug,
                        "score": br.score, "is_current": br.model_slug == slug})

    # Ensure current model always visible
    if slug not in seen:
        current = session.query(BenchmarkResult, Model.name).join(
            Model, Model.slug == BenchmarkResult.model_slug
        ).filter(
            BenchmarkResult.model_slug == slug,
            BenchmarkResult.benchmark_name == bname
        ).first()
        if current:
            br, mname = current
            entries.append({"name": mname or slug, "slug": slug,
                           "score": br.score, "is_current": True})
            entries.sort(key=lambda e: e["score"], reverse=True)

    if entries:
        benchmark_leaderboards[bname] = entries
```

### Bar Width Rule

Bar width = raw score (capped at 100). Do NOT compute `score / max_score * 100` — the user explicitly corrected this.

```html
<div class="benchmark-bar-fill" style="width:{{'%d'|format(e.score if e.score <= 100 else 100)}}%"></div>
```

## Compare Page Benchmarks

The compare route fetches ALL BenchmarkResult rows for compared models and groups by benchmark name:

```python
results = session.query(BenchmarkResult).filter(
    BenchmarkResult.model_slug.in_(slugs)
).order_by(BenchmarkResult.benchmark_name).all()
grouped = {}
for r in results:
    key = r.benchmark_name
    if key not in grouped:
        grouped[key] = {"name": key, "metric": r.metric, "scores": {}}
    grouped[key]["scores"][r.model_slug] = r.score
benchmark_rows = sorted(grouped.values(), key=lambda x: x["name"])
```

The template iterates benchmark_rows. Missing scores show "—".

## Section Header Icons

Section headers on the compare page use inline SVG icons, NEVER emojis. The `.section-icon` class handles vertical alignment:

```html
<tr class="section-header">
  <th colspan="3">
    <svg class="section-icon" viewBox="0 0 24 24" width="16" height="16">
      <path d="M4 19V9m6 10V5m6 14v-7m4 7H2"/>
    </svg> Benchmarks
  </th>
</tr>
```

```css
.section-icon{display:inline;vertical-align:middle;margin-right:6px;color:var(--muted)}
```
