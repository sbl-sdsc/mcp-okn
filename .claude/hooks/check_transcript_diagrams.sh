#!/usr/bin/env bash
# Stop hook: enforce the query-diagram completeness gate on reproducibility transcripts.
#
# Blocks stopping when a *reproducibility*.md file in the WORKING TREE (modified/staged/untracked —
# so committed example files never trigger it) has ```sparql blocks with no following ```mermaid,
# i.e. the defer-and-re-add flow's re-add half was skipped. The block reason tells the model exactly
# how to fix it. Verification is `readd_query_diagrams.py --check`, which needs no third-party package.
#
# Portable across bash 3.2 (macOS) and zsh: no `mapfile`, no arrays-from-process-substitution.
set -u

input="$(cat)"

# Avoid an infinite loop: if we already blocked once in this stop-sequence, let the stop through.
if printf '%s' "$input" | jq -e '.stop_hook_active == true' >/dev/null 2>&1; then
  exit 0
fi

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
checker="$root/skills/okn-report-style/scripts/readd_query_diagrams.py"
[ -f "$checker" ] || exit 0            # skill not present in this repo → nothing to enforce
cd "$root" 2>/dev/null || exit 0

# Working-tree reproducibility transcripts: unstaged + staged + untracked, deduped.
candidates="$({ git diff --name-only; git diff --cached --name-only; \
                git ls-files --others --exclude-standard; } 2>/dev/null \
              | grep -iE 'reproducibility.*\.md$' | sort -u)"
[ -z "$candidates" ] && exit 0

failed=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue
  if ! python3 "$checker" "$f" --check >/dev/null 2>&1; then
    failed="$failed $f"
  fi
done <<EOF
$candidates
EOF

[ -z "${failed# }" ] && exit 0         # every transcript PASSed → allow the stop

reason="Query-diagram completeness gate FAILED for:${failed}. These reproducibility transcript(s) \
have \`\`\`sparql blocks with NO \`\`\`mermaid diagram — the defer-and-re-add flow's re-add half was \
skipped (a silent drop). Fix before stopping: run \`python skills/okn-report-style/scripts/\
readd_query_diagrams.py <file>\` for each (in a report session it emits a work-list to feed the \
sparql_to_mermaid tool, then re-run with --diagrams diagrams.json), then confirm \
\`readd_query_diagrams.py --check <file>\` prints PASS. If the user asked for NO query diagrams, there \
are no such blocks and this never fires. Do not stop until --check PASSes."

jq -n --arg r "$reason" '{decision:"block", reason:$r}'
exit 0
