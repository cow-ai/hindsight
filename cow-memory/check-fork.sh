#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$ROOT"

BASE="$(python3 -c 'import json; print(json.load(open("cow-memory/provenance.json"))["upstream_base"])')"
EXPECTED_ORIGIN='https://github.com/cow-ai/hindsight.git'
EXPECTED_UPSTREAM='https://github.com/vectorize-io/hindsight.git'

[[ "$(git remote get-url origin)" == "$EXPECTED_ORIGIN" ]] || { echo 'origin must be the Cow fork' >&2; exit 1; }
[[ "$(git remote get-url upstream)" == "$EXPECTED_UPSTREAM" ]] || { echo 'upstream must be the official Hindsight repository' >&2; exit 1; }
git merge-base --is-ancestor "$BASE" HEAD || { echo 'Cow branch does not descend from the recorded upstream base' >&2; exit 1; }
[[ -f LICENSE ]] || { echo 'LICENSE is missing' >&2; exit 1; }
[[ -z "$(git diff --name-only "$BASE"..HEAD -- hindsight-api-slim/hindsight_api/alembic/versions)" ]] || {
  echo 'schema changed; update provenance and compatibility evidence before advancing the pin' >&2
  exit 1
}
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo 'tracked fork files are dirty' >&2; exit 1; }

python3 cow-memory/verify-provenance.py
printf 'upstream_base=%s\n' "$BASE"
printf 'cow_head=%s\n' "$(git rev-parse HEAD)"
printf 'patch_files=%s\n' "$(git diff --name-only "$BASE"..HEAD | wc -l | tr -d ' ')"
