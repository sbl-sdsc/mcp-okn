#!/usr/bin/env bash
# Rebuild the committed skill packages from their folders: skills/<skill>.skill and
# skills/<skill>.zip. Both are the same zip archive (the skill folder at the root,
# minus __pycache__/.DS_Store). Claude Desktop and claude.ai only accept a `.skill`
# upload; the `.zip` serves the other clients and the README's curl + unzip install.
# CI fails when either one is out of sync with its folder, so run this after any
# edit under skills/.
set -euo pipefail
cd "$(dirname "$0")/../skills"
for skill in okn-report-style okn-bioanalysis; do
  rm -f "$skill.zip" "$skill.skill"
  zip -rq "$skill.zip" "$skill" -x '*/__pycache__/*' -x '*.DS_Store'
  cp "$skill.zip" "$skill.skill"
  echo "built skills/$skill.skill and skills/$skill.zip"
done
