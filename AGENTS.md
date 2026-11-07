# AGENTS.md

Everything needed to work on this repository. For a short introduction, see `README.md`.

## What this project is

A static website, generated from TOML and Markdown files, that represents the
[SPy](https://github.com/spylang/spy) project as a graph: goals, features, tasks,
problems and bugs, and "cannot be finished or used without" relations between them. It
replaces the flat and outdated `ROADMAP.md` of SPy as a communication tool. The site is
deployed to <https://paugier.github.io/spy-roadmap-repr/> by GitHub Actions.

Keep the project small: no framework, no bundler, little maintenance.

## Commands

```sh
uv run build.py                        # validate data/ and write site/index.html
uv run python -m http.server -d site   # serve it on http://localhost:8000
make build | serve | clean             # same, through the Makefile
```

`build.py` declares its only dependency (`markdown`) inline, so `uv` needs no setup. It
exits with a non-zero status and a list of problems if the data is invalid. Always run it
after editing `data/`, `build.py` or `site_src/`.

The build cannot catch JavaScript errors. The page loads Cytoscape.js and dagre from
jsDelivr, so testing it needs a browser with network access.

## Layout

| Path | Role |
| --- | --- |
| `data/<pillar>.toml` | One file per pillar (file name = pillar id). One `[node-id]` table per node. |
| `data/descriptions/<node-id>.md` | Optional long description of a node. |
| `build.py` | Validates the data, renders descriptions, injects everything as JSON into the template, writes `site/index.html`. |
| `site_src/index.html` | Page template: HTML, CSS and JS in one file. `__DATA__` is replaced by the JSON. |
| `.github/workflows/pages.yml` | On every push to `main`: `uv run build.py`, then deploy `site/`. |
| `site/` | Build output, git-ignored. Never edit it. |

## Data model

A pillar file starts with two top-level keys, `title` and `order` (pillars are sorted by
`order`, then by id). Each `[table]` after them is a node, and the table name is the node
id (unique across all files, kebab-case).

```toml
# data/memory.toml
title = "Memory management"
order = 3

[gc-ref]
title = "gc_ref and raw_ref"
kind = "feature"
status = "done"
when = "2026-Q1"
summary = "Typed references for each allocation kind."
depends_on = ["gc-alloc"]   # ids may live in any pillar file
links = ["https://github.com/spylang/spy/pull/383"]
```

| Field | Required | Values / meaning |
| --- | --- | --- |
| table name | yes | Unique id, used in `depends_on` and in description links. |
| `title` | yes | Short label shown in the graph. |
| `kind` | yes | `goal`, `feature`, `task`, `problem`, `bug`. |
| `status` | yes | `idea`, `planned`, `in-progress`, `done`, `blocked`. |
| `summary` | yes | One or two sentences a reader without compiler background can follow. |
| `when` | no | Quarter such as `"2026-Q2"` (a string). |
| `depends_on` | no | Ids of prerequisites. |
| `links` | no | PR and issue URLs (shown without the `https://github.com/spylang/spy/` prefix). |

The pillar of a node is the file it lives in. To add a pillar, add `data/<id>.toml` with
its own `title` and `order`; if the order collides with an existing pillar, renumber.

Current pillars: Core language (1), Standard library (2), Memory management (3),
Low-level features (4), SPy/C integration (5), SPy/Python integration (6), Documentation
and tooling (7).

### Conventions

- `goal` nodes are the "northern stars"; the Focus menu lists them first. A goal
  may depend on other goals: a main goal (nothing depends on it, drawn bigger, e.g.
  "Faster interpreter", "Python-like stdlib", "Full SPy/Python interop") sits on top
  of the goals of the pillars that lead to it (e.g. "SPy interpreter written in SPy").
  The menu groups them as main and intermediate goals, computed from the
  dependencies; there is no field for it.
- A dependency means "cannot be finished or used without". Add one only when the sources
  state it or the design makes it clear, never to make the graph look connected.
- An edge goes from the prerequisite to what it unlocks, so the layout reads left to
  right from foundations to goals.
- Within a file, put goals first, then nodes in the order you want to read them.
- Status: `done` only for merged work; a feature that is only a proposal is `idea`; one
  that the SPy roadmap already lists is `planned`. Check the PR before choosing
  `in-progress` or `done`.
- `problem` and `bug` nodes are limited to those that block a feature.

### Validation done by `build.py`

TOML syntax errors, missing required fields, unknown fields, unknown `kind` or `status`,
duplicate ids, dependencies on unknown ids, description files without a node, links to
unknown nodes inside descriptions, and dependency cycles.

## Long descriptions

For anything longer than the summary, create `data/descriptions/<node-id>.md`. The file
name must match a node id. It is rendered in the side panel, under the summary.

The dialect is [Python-Markdown](https://python-markdown.github.io/) with the extensions
`fenced_code`, `tables` and `admonition`. It is **not** MyST (the SPy book uses MyST), so
convert when reusing book text:

| MyST | Here |
| --- | --- |
| `:::{admonition} Definition: x` ... `:::` | `!!! note "Definition: x"`, body indented by 4 spaces |
| `` {ref}`label` `` to a roadmap node | `[text](node:<node-id>)`: opens that node in the panel |
| `(label)=` anchors, `{ref}` to book pages | plain text: book pages are not linked |

Pitfalls: a list needs a blank line before it; a heading inside the description should
start at `##` (the panel styles h1 to h3 at the same small size); do not add a title
heading, the node title is already shown.

Style, following the book notes the descriptions come from:

- Write for readers who do not know the advanced concepts, and define technical
  vocabulary in a definition admonition the first time it appears.
- Give complete code excerpts: the SPy code and, when relevant, the lowered C, and explain
  every non-trivial sentence.
- Describe the current plan only, not its history. Keep it short and mention each notion
  once.
- Spellings of proposed features (`InlineArray`, `@noalias`, `ll_union`...) are proposals:
  say so, and do not present them as existing.

## The page

`site_src/index.html` is a single file using [Cytoscape.js](https://js.cytoscape.org/) with
the dagre layout, loaded from jsDelivr at pinned versions (keep exact versions).

- Node colors follow `status` (CSS variables, light and dark theme).
- Selection of what is shown (state in the `state` object, mirrored in the URL hash as
  `#p=<pillars>&f=<focus nodes>&s=<scope>&o=<others>&d=0`, so a view can be shared):
  - **Pillars**: one checkbox per pillar (several can be shown), with `all` / `none`.
  - **Hide done** (checked by default).
  - **Focus**: any set of nodes (goal or not), added from the "+ add a node" menu, from the
    side-panel buttons, or removed with the chips. **Show** says what is kept around each
    focus node: what it needs (path to it, the default), what it unlocks, both, or the
    node only. **Other nodes** are hidden (default), dimmed, or left unchanged; with
    dimmed or unchanged, the focus set is highlighted (accent underlay), which gives
    "highlight only".
  - A node is shown if its pillar is chosen, it is not hidden as done, and (focus active
    and others hidden) it is in the focus set. Focus nodes themselves are always shown.
- Clicking a node opens the side panel: summary, focus buttons (path to it, what it
  unlocks, highlight only, add to / remove from focus), long description, share of
  prerequisites done, "Needs" and "Unlocks" lists (clickable), links.
- Links `[text](node:id)` in descriptions become `<a href="#" data-node="id">` in
  `build.py`, and the page selects the target node on click.
- CSS is written in a few long lines; when editing it with a script, make sure a newline
  is a real newline, not the two characters `\n`.

## Sources of the data

- `ROADMAP.md` in the SPy repo (version of 2026-04-17) seeded the first 44 nodes.
- SPy issues and pull requests give the links and the `done` status.
- The SPy book pages "Low-level features SPy still needs" and "Fixed-size arrays" gave the
  "Low-level features" pillar. Their proposals are `idea` nodes; PR #749 (`calc_layout`)
  is `in-progress` and its real status should be verified.

## Working rules

- Prefer small, reviewable changes to the data over restructuring the schema.
- Edit `site_src/index.html` and `build.py` for the page, never `site/`.
- Do not push or open pull requests unless asked; commit locally and give the diff.
- After any change, run `uv run build.py` and fix every reported problem.

## Possible next steps

- Per-node pages with the design explanation, linked to the technical notes.
- Timeline view: pillars as rows, quarters as columns.
- A script that updates `status` of nodes with linked PRs through the GitHub API.
- Generate `ROADMAP.md` from the data, so the flat file cannot drift.
- A `variants` node (depends on `unions`), and merging `span` with `ptr-kinds`.
