#!/usr/bin/env python3
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = json.loads((ROOT / "cow-memory/provenance.json").read_text())
MIGRATIONS = ROOT / "hindsight-api-slim/hindsight_api/alembic/versions"

revisions: dict[str, str] = {}
down_revisions: set[str] = set()
file_hashes: dict[str, str] = {}

for path in sorted(MIGRATIONS.glob("*.py")):
    revision = None
    down_revision = None
    for node in ast.parse(path.read_text()).body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if not isinstance(target, ast.Name) or target.id not in {"revision", "down_revision"}:
                continue
            value = ast.literal_eval(node.value)
            if target.id == "revision":
                revision = value
            else:
                down_revision = value
    if not isinstance(revision, str):
        raise SystemExit(f"missing revision in {path}")
    revisions[revision] = path.name
    if isinstance(down_revision, str):
        down_revisions.add(down_revision)
    elif isinstance(down_revision, (tuple, list)):
        down_revisions.update(value for value in down_revision if value)
    file_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

actual = {
    "heads": sorted(set(revisions) - down_revisions),
    "migration_count": len(revisions),
    "tree_sha256": hashlib.sha256(
        "".join(f"{name}:{file_hashes[name]}\n" for name in sorted(file_hashes)).encode()
    ).hexdigest(),
}
expected = PROVENANCE["schema"]
if actual != expected:
    raise SystemExit(f"schema provenance mismatch: expected={expected!r} actual={actual!r}")
if PROVENANCE["license"] != "MIT" or "MIT License" not in (ROOT / "LICENSE").read_text():
    raise SystemExit("license provenance mismatch")
print(json.dumps({"upstream_base": PROVENANCE["upstream_base"], "schema": actual}, sort_keys=True))
