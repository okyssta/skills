# Self-Audit via Reference Subagent Convergence

## Problem

When auditing your own work, you can fall into confirmation loops — re-reading the same files and re-drawing the same conclusions. The diagnosis may be wrong but there's no external check.

## Technique

Spawn 3-4 parallel subagents with the same brief and let them converge:

```
delegate_task(
    goal="Audit the current state of <project>",
    context="""
    Review these files: <paths>
    Check these criteria: <list>
    Report: what's working, what's missing, what's broken, what's overclaimed.
    Be honest — flag any gap between the plan and real implementation.
    """
)
```

## How to Interpret Results

- **All converge on same diagnosis** → high confidence the diagnosis is correct. Execute the fixes.
- **2 agree, 2 disagree** → fix what the majority identifies, but flag the disagreement for manual review.
- **All say different things** → the question or context was wrong. Reformulate and retry.

## Pitfalls

- Subagents have NO memory of prior conversation. Pass enough context (file paths, error messages, recent output) or they'll hallucinate from incomplete state.
- Subagents cannot call `clarify` or `memory`. If your brief requires information you don't have, restructure it to be self-contained.
- Subagent summaries are SELF-REPORTS — they can claim "verified correct" without actually testing. For claims about compilation, ask the subagent to run `cargo check` and include the output.
- Convergence on "looks good" from all subagents is LESS trustworthy than convergence on specific errors. A bug-free system requires subagents to *fail* to find problems, which is hard to verify. The technique is strongest for finding missing features, stubs, and overclaims.
