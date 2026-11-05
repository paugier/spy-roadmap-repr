# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Validate data/nodes.yaml and build site/index.html (run: uv run build.py)."""
import json, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parent
KINDS = {"goal", "feature", "task", "problem", "bug"}
STATUSES = {"idea", "planned", "in-progress", "done", "blocked"}
REQUIRED = {"id", "title", "kind", "status", "pillar", "summary"}


def validate(nodes):
    errors, ids = [], set()
    for n in nodes:
        missing = REQUIRED - n.keys()
        if missing:
            errors.append(f"{n.get('id', n)}: missing {sorted(missing)}")
            continue
        if n["id"] in ids:
            errors.append(f"duplicate id {n['id']}")
        ids.add(n["id"])
        if n["kind"] not in KINDS:
            errors.append(f"{n['id']}: bad kind {n['kind']}")
        if n["status"] not in STATUSES:
            errors.append(f"{n['id']}: bad status {n['status']}")
    deps = {n["id"]: n.get("depends_on", []) for n in nodes if "id" in n}
    for i, ds in deps.items():
        errors += [f"{i}: unknown dependency {d}" for d in ds if d not in ids]
    state = {}

    def visit(i, path):
        if state.get(i) == 1:
            errors.append("cycle: " + " -> ".join(path + [i]))
        if i in state or i not in deps:
            return
        state[i] = 1
        for d in deps[i]:
            visit(d, path + [i])
        state[i] = 2

    for i in deps:
        visit(i, [])
    return errors


def main():
    nodes = yaml.safe_load((ROOT / "data" / "nodes.yaml").read_text())
    errors = validate(nodes)
    if errors:
        sys.exit("\n".join(errors))
    payload = json.dumps({"nodes": nodes}, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "site_src" / "index.html").read_text().replace("__DATA__", payload)
    out = ROOT / "site"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"{len(nodes)} nodes -> site/index.html")


if __name__ == "__main__":
    main()
