#!/bin/bash
# Ad-hoc verification script for docsify documentation sites.
# Cross-references commands + permissions from plugin.yml against docs.
# Usage: bash verify-docs.sh [project-base-dir]
# If no argument given, uses current directory.

set -e
BASE="${1:-.}"
DOCS="$BASE/docs"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== Docsify Documentation Verification ==="
echo ""

echo "[Required files]"
for f in \
    "$DOCS/index.html" "$DOCS/_sidebar.md" "$DOCS/_coverpage.md" "$DOCS/README.md" \
    "$DOCS/installation.md" "$DOCS/commands.md" "$DOCS/permissions.md" \
    "$DOCS/configuration.md" "$DOCS/api.md" "$DOCS/faq.md" \
    "$BASE/README.md" "$BASE/CONTRIBUTING.md" "$BASE/LICENSE"; do
    [ -f "$f" ] && pass "$(basename $f)" || fail "$(basename $f) MISSING"
done

echo "[HTML structure]"
grep -q 'docsify.min.js' "$DOCS/index.html" 2>/dev/null && pass "docsify script" || fail "docsify script missing"
grep -q 'loadSidebar' "$DOCS/index.html" 2>/dev/null && pass "loadSidebar" || fail "loadSidebar missing"
grep -q 'coverpage' "$DOCS/index.html" 2>/dev/null && pass "coverpage" || fail "coverpage missing"

echo "[Sidebar link validation]"
SIDEBAR="$DOCS/_sidebar.md"
for link in README.md installation.md commands.md permissions.md configuration.md api.md faq.md; do
    grep -qi "$link" "$SIDEBAR" 2>/dev/null && pass "$link" || fail "$link missing from sidebar"
done

echo "[Command coverage]"
PLUGIN_YML="$BASE/src/main/resources/plugin.yml"
if [ -f "$PLUGIN_YML" ]; then
    grep -A500 '^commands:' "$PLUGIN_YML" | grep '^  [a-z]' | sed 's/://' | awk '{print $1}' | while read cmd; do
        [ -z "$cmd" ] && continue
        echo "$cmd" | grep -q '\.' && continue  # skip subcommand nodes
        if grep -qi "[/]\?$cmd\b" "$DOCS/commands.md" 2>/dev/null; then
            echo "  PASS: /$cmd"
        else
            echo "  FAIL: /$cmd NOT documented"
            exit 1
        fi
    done || fail "Command check had errors"
    pass "All commands verified"
else
    echo "  (no plugin.yml found, skipping command check)"
fi

echo "[Permission coverage]"
if [ -f "$PLUGIN_YML" ]; then
    grep -E '^  casualbans\.' "$PLUGIN_YML" | sed 's/:.*//' | awk '{print $1}' | while read perm; do
        [ -z "$perm" ] && continue
        if grep -qiF "$perm" "$DOCS/permissions.md" 2>/dev/null; then
            echo "  PASS: $perm"
        else
            echo "  FAIL: $perm MISSING from permissions.md"
            exit 1
        fi
    done || fail "Permission check had errors"
    pass "All permissions verified"
else
    echo "  (no plugin.yml found, skipping permission check)"
fi

echo "[LICENSE]"
grep -qi "MIT License\|Apache\|GNU" "$BASE/LICENSE" 2>/dev/null && pass "LICENSE present" || fail "LICENSE missing or unrecognized"

echo "[CONTRIBUTING sections]"
[ -f "$BASE/CONTRIBUTING.md" ] && pass "CONTRIBUTING exists" || fail "CONTRIBUTING missing"
grep -qi "Pull Request" "$BASE/CONTRIBUTING.md" 2>/dev/null && pass "PR process" || fail "PR process section missing"
grep -qi "gradlew\|npm\|build\|make" "$BASE/CONTRIBUTING.md" 2>/dev/null && pass "Build steps" || fail "Build steps section missing"

echo "[File size sanity]"
for f in "$DOCS/index.html" "$DOCS/_sidebar.md" "$DOCS/_coverpage.md" "$DOCS/README.md" "$DOCS/installation.md" "$DOCS/commands.md" "$DOCS/permissions.md" "$DOCS/configuration.md" "$DOCS/api.md" "$DOCS/faq.md"; do
    [ -f "$f" ] || continue
    sz=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
    [ "$sz" -gt 200 ] && pass "$(basename $f) ($sz B)" || fail "$(basename $f) too small ($sz B)"
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "=== VERIFIED ===" || echo "=== ISSUES FOUND ==="
exit $FAIL
