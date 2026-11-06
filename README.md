# Representations of the SPy project and of its roadmap

A small static website that shows how the pieces of [SPy](https://github.com/spylang/spy)
(a new pythonic language) fit together: goals, features, tasks, and what depends on what.

Site: <https://paugier.github.io/spy-roadmap-repr/>

SPy's own `ROADMAP.md` is a flat, hard-to-read text. Here the same information is a graph
that a newcomer can explore. Click a node to read a plain-language summary, a longer
explanation, what it needs, what it unlocks and the related pull requests. "Path to goal"
dims everything that is not a prerequisite of the chosen goal.

## Build the site locally

```sh
uv run build.py                        # validates data/, writes site/index.html
uv run python -m http.server -d site   # then open http://localhost:8000
```

The page loads its scripts from a CDN, so a browser with network access is needed.

## Contribute

The content is plain text in `data/`:

- `data/<pillar>.toml`: one file per theme, one `[node-id]` table per node (title, kind,
  status, summary, dependencies, links);
- `data/descriptions/<node-id>.md`: optional longer text for a node.

Edit them, run `uv run build.py` (it reports any inconsistency), look at the graph, and
open a pull request. Every push to `main` redeploys the site to GitHub Pages.

The full data model, the Markdown dialect of the descriptions and the project conventions
are in [AGENTS.md](AGENTS.md), which is written for both people and coding agents.

## License

BSD-3-Clause.
