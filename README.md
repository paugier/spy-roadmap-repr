# Representations of the SPy project and of its roadmap

A small static website that shows how the pieces of [SPy](https://github.com/spylang/spy)
(a new pythonic language) fit together: goals, features, tasks, and what depends on
what. The data lives in one YAML file; the page is generated from it and deployed to
GitHub Pages.

Site: <https://paugier.github.io/spy-roadmap-repr/>

SPy's own `ROADMAP.md` is a flat and hard-to-read text. This repo turns
the same information into a graph that a newcomer can explore, and gives each item a
plain-language summary.

## Quick start

```sh
uv run build.py        # validates data/nodes.yaml, writes site/index.html
python -m http.server -d site   # then open http://localhost:8000
```

`build.py` declares its only dependency (`pyyaml`) inline, so `uv` needs no setup. It
exits with a non-zero status and a list of problems if the data is invalid.

## Layout

| Path | Role |
| --- | --- |
| `data/nodes.yaml` | The single source of truth: one node per line. Edit this file to change the site. |
| `build.py` | Validates the data, injects it as JSON into the template, writes `site/index.html`. |
| `site_src/index.html` | Page template (HTML, CSS and JS in one file). `__DATA__` is replaced by the JSON. |
| `.github/workflows/pages.yml` | On every push to `main`: `uv run build.py`, then deploy `site/` to GitHub Pages. |
| `site/` | Build output, git-ignored. |

## Data model

Each entry of `data/nodes.yaml` is one node:

```yaml
- {id: heap-classes, title: Heap-allocated classes, kind: feature, status: planned,
   pillar: core, when: 2026-Q2, depends_on: [gc-ref],
   links: [https://github.com/spylang/spy/pull/383],
   summary: "Classes whose instances live on the heap and are accessed by reference."}
```

| Field | Required | Values / meaning |
| --- | --- | --- |
| `id` | yes | Unique kebab-case slug. |
| `title` | yes | Short label shown in the graph. |
| `kind` | yes | `goal`, `feature`, `task`, `problem`, `bug`. |
| `status` | yes | `idea`, `planned`, `in-progress`, `done`, `blocked`. |
| `pillar` | yes | `core`, `stdlib`, `memory`, `spy-c`, `spy-python`, `tooling`. |
| `summary` | yes | One or two sentences a reader without compiler background can follow. |
| `when` | no | Quarter such as `2026-Q2`. |
| `depends_on` | no | Ids of prerequisites. |
| `links` | no | PR and issue URLs. |
| `notes` | no | Reserved for a link to the matching technical note (not rendered yet). |

Conventions:

- `goal` nodes are the "northern stars"; the "Path to goal" selector lists them.
- A dependency means "cannot be finished or used without". Add one only when it is stated
  in the sources or clear from the design, never to make the graph look connected.
- An edge goes from the prerequisite to what it unlocks, so the layout reads left to
  right from foundations to goals.
- Keep nodes on one line and entries grouped by pillar, so diffs stay small.

`build.py` rejects missing required fields, unknown `kind`/`status`, duplicate ids,
dependencies on unknown ids, and dependency cycles.

## The page

`site_src/index.html` uses [Cytoscape.js](https://js.cytoscape.org/) with the dagre
layout, loaded from jsDelivr at pinned versions. Node colors follow `status` (CSS
variables, light and dark theme).

- Filters: pillar, hide done.
- "Path to goal": dims everything that is not upstream of the chosen goal.
- Clicking a node opens a side panel: summary, share of prerequisites done, "Needs" and
  "Unlocks" lists (clickable), links.

There is no framework and no bundler. Keep it that way unless the page outgrows one file.

## Working on this repo

- Change data: edit `data/nodes.yaml`, run `uv run build.py`, check the graph in a browser.
- Change the page: edit `site_src/index.html`; do not edit `site/`.
- The page loads scripts only from jsDelivr, so a browser with network access is needed to
  test it. The build step alone cannot catch JavaScript errors.
- Prefer small, reviewable changes to the data over restructuring the schema.

## Sources of the data

- `ROADMAP.md` in the SPy repo (version of 2026-04-17) seeded the first 44 nodes.
- SPy issues and pull requests provide the links and the done status.

## Possible next steps

- Per-node pages with the design explanation, linked to the technical notes (`notes`).
- Timeline view: pillars as rows, quarters as columns.
- A script that updates `status` of nodes with linked PRs through the GitHub API.
- Generate `ROADMAP.md` from the data, so the flat file cannot drift.
- Add `problem` and `bug` nodes, limited to those that block a feature.
