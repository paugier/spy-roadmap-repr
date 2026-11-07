# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown"]
# ///
"""Validate data/*.toml and build site/index.html (run: uv run build.py).

Data layout:
  data/<pillar>.toml          one file per pillar; top-level `title` and `order`,
                              then one [node-id] table per node (prerequisites go in
                              `blockers` and `contributors`)
  data/descriptions/<id>.md   optional long description of a node, in Markdown
                              (Python-Markdown: fenced code, tables, `!!! note "Title"`
                              admonitions, and `[text](node:<id>)` links to other nodes)
"""
import json, re, sys, tomllib
from pathlib import Path
import markdown

ROOT = Path(__file__).parent
DATA = ROOT / "data"
KINDS = {"goal", "feature", "task", "problem", "bug"}
# "blocked" is not stored: the page derives it (planned or in-progress node with an unfinished blocker).
STATUSES = {"idea", "planned", "in-progress", "done"}
REQUIRED = {"title", "kind", "status", "summary"}
OPTIONAL = {"when", "blockers", "contributors", "links"}
PILLAR_KEYS = {"title", "order"}


def load():
    """Return (pillars, nodes, errors). The pillar of a node is its file name."""
    pillars, nodes, errors, seen = [], [], [], {}
    for path in sorted(DATA.glob("*.toml")):
        pillar = path.stem
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            errors.append(f"{path.name}: {e}")
            continue
        pillars.append({"id": pillar, "title": raw.get("title", pillar), "order": raw.get("order", 100)})
        for key in raw.keys() & PILLAR_KEYS:
            raw.pop(key)
        for nid, fields in raw.items():
            if not isinstance(fields, dict):
                errors.append(f"{path.name}: unexpected top-level key {nid!r} (nodes are [tables])")
                continue
            if nid in seen:
                errors.append(f"duplicate id {nid} ({seen[nid]} and {path.name})")
            seen[nid] = path.name
            nodes.append({"id": nid, "pillar": pillar, **fields})
    pillars.sort(key=lambda p: (p["order"], p["id"]))
    return pillars, nodes, errors


def attach_descriptions(nodes, errors):
    ids = {n["id"] for n in nodes}
    folder = DATA / "descriptions"
    for path in sorted(folder.glob("*.md")):
        if path.stem == "README":
            continue
        if path.stem not in ids:
            errors.append(f"descriptions/{path.name}: no node with id {path.stem}")
    for n in nodes:
        path = folder / f"{n['id']}.md"
        if path.exists():
            html = markdown.markdown(
                path.read_text(encoding="utf-8"), extensions=["fenced_code", "tables", "admonition"])

            def node_link(m):
                if m["id"] not in ids:
                    errors.append(f"descriptions/{path.name}: link to unknown node {m['id']}")
                return f'href="#" data-node="{m["id"]}"'

            n["description_html"] = re.sub(r'href="node:(?P<id>[^"]+)"', node_link, html)


def validate(nodes):
    errors, ids = [], {n["id"] for n in nodes}
    for n in nodes:
        i = n["id"]
        missing = REQUIRED - n.keys()
        if missing:
            errors.append(f"{i}: missing {sorted(missing)}")
        unknown = n.keys() - REQUIRED - OPTIONAL - {"id", "pillar", "description_html"}
        if unknown:
            errors.append(f"{i}: unknown field(s) {sorted(unknown)}")
        if n.get("kind") not in KINDS:
            errors.append(f"{i}: bad kind {n.get('kind')}")
        if n.get("status") not in STATUSES:
            errors.append(f"{i}: bad status {n.get('status')}")
        for field in ("blockers", "contributors"):
            errors += [f"{i}: unknown id in {field}: {d}" for d in n.get(field, []) if d not in ids]
        both = set(n.get("blockers", [])) & set(n.get("contributors", []))
        if both:
            errors.append(f"{i}: {sorted(both)} in both blockers and contributors")
    deps = {n["id"]: n.get("blockers", []) + n.get("contributors", []) for n in nodes}
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
    pillars, nodes, errors = load()
    attach_descriptions(nodes, errors)
    errors += validate(nodes)
    if errors:
        sys.exit("\n".join(errors))
    payload = json.dumps({"pillars": pillars, "nodes": nodes}, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "site_src" / "index.html").read_text().replace("__DATA__", payload)
    out = ROOT / "site"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"{len(nodes)} nodes in {len(pillars)} pillars -> site/index.html")


if __name__ == "__main__":
    main()
