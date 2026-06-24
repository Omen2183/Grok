#!/usr/bin/env bash
# Install Grok D&D skills into Grok Build.
# Usage: ./install.sh [target_dir]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-.}"
SOURCE_SKILLS="$REPO_ROOT/.grok/skills"
DEST_SKILLS="$TARGET/.grok/skills"

if [[ ! -d "$SOURCE_SKILLS" ]]; then
  echo "Skills directory not found: $SOURCE_SKILLS" >&2
  exit 1
fi

mkdir -p "$DEST_SKILLS"
count=0

for skill_dir in "$SOURCE_SKILLS"/*/; do
  skill_name="$(basename "$skill_dir")"
  if [[ -f "$skill_dir/SKILL.md" ]]; then
    cp -R "$skill_dir" "$DEST_SKILLS/$skill_name"
    echo "  OK $skill_name"
    ((count++)) || true
  fi
done

echo ""
echo "Installed $count skills to $DEST_SKILLS"
echo "Say 'Let's play D&D' to start a campaign."