# Representations of the SPy project and of its roadmap

A small static website that shows how the pieces of [SPy](https://github.com/spylang/spy)
(a new pythonic language) fit together: goals, features, tasks, and what depends on
what. The data lives in TOML files (one per pillar) plus optional Markdown descriptions; the
page is generated from them and deployed to GitHub Pages.

Site: <https://paugier.github.io/spy-roadmap-repr/>

SPy's own `ROADMAP.md` is a flat and hard-to-read text. This repo turns
the same information into a graph that a newcomer can explore, and gives each item a
plain-language summary.

## Quick start

```sh
uv run build.py        # validates data/, writes site/index.html
uv run python -m http.server -d site   # then open http://localhost:8000
```

`build.py` declares its only dependency (`markdown`) inline, so `uv` needs no setup. It
exits with a non-zero status and a list of problems if the data is invalid.

## Layout

| Path | Role |
| --- | --- |
| `data/<pillar>.toml` | One file per pillar (file name = pillar id). One `[node-id]` table per node. |
| `data/descriptions/<id>.md` | Optional long description of a node, in Markdown. |
| `build.py` | Validates the data, injects it as JSON into the template, writes `site/index.html`. |
| `site_src/index.html` | Page template (HTML, CSS and JS in one file). `__DATA__` is replaced by the JSON. |
| `.github/workflows/pages.yml` | On every push to `main`: `uv run build.py`, then deploy `site/` to GitHub Pages. |
| `site/` | Build output, git-ignored. |

## Data model

Each pillar is a TOML file. The top-level `title` and `order` describe the pillar; each
`[table]` below is a node, and the table name is the node id:

```toml
# data/core.toml
title = "Core language"
order = 1

[heap-classes]
title = "Heap-allocated classes"
kind = "feature"
status = "planned"
when = "2026-Q2"
summary = "Classes whose instances live on the heap and are accessed by reference."
depends_on = ["gc-ref"]   # ids can live in any pillar file
links = [
  "https://github.com/spylang/spy/pull/383",
]
```

| Field | Required | Values / meaning |
| --- | --- | --- |
| table name | yes | Unique kebab-case id, used in `depends_on`. |
| `title` | yes | Short label shown in the graph. |
| `kind` | yes | `goal`, `feature`, `task`, `problem`, `bug`. |
| `status` | yes | `idea`, `planned`, `in-progress`, `done`, `blocked`. |
| `summary` | yes | One or two sentences a reader without compiler background can follow. |
| `when` | no | Quarter such as `"2026-Q2"` (a string). |
| `depends_on` | no | Ids of prerequisites. |
| `links` | no | PR and issue URLs. |

The pillar of a node is the file it lives in. To add a pillar, add a new `data/<id>.toml`.

### Long descriptions

For anything longer than the summary, create `data/descriptions/<node-id>.md`. It is
rendered in the side panel, under the summary. The build fails if a file name does not
match a node id.

The dialect is [Python-Markdown](https://python-markdown.github.io/) with three
extensions: fenced code blocks, tables and admonitions. It is **not** MyST, so when
reusing text from MyST notes convert these constructs:

| MyST | Here |
| --- | --- |
| `:::{admonition} Definition: x` ... `:::` | `!!! note "Definition: x"` followed by the body indented by 4 spaces |
| ``{ref}`label` `` | `[text](node:<node-id>)`, a link that opens another node in the panel (the build rejects unknown ids) |
| `(label)=` anchors, `{ref}` to pages | plain text: pages of the SPy book are not linked |

Lists need a blank line before them.

Conventions:

- `goal` nodes are the "northern stars"; the "Path to goal" selector lists them.
- A dependency means "cannot be finished or used without". Add one only when it is stated
  in the sources or clear from the design, never to make the graph look connected.
- An edge goes from the prerequisite to what it unlocks, so the layout reads left to
  right from foundations to goals.
- Within a file, put goals first, then nodes in the order you want to read them.

`build.py` rejects TOML syntax errors, missing required fields, unknown fields, unknown
`kind`/`status`, duplicate ids, dependencies on unknown ids, description files without a
node, and dependency cycles.

## The page

`site_src/index.html` uses [Cytoscape.js](https://js.cytoscape.org/) with the dagre
layout, loaded from jsDelivr at pinned versions. Node colors follow `status` (CSS
variables, light and dark theme).

- Filters: pillar, hide done (checked by default).
- "Path to goal": dims everything that is not upstream of the chosen goal.
- Clicking a node opens a side panel: summary, long description, share of prerequisites done, "Needs" and
  "Unlocks" lists (clickable), links.

There is no framework and no bundler. Keep it that way unless the page outgrows one file.

## Working on this repo

- Change data: edit `data/<pillar>.toml` or `data/descriptions/<id>.md`, run `uv run build.py`, check the graph in a browser.
- Change the page: edit `site_src/index.html`; do not edit `site/`.
- The page loads scripts only from jsDelivr, so a browser with network access is needed to
  test it. The build step alone cannot catch JavaScript errors.
- Prefer small, reviewable changes to the data over restructuring the schema.

## Sources of the data

- `ROADMAP.md` in the SPy repo (version of 2026-04-17) seeded the first 44 nodes.
- The SPy book pages "Low-level features SPy still needs" and "Fixed-size arrays" gave the
  "Low-level features" pillar (proposals, so most nodes are `idea`).
- SPy issues and pull requests provide the links and the done status.

## Possible next steps

- Per-node pages with the design explanation, linked to the technical notes.
- Timeline view: pillars as rows, quarters as columns.
- A script that updates `status` of nodes with linked PRs through the GitHub API.
- Generate `ROADMAP.md` from the data, so the flat file cannot drift.
- Add `problem` and `bug` nodes, limited to those that block a feature.
